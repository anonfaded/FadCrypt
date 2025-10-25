#!/usr/bin/env python3
"""
FadCrypt Windows Elevated Helper Script
Executes privileged operations that require administrator access.

This script is invoked by WindowsElevationManager via Task Scheduler
and handles all privileged file operations and system tool disabling.

Usage: python fadcrypt-elevated-helper.py '{"operation": "disable-tools", "args": []}'
"""

import json
import sys
import os
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[ElevatedHelper] %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import winreg
    import ctypes
    from pathlib import Path
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    logger.error("Windows modules not available")


class ElevatedOperationHandler:
    """Handles privileged operations on Windows"""
    
    def __init__(self):
        self.is_admin = self._check_admin()
        if not self.is_admin:
            logger.error("❌ This script must run with administrator privileges")
            sys.exit(1)
        
        logger.info("✅ Running with administrator privileges")
    
    def _check_admin(self) -> bool:
        """Check if running as administrator"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() == 1
        except:
            return False
    
    def handle_operation(self, operation: str, args: List[Any]) -> bool:
        """
        Dispatch operation to appropriate handler.
        
        Args:
            operation: Operation name (disable-tools, enable-tools, protect-files, etc.)
            args: Operation-specific arguments
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"🔧 Handling operation: {operation}")
        
        handlers = {
            'disable-tools': self.disable_tools,
            'enable-tools': self.enable_tools,
            'protect-files': self.protect_files,
            'unprotect-files': self.unprotect_files,
        }
        
        handler = handlers.get(operation)
        if not handler:
            logger.error(f"❌ Unknown operation: {operation}")
            return False
        
        try:
            result = handler(*args) if args else handler()
            return result
        except Exception as e:
            logger.error(f"❌ Operation failed: {e}")
            return False
    
    def disable_tools(self) -> bool:
        """
        Disable Command Prompt, Task Manager, Registry Editor, Control Panel.
        
        This prevents users from bypassing FadCrypt's application locking.
        """
        logger.info("🔒 Disabling system tools...")
        
        try:
            disable_configs = [
                # Note: CMD is not disabled here to avoid startup issues
                # Users should lock cmd.exe as an application instead
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 'DisableTaskMgr', 1),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\Explorer', 'NoControlPanel', 1),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 'DisableRegistryTools', 1),
                (r'Software\Policies\Microsoft\Windows\PowerShell', 'ExecutionPolicy', 0),
            ]
            
            success_count = 0
            for reg_path, value_name, value in disable_configs:
                try:
                    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value)
                    winreg.CloseKey(key)
                    logger.info(f"  ✅ Disabled: {value_name}")
                    success_count += 1
                except Exception as e:
                    logger.error(f"  ❌ Failed to disable {value_name}: {e}")
            
            if success_count > 0:
                logger.info(f"🛡️  Successfully disabled {success_count}/{len(disable_configs)} tools")
                return True
            else:
                logger.error("❌ Failed to disable any tools")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error disabling tools: {e}")
            return False
    
    def enable_tools(self) -> bool:
        """
        Re-enable previously disabled system tools.
        
        Called during cleanup or when monitoring is stopped.
        """
        logger.info("🔓 Enabling system tools...")
        
        try:
            enable_configs = [
                # Note: CMD is not managed here to avoid startup issues
                # Users should unlock cmd.exe as an application instead
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 'DisableTaskMgr'),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\Explorer', 'NoControlPanel'),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 'DisableRegistryTools'),
                (r'Software\Policies\Microsoft\Windows\PowerShell', 'ExecutionPolicy'),
            ]
            
            success_count = 0
            for reg_path, value_name in enable_configs:
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE)
                    try:
                        winreg.DeleteValue(key, value_name)
                        logger.info(f"  ✅ Enabled: {value_name}")
                        success_count += 1
                    except FileNotFoundError:
                        logger.info(f"  ℹ️  Already enabled: {value_name}")
                        success_count += 1
                    finally:
                        winreg.CloseKey(key)
                except Exception as e:
                    logger.warning(f"  ⚠️  Could not enable {value_name}: {e}")
            
            if success_count > 0:
                logger.info(f"✅ Successfully enabled {success_count}/{len(enable_configs)} tools")
                return True
            else:
                logger.error("❌ Failed to enable any tools")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error enabling tools: {e}")
            return False
    
    def protect_files(self, *file_paths) -> bool:
        """
        Protect critical files by setting attributes.
        
        Windows equivalent of chattr +i:
        - Sets HIDDEN, SYSTEM, READONLY attributes
        - Prevents accidental deletion
        """
        logger.info(f"🔐 Protecting {len(file_paths)} files...")
        
        try:
            import ctypes.wintypes as wintypes
            
            # Windows file attribute constants
            FILE_ATTRIBUTE_READONLY = 0x00000001
            FILE_ATTRIBUTE_HIDDEN = 0x00000002
            FILE_ATTRIBUTE_SYSTEM = 0x00000004
            
            # GetFileAttributesW and SetFileAttributesW
            get_attrs = ctypes.windll.kernel32.GetFileAttributesW
            set_attrs = ctypes.windll.kernel32.SetFileAttributesW
            
            get_attrs.argtypes = [wintypes.LPCWSTR]
            get_attrs.restype = wintypes.DWORD
            
            set_attrs.argtypes = [wintypes.LPCWSTR, wintypes.DWORD]
            set_attrs.restype = wintypes.BOOL
            
            success_count = 0
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    logger.warning(f"  ⚠️  File not found: {file_path}")
                    continue
                
                try:
                    # Get current attributes
                    current_attrs = get_attrs(file_path)
                    
                    # Add HIDDEN, SYSTEM, READONLY
                    new_attrs = current_attrs | FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM | FILE_ATTRIBUTE_READONLY
                    
                    # Set new attributes
                    if set_attrs(file_path, new_attrs):
                        logger.info(f"  ✅ Protected: {os.path.basename(file_path)}")
                        success_count += 1
                    else:
                        logger.error(f"  ❌ Failed to protect: {os.path.basename(file_path)}")
                except Exception as e:
                    logger.error(f"  ❌ Error protecting {os.path.basename(file_path)}: {e}")
            
            if success_count > 0:
                logger.info(f"🔒 Successfully protected {success_count}/{len(file_paths)} files")
                return True
            else:
                logger.error("❌ Failed to protect files")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error in file protection: {e}")
            return False
    
    def unprotect_files(self, *file_paths) -> bool:
        """
        Remove protection from files.
        
        Removes HIDDEN, SYSTEM, READONLY attributes.
        """
        logger.info(f"🔓 Unprotecting {len(file_paths)} files...")
        
        try:
            import ctypes.wintypes as wintypes
            
            # Windows file attribute constants
            FILE_ATTRIBUTE_READONLY = 0x00000001
            FILE_ATTRIBUTE_HIDDEN = 0x00000002
            FILE_ATTRIBUTE_SYSTEM = 0x00000004
            FILE_ATTRIBUTE_NORMAL = 0x00000080
            
            get_attrs = ctypes.windll.kernel32.GetFileAttributesW
            set_attrs = ctypes.windll.kernel32.SetFileAttributesW
            
            get_attrs.argtypes = [wintypes.LPCWSTR]
            get_attrs.restype = wintypes.DWORD
            
            set_attrs.argtypes = [wintypes.LPCWSTR, wintypes.DWORD]
            set_attrs.restype = wintypes.BOOL
            
            success_count = 0
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    logger.warning(f"  ⚠️  File not found: {file_path}")
                    continue
                
                try:
                    # Get current attributes
                    current_attrs = get_attrs(file_path)
                    
                    # Remove HIDDEN, SYSTEM, READONLY (keep others, add NORMAL)
                    mask = ~(FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM | FILE_ATTRIBUTE_READONLY)
                    new_attrs = (current_attrs & mask) | FILE_ATTRIBUTE_NORMAL
                    
                    # Set new attributes
                    if set_attrs(file_path, new_attrs):
                        logger.info(f"  ✅ Unprotected: {os.path.basename(file_path)}")
                        success_count += 1
                    else:
                        logger.error(f"  ❌ Failed to unprotect: {os.path.basename(file_path)}")
                except Exception as e:
                    logger.error(f"  ❌ Error unprotecting {os.path.basename(file_path)}: {e}")
            
            if success_count > 0:
                logger.info(f"✅ Successfully unprotected {success_count}/{len(file_paths)} files")
                return True
            else:
                logger.error("❌ Failed to unprotect files")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error in file unprotection: {e}")
            return False


def main():
    """Main entry point for the elevated helper"""
    
    if len(sys.argv) < 2:
        logger.error("Usage: python fadcrypt-elevated-helper.py '{\"operation\": \"...\", \"args\": [...]}'")
        sys.exit(1)
    
    try:
        # Parse JSON arguments
        args_json = sys.argv[1]
        args_data = json.loads(args_json)
        
        operation = args_data.get("operation", "")
        args = args_data.get("args", [])
        
        logger.info(f"📋 Operation: {operation}")
        logger.info(f"📊 Arguments: {len(args)} items")
        
        # Execute operation
        handler = ElevatedOperationHandler()
        success = handler.handle_operation(operation, args)
        
        sys.exit(0 if success else 1)
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse arguments: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
