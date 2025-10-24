"""
FadCrypt Core Module
This module contains shared functionality used by both Windows and Linux versions.
"""

from .config_manager import ConfigManager
from .unified_monitor import UnifiedMonitor
from .crypto_manager import CryptoManager
from .password_manager import PasswordManager
from .file_lock_manager import FileLockManager
from .autostart_manager import (
    AutostartManagerBase,
    AutostartManagerLinux,
    AutostartManagerWindows,
    get_autostart_manager
)

__all__ = [
    'ConfigManager',
    'UnifiedMonitor',
    'CryptoManager',
    'PasswordManager',
    'FileLockManager',
    'AutostartManagerBase',
    'AutostartManagerLinux',
    'AutostartManagerWindows',
    'get_autostart_manager',
]
