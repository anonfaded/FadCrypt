"""
FadCrypt Context Menu Developer Testing Utility

Auto-creates temp file, tests lock/unlock, and cleans up.
No extra headache - just run it!

Usage (with auto temp file):
    python tests/test_context_menu_dev.py
    python tests/test_context_menu_dev.py -l
    python tests/test_context_menu_dev.py -u

Usage (with specific file):
    python tests/test_context_menu_dev.py --lock <path>
    python tests/test_context_menu_dev.py -l <path>
    python tests/test_context_menu_dev.py --unlock <path>
    python tests/test_context_menu_dev.py -u <path>

Features:
    - Auto-creates temporary test file if no path given
    - Simulates Windows context menu lock/unlock without registry
    - Shows GUI dialogs just like real context menu
    - Displays styled console output
    - Auto-cleans up temp files
"""

import sys
import os
import subprocess
import tempfile
import atexit
from pathlib import Path

# Global temp file to clean up
temp_file_path = None

def cleanup_temp_file():
    """Clean up temporary test file"""
    global temp_file_path
    if temp_file_path and os.path.exists(temp_file_path):
        try:
            os.remove(temp_file_path)
            print(f"\n[DEV TEST] Cleaned up temp file: {temp_file_path}")
        except Exception as e:
            print(f"[DEV TEST] Could not delete temp file: {e}")

# Register cleanup on exit
atexit.register(cleanup_temp_file)

def create_temp_file():
    """Create a temporary test file"""
    global temp_file_path
    try:
        # Create in testFolder if it exists, otherwise in temp dir
        test_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'testFolder')
        if os.path.exists(test_folder):
            fd, temp_file_path = tempfile.mkstemp(prefix='fadcrypt_test_', suffix='.txt', dir=test_folder)
        else:
            fd, temp_file_path = tempfile.mkstemp(prefix='fadcrypt_test_', suffix='.txt')
        
        # Write test content
        with os.fdopen(fd, 'w') as f:
            f.write("This is a FadCrypt context menu test file.\n")
        
        print(f"[DEV TEST] Created temp file: {temp_file_path}")
        return temp_file_path
    except Exception as e:
        print(f"✗ Error creating temp file: {e}")
        return None

def show_usage():
    print("""
╭─ 🔒 FadCrypt Context Menu Dev Testing ─────────────────────────
│
│ AUTO MODE (easiest - creates temp file):
│   python tests/test_context_menu_dev.py         (auto lock/unlock cycle)
│
│ LOCK ONLY:
│   python tests/test_context_menu_dev.py -l      (lock temp file)
│   python tests/test_context_menu_dev.py --lock  (lock temp file)
│
│ UNLOCK ONLY:
│   python tests/test_context_menu_dev.py -u      (unlock temp file)
│   python tests/test_context_menu_dev.py --unlock (unlock temp file)
│
│ CUSTOM FILE:
│   python tests/test_context_menu_dev.py -l <path>
│   python tests/test_context_menu_dev.py -u <path>
│
╰────────────────────────────────────────────────────────────────────
""")

def main():
    operation = None
    file_path = None
    auto_mode = False
    
    # Parse arguments
    if len(sys.argv) == 1:
        # Auto mode - create temp file and test both lock/unlock
        auto_mode = True
        file_path = create_temp_file()
        if not file_path:
            return 1
    elif len(sys.argv) == 2:
        # Just operation, create temp file
        operation = sys.argv[1]
        if operation in ['-l', '--lock', 'lock']:
            operation = '--test-context-lock'
            file_path = create_temp_file()
        elif operation in ['-u', '--unlock', 'unlock']:
            operation = '--test-context-unlock'
            file_path = create_temp_file()
        else:
            print(f"✗ Unknown operation: {operation}")
            show_usage()
            return 1
            
        if not file_path:
            return 1
    elif len(sys.argv) >= 3:
        # Operation with specific file path
        operation = sys.argv[1]
        file_path = sys.argv[2]
        
        # Map short flags to long flags
        if operation == '-l':
            operation = '--test-context-lock'
        elif operation == '-u':
            operation = '--test-context-unlock'
        elif operation == '--lock':
            operation = '--test-context-lock'
        elif operation == '--unlock':
            operation = '--test-context-unlock'
        else:
            print(f"✗ Error: Unknown operation '{operation}'")
            show_usage()
            return 1
        
        # Check if file exists
        file_path = str(Path(file_path).resolve())
        if not os.path.exists(file_path):
            print(f"✗ Error: File not found: {file_path}")
            return 1
    else:
        show_usage()
        return 1
    
    # Get the FadCrypt.py path
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fadcrypt_py = os.path.join(script_dir, 'FadCrypt.py')
    
    if not os.path.exists(fadcrypt_py):
        print(f"✗ Error: FadCrypt.py not found at {fadcrypt_py}")
        return 1
    
    # Auto mode: test lock then unlock
    if auto_mode:
        print(f"\n[DEV TEST] ═══════════════════════════════════════════════")
        print(f"[DEV TEST] Testing LOCK operation...")
        print(f"[DEV TEST] ═══════════════════════════════════════════════")
        
        result1 = subprocess.run(
            [sys.executable, fadcrypt_py, '--test-context-lock', file_path],
            capture_output=False,
            text=True
        )
        
        print(f"\n[DEV TEST] ═══════════════════════════════════════════════")
        print(f"[DEV TEST] Testing UNLOCK operation...")
        print(f"[DEV TEST] ═══════════════════════════════════════════════")
        
        result2 = subprocess.run(
            [sys.executable, fadcrypt_py, '--test-context-unlock', file_path],
            capture_output=False,
            text=True
        )
        
        return max(result1.returncode, result2.returncode)
    else:
        # Single operation
        print(f"[DEV TEST] Starting context menu simulation...")
        print(f"[DEV TEST] Operation: {operation.replace('--test-context-', '').upper()}")
        print(f"[DEV TEST] File: {file_path}\n")
        
        try:
            result = subprocess.run(
                [sys.executable, fadcrypt_py, operation, file_path],
                capture_output=False,
                text=True
            )
            return result.returncode
        except Exception as e:
            print(f"✗ Error executing FadCrypt: {e}")
            return 1

if __name__ == '__main__':
    sys.exit(main())
