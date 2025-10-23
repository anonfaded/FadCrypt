"""
ACL-Based File Locking for Windows

Uses Windows NTFS ACL (Access Control Lists) to lock files/folders.
When locked: Set DENY rule for Everyone
When unlocked: Remove DENY rule
No monitoring needed - Windows kernel enforces permissions.
"""

import os
import subprocess
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ACLFileLocker:
    """Lock/unlock files using Windows ACL (ICACLS)"""
    
    def lock_path(self, path: str) -> bool:
        """Lock file/folder by denying Everyone access"""
        try:
            if not os.path.exists(path):
                logger.error(f"Path does not exist: {path}")
                return False
            
            # Deny Everyone all permissions
            result = subprocess.run(
                ['icacls', path, '/deny', 'Everyone:(F)'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"Locked: {path}")
                return True
            else:
                logger.error(f"Failed to lock {path}: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error locking {path}: {e}")
            return False
    
    def unlock_path(self, path: str) -> bool:
        """Unlock file/folder by removing DENY rule"""
        try:
            if not os.path.exists(path):
                logger.error(f"Path does not exist: {path}")
                return False
            
            # Remove deny rule for Everyone
            result = subprocess.run(
                ['icacls', path, '/remove:d', 'Everyone'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"Unlocked: {path}")
                return True
            else:
                logger.error(f"Failed to unlock {path}: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error unlocking {path}: {e}")
            return False
    
    def is_locked(self, path: str) -> bool:
        """Check if path has DENY rule for Everyone"""
        try:
            result = subprocess.run(
                ['icacls', path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Check if output contains DENY for Everyone
            # icacls shows DENY as (N) format, e.g. "Everyone:(N)"
            return 'Everyone:(N)' in result.stdout
        except:
            return False
    
    def lock_recursive(self, path: str) -> bool:
        """Lock path and all subfolders/files"""
        try:
            # Use /grant:r to recursively apply to folder and contents
            result = subprocess.run(
                ['icacls', path, '/deny', 'Everyone:(F)', '/T'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"Recursively locked: {path}")
                return True
            else:
                logger.error(f"Failed to recursively lock {path}: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error in recursive lock: {e}")
            return False
    
    def unlock_recursive(self, path: str) -> bool:
        """Unlock path and all subfolders/files"""
        try:
            result = subprocess.run(
                ['icacls', path, '/remove:d', 'Everyone', '/T'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"Recursively unlocked: {path}")
                return True
            else:
                logger.error(f"Failed to recursively unlock {path}: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error in recursive unlock: {e}")
            return False
