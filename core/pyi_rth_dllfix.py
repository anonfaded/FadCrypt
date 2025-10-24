# -*- coding: utf-8 -*-
"""
Runtime hook to fix PyInstaller DLL loading on Windows
Executes BEFORE main application code to ensure proper temp folder handling
"""
import sys
import os
import tempfile

# CRITICAL: Set environment variables IMMEDIATELY when PyInstaller loads
if hasattr(sys, '_MEIPASS'):
    # Ensure temp directories are accessible
    temp_dir = tempfile.gettempdir()
    os.environ['TMPDIR'] = temp_dir
    os.environ['TEMP'] = temp_dir
    os.environ['TMP'] = temp_dir
    
    # Set working directory to the bundle directory
    exe_dir = os.path.dirname(sys.executable)
    try:
        os.chdir(exe_dir)
    except Exception:
        pass  # If chdir fails, continue anyway
