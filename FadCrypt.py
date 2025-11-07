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
import tempfile
import io

# CRITICAL: Force unbuffered output for live progress display in PowerShell/CMD
os.environ['PYTHONUNBUFFERED'] = '1'

# CRITICAL: Force UTF-8 encoding everywhere - MUST be first thing
# This handles all cases: console=True, console=False, packaged app, development
try:
    import codecs
    
    # Try method 1: reconfigure() - works with console=True
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    
    # Method 2: Wrap with TextIOWrapper - works when stdout exists but can't reconfigure
    if sys.stdout is not None and not hasattr(sys.stdout, 'reconfigure'):
        try:
            if hasattr(sys.stdout, 'buffer'):
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except Exception:
            pass
    
    # Method 3: If stdout is None (console=False), create UTF-8 capable streams
    if sys.stdout is None:
        try:
            sys.stdout = open(os.devnull, 'w', encoding='utf-8', errors='replace')
            sys.stderr = open(os.devnull, 'w', encoding='utf-8', errors='replace')
        except Exception:
            pass
            
    # Set console code page to UTF-8 on Windows
    if platform.system() == 'Windows':
        try:
            import subprocess
            subprocess.run(['chcp', '65001'], capture_output=True)
        except Exception:
            pass
            
except Exception:
    pass  # If all else fails, continue anyway

def get_fadcrypt_logs_folder():
    """Get the unified FadCrypt logs folder for the current platform."""
    if platform.system() == 'Windows':
        appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
        logs_dir = os.path.join(appdata, 'FadCrypt', 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        return logs_dir
    else:
        # For Linux, keep using home directory for now
        user_home = os.path.expanduser('~')
        logs_dir = os.path.join(user_home, '.config', 'FadCrypt', 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        return logs_dir

# Save the original working directory before any changes
# This is important for CLI mode to work in user's current directory
# CRITICAL: When launched from PATH, Windows sets CWD to exe location
# We need to get the ACTUAL terminal directory from environment or parent process
def get_actual_terminal_directory():
    """
    Get the actual terminal directory where user ran the command.
    When launched from PATH, os.getcwd() returns exe location, not terminal location.
    """
    # Try to get from environment variable (we'll set this in a wrapper if needed)
    if 'FADCRYPT_LAUNCH_DIR' in os.environ:
        return os.environ['FADCRYPT_LAUNCH_DIR']
    
    # For Windows, try to get parent process (cmd/powershell) working directory
    if platform.system() == 'Windows':
        try:
            import psutil
            # Get parent process (cmd.exe or powershell.exe)
            parent = psutil.Process(os.getppid())
            # Get the current working directory of the parent process
            parent_cwd = parent.cwd()
            return parent_cwd
        except (ImportError, Exception):
            # If psutil not available or fails, fall back to os.getcwd()
            pass
    
    # Fallback to os.getcwd()
    return os.getcwd()

ORIGINAL_CWD = get_actual_terminal_directory()

# Global verbose flag - set to True if --verbose is in sys.argv
VERBOSE_MODE = '--verbose' in sys.argv

# CRITICAL FIX: Ensure working directory is correct for PyInstaller DLL loading
# This fixes CMD/PowerShell working directory mismatch when launched from .lnk shortcuts
if hasattr(sys, '_MEIPASS'):
    # Running from PyInstaller bundle - set cwd to bundle directory for DLL loading
    exe_dir = os.path.dirname(sys.executable)
    os.chdir(exe_dir)
    # Also ensure TMPDIR points to the correct temp location
    os.environ['TMPDIR'] = tempfile.gettempdir()
    os.environ['TEMP'] = tempfile.gettempdir()
    os.environ['TMP'] = tempfile.gettempdir()
    
    # IMPORTANT: Restore working directory immediately for CLI operations
    # Check if this is a CLI operation (not GUI, not installer operations)
    is_cli_operation = (
        '--cli' in sys.argv or 
        '--lock' in sys.argv or 
        '--unlock' in sys.argv or 
        '--list' in sys.argv or 
        '--list-locked' in sys.argv or
        (len(sys.argv) == 1)  # No arguments = TUI mode
    )
    
    is_gui_operation = '--gui' in sys.argv or '--auto-monitor' in sys.argv
    
    # Restore original directory for CLI operations (but not for GUI)
    if is_cli_operation and not is_gui_operation:
        try:
            os.chdir(ORIGINAL_CWD)
        except (OSError, FileNotFoundError):
            # If original directory no longer exists, stay in current directory
            pass


# CRITICAL: Define safe_print and safe_flush BEFORE they're used in CLI handling
def safe_print(*args, **kwargs):
    """Safely print to stdout, handling None or closed streams"""
    try:
        if sys.stdout is not None and hasattr(sys.stdout, 'write'):
            # Try to print normally
            print(*args, **kwargs)
    except (AttributeError, ValueError, OSError, BrokenPipeError):
        # If stdout is broken or None, silently fail - we can't do much else
        pass


def safe_flush(stream=None):
    """Safely flush stdout/stderr even if None or doesn't have flush method"""
    if stream is None:
        stream = sys.stdout
    if stream is not None and hasattr(stream, 'flush'):
        try:
            stream.flush()
        except (AttributeError, ValueError, OSError):
            pass


# NOTE: Installer will perform context menu registration and PATH changes
# Use --register-context to register context menu (this is invoked by installer)
if '--register-context' in sys.argv:
    # SECURITY: Require password UNLESS called with --internal-auth flag
    # The --internal-auth flag is only used by GUI/installer after they've authenticated
    if '--internal-auth' not in sys.argv:
        from colorama import just_fix_windows_console
        just_fix_windows_console()
        from core.cli.colors import print_error
        from core.password_manager import PasswordManager
        from core.cli.password_prompt import PasswordPrompt
        from core.crypto_manager import CryptoManager
        
        # Get config folder
        if platform.system() == "Windows":
            appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
            config_folder = os.path.join(appdata, 'FadCrypt', 'config')
        else:
            config_folder = os.path.join(os.path.expanduser('~'), '.config', 'FadCrypt')
        
        password_file = os.path.join(config_folder, "encrypted_password.bin")
        recovery_codes_file = os.path.join(config_folder, "recovery_codes.json")
        
        crypto_manager = CryptoManager()
        password_manager = PasswordManager(password_file, crypto_manager, recovery_codes_file)
        password_prompt = PasswordPrompt(password_manager)
        
        # Verify password before allowing registration
        if not password_prompt.verify_password():
            print_error("Authentication failed. Context menu registration cancelled.")
            sys.exit(1)
    
    import subprocess
    import platform
    print("[CONTEXT MENU] Registering FadCrypt context menu...", flush=True)
    
    # Log to file for debugging
    try:
        log_file = os.path.join(get_fadcrypt_logs_folder(), 'fadcrypt_register_context.log')
        with open(log_file, 'w') as f:
            f.write(f"[REGISTER-CONTEXT] Started at {os.times()}\n")
            f.write(f"[REGISTER-CONTEXT] Executable: {sys.executable}\n")
            f.write(f"[REGISTER-CONTEXT] Arguments: {sys.argv}\n")
            f.write(f"[REGISTER-CONTEXT] Platform: {platform.system()}\n")
    except Exception as e:
        print(f"[CONTEXT MENU] Could not create log file: {e}", flush=True)
    
    try:
        from core.windows.shell_extension import ContextMenuManager
        manager = ContextMenuManager()
        success = manager.force_register_context_menu()
        
        if success:
            print("[CONTEXT MENU] Registration completed successfully", flush=True)
            with open(log_file, 'a') as f:
                f.write("[REGISTER-CONTEXT] Force registration result: True\n")
            
            # Always restart explorer after registration to ensure context menu takes effect
            print("[CONTEXT MENU] Registration completed, restarting Explorer...", flush=True)
            with open(log_file, 'a') as f:
                f.write("[REGISTER-CONTEXT] Restarting Explorer...\n")
            try:
                subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], 
                             stderr=subprocess.DEVNULL, timeout=5)
                subprocess.Popen('explorer.exe')
                print("[CONTEXT MENU] Explorer restarted successfully", flush=True)
                with open(log_file, 'a') as f:
                    f.write("[REGISTER-CONTEXT] Explorer restarted successfully\n")
            except Exception as e:
                print(f"[CONTEXT MENU] Warning: Could not restart Explorer: {e}", flush=True)
                with open(log_file, 'a') as f:
                    f.write(f"[REGISTER-CONTEXT] Warning: Could not restart Explorer: {e}\n")
        else:
            print("[CONTEXT MENU] Registration failed", flush=True)
            with open(log_file, 'a') as f:
                f.write("[REGISTER-CONTEXT] Registration failed\n")
        
        with open(log_file, 'a') as f:
            f.write(f"[REGISTER-CONTEXT] Completed successfully\n")
            
    except Exception as e:
        print(f"[CONTEXT MENU] Error during registration: {e}", flush=True)
        import traceback
        traceback.print_exc()
        try:
            with open(log_file, 'a') as f:
                f.write(f"[REGISTER-CONTEXT] Error: {e}\n")
                f.write(f"[REGISTER-CONTEXT] Traceback: {traceback.format_exc()}\n")
        except:
            pass
    sys.exit(0)

