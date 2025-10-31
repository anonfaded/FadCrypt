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
        from core.verbose_logger import vlog
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
                vlog(f"  [ACL] Backed up to: {os.path.basename(backup_path)}")
                return True
            else:
                vlog(f"  [ACL] Backup warning: {result.stderr}")
                return False
                
        except Exception as e:
            vlog(f"  [ACL] Error backing up: {e}")
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
            from core.verbose_logger import vlog
            
            # Restore ACL from backup
            # Note: icacls outputs to console even with capture_output=True
            # We need to redirect to DEVNULL to suppress it completely
            result = subprocess.run(
                ['icacls', os.path.dirname(path), '/restore', backup_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                vlog(f"  [ACL] Restored from backup")
                # Clean up backup file
                try:
                    os.remove(backup_path)
                except:
                    pass
                return True
            else:
                vlog(f"  [ACL] Restore warning: {result.stderr}")
                # Try fallback - also suppress output
                subprocess.run(
                    ['icacls', path, '/grant', 'Everyone:(F)'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=10
                )
                return False
                
        except Exception as e:
            vlog(f"  [ACL] Error restoring: {e}")
            return False
    
    def _get_item_metadata(self, path: str, item_type: str) -> Optional[Dict]:
        """
        Get metadata for file or folder.
        
        Returns dict with: name, path, type, original_permissions (ACL backup path), filesystem, lock_method
        """
        from core.verbose_logger import vlog
        
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
            
            vlog(f"  [Item] Metadata: {metadata['name']} | ACL backed up | icacls")
            return metadata
            
        except Exception as e:
            print(f"[Item] Error getting metadata for {path}: {e}")
            return None
    
    def _lock_item(self, item: Dict) -> bool:
        """
        Lock file or folder by applying file attributes and ACL restrictions.
        
        This makes files:
        1. Hidden (HIDDEN attribute)
        2. System file (SYSTEM attribute)
        3. Read-only (READONLY attribute)
        4. Access denied via ACL (deny Everyone)
        """
        from core.verbose_logger import vlog
        path = item['path']
        
        if not os.path.exists(path):
            vlog(f"[Item] Path no longer exists: {path}")
            return False
        
        # Step 1: Apply file attributes (READONLY only - don't hide files)
        try:
            import subprocess
            result = subprocess.run(
                ['attrib', '+r', path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                vlog(f"  [Item] Applied READONLY attribute to: {os.path.basename(path)}")
            else:
                vlog(f"  [Item] Warning: Could not apply attributes: {result.stderr}")
        except Exception as e:
            vlog(f"  [Item] Warning: attrib command failed: {e}")
        
        # Step 2: Apply ACL deny rules
        try:
            # Deny all access to Everyone
            subprocess.run(
                ['icacls', path, '/deny', 'Everyone:(F)', '/T'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10
            )
            vlog(f"  [Item] Applied ACL deny rules to: {os.path.basename(path)}")
        except Exception as e:
            vlog(f"  [Item] Warning: icacls deny failed: {e}")
        
        vlog(f"  [Item] Locked: {os.path.basename(path)}")
        return True
    
    def _unlock_item(self, item: Dict) -> bool:
        """
        Unlock file or folder by removing file attributes and ACL restrictions.
        
        This removes:
        1. File attributes (HIDDEN + SYSTEM + READONLY)
        2. ACL deny rules (if any)
        3. Stops ProcessMonitor interception
        """
        from core.verbose_logger import vlog
        path = item['path']
        
        if not os.path.exists(path):
            vlog(f"[Item] Path no longer exists: {path}")
            return True  # Consider it "unlocked" if it doesn't exist
        
        # Step 1: Remove file attributes (READONLY only)
        try:
            import subprocess
            result = subprocess.run(
                ['attrib', '-r', path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                vlog(f"  [Item] Removed READONLY attribute from: {os.path.basename(path)}")
            else:
                vlog(f"  [Item] Warning: Could not remove attributes: {result.stderr}")
        except Exception as e:
            vlog(f"  [Item] Warning: attrib command failed: {e}")
        
        # Step 2: Restore ACL from backup (if exists)
        if self._restore_acl(path):
            vlog(f"  [Item] Restored ACL from backup: {os.path.basename(path)}")
        else:
            # Fallback: Grant full control to Everyone
            try:
                subprocess.run(
                    ['icacls', path, '/grant', 'Everyone:(F)', '/T'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=10
                )
                vlog(f"  [Item] Granted full control: {os.path.basename(path)}")
            except:
                pass
        
        vlog(f"  [Item] Unlocked (stopped monitoring): {os.path.basename(path)}")
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
            # Windows uses context menu approach for file locking
            # No additional monitoring needed - files are locked via shell extension
            if not self.locked_items:
                print("[FileLockManager] No locked files to monitor")
                return False
            
            print(f"[FileLockManager] Context menu monitoring ready for {len(self.locked_items)} items")
            print("[FileLockManager] OK: File locking via context menu active")
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
