# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import tkinterdnd2

# Resolve paths
base_path = os.path.abspath(os.path.dirname(__file__))
tkdnd_path = os.path.join(os.path.dirname(tkinterdnd2.__file__), 'tkdnd')

# Encryption (if needed, leave as None otherwise)
block_cipher = None

# Analysis block
a = Analysis(
    ['FadCrypt_Linux.py'],
    pathex=[base_path],  # ensure relative imports work
    binaries=[],
    datas=[
        (os.path.join(base_path, 'img'), 'img'),  # Images folder
        (tkdnd_path, 'tkinterdnd2/tkdnd'),         # Required tkdnd binaries
        (os.path.join(base_path, 'ttkbootstrap'), 'ttkbootstrap'),  # Bootstrap themes
    ],
    hiddenimports=[
        'tkinterdnd2',
        'tkinterdnd2.TkinterDnD',
        'ttkbootstrap',
        'ttkbootstrap.themes',
        'PIL',
        'PIL._imagingtk',
        'PIL._tkinter_finder',
        'pystray',
        'pystray._xorg',
        'pygame',
        'cryptography',
        'psutil',
        'watchdog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Create Python archive
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Executable creation
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='fadcrypt',  # Lowercase CLI convention
    debug=False,
    bootloader_ignore_signals=True,  # recommended for Linux GUI apps
    strip=True,                      # reduce size
    upx=True,                        # compress output
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                   # GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,           # macOS only, safe to leave false
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
