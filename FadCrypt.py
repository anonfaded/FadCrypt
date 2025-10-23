#!/usr/bin/env python3
"""
FadCrypt - PyQt6 Entry Point (Cross-Platform)
Modern application locker with PyQt6 UI

Detects platform and loads appropriate platform-specific main window.
"""

# CRITICAL: Handle --cleanup flag FIRST, before any GUI imports
# This is called by the uninstaller to restore disabled tools
import sys
import os
import platform

# Register context menu on Windows (first launch)
if platform.system() == "Windows" and '--lock' not in sys.argv and '--unlock' not in sys.argv and '--cleanup' not in sys.argv:
    try:
        from core.windows.shell_extension import ContextMenuManager
        import subprocess
        manager = ContextMenuManager()
        success, already_registered = manager.register_context_menu_if_needed()
        
        if success and not already_registered:
            # Only restart explorer if we actually registered something new
            print("[CONTEXT MENU] New registration detected, restarting Explorer...", flush=True)
            try:
                subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], 
                             stderr=subprocess.DEVNULL, timeout=5)
                subprocess.Popen('explorer.exe')
                print("[CONTEXT MENU] Explorer restarted successfully", flush=True)
            except Exception as e:
                print(f"[CONTEXT MENU] Warning: Could not restart Explorer: {e}", flush=True)
        elif success and already_registered:
            print("[CONTEXT MENU] Already registered, skipping Explorer restart", flush=True)
        else:
            print("[CONTEXT MENU] Registration failed", flush=True)
    except Exception as e:
        print(f"[CONTEXT MENU] Error during registration: {e}", flush=True)

