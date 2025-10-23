"""
CLI Lock Handler - Password-Protected File Locking via Context Menu

Handles --lock and --unlock from context menu with password verification.
Uses PyQt6 password dialog for user authentication.
Uses existing PasswordManager and CryptoManager for consistency with GUI.
"""

import sys
import os
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def get_password_manager():
    """Get the same PasswordManager used by the GUI"""
    from core.crypto_manager import CryptoManager
    from core.password_manager import PasswordManager
    
    # Get FadCrypt folder (Windows specific)
    appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    fadcrypt_folder = os.path.join(appdata, 'FadCrypt')
    os.makedirs(fadcrypt_folder, exist_ok=True)
    
    # Use exact same initialization as GUI
    password_file = os.path.join(fadcrypt_folder, "encrypted_password.bin")
    recovery_codes_file = os.path.join(fadcrypt_folder, "recovery_codes.json")
    
    crypto_manager = CryptoManager()
    password_manager = PasswordManager(password_file, crypto_manager, recovery_codes_file)
    
    return password_manager


def show_password_dialog(operation: str) -> Optional[str]:
    """Show password dialog and return entered password"""
    try:
        from PyQt6.QtWidgets import QApplication
        from ui.dialogs.password_dialog import PasswordDialog
        
        # Use the same resource_path logic as FadCrypt.py
        def resource_path(relative_path):
            """Get absolute path to resource, works for dev and for PyInstaller"""
            try:
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)
        
        # Create Qt application if needed
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        dialog = PasswordDialog(
            title="FadCrypt",
            prompt=f"Enter your password to {operation.lower()} this file",
            resource_path=resource_path,
            fullscreen=False,
            parent=None,
            show_forgot_password=False
        )
        
        result = dialog.exec()
        if result == 1:  # QDialog.Accepted
            return dialog.password_value
        
        return None
    
    except Exception as e:
        logger.error(f"Dialog error: {e}")
        return None


def lock_file_with_password(file_path: str) -> bool:
    """Lock file after password verification using existing PasswordManager"""
    try:
        # Show password dialog
        password = show_password_dialog("LOCK")
        if not password:
            logger.warning("Lock cancelled by user")
            return False
        
        # Use same password verification as GUI
        password_manager = get_password_manager()
        if not password_manager.verify_password(password):
            logger.error("Incorrect password")
            return False
        
        # Lock the file using ACL
        from core.windows.acl_locker import ACLFileLocker
        locker = ACLFileLocker()
        
        if locker.lock_path(file_path):
            logger.info(f"File locked: {file_path}")
            return True
        else:
            logger.error(f"Failed to lock file")
            return False
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def unlock_file_with_password(file_path: str) -> bool:
    """Unlock file after password verification using existing PasswordManager"""
    try:
        # Show password dialog
        password = show_password_dialog("UNLOCK")
        if not password:
            logger.warning("Unlock cancelled by user")
            return False
        
        # Use same password verification as GUI
        password_manager = get_password_manager()
        if not password_manager.verify_password(password):
            logger.error("Incorrect password")
            return False
        
        # Unlock the file using ACL
        from core.windows.acl_locker import ACLFileLocker
        locker = ACLFileLocker()
        
        if locker.unlock_path(file_path):
            logger.info(f"File unlocked: {file_path}")
            return True
        else:
            logger.error(f"Failed to unlock file")
            return False
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return False
