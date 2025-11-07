# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

a = Analysis(
    ['FadCrypt.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('img', 'img'),                # Image assets
        ('core', 'core'),              # Core modules
        ('ui', 'ui'),                  # UI modules
        ('core/fonts', 'core/fonts'),  # Fonts for snake game
        ('core/version.py', '.'),      # Version info
        ('core/win_mock.py', '.'),     # Mock Windows on Linux for testing
    ],
    hiddenimports=[
        # Version module
        'core.version',
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
        'core.verbose_logger',
        'core.file_encryption_manager',
        # Windows-specific core modules
        'core.windows',
        'core.windows.acl_locker',
        'core.windows.cli_lock_handler',
        'core.windows.elevation_manager',
        'core.windows.fadcrypt-elevated-helper',
        'core.windows.file_lock_manager_windows',
        'core.windows.file_encryption_manager_windows',
        'core.windows.elevated_service_client',
        'core.windows.fadcrypt_elevated_service',
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
        'ui.dialogs.context_menu_password_dialog',
        'ui.dialogs.edit_application_dialog',
        'ui.dialogs.file_protection_auth_dialog',
        'ui.dialogs.operation_logs_dialog',
        'ui.dialogs.password_dialog',
        'ui.dialogs.readme_dialog',
        'ui.dialogs.recovery_dialog',
        # Windows-specific UI modules
        'ui.windows',
        'ui.windows.main_window_windows',
        'ui.windows.enhanced_stats_window',
        'ui.windows.stats_window',
        # CLI modules
        'core.cli',
        'core.cli.cli_handler_base',
        'core.cli.cli_handler_windows',
        'core.cli.cli_handler_linux',
        'core.cli.password_prompt',
        'core.cli.colors',
        'core.cli.tui_manager',
        'core.cli.menu_navigator',
        'core.cli.help_display',
        'core.cli.curses_password',
        'core.cli.curses_menu',
        'core.cli.curses_file_browser',
        # Curses library (required for CLI password input)
        'curses',
        'curses.ascii',
        'curses.panel',
        'curses.textpad',
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
        # NumPy and PyQtGraph
        'numpy',
        'numpy.core',
        'numpy.core._multiarray_umath',
        'numpy._core',
        'numpy._core._exceptions',
        'numpy._core.multiarray',
        'pyqtgraph',
        'pyqtgraph.graphicsItems',
        # Pygame for snake game
        'pygame.base',
        'pygame.constants',
        'pygame.color',
        'pygame.colordict',
        # Windows-specific modules
        'winreg',
        'ctypes',
        'ctypes.wintypes',
        # Windows compatibility modules
        'core.win_mock',
        # Cryptography extensions
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
    runtime_hooks=['core/pyi_rth_dllfix.py'],
    excludes=[
    'tkinter',
    'tcl',
    '_tkinter',
    'tk',
    'tcl8',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name='FadCrypt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # GUI app - NO console window
    icon='img/1.ico'  # Use .ico file, not .png
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='FadCrypt'
)
