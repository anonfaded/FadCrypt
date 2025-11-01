"""
TUI Manager

Main text-based user interface for FadCrypt CLI.
"""

import os
import sys
import platform

from .colors import Colors, print_colored, print_success, print_error, print_warning, print_info
from .password_prompt import PasswordPrompt
from .file_selector import FileSelector
from .menu_navigator import MenuNavigator
from .curses_menu import show_curses_menu, CURSES_AVAILABLE


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
        self.file_selector = FileSelector()
        self.menu_navigator = MenuNavigator()
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_header(self):
        """Display the FadCrypt header"""
        from FadCrypt import __version__
        
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
        
        # Try curses menu first (with animation)
        if CURSES_AVAILABLE:
            try:
                choice = show_curses_menu("MAIN MENU", main_menu_items)
                if choice:
                    return choice
            except Exception:
                pass  # Fall back to regular menu
        
        # Fallback to regular menu
        return self.menu_navigator.show_menu("MAIN MENU", main_menu_items, self.show_header)
    
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
                    print_success("Goodbye! :)")
                    break
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
    
    def lock_files_menu(self):
        """Lock files/folders menu"""
        self.show_header()
        print_colored("Lock Files/Folders\n", Colors.TITLE)
        
        lock_menu_items = [
            {'key': '1', 'icon': '📁', 'text': 'Browse current directory', 'action': 'browse'},
            {'key': '2', 'icon': '📝', 'text': 'Enter path manually', 'action': 'manual'},
            {'key': '3', 'icon': '🔙', 'text': 'Back to main menu', 'action': 'back'}
        ]
        
        choice = self.menu_navigator.show_menu("SELECT FILES/FOLDERS TO LOCK", lock_menu_items, self.show_header)
        
        if choice == '3' or choice == 'back' or choice == 'quit':
            return
        elif choice == '1':
            # Interactive file selector
            # Get currently locked items to show indicators
            locked_items = self.cli_handler.list_locked_items()
            locked_paths = {item['path'] for item in locked_items}
            
            selected_paths = self.file_selector.select_files(locked_paths=locked_paths)
            
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
                    print_colored(f"Locking {len(actual_paths)} item(s)...\n", Colors.INFO)
                    
                    success, failed = self.cli_handler.lock_multiple(actual_paths)
                    
                    if success > 0:
                        print_success(f"Successfully locked {success} item(s)!")
                    if failed > 0:
                        print_error(f"Failed to lock {failed} item(s).")
                    
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
    
    def unlock_files_menu(self):
        """Unlock files/folders menu"""
        self.show_header()
        print_colored("Unlock Files/Folders\n", Colors.TITLE)
        
        # Get locked items
        locked_items = self.cli_handler.list_locked_items()
        
        if not locked_items:
            print_warning("No locked items found.")
            input("\nPress Enter to continue...")
            return
        
        # Loop to handle refiltering
        while True:
            # Filter items based on filter mode
            current_dir = self.file_selector.current_dir
            items_in_current_dir = [item for item in locked_items if os.path.dirname(item['path']) == current_dir]
            
            # Determine what to show based on filter mode
            if hasattr(self.file_selector, 'unlock_filter_mode') and self.file_selector.unlock_filter_mode == "all":
                items_to_show = locked_items  # Show all locations
            else:
                # Show current directory only
                items_to_show = items_in_current_dir
                # If no items in current dir, show message and switch to all
                if not items_to_show:
                    print_warning(f"No locked items in current directory: {current_dir}")
                    print_info("Switching to 'All Locations' mode...")
                    self.file_selector.unlock_filter_mode = "all"
                    input("\nPress Enter to continue...")
                    continue  # Re-run with all locations
            
            # Show locked items for selection
            selected_paths = self.file_selector.select_from_list(items_to_show, "Select Items to Unlock")
            
            # Check if refilter requested
            if selected_paths and selected_paths[0] == '__REFILTER__':
                continue  # Re-run the loop with new filter
            else:
                break  # Exit loop and process results
        
        # Check for special returns
        if selected_paths and selected_paths[0] == '__SWITCH_TO_LOCK__':
            # Switch to lock screen directly (not menu)
            locked_paths = {item['path'] for item in locked_items}
            selected_paths = self.file_selector.select_files(locked_paths=locked_paths)
            
            # Handle results from lock screen
            if selected_paths and len(selected_paths) > 0:
                # Check for switch back
                if selected_paths[0] == '__SWITCH_TO_UNLOCK__':
                    self.unlock_files_menu()
                    return
                elif selected_paths[0] == '__TELEPORT__':
                    self.show_teleport_menu(locked_items)
                    return
                
                # Normal lock operation
                actual_paths = [p for p in selected_paths if not p.startswith('__')]
                if actual_paths:
                    self.show_header()
                    print_colored(f"Locking {len(actual_paths)} item(s)...\n", Colors.INFO)
                    success, failed = self.cli_handler.lock_multiple(actual_paths)
                    if success > 0:
                        print_success(f"Successfully locked {success} item(s)!")
                    if failed > 0:
                        print_error(f"Failed to lock {failed} item(s).")
                    input("\nPress Enter to continue...")
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
                print_colored(f"Unlocking {len(actual_paths)} item(s)...\n", Colors.INFO)
                
                success, failed = self.cli_handler.unlock_multiple(actual_paths)
                
                if success > 0:
                    print_success(f"Successfully unlocked {success} item(s)!")
                if failed > 0:
                    print_error(f"Failed to unlock {failed} item(s).")
                
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
                self.file_selector.current_dir = target_dir
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
            # Show path of first item
            first_item_path = locked_items[0]['path']
            print(f"{Colors.BORDER}│{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET} {Colors.INFO}Current Item Path:{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET} {Colors.DIM}{first_item_path}{Colors.RESET}")
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
                    self.file_selector.current_dir = target_dir
                    print_success(f"Teleported to: {target_dir}")
                    input("\nPress Enter to continue...")
                    
                    # Go directly to unlock screen (user can switch to lock with [S])
                    items_in_dir = [item for item in locked_items if os.path.dirname(item['path']) == target_dir]
                    if items_in_dir:
                        selected_paths = self.file_selector.select_from_list(items_in_dir, "Select Items to Unlock")
                        
                        # Check for special returns
                        if selected_paths and len(selected_paths) > 0:
                            if selected_paths[0] == '__SWITCH_TO_LOCK__':
                                # Switch to lock menu
                                locked_paths = {item['path'] for item in locked_items}
                                selected_paths = self.file_selector.select_files(locked_paths=locked_paths)
                                
                                if selected_paths and len(selected_paths) > 0:
                                    actual_paths = [p for p in selected_paths if not p.startswith('__')]
                                    if actual_paths:
                                        self.show_header()
                                        print_colored(f"Locking {len(actual_paths)} item(s)...\n", Colors.INFO)
                                        success, failed = self.cli_handler.lock_multiple(actual_paths)
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
                                    print_colored(f"Unlocking {len(actual_paths)} item(s)...\n", Colors.INFO)
                                    success, failed = self.cli_handler.unlock_multiple(actual_paths)
                                    if success > 0:
                                        print_success(f"Successfully unlocked {success} item(s)!")
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
                {'key': '3', 'icon': '📖', 'text': 'About FadCrypt', 'action': 'about'},
                {'key': '4', 'icon': '🔙', 'text': 'Back to Main Menu', 'action': 'back'}
            ]
            
            def settings_header():
                self.show_header()
                print(f"{Colors.TITLE}Settings{Colors.RESET}\n")
            
            choice = self.menu_navigator.show_menu("OPTIONS", settings_menu_items, settings_header)
            
            if choice == '4' or choice == 'back' or choice == 'quit':
                break
            elif choice == '1':
                self.password_prompt.change_password()
                input("\nPress Enter to continue...")
            elif choice == '2':
                # Verify password before generating recovery codes
                if self.password_prompt.verify_password():
                    self.password_prompt.generate_recovery_codes()
                else:
                    input("\nPress Enter to continue...")
            elif choice == '3':
                self.show_about()
    
    def show_about(self):
        """Show about information"""
        from FadCrypt import __version__
        
        self.show_header()
        print(f"{Colors.TITLE}About FadCrypt{Colors.RESET}\n")
        
        print(f"{Colors.BORDER}╭─ {Colors.TITLE}INFORMATION{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.TEXT}FadCrypt v{__version__}{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.TEXT}Cross-platform File, Folder & Application Protection{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.INFO}Platform:{Colors.RESET} {platform.system()}")
        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.INFO}Python:{Colors.RESET} {sys.version.split()[0]}")
        print(f"{Colors.BORDER}│{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.DIM}© 2024-2025 FadSec Lab{Colors.RESET}")
        print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}")
        
        # Add links section
        print(f"\n{Colors.BORDER}╭─ {Colors.TITLE}LINKS & SUPPORT{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.SUCCESS}🌐 GitHub:{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET}   {Colors.HIGHLIGHT}https://github.com/anonfaded/FadCrypt{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.SUCCESS}💬 Discord Community:{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET}   {Colors.HIGHLIGHT}https://discord.gg/kvAZvdkuuN{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.SUCCESS}☕ Support Development (Ko-fi):{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET}   {Colors.HIGHLIGHT}https://ko-fi.com/fadedx{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET}")
        print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}")
        
        input("\nPress Enter to continue...")
    
    def launch_gui(self):
        """Launch the GUI application"""
        self.show_header()
        print_colored("Launch GUI Application\n", Colors.TITLE)
        
        print_info("To launch the GUI, open a new terminal and run:")
        print_colored("  fadcrypt --gui\n", Colors.HIGHLIGHT)
        
        print_warning("Note: The GUI cannot be launched from within this CLI interface.")
        
        input("\nPress Enter to continue...")
