"""
TUI Manager

Main text-based user interface for FadCrypt CLI.
"""

import os
import sys
import platform

from .colors import Colors, print_colored, print_success, print_error, print_warning, print_info
from .password_prompt import PasswordPrompt
from .curses_file_browser import show_file_browser as show_file_selector, show_unlock_browser as show_unlock_selector
from .menu_navigator import MenuNavigator
from .curses_menu import show_curses_menu, CURSES_AVAILABLE


class DirectoryTracker:
    """Simple class to track current directory for navigation"""
    def __init__(self, current_dir: str = None):
        self.current_dir = current_dir or os.getcwd()


class TUIManager:
    """Main TUI manager for FadCrypt"""
    
    def __init__(self, password_manager, cli_handler):
        """
        Initialize TUI manager.
        
        Args:
            password_manager: PasswordManager instance
            cli_handler: Platform-specific CLI handler
        """
        self.password_manager = password_manager
        self.cli_handler = cli_handler
        self.password_prompt = PasswordPrompt(password_manager)
        self.directory_tracker = DirectoryTracker()
        self.menu_navigator = MenuNavigator()
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_header(self):
        """Display the FadCrypt header"""
        from ..version import __version__
        
        self.clear_screen()
        print(f"{Colors.BORDER}╭─ {Colors.TITLE}🏴 FadCrypt v{__version__}{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.TITLE}File, Folder & Application Protection Suite{Colors.RESET}")
        print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}\n")
    
    def show_main_menu(self):
        """Display the main menu with arrow navigation"""
        main_menu_items = [
            {'key': '1', 'icon': '🔒', 'text': 'Lock Files/Folders', 'action': 'lock'},
            {'key': '2', 'icon': '🔓', 'text': 'Unlock Files/Folders', 'action': 'unlock'},
            {'key': '3', 'icon': '📋', 'text': 'List Locked Items', 'action': 'list'},
            {'key': '4', 'icon': '💻', 'text': 'Open GUI Application', 'action': 'gui'},
            {'key': '5', 'icon': '🔧', 'text': 'Settings', 'action': 'settings'},
            {'key': '6', 'icon': '❌', 'text': 'Exit', 'action': 'exit'}
        ]
        
        # Use curses menu with animation
        return show_curses_menu("MAIN MENU", main_menu_items)
    
    def run(self):
        """Run the main TUI loop"""
        # Ensure password exists
        if not self.password_prompt.ensure_password_exists():
            print_error("Cannot proceed without a master password.")
            return
        
        while True:
            try:
                choice = self.show_main_menu()
                
                if choice == 'quit' or choice == '6':
                    # Ask for confirmation before quitting
                    self.show_header()
                    print_colored("Exit FadCrypt?\n", Colors.TITLE)
                    print_colored("Are you sure you want to exit FadCrypt?", Colors.INFO)
                    confirm = input(f"\n{Colors.DIM}[Y/N]: {Colors.RESET}").strip().lower()
                    
                    if confirm in ['y', 'yes']:
                        # Clear screen and animate goodbye message
                        import time
                        self.clear_screen()
                        goodbye_msg = "Goodbye from FadCrypt... :)"
                        print(f"\n{Colors.HIGHLIGHT}", end="", flush=True)
                        for char in goodbye_msg:
                            print(char, end="", flush=True)
                            time.sleep(0.05)
                        print(f"{Colors.RESET}\n")
                        break
                    else:
                        print_info("Returning to main menu...")
                        input("\nPress Enter to continue...")
                        continue
                elif choice == '1':
                    self.lock_files_menu()
                elif choice == '2':
                    self.unlock_files_menu()
                elif choice == '3':
                    self.list_locked_items()
                elif choice == '4':
                    self.launch_gui()
                elif choice == '5':
                    self.settings_menu()
                elif choice == 'back':
                    continue  # Stay in main menu
                    
            except KeyboardInterrupt:
                print()
                break
    
    def lock_files_browser(self):
        """Direct lock files browser (used for switching from unlock)"""
        # Interactive file selector using curses with locked paths info
        locked_items = self.cli_handler.list_locked_items()
        locked_paths = {item['path'] for item in locked_items}
        selected_paths = show_file_selector(self.directory_tracker.current_dir, mode="lock", locked_paths=locked_paths)
        
        # Check if user wants to switch back to unlock
        if selected_paths and len(selected_paths) > 0 and selected_paths[0] == '__SWITCH_TO_UNLOCK__':
            # Switch back to unlock menu
            self.unlock_files_menu()
            return
        
        # Check if user wants to teleport
        if selected_paths and len(selected_paths) > 0 and selected_paths[0] == '__TELEPORT__':
            # Show teleport menu
            locked_items = self.cli_handler.list_locked_items()
            self.show_teleport_menu(locked_items)
            return
        
        # Process selected files for locking
        if selected_paths and len(selected_paths) > 0:
            # Filter out special commands
            actual_paths = [p for p in selected_paths if not p.startswith('__')]
            
            if actual_paths:
                self.show_header()
                print_colored(f"🔒 Locking {len(actual_paths)} item(s)...\n", Colors.INFO)
                
                success_count = 0
                failed_count = 0
                for path in actual_paths:
                    try:
                        if self.cli_handler.lock_item(path):
                            success_count += 1
                        else:
                            failed_count += 1
                            print_error(f"✗ Failed to lock: {os.path.basename(path)}")
                    except Exception as e:
                        failed_count += 1
                        print_error(f"✗ Error locking {os.path.basename(path)}: {str(e)}")
                
                # Styled summary box like --lock
                if success_count > 0 or failed_count > 0:
                    print(f"{Colors.SUCCESS}╭─ 🔒 LOCK STATUS ───────────────────────{Colors.RESET}")
                    if success_count > 0:
                        print(f"{Colors.SUCCESS}├ ✓ {success_count} item(s) locked successfully{Colors.RESET}")
                    if failed_count > 0:
                        print(f"{Colors.ERROR}├ ✗ {failed_count} item(s) failed{Colors.RESET}")
                    print(f"{Colors.SUCCESS}╰─────────────────────────────────────────{Colors.RESET}")
                
                input("\nPress Enter to continue...")

    def lock_files_menu(self):
        """Lock files/folders menu"""
        lock_menu_items = [
            {'key': '1', 'icon': '📁', 'text': 'Browse current directory', 'action': 'browse'},
            {'key': '2', 'icon': '📝', 'text': 'Enter path manually', 'action': 'manual'},
            {'key': '3', 'icon': '🔙', 'text': 'Back to main menu', 'action': 'back'}
        ]
        
        choice = show_curses_menu("SELECT FILES/FOLDERS TO LOCK", lock_menu_items, "Back")
        
        if choice == '3' or choice == 'back' or choice == 'quit':
            return
        elif choice == '1':
            # Interactive file selector using curses with locked paths info
            locked_items = self.cli_handler.list_locked_items()
            locked_paths = {item['path'] for item in locked_items}
            selected_paths = show_file_selector(self.directory_tracker.current_dir, mode="lock", locked_paths=locked_paths)
            
            # Check if user wants to switch to unlock
            if selected_paths and len(selected_paths) > 0 and selected_paths[0] == '__SWITCH_TO_UNLOCK__':
                # Switch to unlock menu
                self.unlock_files_menu()
                return
            
            # Check if user wants to teleport
            if selected_paths and len(selected_paths) > 0 and selected_paths[0] == '__TELEPORT__':
                # Show teleport menu
                locked_items = self.cli_handler.list_locked_items()
                self.show_teleport_menu(locked_items)
                return
            
            if selected_paths and len(selected_paths) > 0:
                # Filter out special commands
                actual_paths = [p for p in selected_paths if not p.startswith('__')]
                
                if actual_paths:
                    self.show_header()
                    print_colored(f"🔒 Locking {len(actual_paths)} item(s)...\n", Colors.INFO)
                    
                    success, failed, _ = self.cli_handler.lock_multiple(actual_paths)
                    
                    # Styled summary box like --lock
                    if success > 0 or failed > 0:
                        print(f"{Colors.SUCCESS}╭─ 🔒 LOCK STATUS ───────────────────────{Colors.RESET}")
                        if success > 0:
                            print(f"{Colors.SUCCESS}├ ✓ {success} item(s) locked successfully{Colors.RESET}")
                        if failed > 0:
                            print(f"{Colors.ERROR}├ ✗ {failed} item(s) failed{Colors.RESET}")
                        print(f"{Colors.SUCCESS}╰─────────────────────────────────────────{Colors.RESET}")
                    
                    input("\nPress Enter to continue...")
        
        elif choice == '2':
            # Manual path entry
            print(f"\n{Colors.PRIMARY}Enter path to lock:")
            print(f" {Colors.ERROR}❯{Colors.RESET} ", end='')
            path = input().strip()
            
            if path:
                path = os.path.abspath(path)
                print_colored(f"\nLocking {path}...", Colors.INFO)
                
                if not os.path.exists(path):
                    print_error(f"Path does not exist: {path}")
                elif not os.access(path, os.R_OK):
                    print_error(f"Permission denied: Cannot access {path}")
                else:
                    # Check if already locked by looking for .fadcrypt files
                    if os.path.isfile(path):
                        lock_file = path + '.fadcrypt'
                        if os.path.exists(lock_file):
                            print_error(f"File is already locked: {os.path.basename(path)}")
                        elif self.cli_handler.lock_path(path):
                            print_success("Successfully locked!")
                        else:
                            print_error("Failed to lock file. Check permissions and try again.")
                    else:
                        # Directory
                        config_file = os.path.join(path, '.fadcrypt_config')
                        if os.path.exists(config_file):
                            print_error(f"Folder is already locked: {os.path.basename(path)}")
                        elif self.cli_handler.lock_path(path):
                            print_success("Successfully locked!")
                        else:
                            print_error("Failed to lock folder. Check permissions and try again.")
                
                input("\nPress Enter to continue...")
    
    def unlock_files_menu(self, filter_mode: str = "current"):
        """Unlock files/folders menu"""
        self.show_header()
        print_colored("Unlock Files/Folders\n", Colors.TITLE)
        
        # Get locked items
        locked_items = self.cli_handler.list_locked_items()
        
        if not locked_items:
            print_warning("No locked items found.")
            input("\nPress Enter to continue...")
            return
        
        # Show locked items for selection using enhanced curses interface
        current_dir = self.directory_tracker.current_dir
        selected_paths = show_unlock_selector(locked_items, "Select Items to Unlock", current_dir, filter_mode)
        
        # Check for special returns
        if selected_paths and selected_paths[0] == '__SWITCH_TO_LOCK__':
            # Switch directly to lock file browser (not the menu)
            self.lock_files_browser()
            return
        
        if selected_paths and selected_paths[0] == '__REFILTER__':
            # Refilter requested - toggle filter mode and restart unlock menu
            new_filter_mode = "all" if filter_mode == "current" else "current"
            self.unlock_files_menu(new_filter_mode)
            return
        
        if selected_paths and selected_paths[0] == '__TELEPORT__':
            # Show teleport menu
            self.show_teleport_menu(locked_items)
            return
        
        if selected_paths and len(selected_paths) > 0:
            # Filter out special commands
            actual_paths = [p for p in selected_paths if not p.startswith('__')]
            
            if actual_paths:
                self.show_header()
                print_colored(f"🔓 Unlocking {len(actual_paths)} item(s)...\n", Colors.INFO)
                
                success, failed, _ = self.cli_handler.unlock_multiple(actual_paths)
                
                # Styled summary box like --unlock
                if success > 0 or failed > 0:
                    print(f"{Colors.SUCCESS}╭─ 🔓 UNLOCK STATUS ─────────────────────{Colors.RESET}")
                    if success > 0:
                        print(f"{Colors.SUCCESS}├ ✓ {success} item(s) unlocked successfully{Colors.RESET}")
                    if failed > 0:
                        print(f"{Colors.ERROR}├ ✗ {failed} item(s) failed{Colors.RESET}")
                    print(f"{Colors.SUCCESS}╰─────────────────────────────────────────{Colors.RESET}")
                
                input("\nPress Enter to continue...")
    
    def show_teleport_menu(self, locked_items):
        """Show teleport menu for locked items"""
        self.show_header()
        print_colored("📍 Teleport to Location\n", Colors.TITLE)
        
        # Get unique directories
        directories = {}
        for item in locked_items:
            dir_path = os.path.dirname(item['path'])
            if dir_path not in directories:
                directories[dir_path] = []
            directories[dir_path].append(item['name'])
        
        # Show directories with item counts
        print(f"{Colors.BORDER}╭─ 📍 {Colors.TITLE}LOCATIONS ({len(directories)} unique){Colors.RESET}")
        for idx, (dir_path, items) in enumerate(directories.items(), 1):
            dir_name = os.path.basename(dir_path) or dir_path
            print(f"{Colors.BORDER}│{Colors.RESET} {Colors.SUCCESS}[{idx}]{Colors.RESET} {Colors.TEXT}{dir_name}{Colors.RESET} {Colors.DIM}({len(items)} item(s)){Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET}   {Colors.DIM}└─ {dir_path}{Colors.RESET}")
        print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}")
        
        # Ask if user wants to teleport - consistent input style
        print(f"\n{Colors.INFO}Enter location number (or press Enter to go back):{Colors.RESET}")
        print(f" {Colors.ERROR}❯{Colors.RESET} ", end='')
        choice = input().strip()
        
        if choice.isdigit():
            idx = int(choice) - 1
            dir_list = list(directories.keys())
            if 0 <= idx < len(dir_list):
                target_dir = dir_list[idx]
                self.directory_tracker.current_dir = target_dir
                print_success(f"Teleported to: {target_dir}")
                input("\nPress Enter to continue...")
                # Go back to unlock menu with new directory
                self.unlock_files_menu()
    
    def list_locked_items(self):
        """List all locked items"""
        from datetime import datetime
        
        # Clear screen first
        self.clear_screen()
        
        locked_items = self.cli_handler.list_locked_items()
        
        if not locked_items:
            self.show_header()
            print(f"{Colors.TITLE}Locked Items{Colors.RESET}\n")
            print_warning("No locked items found.")
        else:
            # Show custom header with path
            from FadCrypt import __version__
            print(f"\n{Colors.BORDER}╭─ 🏴 {Colors.TITLE}FadCrypt v{__version__}{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET} {Colors.TEXT}File, Folder & Application Protection Suite{Colors.RESET}")
            # Show current directory path
            current_dir = self.directory_tracker.current_dir
            print(f"{Colors.BORDER}│{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET} {Colors.INFO}Current Directory:{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET} {Colors.DIM}{current_dir}{Colors.RESET}")
            print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}\n")
            
            # Display items without heading
            print(f"{Colors.BORDER}╭─ 📋 {Colors.TITLE}Items{Colors.RESET}")
            
            for idx, item in enumerate(locked_items):
                icon = Colors.ICON_FOLDER if item['type'] == 'folder' else Colors.ICON_FILE
                name = item['name']
                
                # Get file info
                try:
                    path = item['path']
                    if os.path.exists(path):
                        stat_info = os.stat(path)
                        size_mb = stat_info.st_size / (1024 * 1024)
                        modified_time = datetime.fromtimestamp(stat_info.st_mtime)
                        modified_str = modified_time.strftime("%d-%b-%Y %I:%M %p")
                        
                        if item['type'] == 'folder':
                            size_display = "" if size_mb == 0 else f"{size_mb:6.2f}MB"
                        else:
                            size_display = f"{max(0.01, size_mb):6.2f}MB"
                    else:
                        size_display = "N/A"
                        modified_str = "N/A"
                except:
                    size_display = "N/A"
                    modified_str = "N/A"
                
                # Display item with size and date (no path below)
                item_type = item['type'].capitalize()
                size_date = f"{size_display:>8}  {modified_str}" if size_display != "N/A" else modified_str
                print(f"{Colors.BORDER}│{Colors.RESET} {icon} {Colors.DIM}{item_type:<6}{Colors.RESET} {Colors.TEXT}{name:<40}{Colors.RESET} {Colors.DIM}{size_date}{Colors.RESET}")
            
            print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}")
            
            print(f"\n{Colors.INFO}Total: {len(locked_items)} item(s){Colors.RESET}")
            
            # Add teleport feature
            print(f"\n{Colors.WARNING}📍 Teleport to Location:{Colors.RESET}")
            
            # Get unique directories
            directories = {}
            for item in locked_items:
                dir_path = os.path.dirname(item['path'])
                if dir_path not in directories:
                    directories[dir_path] = []
                directories[dir_path].append(item['name'])
            
            # Show directories with item counts
            print(f"\n{Colors.BORDER}╭─ 📍 {Colors.TITLE}LOCATIONS ({len(directories)} unique){Colors.RESET}")
            for idx, (dir_path, items) in enumerate(directories.items(), 1):
                dir_name = os.path.basename(dir_path) or dir_path
                print(f"{Colors.BORDER}│{Colors.RESET} {Colors.SUCCESS}[{idx}]{Colors.RESET} {Colors.TEXT}{dir_name}{Colors.RESET} {Colors.DIM}({len(items)} item(s)){Colors.RESET}")
                print(f"{Colors.BORDER}│{Colors.RESET}   {Colors.DIM}└─ {dir_path}{Colors.RESET}")
            print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}")
            
            # Ask if user wants to teleport - consistent input style
            print(f"\n{Colors.INFO}Enter location number to teleport (or press Enter to go back):{Colors.RESET}")
            print(f" {Colors.ERROR}❯{Colors.RESET} ", end='')
            choice = input().strip()
            
            if choice.isdigit():
                idx = int(choice) - 1
                dir_list = list(directories.keys())
                if 0 <= idx < len(dir_list):
                    target_dir = dir_list[idx]
                    self.directory_tracker.current_dir = target_dir
                    print_success(f"Teleported to: {target_dir}")
                    input("\nPress Enter to continue...")
                    
                    # Go directly to unlock screen (user can switch to lock with [S])
                    items_in_dir = [item for item in locked_items if os.path.dirname(item['path']) == target_dir]
                    if items_in_dir:
                        selected_paths = show_unlock_selector(items_in_dir, "Select Items to Unlock", target_dir)
                        
                        # Check for special returns
                        if selected_paths and len(selected_paths) > 0:
                            if selected_paths[0] == '__SWITCH_TO_LOCK__':
                                # Switch to lock menu
                                locked_paths = {item['path'] for item in locked_items}
                                selected_paths = show_file_selector(target_dir, mode="lock", locked_paths=locked_paths)
                                
                                if selected_paths and len(selected_paths) > 0:
                                    actual_paths = [p for p in selected_paths if not p.startswith('__')]
                                    if actual_paths:
                                        self.show_header()
                                        print_colored(f"🔒 Locking {len(actual_paths)} item(s)...\n", Colors.INFO)
                                        success, failed, _ = self.cli_handler.lock_multiple(actual_paths)
                                        if success > 0:
                                            print_success(f"Successfully locked {success} item(s)!")
                                        if failed > 0:
                                            print_error(f"Failed to lock {failed} item(s).")
                                        input("\nPress Enter to continue...")
                            elif selected_paths[0] == '__TELEPORT__':
                                # Recursive teleport
                                self.show_teleport_menu(locked_items)
                                return
                            else:
                                # Normal unlock
                                actual_paths = [p for p in selected_paths if not p.startswith('__')]
                                if actual_paths:
                                    self.show_header()
                                    print_colored(f"🔓 Unlocking {len(actual_paths)} item(s)...\n", Colors.INFO)
                                    success, failed, _ = self.cli_handler.unlock_multiple(actual_paths)
                                    if success > 0:
                                        print_success(f"✅ Successfully unlocked {success} item(s)!")
                                    if failed > 0:
                                        print_error(f"Failed to unlock {failed} item(s).")
                                    input("\nPress Enter to continue...")
                    else:
                        print_warning("No locked items in this directory.")
                        input("\nPress Enter to continue...")
                    return
        
        input("\nPress Enter to continue...")
    
    def settings_menu(self):
        """Settings menu"""
        while True:
            settings_menu_items = [
                {'key': '1', 'icon': '🔑', 'text': 'Change Password', 'action': 'password'},
                {'key': '2', 'icon': '🔐', 'text': 'Generate Recovery Codes', 'action': 'recovery'},
                {'key': '3', 'icon': '⚠️', 'text': 'Dangerous Operations', 'action': 'dangerous'},
                {'key': '4', 'icon': '📖', 'text': 'About FadCrypt', 'action': 'about'},
                {'key': '5', 'icon': '🔙', 'text': 'Back to Main Menu', 'action': 'back'}
            ]
            
            choice = show_curses_menu("OPTIONS", settings_menu_items, "Back")
            
            if choice == '5' or choice == 'back' or choice == 'quit':
                break
            elif choice == '1':
                self.password_prompt.change_password()
                input("\nPress Enter to continue...")
            elif choice == '2':
                # Verify password before generating recovery codes (with recovery option)
                if self.password_prompt.verify_password_with_recovery():
                    self.password_prompt.generate_recovery_codes()
                input("\nPress Enter to continue...")
            elif choice == '3':
                self.dangerous_operations_menu()
            elif choice == '4':
                self.show_about()
    
    def dangerous_operations_menu(self):
        """Dangerous operations menu"""
        from core.file_protection import safe_write_to_protected_file
        import json
        
        while True:
            try:
                # Load current config
                config_file = os.path.join(self.cli_handler.config_folder, "apps_config.json")
                
                # Create config folder and default config if they don't exist
                if not os.path.exists(self.cli_handler.config_folder):
                    os.makedirs(self.cli_handler.config_folder, exist_ok=True)
                
                if not os.path.exists(config_file):
                    # Create default config using safe write
                    default_config = {
                        "applications": [],
                        "locked_files_and_folders": [],
                        "dangerous_operations": {
                            "encryption": False
                        }
                    }
                    config_content = json.dumps(default_config, indent=2)
                    safe_write_to_protected_file(config_file, config_content)
                    config = default_config
                else:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    
                    # Merge with default structure to ensure all required keys exist
                    default_config = {
                        "applications": [],
                        "locked_files_and_folders": [],
                        "dangerous_operations": {
                            "encryption": False
                        }
                    }
                    # Deep merge: preserve existing values, add missing keys
                    for key, default_value in default_config.items():
                        if key not in config:
                            config[key] = default_value
                        elif isinstance(default_value, dict) and isinstance(config[key], dict):
                            # Merge nested dicts
                            for nested_key, nested_default in default_value.items():
                                if nested_key not in config[key]:
                                    config[key][nested_key] = nested_default
                
                # Ensure dangerous_operations key exists
                if "dangerous_operations" not in config:
                    config["dangerous_operations"] = {"encryption": True}
                
                dangerous_ops = config.get("dangerous_operations", {})
                encryption_enabled = dangerous_ops.get("encryption", False)
                
                self.show_header()
                print_colored("DANGEROUS OPERATIONS", Colors.TITLE)
                print(f"\n{Colors.BORDER}Current Settings:{Colors.RESET}\n")
                print(f"  [1] File/Folder Encryption: {'ENABLED ✓' if encryption_enabled else 'DISABLED'}")
                
                print(f"\n{Colors.BORDER}Description:{Colors.RESET}\n")
                if encryption_enabled:
                    print(Colors.INFO + """
  When ENABLED:
  • Files/folders are ENCRYPTED with AES-256 when locked
  • Files are converted to .fadcrypt format (encrypted binary data)
  • Locked files are COMPLETELY INACCESSIBLE without password
  • Unlocking decrypts files back to original format
  • Decryption requires your MASTER PASSWORD
  • Encryption is IRREVERSIBLE - keep recovery codes safe
  • If password is forgotten, recovery codes allow reset
""" + Colors.RESET)
                else:
                    print(Colors.INFO + """
  When DISABLED (Current):
  • Files/folders are protected using Access Control Lists (ACLs) only
  • Files remain readable when unlocked
  • Fast lock/unlock operations
  • No encryption overhead
""" + Colors.RESET)
                
                print(f"{Colors.BORDER}Actions:{Colors.RESET}\n")
                print_colored("  [E] Enable Encryption", Colors.TITLE if not encryption_enabled else Colors.DIM)
                print_colored("  [D] Disable Encryption", Colors.TITLE if encryption_enabled else Colors.DIM)
                print_colored("  [B] Back to Settings", Colors.TITLE)
                
                choice = input(f"\n{Colors.DIM}[Select option]: {Colors.RESET}").strip().upper()
                
                if choice == 'B':
                    break
                elif choice == 'E':
                    if not encryption_enabled:
                        config["dangerous_operations"]["encryption"] = True
                        content = json.dumps(config, indent=2)
                        success, error = safe_write_to_protected_file(config_file, content)
                        if success:
                            print_success("✓ Encryption ENABLED")
                        else:
                            print_error(f"Failed to save settings: {error}")
                    else:
                        print_warning("Encryption is already enabled")
                    input("\nPress Enter to continue...")
                elif choice == 'D':
                    if encryption_enabled:
                        config["dangerous_operations"]["encryption"] = False
                        content = json.dumps(config, indent=2)
                        success, error = safe_write_to_protected_file(config_file, content)
                        if success:
                            print_success("✓ Encryption DISABLED")
                        else:
                            print_error(f"Failed to save settings: {error}")
                    else:
                        print_warning("Encryption is already disabled")
                    input("\nPress Enter to continue...")
                
            except Exception as e:
                print_error(f"Error accessing dangerous operations: {e}")
                import traceback
                traceback.print_exc()
                input("\nPress Enter to continue...")
    
    def show_about(self):
        """Show about information with menu navigation at bottom"""
        from ..version import __version__
        
        # Custom menu that displays about info
        class AboutMenu:
            def __init__(self):
                self.cursor_pos = 0
                self.running = True
                self.menu_items = [
                    {'key': '1', 'icon': '⬅️', 'text': 'Back to Settings', 'action': 'back'}
                ]
            
            def run(self, stdscr):
                import curses
                import time
                
                self.stdscr = stdscr
                self.stdscr.keypad(True)
                curses.curs_set(0)
                
                # Setup colors
                curses.start_color()
                try:
                    curses.use_default_colors()
                except AttributeError:
                    pass
                
                curses.init_pair(1, curses.COLOR_RED, -1)
                curses.init_pair(2, curses.COLOR_WHITE, -1)
                curses.init_pair(3, curses.COLOR_GREEN, -1)
                curses.init_pair(4, 8, -1)
                curses.init_pair(7, 8, -1)
                
                while self.running:
                    try:
                        self.stdscr.clear()
                        height, width = self.stdscr.getmaxyx()
                        
                        # Calculate centering
                        box_width = min(70, width - 4)
                        start_col = (width - box_width) // 2
                        
                        # Draw header
                        header_y = 1
                        try:
                            self.stdscr.addstr(header_y, start_col, "╭─ ", curses.color_pair(1))
                            self.stdscr.addstr(header_y, start_col + 3, f"🏴 FadCrypt v{__version__}", curses.color_pair(1) | curses.A_BOLD)
                            self.stdscr.addstr(header_y + 1, start_col, "│ ", curses.color_pair(1))
                            self.stdscr.addstr(header_y + 1, start_col + 2, "File, Folder & Application Protection Suite", curses.color_pair(2))
                            self.stdscr.addstr(header_y + 2, start_col, "╰" + "─" * (box_width - 2), curses.color_pair(1))
                        except curses.error:
                            pass
                        
                        # Draw "About FadCrypt" title
                        title_y = header_y + 4
                        title_text = "About FadCrypt"
                        title_col = (width - len(title_text)) // 2
                        try:
                            self.stdscr.addstr(title_y, title_col, title_text, curses.color_pair(1) | curses.A_BOLD)
                        except curses.error:
                            pass
                        
                        # Draw INFORMATION box
                        info_y = title_y + 2
                        try:
                            self.stdscr.addstr(info_y, start_col, "╭─ ℹ️ INFORMATION", curses.color_pair(1))
                            self.stdscr.addstr(info_y + 1, start_col, "│", curses.color_pair(1))
                            self.stdscr.addstr(info_y + 2, start_col, "│ ", curses.color_pair(1))
                            self.stdscr.addstr(info_y + 2, start_col + 2, f"FadCrypt v{__version__}", curses.color_pair(2))
                            self.stdscr.addstr(info_y + 3, start_col, "│ ", curses.color_pair(1))
                            self.stdscr.addstr(info_y + 3, start_col + 2, "Cross-platform File, Folder & Application Protection", curses.color_pair(2))
                            self.stdscr.addstr(info_y + 4, start_col, "│", curses.color_pair(1))
                            self.stdscr.addstr(info_y + 5, start_col, "│ ", curses.color_pair(1))
                            self.stdscr.addstr(info_y + 5, start_col + 2, f"Platform: {platform.system()}", curses.color_pair(4))
                            self.stdscr.addstr(info_y + 6, start_col, "│ ", curses.color_pair(1))
                            self.stdscr.addstr(info_y + 6, start_col + 2, f"Python: {sys.version.split()[0]}", curses.color_pair(4))
                            self.stdscr.addstr(info_y + 7, start_col, "│", curses.color_pair(1))
                            self.stdscr.addstr(info_y + 8, start_col, "│ ", curses.color_pair(1))
                            self.stdscr.addstr(info_y + 8, start_col + 2, "FadSec Lab", curses.color_pair(2))
                            self.stdscr.addstr(info_y + 9, start_col, "│ ", curses.color_pair(1))
                            self.stdscr.addstr(info_y + 9, start_col + 2, "https://faded.dev · © 2024–2025 · GPLv3 License", curses.color_pair(3))
                            self.stdscr.addstr(info_y + 10, start_col, "╰" + "─" * (box_width - 2), curses.color_pair(1))
                        except curses.error:
                            pass
                        
                        # Draw LINKS & SUPPORT box
                        links_y = info_y + 12
                        try:
                            self.stdscr.addstr(links_y, start_col, "╭─ 🔗 LINKS & SUPPORT", curses.color_pair(1))
                            self.stdscr.addstr(links_y + 1, start_col, "│", curses.color_pair(1))
                            self.stdscr.addstr(links_y + 2, start_col, "│ ", curses.color_pair(1))
                            self.stdscr.addstr(links_y + 2, start_col + 2, "🌐 ", curses.color_pair(1))
                            self.stdscr.addstr(links_y + 2, start_col + 5, "GitHub: ", curses.color_pair(2))
                            self.stdscr.addstr(links_y + 2, start_col + 13, "https://github.com/anonfaded/FadCrypt", curses.color_pair(3))
                            self.stdscr.addstr(links_y + 3, start_col, "│", curses.color_pair(1))
                            self.stdscr.addstr(links_y + 4, start_col, "│ ", curses.color_pair(1))
                            self.stdscr.addstr(links_y + 4, start_col + 2, "💬 ", curses.color_pair(1))
                            self.stdscr.addstr(links_y + 4, start_col + 5, "Discord: ", curses.color_pair(2))
                            self.stdscr.addstr(links_y + 4, start_col + 14, "https://discord.gg/kvAZvdkuuN", curses.color_pair(3))
                            self.stdscr.addstr(links_y + 5, start_col, "│", curses.color_pair(1))
                            self.stdscr.addstr(links_y + 6, start_col, "│ ", curses.color_pair(1))
                            self.stdscr.addstr(links_y + 6, start_col + 2, "☕ ", curses.color_pair(1))
                            self.stdscr.addstr(links_y + 6, start_col + 5, "Ko-fi: ", curses.color_pair(2))
                            self.stdscr.addstr(links_y + 6, start_col + 12, "https://ko-fi.com/fadedx", curses.color_pair(3))
                            self.stdscr.addstr(links_y + 7, start_col, "╰" + "─" * (box_width - 2), curses.color_pair(1))
                        except curses.error:
                            pass
                        
                        # Draw menu items at bottom
                        menu_y = links_y + 9
                        try:
                            self.stdscr.addstr(menu_y, start_col, "╭─ 📋 NAVIGATION", curses.color_pair(1))
                            for idx, item in enumerate(self.menu_items):
                                menu_y += 1
                                if idx == self.cursor_pos:
                                    self.stdscr.addstr(menu_y, start_col, "│ ", curses.color_pair(1))
                                    self.stdscr.addstr(menu_y, start_col + 2, "► ", curses.color_pair(3) | curses.A_BOLD)
                                    self.stdscr.addstr(menu_y, start_col + 4, f"[{item['key']}] {item['icon']} {item['text']}", curses.color_pair(3) | curses.A_BOLD)
                                else:
                                    self.stdscr.addstr(menu_y, start_col, "│ ", curses.color_pair(1))
                                    self.stdscr.addstr(menu_y, start_col + 2, f"[{item['key']}] {item['icon']} {item['text']}", curses.color_pair(2))
                            
                            menu_y += 1
                            self.stdscr.addstr(menu_y, start_col, "╰" + "─" * (box_width - 2), curses.color_pair(1))
                        except curses.error:
                            pass
                        
                        self.stdscr.refresh()
                        
                        key = self.stdscr.getch()
                        
                        if key == curses.KEY_UP:
                            self.cursor_pos = max(0, self.cursor_pos - 1)
                        elif key == curses.KEY_DOWN:
                            self.cursor_pos = min(len(self.menu_items) - 1, self.cursor_pos + 1)
                        elif key == ord('\n') or key == ord('\r'):
                            self.running = False
                            return self.menu_items[self.cursor_pos]['key']
                        elif key == ord('b') or key == ord('B'):
                            self.running = False
                            return 'back'
                        elif key == ord('q') or key == ord('Q'):
                            self.running = False
                            return 'quit'
                        elif key >= ord('1') and key <= ord('9'):
                            for item in self.menu_items:
                                if item['key'] == chr(key):
                                    self.running = False
                                    return item['key']
                    
                    except:
                        pass
                    
                    time.sleep(0.05)
        
        # Run the about menu
        try:
            import curses
            def _about_wrapper(stdscr):
                menu = AboutMenu()
                return menu.run(stdscr)
            
            curses.wrapper(_about_wrapper)
        except Exception:
            pass
    
    def launch_gui(self):
        """Launch the GUI application"""
        self.show_header()
        print_colored("Launch GUI Application\n", Colors.TITLE)
        
        print_info("To launch the GUI, open a new terminal and run:")
        print_colored("  fadcrypt --gui\n", Colors.HIGHLIGHT)
        
        print_warning("Note: The GUI cannot be launched from within this CLI interface.")
        
        input("\nPress Enter to continue...")
