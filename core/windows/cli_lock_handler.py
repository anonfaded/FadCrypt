"""
Context Menu Lock Handler - Password-Protected File Locking via Context Menu

Handles --context-lock and --context-unlock from Windows context menu with password verification.
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


def get_fadcrypt_config_folder():
    """Get FadCrypt configuration folder path (matches main_window_windows.py)"""
    appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    config_dir = os.path.join(appdata, 'FadCrypt', 'config')
    os.makedirs(config_dir, exist_ok=True)
    return config_dir


def get_password_manager():
    """Get the same PasswordManager used by the GUI"""
    from core.crypto_manager import CryptoManager
    from core.password_manager import PasswordManager
    
    # Use same folder structure as GUI
    fadcrypt_folder = get_fadcrypt_config_folder()
    
    # Use exact same initialization as GUI
    password_file = os.path.join(fadcrypt_folder, "encrypted_password.bin")
    recovery_codes_file = os.path.join(fadcrypt_folder, "recovery_codes.json")
    
    crypto_manager = CryptoManager()
    password_manager = PasswordManager(password_file, crypto_manager, recovery_codes_file)
    
    return password_manager


def add_to_locked_items(file_path: str) -> bool:
    """
    Add file/folder to locked items list in apps_config.json.
    This makes it appear in the Files & Folders tab.
    
    Args:
        file_path: Absolute path to file or folder
    
    Returns:
        True if added successfully, False otherwise
    """
    try:
        import json
        import time
        
        config_folder = get_fadcrypt_config_folder()
        config_file = os.path.join(config_folder, 'apps_config.json')
        
        # Determine if it's a file or folder
        if os.path.isfile(file_path):
            item_type = "file"
        elif os.path.isdir(file_path):
            item_type = "folder"
        else:
            logger.error(f"Path does not exist or is not a file/folder: {file_path}")
            return False
        
        # Load existing config
        config = {"applications": [], "locked_files_and_folders": []}
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        # Check if already in list
        locked_items = config.get("locked_files_and_folders", [])
        if any(item['path'] == file_path for item in locked_items):
            logger.info(f"Item already in locked list: {file_path}")
            return False
        
        # Create metadata for the item
        item_metadata = {
            "name": os.path.basename(file_path) or file_path,
            "path": os.path.abspath(file_path),
            "type": item_type,
            "original_permissions": "default",
            "filesystem": "ntfs",
            "lock_method": "icacls",
            "locked_at": int(time.time()),
            "unlock_count": 0
        }
        
        # Add to locked items
        locked_items.append(item_metadata)
        config["locked_files_and_folders"] = locked_items
        
        # Save config using safe write (handles protected files)
        try:
            from core.file_protection import safe_write_to_protected_file
            content = json.dumps(config, indent=4)
            success, error = safe_write_to_protected_file(config_file, content)
            
            if success:
                logger.info(f"Added to locked items: {os.path.basename(file_path)}")
                return True
            else:
                logger.error(f"Failed to save config: {error}")
                return False
        except Exception as e:
            logger.error(f"Error using safe write: {e}")
            # Fallback to direct write
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
            logger.info(f"Added to locked items (direct write): {os.path.basename(file_path)}")
            return True
        
    except Exception as e:
        logger.error(f"Error adding to locked items: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def remove_from_locked_items(file_path: str) -> bool:
    """
    Remove file/folder from locked items list in apps_config.json.
    This makes it disappear from the Files & Folders tab.
    
    Args:
        file_path: Absolute path to file or folder
    
    Returns:
        True if removed successfully, False otherwise
    """
    try:
        import json
        
        config_folder = get_fadcrypt_config_folder()
        config_file = os.path.join(config_folder, 'apps_config.json')
        
        # Load existing config
        if not os.path.exists(config_file):
            logger.warning("Config file does not exist")
            return False
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return False
        
        # Remove from locked items
        locked_items = config.get("locked_files_and_folders", [])
        original_count = len(locked_items)
        
        # Filter out the item with matching path
        locked_items = [item for item in locked_items if item['path'] != file_path]
        
        if len(locked_items) == original_count:
            logger.warning(f"Item not found in locked list: {file_path}")
            return False
        
        config["locked_files_and_folders"] = locked_items
        
        # Save config using safe write (handles protected files)
        try:
            from core.file_protection import safe_write_to_protected_file
            content = json.dumps(config, indent=4)
            success, error = safe_write_to_protected_file(config_file, content)
            
            if success:
                logger.info(f"Removed from locked items: {os.path.basename(file_path)}")
                return True
            else:
                logger.error(f"Failed to save config: {error}")
                return False
        except Exception as e:
            logger.error(f"Error using safe write: {e}")
            # Fallback to direct write
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
            logger.info(f"Removed from locked items (direct write): {os.path.basename(file_path)}")
            return True
        
    except Exception as e:
        logger.error(f"Error removing from locked items: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


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
            
            # Add to locked items list so it appears in Files & Folders tab
            logger.info("Adding to locked items list...")
            if add_to_locked_items(file_path):
                logger.info("Successfully added to locked items list")
            else:
                logger.warning("Could not add to locked items list (may already exist)")
            
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
            
            # Remove from locked items list so it disappears from Files & Folders tab
            logger.info("Removing from locked items list...")
            if remove_from_locked_items(file_path):
                logger.info("Successfully removed from locked items list")
            else:
                logger.warning("Could not remove from locked items list (may not exist)")
            
            return True
        else:
            logger.error(f"Failed to unlock file")
            return False
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return False
