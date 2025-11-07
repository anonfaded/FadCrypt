#!/usr/bin/env python3
"""
FadCrypt Elevated Daemon

Runs as root via systemd service
Provides file operations (chattr, chmod) via Unix socket
Enables seamless elevated operations across reboots without password prompts

Operations:
- chattr: Set/unset immutable flag on files
- chmod: Change file permissions
- fanotify_watch: Monitor file/folder access with kernel-level interception
- fanotify_unwatch: Stop monitoring files/folders

All operations execute with root privileges - no polkit/sudo prompts needed.
"""

import socket
import os
import sys
import json
import subprocess
import logging
import struct
import select
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from ctypes import *

# Configuration
SOCKET_FILE = "/run/fadcrypt/elevated.sock"
SOCKET_DIR = "/run/fadcrypt"
LOG_FILE = "/var/log/fadcrypt-daemon.log"
FANOTIFY_SOCKET = "/run/fadcrypt/fanotify.sock"

# Fanotify constants
FAN_CLASS_CONTENT = 0x00000004
FAN_UNLIMITED_QUEUE = 0x00000010
FAN_UNLIMITED_MARKS = 0x00000020

FAN_OPEN_PERM = 0x00010000
FAN_ACCESS_PERM = 0x00020000

FAN_MARK_ADD = 0x00000001
FAN_MARK_REMOVE = 0x00000002

FAN_ALLOW = 0x01
FAN_DENY = 0x02

O_RDONLY = 0
O_WRONLY = 1
O_RDWR = 2
O_CLOEXEC = 0o2000000
O_LARGEFILE = 0o100000

# Setup logging
log_handlers = [logging.StreamHandler()]  # Always log to stderr
try:
    log_handlers.append(logging.FileHandler(LOG_FILE))
except (PermissionError, OSError):
    pass  # Log file location not available (not running as root), use stdout only

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [DAEMON] %(levelname)s: %(message)s',
    handlers=log_handlers
)
logger = logging.getLogger(__name__)

# Load libc for fanotify syscalls
try:
    libc = CDLL("libc.so.6", use_errno=True)
    
    # Fanotify syscalls
    libc.fanotify_init.argtypes = [c_uint, c_uint]
    libc.fanotify_init.restype = c_int
    
    libc.fanotify_mark.argtypes = [c_int, c_uint, c_ulonglong, c_int, c_char_p]
    libc.fanotify_mark.restype = c_int
    
    FANOTIFY_AVAILABLE = True
except Exception as e:
    logger.warning(f"Fanotify not available: {e}")
    FANOTIFY_AVAILABLE = False


# Event metadata structure
class fanotify_event_metadata(Structure):
    _fields_ = [
        ("event_len", c_uint32),
        ("vers", c_uint8),
        ("reserved", c_uint8),
        ("metadata_len", c_uint16),
        ("mask", c_ulonglong),
        ("fd", c_int32),
        ("pid", c_int32),
    ]


# Response structure
class fanotify_response(Structure):
    _fields_ = [
        ("fd", c_int32),
        ("response", c_uint32),
    ]


