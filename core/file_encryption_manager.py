"""
File and Folder Encryption Manager (Base Class)

Abstract base class for platform-specific file/folder encryption implementations.
Provides interface for encrypting and decrypting files and folders with AES-256-GCM.
"""

import os
import json
import hashlib
import tarfile
import tempfile
import time
import sys
import threading
import signal
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple
from .crypto_manager import CryptoManager
from .verbose_logger import vlog

# Global flag for graceful interruption
interrupted = False

def signal_handler(signum, frame):
    """Handle SIGINT (Ctrl+C) for graceful interruption"""
    global interrupted
    interrupted = True
    print("\n⚠️  Operation interrupted by user (Ctrl+C). Cleaning up...", flush=True)


def format_bytes(size_bytes):
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def show_spinner(message, stop_event, start_time=None):
    """Show a spinning animation until stop_event is set"""
    global interrupted
    import sys
    print(f"{message}...", end='', flush=True)  # Print initial message
    spinner = ['|', '/', '-', '\\']
    i = 0
    last_update = time.time()
    while not stop_event.is_set() and not interrupted:
        current_time = time.time()
        if current_time - last_update >= 0.1:  # Update every 0.1 seconds
            elapsed = ""
            if start_time:
                elapsed = f" ({current_time - start_time:.1f}s)"
            sys.stdout.write(f"\r{message} {spinner[i % len(spinner)]}{elapsed}")
            sys.stdout.flush()
            i += 1
            last_update = current_time
        else:
            time.sleep(0.01)  # Small sleep to not hog CPU
    
    # Clear spinner line if interrupted
    if interrupted:
        sys.stdout.write('\r' + ' ' * 100 + '\r')
        sys.stdout.flush()
    else:
        elapsed = ""
        if start_time:
            elapsed = f" ({time.time() - start_time:.1f}s)"
        sys.stdout.write(f"\r{message} ✓{elapsed}\n")
        sys.stdout.flush()


def show_progress(message, progress_callback, stop_event, start_time=None):
    """Show detailed progress with spinner animation and progress bar"""
    global interrupted
    import sys
    from core.cli.colors import Colors
    
    print(f"{message}...", end='', flush=True)  # Print initial message
    spinner = ['|', '/', '-', '\\']
    i = 0
    last_update = time.time()
    while not stop_event.is_set() and not interrupted:
        current_time = time.time()
        if current_time - last_update >= 0.1:  # Update every 0.1 seconds
            progress_msg = progress_callback()
            
            # Extract percentage for progress bar
            percentage = 0.0
            if '%' in progress_msg:
                try:
                    # Extract percentage from the message
                    percent_str = progress_msg.split('%')[0].strip()
                    if percent_str.replace('.', '').isdigit():
                        percentage = float(percent_str)
                except:
                    percentage = 0.0
            
            # Create progress bar (20 characters wide)
            bar_width = 20
            filled = int(bar_width * percentage / 100)
            bar = '█' * filled + '░' * (bar_width - filled)
            progress_bar = f"{Colors.ERROR}[{bar}]{Colors.RESET}"
            
            elapsed = ""
            if start_time:
                elapsed = f" ({current_time - start_time:.1f}s)"
            
            # Use spinner animation with progress bar and info
            sys.stdout.write(f"\r{message} {spinner[i % len(spinner)]} {progress_bar} {progress_msg}{elapsed}")
            sys.stdout.flush()
            i += 1
            last_update = current_time
        else:
            time.sleep(0.01)  # Small sleep to not hog CPU
    
    # Clear progress line and show interruption message if interrupted
    if interrupted:
        sys.stdout.write('\r' + ' ' * 150 + '\r')  # Clear the line
        sys.stdout.flush()
    else:
        # Clear the progress line after completion
        sys.stdout.write('\r' + ' ' * 150 + '\r')  # Clear the line
        sys.stdout.flush()