# Use --unregister-context to unregister context menu (this is invoked by uninstaller)
if '--unregister-context' in sys.argv:
    # SECURITY: Require password UNLESS called with --internal-auth flag
    if '--internal-auth' not in sys.argv:
        from colorama import just_fix_windows_console
        just_fix_windows_console()
        from core.cli.colors import print_error
        from core.password_manager import PasswordManager
        from core.cli.password_prompt import PasswordPrompt
        from core.crypto_manager import CryptoManager
        
        # Get config folder
        if platform.system() == "Windows":
            appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
            config_folder = os.path.join(appdata, 'FadCrypt', 'config')
        else:
            config_folder = os.path.join(os.path.expanduser('~'), '.config', 'FadCrypt')
        
        password_file = os.path.join(config_folder, "encrypted_password.bin")
        recovery_codes_file = os.path.join(config_folder, "recovery_codes.json")
        
        crypto_manager = CryptoManager()
        password_manager = PasswordManager(password_file, crypto_manager, recovery_codes_file)
        password_prompt = PasswordPrompt(password_manager)
        
        # Verify password before allowing unregistration
        if not password_prompt.verify_password():
            print_error("Authentication failed. Context menu unregistration cancelled.")
            sys.exit(1)
    
    import subprocess
    import platform
    print("[CONTEXT MENU] Unregistering FadCrypt context menu...", flush=True)
    
    # Log to file for debugging
    try:
        log_file = os.path.join(get_fadcrypt_logs_folder(), 'fadcrypt_unregister_context.log')
        with open(log_file, 'w') as f:
            f.write(f"[UNREGISTER-CONTEXT] Started at {os.times()}\n")
            f.write(f"[UNREGISTER-CONTEXT] Executable: {sys.executable}\n")
            f.write(f"[UNREGISTER-CONTEXT] Arguments: {sys.argv}\n")
            f.write(f"[UNREGISTER-CONTEXT] Platform: {platform.system()}\n")
    except Exception as e:
        print(f"[CONTEXT MENU] Could not create log file: {e}", flush=True)
    
    try:
        from core.windows.shell_extension import ContextMenuManager
        manager = ContextMenuManager()
        success = manager.unregister_context_menu()
        
        if success:
            print("[CONTEXT MENU] Unregistration completed successfully", flush=True)
            with open(log_file, 'a') as f:
                f.write("[UNREGISTER-CONTEXT] Unregistration result: True\n")
            
            # Always restart explorer after unregistration to ensure context menu changes take effect
            print("[CONTEXT MENU] Unregistration completed, restarting Explorer...", flush=True)
            with open(log_file, 'a') as f:
                f.write("[UNREGISTER-CONTEXT] Restarting Explorer...\n")
            try:
                subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], 
                             stderr=subprocess.DEVNULL, timeout=5)
                subprocess.Popen('explorer.exe')
                print("[CONTEXT MENU] Explorer restarted successfully", flush=True)
                with open(log_file, 'a') as f:
                    f.write("[UNREGISTER-CONTEXT] Explorer restarted successfully\n")
            except Exception as e:
                print(f"[CONTEXT MENU] Warning: Could not restart Explorer: {e}", flush=True)
                with open(log_file, 'a') as f:
                    f.write(f"[UNREGISTER-CONTEXT] Warning: Could not restart Explorer: {e}\n")
        else:
            print("[CONTEXT MENU] Unregistration failed or no entries found", flush=True)
            with open(log_file, 'a') as f:
                f.write("[UNREGISTER-CONTEXT] Unregistration failed or no entries found\n")
        
        with open(log_file, 'a') as f:
            f.write(f"[UNREGISTER-CONTEXT] Completed successfully\n")
            
    except Exception as e:
        print(f"[CONTEXT MENU] Error during unregistration: {e}", flush=True)
        import traceback
        traceback.print_exc()
        try:
            with open(log_file, 'a') as f:
                f.write(f"[UNREGISTER-CONTEXT] Error: {e}\n")
                f.write(f"[UNREGISTER-CONTEXT] Traceback: {traceback.format_exc()}\n")
        except:
            pass
    sys.exit(0)
    try:
        # Log to file for debugging installer issues
        import tempfile
        log_file = os.path.join(tempfile.gettempdir(), 'fadcrypt_register_context.log')
        with open(log_file, 'w') as f:
            f.write(f"[REGISTER-CONTEXT] Started at {os.times()}\n")
            f.write(f"[REGISTER-CONTEXT] Executable: {sys.executable}\n")
            f.write(f"[REGISTER-CONTEXT] Arguments: {sys.argv}\n")
            f.write(f"[REGISTER-CONTEXT] Platform: {platform.system()}\n")
        
        from core.windows.shell_extension import ContextMenuManager
        import subprocess
        manager = ContextMenuManager()
        # Force registration on every install to ensure it's always up to date
        success = manager.force_register_context_menu()
        
        with open(log_file, 'a') as f:
            f.write(f"[REGISTER-CONTEXT] Force registration result: {success}\n")
        
        if success:
            # Always restart explorer after registration to ensure context menu takes effect
            print("[CONTEXT MENU] Registration completed, restarting Explorer...", flush=True)
            with open(log_file, 'a') as f:
                f.write("[REGISTER-CONTEXT] Restarting Explorer...\n")
            try:
                subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], 
                             stderr=subprocess.DEVNULL, timeout=5)
                subprocess.Popen('explorer.exe')
                print("[CONTEXT MENU] Explorer restarted successfully", flush=True)
                with open(log_file, 'a') as f:
                    f.write("[REGISTER-CONTEXT] Explorer restarted successfully\n")
            except Exception as e:
                print(f"[CONTEXT MENU] Warning: Could not restart Explorer: {e}", flush=True)
                with open(log_file, 'a') as f:
                    f.write(f"[REGISTER-CONTEXT] Warning: Could not restart Explorer: {e}\n")
        else:
            print("[CONTEXT MENU] Registration failed", flush=True)
            with open(log_file, 'a') as f:
                f.write("[REGISTER-CONTEXT] Registration failed\n")
        
        with open(log_file, 'a') as f:
            f.write(f"[REGISTER-CONTEXT] Completed successfully\n")
            
    except Exception as e:
        print(f"[CONTEXT MENU] Error during registration: {e}", flush=True)
        import traceback
        traceback.print_exc()
        try:
            with open(log_file, 'a') as f:
                f.write(f"[REGISTER-CONTEXT] Error: {e}\n")
                f.write(f"[REGISTER-CONTEXT] Traceback: {traceback.format_exc()}\n")
        except:
            pass
    sys.exit(0)

