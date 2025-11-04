"""
Windows CLI Handler

Windows-specific implementation of CLI lock/unlock operations.
"""

import os
import json
import time
from typing import List, Dict, Tuple

from .cli_handler_base import CLIHandlerBase


class CLIHandlerWindows(CLIHandlerBase):
    """Windows implementation of CLI handler"""
    
    def __init__(self, config_folder: str):
        """Initialize Windows CLI handler"""
        super().__init__(config_folder)
        self.file_lock_manager = None
        self._init_file_lock_manager()
    
    def _init_file_lock_manager(self):
        """Initialize the file lock manager"""
        try:
            from core.windows.file_lock_manager_windows import FileLockManagerWindows
            self.file_lock_manager = FileLockManagerWindows(self.config_folder)
            # Verify initialization succeeded
            if self.file_lock_manager is None:
                print("Warning: FileLockManagerWindows initialization returned None")
        except ImportError as e:
            print(f"Import error initializing file lock manager: {e}")
            self.file_lock_manager = None
        except Exception as e:
            print(f"Error initializing file lock manager: {e}")
            self.file_lock_manager = None
    
    def lock_path(self, path: str) -> Tuple[bool, str]:
        """Lock a file or folder using Windows ACL"""
        if not self.file_lock_manager:
            return False, "File lock manager not initialized"
        
        if not self.validate_path(path):
            return False, "Invalid path"
        
        # Convert to absolute path for consistency
        abs_path = os.path.abspath(path)
        
        # Determine type
        item_type = "folder" if os.path.isdir(abs_path) else "file"
        
        # Add to locked items
        if self.file_lock_manager.add_item(abs_path, item_type):
            return True, ""
        else:
            return False, "Failed to lock item"
    
    def unlock_path(self, path: str) -> Tuple[bool, str]:
        """Unlock a file or folder"""
        if not self.file_lock_manager:
            return False, "File lock manager not initialized"
        
        # Path existence and lock status already validated in unlock_multiple, no need to check again
        
        # Convert to absolute path to match stored paths
        abs_path = os.path.abspath(path)
        
        # Remove from locked items
        if self.file_lock_manager.remove_item(abs_path):
            return True, ""
        else:
            return False, f"Failed to unlock (permission or system error): {os.path.basename(path)}"
    
    def list_locked_items(self) -> List[Dict]:
        """List all locked items"""
        if not self.file_lock_manager:
            return []
        
        # Reload from disk to get fresh data
        self.file_lock_manager._load_locked_items()
        return self.file_lock_manager.get_locked_items()
    
    def toggle_tamper_proof(self, path: str, enable: bool) -> bool:
        """Toggle tamper-proof protections on Windows via ACL"""
        if not self.file_lock_manager:
            return False
        
        if not self.validate_path(path):
            return False
        
        abs_path = os.path.abspath(path)
        
        try:
            # Use the file lock manager to toggle protections
            # For now, return stub - full implementation to follow
            return self.file_lock_manager.toggle_tamper_proof(abs_path, enable)
        except Exception as e:
            print(f"Error toggling tamper-proof: {e}")
            return False
