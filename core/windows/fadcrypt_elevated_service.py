"""
FadCrypt Windows Elevated Service

A Windows service that provides persistent elevated privileges for FadCrypt operations.
This service runs with SYSTEM privileges and handles file protection and system tool management.

Installation:
- Install as a Windows service during InnoSetup installation
- Runs automatically on boot with SYSTEM privileges
- Provides IPC interface for FadCrypt to request elevated operations

Operations:
- protect-files: Protect critical files with SYSTEM privileges
- unprotect-files: Unprotect files
- disable-tools: Disable system tools (CMD, TaskMgr, etc.)
- enable-tools: Re-enable system tools
"""

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import threading
import json
import os
import sys
import logging
from pathlib import Path

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    import winreg
    import ctypes
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

# Service configuration
SERVICE_NAME = "FadCryptElevated"
SERVICE_DISPLAY_NAME = "FadCrypt Elevated Service"
SERVICE_DESCRIPTION = "Provides elevated privileges for FadCrypt operations"

SOCKET_FILE = r"\\.\pipe\fadcrypt-elevated"
LOG_FILE = os.path.join(os.environ.get('PROGRAMDATA', 'C:\\ProgramData'), 'FadCrypt', 'service.log')


class FadCryptElevatedService(win32serviceutil.ServiceFramework):
    """Windows service for FadCrypt elevated operations"""

    _svc_name_ = SERVICE_NAME
    _svc_display_name_ = SERVICE_DISPLAY_NAME
    _svc_description_ = SERVICE_DESCRIPTION

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True
        self.server_thread = None

        # Ensure log directory exists
        log_dir = os.path.dirname(LOG_FILE)
        os.makedirs(log_dir, exist_ok=True)

        # Setup logging
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def SvcStop(self):
        """Stop the service"""
        self.logger.info("Service stop requested")
        self.is_running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """Main service loop"""
        self.logger.info("FadCrypt Elevated Service starting")

        try:
            # Start the IPC server
            self.server_thread = threading.Thread(target=self._run_server)
            self.server_thread.daemon = True
            self.server_thread.start()

            self.logger.info("Service running, waiting for requests...")

            # Wait for stop event
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

        except Exception as e:
            self.logger.error(f"Service error: {e}")
        finally:
            self.logger.info("FadCrypt Elevated Service stopped")

    def _run_server(self):
        """Run the IPC server to handle requests"""
        try:
            # Note: Named pipes don't need to be "removed" like Unix sockets
            # Windows handles pipe cleanup automatically

            # Create named pipe server
            import win32pipe
            import win32file

            while self.is_running:
                try:
                    # Create named pipe
                    pipe = win32pipe.CreateNamedPipe(
                        SOCKET_FILE,
                        win32pipe.PIPE_ACCESS_DUPLEX,
                        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                        1,  # Max instances
                        65536,  # Out buffer size
                        65536,  # In buffer size
                        0,  # Default timeout
                        None  # Security attributes
                    )

                    self.logger.info("Waiting for client connection...")

                    # Wait for client
                    win32pipe.ConnectNamedPipe(pipe, None)

                    # Read request
                    result, data = win32file.ReadFile(pipe, 65536)
                    if result == 0:  # Success
                        request = data.decode('utf-8', errors='ignore')
                        self.logger.info(f"Received request: {request}")

                        try:
                            request_data = json.loads(request)
                            response = self._handle_request(request_data)
                            response_json = json.dumps(response)

                            # Send response
                            win32file.WriteFile(pipe, response_json.encode('utf-8'))
                        except Exception as e:
                            error_response = {"success": False, "error": str(e)}
                            win32file.WriteFile(pipe, json.dumps(error_response).encode('utf-8'))
                            self.logger.error(f"Request handling error: {e}")

                    # Disconnect
                    win32pipe.DisconnectNamedPipe(pipe)

                except Exception as e:
                    self.logger.error(f"Pipe error: {e}")
                    break

        except Exception as e:
            self.logger.error(f"Server error: {e}")

    def _handle_request(self, request):
        """Handle incoming requests"""
        try:
            operation = request.get('operation')
            args = request.get('args', [])

            self.logger.info(f"Handling operation: {operation}")

            if operation == 'disable-tools':
                success = self._disable_system_tools()
                return {"success": success}

            elif operation == 'enable-tools':
                success = self._enable_system_tools()
                return {"success": success}

            elif operation == 'protect-files':
                file_paths = args
                success = self._protect_files(file_paths)
                return {"success": success}

            elif operation == 'unprotect-files':
                file_paths = args
                success = self._unprotect_files(file_paths)
                return {"success": success}

            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            self.logger.error(f"Request handling error: {e}")
            return {"success": False, "error": str(e)}

    def _disable_system_tools(self):
        """Disable system tools with elevated privileges"""
        try:
            disable_configs = [
                (r'Software\Policies\Microsoft\Windows\System', 'DisableCMD', 1),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 'DisableTaskMgr', 1),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\Explorer', 'NoControlPanel', 1),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 'DisableRegistryTools', 1),
            ]

            for reg_path, value_name, value in disable_configs:
                try:
                    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value)
                    winreg.CloseKey(key)
                    self.logger.info(f"Disabled: {value_name}")
                except Exception as e:
                    self.logger.warning(f"Could not disable {value_name}: {e}")

            return True
        except Exception as e:
            self.logger.error(f"Error disabling tools: {e}")
            return False

    def _enable_system_tools(self):
        """Re-enable system tools"""
        try:
            enable_configs = [
                (r'Software\Policies\Microsoft\Windows\System', 'DisableCMD'),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 'DisableTaskMgr'),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\Explorer', 'NoControlPanel'),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 'DisableRegistryTools'),
            ]

            for reg_path, value_name in enable_configs:
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE)
                    try:
                        winreg.DeleteValue(key, value_name)
                        self.logger.info(f"Enabled: {value_name}")
                    except FileNotFoundError:
                        self.logger.info(f"Already enabled: {value_name}")
                    winreg.CloseKey(key)
                except Exception as e:
                    self.logger.warning(f"Could not enable {value_name}: {e}")

            return True
        except Exception as e:
            self.logger.error(f"Error enabling tools: {e}")
            return False

    def _protect_files(self, file_paths):
        """Protect files with SYSTEM privileges"""
        try:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    # Set file attributes: Hidden + System + Read-only
                    ctypes.windll.kernel32.SetFileAttributesW(file_path, 0x02 | 0x04 | 0x01)
                    self.logger.info(f"Protected: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error protecting files: {e}")
            return False

    def _unprotect_files(self, file_paths):
        """Unprotect files"""
        try:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    # Remove Hidden + System + Read-only attributes
                    ctypes.windll.kernel32.SetFileAttributesW(file_path, 0x80)  # Normal
                    self.logger.info(f"Unprotected: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error unprotecting files: {e}")
            return False


