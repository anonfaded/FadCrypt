"""
Config Manager - Handles import/export of configuration files
This is shared between Windows and Linux versions
"""


class ConfigManager:
    """
    Manages configuration import/export operations.
    This class provides unified functionality for both Windows and Linux versions.
    """
    
    def __init__(self, app_locker, get_fadcrypt_folder_func):
        """
        Initialize the ConfigManager
        
        Args:
            app_locker: The AppLocker instance that contains the config
            get_fadcrypt_folder_func: Function that returns the FadCrypt folder path
        """
        self.app_locker = app_locker
        self.get_fadcrypt_folder = get_fadcrypt_folder_func
