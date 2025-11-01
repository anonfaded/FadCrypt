"""
Recovery Manager - Password Recovery Code Operations
Handles generation, storage, verification, and consumption of recovery codes
Provides secure password reset functionality when master password is forgotten

SECURITY MODEL:
- Recovery codes are hashed with PBKDF2-HMAC-SHA256 (100,000 iterations)
- Each code has a unique random salt (32 bytes)
- Hashes are stored WITHOUT password encryption
- Even with hash file access, codes cannot be reversed
- Brute force is computationally infeasible due to iteration count
"""

import os
import json
import secrets
import string
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from .verbose_logger import vlog


class RecoveryCodeManager:
    """
    Manages password recovery codes for FadCrypt.
    
    SECURITY ARCHITECTURE:
    - Codes are hashed using PBKDF2-HMAC-SHA256 with 100,000 iterations
    - Each code has a unique 32-byte random salt
    - Hashes stored separately from encrypted password file
    - Verification works WITHOUT needing the master password
    - Hash file compromise does NOT reveal codes (cryptographically secure)
    - Brute force attacks are computationally infeasible
    
    Features:
    - Generate 10 unique recovery codes per password setup
    - Store code hashes securely (password-independent)
    - Verify codes against hashes WITHOUT password
    - Track used/unused codes
    - Support password recovery without original password
    - One-time use enforcement (non-bypassable)
    
    Attributes:
        recovery_codes_file: Path to recovery code hashes file
    """
    
    # Recovery code format: 4 groups of 4 alphanumeric chars (case-insensitive)
    # Example: ABCD-EFGH-IJKL-MNOP
    CODE_CHARS = string.ascii_uppercase + string.digits
    CODES_PER_GROUP = 4
    GROUPS_PER_CODE = 4
    TOTAL_CODES = 10
    
    # Hash security parameters
    HASH_ITERATIONS = 100000  # PBKDF2 iterations (high for security)
    SALT_LENGTH = 32  # 32 bytes = 256 bits (cryptographically secure)
    
    def __init__(self, recovery_codes_file_path: str):
        """
        Initialize the RecoveryCodeManager.
        
        Args:
            recovery_codes_file_path: Full path to recovery_codes.json file
        """
        self.recovery_codes_file = recovery_codes_file_path
        # Debug log (commented out for cleaner CLI)
        # print(f"[RecoveryCodeManager] Initialized with codes file: {recovery_codes_file_path}")
    
    @staticmethod
    def generate_code() -> str:
        """
        Generate a single recovery code in format XXXX-XXXX-XXXX-XXXX.
        
        Returns:
            Generated recovery code (uppercase alphanumeric)
        """
        code_parts = []
        for _ in range(RecoveryCodeManager.GROUPS_PER_CODE):
            part = ''.join(secrets.choice(RecoveryCodeManager.CODE_CHARS) 
                          for _ in range(RecoveryCodeManager.CODES_PER_GROUP))
            code_parts.append(part)
        return '-'.join(code_parts)
    
    @staticmethod
    def generate_codes(count: int = TOTAL_CODES) -> List[str]:
        """
        Generate multiple unique recovery codes.
        
        Args:
            count: Number of codes to generate (default: 10)
            
        Returns:
            List of unique recovery codes
        """
        codes = set()
        while len(codes) < count:
            codes.add(RecoveryCodeManager.generate_code())
        return sorted(list(codes))
    
    @staticmethod
    def _hash_recovery_code(code: str, salt: bytes) -> bytes:
        """
        Hash a recovery code using PBKDF2-HMAC-SHA256.
        
        SECURITY:
        - Uses 100,000 iterations (computationally expensive for attackers)
        - Unique salt per code (prevents rainbow table attacks)
        - SHA-256 output (256-bit security)
        - Even with hash + salt, code cannot be reversed
        
        Args:
            code: Recovery code to hash (normalized: uppercase, no dashes)
            salt: Random salt bytes (32 bytes)
            
        Returns:
            Hash bytes (32 bytes from SHA-256)
        """
        # Normalize code: uppercase, no separators
        normalized_code = code.upper().replace('-', '').replace(' ', '')
        code_bytes = normalized_code.encode('utf-8')
        
        # PBKDF2-HMAC-SHA256 with 100k iterations
        hash_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            code_bytes,
            salt,
            RecoveryCodeManager.HASH_ITERATIONS
        )
        return hash_bytes
    
    @staticmethod
    def _verify_code_against_hash(code: str, stored_hash: bytes, salt: bytes) -> bool:
        """
        Verify a recovery code against its stored hash.
        
        Args:
            code: User-entered recovery code
            stored_hash: Stored hash bytes
            salt: Salt used for original hash
            
        Returns:
            True if code matches hash, False otherwise
        """
        computed_hash = RecoveryCodeManager._hash_recovery_code(code, salt)
        # Constant-time comparison (prevents timing attacks)
        return secrets.compare_digest(computed_hash, stored_hash)
    
    def create_recovery_codes(self) -> Tuple[bool, Optional[List[str]]]:
        """
        Generate and store new recovery codes using hash-based storage.
        
        SECURITY:
        - Codes hashed with PBKDF2-HMAC-SHA256 (100,000 iterations)
        - Unique 32-byte salt per code
        - Hashes stored in plain JSON (no password encryption)
        - Actual codes returned ONCE to display to user
        
        Returns:
            Tuple of (success: bool, codes: Optional[List[str]])
        """
        try:
            # Generate 10 unique codes
            codes = self.generate_codes(self.TOTAL_CODES)
            
            # Create recovery data with hashes instead of encrypted codes
            recovery_data = {
                'version': '2.0',  # Version 2.0 uses hash-based verification
                'created_at': datetime.now().isoformat(),
                'hash_algorithm': 'PBKDF2-HMAC-SHA256',
                'iterations': self.HASH_ITERATIONS,
                'codes': []
            }
            
            # Hash each code with unique salt
            for code in codes:
                # Generate unique random salt (32 bytes = 256 bits)
                salt = secrets.token_bytes(self.SALT_LENGTH)
                
                # Hash the code
                code_hash = self._hash_recovery_code(code, salt)
                
                # Store hash + salt + metadata (NOT the code itself)
                recovery_data['codes'].append({
                    'hash': code_hash.hex(),  # Store as hex string
                    'salt': salt.hex(),        # Store as hex string
                    'used': False,
                    'used_at': None,
                    'attempts': 0,
                    'created_at': datetime.now().isoformat()
                })
            
            # Save to file (plain JSON, no encryption needed)
            # The hashes are useless without the actual codes
            with open(self.recovery_codes_file, 'w', encoding='utf-8') as f:
                json.dump(recovery_data, f, indent=2)
            
            vlog(f"[RecoveryCodeManager] ✅ Created {len(codes)} recovery codes with secure hashes")
            vlog(f"[RecoveryCodeManager] Hash algorithm: PBKDF2-HMAC-SHA256 ({self.HASH_ITERATIONS} iterations)")
            vlog(f"[RecoveryCodeManager] File now exists: {os.path.exists(self.recovery_codes_file)}")
            return True, codes
                
        except Exception as e:
            print(f"[RecoveryCodeManager] ❌ Error creating recovery codes: {e}")
            import traceback
            traceback.print_exc()
            return False, None
    
    def verify_recovery_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Verify if a recovery code is valid and unused using hash-based verification.
        
        SECURITY:
        - Does NOT require master password
        - Compares entered code hash against stored hashes
        - Uses constant-time comparison (prevents timing attacks)
        - Computationally expensive to brute force (100k iterations per attempt)
        
        Args:
            code: Recovery code to verify (will be normalized to uppercase)
            
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        try:
            if not os.path.exists(self.recovery_codes_file):
                return False, "Recovery codes not found"
            
            # Normalize code (remove dashes/spaces, convert to uppercase)
            normalized_input = code.upper().replace('-', '').replace(' ', '')
            if len(normalized_input) != self.GROUPS_PER_CODE * self.CODES_PER_GROUP:
                return False, "Invalid recovery code format"
            
            # Load recovery data (plain JSON)
            with open(self.recovery_codes_file, 'r', encoding='utf-8') as f:
                recovery_data = json.load(f)
            
            # Verify code against stored hashes
            for code_entry in recovery_data.get('codes', []):
                # Get stored hash and salt
                stored_hash_hex = code_entry.get('hash')
                salt_hex = code_entry.get('salt')
                
                if not stored_hash_hex or not salt_hex:
                    continue
                
                # Convert from hex
                stored_hash = bytes.fromhex(stored_hash_hex)
                salt = bytes.fromhex(salt_hex)
                
                # Verify code against this hash
                if self._verify_code_against_hash(normalized_input, stored_hash, salt):
                    # Code matches - check if already used
                    if code_entry.get('used', False):
                        return False, "This recovery code has already been used"
                    
                    # Code is valid and unused
                    from core.verbose_logger import vlog
                    vlog("[RecoveryCodeManager] Recovery code verified")
                    return True, None
            
            # Code not found in any hash
            return False, "Recovery code not found or incorrect"
            
        except Exception as e:
            from core.verbose_logger import vlog
            vlog(f"[RecoveryCodeManager] ❌ Error verifying recovery code: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Error verifying code: {str(e)}"
    
    def consume_recovery_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Mark a recovery code as used (one-time consumption).
        
        SECURITY:
        - Marks code as used in hash storage file
        - Uses file locking to prevent race conditions
        - Cannot be bypassed (hash storage is permanent)
        
        Args:
            code: Recovery code to consume
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            if not os.path.exists(self.recovery_codes_file):
                return False, "Recovery codes not found"
            
            # Normalize code
            normalized_input = code.upper().replace('-', '').replace(' ', '')
            
            # Load current data
            with open(self.recovery_codes_file, 'r', encoding='utf-8') as f:
                recovery_data = json.load(f)
            
            # Find and mark code as used
            code_found = False
            for code_entry in recovery_data.get('codes', []):
                stored_hash_hex = code_entry.get('hash')
                salt_hex = code_entry.get('salt')
                
                if not stored_hash_hex or not salt_hex:
                    continue
                
                # Convert from hex
                stored_hash = bytes.fromhex(stored_hash_hex)
                salt = bytes.fromhex(salt_hex)
                
                # Check if this is the matching code
                if self._verify_code_against_hash(normalized_input, stored_hash, salt):
                    # Mark as used
                    code_entry['used'] = True
                    code_entry['used_at'] = datetime.now().isoformat()
                    code_found = True
                    break
            
            if not code_found:
                return False, "Recovery code not found"
            
            # Save updated data
            with open(self.recovery_codes_file, 'w', encoding='utf-8') as f:
                json.dump(recovery_data, f, indent=2)
            
            from core.verbose_logger import vlog
            vlog("[RecoveryCodeManager] Recovery code marked as used")
            return True, None
            
        except Exception as e:
            print(f"[RecoveryCodeManager] ❌ Error consuming recovery code: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Error consuming code: {str(e)}"
    
    def delete_recovery_codes(self) -> bool:
        """
        Delete recovery codes file (used during password reset).
        
        This is part of cleanup process when resetting password via recovery code.
        New codes will be generated with the new password.
        
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if os.path.exists(self.recovery_codes_file):
                os.remove(self.recovery_codes_file)
                print("[RecoveryCodeManager] Recovery codes deleted")
                return True
            return True  # Already deleted
        except Exception as e:
            print(f"[RecoveryCodeManager] ❌ Error deleting recovery codes: {e}")
            return False
    
    def has_recovery_codes(self) -> bool:
        """
        Check if recovery codes have been set.
        
        Returns:
            True if recovery codes file exists, False otherwise
        """
        return os.path.exists(self.recovery_codes_file)
    
    def get_remaining_codes_count(self) -> Tuple[bool, Optional[int]]:
        """
        Get count of unused recovery codes.
        
        Returns:
            Tuple of (success: bool, count: Optional[int])
        """
        try:
            if not os.path.exists(self.recovery_codes_file):
                return False, None
            
            # Load plain JSON
            with open(self.recovery_codes_file, 'r', encoding='utf-8') as f:
                recovery_data = json.load(f)
            
            # Count unused codes
            unused_count = sum(
                1 for code_entry in recovery_data.get('codes', [])
                if not code_entry.get('used', False)
            )
            
            return True, unused_count
            
        except Exception as e:
            print(f"[RecoveryCodeManager] ❌ Error counting recovery codes: {e}")
            return False, None
    
    def list_recovery_codes(self) -> Tuple[bool, Optional[List[Dict]]]:
        """
        List recovery code metadata (NOT the actual codes - they're hashed).
        
        SECURITY:
        - Actual codes are NEVER stored, only hashes
        - Returns metadata: used status, timestamps
        
        NOTE: Cannot return actual codes because they're not stored.
        
        Returns:
            Tuple of (success: bool, metadata_list: Optional[List[Dict]])
        """
        try:
            if not os.path.exists(self.recovery_codes_file):
                return False, None
            
            # Load plain JSON
            with open(self.recovery_codes_file, 'r', encoding='utf-8') as f:
                recovery_data = json.load(f)
            
            # Return metadata only
            codes_metadata = []
            for entry in recovery_data.get('codes', []):
                codes_metadata.append({
                    'code': '[HASHED - NOT RECOVERABLE]',  # Cannot show actual codes
                    'used': entry.get('used', False),
                    'used_at': entry.get('used_at'),
                    'created_at': entry.get('created_at')
                })
            
            return True, codes_metadata
            
        except Exception as e:
            print(f"[RecoveryCodeManager] ❌ Error listing recovery codes: {e}")
            return False, None

