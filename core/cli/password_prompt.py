"""
CLI Password Prompt

Secure password input for CLI without GUI dialogs.
Uses curses for animated input.
"""

import os
from typing import Optional

from .colors import Colors, print_colored, print_error, print_success, print_warning, print_info
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
    
    def verify_password_with_recovery(self, prompt: str = "Enter your FadCrypt password: ") -> bool:
        """
        Verify password with recovery code fallback option.
        
        Args:
            prompt: Prompt text to display
        
        Returns:
            True if password is correct or recovery successful, False otherwise
        """
        password = self.prompt_password(prompt)
        
        if not password:
            return False
        
        # Check if user pressed F1 for "Forgot Password?"
        if password == "FORGOT_PASSWORD":
            # Check if recovery codes are available
            if not self.password_manager.has_recovery_codes():
                print_warning("No recovery codes available.")
                return False
            
            return self._handle_password_recovery()
        
        if self.password_manager.verify_password(password):
            return True
        else:
            print_error("Incorrect password!")
            
            # Check if recovery codes are available
            if not self.password_manager.has_recovery_codes():
                print_warning("No recovery codes available.")
                return False
            
            # Offer recovery option
            print(f"\n{Colors.PRIMARY}Forgot your password? You can use a recovery code to reset it.")
            print(f"{Colors.PRIMARY}Use recovery code? (y/n):")
            print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
            choice = input().strip().lower()
            
            if choice == 'y':
                return self._handle_password_recovery()
            
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
        # Get current password with recovery option
        current_password = self._get_current_password_with_recovery()
        if not current_password:
            return False
        
        # Check if password was reset via recovery
        if current_password == "RECOVERY_COMPLETED":
            # Password was already reset via recovery, operation is complete
            return True
        
        # Get new password
        while True:
            new_password = self.prompt_password("Enter new password", confirm=True)
            
            if not new_password:
                print_warning("Password change cancelled.")
                return False
            
            # Change password with both old and new passwords
            if self.password_manager.change_password(current_password, new_password):
                print_success("Password changed successfully!")
                
                # Ask if user wants to generate new recovery codes
                print(f"\n{Colors.INFO}Since you changed your password, you might want to generate new recovery codes.")
                print(f"{Colors.WARNING}⚠️  Important: Generating new codes will invalidate your existing recovery codes.")
                print(f"{Colors.WARNING}   Your old codes will no longer work and cannot be used again.")
                print(f"{Colors.PRIMARY}Would you like to generate new recovery codes? (y/n):")
                print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
                choice = input().strip().lower()
                
                if choice == 'y':
                    self.generate_recovery_codes()
                
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
        # Check if user already has recovery codes
        if self.password_manager.has_recovery_codes():
            print(f"\n{Colors.WARNING}⚠️  Warning: You already have recovery codes.")
            print(f"{Colors.WARNING}   Generating new codes will invalidate your existing recovery codes.")
            print(f"{Colors.WARNING}   Your old codes will no longer work and cannot be used again.")
            print(f"{Colors.PRIMARY}Do you want to continue and generate new recovery codes? (y/n):")
            print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
            choice = input().strip().lower()
            
            if choice != 'y':
                print_info("Recovery codes generation cancelled.")
                return False
        
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
                # Use the improved save method
                self._save_recovery_codes_to_file(codes)
            
            return True
        
        print_error("Failed to generate recovery codes.")
        return False
    
    def _handle_password_recovery(self) -> bool:
        """
        Handle password recovery using recovery codes.
        
        Returns:
            True if recovery successful, False otherwise
        """
        # Get recovery code
        recovery_code = self._prompt_recovery_code()
        if not recovery_code:
            return False
        
        # Verify recovery code
        is_valid, error_msg = self.password_manager.verify_recovery_code(recovery_code)
        if not is_valid:
            if error_msg and "already been used" in error_msg:
                print_error("Recovery code has already been used!")
            elif error_msg and ("not found" in error_msg or "incorrect" in error_msg):
                print_error("Invalid recovery code!")
            elif error_msg and "format" in error_msg:
                print_error("Invalid code format! Use format: XXXX-XXXX-XXXX-XXXX")
            else:
                print_error(f"Recovery code error: {error_msg}")
            return False
        
        print_success("Recovery code verified!")
        
        # Get new password
        print(f"\n{Colors.INFO}Now create a new master password:")
        new_password = self.prompt_password("New password", confirm=True)
        if not new_password:
            print_warning("Password recovery cancelled.")
            return False
        
        # Recover password using existing method
        success, error_msg = self.password_manager.recover_password_with_code(recovery_code, new_password)
        
        if success:
            print_success("Password successfully reset!")
            
            # Ask if user wants to generate new recovery codes
            print(f"\n{Colors.WARNING}⚠️  Important: Your old recovery codes are now invalid and cannot be used again.")
            print(f"{Colors.PRIMARY}Would you like to generate new recovery codes? (y/n):")
            print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
            choice = input().strip().lower()
            
            if choice == 'y':
                # Generate new recovery codes
                print(f"\n{Colors.INFO}Generating new recovery codes...")
                codes_success, new_codes = self.password_manager.create_recovery_codes()
                
                if codes_success and new_codes:
                    print(f"\n{Colors.BORDER}╭─ {Colors.TITLE}🔑 New Recovery Codes{Colors.RESET}")
                    print(f"{Colors.BORDER}│{Colors.RESET} {Colors.INFO}Here are your NEW recovery codes:{Colors.RESET}")
                    print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────{Colors.RESET}\n")
                    
                    for i, code in enumerate(new_codes, 1):
                        print_colored(f"  {i}. {code}", Colors.SUCCESS)
                    
                    # Ask if user wants to save codes
                    print(f"\n{Colors.PRIMARY}Would you like to save these codes to a file? (y/n):")
                    print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
                    save_choice = input().strip().lower()
                    
                    if save_choice == 'y':
                        self._save_recovery_codes_to_file(new_codes)
                else:
                    print_warning("Failed to generate new recovery codes.")
                    print_warning("You can generate them later from the main menu.")
            
            return True
        else:
            print_error(f"Failed to reset password: {error_msg}")
            return False
    
    def _prompt_recovery_code(self) -> Optional[str]:
        """
        Prompt for recovery code with format validation.
        
        Returns:
            Recovery code string or None if cancelled
        """        
        while True:
            code = self.prompt_password("Enter recovery code")
            if not code:
                return None
            
            # Normalize the code (remove spaces, convert to uppercase)
            normalized_code = code.replace(" ", "").replace("-", "").upper()
            
            # Validate format (16 characters, alphanumeric)
            if len(normalized_code) == 16 and normalized_code.isalnum():
                # Format as XXXX-XXXX-XXXX-XXXX
                formatted_code = f"{normalized_code[:4]}-{normalized_code[4:8]}-{normalized_code[8:12]}-{normalized_code[12:16]}"
                return formatted_code
            else:
                print_error("Invalid format! Recovery codes are 16 characters (letters and numbers).")
                print_colored("Example: A1B2-C3D4-E5F6-G7H8", Colors.DIM)
                
                print(f"\n{Colors.PRIMARY}Try again? (y/n):")
                print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
                retry = input().strip().lower()
                if retry != 'y':
                    return None
    
    def _save_recovery_codes_to_file(self, codes: list) -> None:
        """
        Save recovery codes to a file.
        
        Args:
            codes: List of recovery codes to save
        """
        try:
            # Get default save location (cross-platform)
            import platform
            system = platform.system()
            
            if system == "Windows":
                # Windows: Documents folder
                documents = os.path.join(os.path.expanduser("~"), "Documents")
                default_path = os.path.join(documents, "fadcrypt_recovery_codes.txt")
            else:
                # Linux/Unix: Documents folder or home if Documents doesn't exist
                documents = os.path.join(os.path.expanduser("~"), "Documents")
                if not os.path.exists(documents):
                    # Fallback to home directory on Linux
                    documents = os.path.expanduser("~")
                default_path = os.path.join(documents, "fadcrypt_recovery_codes.txt")
            
            print_colored(f"\nCodes will be saved to your {os.path.basename(documents)} folder.", Colors.INFO)
            print_colored(f"Location: {default_path}", Colors.DIM)
            
            # Check if file already exists and warn user
            if os.path.exists(default_path):
                print_colored(f"⚠️  File already exists and will be overwritten.", Colors.WARNING)
            
            print(f"\n{Colors.PRIMARY}Press Enter to save, or type a custom path:")
            print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
            custom_path = input().strip()
            
            save_path = custom_path if custom_path else default_path
            
            print_colored(f"\n📁 Saving codes to: {save_path}", Colors.INFO)
            
            # Ensure directory exists (cross-platform)
            save_dir = os.path.dirname(save_path)
            if not os.path.exists(save_dir):
                print_colored(f"📂 Creating directory: {save_dir}", Colors.INFO)
                os.makedirs(save_dir, exist_ok=True)
            
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
            
            # Verify file was created and has content
            if os.path.exists(save_path):
                file_size = os.path.getsize(save_path)
                print_success(f"\n✅ Recovery codes saved successfully!")
                print_colored(f"   📄 File: {save_path}", Colors.SUCCESS)
                print_colored(f"   📊 Size: {file_size} bytes", Colors.SUCCESS)
                print_colored(f"   💾 Contains: {len(codes)} recovery codes", Colors.SUCCESS)
            else:
                print_error(f"\n❌ File was not created!")
                print_error(f"   Expected location: {save_path}")
                
        except PermissionError as e:
            print_error(f"\n❌ Permission denied!")
            print_error(f"   Error: {e}")
            print_error(f"   💡 Try running as administrator or choose a different location.")
        except FileNotFoundError as e:
            print_error(f"\n❌ Directory not found!")
            print_error(f"   Error: {e}")
            print_error(f"   💡 Try specifying a full path or create the directory first.")
        except OSError as e:
            print_error(f"\n❌ System error!")
            print_error(f"   Error: {e}")
            print_error(f"   💡 Check disk space and file permissions.")
        except Exception as e:
            print_error(f"\n❌ Unexpected error!")
            print_error(f"   Error: {e}")
            print_error(f"   Type: {type(e).__name__}")
            # Show traceback for debugging
            import traceback
            print_error(f"   Details: {traceback.format_exc()}")
        
        # ALWAYS pause so user can see the result (success or error)
        print(f"\n{Colors.INFO}Press Enter to continue...")
        input()
    
    def _get_current_password_with_recovery(self) -> Optional[str]:
        """
        Get current password with recovery option.
        
        Returns:
            Password string or None if cancelled/failed
        """
        password = self.prompt_password("Enter current password")
        
        if not password:
            return None
        
        # Check if user pressed F1 for "Forgot Password?"
        if password == "FORGOT_PASSWORD":
            # Check if recovery codes are available
            if not self.password_manager.has_recovery_codes():
                print_warning("No recovery codes available.")
                return None
            
            # Handle password recovery (this will reset password)
            if self._handle_password_recovery():
                print_success("Password was reset via recovery!")
                print_info("Since your password was reset, the change password operation is complete.")
                return "RECOVERY_COMPLETED"  # Special return value
            else:
                return None
        
        # Verify the password
        if self.password_manager.verify_password(password):
            return password
        else:
            print_error("Incorrect current password!")
            
            # Check if recovery codes are available
            if not self.password_manager.has_recovery_codes():
                print_warning("No recovery codes available.")
                return None
            
            # Offer recovery option
            print(f"\n{Colors.PRIMARY}Forgot your password? You can use a recovery code to reset it.")
            print(f"{Colors.PRIMARY}Use recovery code? (y/n):")
            print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
            choice = input().strip().lower()
            
            if choice == 'y':
                if self._handle_password_recovery():
                    print_success("Password was reset via recovery!")
                    print_info("Since your password was reset, the change password operation is complete.")
                    return "RECOVERY_COMPLETED"  # Special return value
                else:
                    return None
            
            return None
    
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
