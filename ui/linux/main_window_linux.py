"""Linux-specific Main Window for FadCrypt PyQt6 UI"""

import os
import subprocess
from PyQt6.QtWidgets import QMessageBox
from ui.base.main_window_base import MainWindowBase


class MainWindowLinux(MainWindowBase):
    """
    Linux-specific main window extending MainWindowBase.
    
    Handles Linux-specific functionality:
    - .desktop file autostart
    - Linux-specific paths (~/.config/autostart/)
    - ELF binary detection
    - fcntl locking for single-instance
    """
    
    def __init__(self, version=None):
        super().__init__(version)
        self.setup_linux_specifics()
    
    def setup_linux_specifics(self):
        """Initialize Linux-specific features"""
        # Platform-specific initialization complete
        pass
    
    def get_platform_name(self):
        """Override to always return Linux for this implementation"""
        return "Linux"
    
    def handle_autostart_setting(self, enable):
        """
        Handle autostart setting change for Linux.
        
        Args:
            enable: True to enable autostart, False to disable
        """
        self.setup_autostart_linux(enable)
    
    def setup_autostart_linux(self, enable=True):
        """
        Set up autostart for Linux using .desktop file.
        
        Args:
            enable: If True, create autostart entry. If False, remove it.
        """
        autostart_dir = os.path.expanduser("~/.config/autostart")
        desktop_file = os.path.join(autostart_dir, "fadcrypt.desktop")
        
        if enable:
            # Create autostart directory if it doesn't exist
            os.makedirs(autostart_dir, exist_ok=True)
            
            # Get the path to the executable
            import sys
            if getattr(sys, 'frozen', False):
                # Running as PyInstaller bundle
                exec_path = sys.executable
            else:
                # Running as script
                exec_path = os.path.abspath(sys.argv[0])
            
            # Create .desktop file content
            desktop_content = f"""[Desktop Entry]
Type=Application
Name=FadCrypt
Comment=Application Locker and Monitor
Exec={exec_path} --auto-monitor
Icon=fadcrypt
Terminal=false
Categories=Utility;Security;
StartupNotify=false
X-GNOME-Autostart-enabled=true
"""
            
            # Write .desktop file
            try:
                with open(desktop_file, 'w') as f:
                    f.write(desktop_content)
                
                # Make it executable
                os.chmod(desktop_file, 0o755)
                
                print(f"Autostart enabled: {desktop_file}")
                return True
            except Exception as e:
                print(f"Failed to create autostart entry: {e}")
                QMessageBox.warning(
                    self,
                    "Autostart Error",
                    f"Failed to enable autostart:\n{str(e)}"
                )
                return False
        else:
            # Remove autostart entry
            try:
                if os.path.exists(desktop_file):
                    os.remove(desktop_file)
                    print(f"Autostart disabled: {desktop_file}")
                return True
            except Exception as e:
                print(f"Failed to remove autostart entry: {e}")
                QMessageBox.warning(
                    self,
                    "Autostart Error",
                    f"Failed to disable autostart:\n{str(e)}"
                )
                return False
    
    def is_autostart_enabled_linux(self):
        """
        Check if autostart is enabled on Linux.
        
        Returns:
            bool: True if autostart is enabled, False otherwise
        """
        desktop_file = os.path.expanduser("~/.config/autostart/fadcrypt.desktop")
        return os.path.exists(desktop_file)
    
    def open_terminal_linux(self):
        """Open a terminal on Linux (distribution-aware)"""
        terminals = [
            'gnome-terminal',
            'konsole',
            'xfce4-terminal',
            'xterm',
            'terminator',
            'tilix'
        ]
        
        for terminal in terminals:
            try:
                subprocess.Popen([terminal])
                print(f"Opened terminal: {terminal}")
                return True
            except FileNotFoundError:
                continue
        
        QMessageBox.warning(
            self,
            "Terminal Not Found",
            "Could not find a terminal emulator.\n"
            "Please install gnome-terminal, konsole, or xterm."
        )
        return False
    
    def open_system_monitor_linux(self):
        """Open system monitor on Linux (distribution-aware)"""
        monitors = [
            'gnome-system-monitor',
            'ksysguard',
            'xfce4-taskmanager',
            'mate-system-monitor',
            'htop',
            'top'
        ]
        
        for monitor in monitors:
            try:
                if monitor in ['htop', 'top']:
                    # These need a terminal
                    subprocess.Popen(['gnome-terminal', '--', monitor])
                else:
                    subprocess.Popen([monitor])
                print(f"Opened system monitor: {monitor}")
                return True
            except FileNotFoundError:
                continue
        
        QMessageBox.warning(
            self,
            "System Monitor Not Found",
            "Could not find a system monitor application.\n"
            "Please install gnome-system-monitor or ksysguard."
        )
        return False
    
    def get_fadcrypt_folder(self):
        """
        Get the FadCrypt configuration folder for Linux.
        
        Returns:
            str: Path to ~/.config/FadCrypt/
        """
        config_dir = os.path.expanduser("~/.config/FadCrypt")
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    
    def get_backup_folder(self):
        """
        Get the backup folder for Linux.
        
        Returns:
            str: Path to ~/.config/FadCrypt/backup/
        """
        backup_dir = os.path.expanduser("~/.config/FadCrypt/backup")
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir
    
    def get_logs_folder(self):
        """
        Get the logs folder for Linux.
        
        Returns:
            str: Path to ~/.config/FadCrypt/logs/
        """
        logs_dir = os.path.expanduser("~/.config/FadCrypt/logs")
        os.makedirs(logs_dir, exist_ok=True)
        return logs_dir
    
    def get_temp_folder(self):
        """
        Get the temp folder for Linux.
        
        Returns:
            str: Path to ~/.config/FadCrypt/temp/
        """
        temp_dir = os.path.expanduser("~/.config/FadCrypt/temp")
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
    
    def disable_system_tools(self):
        """
        Disable system tools on Linux (terminals and system monitors).
        Uses elevated daemon to remove execute permissions. Seamless - no password prompts.
        This is called when "Disable Main loopholes" is enabled before monitoring starts.
        """
        try:
            from core.linux.elevated_daemon_client import get_elevated_client
            
            # List of common terminal and system monitor executables
            tools_to_disable = [
                '/usr/bin/gnome-terminal',
                '/usr/bin/konsole',
                '/usr/bin/xterm',
                '/usr/bin/gnome-system-monitor',
                '/usr/bin/htop',
                '/usr/bin/top'
            ]
            
            disabled_tools = []
            for tool in tools_to_disable:
                if os.path.exists(tool) and os.access(tool, os.X_OK):
                    disabled_tools.append(tool)
            
            if disabled_tools:
                # Use elevated daemon to change permissions
                client = get_elevated_client()
                if not client.is_available():
                    print(f"✗ Elevated daemon not available for chmod operations")
                    return False
                
                # Change all tools to 644 (no execute permission)
                success, message = client.chmod(disabled_tools, 0o644)
                if success:
                    print(f"✓ Disabled tools: {disabled_tools}")
                    
                    # Save the list of modified tools for re-enabling later
                    disabled_tools_file = os.path.join(self.get_fadcrypt_folder(), 'disabled_tools.txt')
                    with open(disabled_tools_file, 'w') as f:
                        f.write('\n'.join(disabled_tools))
                    
                    return True
                else:
                    print(f"✗ Daemon failed to disable tools: {message}")
                    return False
            else:
                print("ℹ No tools were disabled (tools not found or already disabled)")
                return True
                
        except Exception as e:
            print(f"Error in disable_system_tools: {e}")
            return False
    
    def enable_system_tools(self):
        """
        Re-enable previously disabled tools on Linux.
        Restores execute permissions using elevated daemon. Seamless - no password prompts.
        This is called when monitoring stops or during cleanup.
        """
        try:
            from core.linux.elevated_daemon_client import get_elevated_client
            
            # First try to read from the tracking file
            disabled_tools_file = os.path.join(self.get_fadcrypt_folder(), 'disabled_tools.txt')
            tools_to_enable = []
            
            if os.path.exists(disabled_tools_file):
                with open(disabled_tools_file, 'r') as f:
                    tools_to_enable = [tool.strip() for tool in f.read().strip().split('\n') if tool.strip()]
            
            # If no tracking file, try to re-enable all common tools
            if not tools_to_enable:
                tools_to_enable = [
                    '/usr/bin/gnome-terminal',
                    '/usr/bin/konsole',
                    '/usr/bin/xterm',
                    '/usr/bin/gnome-system-monitor',
                    '/usr/bin/htop',
                    '/usr/bin/top'
                ]

            valid_tools = []
            for tool in tools_to_enable:
                if tool and os.path.exists(tool):
                    valid_tools.append(tool)

            if valid_tools:
                # Use elevated daemon to restore permissions
                client = get_elevated_client()
                if not client.is_available():
                    print(f"✗ Elevated daemon not available for chmod operations")
                    return False
                
                # Change all tools to 755 (executable permission restored)
                success, message = client.chmod(valid_tools, 0o755)
                if success:
                    for tool in valid_tools:
                        print(f"✓ Re-enabled: {tool}")
                    
                    # Clean up the record file after restoring permissions
                    if os.path.exists(disabled_tools_file):
                        os.remove(disabled_tools_file)
                    
                    return True
                else:
                    print(f"✗ Daemon failed to restore permissions: {message}")
                    return False
            else:
                print("ℹ No valid tools found to re-enable")
                return True
                
        except Exception as e:
            print(f"Error in enable_system_tools: {e}")
            return False

