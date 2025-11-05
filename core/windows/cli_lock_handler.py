"""
Context Menu Lock Handler - Uses CLI handler with full encryption support

Handles --context-lock and --context-unlock from Windows context menu with password verification.
Uses PyQt6 password dialog for user authentication.
Uses CLI handler for FULL encryption/decryption logic (not just ACL).
"""

import sys
import os
import logging
from typing import Optional, Tuple

# Import color utilities
try:
    from core.cli.colors import Colors, print_error, print_success, print_colored
except ImportError:
    class Colors:
        BORDER = '\033[91m'
        HIGHLIGHT = '\033[92m'
        SECONDARY = '\033[34m'
        DIM = '\033[90m'
        INFO = '\033[94m'
        SUCCESS = '\033[92m'
        ERROR = '\033[91m'
        RESET = '\033[0m'
    
    def print_error(msg):
        print(f"{Colors.ERROR}{msg}{Colors.RESET}")
    
    def print_success(msg):
        print(f"{Colors.SUCCESS}{msg}{Colors.RESET}")
    
    def print_colored(msg, color):
        print(f"{color}{msg}{Colors.RESET}")

# Logging
def get_fadcrypt_logs_folder():
    appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    logs_dir = os.path.join(appdata, 'FadCrypt', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler(os.path.join(get_fadcrypt_logs_folder(), 'fadcrypt_cli_debug.log'), mode='a')
    ]
)
logger = logging.getLogger(__name__)


def get_fadcrypt_config_folder():
    appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    config_dir = os.path.join(appdata, 'FadCrypt', 'config')
    os.makedirs(config_dir, exist_ok=True)
    return config_dir


def get_password_manager():
    from core.crypto_manager import CryptoManager
    from core.password_manager import PasswordManager
    
    fadcrypt_folder = get_fadcrypt_config_folder()
    password_file = os.path.join(fadcrypt_folder, "encrypted_password.bin")
    recovery_codes_file = os.path.join(fadcrypt_folder, "recovery_codes.json")
    
    crypto_manager = CryptoManager()
    password_manager = PasswordManager(password_file, crypto_manager, recovery_codes_file)
    return password_manager


def show_result_dialog(success: bool, operation: str, filename: str, error_msg: str = None):
    """Show result dialog after lock/unlock operation"""
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        if success:
            if operation.upper() == "LOCK":
                title = "File Locked Successfully"
                message = f"✓ '{filename}' is now locked\n\nThe file has been encrypted and protected."
            else:
                title = "File Unlocked Successfully"
                message = f"✓ '{filename}' is now unlocked\n\nThe file has been decrypted and is accessible."
            QMessageBox.information(None, f"FadCrypt - {title}", message)
        else:
            if operation.upper() == "LOCK":
                title = "Lock Failed"
                message = f"✗ Failed to lock '{filename}'\n\n{error_msg or 'Check permissions and try again.'}"
            else:
                title = "Unlock Failed"
                message = f"✗ Failed to unlock '{filename}'\n\n{error_msg or 'Check permissions and try again.'}"
            QMessageBox.critical(None, f"FadCrypt - {title}", message)
        
    except Exception as e:
        logger.error(f"Error showing result dialog: {e}")


def show_output_dialog(output: str, operation: str):
    """Show operation output in a scrollable text dialog"""
    try:
        from PyQt6.QtWidgets import QApplication
        from ui.dialogs.operation_logs_dialog import OperationLogsDialog
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        dialog = OperationLogsDialog(
            title=f"FadCrypt - {operation} Operation Results",
            logs=output,
            parent=None
        )
        dialog.exec()
        
    except Exception as e:
        logger.error(f"Error showing output dialog: {e}")