# DEV MODE: Test context menu without registry (for development/testing)
# Usage: python FadCrypt.py --test-context-lock <path> [<path2> ...]
#        python FadCrypt.py --test-context-unlock <path> [<path2> ...]
if '--test-context-lock' in sys.argv or '--test-context-unlock' in sys.argv:
    print(f"[DEV MODE] Testing context menu: {sys.argv}", flush=True)
    try:
        if '--test-context-lock' in sys.argv:
            idx = sys.argv.index('--test-context-lock')
            # Get all paths after the flag (filter out other flags)
            paths = [arg for arg in sys.argv[idx + 1:] if not arg.startswith('--')]
            if not paths:
                print(f"[DEV MODE] No paths provided", flush=True)
                sys.exit(1)
            
            if len(paths) == 1:
                # Single file
                print(f"[DEV MODE] Test-locking file: {paths[0]}", flush=True)
                from core.windows.cli_lock_handler import lock_file_with_password
                success, info = lock_file_with_password(paths[0])
                print(f"[DEV MODE] Test-lock result: {success}", flush=True)
            else:
                # Batch operation
                print(f"[DEV MODE] Test-locking {len(paths)} files: {paths}", flush=True)
                from core.windows.cli_lock_handler import lock_multiple_with_password
                success, info = lock_multiple_with_password(paths)
                print(f"[DEV MODE] Test-lock result: {success} - {info['success']}/{len(paths)} succeeded", flush=True)
            
            sys.exit(0 if success else 1)
        
        elif '--test-context-unlock' in sys.argv:
            idx = sys.argv.index('--test-context-unlock')
            # Get all paths after the flag (filter out other flags)
            paths = [arg for arg in sys.argv[idx + 1:] if not arg.startswith('--')]
            if not paths:
                print(f"[DEV MODE] No paths provided", flush=True)
                sys.exit(1)
            
            if len(paths) == 1:
                # Single file
                print(f"[DEV MODE] Test-unlocking file: {paths[0]}", flush=True)
                from core.windows.cli_lock_handler import unlock_file_with_password
                success, info = unlock_file_with_password(paths[0])
                print(f"[DEV MODE] Test-unlock result: {success}", flush=True)
            else:
                # Batch operation
                print(f"[DEV MODE] Test-unlocking {len(paths)} files: {paths}", flush=True)
                from core.windows.cli_lock_handler import unlock_multiple_with_password
                success, info = unlock_multiple_with_password(paths)
                print(f"[DEV MODE] Test-unlock result: {success} - {info['success']}/{len(paths)} succeeded", flush=True)
            
            sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[DEV MODE] Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Handle --context-lock and --context-unlock from context menu
