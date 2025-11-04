"""
CLI Handler Base Class

Abstract base class for platform-specific lock/unlock operations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
import os
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
        
        for path in paths:
            # Check file size and confirm lock with user - returns (confirmed, is_large)
            confirmed, is_large = self._check_file_size_and_confirm(path)
            if not confirmed:
                failure_count += 1
                if is_large:
                    error_messages.append(f"{path}: Cancelled - file too large (≥500 MB)")
                else:
                    error_messages.append(f"{path}: Cancelled by user")
                continue
            
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
        
        # Use curses for beautiful menu-style confirmation (always show)
        import curses
        def show_confirmation_menu(stdscr):
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
                        # Single file
                        items_info = "Items: 1 file"
                    elif file_count > 1 and folder_count == 1:
                        # Single folder with multiple files
                        items_info = f"Items: {file_count} files in 1 folder"
                    else:
                        # Multiple folders
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
                    
                    # Warning: Tamper-Proof
                    stdscr.addstr(line_y, box_start_x + 2, "⚠️  TAMPER-PROOF ENCRYPTION:", curses.color_pair(4) | curses.A_BOLD)
                    line_y += 1
                    
                    warning1 = "Once locked, this file CANNOT be:"
                    stdscr.addstr(line_y, box_start_x + 4, warning1[:box_width-6], curses.color_pair(6))
                    line_y += 1
                    
                    warning2 = "• Copied  • Moved  • Edited  • Deleted"
                    stdscr.addstr(line_y, box_start_x + 4, warning2[:box_width-6], curses.color_pair(2))
                    line_y += 1
                    
                    guide_hint = "Press G to see how to disable this behavior →"
                    stdscr.addstr(line_y, box_start_x + 4, guide_hint[:box_width-6], curses.color_pair(4))
                    line_y += 2
                    
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
                            # Highlighted option - fill entire row with red background
                            prefix = "► "
                            option_text = prefix + text
                            # Fill entire row width with the color
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
                        # Show tamper-proof guide (call it directly, we're already in curses)
                        show_guide_screen(stdscr, height, width)
                        # Don't return, continue the menu loop
                except:
                    pass
        
        def show_guide_screen(stdscr, height, width):
            """Display guide about tamper-proof options and --0/--1 flags with cursor menu."""
            # Menu options at bottom
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
                    
                    # Title
                    title = "🔐 TAMPER-PROOF OPTIONS GUIDE"
                    title_x = box_start_x + max(2, (box_width - len(title)) // 2)
                    stdscr.addstr(line_y, title_x, title, curses.color_pair(5) | curses.A_BOLD)
                    line_y += 2
                    
                    # Content lines
                    lines = [
                        ("TAMPER-PROOF: Like a Switch (OFF=0, ON=1)", curses.color_pair(4) | curses.A_BOLD),
                        ("By default, FadCrypt locks files with FULL", curses.color_pair(2)),
                        ("tamper-proof protection (ON). Encrypted files", curses.color_pair(2)),
                        ("CANNOT be copied, moved, edited, or deleted.", curses.color_pair(2)),
                        ("", curses.color_pair(2)),
                        ("TURN OFF (--0 or --off):", curses.color_pair(4) | curses.A_BOLD),
                        ("Disable tamper-proof protections from encrypted files.", curses.color_pair(2)),
                        ("Files become MOVEABLE, COPYABLE, & DELETABLE.", curses.color_pair(2)),
                        ("Examples: fadcrypt --0 file.txt  OR  fadcrypt --off file.txt", curses.color_pair(6)),
                        ("", curses.color_pair(2)),
                        ("TURN ON (--1 or --on):", curses.color_pair(4) | curses.A_BOLD),
                        ("Re-enable full tamper-proof protections.", curses.color_pair(2)),
                        ("Returns file to fully protected state.", curses.color_pair(2)),
                        ("Examples: fadcrypt --1 TestFolder  OR  fadcrypt --on TestFolder", curses.color_pair(6)),
                    ]
                    
                    for text, attr in lines:
                        if line_y < box_start_y + box_height - 3:
                            display_text = text[:box_width-6] if text else ""
                            
                            # Special handling for "OR" - render it in gray (dimmed)
                            if "OR" in display_text:
                                # Split and render with different colors for OR
                                parts = display_text.split("  OR  ")
                                if len(parts) == 2:
                                    # Render first part
                                    stdscr.addstr(line_y, box_start_x + 2, parts[0], attr)
                                    # Render OR in gray
                                    or_pos = box_start_x + 2 + len(parts[0])
                                    stdscr.addstr(line_y, or_pos, "  OR  ", curses.color_pair(4))
                                    # Render second part
                                    second_pos = or_pos + 6
                                    stdscr.addstr(line_y, second_pos, parts[1], attr)
                                else:
                                    stdscr.addstr(line_y, box_start_x + 2, display_text, attr)
                            else:
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
        
            
        
        # Run the curses menu
        user_confirmed = curses.wrapper(show_confirmation_menu)
        return (user_confirmed, is_large)
    
    def _ensure_password_for_encryption(self):
        """
        Ensure password is set in file_lock_manager if encryption is enabled.
        This is called before locking operations.
        """
        import json
        import os
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
        if not os.path.exists(path):
            return False
        
        try:
            # Try to access the path
            os.stat(path)
            return True
        except (PermissionError, OSError):
            return False
    
    def _ensure_config_initialized(self):
        """
        Ensure the config file exists with all required keys.
        This prevents KeyError exceptions when accessing config values.
        """
        import json
        from core.file_protection import safe_write_to_protected_file
        
        # Default config structure
        default_config = {
            "applications": [],
            "locked_files_and_folders": [],
            "dangerous_operations": {
                "encryption": False
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
