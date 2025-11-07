"""
Linux File Encryption Manager

Linux-specific implementation of file/folder encryption.
"""

import os
import tempfile
from typing import Tuple
from core.file_encryption_manager import FileEncryptionManager
from core.crypto_manager import CryptoManager


class FileEncryptionManagerLinux(FileEncryptionManager):
    """Linux implementation of file/folder encryption"""
    
    def __init__(self, config_folder: str, crypto_manager: CryptoManager = None):
        super().__init__(config_folder, crypto_manager)
    
    def _get_temp_dir(self) -> str:
        """
        Get Linux temporary directory.
        
        Returns:
            Path to Linux temp directory (usually /tmp)
        """
        return tempfile.gettempdir()
