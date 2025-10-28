"""
TUI Manager

Main text-based user interface for FadCrypt CLI.
"""

import os
import sys
import platform
from typing import Optional

from .colors import Colors, BoxChars, print_colored, print_success, print_error, print_warning, print_info
from .password_prompt import PasswordPrompt
from .file_selector import FileSelector


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
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_header(self):
        """Display the FadCrypt header"""
        self.clear_screen()
        print_colored(f"{BoxChars.TOP_LEFT}{BoxChars.HORIZONTAL * 61}{BoxChars.TOP_RIGHT}", Colors.BORDER)
        print_colored(f"{BoxChars.VERTICAL}{Colors.ICON_LOCK} FadCrypt v2.0{' ' * 44}{BoxChars.VERTICAL}", Colors.TITLE)
        print_colored(f"{BoxChars.VERTICAL}{'File & Folder Protection Suite':^61}{BoxChars.VERTICAL}", Colors.TITLE)
        print_colored(f"{BoxChars.BOTTOM_LEFT}{BoxChars.HORIZONTAL * 61}{BoxChars.BOTTOM_RIGHT}\n", Colors.BORDER)
    
    def show_main_menu(self):
        """Display the main menu"""
        self.show_header()
        
        print_colored(f"{BoxChars.S_TOP_LEFT}{BoxChars.S_HORIZONTAL * 61}{BoxChars.S_TOP_RIGHT}", Colors.BORDER)
        print_colored(f"{BoxChars.S_VERTICAL}{'MAIN MENU':^61}{BoxChars.S_VERTICAL}", Colors.TITLE)
        print_colored(f"{BoxChars.S_T_RIGHT}{BoxChars.S_HORIZONTAL * 61}{BoxChars.S_T_LEFT}", Colors.BORDER)
        print_colored(f"{BoxChars.S_VERTICAL}{' ' * 61}{BoxChars.S_VERTICAL}", Colors.TEXT)
        print_colored(f"{BoxChars.S_VERTICAL}  1. {Colors.ICON_LOCK} Lock Files/Folders{' ' * 35}{BoxChars.S_VERTICAL}", Colors.TEXT)
        print_colored(f"{BoxChars.S_VERTICAL}  2. {Colors.ICON_UNLOCK} Unlock Files/Folders{' ' * 33}{BoxChars.S_VERTICAL}", Colors.TEXT)
        print_colored(f"{BoxChars.S_VERTICAL}  3. 📋 List Locked Items{' ' * 36}{BoxChars.S_VERTICAL}", Colors.TEXT)
        print_colored(f"{BoxChars.S_VERTICAL}  4. 🖥️  Open GUI Application{' ' * 33}{BoxChars.S_VERTICAL}", Colors.TEXT)
        print_colored(f"{BoxChars.S_VERTICAL}  5. ⚙️  Settings{' ' * 46}{BoxChars.S_VERTICAL}", Colors.TEXT)
        print_colored(f"{BoxChars.S_VERTICAL}  6. ❌ Exit{' ' * 50}{BoxChars.S_VERTICAL}", Colors.TEXT)
        print_colored(f"{BoxChars.S_VERTICAL}{' ' * 61}{BoxChars.S_VERTICAL}", Colors.TEXT)
        print_colored(f"{BoxChars.S_BOTTOM_LEFT}{BoxChars.S_HORIZONTAL * 61}{BoxChars.S_BOTTOM_RIGHT}\n", Colors.BORDER)
    
    def run(self):
        """Run the main TUI loop"""
        # Ensure password exists
        if not self.password_prompt.ensure_password_exists():
            print_error("Cannot proceed without a master password.")
            return
        
        while True:
            self.show_main_menu()
            
            print_colored("Enter your choice (1-6): ", Colors.PRIMARY, end='')
            try:
                choice = input().strip()
            except KeyboardInterrupt:
                print()
                break
            
            if choice == '1':
                self.lock_files_menu()
            elif choice == '2':
                self.unlock_files_menu()
            elif choice == '3':
                self.list_locked_items()
            elif choice == '4':
                self.launch_gui()
            elif choice == '5':
                self.settings_menu()
            elif choice == '6':
                print_success("Goodbye!")
                break
            else:
                print_error("Invalid choice. Please enter a number between 1 and 6.")
                input("\nPress Enter to continue...")
    
    def lock_files_menu(self):
        """Lock files/folders menu"""
        self.show_header()
        print_colored("Lock Files/Folders\n", Colors.TITLE)
        
        # Verify password first
        if not self.password_prompt.verify_password():
            input("\nPress Enter to continue...")
            return
        
        print_colored("\nSelect files/folders to lock:\n", Colors.INFO)
        print_colored("1. Browse current directory", Colors.TEXT)
        print_colored("2. Enter path manually", Colors.TEXT)
        print_colored("3. Back to main menu\n", Colors.TEXT)
        
        print_colored("Enter your choice (1-3): ", Colors.PRIMARY, end='')
        choice = input().strip()
        
        if choice == '1':
            # Interactive file selector
            selected_paths = self.file_selector.select_files()
            
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
            print_colored("\nEnter path to lock: ", Colors.PRIMARY, end='')
            path = input().strip()
            
            if path:
                path = os.path.abspath(path)
                print_colored(f"\nLocking {path}...", Colors.INFO)
                
                if self.cli_handler.lock_path(path):
                    print_success("Successfully locked!")
                else:
                    print_error("Failed to lock. Path may not exist or already locked.")
                
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
        print_colored("Locked Items\n", Colors.TITLE)
        
        locked_items = self.cli_handler.list_locked_items()
        
        if not locked_items:
            print_warning("No locked items found.")
        else:
            print_colored(f"{BoxChars.S_TOP_LEFT}{BoxChars.S_HORIZONTAL * 61}{BoxChars.S_TOP_RIGHT}", Colors.BORDER)
            print_colored(f"{BoxChars.S_VERTICAL}{'Type':<8}{'Name':<50}{BoxChars.S_VERTICAL}", Colors.TITLE)
            print_colored(f"{BoxChars.S_T_RIGHT}{BoxChars.S_HORIZONTAL * 61}{BoxChars.S_T_LEFT}", Colors.BORDER)
            
            for item in locked_items:
                icon = Colors.ICON_FOLDER if item['type'] == 'folder' else Colors.ICON_FILE
                name = item['name']
                if len(name) > 48:
                    name = name[:45] + '...'
                
                item_type = item['type'].capitalize()
                line = f"{BoxChars.S_VERTICAL} {icon} {item_type:<6}{name:<48}{BoxChars.S_VERTICAL}"
                print_colored(line, Colors.TEXT)
            
            print_colored(f"{BoxChars.S_BOTTOM_LEFT}{BoxChars.S_HORIZONTAL * 61}{BoxChars.S_BOTTOM_RIGHT}", Colors.BORDER)
            print_colored(f"\nTotal: {len(locked_items)} item(s)", Colors.INFO)
        
        input("\nPress Enter to continue...")
    
    def settings_menu(self):
        """Settings menu"""
        while True:
            self.show_header()
            print_colored("Settings\n", Colors.TITLE)
            
            print_colored(f"{BoxChars.S_TOP_LEFT}{BoxChars.S_HORIZONTAL * 61}{BoxChars.S_TOP_RIGHT}", Colors.BORDER)
            print_colored(f"{BoxChars.S_VERTICAL}{' ' * 61}{BoxChars.S_VERTICAL}", Colors.TEXT)
            print_colored(f"{BoxChars.S_VERTICAL}  1. 🔑 Change Password{' ' * 38}{BoxChars.S_VERTICAL}", Colors.TEXT)
            print_colored(f"{BoxChars.S_VERTICAL}  2. 🔐 Generate Recovery Codes{' ' * 31}{BoxChars.S_VERTICAL}", Colors.TEXT)
            print_colored(f"{BoxChars.S_VERTICAL}  3. ℹ️  About FadCrypt{' ' * 39}{BoxChars.S_VERTICAL}", Colors.TEXT)
            print_colored(f"{BoxChars.S_VERTICAL}  4. ⬅️  Back to Main Menu{' ' * 36}{BoxChars.S_VERTICAL}", Colors.TEXT)
            print_colored(f"{BoxChars.S_VERTICAL}{' ' * 61}{BoxChars.S_VERTICAL}", Colors.TEXT)
            print_colored(f"{BoxChars.S_BOTTOM_LEFT}{BoxChars.S_HORIZONTAL * 61}{BoxChars.S_BOTTOM_RIGHT}\n", Colors.BORDER)
            
            print_colored("Enter your choice (1-4): ", Colors.PRIMARY, end='')
            choice = input().strip()
            
            if choice == '1':
                self.password_prompt.change_password()
                input("\nPress Enter to continue...")
            elif choice == '2':
                self.password_prompt.generate_recovery_codes()
            elif choice == '3':
                self.show_about()
            elif choice == '4':
                break
            else:
                print_error("Invalid choice.")
                input("\nPress Enter to continue...")
    
    def show_about(self):
        """Show about information"""
        self.show_header()
        print_colored("About FadCrypt\n", Colors.TITLE)
        
        print_colored(f"{BoxChars.S_TOP_LEFT}{BoxChars.S_HORIZONTAL * 61}{BoxChars.S_TOP_RIGHT}", Colors.BORDER)
        print_colored(f"{BoxChars.S_VERTICAL} FadCrypt v2.0{' ' * 48}{BoxChars.S_VERTICAL}", Colors.TEXT)
        print_colored(f"{BoxChars.S_VERTICAL} Cross-platform File & Folder Protection{' ' * 21}{BoxChars.S_VERTICAL}", Colors.TEXT)
        print_colored(f"{BoxChars.S_VERTICAL}{' ' * 61}{BoxChars.S_VERTICAL}", Colors.TEXT)
        print_colored(f"{BoxChars.S_VERTICAL} Platform: {platform.system()}{' ' * (50 - len(platform.system()))}{BoxChars.S_VERTICAL}", Colors.TEXT)
        print_colored(f"{BoxChars.S_VERTICAL} Python: {sys.version.split()[0]}{' ' * (52 - len(sys.version.split()[0]))}{BoxChars.S_VERTICAL}", Colors.TEXT)
        print_colored(f"{BoxChars.S_VERTICAL}{' ' * 61}{BoxChars.S_VERTICAL}", Colors.TEXT)
        print_colored(f"{BoxChars.S_VERTICAL} © 2024-2025 FadSec Lab{' ' * 37}{BoxChars.S_VERTICAL}", Colors.TEXT)
        print_colored(f"{BoxChars.S_BOTTOM_LEFT}{BoxChars.S_HORIZONTAL * 61}{BoxChars.S_BOTTOM_RIGHT}", Colors.BORDER)
        
        input("\nPress Enter to continue...")
    
    def launch_gui(self):
        """Launch the GUI application"""
        self.show_header()
        print_colored("Launching GUI application...\n", Colors.INFO)
        
        try:
            # Import and launch GUI
            from PyQt6.QtWidgets import QApplication
            
            # Check if QApplication already exists
            app = QApplication.instance()
            if app is None:
                print_info("Starting GUI...")
                # This will be handled by the main entry point
                print_warning("Please use 'fadcrypt --gui' to launch the GUI.")
            else:
                print_warning("GUI is already running.")
        except ImportError:
            print_error("PyQt6 is not installed. Cannot launch GUI.")
        except Exception as e:
            print_error(f"Error launching GUI: {e}")
        
        input("\nPress Enter to continue...")
