"""
File Monitor - Config File Backup and Recovery
Monitors critical configuration files and automatically restores them if deleted
"""

import os
import sys
import shutil
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import List, Callable, Optional


class ConfigFileMonitor:
    """
    Monitors critical configuration files and backs them up.
    
    Automatically restores files if they're deleted during monitoring.
    This prevents users from bypassing the app locker by deleting config files.
    """
    
    def __init__(
        self,
        config_folder_func: Callable[[], str],
        backup_folder_func: Callable[[], str],
        files_to_monitor: Optional[List[str]] = None
    ):
        """
        Initialize the file monitor.
        
        Args:
            config_folder_func: Function that returns the config folder path
            backup_folder_func: Function that returns the backup folder path
            files_to_monitor: List of file paths to monitor (default: auto-detect)
        """
        self.get_config_folder = config_folder_func
        self.get_backup_folder = backup_folder_func
        self.observer = None
        self.monitoring_thread = None
        self.monitoring = False
        
        # Set files to monitor
        if files_to_monitor:
            self.files_to_monitor = files_to_monitor
        else:
            self.files_to_monitor = self._get_default_files()
    
    def _get_default_files(self) -> List[str]:
        """
        Get default files to monitor.
        
        On Windows, skips files that are currently protected (Windows will hold exclusive lock).
        On Linux, returns all files.
        
        Returns:
            List of file paths to monitor
        """
        config_folder = self.get_config_folder()
        all_files = [
            os.path.join(config_folder, 'apps_config.json'),
            os.path.join(config_folder, 'encrypted_password.bin'),
            os.path.join(config_folder, 'settings.json')
        ]
        
        # On Windows, filter out protected files that will cause file handle conflicts
        if sys.platform == 'win32':
            try:
                import ctypes
                FILE_ATTRIBUTE_HIDDEN = 0x00000002
                FILE_ATTRIBUTE_SYSTEM = 0x00000004
                FILE_ATTRIBUTE_READONLY = 0x00000001
                
                filtered_files = []
                for file_path in all_files:
                    if os.path.exists(file_path):
                        attrs = ctypes.windll.kernel32.GetFileAttributesW(file_path)
                        if attrs != -1:
                            is_protected = bool(attrs & (FILE_ATTRIBUTE_READONLY | FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM))
                            if not is_protected:
                                filtered_files.append(file_path)
                            else:
                                print(f"[FILE MONITOR] Skipping protected file from watchdog monitor: {os.path.basename(file_path)}")
                        else:
                            filtered_files.append(file_path)
                    else:
                        filtered_files.append(file_path)
                return filtered_files
            except:
                # Fall back to all files if protection check fails
                return all_files
        else:
            # On Linux, return all files (protection is via immutable flag, not file handles)
            return all_files
    
    def start_monitoring(self):
        """Start monitoring configuration files."""
        if self.monitoring:
            print("[FILE MONITOR] Already monitoring")
            return
        
        self.monitoring = True
        
        # Create backup folder
        backup_folder = self.get_backup_folder()
        os.makedirs(backup_folder, exist_ok=True)
        
        # Create initial backups
        self._backup_all_files()
        
        # Start watchdog observer
        event_handler = self.FileChangeHandler(
            self.files_to_monitor,
            backup_folder
        )
        
        self.observer = Observer()
        
        # Watch the config folder
        config_folder = self.get_config_folder()
        self.observer.schedule(event_handler, config_folder, recursive=False)
        self.observer.start()
        
        print(f"[FILE MONITOR] Started monitoring {len(self.files_to_monitor)} files")
        for file_path in self.files_to_monitor:
            print(f"   📁 {os.path.basename(file_path)}")
    
    def stop_monitoring(self):
        """Stop monitoring configuration files."""
        if not self.monitoring:
            return
        
        self.monitoring = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=2.0)
            self.observer = None
        
        print("[FILE MONITOR] Stopped monitoring")
    
    def _backup_all_files(self):
        """Create initial backup of all monitored files."""
        backup_folder = self.get_backup_folder()
        
        # Ensure backup folder exists with proper permissions
        try:
            os.makedirs(backup_folder, mode=0o755, exist_ok=True)
        except Exception as e:
            print(f"[FILE MONITOR] ⚠️  Could not create backup folder: {e}")
            return
        
        for file_path in self.files_to_monitor:
            if os.path.exists(file_path):
                backup_path = os.path.join(backup_folder, os.path.basename(file_path))
                try:
                    # Skip backup if file is protected (will retry on next modification)
                    # This avoids holding a handle to protected files
                    if sys.platform == 'win32':
                        try:
                            import ctypes
                            attrs = ctypes.windll.kernel32.GetFileAttributesW(file_path)
                            if attrs != -1:
                                FILE_ATTRIBUTE_HIDDEN = 0x00000002
                                FILE_ATTRIBUTE_SYSTEM = 0x00000004
                                FILE_ATTRIBUTE_READONLY = 0x00000001
                                is_protected = bool(attrs & (FILE_ATTRIBUTE_READONLY | FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM))
                                if is_protected:
                                    print(f"[FILE MONITOR] ⏭️  Skipping backup of protected file: {os.path.basename(file_path)} (will retry on modification)")
                                    continue
                        except:
                            pass  # Fall through to normal backup
                    
                    shutil.copy(file_path, backup_path)
                    # Ensure backup file is writable
                    os.chmod(backup_path, 0o644)
                    print(f"[FILE MONITOR] Backed up: {os.path.basename(file_path)}")
                except PermissionError:
                    # Silently skip permission errors
                    pass
                except Exception as e:
                    if "Permission denied" not in str(e):
                        print(f"[FILE MONITOR] Error backing up {file_path}: {e}")
    
    class FileChangeHandler(FileSystemEventHandler):
        """Handle file system events for monitored files."""
        
        def __init__(self, files_to_monitor: List[str], backup_folder: str):
            super().__init__()
            self.files_to_monitor = files_to_monitor
            self.backup_folder = backup_folder
        
        def on_modified(self, event):
            """Handle file modification events."""
            if event.src_path in self.files_to_monitor:
                print(f"[FILE MONITOR] File modified: {os.path.basename(event.src_path)}")
                self._backup_file(event.src_path)
        
        def on_deleted(self, event):
            """Handle file deletion events."""
            if event.src_path in self.files_to_monitor:
                print(f"[FILE MONITOR] ⚠️  File deleted: {os.path.basename(event.src_path)}")
                print(f"[FILE MONITOR] 🔄 Auto-restoring from backup...")
                self._restore_file(event.src_path)
        
        def _backup_file(self, file_path: str):
            """
            Backup a single file.
            
            Args:
                file_path: Path to file to backup
            """
            if os.path.exists(file_path):
                backup_path = os.path.join(self.backup_folder, os.path.basename(file_path))
                try:
                    # Ensure backup folder exists with write permissions
                    os.makedirs(self.backup_folder, mode=0o755, exist_ok=True)
                    
                    # Copy file (works even if source is read-only)
                    shutil.copy(file_path, backup_path)
                    
                    # Ensure backup file is writable for future overwrites
                    os.chmod(backup_path, 0o644)
                    
                    print(f"[FILE MONITOR] ✅ Backed up: {os.path.basename(file_path)}")
                except PermissionError as e:
                    # Silently skip if backup folder is not writable
                    # This happens when files are locked and backup folder is in protected location
                    pass
                except Exception as e:
                    # Only print error for non-permission issues
                    if "Permission denied" not in str(e):
                        print(f"[FILE MONITOR] ❌ Error backing up {file_path}: {e}")
        
        def _restore_file(self, file_path: str):
            """
            Restore a single file from backup.
            
            Args:
                file_path: Path to file to restore
            """
            backup_path = os.path.join(self.backup_folder, os.path.basename(file_path))
            
            if not os.path.exists(file_path) and os.path.exists(backup_path):
                # Ensure target directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                try:
                    shutil.copy(backup_path, file_path)
                    print(f"[FILE MONITOR] ✅ Restored: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"[FILE MONITOR] ❌ Error restoring {file_path}: {e}")
            else:
                if os.path.exists(file_path):
                    print(f"[FILE MONITOR] ℹ️  File already exists: {os.path.basename(file_path)}")
                else:
                    print(f"[FILE MONITOR] ❌ No backup found for: {os.path.basename(file_path)}")


def start_file_monitor_daemon(
    config_folder_func: Callable[[], str],
    backup_folder_func: Callable[[], str]
) -> ConfigFileMonitor:
    """
    Start file monitor as a daemon thread.
    
    Args:
        config_folder_func: Function that returns the config folder path
        backup_folder_func: Function that returns the backup folder path
    
    Returns:
        ConfigFileMonitor instance (keep reference to prevent GC)
    """
    monitor = ConfigFileMonitor(config_folder_func, backup_folder_func)
    
    def monitor_thread_func():
        monitor.start_monitoring()
        try:
            while monitor.monitoring:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop_monitoring()
    
    thread = threading.Thread(target=monitor_thread_func, daemon=True)
    thread.start()
    
    print("[FILE MONITOR] Daemon thread started")
    return monitor
