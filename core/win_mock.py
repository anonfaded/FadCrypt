"""
Windows Mock Module for Testing on Linux
Usage: python FadCrypt.py --windows

IMPORTANT: This does NOT change sys.platform to avoid breaking psutil.
Instead, it only mocks Windows-specific APIs (winreg, ctypes.windll).
The UI detection is handled by the --windows flag directly.
"""

import sys
import os


def setup_windows_mocks():
    """Set up Windows mocks for Linux testing (without changing sys.platform)"""
    print("🧪 [MOCK] Setting up Windows API simulation...")
    print("🧪 [MOCK] Note: sys.platform remains 'linux' to keep psutil working")
    print("🧪 [MOCK] UI will use Windows mode via --windows flag detection")
    
    # Set up Windows environment variables
    home = os.path.expanduser('~')
    if 'APPDATA' not in os.environ:
        os.environ['APPDATA'] = os.path.join(home, '.local', 'share', 'mock_appdata')
        print(f"🧪 [MOCK] APPDATA: {os.environ['APPDATA']}")
    if 'LOCALAPPDATA' not in os.environ:
        os.environ['LOCALAPPDATA'] = os.path.join(home, '.local', 'share', 'mock_localappdata')
        print(f"🧪 [MOCK] LOCALAPPDATA: {os.environ['LOCALAPPDATA']}")
    if 'PROGRAMDATA' not in os.environ:
        os.environ['PROGRAMDATA'] = os.path.join(home, '.local', 'share', 'mock_programdata')
        print(f"🧪 [MOCK] PROGRAMDATA: {os.environ['PROGRAMDATA']}")
    
    # Mock winreg module
    class MockWinReg:
        HKEY_CURRENT_USER = "HKEY_CURRENT_USER"
        HKEY_LOCAL_MACHINE = "HKEY_LOCAL_MACHINE"
        KEY_SET_VALUE = 0x0002
        KEY_READ = 0x20019
        KEY_ALL_ACCESS = 0xF003F
        REG_SZ = 1
        REG_DWORD = 4
        REG_BINARY = 3
        
        @staticmethod
        def OpenKey(key, sub_key, reserved=0, access=0):
            print(f"🧪 [winreg] OpenKey: {key}\\{sub_key} (access={access})")
            return "mock_registry_key"
        
        @staticmethod
        def SetValueEx(key, value_name, reserved, type, value):
            type_name = {1: "REG_SZ", 4: "REG_DWORD", 3: "REG_BINARY"}.get(type, f"TYPE_{type}")
            print(f"🧪 [winreg] SetValueEx: {value_name} = {value} ({type_name})")
        
        @staticmethod
        def DeleteValue(key, value_name):
            print(f"🧪 [winreg] DeleteValue: {value_name}")
        
        @staticmethod
        def CloseKey(key):
            # Don't spam logs with CloseKey
            pass
        
        @staticmethod
        def QueryValueEx(key, value_name):
            print(f"🧪 [winreg] QueryValueEx: {value_name}")
            return ("mock_value", MockWinReg.REG_SZ)
        
        @staticmethod
        def CreateKey(key, sub_key):
            print(f"🧪 [winreg] CreateKey: {key}\\{sub_key}")
            return "mock_registry_key"
    
    # Mock ctypes.windll
    class MockWinDLL:
        class Shell32:
            @staticmethod
            def IsUserAnAdmin():
                print("🧪 [ctypes.windll.shell32] IsUserAnAdmin() → True")
                return 1  # Simulate admin
            
            @staticmethod
            def ShellExecuteW(hwnd, operation, file, parameters, directory, show_cmd):
                print(f"🧪 [ctypes.windll.shell32] ShellExecuteW:")
                print(f"    operation: {operation}")
                print(f"    file: {file}")
                print(f"    parameters: {parameters}")
                return 42  # Success code
        
        class User32:
            @staticmethod
            def SystemParametersInfoW(action, param, pvParam, winini):
                print(f"🧪 [ctypes.windll.user32] SystemParametersInfoW(action={action})")
                return 1  # Success
        
        shell32 = Shell32()
        user32 = User32()
    
    # Patch modules
    import ctypes
    if not hasattr(ctypes, 'windll'):
        ctypes.windll = MockWinDLL()
        print("🧪 [MOCK] ctypes.windll patched")
    
    sys.modules['winreg'] = MockWinReg()
    print("🧪 [MOCK] winreg module patched")
    
    # DO NOT change sys.platform - keep it as 'linux' so psutil works
    # The UI will detect Windows mode via the --mock-windows flag
    print("🧪 [MOCK] sys.platform kept as 'linux' (for psutil compatibility)")
    
    # Create mock Windows directories for app scanning
    mock_program_files = os.path.join(home, '.mock_windows', 'Program Files')
    mock_program_files_x86 = os.path.join(home, '.mock_windows', 'Program Files (x86)')
    mock_local_programs = os.path.join(home, '.mock_windows', 'AppData', 'Local', 'Programs')
    
    for mock_dir in [mock_program_files, mock_program_files_x86, mock_local_programs]:
        os.makedirs(mock_dir, exist_ok=True)
    
    print(f"🧪 [MOCK] Created mock Windows directories:")
    print(f"    {mock_program_files}")
    print(f"    {mock_program_files_x86}")
    print(f"    {mock_local_programs}")
    
    print("🧪 [MOCK] Windows API mocking ready!")
    print("=" * 60)


def cleanup_mocks():
    """Clean up mocks (no-op since we don't change sys.platform anymore)"""
    print("\n🧪 [MOCK] Cleanup complete")
