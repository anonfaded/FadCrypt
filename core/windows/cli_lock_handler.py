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

# Set up logging to both console and file
def get_fadcrypt_logs_folder():
    """Get the unified FadCrypt logs folder for Windows."""
    import os
    appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    logs_dir = os.path.join(appdata, 'FadCrypt', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),  # Console output
        logging.FileHandler(os.path.join(get_fadcrypt_logs_folder(), 'fadcrypt_cli_debug.log'), mode='a')  # File output
    ]
)
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
        logger.info(f"Creating password dialog for {operation}")
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
        
        logger.info("Creating QApplication instance")
        # Create Qt application if needed
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            logger.info("Created new QApplication")
        else:
            logger.info("Using existing QApplication")
        
        logger.info("Creating PasswordDialog")
        dialog = PasswordDialog(
            title="FadCrypt",
            prompt=f"Enter your password to {operation.lower()} this file",
            resource_path=resource_path,
            fullscreen=False,
            parent=None,
            show_forgot_password=False
        )
        
        logger.info("Showing password dialog")
        result = dialog.exec()
        logger.info(f"Dialog result: {result}")
        
        if result == 1:  # QDialog.Accepted
            logger.info("Password accepted")
            return dialog.password_value
        else:
            logger.info("Password dialog cancelled")
            return None
        
    except Exception as e:
        logger.error(f"Dialog error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


def lock_file_with_password(file_path: str) -> bool:
    """Lock file after password verification using existing PasswordManager"""
    try:
        logger.info(f"Starting lock operation for: {file_path}")
        
        # Check if password exists first
        password_manager = get_password_manager()
        password_file = password_manager.password_file
        
        if not os.path.exists(password_file):
            logger.error("No master password set up. Please open FadCrypt GUI and create a password first.")
            # Show error dialog
            from PyQt6.QtWidgets import QApplication, QMessageBox
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            QMessageBox.critical(
                None,
                "FadCrypt - Password Required",
                "No master password has been set up.\n\nPlease open the FadCrypt application and create a password first before using context menu locking."
            )
            return False
        
        # Show password dialog
        password = show_password_dialog("LOCK")
        if not password:
            logger.warning("Lock cancelled by user")
            return False
        
        logger.info("Password entered, verifying...")
        # Use same password verification as GUI
        if not password_manager.verify_password(password):
            logger.error("Incorrect password")
            return False
        
        logger.info("Password verified, locking file...")
        # Lock the file using ACL
        from core.windows.acl_locker import ACLFileLocker
        locker = ACLFileLocker()
        
        if locker.lock_path(file_path):
            logger.info(f"File locked: {file_path}")
            return True
        else:
            logger.error(f"Failed to lock file: {file_path}")
            return False
    
    except Exception as e:
        logger.error(f"Lock error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def unlock_file_with_password(file_path: str) -> bool:
    """Unlock file after password verification using existing PasswordManager"""
    try:
        # Check if password exists first
        password_manager = get_password_manager()
        password_file = password_manager.password_file
        
        if not os.path.exists(password_file):
            logger.error("No master password set up. Please open FadCrypt GUI and create a password first.")
            # Show error dialog
            from PyQt6.QtWidgets import QApplication, QMessageBox
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            QMessageBox.critical(
                None,
                "FadCrypt - Password Required",
                "No master password has been set up.\n\nPlease open the FadCrypt application and create a password first before using context menu unlocking."
            )
            return False
        
        # Show password dialog
        password = show_password_dialog("UNLOCK")
        if not password:
            logger.warning("Unlock cancelled by user")
            return False
        
        # Use same password verification as GUI
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
