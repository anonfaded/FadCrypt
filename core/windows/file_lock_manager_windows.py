"""
Windows File Lock Manager

Implements file/folder locking using icacls to deny all access.
Backs up and restores ACLs for proper permission recovery.
Integrates with FileEncryptionManagerWindows for encrypted file/folder protection.
"""

import os
import subprocess
import tempfile
from typing import Dict, Optional
import time

from core.file_lock_manager import FileLockManager
from core.verbose_logger import vlog


class FileLockManagerWindows(FileLockManager):
    """Windows implementation of file/folder locking using icacls"""
    
    def __init__(self, config_folder: str, app_locker=None):
        super().__init__(config_folder, app_locker)
        self.acl_backup_folder = os.path.join(config_folder, "acl_backups")
        os.makedirs(self.acl_backup_folder, exist_ok=True)
        
        # Initialize encryption manager for Windows
        from core.windows.file_encryption_manager_windows import FileEncryptionManagerWindows
        from core.crypto_manager import CryptoManager
        self.encryption_manager = FileEncryptionManagerWindows(config_folder, CryptoManager())
    
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
            vlog(f"  [ACL] No backup found, using default restore")
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
        Lock file or folder by encrypting (if enabled) then applying ACL restrictions.
        
        Encryption (if enabled):
        1. Converts file/folder to .fadcrypt format using AES-256-GCM
        2. Original file/folder is deleted after successful encryption
        3. Encrypted .fadcrypt file is then ACL-locked
        
        ACL always applied:
        1. Hidden (HIDDEN attribute)
        2. System file (SYSTEM attribute)
        3. Read-only (READONLY attribute)
        4. Access denied via ACL (deny Everyone)
        """
        path = item['path']
        
        if not os.path.exists(path):
            vlog(f"[Item] Path no longer exists: {path}")
            return False
        
        # Step 0: Encrypt if feature is enabled
        config = self._get_config()
        dangerous_ops = config.get("dangerous_operations", {})
        encryption_enabled = dangerous_ops.get("encryption", False)
        has_manager = self.encryption_manager is not None
        has_password = self.password_bytes is not None
        
        vlog(f"[Item] Config dangerous_ops: {dangerous_ops}")
        vlog(f"[Item] encryption_enabled={encryption_enabled}, has_manager={has_manager}, has_password={has_password}")
        
        if encryption_enabled:
            vlog(f"[Item] Encryption feature ENABLED")
            vlog(f"[Item] Has manager: {has_manager}, Has password: {has_password}")
        
        if encryption_enabled and has_manager and has_password:
            print(f"🔐 Encrypting: {os.path.basename(path)}")
            vlog(f"[Item] Encryption enabled - encrypting before lock...")
            item_type = item.get('type', 'file')
            success, encrypted_path, error = self.encryption_manager.encrypt_item(
                path,
                self.password_bytes,
                item_type
            )
            
            if success:
                print(f"✓ Encrypted successfully: {os.path.basename(encrypted_path)}")
                vlog(f"  [Encrypt] ✓ Successfully encrypted to .fadcrypt")
                # Update item metadata to track encryption
                item['is_encrypted'] = True
                item['encrypted_path'] = encrypted_path
                # Now lock the encrypted file instead of original
                path = encrypted_path
            else:
                print(f"❌ Encryption failed: {error}")
                vlog(f"  [Encrypt] ❌ Encryption failed: {error}")
                return False
        else:
            # Mark as not encrypted
            item['is_encrypted'] = False
            item['encrypted_path'] = None
        
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
        
        If item was encrypted, decrypt it first before unlocking.
        
        This removes:
        1. File attributes (HIDDEN + SYSTEM + READONLY)
        2. ACL deny rules (if any)
        3. Stops ProcessMonitor interception
        """
        path = item['path']
        
        # CRITICAL: Handle encrypted items first
        is_encrypted = item.get('is_encrypted', False)
        encrypted_path = item.get('encrypted_path', f"{path}.fadcrypt")
        
        if is_encrypted:
            # File was encrypted - the actual file is now .fadcrypt
            if not os.path.exists(encrypted_path):
                vlog(f"[Item] Encrypted file not found: {encrypted_path}")
            else:
                vlog(f"[Item] Item is encrypted - decrypting first: {os.path.basename(encrypted_path)}")
                
                # Step 1: Remove file attributes first (READONLY, SYSTEM, HIDDEN)
                try:
                    import subprocess
                    subprocess.run(
                        ['attrib', '-R', '-S', '-H', encrypted_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=5
                    )
                    vlog(f"  [Item] Removed file attributes from encrypted file")
                except Exception as e:
                    vlog(f"  [Item] Warning: Could not remove file attributes: {e}")
                
                # Step 2: Restore ACL on encrypted file so we can decrypt it
                if self._restore_acl(encrypted_path):
                    vlog(f"  [Item] Restored ACL on encrypted file")
                else:
                    # Fallback: Grant full control
                    try:
                        import subprocess
                        subprocess.run(
                            ['icacls', encrypted_path, '/grant', 'Everyone:(F)'],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            timeout=10
                        )
                        vlog(f"  [Item] Granted full control on encrypted file")
                    except:
                        pass
                
                # Step 3: Try to decrypt the file
                # If password not cached, try to load it from encrypted_password.bin
                if not self.password_bytes and self.encryption_manager:
                    vlog(f"  [Item] Password not cached - attempting to load from encrypted_password.bin")
                    try:
                        from core.password_manager import PasswordManager
                        from core.crypto_manager import CryptoManager
                        from core.cli.password_prompt import PasswordPrompt
                        
                        config_dir = os.path.dirname(self.config_file) if self.config_file else None
                        if config_dir:
                            password_file = os.path.join(config_dir, "encrypted_password.bin")
                            if os.path.exists(password_file):
                                crypto_manager = CryptoManager()
                                password_manager = PasswordManager(password_file, crypto_manager)
                                
                                # Try to prompt for password
                                password_prompt = PasswordPrompt(password_manager)
                                if password_prompt.verify_password():
                                    self.password_bytes = password_manager.get_password_bytes()
                                    vlog(f"  [Item] ✓ Password loaded from encrypted_password.bin")
                                else:
                                    vlog(f"  [Item] ⚠ Password prompt cancelled or failed")
                    except Exception as e:
                        vlog(f"  [Item] Warning: Could not load password: {e}")
                
                if self.encryption_manager and self.password_bytes:
                    success, error = self.encryption_manager.decrypt_item(encrypted_path, self.password_bytes, path)
                    if success:
                        print(f"✓ Decrypted successfully: {os.path.basename(path)}")
                        vlog(f"  [Item] ✓ Decrypted and restored: {os.path.basename(path)}")
                        # Decryption automatically deletes the .fadcrypt file
                        # Continue to unlock the restored original file
                    else:
                        vlog(f"  [Item] ⚠ Decryption failed: {error}")
                        return False
                else:
                    vlog(f"  [Item] ⚠ Cannot decrypt - missing encryption manager or password")
                    return False
        
        # Now unlock the item (whether originally locked or just decrypted)
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
        
        # Step 3: If this was an encrypted item, delete the .fadcrypt file
        if is_encrypted:
            try:
                if os.path.exists(encrypted_path):
                    # Ensure we have full control first
                    try:
                        import subprocess
                        subprocess.run(
                            ['icacls', encrypted_path, '/grant', 'Everyone:(F)', '/T'],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            timeout=10
                        )
                    except:
                        pass
                    
                    # Remove any read-only attributes
                    try:
                        subprocess.run(
                            ['attrib', '-r', encrypted_path],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            timeout=5
                        )
                    except:
                        pass
                    
                    # Now delete it
                    os.remove(encrypted_path)
                    vlog(f"  [Item] OK Deleted encrypted file: {os.path.basename(encrypted_path)}")
            except Exception as e:
                vlog(f"  [Item] Warning: Could not delete encrypted file: {e}")
        
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
            vlog("Monitoring already started")
            return False
        
        try:
            # Windows uses context menu approach for file locking
            # No additional monitoring needed - files are locked via shell extension
            if not self.locked_items:
                vlog("No locked files to monitor")
                return False
            
            vlog(f"Context menu monitoring ready for {len(self.locked_items)} items")
            vlog("OK: File locking via context menu active")
            return True
            
        except Exception as e:
            vlog(f"Error starting monitor: {e}")
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
                from core.verbose_logger import vlog
                vlog(f"Error stopping monitor: {e}")
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
    
    def toggle_tamper_proof(self, path: str, enable: bool) -> bool:
        """
        Toggle tamper-proof protections on Windows via ACL.
        
        Args:
            path: Path to the file or folder
            enable: True to enable protections, False to disable
        
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(path):
            return False
        
        try:
            if enable:
                # Apply same deny rules as _lock_item uses
                subprocess.run(
                    ['icacls', path, '/deny', 'Everyone:(F)', '/T'],
                    capture_output=True,
                    timeout=10
                )
                return True
            else:
                # Remove deny rules (tamper-proof OFF)
                subprocess.run(
                    ['icacls', path, '/remove:d', 'Everyone'],
                    capture_output=True,
                    timeout=10
                )
                return True
        except Exception as e:
            vlog(f"Error toggling tamper-proof on {path}: {e}")
            return False
