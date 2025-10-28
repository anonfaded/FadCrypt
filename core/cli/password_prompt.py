"""
CLI Password Prompt

Secure password input for CLI without GUI dialogs.
Uses getpass for masked input.
"""

import getpass
import os
import sys
from typing import Optional, Tuple

from .colors import Colors, print_colored, print_error, print_success, print_warning


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
        Prompt for password with masked input.
        
        Args:
            prompt: Prompt text to display
            confirm: If True, ask for confirmation
        
        Returns:
            Password string or None if cancelled
        """
        try:
            password = getpass.getpass(f"{Colors.PRIMARY}{prompt}{Colors.RESET}")
            
            if not password:
                return None
            
            if confirm:
                confirm_password = getpass.getpass(f"{Colors.PRIMARY}Confirm password: {Colors.RESET}")
                if password != confirm_password:
                    print_error("Passwords do not match!")
                    return None
            
            return password
            
        except KeyboardInterrupt:
            print()
            return None
        except Exception as e:
            print_error(f"Error reading password: {e}")
            return None
    
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
        print_colored("\n╔═══════════════════════════════════════════════════════════╗", Colors.BORDER)
        print_colored("║           Create Master Password                          ║", Colors.TITLE)
        print_colored("╚═══════════════════════════════════════════════════════════╝\n", Colors.BORDER)
        
        print_colored("Your master password will be used to lock/unlock files.", Colors.INFO)
        print_colored("Make sure to remember it - it cannot be recovered!\n", Colors.WARNING)
        
        while True:
            password = self.prompt_password("Create password: ", confirm=True)
            
            if not password:
                print_warning("Password creation cancelled.")
                return False
            
            # Validate password strength
            if len(password) < 4:
                print_error("Password must be at least 4 characters long!")
                continue
            
            # Create password
            if self.password_manager.create_password(password):
                print_success("Master password created successfully!")
                
                # Offer to create recovery codes
                print_colored("\nWould you like to generate recovery codes? (y/n): ", Colors.INFO, end='')
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
        print_colored("\n╔═══════════════════════════════════════════════════════════╗", Colors.BORDER)
        print_colored("║           Change Master Password                          ║", Colors.TITLE)
        print_colored("╚═══════════════════════════════════════════════════════════╝\n", Colors.BORDER)
        
        # Verify current password
        if not self.verify_password("Enter current password: "):
            return False
        
        # Get new password
        while True:
            new_password = self.prompt_password("Enter new password: ", confirm=True)
            
            if not new_password:
                print_warning("Password change cancelled.")
                return False
            
            if len(new_password) < 4:
                print_error("Password must be at least 4 characters long!")
                continue
            
            # Change password
            if self.password_manager.change_password(new_password):
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
            print_colored("\n╔═══════════════════════════════════════════════════════════╗", Colors.BORDER)
            print_colored("║              Recovery Codes Generated                     ║", Colors.TITLE)
            print_colored("╚═══════════════════════════════════════════════════════════╝\n", Colors.BORDER)
            
            print_colored("Save these codes in a secure place!", Colors.WARNING)
            print_colored("You can use them to reset your password if you forget it.\n", Colors.INFO)
            
            for i, code in enumerate(codes, 1):
                print_colored(f"  {i}. {code}", Colors.SUCCESS)
            
            print_colored("\nPress Enter to continue...", Colors.DIM, end='')
            input()
            return True
        else:
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