def install_service():
    """Install the Windows service"""
    try:
        # Ensure log directory exists
        log_dir = r"C:\ProgramData\FadCrypt"
        os.makedirs(log_dir, exist_ok=True)
        
        # Get the path to the service script
        script_path = os.path.abspath(__file__)

        # Install service
        win32serviceutil.InstallService(
            None,  # cls
            SERVICE_NAME,
            SERVICE_DISPLAY_NAME,
            startType=win32service.SERVICE_AUTO_START,
            exeName=sys.executable,
            exeArgs='--run-service'
        )

        print(f"Service '{SERVICE_DISPLAY_NAME}' installed successfully")
        return True
    except Exception as e:
        print(f"Failed to install service: {e}")
        return False


def uninstall_service():
    """Uninstall the Windows service"""
    try:
        win32serviceutil.RemoveService(SERVICE_NAME)
        print(f"Service '{SERVICE_DISPLAY_NAME}' uninstalled successfully")
        return True
    except Exception as e:
        print(f"Failed to uninstall service: {e}")
        return False


def start_service():
    """Start the service"""
    try:
        win32serviceutil.StartService(SERVICE_NAME)
        print(f"Service '{SERVICE_DISPLAY_NAME}' started successfully")
        return True
    except Exception as e:
        print(f"Failed to start service: {e}")
        return False


def stop_service():
    """Stop the service"""
    try:
        win32serviceutil.StopService(SERVICE_NAME)
        print(f"Service '{SERVICE_DISPLAY_NAME}' stopped successfully")
        return True
    except Exception as e:
        print(f"Failed to stop service: {e}")
        return False


def check_service_status():
    """Check the status of the service"""
    try:
        status = win32serviceutil.QueryServiceStatus(SERVICE_NAME)
        status_text = {
            win32service.SERVICE_STOPPED: "STOPPED",
            win32service.SERVICE_START_PENDING: "START_PENDING", 
            win32service.SERVICE_STOP_PENDING: "STOP_PENDING",
            win32service.SERVICE_RUNNING: "RUNNING",
            win32service.SERVICE_CONTINUE_PENDING: "CONTINUE_PENDING",
            win32service.SERVICE_PAUSE_PENDING: "PAUSE_PENDING",
            win32service.SERVICE_PAUSED: "PAUSED"
        }.get(status[1], f"UNKNOWN ({status[1]})")
        
        print(f"Service '{SERVICE_DISPLAY_NAME}' status: {status_text}")
        return True
    except Exception as e:
        print(f"Service '{SERVICE_DISPLAY_NAME}' not found or error: {e}")
        return False


if __name__ == '__main__':
    # Handle command line arguments
    if len(sys.argv) == 1:
        # Run as service
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(FadCryptElevatedService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Handle installation commands
        command = sys.argv[1].lower()
        if command == 'install':
            install_service()
        elif command == 'uninstall':
            uninstall_service()
        elif command == 'start':
            start_service()
        elif command == 'stop':
            stop_service()
        elif command == 'status':
            check_service_status()
        else:
            print("Usage: python fadcrypt_elevated_service.py [install|uninstall|start|stop|status]")