def show_context_menu_password_dialog(operation: str) -> Tuple[Optional[str], 'ContextMenuPasswordDialog']:
    """Show context menu password dialog with logs display."""
    try:
        logger.info(f"Creating context menu password dialog for {operation}")
        from PyQt6.QtWidgets import QApplication
        from ui.dialogs.context_menu_password_dialog import ContextMenuPasswordDialog
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            logger.info("Created new QApplication")
        
        dialog = ContextMenuPasswordDialog(operation=operation, parent=None)
        
        # Show dialog modally - this will block until user closes it
        result = dialog.exec()
        
        # Return password and dialog for post-operation processing
        return dialog.password_value, dialog
        
    except Exception as e:
        logger.error(f"Dialog error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None, None


def show_password_dialog(operation: str) -> Optional[str]:
    """Show password dialog and return entered password"""
    try:
        logger.info(f"Creating password dialog for {operation}")
        from PyQt6.QtWidgets import QApplication
        from ui.dialogs.password_dialog import PasswordDialog
        
        def resource_path(relative_path):
            try:
                base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            logger.info("Created new QApplication")
        
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
        else:
            return None
        
    except Exception as e:
        logger.error(f"Dialog error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


def perform_lock_operation(file_path: str, password: str, pwd_dialog) -> bool:
    """Perform the actual lock operation with password and dialog for logs."""
    try:
        # Convert to absolute path to match how CLI stores paths
        abs_file_path = os.path.abspath(file_path)
        
        # Verify password
        password_manager = get_password_manager()
        if not password_manager.verify_password(password):
            logger.error("Incorrect password")
            if pwd_dialog:
                pwd_dialog.update_logs("❌ Incorrect password!")
            return False
        
        # Update logs in dialog
        if pwd_dialog:
            pwd_dialog.update_logs(f"✓ Password verified")
            pwd_dialog.update_logs(f"🔒 Locking: {os.path.basename(abs_file_path)}...")
        
        # Save original print before redirecting
        original_print = print
        
        # Define print redirect with event processing - ONLY send to dialog, not terminal
        from PyQt6.QtWidgets import QApplication
        
        def print_with_logs_and_events(*args, **kwargs):
            msg = ' '.join(str(a) for a in args)
            if pwd_dialog:
                pwd_dialog.update_logs(msg)
                # Process GUI events so logs appear in real-time
                QApplication.processEvents()
            # Do NOT print to terminal during operation - show ONLY in dialog
        
        # Redirect print BEFORE importing file_lock_manager
        import builtins
        import sys
        import io
        
        # Save original stdout/stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        # Create dummy streams to suppress non-dialog output
        dummy_stream = io.StringIO()
        builtins.print = print_with_logs_and_events
        
        try:
            # Suppress stdout/stderr during operation - all output should go to dialog
            sys.stdout = dummy_stream
            sys.stderr = dummy_stream
            
            # Use CLI handler with full encryption support
            logger.info("Using file lock manager with encryption support")
            from core.windows.file_lock_manager_windows import FileLockManagerWindows
            
            config_folder = os.path.dirname(password_manager.password_file)
            file_lock_mgr = FileLockManagerWindows(config_folder)
            
            # Set password bytes for encryption
            file_lock_mgr.password_bytes = password_manager.get_password_bytes()
            
            # Lock the item directly
            item_type = "folder" if os.path.isdir(abs_file_path) else "file"
            success = file_lock_mgr.add_item(abs_file_path, item_type)
            
            if success:
                if pwd_dialog:
                    pwd_dialog.update_logs("✓ Lock operation completed successfully!")
            else:
                if pwd_dialog:
                    pwd_dialog.update_logs("✗ Lock operation failed!")
            
            return success
        finally:
            # Restore stdout/stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            builtins.print = original_print
            # Process events to show final logs in dialog
            if pwd_dialog:
                for _ in range(10):  # Process multiple times to ensure all updates show
                    QApplication.processEvents()
    except Exception as e:
        logger.error(f"Lock operation error: {e}")
        if pwd_dialog:
            pwd_dialog.update_logs(f"❌ Error: {str(e)}")
        return False


def lock_file_with_password(file_path: str) -> Tuple[bool, dict]:
    """
    Lock file with integrated password dialog and logs display.
    
    Returns:
        Tuple[bool, dict]: (success: bool, info: dict)
    """
    try:
        logger.info(f"Starting lock operation for: {file_path}")
        
        password_manager = get_password_manager()
        password_file = password_manager.password_file
        
        if not os.path.exists(password_file):
            logger.error("No master password set up.")
            from PyQt6.QtWidgets import QApplication, QMessageBox
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            QMessageBox.critical(
                None,
                "FadCrypt - Password Required",
                "No master password has been set up.\n\nPlease open FadCrypt and create a password first."
            )
            return False, {'path': file_path, 'name': os.path.basename(file_path), 'error': 'No password'}
        
        # Define the operation callback
        def perform_operation(password, dialog):
            return perform_lock_operation(file_path, password, dialog)
        
        # Show context menu password dialog with callback
        from PyQt6.QtWidgets import QApplication
        from ui.dialogs.context_menu_password_dialog import ContextMenuPasswordDialog
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        dialog = ContextMenuPasswordDialog(operation="LOCK", parent=None, operation_callback=perform_operation)
        
        # Show dialog modally - operation executes inside dialog
        result = dialog.exec()
        
        # Get success from dialog's operation result
        password = dialog.password_value
        if not password:
            logger.warning("Lock cancelled by user")
            return False, {'path': file_path, 'name': os.path.basename(file_path), 'error': 'Cancelled'}
        
        # Return result (operation already completed inside dialog)
        # We need to track success - let's add it to dialog
        success = dialog.operation_complete
        
        if success:
            return True, {'path': file_path, 'name': os.path.basename(file_path), 'error': None}
        else:
            return False, {'path': file_path, 'name': os.path.basename(file_path), 'error': 'Operation failed'}
    
    except Exception as e:
        logger.error(f"Lock error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False, {'path': file_path, 'name': os.path.basename(file_path), 'error': str(e)}


def perform_unlock_operation(file_path: str, password: str, pwd_dialog) -> bool:
    """Perform the actual unlock operation with password and dialog for logs."""
    try:
        # Convert to absolute path to match stored paths
        abs_file_path = os.path.abspath(file_path)
        
        # Verify password
        password_manager = get_password_manager()
        if not password_manager.verify_password(password):
            logger.error("Incorrect password")
            if pwd_dialog:
                pwd_dialog.update_logs("❌ Incorrect password!")
            return False
        
        # Update logs in dialog
        if pwd_dialog:
            pwd_dialog.update_logs(f"✓ Password verified")
            pwd_dialog.update_logs(f"🔓 Unlocking: {os.path.basename(abs_file_path)}...")
        
        # Save original print before redirecting
        original_print = print
        
        # Define print redirect with event processing - send to dialog, not terminal
        from PyQt6.QtWidgets import QApplication
        
        def print_with_logs_and_events(*args, **kwargs):
            msg = ' '.join(str(a) for a in args)
            if pwd_dialog:
                pwd_dialog.update_logs(msg)
                # Process GUI events so logs appear in real-time
                QApplication.processEvents()
            # Do NOT print to terminal during operation - show ONLY in dialog
        
        # Redirect print BEFORE importing file_lock_manager
        import builtins
        import sys
        import io
        
        # Save original stdout/stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        # Create dummy streams to suppress non-dialog output
        dummy_stream = io.StringIO()
        builtins.print = print_with_logs_and_events
        
        try:
            # Suppress stdout/stderr during operation - all output should go to dialog
            sys.stdout = dummy_stream
            sys.stderr = dummy_stream
            
            # Use the full file lock manager flow (matches CLI behavior)
            logger.info("Using full file lock manager with decryption support")
            from core.windows.file_lock_manager_windows import FileLockManagerWindows
            
            config_folder = os.path.dirname(password_manager.password_file)
            file_lock_mgr = FileLockManagerWindows(config_folder)
            
            # Set password bytes for decryption (this was cached when password was verified)
            file_lock_mgr.password_bytes = password_manager.get_password_bytes()
            
            # Unlock the item using the full remove_item() flow (handles decryption, ACL removal, config persistence)
            # Pass absolute path to match how items are stored
            success = file_lock_mgr.remove_item(abs_file_path)
            
            if success:
                if pwd_dialog:
                    pwd_dialog.update_logs("✓ Unlock operation completed successfully!")
            else:
                if pwd_dialog:
                    pwd_dialog.update_logs("✗ Unlock operation failed!")
                logger.error(f"[perform_unlock] remove_item returned False for {abs_file_path}")
            
            return success
        finally:
            # Restore stdout/stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            builtins.print = original_print
            # Process events to show final logs in dialog
            if pwd_dialog:
                for _ in range(10):  # Process multiple times to ensure all updates show
                    QApplication.processEvents()
    except Exception as e:
        logger.error(f"Unlock operation error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        if pwd_dialog:
            pwd_dialog.update_logs(f"❌ Error: {str(e)}")
        return False


def unlock_file_with_password(file_path: str) -> Tuple[bool, dict]:
    """
    Unlock file with integrated password dialog and logs display.
    
    Returns:
        Tuple[bool, dict]: (success: bool, info: dict)
    """
    try:
        logger.info(f"Starting unlock operation for: {file_path}")
        
        password_manager = get_password_manager()
        password_file = password_manager.password_file
        
        if not os.path.exists(password_file):
            logger.error("No master password set up.")
            from PyQt6.QtWidgets import QApplication, QMessageBox
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            QMessageBox.critical(
                None,
                "FadCrypt - Password Required",
                "No master password has been set up.\n\nPlease open FadCrypt and create a password first."
            )
            return False, {'path': file_path, 'name': os.path.basename(file_path), 'error': 'No password'}
        
        # Define the operation callback
        def perform_operation(password, dialog):
            return perform_unlock_operation(file_path, password, dialog)
        
        # Show context menu password dialog with callback
        from PyQt6.QtWidgets import QApplication
        from ui.dialogs.context_menu_password_dialog import ContextMenuPasswordDialog
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        dialog = ContextMenuPasswordDialog(operation="UNLOCK", parent=None, operation_callback=perform_operation)
        
        # Show dialog modally - operation executes inside dialog
        result = dialog.exec()
        
        # Get success from dialog's operation result
        password = dialog.password_value
        if not password:
            logger.warning("Unlock cancelled by user")
            return False, {'path': file_path, 'name': os.path.basename(file_path), 'error': 'Cancelled'}
        
        # Return result (operation already completed inside dialog)
        success = dialog.operation_complete
        
        if success:
            return True, {'path': file_path, 'name': os.path.basename(file_path), 'error': None}
        else:
            return False, {'path': file_path, 'name': os.path.basename(file_path), 'error': 'Operation failed'}
    
    except Exception as e:
        logger.error(f"Unlock error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False, {'path': file_path, 'name': os.path.basename(file_path), 'error': str(e)}


def lock_multiple_with_password(paths: list) -> tuple:
    """
    Lock multiple files with a single password dialog.
    Shows progress as each file is processed.
    
    Args:
        paths: List of file paths to lock
        
    Returns:
        Tuple of (success: bool, info: dict) where info contains:
            - 'success': number of successfully locked files
            - 'failed': number of failed files
            - 'paths': list of successfully locked file paths
            - 'errors': dict mapping failed paths to error messages
    """
    try:
        from ui.dialogs.context_menu_password_dialog import ContextMenuPasswordDialog
        from PyQt6.QtWidgets import QApplication
        import sys
        
        logger.info(f"[BATCH LOCK] Processing {len(paths)} file(s)")
        
        # Ensure QApplication exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Initialize result tracking
        successful_paths = []
        failed_paths = {}
        
        # Create dialog for batch lock operation
        pwd_dialog = ContextMenuPasswordDialog(operation="LOCK")
        
        # Define batch operation callback
        def batch_operation(password, dialog):
            """Process all files with progress updates"""
            nonlocal successful_paths, failed_paths
            
            dialog.update_logs(f"<span style='color:#00bfff;'>🔄 Processing {len(paths)} file(s)...</span>")
            
            for idx, file_path in enumerate(paths, 1):
                filename = os.path.basename(file_path)
                dialog.update_logs(f"<span style='color:#00bfff;'>📁 [{idx}/{len(paths)}] Processing: {filename}</span>")
                
                # Perform lock operation for this file
                success = perform_lock_operation(file_path, password, dialog)
                
                if success:
                    successful_paths.append(file_path)
                else:
                    failed_paths[file_path] = "Operation failed"
            
            # Show summary
            if successful_paths:
                dialog.update_logs(f"<span style='color:#00ff00;'>✓ Successfully locked {len(successful_paths)} of {len(paths)} file(s)</span>")
            if failed_paths:
                dialog.update_logs(f"<span style='color:#ff4444;'>✗ Failed to lock {len(failed_paths)} of {len(paths)} file(s)</span>")
            
            return len(successful_paths) > 0
        
        # Set operation callback in constructor - pass as operation_callback parameter
        pwd_dialog.operation_callback = batch_operation
        
        # Show dialog and wait for user
        logger.info("[BATCH LOCK] Showing password dialog...")
        result = pwd_dialog.exec()
        
        if result == pwd_dialog.DialogCode.Rejected:
            logger.warning("[BATCH LOCK] Cancelled by user")
            return False, {
                'success': 0,
                'failed': len(paths),
                'paths': [],
                'errors': {path: 'Cancelled' for path in paths}
            }
        
        # Return results
        overall_success = len(successful_paths) > 0
        return overall_success, {
            'success': len(successful_paths),
            'failed': len(failed_paths),
            'paths': successful_paths,
            'errors': failed_paths
        }
    
    except Exception as e:
        logger.error(f"[BATCH LOCK] Error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False, {
            'success': 0,
            'failed': len(paths),
            'paths': [],
            'errors': {path: str(e) for path in paths}
        }


def unlock_multiple_with_password(paths: list) -> tuple:
    """
    Unlock multiple files with a single password dialog.
    Shows progress as each file is processed.
    
    Args:
        paths: List of file paths to unlock
        
    Returns:
        Tuple of (success: bool, info: dict) where info contains:
            - 'success': number of successfully unlocked files
            - 'failed': number of failed files
            - 'paths': list of successfully unlocked file paths
            - 'errors': dict mapping failed paths to error messages
    """
    try:
        from ui.dialogs.context_menu_password_dialog import ContextMenuPasswordDialog
        from PyQt6.QtWidgets import QApplication
        import sys
        
        logger.info(f"[BATCH UNLOCK] Processing {len(paths)} file(s)")
        
        # Ensure QApplication exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Initialize result tracking
        successful_paths = []
        failed_paths = {}
        
        # Create dialog for batch unlock operation
        pwd_dialog = ContextMenuPasswordDialog(operation="UNLOCK")
        
        # Define batch operation callback
        def batch_operation(password, dialog):
            """Process all files with progress updates"""
            nonlocal successful_paths, failed_paths
            
            dialog.update_logs(f"<span style='color:#00bfff;'>🔄 Processing {len(paths)} file(s)...</span>")
            
            for idx, file_path in enumerate(paths, 1):
                filename = os.path.basename(file_path)
                dialog.update_logs(f"<span style='color:#00bfff;'>📁 [{idx}/{len(paths)}] Processing: {filename}</span>")
                
                # Perform unlock operation for this file
                success = perform_unlock_operation(file_path, password, dialog)
                
                if success:
                    successful_paths.append(file_path)
                else:
                    failed_paths[file_path] = "Operation failed"
            
            # Show summary
            if successful_paths:
                dialog.update_logs(f"<span style='color:#00ff00;'>✓ Successfully unlocked {len(successful_paths)} of {len(paths)} file(s)</span>")
            if failed_paths:
                dialog.update_logs(f"<span style='color:#ff4444;'>✗ Failed to unlock {len(failed_paths)} of {len(paths)} file(s)</span>")
            
            return len(successful_paths) > 0
        
        # Set operation callback in constructor
        pwd_dialog.operation_callback = batch_operation
        
        # Show dialog and wait for user
        logger.info("[BATCH UNLOCK] Showing password dialog...")
        result = pwd_dialog.exec()
        
        if result == pwd_dialog.DialogCode.Rejected:
            logger.warning("[BATCH UNLOCK] Cancelled by user")
            return False, {
                'success': 0,
                'failed': len(paths),
                'paths': [],
                'errors': {path: 'Cancelled' for path in paths}
            }
        
        # Return results
        overall_success = len(successful_paths) > 0
        return overall_success, {
            'success': len(successful_paths),
            'failed': len(failed_paths),
            'paths': successful_paths,
            'errors': failed_paths
        }
    
    except Exception as e:
        logger.error(f"[BATCH UNLOCK] Error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False, {
            'success': 0,
            'failed': len(paths),
            'paths': [],
            'errors': {path: str(e) for path in paths}
        }
