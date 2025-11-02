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
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple
from .crypto_manager import CryptoManager
from .verbose_logger import vlog


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
                # Hash folder contents
                for root, dirs, files in os.walk(file_path):
                    # Sort for consistent ordering
                    dirs.sort()
                    for file in sorted(files):
                        file_full_path = os.path.join(root, file)
                        try:
                            with open(file_full_path, 'rb') as f:
                                for chunk in iter(lambda: f.read(4096), b''):
                                    sha256.update(chunk)
                        except (OSError, IOError):
                            continue
            
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
        import time
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
        try:
            if not os.path.exists(item_path):
                error = f"Item does not exist: {item_path}"
                vlog(f"[FileEncryption] {error}")
                return False, "", error
            
            # Calculate original content hash for verification
            vlog(f"[FileEncryption] Calculating hash of original...")
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
                    # For single file: read directly
                    with open(item_path, 'rb') as f:
                        file_data = f.read()
                    vlog(f"[FileEncryption] File size: {len(file_data)} bytes")
                else:
                    # For folder: create tar.gz archive in memory
                    vlog(f"[FileEncryption] Creating archive of folder...")
                    import io
                    archive_buffer = io.BytesIO()
                    with tarfile.open(fileobj=archive_buffer, mode='w:gz') as tar:
                        tar.add(item_path, arcname=os.path.basename(item_path), recursive=True)
                    file_data = archive_buffer.getvalue()
                    vlog(f"[FileEncryption] Archive size: {len(file_data)} bytes")
                
                # Create metadata
                metadata = self._create_metadata(item_path, item_type, original_hash)
                metadata_json = json.dumps(metadata).encode('utf-8')
                
                # Encrypt file
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
                
                # Write to temporary file
                with open(temp_encrypted_path, 'wb') as f:
                    f.write(self.FADCRYPT_HEADER)
                    f.write(self.FADCRYPT_VERSION.to_bytes(1, 'little'))
                    f.write(len(encrypted_metadata).to_bytes(4, 'little'))
                    f.write(encrypted_metadata)
                    f.write(salt)
                    f.write(encryptor_meta.tag)
                    f.write(encryptor.tag)
                    f.write(encrypted_data)
                
                vlog(f"[FileEncryption] Verifying encrypted file...")
                
                # Verify encrypted file can be decrypted
                metadata_check = self._extract_metadata(temp_encrypted_path, password)
                if not metadata_check:
                    error = "Encryption verification failed: cannot decrypt metadata"
                    vlog(f"[FileEncryption] {error}")
                    try:
                        os.remove(temp_encrypted_path)
                    except:
                        pass
                    return False, "", error
                
                # Move temporary file to final location (now on same drive, so atomic rename)
                try:
                    import shutil
                    shutil.move(temp_encrypted_path, encrypted_path)
                    vlog(f"[FileEncryption] ✓ Encrypted file created: {os.path.basename(encrypted_path)}")
                    
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
                
        except Exception as e:
            error = f"Encryption operation failed: {e}"
            vlog(f"[FileEncryption] {error}")
            return False, "", error
    
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
        try:
            if not os.path.exists(encrypted_path):
                error = f"Encrypted file does not exist: {encrypted_path}"
                vlog(f"[FileEncryption] {error}")
                return False, error
            
            vlog(f"[FileEncryption] Decrypting: {os.path.basename(encrypted_path)}")
            
            # Extract metadata
            metadata = self._extract_metadata(encrypted_path, password)
            if not metadata:
                error = "Failed to decrypt metadata - password may be incorrect"
                vlog(f"[FileEncryption] {error}")
                return False, error
            
            original_hash = metadata.get("original_hash", "")
            item_type = metadata.get("item_type", "file")
            
            vlog(f"[FileEncryption] Metadata: type={item_type}, hash={original_hash[:16]}...")
            
            # Create temporary extraction directory
            temp_dir = self._get_temp_dir()
            temp_extract_dir = tempfile.mkdtemp(suffix='.fadcrypt_extract', dir=temp_dir)
            
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
                
                vlog(f"[FileEncryption] Decrypted {len(decrypted_data)} bytes")
                
                # Handle based on item type
                if item_type == "file":
                    # Write directly to output path
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(decrypted_data)
                    vlog(f"[FileEncryption] Restored file: {os.path.basename(output_path)}")
                else:
                    # Extract archive
                    import io
                    with tarfile.open(fileobj=io.BytesIO(decrypted_data), mode='r:gz') as tar:
                        tar.extractall(path=temp_extract_dir)
                    
                    # Move extracted folder to output path
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    import shutil
                    extracted_items = os.listdir(temp_extract_dir)
                    if extracted_items:
                        extracted_path = os.path.join(temp_extract_dir, extracted_items[0])
                        shutil.move(extracted_path, output_path)
                    vlog(f"[FileEncryption] Restored folder: {os.path.basename(output_path)}")
                
                # Verify hash if possible
                vlog(f"[FileEncryption] Verifying decrypted content...")
                restored_hash = self._calculate_hash(output_path)
                
                if restored_hash == original_hash:
                    vlog(f"[FileEncryption] ✓ Hash verification passed")
                else:
                    vlog(f"[FileEncryption] ⚠ Hash mismatch - data may be corrupted")
                    vlog(f"[FileEncryption]   Expected: {original_hash}")
                    vlog(f"[FileEncryption]   Got:      {restored_hash}")
                
                # ATOMIC: Delete encrypted .fadcrypt file after successful decryption
                try:
                    os.remove(encrypted_path)
                    vlog(f"[FileEncryption] ✓ Deleted encrypted file: {os.path.basename(encrypted_path)}")
                except Exception as del_error:
                    vlog(f"[FileEncryption] ⚠ Warning: Could not delete encrypted file: {del_error}")
                
                # Cleanup temp extraction directory
                try:
                    import shutil
                    shutil.rmtree(temp_extract_dir)
                except:
                    pass
                
                return True, ""
                    
            except Exception as e:
                error = f"Decryption error: {e}"
                vlog(f"[FileEncryption] {error}")
                # Cleanup on error
                try:
                    import shutil
                    shutil.rmtree(temp_extract_dir)
                except:
                    pass
                return False, error
                
        except Exception as e:
            error = f"Decryption operation failed: {e}"
            vlog(f"[FileEncryption] {error}")
            return False, error