if '--context-lock' in sys.argv or '--context-unlock' in sys.argv:
    safe_print(f"[CONTEXT MENU] Processing context menu arguments: {sys.argv}")
    try:
        if '--context-lock' in sys.argv:
            idx = sys.argv.index('--context-lock')
            if idx + 1 < len(sys.argv):
                # Get all paths after --context-lock (support batch operations)
                paths = [arg for arg in sys.argv[idx + 1:] if not arg.startswith('--')]
                if not paths:
                    safe_print(f"[CONTEXT MENU] No paths provided")
                    sys.exit(1)
                
                safe_print(f"[CONTEXT MENU] Locking {len(paths)} item(s): {paths}")
                from core.windows.cli_lock_handler import lock_multiple_with_password
                success, info = lock_multiple_with_password(paths)
                safe_print(f"[CONTEXT MENU] Lock result: {success}")
                sys.exit(0 if success else 1)
        
        elif '--context-unlock' in sys.argv:
            idx = sys.argv.index('--context-unlock')
            if idx + 1 < len(sys.argv):
                # Get all paths after --context-unlock (support batch operations)
                paths = [arg for arg in sys.argv[idx + 1:] if not arg.startswith('--')]
                if not paths:
                    safe_print(f"[CONTEXT MENU] No paths provided")
                    sys.exit(1)
                
                safe_print(f"[CONTEXT MENU] Unlocking {len(paths)} item(s): {paths}")
                from core.windows.cli_lock_handler import unlock_multiple_with_password
                success, info = unlock_multiple_with_password(paths)
                safe_print(f"[CONTEXT MENU] Unlock result: {success}")
                sys.exit(0 if success else 1)
    except Exception as e:
        safe_print(f"[CLI] Error: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr if sys.stderr is not None else None)
        sys.exit(1)

if '--cleanup' in sys.argv:
    # SECURITY: Require password UNLESS called with --internal-auth flag
    if '--internal-auth' not in sys.argv:
        from colorama import just_fix_windows_console
        just_fix_windows_console()
        from core.cli.colors import print_error
        from core.password_manager import PasswordManager
        from core.cli.password_prompt import PasswordPrompt
        from core.crypto_manager import CryptoManager
        
        # Get config folder
        if platform.system() == "Windows":
            appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
            config_folder = os.path.join(appdata, 'FadCrypt', 'config')
        else:
            config_folder = os.path.join(os.path.expanduser('~'), '.config', 'FadCrypt')
        
        password_file = os.path.join(config_folder, "encrypted_password.bin")
        recovery_codes_file = os.path.join(config_folder, "recovery_codes.json")
        
        crypto_manager = CryptoManager()
        password_manager = PasswordManager(password_file, crypto_manager, recovery_codes_file)
        password_prompt = PasswordPrompt(password_manager)
        
        # Verify password before allowing cleanup
        if not password_prompt.verify_password():
            print_error("Authentication failed. Cleanup operation cancelled.")
            sys.exit(1)
    
    import subprocess
    import platform
    print("[CLEANUP] Starting FadCrypt cleanup...", flush=True)
    
    # Log to file for debugging uninstall issues
    try:
        log_file = os.path.join(get_fadcrypt_logs_folder(), 'fadcrypt_cleanup.log')
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
                            print("[CLEANUP] [OK] Removed immutable flags", flush=True)
                        else:
                            print("[CLEANUP] [WARN] Could not remove immutable flags via chattr", flush=True)
                            print(f"[CLEANUP]     Note: Daemon will handle cleanup when service stops", flush=True)
                    except Exception as e:
                        print("[CLEANUP] [WARN] Warning: Could not remove immutable flags: {e}", flush=True)
            
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
                        print(f"[CLEANUP] OK Removed: {folder}", flush=True)
                    except Exception as e:
                        print(f"[CLEANUP] WARN Warning: Could not remove {folder}: {e}", flush=True)
            
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
                    print(f"[CLEANUP] OK Restored {len(tools_to_restore)} tools", flush=True)
                else:
                    print(f"[CLEANUP] WARN Warning: {result.stderr}", flush=True)
            else:
                print("[CLEANUP] No disabled tools found", flush=True)
            
            # Remove lock file if it exists
            lock_file = '/tmp/fadcrypt.lock'
            if os.path.exists(lock_file):
                try:
                    os.remove(lock_file)
                    print("[CLEANUP] [OK] Removed lock file: {lock_file}", flush=True)
                except PermissionError:
                    # Lock file might be owned by different user - cleanup script runs as root
                    try:
                        subprocess.run(['rm', '-f', lock_file], check=True)
                        print(f"[CLEANUP] OK Removed lock file: {lock_file}", flush=True)
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
                        print("[CLEANUP] [INFO] PATH is empty", flush=True)
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
                                print("[CLEANUP] OK Removed FadCrypt from PATH", flush=True)
                            else:
                                print("[CLEANUP] INFO FadCrypt directory not found in PATH", flush=True)
                        else:
                            print("[CLEANUP] INFO Not running from PyInstaller bundle, skipping PATH removal", flush=True)
                except FileNotFoundError:
                    print("[CLEANUP] INFO PATH environment variable not found", flush=True)
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
                        print("[CLEANUP] [OK] Notified system of PATH change", flush=True)
                except Exception as e:
                    print("[CLEANUP] [INFO] Could not notify system of PATH change: {e}", flush=True)
                    
            except Exception as e:
                print(f"[CLEANUP] Warning: Could not remove from PATH: {e}", flush=True)
            
            # Registry keys that FadCrypt may have disabled
            # Note: These are set in HKEY_USERS\{user_sid}, so we need to find the current user's SID
            import win32security
            import win32api
            import win32con
            
            try:
                token = win32security.OpenProcessToken(win32api.GetCurrentProcess(), win32con.TOKEN_QUERY)
                user_sid = win32security.GetTokenInformation(token, win32security.TokenUser)[0]
                user_sid_str = win32security.ConvertSidToStringSid(user_sid)
                win32api.CloseHandle(token)
                
                keys_to_restore = [
                    # Note: CMD is not managed by system tools anymore
                    (r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 'DisableTaskMgr'),
                    (r'Software\Microsoft\Windows\CurrentVersion\Policies\Explorer', 'NoControlPanel'),
                    (r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 'DisableRegistryTools')
                ]
                
                restored_count = 0
                for reg_path, value_name in keys_to_restore:
                    try:
                        full_reg_path = f"{user_sid_str}\\{reg_path}"
                        key = winreg.OpenKey(winreg.HKEY_USERS, full_reg_path, 0, winreg.KEY_SET_VALUE)
                        try:
                            winreg.DeleteValue(key, value_name)
                            restored_count += 1
                            print(f"[CLEANUP] Restored: {value_name}", flush=True)
                        except FileNotFoundError:
                            pass  # Value doesn't exist
                        finally:
                            winreg.CloseKey(key)
                    except FileNotFoundError:
                        pass  # Key doesn't exist
                    except Exception as e:
                        print(f"[CLEANUP] Warning: Could not restore {value_name}: {e}", flush=True)
                        
            except Exception as e:
                print(f"[CLEANUP] Warning: Could not get user SID for registry cleanup: {e}", flush=True)
            
            # Remove FadCrypt context menu entries
            print("[CLEANUP] Removing FadCrypt context menu entries...", flush=True)
            try:
                from core.windows.shell_extension import ContextMenuManager
                manager = ContextMenuManager()
                if manager.unregister_context_menu():
                    print("[CLEANUP] [OK] Removed context menu entries", flush=True)
                    # Restart File Explorer to clear context menu cache
                    print("[CLEANUP] Restarting File Explorer to clear context menu cache...", flush=True)
                    try:
                        # Kill explorer and restart it properly
                        subprocess.run(['taskkill.exe', '/f', '/im', 'explorer.exe'], 
                                     capture_output=True, timeout=5)
                        # Give it a moment to fully terminate
                        import time
                        time.sleep(1)
                        # Start explorer again (don't wait for it since it's long-running)
                        subprocess.Popen(['explorer.exe'])
                        print("[CLEANUP] [OK] File Explorer restarted (context menu cache cleared)", flush=True)
                    except Exception as e:
                        print(f"[CLEANUP] WARNING: Could not restart File Explorer: {e}", flush=True)
                        print("[CLEANUP] INFO: Context menu changes will take effect on next login", flush=True)
                else:
                    print("[CLEANUP] [INFO] No context menu entries found to remove", flush=True)
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
            
            print(f"[CLEANUP] OK Restored {restored_count} Windows settings", flush=True)
            
            # Remove FadCrypt data directories
            print("[CLEANUP] Removing FadCrypt data directories...", flush=True)
            import shutil
            
            # Get standard Windows directories
            appdata = os.environ.get('APPDATA', '')
            local_appdata = os.environ.get('LOCALAPPDATA', '')
            programdata = os.environ.get('PROGRAMDATA', '')
            
            data_dirs_to_remove = []
            if appdata:
                data_dirs_to_remove.append(os.path.join(appdata, 'FadCrypt'))
            if local_appdata:
                data_dirs_to_remove.append(os.path.join(local_appdata, 'FadCrypt'))
            if programdata:
                data_dirs_to_remove.append(os.path.join(programdata, 'FadCrypt'))
            
            removed_count = 0
            for data_dir in data_dirs_to_remove:
                if os.path.exists(data_dir):
                    try:
                        shutil.rmtree(data_dir)
                        print("[CLEANUP] [OK] Removed data directory: {data_dir}", flush=True)
                        removed_count += 1
                    except Exception as e:
                        print("[CLEANUP] [WARN] Warning: Could not remove {data_dir}: {e}", flush=True)
            
            if removed_count > 0:
                print("[CLEANUP] [OK] Removed {removed_count} data directories", flush=True)
            else:
                print("[CLEANUP] [INFO] No data directories found to remove", flush=True)
            
            # Note: File Explorer restart not needed for context menu changes to take effect
            print("[CLEANUP] INFO: Context menu changes will take effect on next File Explorer restart", flush=True)
        
        print("[CLEANUP] OK: Cleanup completed successfully", flush=True)
        
        # Log completion
        try:
            log_file = os.path.join(get_fadcrypt_logs_folder(), 'fadcrypt_cleanup.log')
            with open(log_file, 'a') as f:
                f.write(f"[CLEANUP] Completed successfully at {os.times()}\n")
        except:
            pass
            
        sys.exit(0)
        
    except Exception as e:
        print(f"[CLEANUP] ERROR Error during cleanup: {e}", flush=True)
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

# Handle --install-service and --uninstall-service flags (called by installer)
if '--install-service' in sys.argv:
    # SECURITY: Require password UNLESS called with --internal-auth flag
    if '--internal-auth' not in sys.argv:
        from colorama import just_fix_windows_console
        just_fix_windows_console()
        from core.cli.colors import print_error
        from core.password_manager import PasswordManager
        from core.cli.password_prompt import PasswordPrompt
        from core.crypto_manager import CryptoManager
        
        # Get config folder
        if platform.system() == "Windows":
            appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
            config_folder = os.path.join(appdata, 'FadCrypt', 'config')
        else:
            config_folder = os.path.join(os.path.expanduser('~'), '.config', 'FadCrypt')
        
        password_file = os.path.join(config_folder, "encrypted_password.bin")
        recovery_codes_file = os.path.join(config_folder, "recovery_codes.json")
        
        crypto_manager = CryptoManager()
        password_manager = PasswordManager(password_file, crypto_manager, recovery_codes_file)
        password_prompt = PasswordPrompt(password_manager)
        
        # Verify password before allowing service installation
        if not password_prompt.verify_password():
            print_error("Authentication failed. Service installation cancelled.")
            sys.exit(1)
    
    # Create log file for service installation
    import tempfile
    log_file = os.path.join(get_fadcrypt_logs_folder(), 'fadcrypt_service_install.log')
    
    def log_message(message):
        print(message, flush=True)
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{message}\n")
        except Exception as e:
            print(f"Failed to write to log file: {e}", flush=True)
    
    log_message("[SERVICE] Installing FadCrypt elevated service...")
    
    try:
        # Log the current environment for debugging
        log_message(f"[SERVICE] Current working directory: {os.getcwd()}")
        log_message(f"[SERVICE] Executable: {sys.executable}")
        log_message(f"[SERVICE] Script location: {__file__}")
        log_message(f"[SERVICE] Log file: {log_file}")
        
        # Try to import and install the service directly
        try:
            from core.windows.fadcrypt_elevated_service import install_service, start_service
            log_message("[SERVICE] Successfully imported service functions")
            
            if install_service():
                log_message("[SERVICE] Service installed successfully")
                if start_service():
                    log_message("[SERVICE] Service started successfully")
                    sys.exit(0)
                else:
                    log_message("[SERVICE] Service installed but failed to start")
                    sys.exit(1)
            else:
                log_message("[SERVICE] Failed to install service")
                sys.exit(1)
                
        except ImportError as e:
            log_message(f"[SERVICE] Failed to import service functions: {e}")
            log_message("[SERVICE] Falling back to subprocess approach")
            
            # Fallback: Run the service installation as a subprocess
            service_script = os.path.join(project_root, 'core', 'windows', 'fadcrypt_elevated_service.py')
            log_message(f"[SERVICE] Service script path: {service_script}")
            log_message(f"[SERVICE] Service script exists: {os.path.exists(service_script)}")
            
            import subprocess
            result = subprocess.run([sys.executable, service_script, 'install'], 
                                  capture_output=True, text=True, cwd=str(project_root))
            
            log_message(f"[SERVICE] Install command exit code: {result.returncode}")
            log_message(f"[SERVICE] Install stdout: {result.stdout}")
            log_message(f"[SERVICE] Install stderr: {result.stderr}")
            
            if result.returncode == 0:
                log_message("[SERVICE] Service installed successfully (subprocess)")
                # Try to start the service
                start_result = subprocess.run([sys.executable, service_script, 'start'], 
                                            capture_output=True, text=True, cwd=str(project_root))
                
                log_message(f"[SERVICE] Start command exit code: {start_result.returncode}")
                log_message(f"[SERVICE] Start stdout: {start_result.stdout}")
                log_message(f"[SERVICE] Start stderr: {start_result.stderr}")
                
                if start_result.returncode == 0:
                    log_message("[SERVICE] Service started successfully (subprocess)")
                    sys.exit(0)
                else:
                    log_message("[SERVICE] Service installed but failed to start (subprocess)")
                    sys.exit(1)
            else:
                log_message("[SERVICE] Failed to install service (subprocess)")
                sys.exit(1)

    except Exception as e:
        log_message(f"[SERVICE] Error installing service: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if '--uninstall-service' in sys.argv:
    # SECURITY: Require password UNLESS called with --internal-auth flag
    if '--internal-auth' not in sys.argv:
        from colorama import just_fix_windows_console
        just_fix_windows_console()
        from core.cli.colors import print_error
        from core.password_manager import PasswordManager
        from core.cli.password_prompt import PasswordPrompt
        from core.crypto_manager import CryptoManager
        
        # Get config folder
        if platform.system() == "Windows":
            appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
            config_folder = os.path.join(appdata, 'FadCrypt', 'config')
        else:
            config_folder = os.path.join(os.path.expanduser('~'), '.config', 'FadCrypt')
        
        password_file = os.path.join(config_folder, "encrypted_password.bin")
        recovery_codes_file = os.path.join(config_folder, "recovery_codes.json")
        
        crypto_manager = CryptoManager()
        password_manager = PasswordManager(password_file, crypto_manager, recovery_codes_file)
        password_prompt = PasswordPrompt(password_manager)
        
        # Verify password before allowing service uninstallation
        if not password_prompt.verify_password():
            print_error("Authentication failed. Service uninstallation cancelled.")
            sys.exit(1)
    
    # Create log file for service uninstallation
    import tempfile
    log_file = os.path.join(get_fadcrypt_logs_folder(), 'fadcrypt_service_uninstall.log')
    
    def log_message(message):
        print(message, flush=True)
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{message}\n")
        except Exception as e:
            print(f"Failed to write to log file: {e}", flush=True)
    
    log_message("[SERVICE] Uninstalling FadCrypt elevated service...")
    
    try:
        # Try to import and uninstall the service directly
        try:
            from core.windows.fadcrypt_elevated_service import uninstall_service, stop_service
            log_message("[SERVICE] Successfully imported service functions")
            
            if stop_service():
                log_message("[SERVICE] Service stopped successfully")
            else:
                log_message("[SERVICE] Warning: Could not stop service")
            
            if uninstall_service():
                log_message("[SERVICE] Service uninstalled successfully")
                sys.exit(0)
            else:
                log_message("[SERVICE] Failed to uninstall service")
                sys.exit(1)
                
        except ImportError as e:
            log_message(f"[SERVICE] Failed to import service functions: {e}")
            log_message("[SERVICE] Falling back to subprocess approach")
            
            # Fallback: Run the service uninstallation as a subprocess
            service_script = os.path.join(project_root, 'core', 'windows', 'fadcrypt_elevated_service.py')
            log_message(f"[SERVICE] Service script path: {service_script}")
            log_message(f"[SERVICE] Service script exists: {os.path.exists(service_script)}")
            
            import subprocess
            # Try to stop the service first
            stop_result = subprocess.run([sys.executable, service_script, 'stop'], 
                                       capture_output=True, text=True, cwd=str(project_root))
            
            log_message(f"[SERVICE] Stop command exit code: {stop_result.returncode}")
            log_message(f"[SERVICE] Stop stdout: {stop_result.stdout}")
            log_message(f"[SERVICE] Stop stderr: {stop_result.stderr}")
            
            if stop_result.returncode == 0:
                log_message("[SERVICE] Service stopped successfully (subprocess)")
            else:
                log_message("[SERVICE] Warning: Could not stop service (subprocess)")
            
            # Uninstall the service
            result = subprocess.run([sys.executable, service_script, 'uninstall'], 
                                  capture_output=True, text=True, cwd=str(project_root))
            
            log_message(f"[SERVICE] Uninstall command exit code: {result.returncode}")
            log_message(f"[SERVICE] Uninstall stdout: {result.stdout}")
            log_message(f"[SERVICE] Uninstall stderr: {result.stderr}")
            
            if result.returncode == 0:
                log_message("[SERVICE] Service uninstalled successfully (subprocess)")
                sys.exit(0)
            else:
                log_message("[SERVICE] Failed to uninstall service (subprocess)")
                sys.exit(1)

    except Exception as e:
        log_message(f"[SERVICE] Error uninstalling service: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if '--run-service' in sys.argv:
    try:
        from core.windows.fadcrypt_elevated_service import FadCryptElevatedService
        import servicemanager
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(FadCryptElevatedService)
        servicemanager.StartServiceCtrlDispatcher()
    except Exception as e:
        print(f"Failed to run service: {e}")
        sys.exit(1)

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt, QTimer
except ImportError as e:
    print("❌ PyQt6 is not installed!")
    print("📦 Install with: pip install PyQt6")
    print(f"   Error: {e}")
    sys.exit(1)

from core.version import __version__, __version_code__


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


def launch_tui():
    """Launch the Text User Interface (TUI)"""
    try:
        # Initialize colorama for Windows
        from colorama import just_fix_windows_console
        just_fix_windows_console()
        
        # Debug: Print launch info
        if VERBOSE_MODE:
            safe_print("[TUI] Launching TUI mode...")
            safe_print(f"[TUI] stdout is None: {sys.stdout is None}")
            safe_print(f"[TUI] stdin is None: {sys.stdin is None}")
            safe_print(f"[TUI] stderr is None: {sys.stderr is None}")
        
        # Get platform-specific paths
        system = platform.system()
        
        if system == "Windows":
            appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
            config_folder = os.path.join(appdata, 'FadCrypt', 'config')
        else:
            config_folder = os.path.join(os.path.expanduser('~'), '.config', 'FadCrypt')
        
        os.makedirs(config_folder, exist_ok=True)
        
        # Initialize password manager
        from core.crypto_manager import CryptoManager
        from core.password_manager import PasswordManager
        
        password_file = os.path.join(config_folder, "encrypted_password.bin")
        recovery_codes_file = os.path.join(config_folder, "recovery_codes.json")
        
        crypto_manager = CryptoManager()
        password_manager = PasswordManager(password_file, crypto_manager, recovery_codes_file)
        
        # Inform user that CLI/TUI is starting (helps when launched from explorer/context menu)
        try:
            print("🔐 FadCrypt CLI starting...")
            sys.stdout.flush()
        except Exception:
            pass

        # Verify password before launching TUI
        from core.cli.password_prompt import PasswordPrompt
        password_prompt = PasswordPrompt(password_manager)
        
        # Ensure password exists
        if not password_prompt.ensure_password_exists():
            from core.cli.colors import print_error
            print_error("Cannot proceed without a master password.")
            return
        
        # Verify password (with recovery option)
        if not password_prompt.verify_password_with_recovery():
            from core.cli.colors import print_error
            print_error("Authentication failed.")
            return
        
        # Clear screen after successful authentication
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Initialize CLI handler
        if system == "Windows":
            from core.cli.cli_handler_windows import CLIHandlerWindows
            cli_handler = CLIHandlerWindows(config_folder)
        else:
            from core.cli.cli_handler_linux import CLIHandlerLinux
            cli_handler = CLIHandlerLinux(config_folder)
        
        # Launch TUI
        from core.cli.tui_manager import TUIManager
        tui = TUIManager(password_manager, cli_handler)
        tui.run()
        
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


def is_installer_operation():
    """
    Check if this is a legitimate installer/uninstaller operation.
    These operations should only be callable by the installer, not by users.
    """
    INSTALLER_OPERATIONS = [
        '--register-context',
        '--unregister-context',
        '--cleanup',
        '--install-service',
        '--uninstall-service',
        '--run-service'
    ]
    
    # Check if any installer operation is present
    for arg in sys.argv:
        if arg in INSTALLER_OPERATIONS:
            # These operations are already handled early in the script
            # before this function is called, so this is just a safety check
            return True
    
    return False


def requires_password_protection():
    """
    Check if current command requires password protection.
    
    Returns True if password is needed, False for public/system operations.
    """
    # Public operations that don't need password
    PUBLIC_OPERATIONS = [
        '--help',
        '-h',
        '--version',
        '-v'
    ]
    
    # Operations with their own authentication
    OWN_AUTH_OPERATIONS = [
        '--gui',                   # GUI has own auth system
        '--context-lock',          # Context menu has own auth
        '--context-unlock'         # Context menu has own auth
    ]
    
    # Check if any public or own-auth operation is present
    for arg in sys.argv:
        if arg in PUBLIC_OPERATIONS or arg in OWN_AUTH_OPERATIONS:
            return False
    
    # All other CLI commands need password protection
    return True


def setup_console_encoding():
    """Setup UTF-8 encoding for console output, handling None stdout/stderr gracefully"""
    import io
    import sys
    
    # Only set UTF-8 if stdout/stderr exist and buffer is available
    if sys.stdout is not None and hasattr(sys.stdout, 'buffer') and sys.stdout.buffer is not None:
        if getattr(sys.stdout, 'encoding', None) != 'utf-8':
            try:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            except (AttributeError, ValueError):
                pass  # Fallback if wrapping fails
    
    if sys.stderr is not None and hasattr(sys.stderr, 'buffer') and sys.stderr.buffer is not None:
        if getattr(sys.stderr, 'encoding', None) != 'utf-8':
            try:
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
            except (AttributeError, ValueError):
                pass  # Fallback if wrapping fails

def handle_direct_cli_commands():
    """Handle direct CLI commands like --lock, --unlock, --list with password protection"""
    import sys
    import os
    
    # CRITICAL: Restore stdin/stdout/stderr if console=False in spec
    # Without these, print() and other I/O operations will fail
    if sys.stdout is None or sys.stdin is None or sys.stderr is None:
        # Reopen standard streams for console I/O (for when running with console=False)
        sys.stdin = open(os.devnull, 'r')
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        # On Windows, try to use a real console if available
        if os.name == 'nt':
            try:
                import ctypes
                ctypes.windll.kernel32.AllocConsole()
                # Redirect to the new console
                sys.stdout = open('CON:', 'w')
                sys.stdin = open('CON:', 'r')
                sys.stderr = open('CON:', 'w')
            except:
                pass  # Fall back to os.devnull
    
    # Setup console encoding safely
    setup_console_encoding()
    
    from colorama import just_fix_windows_console
    just_fix_windows_console()
    
    from core.cli.colors import print_success, print_error, print_info, print_colored, Colors, BoxChars
    
    # Get platform-specific paths
    system = platform.system()
    
    if system == "Windows":
        appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
        config_folder = os.path.join(appdata, 'FadCrypt', 'config')
    else:
        config_folder = os.path.join(os.path.expanduser('~'), '.config', 'FadCrypt')
    
    os.makedirs(config_folder, exist_ok=True)
    
    # Initialize password manager
    from core.crypto_manager import CryptoManager
    from core.password_manager import PasswordManager
    from core.cli.password_prompt import PasswordPrompt
    
    password_file = os.path.join(config_folder, "encrypted_password.bin")
    recovery_codes_file = os.path.join(config_folder, "recovery_codes.json")
    
    crypto_manager = CryptoManager()
    password_manager = PasswordManager(password_file, crypto_manager, recovery_codes_file)
    password_prompt = PasswordPrompt(password_manager)
    
    # Initialize CLI handler
    if system == "Windows":
        from core.cli.cli_handler_windows import CLIHandlerWindows
        cli_handler = CLIHandlerWindows(config_folder)
    else:
        from core.cli.cli_handler_linux import CLIHandlerLinux
        cli_handler = CLIHandlerLinux(config_folder)
    
    # EARLY PATH VALIDATION: Check paths before password authentication
    # This prevents prompting for password when paths are invalid
    if '--lock' in sys.argv:
        idx = sys.argv.index('--lock')
        if idx + 1 < len(sys.argv):
            paths = [arg for arg in sys.argv[idx + 1:] if not arg.startswith('--')]
            if paths:
                # Validate all paths exist before proceeding
                invalid_paths = []
                for path in paths:
                    if not cli_handler.validate_path(path):
                        invalid_paths.append(path)
                
                if invalid_paths:
                    print_error("Cannot proceed - the following paths are invalid:")
                    for path in invalid_paths:
                        print_error(f"   {path}: Path does not exist or is not accessible")
                    return False
    elif '--unlock' in sys.argv:
        idx = sys.argv.index('--unlock')
        if idx + 1 < len(sys.argv):
            paths = [arg for arg in sys.argv[idx + 1:] if not arg.startswith('--')]
            if paths:
                # EARLY VALIDATION: Check if paths exist and determine if any are actually locked
                # Only prompt for password if there are locked items
                valid_paths = []
                invalid_paths = []  # Paths that don't exist
                unlocked_paths = []  # Paths that exist but are not locked
                suggested_paths = []  # For when user tries to unlock original file that's been encrypted
                
                locked_items = cli_handler.file_lock_manager.get_locked_items()
                locked_items_paths = [item['path'] for item in locked_items]
                
                for path in paths:
                    abs_path = os.path.abspath(path)
                    
                    # Check various scenarios for unlock
                    path_exists = cli_handler.validate_path(path)
                    if path_exists:
                        # Path exists - check if it's locked
                        is_locked = abs_path in locked_items_paths
                        if not is_locked and abs_path.endswith('.fadcrypt'):
                            # Check if original path is locked
                            original_path = os.path.splitext(abs_path)[0]  # Remove .fadcrypt extension
                            original_path = os.path.normpath(original_path)
                            locked_items_paths_normalized = [os.path.normpath(p) for p in locked_items_paths]
                            is_locked = original_path in locked_items_paths_normalized
                        
                        if is_locked:
                            valid_paths.append(path)
                        else:
                            unlocked_paths.append(path)  # Exists but not locked
                    else:
                        # Path doesn't exist - check if it's an original file that was encrypted
                        if abs_path in locked_items_paths:
                            # Original file is locked, check if .fadcrypt file exists
                            fadcrypt_path = abs_path + '.fadcrypt'
                            if os.path.exists(fadcrypt_path):
                                # Auto-map to .fadcrypt file and unlock it
                                valid_paths.append(fadcrypt_path)
                            else:
                                invalid_paths.append(path)  # Locked but .fadcrypt file missing
                        else:
                            invalid_paths.append(path)  # Truly doesn't exist
                
                # Check which valid paths are actually locked (already done above)
                locked_paths = valid_paths
                
                # If there are invalid paths or no locked paths, handle without calling CLI handler
                if invalid_paths or suggested_paths or unlocked_paths or not locked_paths:
                    print_colored(f"🔐 Unlocking {len(paths)} item(s)...\n", Colors.INFO)
                    safe_flush()
                    
                    # Build error messages
                    error_messages = []
                    if invalid_paths:
                        for path in invalid_paths:
                            abs_path = os.path.abspath(path)
                            if abs_path in locked_items_paths:
                                # File is locked but .fadcrypt file is missing
                                error_messages.append(f"{path}: Locked item file is missing (expected {path}.fadcrypt)")
                            else:
                                error_messages.append(f"{path}: File or folder does not exist")
                    
                    if suggested_paths:
                        for original_path, fadcrypt_path in suggested_paths:
                            error_messages.append(f"{original_path}: File was locked, use: fadcrypt --unlock {os.path.basename(fadcrypt_path)}")
                    
                    if unlocked_paths:
                        error_messages.extend([f"{path}: Item is not locked: {os.path.basename(path)}" for path in unlocked_paths])
                    
                    # Show errors
                    if error_messages:
                        print_error(f"Failed to unlock {len(error_messages)} item(s):")
                        for error_msg in error_messages:
                            print_error(f"   {error_msg}")
                        safe_flush()
                    
                    return True
                else:
                    # There are locked items, proceed with normal password verification
                    pass  # Fall through to normal processing
    
    # Only require password for user-facing commands (not system operations)
    if requires_password_protection():
        # Ensure password exists
        if not password_prompt.ensure_password_exists():
            print_error("Cannot proceed without a master password.")
            return False
        
        # Verify password for all operations (with recovery option)
        if not password_prompt.verify_password_with_recovery():
            print_error("Authentication failed.")
            return False
        
        # Get the cached password and set it in cli_handler so we don't prompt again
        cached_password = password_manager.get_password_bytes()
        if cached_password and hasattr(cli_handler, 'file_lock_manager') and cli_handler.file_lock_manager:
            cli_handler.file_lock_manager.set_password(cached_password)
        
        # Clear screen after successful authentication
        os.system('cls' if os.name == 'nt' else 'clear')
        safe_flush()
        safe_flush(sys.stderr)
    
    # Handle --lock
    if '--lock' in sys.argv:
        idx = sys.argv.index('--lock')
        if idx + 1 < len(sys.argv):
            # Get paths, but filter out flags (things starting with --)
            paths = [arg for arg in sys.argv[idx + 1:] if not arg.startswith('--')]
            
            if not paths:
                print_error("Usage: fadcrypt --lock <path1> [path2] ...")
                return False
            
            # Setup UTF-8 encoding for emoji display
            setup_console_encoding()
            
            print_colored(f"🔒 Locking {len(paths)} item(s)...\n", Colors.INFO)
            safe_flush()
            
            success, failed, successful_paths, error_messages = cli_handler.lock_multiple(paths)
            
            if success > 0:
                print_success(f"Successfully locked {success} item(s)!")
                print()
                print_colored("🔒 Items are now protected. To unlock later, use:", Colors.INFO)
                for path in successful_paths:
                    item_name = os.path.basename(path)
                    print_colored(f"   fadcrypt --unlock {item_name}", Colors.SUCCESS)
                print()
                safe_flush()
            
            if failed > 0:
                print_error(f"Failed to lock {failed} item(s).")
                if error_messages:
                    print_colored("Error details:", Colors.ERROR)
                    for error_msg in error_messages:
                        print_colored(f"   {error_msg}", Colors.ERROR)
                safe_flush()
            
            return True
        else:
            print_error("Usage: fadcrypt --lock <path1> [path2] ...")

            return False
    
    # Handle --unlock
    elif '--unlock' in sys.argv:
        idx = sys.argv.index('--unlock')
        if idx + 1 < len(sys.argv):
            # Get paths, but filter out flags (things starting with --)
            paths = [arg for arg in sys.argv[idx + 1:] if not arg.startswith('--')]
            
            if not paths:
                print_error("Usage: fadcrypt --unlock <path1> [path2] ...")
                return False
            
            # Setup UTF-8 encoding for emoji display
            setup_console_encoding()
            
            print_colored(f"🔐 Unlocking {len(paths)} item(s)...\n", Colors.INFO)
            safe_flush()
            
            success, failed, successful_paths, error_messages = cli_handler.unlock_multiple(paths)
            
            if success > 0:
                print_success(f"Successfully unlocked {success} item(s)!")
                print()
                print_colored("🔓 Items are now accessible at their original locations:", Colors.INFO)
                for path in successful_paths:
                    # Remove .fadcrypt extension for display since files are restored to original names
                    item_name = os.path.basename(path)
                    if item_name.endswith('.fadcrypt'):
                        item_name = item_name[:-10]  # Remove '.fadcrypt' (10 characters)
                    print_colored(f"   📁 {item_name}", Colors.SUCCESS)
                print()
                print_colored("🔒 To lock these items again later, use:", Colors.INFO)
                for path in successful_paths:
                    # Remove .fadcrypt extension for display since files are restored to original names
                    item_name = os.path.basename(path)
                    if item_name.endswith('.fadcrypt'):
                        item_name = item_name[:-10]  # Remove '.fadcrypt' (10 characters)
                    print_colored(f"   fadcrypt --lock {item_name}", Colors.SUCCESS)
                print()
                safe_flush()
            if failed > 0:
                print_error(f"Failed to unlock {failed} item(s):")
                for error_msg in error_messages:
                    print_error(f"   {error_msg}")
                safe_flush()
            
            return True
        else:
            print_error("Usage: fadcrypt --unlock <path1> [path2] ...")
            return False
    
    # Handle --list (or --list-locked for backwards compatibility)
    elif '--list' in sys.argv or '--list-locked' in sys.argv:
        from datetime import datetime
        locked_items = cli_handler.list_locked_items()
        
        if not locked_items:
            print_info("No locked items found.")
        else:
            # Show header with first item directory (matching TUI design)
            from FadCrypt import __version__
            print(f"\n{Colors.BORDER}╭─ 🏴 {Colors.TITLE}FadCrypt v{__version__}{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET} {Colors.TEXT}File, Folder & Application Protection Suite{Colors.RESET}")
            # Show current working directory
            current_folder = os.getcwd()
            print(f"{Colors.BORDER}│{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET} {Colors.INFO}Current Folder:{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET} {Colors.DIM}{current_folder}{Colors.RESET}")
            print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}\n")
            
            # Display items
            print(f"{Colors.BORDER}╭─ 📋 {Colors.TITLE}Items{Colors.RESET}")
            
            for item in locked_items:
                icon = '📁' if item['type'] == 'folder' else '📄'
                name = item['name']
                
                # Get file info
                try:
                    path = item['path']
                    if os.path.exists(path):
                        stat_info = os.stat(path)
                        size_mb = stat_info.st_size / (1024 * 1024)
                        modified_time = datetime.fromtimestamp(stat_info.st_mtime)
                        modified_str = modified_time.strftime("%d-%b-%Y %I:%M %p")
                        
                        if item['type'] == 'folder':
                            size_display = "" if size_mb == 0 else f"{size_mb:6.2f}MB"
                        else:
                            size_display = f"{max(0.01, size_mb):6.2f}MB"
                    else:
                        size_display = "N/A"
                        modified_str = "N/A"
                except:
                    size_display = "N/A"
                    modified_str = "N/A"
                
                # Display item with size and date
                item_type = item['type'].capitalize()
                size_date = f"{size_display:>8}  {modified_str}" if size_display != "N/A" else modified_str
                print(f"{Colors.BORDER}│{Colors.RESET} {icon} {Colors.DIM}{item_type:<6}{Colors.RESET} {Colors.TEXT}{name:<40}{Colors.RESET} {Colors.DIM}{size_date}{Colors.RESET}")
            
            print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}")
            print(f"\n{Colors.INFO}Total: {len(locked_items)} item(s){Colors.RESET}")
            
            # Add locations section (like teleport feature in TUI)
            # Get unique directories
            directories = {}
            for item in locked_items:
                dir_path = os.path.dirname(item['path'])
                if dir_path not in directories:
                    directories[dir_path] = []
                directories[dir_path].append(item['name'])
            
            # Show directories with item counts if more than one location
            if len(directories) > 1:
                print(f"\n{Colors.BORDER}╭─ 📍 {Colors.TITLE}LOCATIONS ({len(directories)} unique){Colors.RESET}")
                for idx, (dir_path, items) in enumerate(directories.items(), 1):
                    dir_name = os.path.basename(dir_path) or dir_path
                    print(f"{Colors.BORDER}│{Colors.RESET} {Colors.SUCCESS}[{idx}]{Colors.RESET} {Colors.TEXT}{dir_name}{Colors.RESET} {Colors.DIM}({len(items)} item(s)){Colors.RESET}")
                    print(f"{Colors.BORDER}│{Colors.RESET}   {Colors.DIM}└─ {dir_path}{Colors.RESET}")
                print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}")
            
            print()  # Empty line at end
        
        return True
    
    # Handle tamper-proof toggle flags: --0/--off and --1/--on
    elif '--0' in sys.argv or '--off' in sys.argv or '--1' in sys.argv or '--on' in sys.argv:
        # Determine which flag was used
        toggle_mode = None
        flag_used = None
        if '--0' in sys.argv:
            toggle_mode = False  # Disable protections
            idx = sys.argv.index('--0')
            flag_used = '--0'
        elif '--off' in sys.argv:
            toggle_mode = False
            idx = sys.argv.index('--off')
            flag_used = '--off'
        elif '--1' in sys.argv:
            toggle_mode = True  # Enable protections
            idx = sys.argv.index('--1')
            flag_used = '--1'
        elif '--on' in sys.argv:
            toggle_mode = True
            idx = sys.argv.index('--on')
            flag_used = '--on'
        
        # Get paths
        if idx + 1 < len(sys.argv):
            paths = [arg for arg in sys.argv[idx + 1:] if not arg.startswith('--')]
        else:
            paths = []
        
        if not paths:
            print_error(f"Usage: fadcrypt {flag_used} <path1> [path2] ...")
            return False
        
        
        # Toggle tamper-proof protections
        from core.cli.colors import Colors, BoxChars
        
        toggled_count = 0
        skipped_count = 0
        failed_count = 0
        toggled_paths = []
        
        for path in paths:
            try:
                if not os.path.exists(path):
                    print_error(f"✗ Path does not exist: {path}")
                    failed_count += 1
                    continue
                
                # Check current protection state
                current_protected_state = cli_handler.is_tamper_proof_enabled(path)
                
                # Only toggle if state is different from desired state
                if current_protected_state == toggle_mode:
                    skipped_count += 1
                    continue
                
                # Toggle protection
                if cli_handler.toggle_tamper_proof(path, toggle_mode):
                    toggled_paths.append(os.path.basename(path))
                    toggled_count += 1
                else:
                    print_error(f"✗ Failed to toggle protections for: {path}")
                    failed_count += 1
            except Exception as e:
                print_error(f"✗ Error processing {path}: {str(e)}")
                failed_count += 1
        
        # Summary with styled box (like MAIN MENU)
        print()
        
        if toggled_count > 0:
            # Toggled successfully
            if toggle_mode:
                print(f"{Colors.BORDER}╭─ 🔒 Locked {toggled_count} item(s) successfully{Colors.RESET}")
            else:
                print(f"{Colors.BORDER}╭─ 🔓 Released {toggled_count} item(s) successfully{Colors.RESET}")
            
            if failed_count > 0 or skipped_count > 0:
                print(f"{Colors.BORDER}│{Colors.RESET}")
            
            if failed_count > 0:
                print_error(f"{Colors.BORDER}│{Colors.RESET}  ✗ {failed_count} item(s) failed")
            elif skipped_count > 0:
                print(f"{Colors.BORDER}│{Colors.RESET}  ○ {skipped_count} item(s) already protected")
            
            # Command info with colors - multi-line format
            if paths and os.path.exists(paths[0]):
                filename = os.path.basename(paths[0])
                print(f"{Colors.BORDER}│{Colors.RESET}")
                if toggle_mode:
                    print(f"{Colors.BORDER}│{Colors.RESET}  Files: {Colors.HIGHLIGHT}IMMUTABLE & LOCKED{Colors.RESET}")
                    print(f"{Colors.BORDER}│{Colors.RESET}  To turn OFF tamper-proof protections:")
                    print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.SECONDARY}fadcrypt --0 {Colors.RESET}{Colors.HIGHLIGHT}{filename}{Colors.RESET}")
                    print(f"{Colors.BORDER}│{Colors.RESET}              {Colors.DIM}or{Colors.RESET}")
                    print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.SECONDARY}fadcrypt --off {Colors.RESET}{Colors.HIGHLIGHT}{filename}{Colors.RESET}")
                else:
                    print(f"{Colors.BORDER}│{Colors.RESET}  Files: {Colors.HIGHLIGHT}MOVEABLE, COPYABLE & DELETABLE{Colors.RESET}")
                    print(f"{Colors.BORDER}│{Colors.RESET}  To turn ON tamper-proof protections:")
                    print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.SECONDARY}fadcrypt --1 {Colors.RESET}{Colors.HIGHLIGHT}{filename}{Colors.RESET}")
                    print(f"{Colors.BORDER}│{Colors.RESET}              {Colors.DIM}or{Colors.RESET}")
                    print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.SECONDARY}fadcrypt --on {Colors.RESET}{Colors.HIGHLIGHT}{filename}{Colors.RESET}")
            
            print(f"{Colors.BORDER}╰────────────────────────────────────────────{Colors.RESET}")
        elif failed_count > 0:
            print(f"{Colors.BORDER}╭─ ✗ {failed_count} item(s) failed{Colors.RESET}")
            print(f"{Colors.BORDER}╰────────────────────────────────────────────{Colors.RESET}")
        elif skipped_count > 0:
            if toggle_mode:
                print(f"{Colors.BORDER}╭─ 🔒 All {skipped_count} item(s) already protected{Colors.RESET}")
            else:
                print(f"{Colors.BORDER}╭─ 🔓 All {skipped_count} item(s) already released{Colors.RESET}")
            
            if paths and os.path.exists(paths[0]):
                filename = os.path.basename(paths[0])
                print(f"{Colors.BORDER}│{Colors.RESET}")
                if toggle_mode:
                    print(f"{Colors.BORDER}│{Colors.RESET}  Files: {Colors.HIGHLIGHT}IMMUTABLE & LOCKED{Colors.RESET}")
                    print(f"{Colors.BORDER}│{Colors.RESET}  To turn OFF tamper-proof protections:")
                    print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.SECONDARY}fadcrypt --0 {Colors.RESET}{Colors.HIGHLIGHT}{filename}{Colors.RESET}")
                    print(f"{Colors.BORDER}│{Colors.RESET}              {Colors.DIM}or{Colors.RESET}")
                    print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.SECONDARY}fadcrypt --off {Colors.RESET}{Colors.HIGHLIGHT}{filename}{Colors.RESET}")
                else:
                    print(f"{Colors.BORDER}│{Colors.RESET}  Files: {Colors.HIGHLIGHT}MOVEABLE, COPYABLE & DELETABLE{Colors.RESET}")
                    print(f"{Colors.BORDER}│{Colors.RESET}  To turn ON tamper-proof protections:")
                    print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.SECONDARY}fadcrypt --1 {Colors.RESET}{Colors.HIGHLIGHT}{filename}{Colors.RESET}")
                    print(f"{Colors.BORDER}│{Colors.RESET}              {Colors.DIM}or{Colors.RESET}")
                    print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.SECONDARY}fadcrypt --on {Colors.RESET}{Colors.HIGHLIGHT}{filename}{Colors.RESET}")
            
            print(f"{Colors.BORDER}╰────────────────────────────────────────────{Colors.RESET}")
        
        return True if toggled_count > 0 else False
    
    return False


