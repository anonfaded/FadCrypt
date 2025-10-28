"""
Windows Shell Context Menu Integration for FadCrypt

Registers FadCrypt as context menu options for right-click on files/folders.
Uses Windows Registry with direct commands (not submenus - Win 11 limitation).
Supports both script execution (development) and packaged app execution (production).
"""

import os
import sys
import winreg
import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ContextMenuManager:
    """Manage Windows shell context menu registration"""

    REGISTRY_BASE = r"Software\Classes"
    # Direct commands for files and folders - no submenus on Windows 11
    FILE_LOCK_KEY = r"*\shell\FadCryptLock"
    FILE_UNLOCK_KEY = r"*\shell\FadCryptUnlock"
    FOLDER_LOCK_KEY = r"Directory\shell\FadCryptLock"
    FOLDER_UNLOCK_KEY = r"Directory\shell\FadCryptUnlock"

    def __init__(self, exe_path: Optional[str] = None, fadcrypt_folder: Optional[str] = None, is_packaged: Optional[bool] = None):
        """
        Args:
            exe_path: Path to FadCrypt executable/script
            fadcrypt_folder: Path to FadCrypt installation folder
            is_packaged: Whether running from PyInstaller bundle
        """
        if is_packaged is None:
            is_packaged = hasattr(sys, '_MEIPASS')

        if is_packaged:
            # Running from PyInstaller bundle
            if exe_path is None:
                exe_path = sys.executable  # Use the actual executable path
            if fadcrypt_folder is None:
                exe_dir = os.path.dirname(sys.executable)
                fadcrypt_folder = exe_dir
                # Check if we're running from an installed location (not development dist)
                # If fadcrypt is in PATH, use the command name instead of full path
                self.use_command_name = self._is_fadcrypt_in_path()
        else:
            # Running from source/script
            if exe_path is None:
                # Use the script path, not the python executable
                import __main__
                if hasattr(__main__, '__file__'):
                    exe_path = os.path.abspath(__main__.__file__)
                else:
                    exe_path = os.path.join(os.getcwd(), 'FadCrypt.py')
            if fadcrypt_folder is None:
                # When running from source, use the script directory
                import __main__
                if hasattr(__main__, '__file__'):
                    script_dir = os.path.dirname(os.path.abspath(__main__.__file__))
                else:
                    script_dir = os.getcwd()
                fadcrypt_folder = script_dir

        self.exe_path = exe_path
        self.fadcrypt_folder = fadcrypt_folder
        self.is_packaged = is_packaged
        self.batch_files_dir = os.path.join(fadcrypt_folder, 'core', 'windows')
    
    def _is_fadcrypt_in_path(self) -> bool:
        """Check if fadcrypt command is available in PATH"""
        try:
            # Use where without shell to avoid quoting issues
            result = subprocess.run(['where', 'fadcrypt'], capture_output=True, text=True)
            return result.returncode == 0 and 'fadcrypt' in result.stdout.lower()
        except:
            return False
    
    def is_context_menu_registered(self) -> bool:
        """Check if FadCrypt context menu entries are already registered"""
        try:
            # Check if at least one key exists
            winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                          f"{self.REGISTRY_BASE}\\{self.FILE_LOCK_KEY}", 
                          0, winreg.KEY_READ)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False
    
    def register_context_menu(self) -> bool:
        """Register Lock/Unlock options in context menu - direct commands (no submenus)"""
        try:
            # Register for files
            self._register_file_lock()
            self._register_file_unlock()
            # Register for folders
            self._register_folder_lock()
            self._register_folder_unlock()
            logger.info("Context menu registered successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to register context menu: {e}")
            return False
    
    def register_context_menu_if_needed(self) -> tuple[bool, bool]:
        """
        Register context menu only if not already registered.
        
        Returns:
            tuple: (success: bool, was_already_registered: bool)
        """
        if self.is_context_menu_registered():
            logger.info("Context menu already registered, skipping registration")
            return True, True
        
        success = self.register_context_menu()
        return success, False
    
    def force_register_context_menu(self) -> bool:
        """
        Force re-register context menu entries, even if already registered.
        Useful for updating paths or fixing corrupted entries.
        """
        logger.info("Force re-registering context menu...")
        # First unregister, then register
        self.unregister_context_menu()
        return self.register_context_menu()
    
    def _register_file_lock(self):
        """Register Lock for files"""
        try:
            key_path = f"{self.REGISTRY_BASE}\\{self.FILE_LOCK_KEY}"
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Lock with FadCrypt")
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, f"{self.exe_path},0")
            
            # Direct execution without start wrapper - fastest (50ms) and most reliable
            cmd_key = f"{key_path}\\command"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_key) as key:
                if self.is_packaged:
                    # Packaged app - direct cmd.exe execution
                    if hasattr(self, 'use_command_name') and self.use_command_name:
                        cmd = 'cmd.exe /c fadcrypt --lock "%1"'
                    else:
                        cmd = f'cmd.exe /c "{self.exe_path}" --lock "%1"'
                else:
                    # Script execution - use python.exe (not pythonw.exe) so dialog can show
                    python_path = sys.executable
                    cmd = f'cmd.exe /c "{python_path}" "{self.exe_path}" --lock "%1"'
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, cmd)
            
            logger.debug(f"Registered file lock context menu: {key_path}")
        except Exception as e:
            logger.error(f"Failed to register file lock: {e}")
            raise
    
    def _register_file_unlock(self):
        """Register Unlock for files"""
        try:
            key_path = f"{self.REGISTRY_BASE}\\{self.FILE_UNLOCK_KEY}"
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Unlock with FadCrypt")
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, f"{self.exe_path},0")
            
            # Direct execution without start wrapper - fastest (50ms) and most reliable
            cmd_key = f"{key_path}\\command"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_key) as key:
                if self.is_packaged:
                    # Packaged app - direct cmd.exe execution
                    if hasattr(self, 'use_command_name') and self.use_command_name:
                        cmd = 'cmd.exe /c fadcrypt --unlock "%1"'
                    else:
                        cmd = f'cmd.exe /c "{self.exe_path}" --unlock "%1"'
                else:
                    # Script execution - use python.exe (not pythonw.exe) so dialog can show
                    python_path = sys.executable
                    cmd = f'cmd.exe /c "{python_path}" "{self.exe_path}" --unlock "%1"'
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, cmd)
            
            logger.debug(f"Registered file unlock context menu: {key_path}")
        except Exception as e:
            logger.error(f"Failed to register file unlock: {e}")
            raise
    
    def _register_folder_lock(self):
        """Register Lock for folders"""
        try:
            key_path = f"{self.REGISTRY_BASE}\\{self.FOLDER_LOCK_KEY}"
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Lock with FadCrypt")
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, f"{self.exe_path},0")
            
            # Direct execution without start wrapper - fastest (50ms) and most reliable
            cmd_key = f"{key_path}\\command"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_key) as key:
                if self.is_packaged:
                    # Packaged app - direct cmd.exe execution
                    if hasattr(self, 'use_command_name') and self.use_command_name:
                        cmd = 'cmd.exe /c fadcrypt --lock "%1"'
                    else:
                        cmd = f'cmd.exe /c "{self.exe_path}" --lock "%1"'
                else:
                    # Script execution - use python.exe (not pythonw.exe) so dialog can show
                    python_path = sys.executable
                    cmd = f'cmd.exe /c "{python_path}" "{self.exe_path}" --lock "%1"'
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, cmd)
            
            logger.debug(f"Registered folder lock context menu: {key_path}")
        except Exception as e:
            logger.error(f"Failed to register folder lock: {e}")
            raise
    
    def _register_folder_unlock(self):
        """Register Unlock for folders"""
        try:
            key_path = f"{self.REGISTRY_BASE}\\{self.FOLDER_UNLOCK_KEY}"
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Unlock with FadCrypt")
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, f"{self.exe_path},0")
            
            # Direct execution without start wrapper - fastest (50ms) and most reliable
            cmd_key = f"{key_path}\\command"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_key) as key:
                if self.is_packaged:
                    # Packaged app - direct cmd.exe execution
                    if hasattr(self, 'use_command_name') and self.use_command_name:
                        cmd = 'cmd.exe /c fadcrypt --unlock "%1"'
                    else:
                        cmd = f'cmd.exe /c "{self.exe_path}" --unlock "%1"'
                else:
                    # Script execution - use python.exe (not pythonw.exe) so dialog can show
                    python_path = sys.executable
                    cmd = f'cmd.exe /c "{python_path}" "{self.exe_path}" --unlock "%1"'
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, cmd)
            
            logger.debug(f"Registered folder unlock context menu: {key_path}")
        except Exception as e:
            logger.error(f"Failed to register folder unlock: {e}")
            raise
    
    def unregister_context_menu(self) -> bool:
        """Remove context menu entries"""
        try:
            keys_to_remove = [
                f"{self.REGISTRY_BASE}\\{self.FILE_LOCK_KEY}",
                f"{self.REGISTRY_BASE}\\{self.FILE_UNLOCK_KEY}",
                f"{self.REGISTRY_BASE}\\{self.FOLDER_LOCK_KEY}",
                f"{self.REGISTRY_BASE}\\{self.FOLDER_UNLOCK_KEY}"
            ]

            removed_count = 0
            for key_path in keys_to_remove:
                try:
                    logger.info(f"Attempting to remove registry key: {key_path}")
                    self._delete_key(winreg.HKEY_CURRENT_USER, key_path)
                    removed_count += 1
                    logger.info(f"Successfully removed registry key: {key_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove key {key_path}: {e}")

            logger.info(f"Context menu cleanup completed: {removed_count}/{len(keys_to_remove)} keys removed")
            return removed_count > 0
        except Exception as e:
            logger.error(f"Failed to unregister context menu: {e}")
            return False
    
    def _delete_key(self, hive, path):
        """Recursively delete registry key and all its subkeys"""
        try:
            # First delete all subkeys recursively
            with winreg.OpenKey(hive, path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
                try:
                    i = 0
                    while True:
                        subkey = winreg.EnumKey(key, i)
                        subkey_path = f"{path}\\{subkey}"
                        self._delete_key(hive, subkey_path)
                        i += 1
                except OSError:
                    # No more subkeys
                    pass

            # Now delete the key itself
            parent, key_name = path.rsplit('\\', 1)
            with winreg.OpenKey(hive, parent, 0, winreg.KEY_WRITE) as parent_key:
                winreg.DeleteKey(parent_key, key_name)

        except FileNotFoundError:
            # Key doesn't exist, that's fine
            pass
        except Exception as e:
            logger.warning(f"Failed to delete registry key {path}: {e}")