# Handle --lock and --unlock from context menu
if '--lock' in sys.argv or '--unlock' in sys.argv:
    print(f"[CLI] Processing CLI arguments: {sys.argv}", flush=True)
    try:
        if '--lock' in sys.argv:
            idx = sys.argv.index('--lock')
            if idx + 1 < len(sys.argv):
                path = sys.argv[idx + 1]
                print(f"[CLI] Locking file: {path}", flush=True)
                from core.windows.cli_lock_handler import lock_file_with_password
                success = lock_file_with_password(path)
                print(f"[CLI] Lock result: {success}", flush=True)
                sys.exit(0 if success else 1)
        
        elif '--unlock' in sys.argv:
            idx = sys.argv.index('--unlock')
            if idx + 1 < len(sys.argv):
                path = sys.argv[idx + 1]
                print(f"[CLI] Unlocking file: {path}", flush=True)
                from core.windows.cli_lock_handler import unlock_file_with_password
                success = unlock_file_with_password(path)
                print(f"[CLI] Unlock result: {success}", flush=True)
                sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[CLI] Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if '--cleanup' in sys.argv:
    import subprocess
    import platform
    print("[CLEANUP] Starting FadCrypt cleanup...", flush=True)
    
    # Log to file for debugging uninstall issues
    try:
        log_file = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'fadcrypt_cleanup.log')
        with open(log_file, 'w') as f:
            f.write(f"[CLEANUP] Started at {os.times()}\n")
            f.write(f"[CLEANUP] Executable: {sys.executable}\n")
            f.write(f"[CLEANUP] Arguments: {sys.argv}\n")
            f.write(f"[CLEANUP] Platform: {platform.system()}\n")
    except Exception as e:
        print(f"[CLEANUP] Could not create log file: {e}", flush=True)
    
    try:
        system = platform.system()
        
        if system == "Linux":
            # Get user's home directory (handle sudo context)
            if 'SUDO_USER' in os.environ:
                import pwd
                user_home = pwd.getpwnam(os.environ['SUDO_USER']).pw_dir
                print(f"[CLEANUP] Running as sudo, user home: {user_home}", flush=True)
            else:
                user_home = os.path.expanduser('~')
                print(f"[CLEANUP] User home: {user_home}", flush=True)
            
            fadcrypt_folder = os.path.join(user_home, '.config', 'FadCrypt')
            fadcrypt_backup_folder = os.path.join(user_home, '.local', 'share', 'FadCrypt', 'Backup')
            
            # CRITICAL: Remove immutable flags before deletion (files may have chattr +i from file protection)
            folders_to_clean = [
                fadcrypt_folder,
                fadcrypt_backup_folder
            ]
            
            for folder in folders_to_clean:
                if os.path.exists(folder):
                    try:
                        # Find all files and remove immutable flag
                        print(f"[CLEANUP] Removing immutable flags from {folder}...", flush=True)
                        result = subprocess.run(
                            ['find', folder, '-type', 'f', '-exec', 'chattr', '-i', '{}', '+'],
                            capture_output=True,
                            text=True,
                            check=False,
                            timeout=10
                        )
                        if result.returncode == 0:
                            print(f"[CLEANUP] ✅ Removed immutable flags", flush=True)
                        else:
                            print(f"[CLEANUP] ⚠️  Could not remove immutable flags via chattr", flush=True)
                            print(f"[CLEANUP]     Note: Daemon will handle cleanup when service stops", flush=True)
                    except Exception as e:
                        print(f"[CLEANUP] ⚠️ Warning: Could not remove immutable flags: {e}", flush=True)
            
            # Remove all FadCrypt config and backup folders
            folders_to_remove = [
                fadcrypt_folder,
                fadcrypt_backup_folder
            ]
            
            for folder in folders_to_remove:
                if os.path.exists(folder):
                    try:
                        import shutil
                        shutil.rmtree(folder)
                        print(f"[CLEANUP] ✅ Removed: {folder}", flush=True)
                    except Exception as e:
                        print(f"[CLEANUP] ⚠️ Warning: Could not remove {folder}: {e}", flush=True)
            
            # List of common system tools that might have been disabled
            all_tools = [
                '/usr/bin/gnome-terminal',
                '/usr/bin/konsole',
                '/usr/bin/xterm',
                '/usr/bin/gnome-system-monitor',
                '/usr/bin/htop',
                '/usr/bin/top',
                '/usr/bin/gnome-control-center'
            ]
            
            print(f"[CLEANUP] Checking {len(all_tools)} common system tools...", flush=True)
            
            # Find tools that need restoring
            tools_to_restore = []
            for tool in all_tools:
                if os.path.exists(tool):
                    try:
                        stat_info = os.stat(tool)
                        # Check if execute permission is missing (was disabled)
                        if not (stat_info.st_mode & 0o111):
                            tools_to_restore.append(tool)
                            print(f"[CLEANUP] Will restore: {tool}", flush=True)
                    except Exception as e:
                        print(f"[CLEANUP] Error checking {tool}: {e}", flush=True)
            
            # Restore permissions for disabled tools
            if tools_to_restore:
                print(f"[CLEANUP] Restoring {len(tools_to_restore)} disabled tools...", flush=True)
                chmod_commands = [f'chmod 755 "{tool}"' for tool in tools_to_restore]
                full_command = ' && '.join(chmod_commands)
                
                # Direct chmod (prerm script runs with root)
                result = subprocess.run(['bash', '-c', full_command], 
                                      capture_output=True, 
                                      text=True,
                                      check=False)
                
                if result.returncode == 0:
                    print(f"[CLEANUP] ✅ Restored {len(tools_to_restore)} tools", flush=True)
                else:
                    print(f"[CLEANUP] ⚠️ Warning: {result.stderr}", flush=True)
            else:
                print("[CLEANUP] No disabled tools found", flush=True)
            
            # Remove lock file if it exists
            lock_file = '/tmp/fadcrypt.lock'
            if os.path.exists(lock_file):
                try:
                    os.remove(lock_file)
                    print(f"[CLEANUP] ✅ Removed lock file: {lock_file}", flush=True)
                except PermissionError:
                    # Lock file might be owned by different user - cleanup script runs as root
                    try:
                        subprocess.run(['rm', '-f', lock_file], check=True)
                        print(f"[CLEANUP] ✅ Removed lock file: {lock_file}", flush=True)
                    except Exception as e:
                        print(f"[CLEANUP] Warning: Could not remove lock file: {e}", flush=True)
                except Exception as e:
                    print(f"[CLEANUP] Warning: Could not remove lock file: {e}", flush=True)
        
        elif system == "Windows":
            print("[CLEANUP] Windows cleanup - restoring system tools and cleaning registry...", flush=True)
            import winreg
            
            # Remove FadCrypt from PATH
            print("[CLEANUP] Removing FadCrypt from PATH...", flush=True)
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ | winreg.KEY_SET_VALUE)
                try:
                    current_path, _ = winreg.QueryValueEx(key, "Path")
                    if not current_path:
                        print("[CLEANUP] ℹ️  PATH is empty", flush=True)
                    else:
                        # Get the installation directory (where this executable should be)
                        # During uninstall, we should be running from the installed location
                        exe_path = sys.executable
                        if hasattr(sys, '_MEIPASS'):
                            # Running from PyInstaller bundle - get the directory containing the exe
                            exe_dir = os.path.dirname(exe_path)
                        else:
                            # Running from source - don't modify PATH
                            exe_dir = None
                        
                        if exe_dir:
                            print(f"[CLEANUP] Removing directory from PATH: {exe_dir}", flush=True)
                            # Split PATH and filter out the exe directory
                            path_parts = current_path.split(';')
                            original_count = len(path_parts)
                            # Remove empty strings and the exe directory
                            filtered_parts = [p for p in path_parts if p and p.strip() and p.strip() != exe_dir]
                            
                            if len(filtered_parts) != original_count:
                                new_path = ';'.join(filtered_parts)
                                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                                print("[CLEANUP] ✅ Removed FadCrypt from PATH", flush=True)
                            else:
                                print("[CLEANUP] ℹ️  FadCrypt directory not found in PATH", flush=True)
                        else:
                            print("[CLEANUP] ℹ️  Not running from PyInstaller bundle, skipping PATH removal", flush=True)
                except FileNotFoundError:
                    print("[CLEANUP] ℹ️  PATH environment variable not found", flush=True)
                finally:
                    winreg.CloseKey(key)
                    
                # Notify system of environment change
                try:
                    import ctypes
                    HWND_BROADCAST = 0xFFFF
                    WM_SETTINGCHANGE = 0x001A
                    SMTO_ABORTIFHUNG = 0x0002
                    result = ctypes.windll.user32.SendMessageTimeoutW(
                        HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment",
                        SMTO_ABORTIFHUNG, 5000, None
                    )
                    if result:
                        print("[CLEANUP] ✅ Notified system of PATH change", flush=True)
                except Exception as e:
                    print(f"[CLEANUP] ℹ️  Could not notify system of PATH change: {e}", flush=True)
                    
            except Exception as e:
                print(f"[CLEANUP] Warning: Could not remove from PATH: {e}", flush=True)
            
            # Registry keys that FadCrypt may have disabled
            
            # Registry keys that FadCrypt may have disabled
            keys_to_restore = [
                (r'Software\Policies\Microsoft\Windows\System', 'DisableCMD'),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 'DisableTaskMgr'),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\Explorer', 'NoControlPanel'),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 'DisableRegistryTools')
            ]
            
            restored_count = 0
            for reg_path, value_name in keys_to_restore:
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 0)  # 0 = enabled
                    winreg.CloseKey(key)
                    restored_count += 1
                    print(f"[CLEANUP] Restored: {value_name}", flush=True)
                except FileNotFoundError:
                    pass  # Key doesn't exist
                except Exception as e:
                    print(f"[CLEANUP] Warning: Could not restore {value_name}: {e}", flush=True)
            
            # Remove FadCrypt context menu entries
            print("[CLEANUP] Removing FadCrypt context menu entries...", flush=True)
            try:
                from core.windows.shell_extension import ContextMenuManager
                manager = ContextMenuManager()
                if manager.unregister_context_menu():
                    print("[CLEANUP] ✅ Removed context menu entries", flush=True)
                else:
                    print("[CLEANUP] ⚠️  No context menu entries found to remove", flush=True)
            except Exception as e:
                print(f"[CLEANUP] Warning: Could not remove context menu entries: {e}", flush=True)
            
            # Remove from Windows startup
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                   r"Software\Microsoft\Windows\CurrentVersion\Run",
                                   0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, "FadCrypt")
                winreg.CloseKey(key)
                print("[CLEANUP] Removed from Windows startup", flush=True)
            except FileNotFoundError:
                pass  # Not in startup
            except Exception as e:
                print(f"[CLEANUP] Warning: Could not remove startup entry: {e}", flush=True)
            
            print(f"[CLEANUP] ✅ Restored {restored_count} Windows settings", flush=True)
        
        print("[CLEANUP] ✅ Cleanup completed successfully", flush=True)
        
        # Log completion
        try:
            log_file = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'fadcrypt_cleanup.log')
            with open(log_file, 'a') as f:
                f.write(f"[CLEANUP] Completed successfully at {os.times()}\n")
        except:
            pass
            
        sys.exit(0)
        
    except Exception as e:
        print(f"[CLEANUP] ❌ Error during cleanup: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Normal startup continues below
import platform
import signal
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt, QTimer
except ImportError as e:
    print("❌ PyQt6 is not installed!")
    print("📦 Install with: pip install PyQt6")
    print(f"   Error: {e}")
    sys.exit(1)

from version import __version__, __version_code__


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    import sys
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def get_main_window_class(force_windows=False):
    """
    Detect platform and return appropriate main window class.
    
    Args:
        force_windows: If True, force Windows UI (for mock testing on Linux)
    
    Returns:
        MainWindowLinux or MainWindowWindows depending on platform
    """
    system = platform.system()
    
    # Force Windows UI if mock mode is enabled
    if force_windows:
        print("🧪 [MOCK] Forcing Windows UI (system detected: {})".format(system))
        from ui.windows.main_window_windows import MainWindowWindows
        return MainWindowWindows
    
    if system == "Linux":
        from ui.linux.main_window_linux import MainWindowLinux
        return MainWindowLinux
    elif system == "Windows":
        from ui.windows.main_window_windows import MainWindowWindows
        return MainWindowWindows
    else:
        # Fall back to base class for other platforms (macOS, BSD, etc.)
        print(f"⚠️  Warning: Unsupported platform '{system}', using base implementation")
        from ui.base.main_window_base import MainWindowBase
        return MainWindowBase


def main():
    """Main entry point for FadCrypt PyQt6 application."""
    
    # Check for --windows flag BEFORE any imports
    mock_windows = '--windows' in sys.argv
    if mock_windows:
        print("🧪 Mock Windows mode enabled - simulating Windows environment on Linux")
        from win_mock import setup_windows_mocks
        setup_windows_mocks()
    
    # Detect platform
    system = platform.system()
    
    # Step 1: Single Instance Check - Prevent multiple instances
    from core.single_instance_manager import check_single_instance
    single_instance = check_single_instance(exit_if_running=True)
    print("🔒 Single instance lock acquired - no other FadCrypt instances running")
    
    # Step 2: Start File Monitor Daemon - Monitors and backs up config files
    from core.file_monitor import start_file_monitor_daemon
    
    # Store reference to prevent garbage collection
    _file_monitor = None
    
    # Create QApplication instance
    app = QApplication(sys.argv)
    app.setApplicationName("FadCrypt")
    app.setApplicationVersion(__version__)
    
    # Note: High DPI scaling is automatic in Qt6, no need to set attributes
    
    # Show splash screen
    from ui.components.splash_screen import FadCryptSplashScreen
    splash = FadCryptSplashScreen(resource_path)
    splash.show_message("Initializing FadCrypt...")
    
    print(f"✅ FadCrypt v{__version__} starting...")
    print(f"🔢 Version Code: {__version_code__}")
    print(f"🎨 UI Framework: PyQt6")
    print(f"💻 Platform: {system}")
    if mock_windows:
        print(f"🧪 Mock Mode: Windows UI on Linux")
    print(f"📁 Project Root: {project_root}")
    
    # Get platform-specific window class
    splash.show_message("Loading platform modules...")
    MainWindowClass = get_main_window_class(force_windows=mock_windows)
    
    # Create main window (but don't show yet)
    splash.show_message("Creating main window...")
    window = MainWindowClass(version=__version__)
    
    # Setup Ctrl+C signal handler for graceful shutdown after window is created
    # This allows us to access window._force_quit flag
    def signal_handler(sig, frame):
        print("\n🛑 Ctrl+C detected - Shutting down gracefully...")
        window._force_quit = True  # Set flag to bypass minimize-to-tray
        QTimer.singleShot(0, app.quit)  # Schedule quit on next event loop iteration
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Make Python check for signals by installing a very low-overhead timer
    # This only wakes up the event loop, doesn't execute heavy code
    signal_check_timer = QTimer()
    signal_check_timer.start(100)  # 100ms is sufficient and barely noticeable
    signal_check_timer.timeout.connect(lambda: None)  # Empty slot - just processes signals
    
    # Close splash and show main window with proper centering
    # Splash will display for 2.5 seconds - quick but visible
    splash.show_message("Starting application...")
    splash.close_splash(window, delay_ms=2500)
    
    # Check for --auto-monitor flag (startup autostart mode)
    auto_monitor_mode = '--auto-monitor' in sys.argv
    
    if auto_monitor_mode:
        print("🚀 Auto-monitor mode detected - will start monitoring automatically (silent mode)")
        # Pass flag to window so it knows to skip dialogs
        window.auto_monitor_mode = True
    else:
        window.auto_monitor_mode = False
    
    # NOW check for crash recovery (after auto_monitor_mode flag is set)
    window.check_crash_recovery()
    
    # Show window after splash closes
    def show_window():
        # In auto-monitor mode, skip showing the UI entirely for silent operation
        if not window.auto_monitor_mode:
            window.show()
            # Re-center after window is fully rendered
            QTimer.singleShot(100, window.center_on_screen)
        
        # Start file monitor for config protection
        # This monitors config files and auto-restores them if deleted
        nonlocal _file_monitor
        _file_monitor = start_file_monitor_daemon(
            config_folder_func=window.get_fadcrypt_folder,
            backup_folder_func=window.get_backup_folder if hasattr(window, 'get_backup_folder') else window.get_fadcrypt_folder
        )
        print("✅ Config file monitor started")
        
        print("✅ FadCrypt started successfully!")
        
        # If --auto-monitor flag is present, start monitoring automatically
        if auto_monitor_mode:
            print("🔄 Starting automatic monitoring...")
            QTimer.singleShot(500, window.on_start_monitoring)  # Start monitoring after 500ms
    
    QTimer.singleShot(2550, show_window)  # Show window 50ms after splash closes
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
