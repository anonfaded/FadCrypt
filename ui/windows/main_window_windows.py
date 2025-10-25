"""Windows-specific Main Window for FadCrypt PyQt6 UI"""

import os
import sys
import subprocess
import ctypes
from PyQt6.QtWidgets import QMessageBox

try:
    import winreg
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

from ui.base.main_window_base import MainWindowBase
from core.windows.elevation_manager import get_elevation_manager
from core.windows.elevated_service_client import get_elevated_client


class MainWindowWindows(MainWindowBase):
    """
    Windows-specific main window extending MainWindowBase.
    
    Handles Windows-specific functionality:
    - Registry autostart
    - Windows-specific paths (AppData, ProgramData)
    - .exe detection
    - Windows mutex for single-instance
    """
    
    def __init__(self, version=None):
        super().__init__(version)
        self.setup_windows_specifics()
    
    def setup_windows_specifics(self):
        """Initialize Windows-specific features"""
        # Initialize elevation manager for fallback operations
        self.elevation_manager = get_elevation_manager()

        # Initialize elevated service client for persistent admin rights
        self.elevated_client = get_elevated_client()

        # Check if elevated service is available
        if self.elevated_client.is_available():
            print("[MainWindowWindows] ✅ Elevated service available - persistent admin rights ready")
        else:
            print("[MainWindowWindows] ⚠️  Elevated service not available - using fallback elevation")
            self._setup_persistent_elevation()

        # Check and fix autostart registry entry if needed
        self._check_autostart_registry()
        
        # Platform-specific initialization complete
        pass
    
    def _setup_persistent_elevation(self):
        """Set up persistent elevated access across reboots"""
        try:
            # Elevation manager is ready for on-demand elevated operations
            print("[MainWindowWindows] Elevation manager ready for persistent admin operations")
        except Exception as e:
            print(f"[MainWindowWindows] Error setting up elevation: {e}")
    
    def _check_autostart_registry(self):
        """Check if autostart registry entry exists and points to valid executable"""
        if not WINDOWS_AVAILABLE:
            return
            
        try:
            # Check if autostart is currently enabled
            if self.is_autostart_enabled_windows():
                # Get current registry value
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0,
                    winreg.KEY_READ
                )
                
                try:
                    current_value, _ = winreg.QueryValueEx(key, "FadCrypt")
                    winreg.CloseKey(key)
                    
                    # Get what the registry value should be
                    if getattr(sys, 'frozen', False):
                        expected_exec_path = sys.executable
                    else:
                        expected_exec_path = f'pythonw "{os.path.abspath(sys.argv[0])}"'
                    
                    expected_value = f'"{expected_exec_path}" --auto-monitor'
                    
                    # If registry doesn't match current executable, update it
                    if current_value != expected_value:
                        print(f"[MainWindowWindows] Updating autostart registry from '{current_value}' to '{expected_value}'")
                        self.setup_autostart_windows(enable=True)
                        
                except FileNotFoundError:
                    # Registry value doesn't exist, re-enable it
                    print("[MainWindowWindows] Autostart registry entry missing, re-enabling...")
                    self.setup_autostart_windows(enable=True)
                    
        except Exception as e:
            print(f"[MainWindowWindows] Error checking autostart registry: {e}")
    
    def get_platform_name(self):
        """Override to always return Windows for this implementation"""
        return "Windows"
    
    def handle_autostart_setting(self, enable):
        """
        Handle autostart setting change for Windows.
        
        Args:
            enable: True to enable autostart, False to disable
        """
        self.setup_autostart_windows(enable)
    
    def setup_autostart_windows(self, enable=True):
        """
        Set up autostart for Windows using Registry.
        
        Args:
            enable: If True, create autostart entry. If False, remove it.
        """
        if not WINDOWS_AVAILABLE:
            QMessageBox.warning(
                self,
                "Platform Error",
                "Windows autostart is not available on this platform."
            )
            return False
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        value_name = "FadCrypt"
        
        try:
            # Get the path to the executable
            if getattr(sys, 'frozen', False):
                # Running as PyInstaller bundle
                exec_path = sys.executable
            else:
                # Running as script - use pythonw to avoid console
                exec_path = f'pythonw "{os.path.abspath(sys.argv[0])}"'
            
            # Add --auto-monitor flag
            exec_command = f'"{exec_path}" --auto-monitor'
            
            if enable:
                # Open registry key
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    key_path,
                    0,
                    winreg.KEY_WRITE
                )
                
                # Set the value
                winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, exec_command)
                winreg.CloseKey(key)
                
                print(f"Autostart enabled: {exec_command}")
                return True
            else:
                # Remove the value
                try:
                    key = winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        key_path,
                        0,
                        winreg.KEY_WRITE
                    )
                    winreg.DeleteValue(key, value_name)
                    winreg.CloseKey(key)
                    print("Autostart disabled")
                    return True
                except FileNotFoundError:
                    # Value doesn't exist, already disabled
                    return True
        
        except Exception as e:
            print(f"Failed to modify autostart: {e}")
            QMessageBox.warning(
                self,
                "Autostart Error",
                f"Failed to {'enable' if enable else 'disable'} autostart:\n{str(e)}"
            )
            return False
    
    def is_autostart_enabled_windows(self):
        """
        Check if autostart is enabled on Windows.
        
        Returns:
            bool: True if autostart is enabled, False otherwise
        """
        if not WINDOWS_AVAILABLE:
            return False
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        value_name = "FadCrypt"
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,
                winreg.KEY_READ
            )
            winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error checking autostart: {e}")
            return False
    
    def open_terminal_windows(self):
        """Open a terminal on Windows"""
        try:
            # Try PowerShell first (modern Windows)
            subprocess.Popen(['powershell.exe'])
            print("Opened PowerShell")
            return True
        except Exception:
            try:
                # Fall back to cmd.exe
                subprocess.Popen(['cmd.exe'])
                print("Opened CMD")
                return True
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Terminal Error",
                    f"Failed to open terminal:\n{str(e)}"
                )
                return False
    
    def open_system_monitor_windows(self):
        """Open Task Manager on Windows"""
        try:
            subprocess.Popen(['taskmgr.exe'])
            print("Opened Task Manager")
            return True
        except Exception as e:
            QMessageBox.warning(
                self,
                "Task Manager Error",
                f"Failed to open Task Manager:\n{str(e)}"
            )
            return False
    
    def get_fadcrypt_folder(self):
        """
        Get the FadCrypt configuration folder for Windows.
        
        Returns:
            str: Path to %APPDATA%\\FadCrypt\\
        """
        appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
        config_dir = os.path.join(appdata, 'FadCrypt')
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    
    def get_backup_folder(self):
        """
        Get the backup folder for Windows.
        
        Returns:
            str: Path to C:\\ProgramData\\FadCrypt\\Backup\\
        """
        programdata = os.environ.get('PROGRAMDATA', 'C:\\ProgramData')
        backup_dir = os.path.join(programdata, 'FadCrypt', 'Backup')
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir
    
    def disable_system_tools(self):
        """
        Disable Command Prompt, Task Manager, Control Panel, and Registry Editor.
        Uses elevated service for seamless operation without admin prompts.
        """
        print("🔒 Disabling system tools (task manager, control panel, registry editor)...")

        # Try elevated service first (persistent admin rights)
        if self.elevated_client.is_available():
            success, error = self.elevated_client.disable_system_tools()
            if success:
                print("✅ System tools disabled successfully via elevated service")
                return True
            else:
                print(f"⚠️  Elevated service failed: {error}, trying fallback...")

        # Fallback to elevation manager
        try:
            success, error = self.elevation_manager.disable_system_tools()
            if success:
                print("✅ System tools disabled successfully via elevation manager")
                return True
            else:
                print(f"⚠️  Failed to disable system tools: {error}")
                print("ℹ️  Elevation manager may need setup or admin approval")
                return False

        except Exception as e:
            print(f"❌ Error disabling system tools: {e}")
            return False
    
    def enable_system_tools(self):
        """
        Re-enable Command Prompt, Task Manager, Control Panel, and Registry Editor.
        Uses elevated service for seamless operation without admin prompts.
        """
        print("🔓 Re-enabling system tools...")

        # Try elevated service first (persistent admin rights)
        if self.elevated_client.is_available():
            success, error = self.elevated_client.enable_system_tools()
            if success:
                print("✅ System tools re-enabled successfully via elevated service")
                return True
            else:
                print(f"⚠️  Elevated service failed: {error}, trying fallback...")

        # Fallback to elevation manager
        try:
            success, error = self.elevation_manager.enable_system_tools()
            if success:
                print("✅ System tools re-enabled successfully via elevation manager")
                return True
            else:
                print(f"⚠️  Failed to re-enable system tools: {error}")
                print("ℹ️  Elevation manager may need setup or admin approval")
                return False

        except Exception as e:
            print(f"❌ Error re-enabling system tools: {e}")
            return False
    
    def cleanup_context_menu(self):
        """
        Remove FadCrypt context menu entries from Windows registry.
        Called during uninstall cleanup.
        """
        try:
            from core.windows.shell_extension import ContextMenuManager
            manager = ContextMenuManager()
            if manager.unregister_context_menu():
                print("Context menu entries removed successfully")
                return True
            else:
                print("No context menu entries found to remove")
                return True
        except Exception as e:
            print(f"Failed to remove context menu entries: {e}")
            return False
    
    def refresh_context_menu(self):
        """
        Force refresh FadCrypt context menu entries in Windows registry.
        Called when user clicks the refresh button in settings.
        """
        try:
            from core.windows.shell_extension import ContextMenuManager
            import subprocess
            manager = ContextMenuManager()
            
            print("[CONTEXT MENU] Starting force refresh of context menu entries...", flush=True)
            
            # Show progress message
            QMessageBox.information(
                self,
                "Refreshing Context Menu",
                "Refreshing Windows Explorer context menu entries...\n\nThis will restart Windows Explorer."
            )
            
            if manager.force_register_context_menu():
                print("[CONTEXT MENU] Context menu refreshed successfully", flush=True)
                
                QMessageBox.information(
                    self,
                    "Success",
                    "Context menu entries refreshed successfully!"
                )
                return True
            else:
                print("[CONTEXT MENU] Failed to refresh context menu entries", flush=True)
                QMessageBox.warning(
                    self,
                    "Refresh Failed",
                    "Failed to refresh context menu entries.\n\nPlease check the console for error details."
                )
                return False
        except Exception as e:
            print(f"[CONTEXT MENU] Failed to refresh context menu entries: {e}", flush=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to refresh context menu entries:\n{str(e)}"
            )
            return False

