"""
Windows File Lock Manager

Implements file/folder locking using icacls to deny all access.
Backs up and restores ACLs for proper permission recovery.
"""

import os
import subprocess
import tempfile
from typing import Dict, Optional
import time

from core.file_lock_manager import FileLockManager


class FileLockManagerWindows(FileLockManager):
    """Windows implementation of file/folder locking using icacls"""
    
    def __init__(self, config_folder: str, app_locker=None):
        super().__init__(config_folder, app_locker)
        self.acl_backup_folder = os.path.join(config_folder, "acl_backups")
        os.makedirs(self.acl_backup_folder, exist_ok=True)
    
    def _get_acl_backup_path(self, item_path: str) -> str:
        """Get path for ACL backup file"""
        # Create safe filename from path
        safe_name = item_path.replace(':', '').replace('\\', '_').replace('/', '_')
        return os.path.join(self.acl_backup_folder, f"{safe_name}.acl")
    
    def _backup_acl(self, path: str) -> bool:
        """Backup ACL for path"""
        backup_path = self._get_acl_backup_path(path)
        
        try:
            # Use icacls to save ACL
            result = subprocess.run(
                ['icacls', path, '/save', backup_path, '/T'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"  [ACL] Backed up to: {os.path.basename(backup_path)}")
                return True
            else:
                print(f"  [ACL] Backup warning: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  [ACL] Error backing up: {e}")
            return False
    
    def _restore_acl(self, path: str) -> bool:
        """Restore ACL from backup"""
        backup_path = self._get_acl_backup_path(path)
        
        if not os.path.exists(backup_path):
            print(f"  [ACL] No backup found, using default restore")
            # Fallback: Grant full control to Everyone
            try:
                subprocess.run(
                    ['icacls', path, '/grant', 'Everyone:(F)'],
                    capture_output=True,
                    timeout=10
                )
                return True
            except:
                return False
        
        try:
            # Restore ACL from backup
            result = subprocess.run(
                ['icacls', os.path.dirname(path), '/restore', backup_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"  [ACL] Restored from backup")
                # Clean up backup file
                try:
                    os.remove(backup_path)
                except:
                    pass
                return True
            else:
                print(f"  [ACL] Restore warning: {result.stderr}")
                # Try fallback
                subprocess.run(['icacls', path, '/grant', 'Everyone:(F)'], timeout=10)
                return False
                
        except Exception as e:
            print(f"  [ACL] Error restoring: {e}")
            return False
    
    def _get_item_metadata(self, path: str, item_type: str) -> Optional[Dict]:
        """
        Get metadata for file or folder.
        
        Returns dict with: name, path, type, original_permissions (ACL backup path), filesystem, lock_method
        """
        try:
            # Backup ACL first
            backup_path = self._get_acl_backup_path(path)
            if self._backup_acl(path):
                original_permissions = backup_path
            else:
                original_permissions = "default"  # Will use fallback restore
            
            metadata = {
                "name": os.path.basename(path) or path,
                "path": os.path.abspath(path),
                "type": item_type,
                "original_permissions": original_permissions,
                "filesystem": "ntfs",  # Windows is typically NTFS
                "lock_method": "icacls",
                "locked_at": int(time.time())
            }
            
            print(f"  [Item] Metadata: {metadata['name']} | ACL backed up | icacls")
            return metadata
            
        except Exception as e:
            print(f"[Item] Error getting metadata for {path}: {e}")
            return None
    
    def _lock_item(self, item: Dict) -> bool:
        """
        Lock file or folder using ProcessMonitor (process-level interception).
        
        Does NOT use ACL deny rules because:
        1. ACL deny prevents file access completely
        2. This prevents our app from intercepting and showing password dialog
        3. Instead, ProcessMonitor scans for process access and intercepts
        
        This matches Linux behavior: monitor file access → show password dialog
        """
        path = item['path']
        
        if not os.path.exists(path):
            print(f"[Item] Path no longer exists: {path}")
            return False
        
        # Just record that it's locked - actual monitoring done by ProcessMonitor
        print(f"  [Item] Locked (monitored by ProcessMonitor): {path}")
        return True
    
    def _unlock_item(self, item: Dict) -> bool:
        """
        Unlock file or folder by removing monitoring.
        
        Since we're using ProcessMonitor (process-level interception) instead
        of ACL deny rules, there are no ACL rules to remove. This just marks
        the item as unlocked in the locked_items list.
        
        The ProcessMonitor will stop intercepting once the item is removed
        from the locked_items list.
        """
        path = item['path']
        
        if not os.path.exists(path):
            print(f"[Item] Path no longer exists: {path}")
            return True  # Consider it "unlocked" if it doesn't exist
        
        # Just log that it's unlocked - ProcessMonitor handles the rest
        print(f"  [Item] Unlocked (stopped monitoring): {path}")
        return True
    
    def _lock_config_file(self, path: str):
        """
        Lock config file - uses only file attributes (hidden + system + readonly).
        
        NOTE: Does NOT use ACL deny rules because config files need frequent 
        temporary unlocking for reads/writes, and ACL DENY causes error code 5 
        when trying to unprotect.
        
        Config files are protected by:
        1. File attributes (HIDDEN + SYSTEM + READONLY)  
        2. Only FadCrypt can modify via FileProtection safe_write/read
        """
        # Config files should only use file attributes, not ACL deny rules
        # ACL locks cause error code 5 when trying to temporarily unlock
        # This function is intentionally a no-op
        pass
    
    def start_monitoring(self, password_callback=None, get_state_func=None, set_state_func=None, log_activity_func=None):
        """
        Start monitoring locked files for access attempts.
        
        Uses NativeProcessMonitor (Windows API NtQuerySystemInformation).
        Queries kernel handle table directly - no external tools or psutil limitations.
        
        Args:
            password_callback: Function to verify password, returns bool (True if correct)
            get_state_func: Function to get monitoring state
            set_state_func: Function to update monitoring state
            log_activity_func: Function to log activity events
        """
        if hasattr(self, '_monitor') and self._monitor is not None:
            print("[FileLockManager] Monitoring already started")
            return False
        
        try:
            from core.windows.native_api_v2 import NativeAPIMonitorV2
            
            if not self.locked_items:
                print("[FileLockManager] No locked files to monitor")
                return False
            
            print(f"[FileLockManager] Starting native API monitor for {len(self.locked_items)} items")
            
            def on_access(path, pid, proc_name):
                """Process access detected"""
                if password_callback:
                    password_callback(path)
                print(f"[Access] {proc_name} (PID {pid}) -> {os.path.basename(path)}")
            
            # Create and start monitor
            self._monitor = NativeAPIMonitorV2(
                locked_items=list(self.locked_items),
                callback=on_access,
                scan_interval=1.0  # Query every second
            )
            self._monitor.start()
            
            print("[FileLockManager] OK: Native API v2 monitor started")
            return True
            
        except Exception as e:
            print(f"[FileLockManager] Error starting monitor: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def stop_monitoring(self):
        """Stop monitoring locked files"""
        if hasattr(self, '_monitor') and self._monitor is not None:
            try:
                self._monitor.stop()
                self._monitor = None
                return True
            except Exception as e:
                print(f"[FileLockManager] Error stopping monitor: {e}")
                self._monitor = None
                return False
        return False

    def _unlock_config_file(self, path: str):
        """Unlock config file"""
        if not os.path.exists(path):
            return
        
        try:
            # Remove deny rules
            subprocess.run(
                ['icacls', path, '/remove:d', 'Everyone'],
                capture_output=True,
                timeout=10
            )
        except Exception as e:
            print(f"  [Config] Error unlocking {path}: {e}")
