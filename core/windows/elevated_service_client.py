"""
FadCrypt Windows Elevated Service Client

Client for communicating with the FadCrypt Elevated Service.
Provides the same interface as the Linux elevated daemon client.
"""

import json
import os
import sys
import logging
from typing import Tuple, Optional, List

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    import win32pipe
    import win32file
    import win32api
    import win32con
    import win32security
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

# Service configuration
SERVICE_NAME = "FadCryptElevated"
PIPE_NAME = r"\\.\pipe\fadcrypt-elevated"


class ElevatedServiceClient:
    """Client for FadCrypt Windows Elevated Service"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_available_checked = False
        self._service_available = False

    def is_available(self) -> bool:
        """Check if the elevated service is available"""
        if self.is_available_checked:
            return self._service_available

        self.is_available_checked = True

        if not WINDOWS_AVAILABLE:
            self.logger.warning("Windows API not available")
            return False

        try:
            # Try to connect to the named pipe
            handle = win32file.CreateFile(
                PIPE_NAME,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0, None,
                win32file.OPEN_EXISTING,
                0, None
            )
            win32file.CloseHandle(handle)
            self._service_available = True
            self.logger.info("Elevated service is available")
            return True
        except Exception as e:
            self.logger.warning(f"Elevated service not available: {e}")
            return False

    def _send_request(self, operation: str, args: Optional[List] = None) -> Tuple[bool, Optional[str]]:
        """Send a request to the elevated service"""
        if not self.is_available():
            return False, "Elevated service not available"

        try:
            # Get user SID
            if WINDOWS_AVAILABLE:
                token = win32security.OpenProcessToken(win32api.GetCurrentProcess(), win32con.TOKEN_QUERY)
                user_sid = win32security.GetTokenInformation(token, win32security.TokenUser)[0]
                user_sid_str = win32security.ConvertSidToStringSid(user_sid)
                win32api.CloseHandle(token)
            else:
                user_sid_str = None
            
            # Create request
            request = {
                "operation": operation,
                "args": args or [],
                "user_sid": user_sid_str
            }
            request_json = json.dumps(request)

            # Connect to named pipe
            handle = win32file.CreateFile(
                PIPE_NAME,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0, None,
                win32file.OPEN_EXISTING,
                0, None
            )

            try:
                # Send request
                win32file.WriteFile(handle, request_json.encode('utf-8'))

                # Read response
                result, data = win32file.ReadFile(handle, 65536)
                if result == 0:  # Success
                    response_json = data.decode('utf-8', errors='ignore')
                    response = json.loads(response_json)

                    success = response.get('success', False)
                    error = response.get('error')

                    return success, error
                else:
                    return False, "Failed to read response"

            finally:
                win32file.CloseHandle(handle)

        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            return False, str(e)

    def disable_system_tools(self) -> Tuple[bool, Optional[str]]:
        """Disable system tools via elevated service"""
        return self._send_request("disable-tools")

    def enable_system_tools(self) -> Tuple[bool, Optional[str]]:
        """Enable system tools via elevated service"""
        return self._send_request("enable-tools")

    def protect_files(self, file_paths: List[str]) -> Tuple[bool, Optional[str]]:
        """Protect files via elevated service"""
        return self._send_request("protect-files", file_paths)

    def unprotect_files(self, file_paths: List[str]) -> Tuple[bool, Optional[str]]:
        """Unprotect files via elevated service"""
        return self._send_request("unprotect-files", file_paths)


# Global instance
_elevated_client = None


def get_elevated_client() -> ElevatedServiceClient:
    """Get or create the global elevated service client"""
    global _elevated_client
    if _elevated_client is None:
        _elevated_client = ElevatedServiceClient()
    return _elevated_client