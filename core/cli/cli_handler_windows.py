"""
Windows CLI Handler

Windows-specific implementation of CLI lock/unlock operations.
"""

import os
import json
import time
from typing import List, Dict

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
        except Exception as e:
            print(f"Error initializing file lock manager: {e}")
    
    def lock_path(self, path: str) -> bool:
        """Lock a file or folder using Windows ACL"""
        if not self.file_lock_manager:
            return False
        
        if not self.validate_path(path):
            return False
        
        # Determine type
        item_type = "folder" if os.path.isdir(path) else "file"
        
        # Add to locked items
        return self.file_lock_manager.add_item(path, item_type)
    
    def unlock_path(self, path: str) -> bool:
        """Unlock a file or folder"""
        if not self.file_lock_manager:
            return False
        
        # Remove from locked items
        return self.file_lock_manager.remove_item(path)
    
    def list_locked_items(self) -> List[Dict]:
        """List all locked items"""
        if not self.file_lock_manager:
            return []
        
        # Reload from disk to get fresh data
        self.file_lock_manager._load_locked_items()
        return self.file_lock_manager.get_locked_items()
