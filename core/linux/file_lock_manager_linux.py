"""
Linux File Lock Manager

Implements file/folder locking using chmod permissions and chattr attributes via elevated daemon.
Uses safe write logic like Windows implementation.
Unified approach with daemon for elevated operations.
Integrates with FileEncryptionManagerLinux for encrypted file/folder protection.
"""

import os
import json
from typing import Dict, Optional
import time

from core.file_lock_manager import FileLockManager
from core.verbose_logger import vlog


class FileLockManagerLinux(FileLockManager):
    """Linux implementation of file/folder locking using chmod and chattr"""
    
    def __init__(self, config_folder: str, app_locker=None):
        super().__init__(config_folder, app_locker)
        self.permission_backup_folder = os.path.join(config_folder, "permission_backups")
        os.makedirs(self.permission_backup_folder, exist_ok=True)
        
        # Initialize encryption manager for Linux
        from core.linux.file_encryption_manager_linux import FileEncryptionManagerLinux
        from core.crypto_manager import CryptoManager
        self.encryption_manager = FileEncryptionManagerLinux(config_folder, CryptoManager())
    
    def _get_permission_backup_path(self, item_path: str) -> str:
        """Get path for permission backup file"""
        # Create safe filename from path
        safe_name = item_path.replace('/', '_').replace(':', '_')
        return os.path.join(self.permission_backup_folder, f"{safe_name}.perm")
    
    def _backup_permissions(self, path: str) -> bool:
        """Backup original permissions for path"""
        from core.file_protection import safe_write_to_protected_file
        
        backup_path = self._get_permission_backup_path(path)
        
        try:
            # Get current permissions
            stat_info = os.stat(path)
            permissions = {
                'mode': stat_info.st_mode,
                'uid': stat_info.st_uid,
                'gid': stat_info.st_gid
            }
            
            # Save to backup file using existing safe write
            content = json.dumps(permissions)
            success, error = safe_write_to_protected_file(backup_path, content)
            if success:
                vlog(f"  [PERM] Backed up to: {os.path.basename(backup_path)}")
                return True
            else:
                vlog(f"  [PERM] Error backing up: {error}")
                return False
                
        except Exception as e:
            vlog(f"  [PERM] Error backing up: {e}")
            return False
    
    def _restore_permissions(self, path: str) -> bool:
        """Restore permissions from backup using daemon"""
        backup_path = self._get_permission_backup_path(path)
        
        if not os.path.exists(backup_path):
            vlog("  [PERM] No backup found, using default restore")
            # Set reasonable default permissions via daemon
            try:
                client = self._get_daemon_client()
                if client and client.is_available():
                    mode = 0o755 if os.path.isdir(path) else 0o644
                    success, _ = client.chmod([path], mode)
                    return success
                else:
                    vlog("  [PERM] Error: Daemon not available for default restore")
                    return False
            except Exception:
                return False
        
        try:
            # Restore permissions from backup using existing safe read
            from core.file_protection import safe_read_from_protected_file
            success, content = safe_read_from_protected_file(backup_path)
            if not success:
                vlog(f"  [PERM] Error reading backup: {content}")
                return False
            
            permissions = json.loads(content)
            
            # Use daemon for chmod
            client = self._get_daemon_client()
            if client and client.is_available():
                success, _ = client.chmod([path], permissions['mode'])
                if success:
                    vlog("  [PERM] Restored from backup via daemon")
                    # Clean up backup file
                    try:
                        os.remove(backup_path)
                    except Exception:
                        pass
                    return True
                else:
                    vlog("  [PERM] Error: Daemon chmod failed")
                    return False
            else:
                vlog("  [PERM] Error: Daemon not available")
                return False
                
        except Exception as e:
            vlog(f"  [PERM] Error restoring: {e}")
            return False
    
    def _get_item_metadata(self, path: str, item_type: str) -> Optional[Dict]:
        """
        Get metadata for file or folder.
        
        Returns dict with: name, path, type, original_permissions (backup path), filesystem, lock_method
        """
        
        try:
            # Backup permissions first
            backup_path = self._get_permission_backup_path(path)
            if self._backup_permissions(path):
                original_permissions = backup_path
            else:
                original_permissions = "default"  # Will use fallback restore
            
            metadata = {
                "name": os.path.basename(path) or path,
                "path": os.path.abspath(path),
                "type": item_type,
                "original_permissions": original_permissions,
                "filesystem": "ext4",  # Linux is typically ext4
                "lock_method": "chmod+chattr",
                "locked_at": int(time.time())
            }
            
            vlog(f"  [Item] Metadata: {metadata['name']} | Permissions backed up | chmod+chattr")
            return metadata
            
        except Exception as e:
            print(f"[Item] Error getting metadata for {path}: {e}")
            return None
    
    def _lock_item(self, item: Dict) -> bool:
        """
        Lock file or folder by encrypting (if enabled) then applying daemon protections.
        
        Encryption (if enabled):
        1. Converts file/folder to .fadcrypt format using AES-256-GCM
        2. Original file/folder is deleted after successful encryption
        3. Encrypted .fadcrypt file is then permission-locked
        
        Permission lock always applied:
        1. No permissions for owner/group/others (000) via daemon
        2. Immutable attribute via chattr +i via daemon
        3. Read-only visual indicator
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
        
        vlog(f"[DEBUG] Config dangerous_ops: {dangerous_ops}")
        vlog(f"[DEBUG] encryption_enabled={encryption_enabled}, has_manager={has_manager}, has_password={has_password}")
        
        if encryption_enabled:
            vlog(f"[Item] Encryption feature ENABLED")
            vlog(f"[Item] Has manager: {has_manager}, Has password: {has_password}")
        
        if encryption_enabled and has_manager and has_password:
            vlog(f"🔐 Encrypting: {os.path.basename(path)}")
            vlog(f"[Item] Encryption enabled - encrypting before lock...")
            item_type = item.get('type', 'file')
            success, encrypted_path, error = self.encryption_manager.encrypt_item(
                path,
                self.password_bytes,
                item_type
            )
            
            if success:
                vlog(f"✓ Encrypted successfully: {os.path.basename(encrypted_path)}")
                vlog(f"  [Encrypt] ✓ Successfully encrypted to .fadcrypt")
                # Update item metadata to track encryption
                item['is_encrypted'] = True
                item['encrypted_path'] = encrypted_path
                # Now lock the encrypted file instead of original
                path = encrypted_path
            else:
                vlog(f"❌ Encryption failed: {error}")
                vlog(f"  [Encrypt] ❌ Encryption failed: {error}")
                return False
        else:
            # Mark as not encrypted
            item['is_encrypted'] = False
            item['encrypted_path'] = None
        
        client = self._get_daemon_client()
        if not client or not client.is_available():
            vlog("  [Item] Error: Daemon not available")
            return False
        
        # Step 1: Remove all permissions via daemon
        success, msg = client.chmod([path], 0o000)
        if success:
            vlog(f"  [Item] Removed all permissions via daemon: {os.path.basename(path)}")
        else:
            vlog(f"  [Item] Warning: daemon chmod failed: {msg}")
        
        # Step 2: Apply chattr immutable attribute via daemon
        success, msg = client.chattr([path], set_immutable=True)
        if success:
            vlog(f"  [Item] Applied immutable attribute via daemon: {os.path.basename(path)}")
        else:
            vlog(f"  [Item] Warning: daemon chattr failed: {msg}")
        
        vlog(f"  [Item] Locked: {os.path.basename(path)}")
        return True
    
    def _unlock_item(self, item: Dict) -> bool:
        """
        Unlock file or folder using daemon for elevated operations.
        
        If item was encrypted, decrypt it first before unlocking.
        
        This removes:
        1. Immutable attribute via daemon chattr -i
        2. Restores original permissions from backup via daemon
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
                
                # Step 1: Remove immutable attribute first (if exists)
                client = self._get_daemon_client()
                if client and client.is_available():
                    success, msg = client.chattr([encrypted_path], set_immutable=False)
                    if success:
                        vlog(f"  [Item] Removed immutable attribute from encrypted file")
                    else:
                        vlog(f"  [Item] Warning: Could not remove immutable from encrypted file: {msg}")
                
                # Step 2: Restore permissions on encrypted file so we can decrypt it
                if self._restore_permissions(encrypted_path):
                    vlog(f"  [Item] Restored permissions on encrypted file")
                else:
                    # Set reasonable permissions via daemon
                    if client and client.is_available():
                        mode = 0o644  # Read/write for owner, read for group/others
                        success, _ = client.chmod([encrypted_path], mode)
                        if success:
                            vlog(f"  [Item] Granted access on encrypted file")
                        else:
                            vlog(f"  [Item] Warning: Could not grant access to encrypted file")
                
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
                        vlog(f"✓ Decrypted successfully: {os.path.basename(path)}")
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
        
        client = self._get_daemon_client()
        if not client or not client.is_available():
            vlog("  [Item] Error: Daemon not available")
            return False
        
        # Step 1: Remove chattr immutable attribute via daemon
        success, msg = client.chattr([path], set_immutable=False)
        if success:
            vlog(f"  [Item] Removed immutable attribute via daemon: {os.path.basename(path)}")
        else:
            vlog(f"  [Item] Warning: daemon chattr removal failed: {msg}")
        
        # Step 2: Restore permissions from backup via daemon
        if self._restore_permissions(path):
            vlog(f"  [Item] Restored permissions from backup: {os.path.basename(path)}")
        else:
            # Set reasonable default permissions via daemon
            mode = 0o755 if os.path.isdir(path) else 0o644
            success, _ = client.chmod([path], mode)
            if success:
                vlog(f"  [Item] Set default permissions via daemon: {os.path.basename(path)}")
            else:
                vlog(f"  [Item] Error: Failed to set default permissions via daemon: {os.path.basename(path)}")
                # Fallback to os.chmod
                try:
                    os.chmod(path, mode)
                    vlog(f"  [Item] Set default permissions via os.chmod: {os.path.basename(path)}")
                except Exception as e:
                    vlog(f"  [Item] Error: os.chmod also failed: {e}")
        
        vlog(f"  [Item] Unlocked: {os.path.basename(path)}")
        return True
    
    def _lock_config_file(self, path: str):
        """
        Lock config file using daemon - uses only permissions (read-only).
        
        NOTE: Does NOT use chattr immutable because config files need frequent 
        temporary unlocking for reads/writes, and chattr +i prevents all modifications.
        
        Config files are protected by:
        1. Read-only permissions (444) via daemon
        2. Only FadCrypt can modify via safe_write/read
        """
        client = self._get_daemon_client()
        if client and client.is_available():
            success, msg = client.chmod([path], 0o444)
            if not success:
                vlog(f"⚠️  Error locking config {path} via daemon: {msg}")
        else:
            vlog(f"⚠️  Error: Daemon not available for config locking: {path}")
    
    def _unlock_config_file(self, path: str):
        """Unlock config file using daemon"""
        client = self._get_daemon_client()
        if client and client.is_available():
            success, msg = client.chmod([path], 0o644)
            if not success:
                vlog(f"⚠️  Error unlocking config {path} via daemon: {msg}")
        else:
            vlog(f"⚠️  Error: Daemon not available for config unlocking: {path}")
    
    def start_monitoring(self):
        """
        Activate file locking protection.
        
        Linux uses static file protection via chmod+chattr - no monitoring needed.
        Files are protected by permissions and immutable flags, not runtime monitoring.
        """
        if not self.locked_items:
            vlog("No locked files to protect")
            return False
        
        vlog(f"Static file protection active for {len(self.locked_items)} items")
        vlog("OK: File protection via chmod+chattr active")
        return True
    
    def stop_monitoring(self):
        """Deactivate file locking protection"""
        # No background processes to stop - static protection only
        return True
    
    def _get_daemon_client(self):
        """Get elevated daemon client"""
        try:
            from core.linux.elevated_daemon_client import get_elevated_client
            return get_elevated_client()
        except ImportError:
            return None
    
    def toggle_tamper_proof(self, path: str, enable: bool) -> bool:
        """
        Toggle tamper-proof protections on Linux via chmod/chattr.
        
        Args:
            path: Path to the file or folder
            enable: True to enable protections, False to disable
        
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(path):
            return False
        
        client = self._get_elevated_client()
        if not client:
            vlog(f"[Toggle] Error: Daemon not available")
            return False
        
        try:
            if enable:
                # Apply same protections as _lock_item: chmod 000 via daemon, then chattr +i
                success, msg = client.chmod([path], 0o000)
                if success:
                    vlog(f"  [Toggle] Applied 000 permissions via daemon: {os.path.basename(path)}")
                    # Set immutable flag via daemon
                    client.execute_command("chattr", ["+i", path])
                    return True
                else:
                    vlog(f"  [Toggle] daemon chmod failed: {msg}")
                    return False
            else:
                # Disable tamper-proof protections via daemon
                if os.path.isdir(path):
                    success, msg = client.chmod([path], 0o755)
                else:
                    success, msg = client.chmod([path], 0o644)
                
                if success:
                    vlog(f"  [Toggle] Restored permissions via daemon: {os.path.basename(path)}")
                    client.execute_command("chattr", ["-i", path])
                    return True
                else:
                    vlog(f"  [Toggle] daemon chmod failed: {msg}")
                    return False
        except Exception as e:
            vlog(f"Error toggling tamper-proof on {path}: {e}")
            return False
