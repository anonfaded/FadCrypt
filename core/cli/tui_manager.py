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
            {'key': '1', 'icon': Colors.ICON_LOCK, 'text': 'Lock Files/Folders', 'action': 'lock'},
            {'key': '2', 'icon': Colors.ICON_UNLOCK, 'text': 'Unlock Files/Folders', 'action': 'unlock'},
            {'key': '3', 'icon': '📋', 'text': 'List Locked Items', 'action': 'list'},
            {'key': '4', 'icon': '💻', 'text': 'Open GUI Application', 'action': 'gui'},
            {'key': '5', 'icon': '🔧', 'text': 'Settings', 'action': 'settings'},
            {'key': '6', 'icon': '❌', 'text': 'Exit', 'action': 'exit'}
        ]
        
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
        
        # Verify password first
        if not self.password_prompt.verify_password():
            input("\nPress Enter to continue...")
            return
        
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
            
            if selected_paths:
                self.show_header()
                print_colored(f"Locking {len(selected_paths)} item(s)...\n", Colors.INFO)
                
                success, failed = self.cli_handler.lock_multiple(selected_paths)
                
                if success > 0:
                    print_success(f"Successfully locked {success} item(s)!")
                if failed > 0:
                    print_error(f"Failed to lock {failed} item(s).")
                
                input("\nPress Enter to continue...")
        
        elif choice == '2':
            # Manual path entry
            print(f"\n{Colors.PRIMARY}Enter path to lock:")
            print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
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
        
        # Verify password first
        if not self.password_prompt.verify_password():
            input("\nPress Enter to continue...")
            return
        
        # Get locked items
        locked_items = self.cli_handler.list_locked_items()
        
        if not locked_items:
            print_warning("No locked items found.")
            input("\nPress Enter to continue...")
            return
        
        # Show locked items for selection
        selected_paths = self.file_selector.select_from_list(locked_items, "Select Items to Unlock")
        
        if selected_paths:
            self.show_header()
            print_colored(f"Unlocking {len(selected_paths)} item(s)...\n", Colors.INFO)
            
            success, failed = self.cli_handler.unlock_multiple(selected_paths)
            
            if success > 0:
                print_success(f"Successfully unlocked {success} item(s)!")
            if failed > 0:
                print_error(f"Failed to unlock {failed} item(s).")
            
            input("\nPress Enter to continue...")
    
    def list_locked_items(self):
        """List all locked items"""
        self.show_header()
        print(f"{Colors.TITLE}Locked Items{Colors.RESET}\n")
        
        locked_items = self.cli_handler.list_locked_items()
        
        if not locked_items:
            print_warning("No locked items found.")
        else:
            print(f"{Colors.BORDER}╭─ {Colors.TITLE}LOCKED ITEMS{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET}")
            
            for item in locked_items:
                icon = Colors.ICON_FOLDER if item['type'] == 'folder' else Colors.ICON_FILE
                name = item['name']
                if len(name) > 50:
                    name = name[:47] + '...'
                
                item_type = item['type'].capitalize()
                print(f"{Colors.BORDER}│{Colors.RESET} {icon} {Colors.DIM}{item_type:<6}{Colors.RESET} {Colors.TEXT}{name}{Colors.RESET}")
            
            print(f"{Colors.BORDER}│{Colors.RESET}")
            print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}")
            print(f"\n{Colors.INFO}Total: {len(locked_items)} item(s){Colors.RESET}")
        
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
        
        input("\nPress Enter to continue...")
    
    def launch_gui(self):
        """Launch the GUI application"""
        self.show_header()
        print_colored("Launch GUI Application\n", Colors.TITLE)
        
        print_info("To launch the GUI, open a new terminal and run:")
        print_colored("  fadcrypt --gui\n", Colors.HIGHLIGHT)
        
        print_warning("Note: The GUI cannot be launched from within this CLI interface.")
        
        input("\nPress Enter to continue...")
