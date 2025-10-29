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
        from FadCrypt import __version__
        
        self.clear_screen()
        print(f"{Colors.BORDER}╭─ {Colors.TITLE}🏴 FadCrypt v{__version__}{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.TITLE}File, Folder & Application Protection Suite{Colors.RESET}")
        print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}\n")
    
    def show_main_menu(self):
        """Display the main menu"""
        self.show_header()
        
        print(f"{Colors.BORDER}╭─ {Colors.TITLE}MAIN MENU{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.DIM}1.{Colors.RESET} {Colors.ICON_LOCK} {Colors.TEXT}Lock Files/Folders{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.DIM}2.{Colors.RESET} {Colors.ICON_UNLOCK} {Colors.TEXT}Unlock Files/Folders{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.DIM}3.{Colors.RESET} 📋 {Colors.TEXT}List Locked Items{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.DIM}4.{Colors.RESET} 🖥️  {Colors.TEXT}Open GUI Application{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.DIM}5.{Colors.RESET} ⚙️  {Colors.TEXT}Settings{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.DIM}6.{Colors.RESET} ❌ {Colors.TEXT}Exit{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET}")
        print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}\n")
    
    def run(self):
        """Run the main TUI loop"""
        # Ensure password exists
        if not self.password_prompt.ensure_password_exists():
            print_error("Cannot proceed without a master password.")
            return
        
        while True:
            self.show_main_menu()
            
            print(f"{Colors.PRIMARY}Enter command:")
            print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
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
                print_success("Goodbye! :)")
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
        
        print(f"{Colors.PRIMARY}Enter command:")
        print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
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
            print(f"\n{Colors.PRIMARY}Enter path to lock:")
            print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
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
            self.show_header()
            print(f"{Colors.TITLE}Settings{Colors.RESET}\n")
            
            print(f"{Colors.BORDER}╭─ {Colors.TITLE}OPTIONS{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.DIM}1.{Colors.RESET} 🔑 {Colors.TEXT}Change Password{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.DIM}2.{Colors.RESET} 🔐 {Colors.TEXT}Generate Recovery Codes{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.DIM}3.{Colors.RESET} ℹ️  {Colors.TEXT}About FadCrypt{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.DIM}4.{Colors.RESET} ⬅️  {Colors.TEXT}Back to Main Menu{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET}")
            print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}\n")
            
            print(f"{Colors.PRIMARY}Enter command:")
            print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
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
        print(f"{Colors.TITLE}About FadCrypt{Colors.RESET}\n")
        
        print(f"{Colors.BORDER}╭─ {Colors.TITLE}INFORMATION{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.TEXT}FadCrypt v2.0{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.TEXT}Cross-platform File & Folder Protection{Colors.RESET}")
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
