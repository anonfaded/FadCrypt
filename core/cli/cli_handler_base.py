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
    
    @abstractmethod
    def lock_path(self, path: str) -> bool:
        """
        Lock a file or folder.
        
        Args:
            path: Absolute path to file or folder
        
        Returns:
            True if locked successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def unlock_path(self, path: str) -> bool:
        """
        Unlock a file or folder.
        
        Args:
            path: Absolute path to file or folder
        
        Returns:
            True if unlocked successfully, False otherwise
        """
        pass
    
    def lock_multiple(self, paths: List[str]) -> Tuple[int, int]:
        """
        Lock multiple paths.
        
        Before locking, ensure encryption password is set if enabled.
        
        Args:
            paths: List of absolute paths
        
        Returns:
            Tuple of (success_count, failure_count)
        """
        # CRITICAL: Set password for encryption if enabled
        self._ensure_password_for_encryption()
        
        success_count = 0
        failure_count = 0
        
        for path in paths:
            if self.lock_path(path):
                success_count += 1
            else:
                failure_count += 1
        
        return (success_count, failure_count)
    
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
    
    def unlock_multiple(self, paths: List[str]) -> Tuple[int, int]:
        """
        Unlock multiple paths.
        
        Args:
            paths: List of absolute paths
        
        Returns:
            Tuple of (success_count, failure_count)
        """
        success_count = 0
        failure_count = 0
        
        for path in paths:
            if self.unlock_path(path):
                success_count += 1
            else:
                failure_count += 1
        
        return (success_count, failure_count)
    
    @abstractmethod
    def list_locked_items(self) -> List[Dict]:
        """
        List all locked items.
        
        Returns:
            List of locked items with metadata
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