def main():
    """Main entry point for FadCrypt - TUI or GUI."""
    import sys
    import os
    
    # CRITICAL: If console=False in spec file, stdout/stderr are None
    # Setup minimal stdout for print() to work before GUI window is created
    # This is especially important for help/version output and splash screen messages
    if sys.stdout is None or sys.stderr is None:
        # Redirect to devnull so print() doesn't crash (output won't be visible but no error)
        if sys.stdout is None:
            sys.stdout = open(os.devnull, 'w')
        if sys.stderr is None:
            sys.stderr = open(os.devnull, 'w')
        if sys.stdin is None:
            sys.stdin = open(os.devnull, 'r')
    
    # Handle --help first (before any other processing)
    if '--help' in sys.argv or '-h' in sys.argv:
        from colorama import just_fix_windows_console
        just_fix_windows_console()
        from core.cli.help_display import show_help
        show_help()
        return
    
    # Handle --version
    if '--version' in sys.argv or '-v' in sys.argv:
        from colorama import just_fix_windows_console
        just_fix_windows_console()
        from core.cli.colors import Colors
        
        python_version = sys.version.split()[0]
        system = platform.system()
        
        RED = Colors.BORDER
        BRIGHT_RED = Colors.TITLE
        RESET = Colors.RESET
        
        print(f"\n{RED}╭─ 🔒 FadCrypt Version{RESET}")
        print(f"{RED}│{RESET} Version: {BRIGHT_RED}v{__version__}{RESET}")
        print(f"{RED}│{RESET} Version Code: {__version_code__}")
        print(f"{RED}│{RESET} Platform: {system}")
        print(f"{RED}│{RESET} Python: {python_version}")
        print(f"{RED}╰───────────────────{RESET}\n")
        return
    
    # Check for --windows flag BEFORE any imports
    mock_windows = '--windows' in sys.argv
    if mock_windows:
        print("🧪 Mock Windows mode enabled - simulating Windows environment on Linux")
        from core.win_mock import setup_windows_mocks
        setup_windows_mocks()
    
    # Detect platform
    system = platform.system()
    
    # Handle direct CLI commands first
    if '--lock' in sys.argv or '--unlock' in sys.argv or '--list' in sys.argv or '--list-locked' in sys.argv or \
       '--0' in sys.argv or '--1' in sys.argv or '--off' in sys.argv or '--on' in sys.argv:
        handle_direct_cli_commands()
        return
    
    # Check if GUI mode is explicitly requested
    gui_mode = '--gui' in sys.argv or '--auto-monitor' in sys.argv
    
    # Check if CLI/TUI mode is requested
    # CLI mode is default unless GUI is explicitly requested
    # Filter out non-functional flags like --verbose, --windows
    non_functional_flags = {'--verbose', '--windows'}
    functional_args = [arg for arg in sys.argv[1:] if arg not in non_functional_flags]
    
    if VERBOSE_MODE:
        safe_print(f"[MAIN] sys.argv: {sys.argv}")
        safe_print(f"[MAIN] gui_mode: {gui_mode}")
        safe_print(f"[MAIN] functional_args: {functional_args}")
    
    # CLI mode if: explicitly requested, no arguments (except non-functional flags), or not GUI mode
    cli_mode = '--cli' in sys.argv or (len(functional_args) == 0) or not gui_mode
    
    # If CLI mode or no arguments, launch TUI
    if cli_mode and not gui_mode:
        if VERBOSE_MODE:
            safe_print(f"[MAIN] cli_mode={cli_mode}, gui_mode={gui_mode} - Launching TUI...")
        launch_tui()
        return
    
    if VERBOSE_MODE:
        safe_print(f"[MAIN] cli_mode={cli_mode}, gui_mode={gui_mode} - Launching GUI...")
    
    # Otherwise, launch GUI
    # Step 1: Single Instance Check - Prevent multiple instances
    from core.single_instance_manager import check_single_instance
    single_instance = check_single_instance(exit_if_running=True)
    print("[LOCK] Single instance lock acquired - no other FadCrypt instances running")
    
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
