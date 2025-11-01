"""
CLI Password Prompt

Secure password input for CLI without GUI dialogs.
Uses curses for animated input.
"""

import os
from typing import Optional

from .colors import Colors, print_colored, print_error, print_success, print_warning
from .curses_password import prompt_password_curses


class PasswordPrompt:
    """Handle password operations in CLI"""
    
    def __init__(self, password_manager):
        """
        Initialize password prompt.
        
        Args:
            password_manager: PasswordManager instance
        """
        self.password_manager = password_manager
    
    def prompt_password(self, prompt: str = "Enter password: ", confirm: bool = False) -> Optional[str]:
        """
        Prompt for password with masked input using curses animated input.
        
        Args:
            prompt: Prompt text to display
            confirm: If True, ask for confirmation
        
        Returns:
            Password string or None if cancelled
        """
        # Remove trailing colon and "Enter" prefix for cleaner curses display
        clean_prompt = prompt.replace("Enter ", "").replace(":", "").strip()
        return prompt_password_curses(clean_prompt, confirm)
    
    def verify_password(self, prompt: str = "Enter your FadCrypt password: ") -> bool:
        """
        Verify password against stored password.
        
        Args:
            prompt: Prompt text to display
        
        Returns:
            True if password is correct, False otherwise
        """
        password = self.prompt_password(prompt)
        
        if not password:
            return False
        
        if self.password_manager.verify_password(password):
            return True
        else:
            print_error("Incorrect password!")
            return False
    
    def create_password(self) -> bool:
        """
        Create a new master password.
        
        Returns:
            True if password created successfully, False otherwise
        """
        print(f"\n{Colors.BORDER}╭─ {Colors.TITLE}🔐 Create Master Password{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.TEXT}Your master password will be used to lock/unlock files.{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.WARNING}Remember it or use recovery codes to reset it!{Colors.RESET}")
        print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────{Colors.RESET}\n")
        
        while True:
            password = self.prompt_password("Create password: ", confirm=True)
            
            if not password:
                print_warning("Password creation cancelled.")
                return False
            
            # Create password (no length restriction to match GUI behavior)
            if self.password_manager.create_password(password):
                print_success("Master password created successfully!")
                
                # Offer to create recovery codes
                print(f"\n{Colors.PRIMARY}Would you like to generate recovery codes? (y/n):")
                print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
                choice = input().strip().lower()
                
                if choice == 'y':
                    self.generate_recovery_codes()
                
                return True
            else:
                print_error("Failed to create password. Please try again.")
                return False
    
    def change_password(self) -> bool:
        """
        Change the master password.
        
        Returns:
            True if password changed successfully, False otherwise
        """
        # Get current password
        current_password = self.prompt_password("Enter current password")
        if not current_password:
            return False
        
        # Verify current password
        if not self.password_manager.verify_password(current_password):
            print_error("Incorrect current password!")
            return False
        
        # Get new password
        while True:
            new_password = self.prompt_password("Enter new password", confirm=True)
            
            if not new_password:
                print_warning("Password change cancelled.")
                return False
            
            # Change password with both old and new passwords
            if self.password_manager.change_password(current_password, new_password):
                print_success("Password changed successfully!")
                return True
            else:
                print_error("Failed to change password.")
                return False
    
    def generate_recovery_codes(self) -> bool:
        """
        Generate recovery codes.
        
        Returns:
            True if codes generated successfully, False otherwise
        """
        success, codes = self.password_manager.create_recovery_codes()
        
        if success and codes:
            print(f"\n{Colors.BORDER}╭─ {Colors.TITLE}🔑 Recovery Codes Generated{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET} {Colors.WARNING}Save these codes in a secure place!{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET} {Colors.INFO}You can use them to reset your password if you forget it.{Colors.RESET}")
            print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────{Colors.RESET}\n")
            
            for i, code in enumerate(codes, 1):
                print_colored(f"  {i}. {code}", Colors.SUCCESS)
            
            # Ask if user wants to save to file
            print(f"\n{Colors.PRIMARY}Would you like to save these codes to a file? (y/n):")
            print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
            choice = input().strip().lower()
            
            if choice == 'y':
                # Use the existing save method from recovery manager
                if self.password_manager.recovery_manager:
                    try:
                        # Get default save location in Documents folder
                        import platform
                        if platform.system() == "Windows":
                            # Windows: Documents folder
                            documents = os.path.join(os.path.expanduser("~"), "Documents")
                            default_path = os.path.join(documents, "FadCrypt_Recovery_Codes.txt")
                        else:
                            # Linux: Documents folder or home if it doesn't exist
                            documents = os.path.join(os.path.expanduser("~"), "Documents")
                            if not os.path.exists(documents):
                                documents = os.path.expanduser("~")
                            default_path = os.path.join(documents, "FadCrypt_Recovery_Codes.txt")
                        
                        print_colored("\nCodes will be saved to your Documents folder.", Colors.INFO)
                        print_colored(f"Location: {default_path}", Colors.DIM)
                        print(f"\n{Colors.PRIMARY}Press Enter to save, or type a custom path:")
                        print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
                        custom_path = input().strip()
                        
                        save_path = custom_path if custom_path else default_path
                        
                        # Save codes to file
                        with open(save_path, 'w', encoding='utf-8') as f:
                            f.write("FadCrypt Recovery Codes\n")
                            f.write("=" * 50 + "\n\n")
                            f.write("IMPORTANT: Keep these codes in a secure place!\n")
                            f.write("You can use them to reset your password if you forget it.\n\n")
                            for i, code in enumerate(codes, 1):
                                f.write(f"{i}. {code}\n")
                            f.write("\n" + "=" * 50 + "\n")
                            f.write("Generated by FadCrypt\n")
                        
                        print_success(f"Recovery codes saved to: {save_path}")
                    except Exception as e:
                        print_error(f"Failed to save recovery codes: {e}")
            
            return True
        
        print_error("Failed to generate recovery codes.")
        return False
    
    def ensure_password_exists(self) -> bool:
        """
        Ensure a master password exists, create one if not.
        
        Returns:
            True if password exists or was created, False otherwise
        """
        if not os.path.exists(self.password_manager.password_file):
            print_warning("No master password found. Let's create one!")
            return self.create_password()
        return True