class FanotifyManager:
    """Manages fanotify file access monitoring"""
    
    def __init__(self):
        self.fan_fd: Optional[int] = None
        self.monitored_paths: Set[str] = set()
        self.permission_socket: Optional[socket.socket] = None
        self.event_thread: Optional[threading.Thread] = None
        self.running = False
        
    def init_fanotify(self) -> bool:
        """Initialize fanotify"""
        if not FANOTIFY_AVAILABLE:
            logger.error("Fanotify not available on this system")
            return False
        
        try:
            # Initialize fanotify with permission events
            flags = FAN_CLASS_CONTENT | FAN_UNLIMITED_QUEUE | FAN_UNLIMITED_MARKS
            event_flags = O_RDONLY | O_LARGEFILE | O_CLOEXEC
            
            self.fan_fd = libc.fanotify_init(flags, event_flags)
            
            if self.fan_fd < 0:
                errno = get_errno()
                logger.error(f"fanotify_init failed: {os.strerror(errno)}")
                return False
            
            logger.info(f"Fanotify initialized (fd={self.fan_fd})")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing fanotify: {e}")
            return False
    
    def add_watch(self, path: str) -> bool:
        """Add a file/directory to watch"""
        if not os.path.exists(path):
            logger.warning(f"Path does not exist: {path}")
            return False
        
        try:
            # Mark for permission events (blocks until we respond)
            mask = FAN_OPEN_PERM | FAN_ACCESS_PERM
            flags = FAN_MARK_ADD
            
            # Open file to get fd for marking
            fd = os.open(path, O_RDONLY)
            ret = libc.fanotify_mark(self.fan_fd, flags, mask, fd, None)
            os.close(fd)
            
            if ret < 0:
                errno = get_errno()
                logger.error(f"fanotify_mark failed for {path}: {os.strerror(errno)}")
                return False
            
            self.monitored_paths.add(path)
            logger.info(f"Watching: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding watch for {path}: {e}")
            return False
    
    def remove_watch(self, path: str) -> bool:
        """Remove a file/directory from watch"""
        if path not in self.monitored_paths:
            return True
        
        try:
            mask = FAN_OPEN_PERM | FAN_ACCESS_PERM
            flags = FAN_MARK_REMOVE
            
            fd = os.open(path, O_RDONLY)
            ret = libc.fanotify_mark(self.fan_fd, flags, mask, fd, None)
            os.close(fd)
            
            if ret < 0:
                errno = get_errno()
                logger.warning(f"fanotify_mark remove failed for {path}: {os.strerror(errno)}")
            
            self.monitored_paths.discard(path)
            logger.info(f"Stopped watching: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing watch for {path}: {e}")
            return False
    
    def init_permission_socket(self) -> bool:
        """Initialize Unix socket for permission requests"""
        try:
            # Remove old socket if exists
            if os.path.exists(FANOTIFY_SOCKET):
                os.remove(FANOTIFY_SOCKET)
            
            self.permission_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.permission_socket.bind(FANOTIFY_SOCKET)
            self.permission_socket.listen(5)
            
            # Make socket accessible to all users
            os.chmod(FANOTIFY_SOCKET, 0o666)
            
            logger.info(f"Permission socket listening: {FANOTIFY_SOCKET}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating permission socket: {e}")
            return False
    
    def get_path_from_fd(self, fd: int) -> Optional[str]:
        """Get file path from file descriptor"""
        try:
            return os.readlink(f"/proc/self/fd/{fd}")
        except:
            return None
    
    def ask_user_permission(self, path: str, pid: int) -> bool:
        """Ask user process for permission via socket"""
        logger.info(f"Access attempt: {path} (PID: {pid})")
        
        try:
            # Wait for client connection (with timeout)
            self.permission_socket.settimeout(10.0)
            client_socket, _ = self.permission_socket.accept()
            
            # Send request
            request = {
                "type": "permission_request",
                "path": path,
                "pid": pid
            }
            client_socket.sendall(json.dumps(request).encode() + b'\n')
            
            # Wait for response
            response_data = client_socket.recv(4096).decode().strip()
            response = json.loads(response_data)
            
            client_socket.close()
            
            allowed = response.get("allowed", False)
            logger.info(f"{'ALLOWED' if allowed else 'DENIED'}: {path}")
            
            return allowed
            
        except socket.timeout:
            logger.warning(f"Timeout waiting for user response - DENYING")
            return False
        except Exception as e:
            logger.error(f"Error asking permission: {e} - DENYING")
            return False
    
    def handle_event(self, metadata: fanotify_event_metadata):
        """Handle a fanotify event"""
        fd = metadata.fd
        pid = metadata.pid
        
        # Get file path
        path = self.get_path_from_fd(fd)
        
        if not path:
            # Can't determine path, allow by default
            self.send_response(fd, FAN_ALLOW)
            os.close(fd)
            return
        
        # Check if this is a monitored file
        is_monitored = any(monitored in path for monitored in self.monitored_paths)
        
        if not is_monitored:
            # Not monitored, allow
            self.send_response(fd, FAN_ALLOW)
            os.close(fd)
            return
        
        # Ask user for permission
        allowed = self.ask_user_permission(path, pid)
        
        # Send response
        response = FAN_ALLOW if allowed else FAN_DENY
        self.send_response(fd, response)
        os.close(fd)
    
    def send_response(self, fd: int, response: int):
        """Send permission response to kernel"""
        resp = fanotify_response()
        resp.fd = fd
        resp.response = response
        
        os.write(self.fan_fd, bytes(resp))
    
    def event_loop(self):
        """Main event loop for fanotify"""
        logger.info("Fanotify event loop started")
        
        while self.running:
            try:
                # Read event metadata
                data = os.read(self.fan_fd, 4096)
                
                if not data:
                    continue
                
                # Parse events
                offset = 0
                while offset < len(data):
                    metadata = fanotify_event_metadata.from_buffer_copy(data[offset:])
                    
                    if metadata.vers != 3:
                        logger.warning(f"Unsupported fanotify version: {metadata.vers}")
                        break
                    
                    self.handle_event(metadata)
                    
                    offset += metadata.event_len
                    
            except Exception as e:
                if self.running:
                    logger.error(f"Error in event loop: {e}")
    
    def start(self) -> bool:
        """Start fanotify monitoring"""
        if self.running:
            return True
        
        if not self.init_fanotify():
            return False
        
        if not self.init_permission_socket():
            return False
        
        self.running = True
        self.event_thread = threading.Thread(target=self.event_loop, daemon=True)
        self.event_thread.start()
        
        logger.info("Fanotify monitoring started")
        return True
    
    def stop(self):
        """Stop fanotify monitoring"""
        self.running = False
        
        if self.event_thread:
            self.event_thread.join(timeout=2.0)
        
        if self.fan_fd:
            os.close(self.fan_fd)
            self.fan_fd = None
        
        if self.permission_socket:
            self.permission_socket.close()
            self.permission_socket = None
        
        if os.path.exists(FANOTIFY_SOCKET):
            os.remove(FANOTIFY_SOCKET)
        
        self.monitored_paths.clear()
        logger.info("Fanotify monitoring stopped")


