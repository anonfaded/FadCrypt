# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

a = Analysis(
    ['FadCrypt.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('img', 'img'),  # All image assets
        ('core', 'core'),  # Include all core modules
        ('ui', 'ui'),  # Include all UI modules
        ('core/fonts', 'core/fonts'),  # Include fonts for snake game
        ('version.py', '.'),  # Version info
        ('win_compat.py', '.'),  # Windows compatibility layer
        ('win_mock.py', '.'),  # Mock Windows on Linux for testing
    ],
    hiddenimports=[
        # Version module
        'version',
        # Core modules
        'core',
        'core.autostart_manager',
        'core.config_manager',
        'core.crypto_manager',
        'core.password_manager',
        'core.snake_game',
        'core.unified_monitor',
        'core.file_access_monitor',
        'core.file_lock_manager',
        'core.file_monitor',
        'core.file_protection',
        'core.activity_manager',
        'core.duration_tracker',
        'core.recovery_manager',
        'core.single_instance_manager',
        'core.statistics_manager',
        # Windows-specific core modules
        'core.windows',
        'core.windows.acl_locker',
        'core.windows.cli_lock_handler',
        'core.windows.elevation_manager',
        'core.windows.fadcrypt-elevated-helper',
        'core.windows.file_lock_manager_windows',
        'core.windows.shell_extension',
        # UI modules
        'ui',
        'ui.base',
        'ui.base.main_window_base',
        'ui.components',
        'ui.components.about_panel',
        'ui.components.activity_logs_panel',
        'ui.components.app_grid_widget',
        'ui.components.app_list_widget',
        'ui.components.button_panel',
        'ui.components.file_grid_widget',
        'ui.components.logs_tab_widget',
        'ui.components.settings_panel',
        'ui.components.splash_screen',
        'ui.components.system_tray',
        'ui.dialogs',
        'ui.dialogs.add_application_dialog',
        'ui.dialogs.app_scanner_dialog',
        'ui.dialogs.edit_application_dialog',
        'ui.dialogs.file_protection_auth_dialog',
        'ui.dialogs.password_dialog',
        'ui.dialogs.readme_dialog',
        'ui.dialogs.recovery_dialog',
        # Windows-specific UI modules
        'ui.windows',
        'ui.windows.main_window_windows',
        'ui.windows.enhanced_stats_window',
        'ui.windows.stats_window',
        # External dependencies - PyQt6
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.sip',
        'PyQt6.QtNetwork',
        'PyQt6.QtDBus',
        # External dependencies - Other
        'PIL',
        'PIL.Image',
        'pystray',
        'pystray._win32',
        'pygame',
        'pygame.mixer',
        'cryptography',
        'cryptography.fernet',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.backends',
        'psutil',
        'watchdog',
        'watchdog.observers',
        'watchdog.events',
        # NumPy and PyQtGraph for enhanced stats
        'numpy',
        'numpy.core',
        'numpy.core._multiarray_umath',
        'numpy._core',
        'numpy._core._exceptions',
        'numpy._core.multiarray',
        'pyqtgraph',
        'pyqtgraph.graphicsItems',
        # Pygame for snake game - avoid circular imports
        'pygame.base',
        'pygame.constants',
        'pygame.color',
        'pygame.colordict',
        # Windows-specific modules
        'winreg',
        'ctypes',
        'ctypes.wintypes',
        # Windows compatibility modules
        'win_compat',
        'win_mock',
        # Additional cryptography dependencies
        'cryptography.hazmat.primitives.ciphers',
        'cryptography.hazmat.primitives.kdf.pbkdf2',
        'cryptography.hazmat.primitives.padding',
        # Additional Windows modules
        'msvcrt',
        'nt',
        '_winapi',
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

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FadCrypt',  # Windows executable naming convention
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX to avoid compression issues
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI app, no console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='img/icon.png',  # Application icon
)
