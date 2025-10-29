"""
Crypto Manager - Encryption and Decryption Operations
Handles all cryptographic operations for FadCrypt
"""

import os
import json
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes


class CryptoManager:
    """
    Manages all encryption and decryption operations for FadCrypt.
    
    Uses AES-256 encryption with GCM mode for authenticated encryption.
    Passwords are derived using PBKDF2-HMAC-SHA256 with 100,000 iterations.
    
    Attributes:
        SALT_SIZE: Size of salt in bytes (16 bytes = 128 bits)
        TAG_SIZE: Size of authentication tag in bytes (16 bytes = 128 bits)
        KEY_LENGTH: Length of derived key in bytes (32 bytes = 256 bits)
        ITERATIONS: Number of PBKDF2 iterations (100,000)
    """
    
    SALT_SIZE = 16
    TAG_SIZE = 16
    KEY_LENGTH = 32
    ITERATIONS = 100000
    
    def __init__(self):
        """Initialize the CryptoManager."""
        pass
    
    def derive_key(self, password: bytes, salt: bytes) -> bytes:
        """
        Derive a cryptographic key from a password using PBKDF2-HMAC-SHA256.
        
        Args:
            password: Password as bytes
            salt: Random salt for key derivation
            
        Returns:
            Derived 256-bit key as bytes
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_LENGTH,
            salt=salt,
            iterations=self.ITERATIONS,
            backend=default_backend()
        )
        return kdf.derive(password)
    
    def encrypt_data(self, password: bytes, data: Dict[str, Any], file_path: str) -> bool:
        """
        Encrypt data and save to file using AES-256-GCM.
        
        File format: [salt:16][tag:16][encrypted_data:variable]
        
        Args:
            password: Password for encryption (as bytes)
            data: Dictionary to encrypt (will be JSON serialized)
            file_path: Path where encrypted file will be saved
            
        Returns:
            True if encryption successful, False otherwise
        """
        try:
            # Generate random salt
            salt = os.urandom(self.SALT_SIZE)
            
            # Derive key from password
            key = self.derive_key(password, salt)
            
            # Create cipher with GCM mode
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(salt),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Convert data to JSON and encrypt
            json_data = json.dumps(data).encode('utf-8')
            encrypted_data = encryptor.update(json_data) + encryptor.finalize()
            
            # Write to file: salt + tag + encrypted_data
            with open(file_path, 'wb') as f:
                f.write(salt + encryptor.tag + encrypted_data)
            
            return True
            
        except Exception as e:
            print(f"[CryptoManager] Error encrypting data: {e}")
            return False
    
    def decrypt_data(
        self,
        password: bytes,
        file_path: str,
        suppress_errors: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Decrypt data from file using AES-256-GCM.
        
        Args:
            password: Password for decryption (as bytes)
            file_path: Path to encrypted file
            suppress_errors: If True, don't print error messages
            
        Returns:
            Decrypted data as dictionary, or None if decryption failed
        """
        try:
            # Read encrypted file
            with open(file_path, 'rb') as f:
                salt = f.read(self.SALT_SIZE)
                tag = f.read(self.TAG_SIZE)
                encrypted_data = f.read()
            
            # Validate file format
            if len(salt) != self.SALT_SIZE or len(tag) != self.TAG_SIZE:
                raise ValueError("Invalid file format: corrupted header")
            
            # Derive key from password
            key = self.derive_key(password, salt)
            
            # Create cipher and decrypt
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(salt, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Parse JSON
            return json.loads(decrypted_data.decode('utf-8'))
            
        except FileNotFoundError:
            if not suppress_errors:
                print(f"[CryptoManager] File not found: {file_path}")
            return None
        except json.JSONDecodeError as e:
            if not suppress_errors:
                print(f"[CryptoManager] Invalid JSON in decrypted data: {e}")
            return None
        except Exception as e:
            if not suppress_errors:
                # Debug log (commented out for cleaner CLI)
                # print(f"[CryptoManager] Error decrypting data: {e}")
                pass
            return None
    
    def encrypt_password_hash(
        self,
        password: bytes,
        password_hash: bytes,
        file_path: str
    ) -> bool:
        """
        Encrypt a password hash and save to file.
        
        Used for storing the master password verification hash.
        
        Args:
            password: Password used for encryption (as bytes)
            password_hash: The password hash to encrypt (as bytes)
            file_path: Path where encrypted hash will be saved
            
        Returns:
            True if encryption successful, False otherwise
        """
        try:
            # Generate random salt
            salt = os.urandom(self.SALT_SIZE)
            
            # Derive key from password
            key = self.derive_key(password, salt)
            
            # Create cipher with GCM mode
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(salt),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Encrypt the password hash
            encrypted_hash = encryptor.update(password_hash) + encryptor.finalize()
            
            # Write to file: salt + tag + encrypted_hash
            with open(file_path, 'wb') as f:
                f.write(salt + encryptor.tag + encrypted_hash)
            
            return True
            
        except Exception as e:
            print(f"[CryptoManager] Error encrypting password hash: {e}")
            return False
    
    def decrypt_password_hash(
        self,
        password: bytes,
        file_path: str
    ) -> Optional[bytes]:
        """
        Decrypt a password hash from file.
        
        Args:
            password: Password used for decryption (as bytes)
            file_path: Path to encrypted hash file
            
        Returns:
            Decrypted password hash as bytes, or None if decryption failed
        """
        try:
            # Read encrypted file
            with open(file_path, 'rb') as f:
                salt = f.read(self.SALT_SIZE)
                tag = f.read(self.TAG_SIZE)
                encrypted_hash = f.read()
            
            # Validate file format
            if len(salt) != self.SALT_SIZE or len(tag) != self.TAG_SIZE:
                raise ValueError("Invalid file format: corrupted header")
            
            # Derive key from password
            key = self.derive_key(password, salt)
            
            # Create cipher and decrypt
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(salt, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            decrypted_hash = decryptor.update(encrypted_hash) + decryptor.finalize()
            
            return decrypted_hash
            
        except FileNotFoundError:
            print(f"[CryptoManager] Password file not found: {file_path}")
            return None
        except Exception as e:
            # Debug log (commented out for cleaner CLI)
            # print(f"[CryptoManager] Error decrypting password hash: {e}")
            return None
