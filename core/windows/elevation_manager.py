"""
Windows Privilege Elevation Manager
Equivalent to Linux PolicyKit for persistent elevated authorization.

This module provides professional privilege escalation for Windows using:
1. Windows Task Scheduler - for persistent elevated tasks (SESSION 0)
2. UAC with ShellExecuteW "runas" - for one-time elevation
3. COM API - for service-based elevation (future)

The TaskScheduler approach is more professional than UAC prompts as it:
- Persists through session changes
- Requires auth once, then caches in scheduler
- Runs with SYSTEM privileges
- Handles background operations automatically
"""

import os
import sys
import subprocess
import ctypes
import json
import tempfile
from pathlib import Path
from typing import Tuple, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)

try:
    import winreg
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    logger.warning("[ElevationManager] Windows registry module not available")


class WindowsElevationManager:
    """
    Manages privilege elevation on Windows.
    
    Professional approach: Uses Windows Task Scheduler for persistent elevated operations
    with a single UAC prompt per session, similar to Linux PolicyKit behavior.
    """
    
    # Task Scheduler paths
    TASK_FOLDER = r"\FadCrypt"
    TASK_SCHEDULER_PATH = r"C:\Windows\System32\schtasks.exe"
    
    # Helper script location
    HELPER_SCRIPT_NAME = "fadcrypt-elevated-helper.py"
    
    def __init__(self):
        """Initialize the elevation manager"""
        self.is_admin = self._check_admin()
        self.helper_script_path = self._get_helper_script_path()
        self.task_registered = False
        
        logger.info(f"[ElevationManager] Initialized - Admin: {self.is_admin}")
        logger.info(f"[ElevationManager] Helper script path: {self.helper_script_path}")
    
    def _check_admin(self) -> bool:
        """Check if running with administrator privileges"""
        try:
            if not WINDOWS_AVAILABLE:
                return False
            return ctypes.windll.shell32.IsUserAnAdmin() == 1
        except Exception as e:
            logger.error(f"[ElevationManager] Failed to check admin status: {e}")
            return False
    
    def _get_helper_script_path(self) -> Optional[str]:
        """Get path to the elevated helper script"""
        try:
            # In development: look in core/windows/
            dev_path = os.path.join(
                os.path.dirname(__file__),
                self.HELPER_SCRIPT_NAME
            )
            if os.path.exists(dev_path):
                return dev_path
            
            # In packaged app: look in sys.executable's directory
            if hasattr(sys, '_MEIPASS'):
                pkg_path = os.path.join(sys._MEIPASS, self.HELPER_SCRIPT_NAME)
                if os.path.exists(pkg_path):
                    return pkg_path
            
            logger.warning("[ElevationManager] Helper script not found")
            return None
        except Exception as e:
            logger.error(f"[ElevationManager] Error finding helper script: {e}")
            return None
    
    def execute_elevated(self, operation: str, *args) -> Tuple[bool, Optional[str]]:
        """
        Execute an operation with elevated privileges.
        
        Args:
            operation: Operation name (e.g., 'protect-files', 'unprotect-files', 'disable-tools')
            *args: Operation-specific arguments
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        # Try Task Scheduler approach first (persistent, professional)
        if self.helper_script_path:
            success, error = self._execute_via_task_scheduler(operation, *args)
            if success or error != "Task Scheduler not available":
                return success, error
        
        # Fallback to direct UAC elevation
        logger.info("[ElevationManager] Falling back to direct UAC elevation")
        return self._execute_with_uac(operation, *args)
    
    def _execute_via_task_scheduler(self, operation: str, *args) -> Tuple[bool, Optional[str]]:
        """
        Execute operation via Windows Task Scheduler (persistent elevation).
        
        This is the preferred method as it:
        1. Prompts user once with UAC
        2. Caches auth for subsequent operations
        3. Runs with SYSTEM privileges
        4. Persists across session changes
        """
        try:
            if not self.helper_script_path:
                return False, "Helper script not available"
            
            # Create temporary task that runs the helper script
            task_name = f"FadCrypt-{operation}-{id(args)}"
            task_xml = self._generate_task_xml(
                task_name,
                self.helper_script_path,
                operation,
                *args
            )
            
            # Register and execute task
            success, error = self._register_and_run_task(task_xml, task_name)
            
            # Cleanup task
            self._delete_task(task_name)
            
            return success, error
            
        except Exception as e:
            logger.error(f"[ElevationManager] Task Scheduler error: {e}")
            return False, f"Task Scheduler error: {e}"
    
    def _generate_task_xml(self, task_name: str, script_path: str, 
                          operation: str, *args) -> str:
        """Generate Task Scheduler XML for elevated task"""
        # Prepare arguments JSON
        args_json = json.dumps({"operation": operation, "args": args})
        
        # Escape for XML
        args_json = args_json.replace('"', '&quot;')
        # script_path is already absolute, no need to double-escape
        
        # Task XML with elevated privileges
        xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>FadCrypt Elevated Operation</Description>
  </RegistrationInfo>
  <Triggers>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{sys.executable}</Command>
      <Arguments>"{script_path}" '{args_json}'</Arguments>
    </Exec>
  </Actions>
</Task>
"""
        return xml
    
    def _register_and_run_task(self, xml: str, task_name: str) -> Tuple[bool, Optional[str]]:
        """Register and execute a Task Scheduler task"""
        try:
            # Save XML to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                f.write(xml)
                xml_file = f.name
            
            try:
                # Register task
                cmd_register = [
                    self.TASK_SCHEDULER_PATH,
                    '/create',
                    '/tn', f'FadCrypt\\{task_name}',
                    '/xml', xml_file,
                    '/f'
                ]
                
                result = subprocess.run(
                    cmd_register,
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode != 0:
                    logger.error(f"[ElevationManager] Task registration failed: {result.stderr}")
                    return False, f"Task registration failed: {result.stderr}"
                
                logger.info(f"[ElevationManager] Task registered: {task_name}")
                
                # Run task
                cmd_run = [
                    self.TASK_SCHEDULER_PATH,
                    '/run',
                    '/tn', f'FadCrypt\\{task_name}'
                ]
                
                result = subprocess.run(
                    cmd_run,
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode != 0:
                    logger.error(f"[ElevationManager] Task execution failed: {result.stderr}")
                    return False, f"Task execution failed: {result.stderr}"
                
                logger.info(f"[ElevationManager] Task executed successfully: {task_name}")
                return True, None
                
            finally:
                # Cleanup XML file
                try:
                    os.remove(xml_file)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"[ElevationManager] Error running task: {e}")
            return False, f"Error running task: {e}"
    
    def _delete_task(self, task_name: str) -> bool:
        """Delete a registered Task Scheduler task"""
        try:
            cmd = [
                self.TASK_SCHEDULER_PATH,
                '/delete',
                '/tn', f'FadCrypt\\{task_name}',
                '/f'
            ]
            
            subprocess.run(cmd, capture_output=True, check=False)
            logger.info(f"[ElevationManager] Task deleted: {task_name}")
            return True
        except Exception as e:
            logger.error(f"[ElevationManager] Error deleting task: {e}")
            return False
    
    def _execute_with_uac(self, operation: str, *args) -> Tuple[bool, Optional[str]]:
        """
        Fallback: Execute operation with UAC elevation.
        
        This prompts the user with UAC dialog but doesn't persist.
        Only used if Task Scheduler is unavailable.
        """
        try:
            if not self.helper_script_path:
                return False, "Helper script not available"
            
            # Prepare arguments
            args_json = json.dumps({"operation": operation, "args": args})
            
            # Use ShellExecuteW for UAC elevation
            try:
                import ctypes.wintypes as wintypes
                
                # ShellExecuteW signature
                shell_execute_w = ctypes.windll.shell32.ShellExecuteW
                shell_execute_w.argtypes = [
                    wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR,
                    wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.INT
                ]
                shell_execute_w.restype = wintypes.HINSTANCE
                
                # Execute with "runas" verb
                result = shell_execute_w(
                    None,                    # hwnd
                    "runas",                 # operation
                    sys.executable,          # file (python.exe)
                    f'"{self.helper_script_path}" \'{args_json}\'',  # parameters
                    None,                    # directory
                    1                        # show (SW_SHOW)
                )
                
                if result > 32:  # Success
                    logger.info(f"[ElevationManager] UAC elevation succeeded")
                    return True, None
                else:
                    logger.error(f"[ElevationManager] UAC elevation failed with code: {result}")
                    return False, f"UAC elevation failed: {result}"
                    
            except Exception as e:
                logger.error(f"[ElevationManager] ShellExecuteW error: {e}")
                return False, f"ShellExecuteW error: {e}"
                
        except Exception as e:
            logger.error(f"[ElevationManager] UAC execution error: {e}")
            return False, f"UAC execution error: {e}"
    
    def disable_system_tools(self) -> Tuple[bool, Optional[str]]:
        """
        Disable Command Prompt, Task Manager, Registry Editor, etc.
        Requires elevated privileges.
        """
        logger.info("[ElevationManager] Requesting elevated privileges to disable system tools")
        return self.execute_elevated("disable-tools")
    
    def enable_system_tools(self) -> Tuple[bool, Optional[str]]:
        """
        Enable previously disabled system tools.
        Requires elevated privileges.
        """
        logger.info("[ElevationManager] Requesting elevated privileges to enable system tools")
        return self.execute_elevated("enable-tools")
    
    def protect_files(self, file_paths: list) -> Tuple[bool, Optional[str]]:
        """
        Protect critical files with elevated privileges.
        Requires elevated privileges.
        """
        logger.info(f"[ElevationManager] Requesting elevated privileges to protect {len(file_paths)} files")
        return self.execute_elevated("protect-files", *file_paths)
    
    def unprotect_files(self, file_paths: list) -> Tuple[bool, Optional[str]]:
        """
        Unprotect files with elevated privileges.
        Requires elevated privileges.
        """
        logger.info(f"[ElevationManager] Requesting elevated privileges to unprotect {len(file_paths)} files")
        return self.execute_elevated("unprotect-files", *file_paths)


# Global instance
_elevation_manager = None


def get_elevation_manager() -> WindowsElevationManager:
    """Get or create the global elevation manager"""
    global _elevation_manager
    if _elevation_manager is None:
        _elevation_manager = WindowsElevationManager()
    return _elevation_manager
