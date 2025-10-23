"""
File and Folder Lock Manager (Base Class)

Abstract base class for platform-specific file/folder locking implementations.
Provides interface for locking files and folders to prevent read/write/delete/rename.
"""

import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple


class FileLockManager(ABC):
    """
    Abstract base class for file and folder locking.
    
    Platform-specific implementations must override abstract methods.
    Handles locking, unlocking, permission backup, and metadata management.
    """
    
    def __init__(self, config_folder: str, app_locker=None):
        """
        Initialize file lock manager.
        
        Args:
            config_folder: Path to FadCrypt config folder
            app_locker: Reference to AppLocker instance for unified config access (optional)
        """
        self.config_folder = config_folder
        self.app_locker = app_locker
        self.locked_items: List[Dict] = []
        self.config_file = os.path.join(config_folder, "apps_config.json")
        self._load_locked_items()
    
    def _get_config(self) -> Dict:
        """Get the current configuration from app_locker or direct file"""
        if self.app_locker and hasattr(self.app_locker, 'config'):
            return self.app_locker.config
        elif os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {"applications": [], "locked_files_and_folders": []}
        return {"applications": [], "locked_files_and_folders": []}
    
    def _load_locked_items(self):
        """Load locked items from unified config (apps_config.json) - reads directly from file"""
        # CRITICAL: Always read from file, not from cache, to get fresh data
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.locked_items = config.get("locked_files_and_folders", [])
                    print(f"[FileLockManager] Loaded {len(self.locked_items)} locked items from file")
                    return
            except Exception as e:
                print(f"[FileLockManager] Could not read locked items from file: {e}")
        else:
            print(f"[FileLockManager] Config file does not exist: {self.config_file}")
        
        # Fallback: use _get_config if file doesn't exist
        config = self._get_config()
        self.locked_items = config.get("locked_files_and_folders", [])
        if self.locked_items:
            print(f"📁 Loaded {len(self.locked_items)} locked items from config (fallback)")
    
    def _save_locked_items(self):
        """Save locked items to unified config (apps_config.json)
        
        NOTE: This is called from remove_item(). For UI consistency, prefer using
        MainWindow.save_locked_files_config() which preserves applications.
        """
        try:
            config = self._get_config()
            config["locked_files_and_folders"] = self.locked_items
            
            # Ensure applications key exists
            if "applications" not in config:
                config["applications"] = []
            
            # Always save directly using safe write to ensure file is updated
            from core.file_protection import safe_write_to_protected_file
            import json
            content = json.dumps(config, indent=2)
            success, error = safe_write_to_protected_file(self.config_file, content)
            if success:
                print(f"💾 Saved {len(self.locked_items)} locked items to unified config")
                # Update app_locker config if it exists
                if self.app_locker and hasattr(self.app_locker, 'config'):
                    self.app_locker.config = config
            else:
                print(f"❌ Error saving locked items: {error}")
                
        except Exception as e:
            print(f"❌ Error saving locked items: {e}")
    
    def add_item(self, path: str, item_type: str = "file") -> bool:
        """
        Add file or folder to locked items list.
        
        Args:
            path: Absolute path to file or folder
            item_type: "file" or "folder"
        
        Returns:
            True if added successfully, False otherwise
        """
        # CRITICAL: Reload from file first to ensure fresh state
        self._load_locked_items()
        
        if not os.path.exists(path):
            print(f"❌ Path does not exist: {path}")
            return False
        
        # Check if trying to lock a system path
        if self._is_system_path(path):
            print(f"❌ Cannot lock system path: {path}")
            print(f"   System paths are protected to prevent breaking your system")
            return False
        
        # Check if already in list
        if any(item['path'] == path for item in self.locked_items):
            print(f"⚠️  Already in list: {path}")
            return False
        
        # Get metadata
        metadata = self._get_item_metadata(path, item_type)
        if not metadata:
            return False
        
        self.locked_items.append(metadata)
        self._save_locked_items()
        print(f"✅ Added to locked items: {os.path.basename(path)}")
        return True
    
    def remove_item(self, path: str) -> bool:
        """
        Remove file or folder from locked items list.
        
        Args:
            path: Absolute path to file or folder
        
        Returns:
            True if removed successfully, False otherwise
        """
        original_count = len(self.locked_items)
        self.locked_items = [item for item in self.locked_items if item['path'] != path]
        
        if len(self.locked_items) < original_count:
            self._save_locked_items()
            print(f"✅ Removed from locked items: {os.path.basename(path)}")
            return True
        else:
            print(f"⚠️  Not found in locked items: {path}")
            return False
    
    def get_locked_items(self) -> List[Dict]:
        """Get list of all locked items"""
        return self.locked_items.copy()
    
    def increment_unlock_count(self, path: str):
        """Increment unlock count for a file/folder"""
        for item in self.locked_items:
            if item['path'] == path:
                item['unlock_count'] = item.get('unlock_count', 0) + 1
                self._save_locked_items()
                break
    
    def lock_all(self) -> Tuple[int, int]:
        """
        Lock all items in the locked items list.
        
        Returns:
            Tuple of (success_count, failure_count)
        """
        if not self.locked_items:
            print("ℹ️  No items to lock")
            return (0, 0)
        
        print(f"🔒 Locking {len(self.locked_items)} items...")
        success_count = 0
        failure_count = 0
        
        for item in self.locked_items:
            try:
                if self._lock_item(item):
                    success_count += 1
                    print(f"  ✅ Locked: {item['name']}")
                else:
                    failure_count += 1
                    print(f"  ❌ Failed to lock: {item['name']}")
            except Exception as e:
                failure_count += 1
                print(f"  ❌ Error locking {item['name']}: {e}")
        
        print(f"🔒 Lock complete: {success_count} success, {failure_count} failed")
        return (success_count, failure_count)
    
    def unlock_all(self) -> Tuple[int, int]:
        """
        Unlock all items in the locked items list.
        
        Returns:
            Tuple of (success_count, failure_count)
        """
        if not self.locked_items:
            print("ℹ️  No items to unlock")
            return (0, 0)
        
        print(f"🔓 Unlocking {len(self.locked_items)} items...")
        success_count = 0
        failure_count = 0
        
        for item in self.locked_items:
            try:
                if self._unlock_item(item):
                    success_count += 1
                    print(f"  ✅ Unlocked: {item['name']}")
                else:
                    failure_count += 1
                    print(f"  ❌ Failed to unlock: {item['name']}")
            except Exception as e:
                failure_count += 1
                print(f"  ❌ Error unlocking {item['name']}: {e}")
        
        print(f"🔓 Unlock complete: {success_count} success, {failure_count} failed")
        return (success_count, failure_count)
    
    def lock_fadcrypt_configs(self):
        """
        Lock FadCrypt's own config files to prevent tampering.
        Only immutable-sensitive files are protected by the elevated daemon.
        Config files (apps_config.json, monitoring_state.json) remain writable for app functionality.
        """
        # Files protected by elevated daemon (immutable - cannot be written)
        daemon_protected_files = [
            os.path.join(self.config_folder, "recovery_codes.json"),
            os.path.join(self.config_folder, "encrypted_password.bin")
        ]
        
        print("🔒 Protecting immutable FadCrypt config files...")
        
        # For daemon-protected files, just log that they're protected
        for file_path in daemon_protected_files:
            if os.path.exists(file_path):
                print(f"  ✅ Protected: {os.path.basename(file_path)} (immutable via daemon)")
    
    def unlock_fadcrypt_configs(self):
        """
        Unlock FadCrypt's immutable config files.
        Config files (apps_config.json, monitoring_state.json) are not locked.
        The daemon handles immutable file unprotection seamlessly.
        """
        # Files protected by elevated daemon (immutable)
        daemon_protected_files = [
            os.path.join(self.config_folder, "recovery_codes.json"),
            os.path.join(self.config_folder, "encrypted_password.bin")
        ]
        
        print("🔓 Unprotecting immutable FadCrypt config files...")
        
        # For daemon-protected files, just log that they're handled by daemon
        for file_path in daemon_protected_files:
            if os.path.exists(file_path):
                print(f"  ✅ Unprotected: {os.path.basename(file_path)} (via daemon)")
    
    @abstractmethod
    def _get_item_metadata(self, path: str, item_type: str) -> Optional[Dict]:
        """
        Get metadata for file or folder (platform-specific).
        
        Must include: name, path, type, original_permissions, filesystem, lock_method
        """
        pass
    
    def _is_system_path(self, path: str) -> bool:
        """
        Check if path is a critical system path that should not be locked.
        Returns True if the path is a system path.
        
        Note: Allows /tmp, /home, and user directories.
        Only blocks critical system binary/library directories.
        """
        # Normalize path
        abs_path = os.path.abspath(path).lower()
        
        # List of CRITICAL system paths that should NEVER be locked
        # These would break the entire system if locked
        critical_system_paths = [
            '/usr',      # System binaries and libraries
            '/bin',      # Essential command binaries
            '/sbin',     # System command binaries
            '/lib',      # Essential system libraries
            '/lib64',    # 64-bit system libraries
            '/boot',     # Boot files
            '/sys',      # Kernel interfaces
            '/proc',     # Process info
            '/dev',      # Device files
            '/run',      # Runtime data
            '/etc',      # System configuration (critical)
            '/var',      # System logs and data (critical)
            '/opt',      # Optional software (usually system-wide)
        ]
        
        # Check if path is or is inside a critical system path
        for sys_path in critical_system_paths:
            sys_abs = os.path.abspath(sys_path).lower()
            if abs_path == sys_abs or abs_path.startswith(sys_abs + os.sep):
                return True
        
        # Allow /tmp, /home, and user directories
        # (User can lock their own files at their own risk)
        return False
    
    @abstractmethod
    def _lock_item(self, item: Dict) -> bool:
        """Lock a file or folder (platform-specific)"""
        pass
    
    @abstractmethod
    def _unlock_item(self, item: Dict) -> bool:
        """Unlock a file or folder (platform-specific)"""
        pass
    
    def temporarily_unlock_config(self, filename: str):
        """Temporarily unlock a config file for writing"""
        config_path = os.path.join(self.config_folder, filename)
        if os.path.exists(config_path):
            self._unlock_config_file(config_path)
    
    def relock_config(self, filename: str):
        """Re-lock a config file after writing"""
        config_path = os.path.join(self.config_folder, filename)
        if os.path.exists(config_path):
            self._lock_config_file(config_path)
    
    @abstractmethod
    def _lock_config_file(self, path: str):
        """Lock config file (keep readable, prevent modification)"""
        pass
    
    @abstractmethod
    def _unlock_config_file(self, path: str):
        """Unlock config file"""
        pass
