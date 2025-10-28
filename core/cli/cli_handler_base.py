"""
CLI Handler Base Class

Abstract base class for platform-specific lock/unlock operations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
import os


class CLIHandlerBase(ABC):
    """Abstract base class for CLI lock/unlock operations"""
    
    def __init__(self, config_folder: str):
        """
        Initialize CLI handler.
        
        Args:
            config_folder: Path to FadCrypt config folder
        """
        self.config_folder = config_folder
        self.config_file = os.path.join(config_folder, 'apps_config.json')
    
    @abstractmethod
    def lock_path(self, path: str) -> bool:
        """
        Lock a file or folder.
        
        Args:
            path: Absolute path to file or folder
        
        Returns:
            True if locked successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def unlock_path(self, path: str) -> bool:
        """
        Unlock a file or folder.
        
        Args:
            path: Absolute path to file or folder
        
        Returns:
            True if unlocked successfully, False otherwise
        """
        pass
    
    def lock_multiple(self, paths: List[str]) -> Tuple[int, int]:
        """
        Lock multiple paths.
        
        Args:
            paths: List of absolute paths
        
        Returns:
            Tuple of (success_count, failure_count)
        """
        success_count = 0
        failure_count = 0
        
        for path in paths:
            if self.lock_path(path):
                success_count += 1
            else:
                failure_count += 1
        
        return (success_count, failure_count)
    
    def unlock_multiple(self, paths: List[str]) -> Tuple[int, int]:
        """
        Unlock multiple paths.
        
        Args:
            paths: List of absolute paths
        
        Returns:
            Tuple of (success_count, failure_count)
        """
        success_count = 0
        failure_count = 0
        
        for path in paths:
            if self.unlock_path(path):
                success_count += 1
            else:
                failure_count += 1
        
        return (success_count, failure_count)
    
    @abstractmethod
    def list_locked_items(self) -> List[Dict]:
        """
        List all locked items.
        
        Returns:
            List of locked items with metadata
        """
        pass
    
    def validate_path(self, path: str) -> bool:
        """
        Validate that a path exists and is accessible.
        
        Args:
            path: Path to validate
        
        Returns:
            True if valid, False otherwise
        """
        if not os.path.exists(path):
            return False
        
        try:
            # Try to access the path
            os.stat(path)
            return True
        except (PermissionError, OSError):
            return False
