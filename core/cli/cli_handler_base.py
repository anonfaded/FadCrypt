"""
CLI Handler Base Class

Abstract base class for platform-specific lock/unlock operations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
import os
import json
import curses
import platform
from core.verbose_logger import vlog


class CLIHandlerBase(ABC):
    """Abstract base class for CLI lock/unlock operations"""
    
    def __init__(self, config_folder: str):
        """
        Initialize CLI handler.
        
        Args:
            config_folder: Path to FadCrypt config folder
        """
        self.config_folder = config_folder
        self.config_file = os.path.join(config_folder, 'apps_config.json')
        
        # Ensure config file exists with proper structure
        self._ensure_config_initialized()
    
    @abstractmethod
    def lock_path(self, path: str) -> Tuple[bool, str]:
        """
        Lock a file or folder.
        
        Args:
            path: Absolute path to file or folder
        
        Returns:
            Tuple of (success: bool, error_message: str)
        """
        pass
    
    @abstractmethod
    def unlock_path(self, path: str) -> Tuple[bool, str]:
        """
        Unlock a file or folder.
        
        Args:
            path: Absolute path to file or folder
        
        Returns:
            Tuple of (success: bool, error_message: str)
        """
        pass
    
    def lock_multiple(self, paths: List[str]) -> Tuple[int, int, List[str], List[str]]:
        """
        Lock multiple paths.
        
        Before locking, ensure encryption password is set if enabled.
        
        Args:
            paths: List of absolute paths
        
        Returns:
            Tuple of (success_count, failure_count, successful_paths, error_messages)
        """
        # CRITICAL: Set password for encryption if enabled
        self._ensure_password_for_encryption()
        
        success_count = 0
        failure_count = 0
        successful_paths = []
        error_messages = []
        
        # For batch operations (multiple paths), show single confirmation for all items
        if len(paths) > 1:
            # Calculate total size and item counts for all paths
            total_size = 0
            total_files = 0
            total_folders = 0
            
            for path in paths:
                # Calculate size and counts (try/except handles protected files)
                try:
                    total_size += self._get_item_size(path)
                    file_count, folder_count = self._count_items(path)
                    total_files += file_count
                    total_folders += folder_count
                except (PermissionError, OSError) as e:
                    vlog(f"[Batch Lock] Warning: Could not calculate size for {path}: {e}")
                    # Use default estimate if we can't read (likely protected)
                    total_size += 1024 * 1024  # Assume 1MB default
                    total_files += 1
            
            total_size_mb = total_size / (1024 * 1024)
            is_large = total_size_mb >= 500
            estimated_time = self._calculate_encryption_time(total_size)
            
            # Read encryption and platform settings
            encryption_enabled = True
            is_linux = platform.system() == "Linux"
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    encryption_enabled = config.get("dangerous_operations", {}).get("encryption", True)
            except:
                encryption_enabled = True
            
            # Show single confirmation for all items
            batch_path = f"{len(paths)} items"  # Display name for batch operation
            import curses
            user_confirmed = curses.wrapper(self._show_confirmation_menu, batch_path, total_size_mb, is_large,
                                            estimated_time, total_files, total_folders,
                                            encryption_enabled, is_linux)
            
            if not user_confirmed:
                # User cancelled batch operation
                return (0, len(paths), [], [f"Batch operation cancelled by user"])
        
        # Process each path (with or without per-file confirmation based on batch mode)
        for path in paths:
            # For single file operations, show individual confirmation
            if len(paths) == 1:
                confirmed, is_large = self._check_file_size_and_confirm(path)
                if not confirmed:
                    failure_count += 1
                    if is_large:
                        error_messages.append(f"{path}: Cancelled - file too large (≥500 MB)")
                    else:
                        error_messages.append(f"{path}: Cancelled by user")
                    continue
            
            # Lock the path (batch confirmation already done above)
            success, error_msg = self.lock_path(path)
            if success:
                success_count += 1
                successful_paths.append(path)
            else:
                failure_count += 1
                error_messages.append(f"{path}: {error_msg}")
        
        return (success_count, failure_count, successful_paths, error_messages)
    
    def _get_item_size(self, path: str) -> int:
        """Get total size of file or folder in bytes"""
        if os.path.isfile(path):
            return os.path.getsize(path)
        
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except OSError:
                    pass
        return total_size
    
    def _count_items(self, path: str) -> tuple:
        """
        Count files and folders in path.
        Returns (file_count, folder_count)
        """
        if os.path.isfile(path):
            return (1, 0)
        
        file_count = 0
        folder_count = 0
        for dirpath, dirnames, filenames in os.walk(path):
            file_count += len(filenames)
            folder_count += len(dirnames)
        
        # Add 1 to folder count to include the root folder itself
        folder_count += 1
        
        return (file_count, folder_count)
    
    def _calculate_encryption_time(self, size_bytes: int) -> float:
        """
        Calculate approximate encryption time based on size.
        Formula: 16s per 500MB (32 MB/s)
        """
        MB = 1024 * 1024
        size_mb = size_bytes / MB
        time_seconds = (size_mb / 500) * 16
        return time_seconds
    
    def _check_file_size_and_confirm(self, path: str) -> tuple:
        """
        Show confirmation menu before locking any file with tamper-proof warning.
        Shows time estimate and item counts for all file sizes.
        Returns (confirmed: bool, is_large: bool) - whether user confirmed and if file was >=500MB
        """
        size_bytes = self._get_item_size(path)
        size_mb = size_bytes / (1024 * 1024)
        is_large = size_mb >= 500
        
        estimated_time = self._calculate_encryption_time(size_bytes)
        file_count, folder_count = self._count_items(path)
        
        # Read encryption and platform settings
        encryption_enabled = True
        is_linux = platform.system() == "Linux"
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                encryption_enabled = config.get("dangerous_operations", {}).get("encryption", True)
        except:
            encryption_enabled = True
        
        # Run the curses menu
        user_confirmed = curses.wrapper(self._show_confirmation_menu, path, size_mb, is_large, 
                                        estimated_time, file_count, folder_count, 
                                        encryption_enabled, is_linux)
        return (user_confirmed, is_large)
    
    def _show_confirmation_menu(self, stdscr, path, size_mb, is_large, estimated_time, 
                                file_count, folder_count, encryption_enabled, is_linux):
        """Display the lock confirmation menu with platform-specific protection info."""
        from .colors import Colors
        
        # Setup curses
        curses.start_color()
        try:
            curses.use_default_colors()
        except:
            pass
        
        # Initialize colors matching TUI theme
        curses.init_pair(1, curses.COLOR_RED, -1)                  # Red border
        curses.init_pair(2, curses.COLOR_WHITE, -1)                # White text
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)  # White on red (selected)
        curses.init_pair(4, curses.COLOR_YELLOW, -1)               # Yellow warning
        curses.init_pair(5, curses.COLOR_GREEN, -1)                # Green success
        curses.init_pair(6, curses.COLOR_CYAN, -1)                 # Cyan info
        
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # Calculate centered box position
        box_width = 75
        box_height = 28
        box_start_x = max(0, (width - box_width) // 2)
        box_start_y = max(0, (height - box_height) // 2)
        
        cursor_pos = 0
        options = [("✓ Lock This Item", True), ("✗ Cancel - Don't Lock", False)]
        
        while True:
            stdscr.clear()
            
            # Draw red bordered box
            try:
                # Top border
                stdscr.addstr(box_start_y, box_start_x, "┌" + "─" * (box_width - 2) + "┐", curses.color_pair(1) | curses.A_BOLD)
                
                # Content lines
                line_y = box_start_y + 1
                
                # Title
                if is_large:
                    title = "📦 Large File Detected - Lock Confirmation"
                else:
                    title = "🔒 Lock Confirmation"
                stdscr.addstr(line_y, box_start_x + 2, title, curses.color_pair(4) | curses.A_BOLD)
                line_y += 2
                
                # Size info
                size_info = f"Data Size: {size_mb:.1f} MB"
                stdscr.addstr(line_y, box_start_x + 4, size_info, curses.color_pair(6))
                line_y += 1
                
                # Item counts
                if file_count == 1 and folder_count == 1:
                    items_info = "Items: 1 file"
                elif file_count > 1 and folder_count == 1:
                    items_info = f"Items: {file_count} files in 1 folder"
                else:
                    items_info = f"Items: {file_count} files, {folder_count} folders"
                
                stdscr.addstr(line_y, box_start_x + 4, items_info, curses.color_pair(6))
                line_y += 1
                
                # Time estimate
                time_info = f"Est. Encryption Time: ~{estimated_time:.0f} seconds"
                stdscr.addstr(line_y, box_start_x + 4, time_info, curses.color_pair(6))
                line_y += 2
                
                # Separator
                stdscr.addstr(line_y, box_start_x + 2, "─" * (box_width - 4), curses.color_pair(1))
                line_y += 1
                
                # Warning: Conditional based on encryption setting and platform
                self._render_protection_info(stdscr, line_y, box_start_x, box_width, 
                                            encryption_enabled, is_linux)
                line_y = self._get_protection_info_lines(encryption_enabled, is_linux) + line_y + 2
                
                # Recommendations (always show)
                stdscr.addstr(line_y, box_start_x + 2, "💡 Recommendations:", curses.color_pair(5) | curses.A_BOLD)
                line_y += 1
                
                rec1 = "• Optimal: Lock files ≤500 MB for faster processing"
                stdscr.addstr(line_y, box_start_x + 4, rec1[:box_width-6], curses.color_pair(2))
                line_y += 1
                
                rec2 = "• Split at OUTER level: lock separate folders"
                stdscr.addstr(line_y, box_start_x + 4, rec2[:box_width-6], curses.color_pair(2))
                line_y += 1
                
                rec3 = "  NOT inside the folder (still makes it large)"
                stdscr.addstr(line_y, box_start_x + 4, rec3[:box_width-6], curses.color_pair(2))
                line_y += 1
                
                msg1 = "💬 Faded says: You can skip splitting if you want—"
                stdscr.addstr(line_y, box_start_x + 4, msg1[:box_width-6], curses.color_pair(5))
                line_y += 1
                
                msg2 = "   let FadCrypt encrypt tons of files in one folder,"
                stdscr.addstr(line_y, box_start_x + 4, msg2[:box_width-6], curses.color_pair(5))
                line_y += 1
                
                msg3 = "   just expect slow encryption and a boring wait! 😴"
                stdscr.addstr(line_y, box_start_x + 4, msg3[:box_width-6], curses.color_pair(5))
                line_y += 1
                
                # Separator
                stdscr.addstr(line_y, box_start_x + 2, "─" * (box_width - 4), curses.color_pair(1))
                line_y += 1
                
                # Options
                for idx, (text, _) in enumerate(options):
                    if idx == cursor_pos:
                        prefix = "► "
                        option_text = prefix + text
                        padding = box_width - 4 - len(option_text)
                        full_text = option_text + " " * padding
                        stdscr.addstr(line_y, box_start_x + 2, full_text, curses.color_pair(3) | curses.A_BOLD)
                    else:
                        prefix = "  "
                        stdscr.addstr(line_y, box_start_x + 2, prefix + text, curses.color_pair(2))
                    line_y += 1
                
                # Bottom border
                stdscr.addstr(box_start_y + box_height - 1, box_start_x, "└" + "─" * (box_width - 2) + "┘", curses.color_pair(1) | curses.A_BOLD)
                
                # Instructions at bottom
                instr = "Use ↑↓ Arrow Keys or Y/N | Press ENTER to Confirm"
                if height > box_start_y + box_height + 2:
                    stdscr.addstr(box_start_y + box_height + 2, max(0, (width - len(instr)) // 2), instr, curses.color_pair(1))
                
            except curses.error:
                pass  # Silently handle drawing errors
            
            stdscr.refresh()
            
            # Handle input
            try:
                ch = stdscr.getch()
                if ch == curses.KEY_UP:
                    cursor_pos = (cursor_pos - 1) % len(options)
                elif ch == curses.KEY_DOWN:
                    cursor_pos = (cursor_pos + 1) % len(options)
                elif ch == ord('y') or ch == ord('Y'):
                    return True
                elif ch == ord('n') or ch == ord('N'):
                    return False
                elif ch == ord('\n') or ch == ord('\r'):
                    return options[cursor_pos][1]
                elif ch == ord('q') or ch == 27:  # q or ESC
                    return False
                elif ch == ord('g') or ch == ord('G'):
                    self._show_guide_screen(stdscr, height, width, is_linux)
            except:
                pass
    
    def _get_protection_info_lines(self, encryption_enabled, is_linux):
        """Return number of lines needed for protection info."""
        if encryption_enabled:
            return 4
        else:
            if is_linux:
                return 5
            else:
                return 5
    
    def _render_protection_info(self, stdscr, line_y, box_start_x, box_width, 
                               encryption_enabled, is_linux):
        """Render protection info based on encryption and platform."""
        if encryption_enabled:
            # Encryption enabled - show tamper-proof message
            stdscr.addstr(line_y, box_start_x + 2, "⚠️  TAMPER-PROOF ENCRYPTION:", curses.color_pair(4) | curses.A_BOLD)
            line_y += 1
            
            warning1 = "Once locked, this file CANNOT be:"
            stdscr.addstr(line_y, box_start_x + 4, warning1[:box_width-6], curses.color_pair(6))
            line_y += 1
            
            warning2 = "• Copied  • Moved  • Edited  • Deleted"
            stdscr.addstr(line_y, box_start_x + 4, warning2[:box_width-6], curses.color_pair(2))
            line_y += 1
            
            guide_hint = "Press G to see how to manage this behavior →"
            stdscr.addstr(line_y, box_start_x + 4, guide_hint[:box_width-6], curses.color_pair(4))
        else:
            # Encryption disabled - show platform-specific protection info
            if is_linux:
                stdscr.addstr(line_y, box_start_x + 2, "⚠️  CHMOD+CHATTR PROTECTION ONLY (NOT ENCRYPTED):", curses.color_pair(4) | curses.A_BOLD)
                line_y += 1
                
                warning1 = "File will be protected with chmod & chattr immutable"
                stdscr.addstr(line_y, box_start_x + 4, warning1[:box_width-6], curses.color_pair(6))
                line_y += 1
                
                warning2 = "flags. If protection is removed with --0/--off, file"
                stdscr.addstr(line_y, box_start_x + 4, warning2[:box_width-6], curses.color_pair(6))
                line_y += 1
                
                warning3 = "becomes readable & modifiable. Enable encryption in settings."
                stdscr.addstr(line_y, box_start_x + 4, warning3[:box_width-6], curses.color_pair(1))
                line_y += 1
                
                guide_hint = "Press G to learn more about protection options →"
                stdscr.addstr(line_y, box_start_x + 4, guide_hint[:box_width-6], curses.color_pair(4))
            else:
                stdscr.addstr(line_y, box_start_x + 2, "⚠️  ACL PROTECTION ONLY (NOT ENCRYPTED):", curses.color_pair(4) | curses.A_BOLD)
                line_y += 1
                
                warning1 = "File will be protected with Windows ACLs. If protection"
                stdscr.addstr(line_y, box_start_x + 4, warning1[:box_width-6], curses.color_pair(6))
                line_y += 1
                
                warning2 = "is removed with --0/--off, file becomes readable &"
                stdscr.addstr(line_y, box_start_x + 4, warning2[:box_width-6], curses.color_pair(6))
                line_y += 1
                
                warning3 = "modifiable. Enable encryption in settings for tamper-proof."
                stdscr.addstr(line_y, box_start_x + 4, warning3[:box_width-6], curses.color_pair(1))
                line_y += 1
                
                guide_hint = "Press G to learn more about protection options →"
                stdscr.addstr(line_y, box_start_x + 4, guide_hint[:box_width-6], curses.color_pair(4))
    
    def _show_guide_screen(self, stdscr, height, width, is_linux):
        """Display guide about protection options with platform-specific info."""
        options = [("← Back to Lock Confirmation", False)]
        cursor_pos = 0
        
        while True:
            stdscr.clear()
            
            # Guide box
            box_width = min(75, width - 4)
            box_height = min(30, height - 6)
            box_start_x = max(0, (width - box_width) // 2)
            box_start_y = max(0, 1)
            
            try:
                # Top border
                stdscr.addstr(box_start_y, box_start_x, "┌" + "─" * (box_width - 2) + "┐", curses.color_pair(1) | curses.A_BOLD)
                
                line_y = box_start_y + 1
                
                # Title and content based on platform and encryption
                if is_linux:
                    title = "🔐 PROTECTION OPTIONS (Linux)"
                    stdscr.addstr(line_y, box_start_x + 2, title, curses.color_pair(5) | curses.A_BOLD)
                    line_y += 2
                    
                    lines = [
                        ("ENCRYPTION (DEFAULT - Enabled by default):", curses.color_pair(4) | curses.A_BOLD),
                        ("AES-256-GCM encryption. Files become tamper-proof and", curses.color_pair(2)),
                        ("immutable. Disable in Settings if you need chmod+chattr", curses.color_pair(2)),
                        ("protection only.", curses.color_pair(2)),
                        ("", curses.color_pair(2)),
                        ("chmod+chattr Protection (No encryption mode):", curses.color_pair(4) | curses.A_BOLD),
                        ("Uses Linux permissions & immutable flag. File protected", curses.color_pair(2)),
                        ("but not encrypted (weaker security).", curses.color_pair(2)),
                        ("", curses.color_pair(2)),
                        ("TOGGLE PROTECTIONS (--0/--off and --1/--on):", curses.color_pair(4) | curses.A_BOLD),
                        ("Disable:  fadcrypt --0 file.txt  (or --off)", curses.color_pair(6)),
                        ("Enable:   fadcrypt --1 file.txt  (or --on)", curses.color_pair(6)),
                        ("", curses.color_pair(2)),
                        ("For more info: fadcrypt --help or FadGuide (Tray/GUI)", curses.color_pair(5)),
                    ]
                else:
                    title = "🔐 PROTECTION OPTIONS (Windows)"
                    stdscr.addstr(line_y, box_start_x + 2, title, curses.color_pair(5) | curses.A_BOLD)
                    line_y += 2
                    
                    lines = [
                        ("ENCRYPTION (DEFAULT - Enabled by default):", curses.color_pair(4) | curses.A_BOLD),
                        ("AES-256-GCM encryption. Files become tamper-proof", curses.color_pair(2)),
                        ("(cannot move, copy, edit, or delete). Disable in", curses.color_pair(2)),
                        ("Settings if you need ACL-only protection.", curses.color_pair(2)),
                        ("", curses.color_pair(2)),
                        ("ACL Protection (No encryption mode):", curses.color_pair(4) | curses.A_BOLD),
                        ("Uses Windows Access Control Lists only. File access", curses.color_pair(2)),
                        ("restricted but not encrypted (weaker security).", curses.color_pair(2)),
                        ("", curses.color_pair(2)),
                        ("TOGGLE PROTECTIONS (--0/--off and --1/--on):", curses.color_pair(4) | curses.A_BOLD),
                        ("Disable:  fadcrypt --0 file.txt  (or --off)", curses.color_pair(6)),
                        ("Enable:   fadcrypt --1 file.txt  (or --on)", curses.color_pair(6)),
                        ("", curses.color_pair(2)),
                        ("For more info: fadcrypt --help or FadGuide (Tray/GUI)", curses.color_pair(5)),
                    ]
                
                for text, attr in lines:
                    if line_y < box_start_y + box_height - 3:
                        display_text = text[:box_width-6] if text else ""
                        stdscr.addstr(line_y, box_start_x + 2, display_text, attr)
                        line_y += 1
                
                # Separator before options
                stdscr.addstr(line_y, box_start_x + 2, "─" * (box_width - 4), curses.color_pair(1))
                line_y += 1
                
                # Back option
                for idx, (text, _) in enumerate(options):
                    if idx == cursor_pos:
                        prefix = "► "
                        option_text = prefix + text
                        padding = box_width - 4 - len(option_text)
                        full_text = option_text + " " * padding
                        stdscr.addstr(line_y, box_start_x + 2, full_text, curses.color_pair(3) | curses.A_BOLD)
                    else:
                        prefix = "  "
                        stdscr.addstr(line_y, box_start_x + 2, prefix + text, curses.color_pair(2))
                    line_y += 1
                
                # Bottom border
                stdscr.addstr(box_start_y + box_height - 1, box_start_x, "└" + "─" * (box_width - 2) + "┘", curses.color_pair(1) | curses.A_BOLD)
                
                # Instructions
                instr = "Use ↑↓ Arrow Keys or ENTER to go back"
                if height > box_start_y + box_height + 1:
                    instr_x = max(0, (width - len(instr)) // 2)
                    stdscr.addstr(box_start_y + box_height + 1, instr_x, instr, curses.color_pair(1))
                
            except curses.error:
                pass
            
            stdscr.refresh()
            
            # Handle input
            try:
                ch = stdscr.getch()
                if ch == curses.KEY_UP:
                    cursor_pos = (cursor_pos - 1) % len(options)
                elif ch == curses.KEY_DOWN:
                    cursor_pos = (cursor_pos + 1) % len(options)
                elif ch == ord('\n') or ch == ord('\r'):
                    return  # Go back to main menu
                elif ch == ord('q') or ch == 27:  # q or ESC
                    return  # Go back
            except:
                pass
    
    def _ensure_password_for_encryption(self):
        """
        Ensure password is set in file_lock_manager if encryption is enabled.
        This is called before locking operations.
        """
        from .password_prompt import PasswordPrompt
        from core.password_manager import PasswordManager
        from core.crypto_manager import CryptoManager
        
        try:
            # Check if encryption is enabled
            if not os.path.exists(self.config_file):
                return
            
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                dangerous_ops = config.get("dangerous_operations", {})
                encryption_enabled = dangerous_ops.get("encryption", False)
            
            if not encryption_enabled:
                return  # Encryption not enabled, no need for password
            
            # Check if file_lock_manager has password
            if hasattr(self, 'file_lock_manager') and self.file_lock_manager:
                if self.file_lock_manager.password_bytes is not None:
                    return  # Password already set
                
                # Password not set, need to load it
                password_file = os.path.join(self.config_folder, "encrypted_password.bin")
                recovery_codes_file = os.path.join(self.config_folder, "recovery_codes.json")
                
                # Create password manager
                crypto_manager = CryptoManager()
                password_manager = PasswordManager(password_file, crypto_manager, recovery_codes_file)
                
                # Create password prompt
                password_prompt = PasswordPrompt(password_manager)
                
                # Verify password (this will cache it if correct)
                if password_prompt.verify_password():
                    # Get cached password and set in file_lock_manager
                    cached_pwd = password_manager.get_password_bytes()
                    if cached_pwd:
                        self.file_lock_manager.set_password(cached_pwd)
                        vlog("[Encryption] ✓ Password verified and set for file encryption")
                else:
                    vlog("[Encryption] ❌ Password verification failed - encryption disabled for this operation")
        
        except Exception as e:
            print(f"[Encryption] ⚠ Warning: Could not ensure password: {e}")
    
    def unlock_multiple(self, paths: List[str]) -> Tuple[int, int, List[str], List[str]]:
        """
        Unlock multiple paths.
        
        Before unlocking, ensure encryption password is set if enabled.
        
        Args:
            paths: List of absolute paths
        
        Returns:
            Tuple of (success_count, failure_count, successful_paths, error_messages)
        """
        # CRITICAL: Set password for decryption if enabled
        self._ensure_password_for_encryption()
        
        success_count = 0
        failure_count = 0
        successful_paths = []
        error_messages = []
        
        for path in paths:
            success, error_msg = self.unlock_path(path)
            if success:
                success_count += 1
                successful_paths.append(path)
            else:
                failure_count += 1
                error_messages.append(f"{path}: {error_msg}")
        
        return (success_count, failure_count, successful_paths, error_messages)
    
    @abstractmethod
    def list_locked_items(self) -> List[Dict]:
        """
        List all locked items.
        
        Returns:
            List of locked items with metadata
        """
        pass
    
    @abstractmethod
    def toggle_tamper_proof(self, path: str, enable: bool) -> bool:
        """
        Toggle tamper-proof protections on a file or folder.
        
        Args:
            path: Path to the file or folder
            enable: True to enable protections, False to disable
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    def validate_path(self, path: str) -> bool:
        """
        Validate that a path exists and is accessible.
        
        Args:
            path: Path to validate
        
        Returns:
            True if valid, False otherwise
        """
        # Use lexists() instead of exists() because protected folders (chmod 000) 
        # are inaccessible but still exist on the filesystem
        if not os.path.lexists(path):
            return False
        
        try:
            # Try to access the path - this may fail for protected paths, but that's OK
            # We just need to know the path exists (via lexists)
            os.stat(path)
            return True
        except (PermissionError, OSError):
            # Path exists but is not accessible - that's OK for toggle operations
            # Return True to allow operations on protected paths
            return os.path.lexists(path)
    
    def _ensure_config_initialized(self):
        """
        Ensure the config file exists with all required keys.
        This prevents KeyError exceptions when accessing config values.
        """
        from core.file_protection import safe_write_to_protected_file
        
        # Default config structure
        default_config = {
            "applications": [],
            "locked_files_and_folders": [],
            "dangerous_operations": {
                "encryption": True
            }
        }
        
        try:
            # Check if config file exists
            if os.path.exists(self.config_file):
                # Load existing config
                with open(self.config_file, 'r') as f:
                    existing_config = json.load(f)
                
                # Deep merge with defaults to ensure all keys exist
                merged_config = self._deep_merge_configs(default_config, existing_config)
                
                # Save merged config if different
                if merged_config != existing_config:
                    content = json.dumps(merged_config, indent=2)
                    success, error = safe_write_to_protected_file(self.config_file, content)
                    if not success:
                        print(f"Warning: Could not update config file: {error}")
            else:
                # Create new config file with defaults
                content = json.dumps(default_config, indent=2)
                success, error = safe_write_to_protected_file(self.config_file, content)
                if not success:
                    print(f"Warning: Could not create config file: {error}")
                    
        except Exception as e:
            print(f"Warning: Could not initialize config: {e}")
    
    def _deep_merge_configs(self, default_config: dict, existing_config: dict) -> dict:
        """
        Deep merge default config into existing config, preserving existing values.
        
        Args:
            default_config: Default configuration structure
            existing_config: Existing configuration from file
            
        Returns:
            Merged configuration dict
        """
        merged = existing_config.copy()
        
        for key, default_value in default_config.items():
            if key not in merged:
                # Key missing, add default
                merged[key] = default_value
            elif isinstance(default_value, dict) and isinstance(merged[key], dict):
                # Both are dicts, recursively merge
                merged[key] = self._deep_merge_configs(default_value, merged[key])
            # If key exists and is not a dict, preserve existing value
            
        return merged
