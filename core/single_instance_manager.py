"""
Single Instance Manager - Prevent Multiple Instances
Ensures only one instance of FadCrypt runs at a time
"""

import os
import sys
import platform
from abc import ABC, abstractmethod


class SingleInstanceBase(ABC):
    """
    Abstract base class for single instance enforcement.
    
    Platform-specific implementations should inherit from this class
    and implement the abstract methods.
    """
    
    @abstractmethod
    def acquire_lock(self) -> bool:
        """
        Attempt to acquire single instance lock.
        
        Returns:
            True if lock acquired successfully, False if another instance exists
        """
        pass
    
    @abstractmethod
    def release_lock(self):
        """Release the single instance lock."""
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """
        Check if another instance is running.
        
        Returns:
            True if another instance is running, False otherwise
        """
        pass


class SingleInstanceWindows(SingleInstanceBase):
    """
    Windows single instance implementation using mutex.
    
    Uses Windows API CreateMutexW for process-level locking.
    """
    
    def __init__(self, mutex_name: str = "Global\\FadCrypt"):
        """
        Initialize Windows single instance manager.
        
        Args:
            mutex_name: Unique name for the mutex
        """
        self.mutex_name = mutex_name
        self.mutex = None
        self.error = None
        
    def acquire_lock(self) -> bool:
        """
        Acquire mutex lock on Windows.
        
        Returns:
            True if lock acquired, False if another instance exists
        """
        try:
            import ctypes
            from ctypes import wintypes
            
            # Create mutex
            self.mutex = ctypes.windll.kernel32.CreateMutexW(None, True, self.mutex_name)
            self.error = ctypes.windll.kernel32.GetLastError()
            
            # ERROR_ALREADY_EXISTS = 183
            if self.error == 183:
                print("[WARNING] Another instance of FadCrypt is already running")
                return False
            
            print("[OK] Single instance lock acquired (Windows mutex)")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error acquiring Windows mutex: {e}")
            return True  # Allow running if mutex fails
    
    def release_lock(self):
        """Release mutex lock on Windows."""
        try:
            if self.mutex:
                import ctypes
                ctypes.windll.kernel32.CloseHandle(self.mutex)
                print("✅ Single instance lock released (Windows mutex)")
        except Exception as e:
            print(f"❌ Error releasing Windows mutex: {e}")
    
    def is_running(self) -> bool:
        """Check if another instance is running."""
        return self.error == 183 if self.error is not None else False


class SingleInstanceLinux(SingleInstanceBase):
    """
    Linux single instance implementation using file locking.
    
    Uses fcntl.lockf for file-based process locking.
    """
    
    def __init__(self, lock_file: str = "/tmp/fadcrypt.lock"):
        """
        Initialize Linux single instance manager.
        
        Args:
            lock_file: Path to lock file
        """
        self.lock_file = lock_file
        self.lock_fd = None
        
    def acquire_lock(self) -> bool:
        """
        Acquire file lock on Linux.
        
        Returns:
            True if lock acquired, False if another instance exists
        """
        try:
            import fcntl
            import psutil
            
            # Check if lock file exists and contains a stale PID
            if os.path.exists(self.lock_file):
                try:
                    with open(self.lock_file, 'r') as f:
                        pid_str = f.read().strip()
                        if pid_str:
                            pid = int(pid_str)
                            # Check if process with this PID exists
                            if not psutil.pid_exists(pid):
                                # Stale lock file - remove it
                                print(f"🧹 Removing stale lock file (process {pid} no longer exists)")
                                os.remove(self.lock_file)
                except Exception as e:
                    print(f"Warning: Could not check stale lock: {e}")
            
            # Open lock file
            self.lock_fd = open(self.lock_file, 'w')
            
            # Try to acquire exclusive lock (non-blocking)
            fcntl.lockf(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            
            # Write PID to lock file
            self.lock_fd.write(str(os.getpid()))
            self.lock_fd.flush()
            
            print(f"✅ Single instance lock acquired (Linux file lock: {self.lock_file})")
            return True
            
        except (IOError, OSError) as e:
            print(f"⚠️  Another instance of FadCrypt is already running (lock file: {self.lock_file})")
            if self.lock_fd:
                self.lock_fd.close()
                self.lock_fd = None
            return False
        except Exception as e:
            print(f"❌ Error acquiring Linux lock: {e}")
            return True  # Allow running if lock fails
    
    def release_lock(self):
        """Release file lock on Linux."""
        try:
            if self.lock_fd:
                self.lock_fd.close()
                self.lock_fd = None
            
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
                print(f"✅ Single instance lock released (removed {self.lock_file})")
        except Exception as e:
            print(f"❌ Error releasing Linux lock: {e}")
    
    def is_running(self) -> bool:
        """Check if another instance is running."""
        if not os.path.exists(self.lock_file):
            return False
        
        try:
            import fcntl
            # Try to open and lock the file
            with open(self.lock_file, 'r') as f:
                fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.lockf(f, fcntl.LOCK_UN)
                return False  # Lock available, no instance running
        except (IOError, OSError):
            return True  # Lock held, another instance running


def get_single_instance_manager() -> SingleInstanceBase:
    """
    Factory function to get platform-specific single instance manager.
    
    Returns:
        Platform-specific SingleInstance implementation
    """
    system = platform.system()
    
    if system == "Windows":
        return SingleInstanceWindows()
    elif system == "Linux":
        return SingleInstanceLinux()
    else:
        # Fall back to Linux implementation for other Unix-like systems
        print(f"⚠️  Unknown platform '{system}', using Linux-style locking")
        return SingleInstanceLinux()


# Convenience function for quick single instance check
def check_single_instance(exit_if_running: bool = True) -> SingleInstanceBase:
    """
    Check and enforce single instance.
    
    Args:
        exit_if_running: If True, exit the program if another instance is running
    
    Returns:
        SingleInstance manager object (keep reference to maintain lock)
    """
    manager = get_single_instance_manager()
    
    if not manager.acquire_lock():
        print("❌ FadCrypt is already running. Only one instance is allowed.")
        if exit_if_running:
            sys.exit(1)
    
    return manager
