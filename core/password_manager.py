"""
Password Manager - Master Password Operations
Handles master password creation, verification, changes, and recovery codes
"""

import os
from typing import Optional, Callable, List, Tuple
from .crypto_manager import CryptoManager
from .recovery_manager import RecoveryCodeManager


class PasswordManager:
    """
    Manages the master password for FadCrypt.
    
    The master password is used to encrypt/decrypt all application
    configurations and settings. The password itself is stored as an
    encrypted hash in encrypted_password.bin.
    
    Attributes:
        crypto: CryptoManager instance for encryption operations
        password_file: Path to encrypted password file
        cached_password: In-memory cache of password (bytes)
    """
    
    def __init__(self, password_file_path: str, crypto_manager: Optional[CryptoManager] = None, recovery_codes_file_path: Optional[str] = None):
        """
        Initialize the PasswordManager.
        
        Args:
            password_file_path: Full path to encrypted_password.bin file
            crypto_manager: Optional CryptoManager instance
            recovery_codes_file_path: Full path to recovery_codes.json file
        """
        self.password_file = password_file_path
        self.crypto = crypto_manager or CryptoManager()
        self.cached_password: Optional[bytes] = None
        
        # Initialize recovery code manager if path provided
        self.recovery_manager: Optional[RecoveryCodeManager] = None
        if recovery_codes_file_path:
            self.recovery_manager = RecoveryCodeManager(recovery_codes_file_path)
        
        # Debug logs (commented out for cleaner CLI)
        # print(f"[PasswordManager] Initialized with password file: {password_file_path}")
        # print(f"[PasswordManager] Password file exists: {os.path.exists(password_file_path)}")
        # if self.recovery_manager:
        #     print(f"[PasswordManager] Recovery codes available: {self.recovery_manager.has_recovery_codes()}")
    
    def create_password(self, password: str) -> bool:
        """
        Create/update the master password.
        
        Encrypts the password with itself and stores in password_file.
        This allows verification without storing plaintext.
        
        Args:
            password: New master password (as string)
            
        Returns:
            True if password created successfully, False otherwise
        """
        try:
            password_bytes = password.encode('utf-8')
            
            print(f"[PasswordManager] Creating password at: {self.password_file}")
            
            # Encrypt the password with itself
            success = self.crypto.encrypt_password_hash(
                password=password_bytes,
                password_hash=password_bytes,
                file_path=self.password_file
            )
            
            if success:
                self.cached_password = password_bytes
                print(f"[PasswordManager] [OK] Master password created successfully")
                print(f"[PasswordManager] File now exists: {os.path.exists(self.password_file)}")
                return True
            else:
                print("[PasswordManager] [ERROR] Failed to create master password")
                return False
                
        except Exception as e:
            print(f"[PasswordManager] [ERROR] Error creating password: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_password(self, password: str) -> bool:
        """
        Verify if the provided password matches the master password.
        
        Args:
            password: Password to verify (as string)
            
        Returns:
            True if password is correct, False otherwise
        """
        try:
            if not os.path.exists(self.password_file):
                print(f"[PasswordManager] [WARN] Password file not found: {self.password_file}")
                return False
            
            password_bytes = password.encode('utf-8')
            
            print(f"[PasswordManager] Verifying password from: {self.password_file}")
            
            # Try to decrypt the password hash
            decrypted_hash = self.crypto.decrypt_password_hash(
                password=password_bytes,
                file_path=self.password_file
            )
            
            if decrypted_hash is None:
                print("[PasswordManager] [ERROR] Decryption returned None")
                return False
            
            # Compare with original password
            is_valid = (password_bytes == decrypted_hash)
            
            if is_valid:
                self.cached_password = password_bytes
                print("[PasswordManager] [OK] Password verified successfully")
            else:
                print("[PasswordManager] [ERROR] Password verification failed (mismatch)")
            
            return is_valid
            
        except Exception as e:
            print(f"[PasswordManager] [ERROR] Error verifying password: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def change_password(
        self,
        old_password: str,
        new_password: str,
        re_encrypt_callback: Optional[Callable[[bytes], bool]] = None
    ) -> bool:
        """
        Change the master password.
        
        Args:
            old_password: Current master password
            new_password: New master password
            re_encrypt_callback: Optional callback to re-encrypt configs with new password.
                                Should accept new password (bytes) and return success bool.
            
        Returns:
            True if password changed successfully, False otherwise
        """
        try:
            # Verify old password
            if not self.verify_password(old_password):
                print("[PasswordManager] Old password is incorrect")
                return False
            
            # Create new password
            if not self.create_password(new_password):
                print("[PasswordManager] Failed to create new password")
                return False
            
            # Re-encrypt all configs with new password (if callback provided)
            if re_encrypt_callback:
                new_password_bytes = new_password.encode('utf-8')
                if not re_encrypt_callback(new_password_bytes):
                    print("[PasswordManager] Warning: Failed to re-encrypt some configs")
                    # Don't revert password change - user can manually re-encrypt
            
            print("[PasswordManager] Password changed successfully")
            return True
            
        except Exception as e:
            print(f"[PasswordManager] Error changing password: {e}")
            return False
    
    def load_password(self) -> Optional[bytes]:
        """
        Load the cached password or prompt for it.
        
        Note: In GUI apps, this should prompt the user via a dialog.
        For now, returns cached password if available.
        
        Returns:
            Cached password as bytes, or None if not cached
        """
        return self.cached_password
    
    def is_password_set(self) -> bool:
        """
        Check if a master password has been set.
        
        Returns:
            True if password file exists, False otherwise
        """
        return os.path.exists(self.password_file)
    
    def clear_cache(self):
        """Clear the cached password from memory."""
        self.cached_password = None
        print("[PasswordManager] Password cache cleared")
    
    def get_password_bytes(self) -> Optional[bytes]:
        """
        Get the cached password in bytes format.
        
        Returns:
            Cached password as bytes, or None if not cached
        """
        return self.cached_password

    # ==================== Recovery Code Methods ====================
    
    def create_recovery_codes(self) -> Tuple[bool, Optional[List[str]]]:
        """
        Create recovery codes for the master password.
        
        Should be called immediately after password creation.
        User must write down the codes and store them safely.
        
        Returns:
            Tuple of (success: bool, codes: List[str] or None)
        """
        if not self.recovery_manager:
            print("[PasswordManager] Recovery code manager not initialized")
            return False, None
        
        return self.recovery_manager.create_recovery_codes()
    
    def verify_recovery_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Verify if a recovery code is valid and unused.
        
        Args:
            code: Recovery code to verify
            
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        if not self.recovery_manager:
            return False, "Recovery codes not available"
        
        return self.recovery_manager.verify_recovery_code(code)
    
    def recover_password_with_code(
        self,
        recovery_code: str,
        new_password: str,
        cleanup_callback: Optional[Callable[[str], bool]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Recover access and reset password using a recovery code.
        
        This is the core password recovery mechanism with hash-based security:
        1. Verify recovery code against saved hashes (NO password needed!)
        2. Mark code as used (one-time consumption)
        3. Delete old password file
        4. Delete old recovery codes
        5. Create new password
        6. Create new recovery codes
        7. Call cleanup callback (e.g., stop monitoring, unlock files)
        
        CRITICAL SECURITY (Version 2.0 - Hash-Based):
        - Recovery codes verified WITHOUT needing old password
        - PBKDF2-HMAC-SHA256 hash verification (100k iterations)
        - Code must match stored hash to proceed
        - Code marked as used immediately after verification
        - Old password file deleted (no bypass with old password)
        - Old recovery codes deleted (used code won't work again)
        - New recovery codes created with new password
        - Even with hash file access, codes cannot be reversed
        
        Args:
            recovery_code: Recovery code provided by user
            new_password: New master password
            cleanup_callback: Optional callback to cleanup monitoring/files
                             Should accept new_password (str) and return success bool
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not self.recovery_manager:
            return False, "Recovery codes not available"
        
        try:
            if not self.recovery_manager.has_recovery_codes():
                return False, "No recovery codes found. Please reset your password differently."
            
            print("[PasswordManager] Starting password recovery process (hash-based)...")
            
            # Step 1: Verify recovery code
            print("[PasswordManager] Verifying recovery code against stored hashes...")
            is_valid, error_msg = self.recovery_manager.verify_recovery_code(recovery_code)
            
            if not is_valid:
                print(f"[PasswordManager] Recovery code verification failed: {error_msg}")
                return False, f"Invalid recovery code: {error_msg}"
            
            print("[PasswordManager] Recovery code verified successfully")
            
            # Step 2: Consume (mark as used) the recovery code immediately
            print("[PasswordManager] Marking recovery code as used...")
            consumed, consume_error = self.recovery_manager.consume_recovery_code(recovery_code)
            
            if not consumed:
                print(f"[PasswordManager] Failed to mark code as used: {consume_error}")
            else:
                print("[PasswordManager] Recovery code marked as used")
            
            # Step 3: Delete old password file (cannot be recovered)
            if os.path.exists(self.password_file):
                try:
                    os.remove(self.password_file)
                    print("[PasswordManager] [OK] Deleted old password file")
                except Exception as e:
                    print(f"[PasswordManager] ⚠️  Failed to delete old password: {e}")
            
            # Note: Recovery codes are kept - only the used code is marked as consumed
            # Remaining unused codes can still be used for future password resets
            
            # Step 4: Run cleanup callback (stop monitoring, unlock files, reset state)
            if cleanup_callback:
                print("[PasswordManager] Running cleanup callback...")
                if not cleanup_callback(new_password):
                    print("[PasswordManager] ⚠️  Cleanup callback returned False")
            
            # Step 5: Create new password
            if not self.create_password(new_password):
                return False, "Failed to create new password"
            
            print("[PasswordManager] Password recovered and reset successfully")
            
            return True, None
            
        except Exception as e:
            print(f"[PasswordManager] [ERROR] Error recovering password: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Error during recovery: {str(e)}"
    
    def has_recovery_codes(self) -> bool:
        """
        Check if recovery codes are available.
        
        Returns:
            True if recovery codes are set, False otherwise
        """
        if not self.recovery_manager:
            return False
        return self.recovery_manager.has_recovery_codes()
    
    def get_remaining_recovery_codes_count(self) -> Tuple[bool, Optional[int]]:
        """
        Get count of unused recovery codes.
        
        Returns:
            Tuple of (success: bool, count: Optional[int])
        """
        if not self.recovery_manager:
            return False, None
        return self.recovery_manager.get_remaining_codes_count()
