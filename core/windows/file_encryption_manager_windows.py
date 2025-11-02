"""
Windows File Encryption Manager

Windows-specific implementation of file/folder encryption.
"""

import os
import tempfile
from typing import Tuple
from core.file_encryption_manager import FileEncryptionManager
from core.crypto_manager import CryptoManager


class FileEncryptionManagerWindows(FileEncryptionManager):
    """Windows implementation of file/folder encryption"""
    
    def __init__(self, config_folder: str, crypto_manager: CryptoManager = None):
        super().__init__(config_folder, crypto_manager)
    
    def _get_temp_dir(self) -> str:
        """
        Get Windows temporary directory.
        
        Returns:
            Path to Windows temp directory
        """
        return tempfile.gettempdir()
