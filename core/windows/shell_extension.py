"""
Windows Shell Context Menu Integration for FadCrypt

Registers FadCrypt as context menu options for right-click on files/folders.
Uses Windows Registry with direct commands (not submenus - Win 11 limitation).
"""

import os
import sys
import winreg
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ContextMenuManager:
    """Manage Windows shell context menu registration"""
    
    REGISTRY_BASE = r"Software\Classes"
    # Direct commands for files and folders - no submenus on Windows 11
    FILE_LOCK_KEY = r"*\shell\FadCryptLock"
    FILE_UNLOCK_KEY = r"*\shell\FadCryptUnlock"
    FOLDER_LOCK_KEY = r"Directory\shell\FadCryptLock"
    FOLDER_UNLOCK_KEY = r"Directory\shell\FadCryptUnlock"
    
    def __init__(self, exe_path: str = None, fadcrypt_folder: str = None):
        """
        Args:
            exe_path: Path to FadCrypt executable (usually from PyInstaller)
            fadcrypt_folder: Path to FadCrypt installation folder (for batch files)
        """
        if exe_path is None:
            # Detect if running from PyInstaller bundle
            if hasattr(sys, '_MEIPASS'):
                exe_path = os.path.join(sys._MEIPASS, 'FadCrypt.exe')
                fadcrypt_folder = sys._MEIPASS
            else:
                exe_path = sys.executable
                # When running from source, use the script directory
                import __main__
                fadcrypt_folder = os.path.dirname(os.path.abspath(__main__.__file__)) if hasattr(__main__, '__file__') else os.getcwd()
        
        if fadcrypt_folder is None:
            fadcrypt_folder = os.path.dirname(exe_path)
        
        self.exe_path = exe_path
        self.fadcrypt_folder = fadcrypt_folder
    
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
    
    def _register_file_lock(self):
        """Register Lock for files"""
        key_path = f"{self.REGISTRY_BASE}\\{self.FILE_LOCK_KEY}"
        
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Lock with FadCrypt")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, f"{self.exe_path},0")
        
        # Use batch file wrapper to avoid "open with" dialog
        cmd_key = f"{key_path}\\command"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_key) as key:
            batch_file = os.path.join(self.fadcrypt_folder, 'FadCryptLock.bat')
            cmd = f'"{batch_file}" "%%1"'
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, cmd)
    
    def _register_file_unlock(self):
        """Register Unlock for files"""
        key_path = f"{self.REGISTRY_BASE}\\{self.FILE_UNLOCK_KEY}"
        
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Unlock with FadCrypt")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, f"{self.exe_path},0")
        
        # Use batch file wrapper to avoid "open with" dialog
        cmd_key = f"{key_path}\\command"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_key) as key:
            batch_file = os.path.join(self.fadcrypt_folder, 'FadCryptUnlock.bat')
            cmd = f'"{batch_file}" "%%1"'
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, cmd)
    
    def _register_folder_lock(self):
        """Register Lock for folders"""
        key_path = f"{self.REGISTRY_BASE}\\{self.FOLDER_LOCK_KEY}"
        
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Lock with FadCrypt")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, f"{self.exe_path},0")
        
        # Use batch file wrapper
        cmd_key = f"{key_path}\\command"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_key) as key:
            batch_file = os.path.join(self.fadcrypt_folder, 'FadCryptLock.bat')
            cmd = f'"{batch_file}" "%%1"'
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, cmd)
    
    def _register_folder_unlock(self):
        """Register Unlock for folders"""
        key_path = f"{self.REGISTRY_BASE}\\{self.FOLDER_UNLOCK_KEY}"
        
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Unlock with FadCrypt")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, f"{self.exe_path},0")
        
        # Use batch file wrapper
        cmd_key = f"{key_path}\\command"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_key) as key:
            batch_file = os.path.join(self.fadcrypt_folder, 'FadCryptUnlock.bat')
            cmd = f'"{batch_file}" "%%1"'
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, cmd)
    
    def unregister_context_menu(self) -> bool:
        """Remove context menu entries"""
        try:
            keys_to_remove = [
                f"{self.REGISTRY_BASE}\\{self.FILE_LOCK_KEY}",
                f"{self.REGISTRY_BASE}\\{self.FILE_UNLOCK_KEY}",
                f"{self.REGISTRY_BASE}\\{self.FOLDER_LOCK_KEY}",
                f"{self.REGISTRY_BASE}\\{self.FOLDER_UNLOCK_KEY}"
            ]
            
            for key_path in keys_to_remove:
                try:
                    self._delete_key(winreg.HKEY_CURRENT_USER, key_path)
                except:
                    pass
            
            logger.info("Context menu unregistered")
            return True
        except Exception as e:
            logger.error(f"Failed to unregister: {e}")
            return False
    
    def _delete_key(self, hive, path):
        """Recursively delete registry key"""
        try:
            parent, key = path.rsplit('\\', 1)
            with winreg.OpenKey(hive, parent, 0, winreg.KEY_WRITE) as key_obj:
                winreg.DeleteKey(key_obj, key)
        except:
            pass