class ElevatedDaemon:
    """Daemon that runs as root and handles elevated file operations via socket."""
    
    def __init__(self):
        """Initialize and start the daemon."""
        try:
            self.fanotify_manager = FanotifyManager()
            self.setup_socket()
            logger.info("FadCrypt Elevated Daemon started successfully")
            logger.info(f"Listening on socket: {SOCKET_FILE}")
            self.run()
        except Exception as e:
            logger.error(f"Failed to start daemon: {e}")
            sys.exit(1)
    
    def setup_socket(self) -> None:
        """Setup Unix domain socket for IPC."""
        # Create socket directory
        Path(SOCKET_DIR).mkdir(parents=True, exist_ok=True, mode=0o755)
        
        # Remove old socket if exists
        if os.path.exists(SOCKET_FILE):
            try:
                os.remove(SOCKET_FILE)
            except OSError as e:
                logger.warning(f"Could not remove old socket: {e}")
        
        # Create Unix domain socket
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(SOCKET_FILE)
        self.server_socket.listen(5)  # Allow up to 5 pending connections
        
        # Set permissions so any user can connect
        os.chmod(SOCKET_FILE, 0o666)
        logger.info(f"Socket created with world-accessible permissions: {SOCKET_FILE}")
    
    def run(self) -> None:
        """Main daemon loop - accept and handle requests."""
        logger.info("Starting request loop...")
        connection_count = 0
        
        while True:
            try:
                connection, _ = self.server_socket.accept()
                connection_count += 1
                logger.debug(f"Accepted connection #{connection_count}")
                
                try:
                    self.handle_request(connection)
                except Exception as e:
                    logger.error(f"Error handling request: {e}")
                finally:
                    connection.close()
                    
            except KeyboardInterrupt:
                logger.info("Daemon interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
    
    def handle_request(self, connection: socket.socket) -> None:
        """Handle a single request from client."""
        try:
            # Receive request JSON
            data = connection.recv(8192).decode()
            if not data:
                logger.warning("Received empty request")
                return
            
            request = json.loads(data)
            logger.debug(f"Received request: {request}")
            
            command = request.get('command')
            
            # Route to appropriate handler
            if command == 'chattr':
                response = self._handle_chattr(request)
            elif command == 'chmod':
                response = self._handle_chmod(request)
            elif command == 'fanotify_watch':
                response = self._handle_fanotify_watch(request)
            elif command == 'fanotify_unwatch':
                response = self._handle_fanotify_unwatch(request)
            elif command == 'fanotify_start':
                response = self._handle_fanotify_start(request)
            elif command == 'fanotify_stop':
                response = self._handle_fanotify_stop(request)
            elif command == 'ping':
                response = {'success': True, 'message': 'pong'}
            else:
                response = {'success': False, 'error': f'Unknown command: {command}'}
            
            # Send response
            logger.debug(f"Sending response: {response}")
            connection.send(json.dumps(response).encode())
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request: {e}")
            error_response = json.dumps({'success': False, 'error': 'Invalid JSON'})
            try:
                connection.send(error_response.encode())
            except:
                pass
        except Exception as e:
            logger.error(f"Unexpected error handling request: {e}")
            error_response = json.dumps({'success': False, 'error': str(e)})
            try:
                connection.send(error_response.encode())
            except:
                pass
    
    def _handle_chattr(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chattr command to set/unset immutable flag."""
        try:
            files = request.get('files', [])
            mode = request.get('mode', '+i')  # +i (set immutable) or -i (unset)
            
            if not files:
                return {'success': False, 'error': 'No files specified'}
            
            if mode not in ['+i', '-i']:
                return {'success': False, 'error': f'Invalid mode: {mode}'}
            
            # Validate file paths (security check)
            validated_files = []
            for f in files:
                # Ensure file path is absolute and doesn't escape
                abs_path = os.path.abspath(f)
                if os.path.exists(abs_path) or mode == '-i':  # Allow -i on non-existent (in case already gone)
                    validated_files.append(abs_path)
                else:
                    logger.warning(f"File does not exist: {f}")
            
            if not validated_files:
                return {'success': False, 'error': 'No valid files to process'}
            
            # Execute chattr command
            cmd = ['chattr', mode] + validated_files
            logger.info(f"Executing: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"chattr {mode} successful for {len(validated_files)} files")
                return {
                    'success': True,
                    'message': f"chattr {mode} completed for {len(validated_files)} files",
                    'files_processed': len(validated_files)
                }
            else:
                error_msg = result.stderr or "chattr failed"
                logger.error(f"chattr failed: {error_msg}")
                return {'success': False, 'error': error_msg}
        
        except subprocess.TimeoutExpired:
            logger.error("chattr command timed out")
            return {'success': False, 'error': 'Command timeout'}
        except Exception as e:
            logger.error(f"Error in chattr handler: {e}")
            return {'success': False, 'error': str(e)}
    
    def _handle_chmod(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chmod command to change file permissions."""
        try:
            files = request.get('files', [])
            mode = request.get('mode', 0o600)  # Default: rw-------
            
            if not files:
                return {'success': False, 'error': 'No files specified'}
            
            if not isinstance(mode, int):
                try:
                    mode = int(mode, 8)  # Handle octal strings like "600"
                except ValueError:
                    return {'success': False, 'error': f'Invalid mode: {mode}'}
            
            success_count = 0
            errors = []
            
            for file_path in files:
                try:
                    abs_path = os.path.abspath(file_path)
                    
                    if not os.path.exists(abs_path):
                        logger.warning(f"File does not exist: {abs_path}")
                        errors.append(f"{abs_path}: Not found")
                        continue
                    
                    logger.debug(f"chmod {oct(mode)} on {abs_path}")
                    os.chmod(abs_path, mode)
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"chmod failed for {file_path}: {e}")
                    errors.append(f"{file_path}: {str(e)}")
            
            logger.info(f"chmod completed: {success_count} successful, {len(errors)} errors")
            
            return {
                'success': len(errors) == 0,
                'message': f"chmod completed for {success_count} files",
                'files_processed': success_count,
                'errors': errors
            }
        
        except Exception as e:
            logger.error(f"Error in chmod handler: {e}")
            return {'success': False, 'error': str(e)}
    
    def _handle_fanotify_start(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle fanotify_start command to initialize fanotify monitoring."""
        try:
            if self.fanotify_manager.running:
                return {'success': True, 'message': 'Fanotify already running'}
            
            if self.fanotify_manager.start():
                return {'success': True, 'message': 'Fanotify monitoring started'}
            else:
                return {'success': False, 'error': 'Failed to start fanotify'}
        
        except Exception as e:
            logger.error(f"Error in fanotify_start handler: {e}")
            return {'success': False, 'error': str(e)}
    
    def _handle_fanotify_stop(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle fanotify_stop command to stop fanotify monitoring."""
        try:
            self.fanotify_manager.stop()
            return {'success': True, 'message': 'Fanotify monitoring stopped'}
        
        except Exception as e:
            logger.error(f"Error in fanotify_stop handler: {e}")
            return {'success': False, 'error': str(e)}
    
    def _handle_fanotify_watch(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle fanotify_watch command to add files/folders to watch."""
        try:
            paths = request.get('paths', [])
            
            if not paths:
                return {'success': False, 'error': 'No paths specified'}
            
            success_count = 0
            errors = []
            
            for path in paths:
                abs_path = os.path.abspath(path)
                if self.fanotify_manager.add_watch(abs_path):
                    success_count += 1
                else:
                    errors.append(f"{path}: Failed to add watch")
            
            logger.info(f"fanotify_watch: {success_count} successful, {len(errors)} errors")
            
            return {
                'success': len(errors) == 0,
                'message': f"Watching {success_count} paths",
                'paths_watched': success_count,
                'errors': errors
            }
        
        except Exception as e:
            logger.error(f"Error in fanotify_watch handler: {e}")
            return {'success': False, 'error': str(e)}
    
    def _handle_fanotify_unwatch(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle fanotify_unwatch command to remove files/folders from watch."""
        try:
            paths = request.get('paths', [])
            
            if not paths:
                return {'success': False, 'error': 'No paths specified'}
            
            success_count = 0
            errors = []
            
            for path in paths:
                abs_path = os.path.abspath(path)
                if self.fanotify_manager.remove_watch(abs_path):
                    success_count += 1
                else:
                    errors.append(f"{path}: Failed to remove watch")
            
            logger.info(f"fanotify_unwatch: {success_count} successful, {len(errors)} errors")
            
            return {
                'success': len(errors) == 0,
                'message': f"Stopped watching {success_count} paths",
                'paths_unwatched': success_count,
                'errors': errors
            }
        
        except Exception as e:
            logger.error(f"Error in fanotify_unwatch handler: {e}")
            return {'success': False, 'error': str(e)}


def main():
    """Entry point for the daemon."""
    # Check if running as root
    if os.geteuid() != 0:
        logger.error("Daemon must run as root!")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("FadCrypt Elevated Daemon Starting")
    logger.info("=" * 60)
    
    daemon = ElevatedDaemon()


if __name__ == '__main__':
    main()