class FileEncryptionManager(ABC):
    """
    Abstract base class for file and folder encryption.
    
    Platform-specific implementations must override abstract methods.
    Handles encryption, decryption, and metadata management.
    
    Features:
    - Hybrid approach: stream encrypt files, archive+encrypt folders
    - Atomic operations with verification and rollback
    - Master password-based key derivation
    - Encrypted metadata storage
    """
    
    # File format header
    FADCRYPT_HEADER = b"FADCRYPT"
    FADCRYPT_VERSION = 1
    
    def __init__(self, config_folder: str, crypto_manager: Optional[CryptoManager] = None):
        """
        Initialize file encryption manager.
        
        Args:
            config_folder: Path to FadCrypt config folder
            crypto_manager: CryptoManager instance for encryption operations
        """
        self.config_folder = config_folder
        self.crypto = crypto_manager or CryptoManager()
        self.encrypted_items_dir = os.path.join(config_folder, "encrypted_items")
        os.makedirs(self.encrypted_items_dir, exist_ok=True)
    
    @abstractmethod
    def _get_temp_dir(self) -> str:
        """
        Get platform-specific temporary directory.
        Must be implemented by platform-specific subclasses.
        
        Returns:
            Path to temporary directory
        """
        pass
    
    def _calculate_hash(self, file_path: str) -> str:
        """
        Calculate SHA256 hash of file/folder contents.
        
        Args:
            file_path: Path to file or folder
            
        Returns:
            SHA256 hash as hex string
        """
        try:
            sha256 = hashlib.sha256()
            
            if os.path.isfile(file_path):
                # Hash file directly
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b''):
                        sha256.update(chunk)
            else:
                # Hash folder contents with progress
                total_files = 0
                processed_files = 0
                for root, dirs, files in os.walk(file_path):
                    total_files += len(files)
                
                start_hash = time.time()
                for root, dirs, files in os.walk(file_path):
                    # Sort for consistent ordering
                    dirs.sort()
                    for file in sorted(files):
                        file_full_path = os.path.join(root, file)
                        try:
                            with open(file_full_path, 'rb') as f:
                                for chunk in iter(lambda: f.read(4096), b''):
                                    sha256.update(chunk)
                            processed_files += 1
                            
                            # Show progress every 50 files or at end
                            if processed_files % 50 == 0 or processed_files == total_files:
                                progress = processed_files / total_files * 100
                                elapsed = time.time() - start_hash
                                if elapsed > 0:
                                    rate = processed_files / elapsed  # files per second
                                    eta = (total_files - processed_files) / rate if rate > 0 else 0
                                else:
                                    eta = 0
                                
                                progress_msg = f'🔐 Analyzing {os.path.basename(file_path)}: {progress:.1f}% ({processed_files}/{total_files} files) | ETA: {eta:.1f}s'
                                progress_msg = progress_msg.ljust(80)
                                sys.stdout.write(f'\r{progress_msg}')
                                sys.stdout.flush()
                        except (OSError, IOError):
                            continue
                
                # Clear progress line
                sys.stdout.write('\r' + ' ' * 100 + '\r')
            
            return sha256.hexdigest()
            
        except Exception as e:
            vlog(f"[FileEncryption] Error calculating hash: {e}")
            return ""
    
    def _create_metadata(self, item_path: str, item_type: str, original_hash: str) -> Dict:
        """
        Create encryption metadata.
        
        Args:
            item_path: Original path of item
            item_type: "file" or "folder"
            original_hash: SHA256 hash of original content
            
        Returns:
            Metadata dictionary
        """
        return {
            "original_path": item_path,
            "item_type": item_type,
            "original_hash": original_hash,
            "timestamp": time.time(),
            "version": self.FADCRYPT_VERSION
        }
    
    def _extract_metadata(self, encrypted_file: str, password: bytes) -> Optional[Dict]:
        """
        Extract and decrypt metadata from encrypted file.
        
        Args:
            encrypted_file: Path to .fadcrypt file
            password: Master password as bytes
            
        Returns:
            Metadata dictionary if successful, None otherwise
        """
        try:
            with open(encrypted_file, 'rb') as f:
                # Read header
                header = f.read(len(self.FADCRYPT_HEADER))
                if header != self.FADCRYPT_HEADER:
                    vlog(f"[FileEncryption] Invalid file format: {encrypted_file}")
                    return None
                
                # Read version
                version_byte = f.read(1)
                if not version_byte:
                    return None
                
                version = int.from_bytes(version_byte, 'little')
                if version != self.FADCRYPT_VERSION:
                    vlog(f"[FileEncryption] Unsupported version: {version}")
                    return None
                
                # Read metadata length (4 bytes, little-endian)
                metadata_len_bytes = f.read(4)
                if len(metadata_len_bytes) < 4:
                    return None
                
                metadata_len = int.from_bytes(metadata_len_bytes, 'little')
                
                # Read encrypted metadata
                encrypted_metadata = f.read(metadata_len)
                if len(encrypted_metadata) < metadata_len:
                    return None
                
                # Read salt and tags
                salt = f.read(self.crypto.SALT_SIZE)
                if len(salt) < self.crypto.SALT_SIZE:
                    return None
                    
                tag_meta = f.read(16)  # Metadata authentication tag
                if len(tag_meta) < 16:
                    return None
                
                # Decrypt metadata using the salt from file
                key = self.crypto.derive_key(password, salt)
                
                # Decrypt metadata
                try:
                    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
                    from cryptography.hazmat.backends import default_backend
                    
                    cipher_meta = Cipher(
                        algorithms.AES(key),
                        modes.GCM(salt, tag_meta),
                        backend=default_backend()
                    )
                    decryptor_meta = cipher_meta.decryptor()
                    decrypted_metadata = decryptor_meta.update(encrypted_metadata) + decryptor_meta.finalize()
                    
                    return json.loads(decrypted_metadata.decode('utf-8'))
                except Exception as e:
                    vlog(f"[FileEncryption] Error decrypting metadata: {e}")
                    return None
                    
        except Exception as e:
            vlog(f"[FileEncryption] Error extracting metadata: {e}")
            return None
    
    def encrypt_item(self, item_path: str, password: bytes, item_type: str = "file") -> Tuple[bool, str, Optional[str]]:
        """
        Encrypt a file or folder to .fadcrypt format.
        
        Safe atomic operation: Creates temp file, verifies, then moves to final location.
        
        Args:
            item_path: Path to file or folder to encrypt
            password: Master password as bytes
            item_type: "file" or "folder"
            
        Returns:
            Tuple of (success: bool, encrypted_path: str, error_message: Optional[str])
        """
        global interrupted
        
        # Set up signal handler for graceful interruption
        old_handler = signal.signal(signal.SIGINT, signal_handler)
        
        try:
            interrupted = False  # Reset interruption flag
            start_time = time.time()
            
            if not os.path.exists(item_path):
                error = f"Item does not exist: {item_path}"
                vlog(f"[FileEncryption] {error}")
                return False, "", error
            
            # Calculate original content hash for verification
            vlog(f"[FileEncryption] Calculating hash of original...")
            if interrupted:
                error = "Operation interrupted by user"
                vlog(f"[FileEncryption] {error}")
                return False, "", error
            original_hash = self._calculate_hash(item_path)
            if not original_hash:
                error = "Failed to calculate content hash"
                vlog(f"[FileEncryption] {error}")
                return False, "", error
            
            # Determine output path
            encrypted_path = f"{item_path}.fadcrypt"
            if os.path.exists(encrypted_path):
                error = f"Encrypted file already exists: {encrypted_path}"
                vlog(f"[FileEncryption] {error}")
                return False, "", error
            
            # Create temporary file for encryption ON THE SAME DRIVE as the source
            # This enables atomic rename instead of cross-drive copy
            source_dir = os.path.dirname(os.path.abspath(item_path))
            temp_fd, temp_encrypted_path = tempfile.mkstemp(suffix='.fadcrypt.tmp', dir=source_dir)
            os.close(temp_fd)
            
            try:
                vlog(f"[FileEncryption] Encrypting to temporary file: {os.path.basename(temp_encrypted_path)}")
                
                # Prepare data to encrypt
                if os.path.isfile(item_path):
                    # For single file: read with progress
                    file_size = os.path.getsize(item_path)
                    vlog(f"[FileEncryption] File size: {file_size} bytes")
                    file_data = b''
                    chunk_size = 1024 * 1024  # 1MB chunks
                    bytes_read = 0
                    
                    # Progress callback for threaded updates
                    def get_read_progress():
                        progress = (bytes_read / file_size) * 100
                        elapsed = time.time() - start_time
                        if elapsed > 0:
                            speed = bytes_read / elapsed / (1024 * 1024)  # MB/s
                            eta = (file_size - bytes_read) / (speed * 1024 * 1024) if speed > 0 else 0
                        else:
                            speed = 0
                            eta = 0
                        return f"{progress:.1f}% | {speed:.2f} MB/s | ETA: {eta:.1f}s"
                    
                    # Start progress thread
                    stop_event = threading.Event()
                    progress_thread = threading.Thread(target=show_progress, args=(f"🔐 Reading {os.path.basename(item_path)}", get_read_progress, stop_event, start_time))
                    progress_thread.start()
                    
                    with open(item_path, 'rb') as f:
                        while bytes_read < file_size:
                            remaining = file_size - bytes_read
                            current_chunk_size = min(chunk_size, remaining)
                            chunk = f.read(current_chunk_size)
                            if not chunk:
                                break
                            file_data += chunk
                            bytes_read += len(chunk)
                    
                    stop_event.set()
                    progress_thread.join()
                    
                    elapsed = time.time() - start_time
                    # print(f"✓ File read: {format_bytes(len(file_data))} ({elapsed:.1f}s)", flush=True)  # Removed for cleaner output
                else:
                    # For folder: create tar archive in memory with progress
                    vlog(f"[FileEncryption] Creating archive of folder...")
                    start_archive = time.time()
                    
                    # Count total files for progress
                    total_files = 0
                    for root, dirs, files in os.walk(item_path):
                        total_files += len(files)
                    
                    # Progress callback for threaded updates
                    def get_archive_progress():
                        progress = files_added / total_files * 100
                        elapsed = time.time() - start_archive
                        if elapsed > 0:
                            rate = files_added / elapsed  # files per second
                            eta = (total_files - files_added) / rate if rate > 0 else 0
                        else:
                            eta = 0
                        return f"{progress:.1f}% ({files_added}/{total_files} files) | ETA: {eta:.1f}s"
                    
                    # Start progress thread
                    stop_event = threading.Event()
                    progress_thread = threading.Thread(target=show_progress, args=(f"🔐 Archiving {os.path.basename(item_path)}", get_archive_progress, stop_event, start_archive))
                    progress_thread.start()
                    
                    import io
                    archive_buffer = io.BytesIO()
                    with tarfile.open(fileobj=archive_buffer, mode='w') as tar:  # Uncompressed for speed
                        files_added = 0
                        for root, dirs, files in os.walk(item_path):
                            # Sort for consistent ordering
                            dirs.sort()
                            for file in sorted(files):
                                file_path = os.path.join(root, file)
                                arcname = os.path.join(os.path.basename(item_path), os.path.relpath(file_path, item_path))
                                tar.add(file_path, arcname=arcname)
                                files_added += 1
                    
                    stop_event.set()
                    progress_thread.join()
                    
                    file_data = archive_buffer.getvalue()
                    elapsed = time.time() - start_archive
                    # print(f"✓ Archive created: {format_bytes(len(file_data))} ({elapsed:.1f}s)", flush=True)  # Removed for cleaner output
                    vlog(f"[FileEncryption] Archive size: {len(file_data)} bytes")
                
                # Create metadata
                metadata = self._create_metadata(item_path, item_type, original_hash)
                metadata_json = json.dumps(metadata).encode('utf-8')
                
                # Encrypt file
                vlog(f"[FileEncryption] Encrypting data...")
                stop_event = threading.Event()
                start_encrypt = time.time()
                spinner_thread = threading.Thread(target=show_spinner, args=(f"🔐 Encrypting {os.path.basename(item_path)}", stop_event, start_encrypt))
                spinner_thread.start()
                
                salt = os.urandom(self.crypto.SALT_SIZE)
                key = self.crypto.derive_key(password, salt)
                
                from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
                from cryptography.hazmat.backends import default_backend
                
                cipher = Cipher(
                    algorithms.AES(key),
                    modes.GCM(salt),
                    backend=default_backend()
                )
                encryptor = cipher.encryptor()
                encrypted_data = encryptor.update(file_data) + encryptor.finalize()
                
                # Encrypt metadata
                cipher_meta = Cipher(
                    algorithms.AES(key),
                    modes.GCM(salt),
                    backend=default_backend()
                )
                encryptor_meta = cipher_meta.encryptor()
                encrypted_metadata = encryptor_meta.update(metadata_json) + encryptor_meta.finalize()
                
                stop_event.set()
                spinner_thread.join()
                
                elapsed_encrypt = time.time() - start_encrypt
                if interrupted:
                    error = "Encryption interrupted by user during data encryption"
                    vlog(f"[FileEncryption] {error}")
                    # Stop all threads
                    stop_event.set()
                    spinner_thread.join()
                    # Cleanup temp file
                    try:
                        os.remove(temp_encrypted_path)
                    except:
                        pass
                    return False, "", error
                # print(f"✓ Data encrypted: {format_bytes(len(encrypted_data))} ({elapsed_encrypt:.1f}s)", flush=True)  # Removed for cleaner output
                
                # Write to temporary file with progress
                vlog(f"[FileEncryption] Writing encrypted file...")
                total_size = len(self.FADCRYPT_HEADER) + 1 + 4 + len(encrypted_metadata) + self.crypto.SALT_SIZE + 16 + 16 + len(encrypted_data)
                bytes_written = 0
                start_write = time.time()
                
                # Progress callback for threaded updates
                def get_write_progress():
                    progress = bytes_written / total_size * 100
                    elapsed = time.time() - start_write
                    if elapsed > 0:
                        speed = bytes_written / elapsed / (1024 * 1024)  # MB/s
                        eta = (total_size - bytes_written) / (speed * 1024 * 1024) if speed > 0 else 0
                    else:
                        speed = 0
                        eta = 0
                    return f"{progress:.1f}% | {speed:.2f} MB/s | ETA: {eta:.1f}s"
                
                # Start progress thread
                stop_event = threading.Event()
                progress_thread = threading.Thread(target=show_progress, args=(f"🔐 Writing {os.path.basename(encrypted_path)}", get_write_progress, stop_event, start_write))
                progress_thread.start()
                
                with open(temp_encrypted_path, 'wb') as f:
                    # Write header
                    f.write(self.FADCRYPT_HEADER)
                    bytes_written += len(self.FADCRYPT_HEADER)
                    
                    f.write(self.FADCRYPT_VERSION.to_bytes(1, 'little'))
                    bytes_written += 1
                    
                    f.write(len(encrypted_metadata).to_bytes(4, 'little'))
                    bytes_written += 4
                    
                    f.write(encrypted_metadata)
                    bytes_written += len(encrypted_metadata)
                    
                    f.write(salt)
                    bytes_written += self.crypto.SALT_SIZE
                    
                    f.write(encryptor_meta.tag)
                    bytes_written += 16
                    
                    f.write(encryptor.tag)
                    bytes_written += 16
                    
                    # Write encrypted data
                    chunk_size = 1024 * 1024  # 1MB
                    data_offset = 0
                    while data_offset < len(encrypted_data):
                        remaining = len(encrypted_data) - data_offset
                        current_chunk_size = min(chunk_size, remaining)
                        chunk = encrypted_data[data_offset:data_offset + current_chunk_size]
                        f.write(chunk)
                        data_offset += current_chunk_size
                        bytes_written += current_chunk_size
                
                stop_event.set()
                progress_thread.join()
                
                elapsed_write = time.time() - start_write
                # print(f"✓ File written: {format_bytes(total_size)} ({elapsed_write:.1f}s)", flush=True)  # Removed for cleaner output
                vlog(f"[FileEncryption] Encrypted file written: {total_size} bytes")
                
                # Small delay to ensure file system operations are complete
                time.sleep(0.5)
                
                if interrupted:
                    error = "Encryption interrupted by user during file writing"
                    vlog(f"[FileEncryption] {error}")
                    # Stop progress thread
                    stop_event.set()
                    progress_thread.join()
                    # Cleanup temp file
                    try:
                        os.remove(temp_encrypted_path)
                    except:
                        pass
                    return False, "", error
                
                # Verify encrypted file can be decrypted
                start_verify = time.time()
                
                # Show spinner during verification
                stop_event = threading.Event()
                verify_thread = threading.Thread(target=show_spinner, args=(f"🔐 Verifying {os.path.basename(encrypted_path)}", stop_event, start_verify))
                verify_thread.start()
                
                metadata_check = self._extract_metadata(temp_encrypted_path, password)
                
                stop_event.set()
                verify_thread.join()
                
                elapsed_verify = time.time() - start_verify
                if not metadata_check:
                    error = "Encryption verification failed: cannot decrypt metadata"
                    vlog(f"[FileEncryption] {error}")
                    try:
                        os.remove(temp_encrypted_path)
                    except:
                        pass
                    return False, "", error
                # print(f"✓ Verification passed ({elapsed_verify:.1f}s)", flush=True)  # Removed for cleaner output
                vlog(f"[FileEncryption] ✓ Verification successful")
                
                # Small delay to ensure file operations are complete
                time.sleep(0.5)
                
                # Move temporary file to final location (now on same drive, so atomic rename)
                start_finalize = time.time()
                
                # Show spinner during finalization
                stop_event = threading.Event()
                finalize_thread = threading.Thread(target=show_spinner, args=(f"🔐 Finalizing {os.path.basename(encrypted_path)}", stop_event, start_finalize))
                finalize_thread.start()
                
                try:
                    import shutil
                    
                    # Force finalization by trying rename operation with retries
                    # On Windows, file handles may take time to be fully released
                    max_retries = 50  # 50 retries * 0.1s = 5 seconds max
                    retry_count = 0
                    finalize_success = False
                    
                    vlog(f"[FileEncryption] Starting finalization with retries: {os.path.basename(temp_encrypted_path)}")
                    
                    while retry_count < max_retries and not finalize_success:
                        try:
                            # Try atomic rename first (fastest and safest)
                            os.rename(temp_encrypted_path, encrypted_path)
                            finalize_success = True
                            vlog(f"[FileEncryption] ✓ Finalized via atomic rename: {os.path.basename(encrypted_path)}")
                        except OSError as rename_error:
                            if retry_count == 0:
                                vlog(f"[FileEncryption] Rename failed, retrying: {rename_error}")
                            
                            retry_count += 1
                            if retry_count < max_retries:
                                time.sleep(0.1)  # Wait 100ms before retry
                            else:
                                # Final attempt: try shutil.move as fallback
                                try:
                                    shutil.move(temp_encrypted_path, encrypted_path)
                                    finalize_success = True
                                    vlog(f"[FileEncryption] ✓ Finalized via shutil.move: {os.path.basename(encrypted_path)}")
                                except Exception as move_error:
                                    vlog(f"[FileEncryption] Final attempt failed: {move_error}")
                                    raise rename_error  # Re-raise original error
                    
                    if not finalize_success:
                        error = f"Failed to finalize after {max_retries} retries: {temp_encrypted_path}"
                        vlog(f"[FileEncryption] {error}")
                        stop_event.set()
                        finalize_thread.join()
                        return False, "", error
                    
                    # ATOMIC: Delete original file after successful encryption
                    try:
                        if os.path.isdir(item_path):
                            import shutil as sh
                            sh.rmtree(item_path)
                            vlog(f"[FileEncryption] ✓ Original folder deleted: {os.path.basename(item_path)}")
                        else:
                            os.remove(item_path)
                            vlog(f"[FileEncryption] ✓ Original file deleted: {os.path.basename(item_path)}")
                    except Exception as del_error:
                        error = f"Encryption succeeded but failed to delete original: {del_error}"
                        vlog(f"[FileEncryption] {error}")
                        # Try to rollback by deleting the encrypted file
                        try:
                            os.remove(encrypted_path)
                        except:
                            pass
                        return False, "", error
                    
                    stop_event.set()
                    finalize_thread.join()
                    
                    elapsed_finalize = time.time() - start_finalize
                    # print(f"✓ Finalized ({elapsed_finalize:.1f}s)", flush=True)  # Removed for cleaner output
                    vlog(f"[FileEncryption] ✓ Encryption successful: {os.path.basename(encrypted_path)}")
                    return True, encrypted_path, None
                except Exception as e:
                    error = f"Failed to finalize encrypted file: {e}"
                    vlog(f"[FileEncryption] {error}")
                    try:
                        os.remove(temp_encrypted_path)
                    except:
                        pass
                    return False, "", error
                    
            except Exception as e:
                # Cleanup temp file on error
                try:
                    os.remove(temp_encrypted_path)
                except:
                    pass
                error = f"Encryption error: {e}"
                vlog(f"[FileEncryption] {error}")
                return False, "", error
                
            except KeyboardInterrupt:
                # Handle Ctrl+C interruption
                interrupted = True
                error = "Encryption interrupted by user (Ctrl+C)"
                vlog(f"[FileEncryption] {error}")
                # Cleanup temp file
                try:
                    os.remove(temp_encrypted_path)
                except:
                    pass
                return False, "", error
                
        except Exception as e:
            error = f"Encryption operation failed: {e}"
            vlog(f"[FileEncryption] {error}")
            return False, "", error
        finally:
            # Restore original signal handler
            signal.signal(signal.SIGINT, old_handler)
            
            # Comprehensive cleanup of temporary resources
            if 'temp_encrypted_path' in locals() and os.path.exists(temp_encrypted_path):
                try:
                    vlog(f"[FileEncryption] Cleaning up temp file: {os.path.basename(temp_encrypted_path)}")
                    os.remove(temp_encrypted_path)
                except Exception as cleanup_error:
                    vlog(f"[FileEncryption] Warning: Failed to cleanup temp file: {cleanup_error}")
            
            # If interrupted, also cleanup any partial encrypted file that might exist
            if interrupted and 'encrypted_path' in locals() and os.path.exists(encrypted_path):
                try:
                    vlog(f"[FileEncryption] Cleaning up partial encrypted file due to interruption: {os.path.basename(encrypted_path)}")
                    os.remove(encrypted_path)
                except Exception as cleanup_error:
                    vlog(f"[FileEncryption] Warning: Failed to cleanup partial encrypted file: {cleanup_error}")
    
    def decrypt_item(self, encrypted_path: str, password: bytes, output_path: str) -> Tuple[bool, str]:
        """
        Decrypt a .fadcrypt file back to original file or folder.
        
        Safe atomic operation: Decrypts to temp location, verifies hash, then moves to final location.
        
        Args:
            encrypted_path: Path to .fadcrypt file
            password: Master password as bytes
            output_path: Where to restore the decrypted item
            
        Returns:
            Tuple of (success: bool, error_message: str)
        """
        global interrupted
        
        # Set up signal handler for graceful interruption
        old_handler = signal.signal(signal.SIGINT, signal_handler)
        
        try:
            interrupted = False  # Reset interruption flag
            if not os.path.exists(encrypted_path):
                error = f"Encrypted file does not exist: {encrypted_path}"
                vlog(f"[FileEncryption] {error}")
                return False, error
            
            if interrupted:
                error = "Operation interrupted by user"
                vlog(f"[FileEncryption] {error}")
                return False, error
            
            vlog(f"[FileEncryption] Decrypting: {os.path.basename(encrypted_path)}")
            
            # Extract metadata
            if interrupted:
                error = "Operation interrupted by user"
                vlog(f"[FileEncryption] {error}")
                return False, error
            metadata = self._extract_metadata(encrypted_path, password)
            if not metadata:
                error = "Failed to decrypt metadata - password may be incorrect"
                vlog(f"[FileEncryption] {error}")
                return False, error
            
            original_hash = metadata.get("original_hash", "")
            item_type = metadata.get("item_type", "file")
            
            vlog(f"[FileEncryption] Metadata: type={item_type}, hash={original_hash[:16]}...")
            
            # For folders, extract directly to output path (no temp folder needed)
            output_dir = os.path.dirname(os.path.abspath(output_path))
            
            try:
                # Read and decrypt file from encrypted_path
                with open(encrypted_path, 'rb') as f:
                    # Read header and version
                    header = f.read(len(self.FADCRYPT_HEADER))
                    if header != self.FADCRYPT_HEADER:
                        raise ValueError("Invalid file format")
                    
                    version = int.from_bytes(f.read(1), 'little')
                    if version != self.FADCRYPT_VERSION:
                        raise ValueError(f"Unsupported version: {version}")
                    
                    # Skip metadata
                    metadata_len = int.from_bytes(f.read(4), 'little')
                    f.read(metadata_len)
                    
                    # Read salt and tags
                    salt = f.read(self.crypto.SALT_SIZE)
                    tag_meta = f.read(self.crypto.TAG_SIZE)
                    tag_data = f.read(self.crypto.TAG_SIZE)
                    
                    # Read encrypted data
                    encrypted_data = f.read()
                
                # Decrypt file data
                vlog(f"[FileEncryption] Decrypting data...")
                stop_event = threading.Event()
                start_decrypt = time.time()
                spinner_thread = threading.Thread(target=show_spinner, args=(f"🔓 Decrypting {os.path.basename(encrypted_path)}", stop_event, start_decrypt))
                spinner_thread.start()
                
                key = self.crypto.derive_key(password, salt)
                
                from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
                from cryptography.hazmat.backends import default_backend
                
                cipher = Cipher(
                    algorithms.AES(key),
                    modes.GCM(salt, tag_data),
                    backend=default_backend()
                )
                decryptor = cipher.decryptor()
                decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
                
                stop_event.set()
                spinner_thread.join()
                
                elapsed_decrypt = time.time() - start_decrypt
                if interrupted:
                    error = "Decryption interrupted by user during data decryption"
                    vlog(f"[FileEncryption] {error}")
                    # Stop spinner thread
                    stop_event.set()
                    spinner_thread.join()
                    return False, error
                # print(f"✓ Data decrypted: {format_bytes(len(decrypted_data))} ({elapsed_decrypt:.1f}s)", flush=True)  # Removed for cleaner output
                vlog(f"[FileEncryption] Decrypted {len(decrypted_data)} bytes")
                
                # Handle based on item type
                if item_type == "file":
                    # Write directly to output path with progress
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    total_size = len(decrypted_data)
                    bytes_written = 0
                    start_write_time = time.time()
                    
                    # Progress callback for threaded updates
                    def get_decrypt_write_progress():
                        progress = (bytes_written / total_size) * 100
                        elapsed = time.time() - start_write_time
                        if elapsed > 0:
                            speed = bytes_written / elapsed / (1024 * 1024)  # MB/s
                            eta = (total_size - bytes_written) / (speed * 1024 * 1024) if speed > 0 else 0
                        else:
                            speed = 0
                            eta = 0
                        return f"{progress:.1f}% | {speed:.2f} MB/s | ETA: {eta:.1f}s"
                    
                    # Start progress thread
                    stop_event = threading.Event()
                    progress_thread = threading.Thread(target=show_progress, args=(f"🔓 Writing {os.path.basename(output_path)}", get_decrypt_write_progress, stop_event, start_write_time))
                    progress_thread.start()
                    
                    with open(output_path, 'wb') as f:
                        chunk_size = 1024 * 1024  # 1MB
                        while bytes_written < total_size:
                            remaining = total_size - bytes_written
                            current_chunk_size = min(chunk_size, remaining)
                            chunk = decrypted_data[bytes_written:bytes_written + current_chunk_size]
                            f.write(chunk)
                            bytes_written += current_chunk_size
                    
                    stop_event.set()
                    progress_thread.join()
                    
                    elapsed = time.time() - start_write_time
                    # print(f"✓ File restored: {format_bytes(total_size)} ({elapsed:.1f}s)", flush=True)  # Removed for cleaner output
                    vlog(f"[FileEncryption] Restored file: {os.path.basename(output_path)}")
                else:
                    # Extract archive efficiently
                    start_extract = time.time()
                    
                    # Start spinner thread for extraction (simple, no detailed progress for speed)
                    stop_event = threading.Event()
                    spinner_thread = threading.Thread(target=show_spinner, args=(f"🔓 Extracting {os.path.basename(encrypted_path)}", stop_event, start_extract))
                    spinner_thread.start()
                    
                    # Extract all files at once for maximum performance
                    import io
                    import shutil
                    try:
                        # Extract to temp location first to avoid nested folders
                        temp_extract = output_path + "_temp_extract"
                        os.makedirs(temp_extract, exist_ok=True)
                        
                        with tarfile.open(fileobj=io.BytesIO(decrypted_data), mode='r') as tar:
                            # Extract all at once to temp location
                            tar.extractall(path=temp_extract)
                        
                        # Check if tar has nested folder structure (archive contains folder name)
                        # If so, move contents up one level to avoid nesting
                        temp_contents = os.listdir(temp_extract)
                        if len(temp_contents) == 1 and os.path.isdir(os.path.join(temp_extract, temp_contents[0])):
                            # Single folder in archive - check if it matches original folder name
                            extracted_folder = os.path.join(temp_extract, temp_contents[0])
                            original_name = os.path.basename(output_path)
                            if temp_contents[0] == original_name:
                                # Move contents from nested folder to final location
                                os.makedirs(output_path, exist_ok=True)
                                for item in os.listdir(extracted_folder):
                                    src = os.path.join(extracted_folder, item)
                                    dst = os.path.join(output_path, item)
                                    if os.path.exists(dst):
                                        if os.path.isdir(dst):
                                            shutil.rmtree(dst)
                                        else:
                                            os.remove(dst)
                                    shutil.move(src, dst)
                                shutil.rmtree(temp_extract)
                            else:
                                # Different name, just move the temp folder to output path
                                if os.path.exists(output_path):
                                    shutil.rmtree(output_path)
                                shutil.move(extracted_folder, output_path)
                                shutil.rmtree(temp_extract)
                        else:
                            # Multiple items or files directly in archive root
                            if os.path.exists(output_path):
                                shutil.rmtree(output_path)
                            shutil.move(temp_extract, output_path)
                        
                        stop_event.set()
                        spinner_thread.join()
                        
                        elapsed = time.time() - start_extract
                        # print(f"✓ Archive extracted: {format_bytes(len(decrypted_data))} ({elapsed:.1f}s)", flush=True)  # Removed for cleaner output
                        
                    except KeyboardInterrupt:
                        # Handle interruption during extraction
                        stop_event.set()
                        spinner_thread.join()
                        error = "Extraction interrupted by user (Ctrl+C)"
                        vlog(f"[FileEncryption] {error}")
                        return False, error
                    
                    # Folder extraction complete
                    vlog(f"[FileEncryption] Extracted folder: {os.path.basename(output_path)}")
                
                # No hash verification needed - AES-GCM authentication tag already verified integrity during decryption
                # Skip post-verification to significantly improve performance
                
                # Delete encrypted .fadcrypt file after successful decryption
                start_cleanup = time.time()
                
                try:
                    os.remove(encrypted_path)
                    vlog(f"[FileEncryption] ✓ Deleted encrypted file: {os.path.basename(encrypted_path)}")
                except Exception as del_error:
                    vlog(f"[FileEncryption] ⚠ Warning: Could not delete encrypted file: {del_error}")
                
                elapsed_cleanup = time.time() - start_cleanup
                # print(f"✓ Cleanup completed ({elapsed_cleanup:.1f}s)", flush=True)  # Removed for cleaner output
                return True, ""
                    
            except Exception as e:
                error = f"Decryption error: {e}"
                vlog(f"[FileEncryption] {error}")
                return False, error
                
            except KeyboardInterrupt:
                # Handle Ctrl+C interruption
                interrupted = True
                error = "Decryption interrupted by user (Ctrl+C)"
                vlog(f"[FileEncryption] {error}")
                return False, error
                
        except Exception as e:
            error = f"Decryption operation failed: {e}"
            vlog(f"[FileEncryption] {error}")
            return False, error
        finally:
            # Restore original signal handler
            signal.signal(signal.SIGINT, old_handler)
            
            # Comprehensive cleanup of temporary resources
            # temp_extract_dir no longer needed - extracting directly to output path
            
            # If interrupted, also cleanup any partial output that might exist
            if interrupted and 'output_path' in locals() and os.path.exists(output_path):
                try:
                    vlog(f"[FileEncryption] Cleaning up partial output due to interruption: {os.path.basename(output_path)}")
                    if os.path.isdir(output_path):
                        import shutil
                        shutil.rmtree(output_path)
                    else:
                        os.remove(output_path)
                except Exception as cleanup_error:
                    vlog(f"[FileEncryption] Warning: Failed to cleanup partial output: {cleanup_error}")
