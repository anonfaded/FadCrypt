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
        ('core/version.py', '.'),  # Version info
        ('core/win_mock.py', '.'),  # Mock Windows on Linux for testing
    ],
    hiddenimports=[
        # Version module
        'core.version',
        # Core modules
        'core',
        'core.application_manager',
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
        'core.linux',
        'core.linux.file_lock_manager_linux',
        'core.linux.file_encryption_manager_linux',
        'core.linux.elevated_daemon',
        'core.linux.elevated_daemon_client',
        'core.linux.fanotify_client',
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
        'ui.linux',
        'ui.linux.main_window_linux',
        # Windows UI modules for cross-platform testing/development
        'ui.windows',
        'ui.windows.main_window_windows',
        'ui.windows.enhanced_stats_window',
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
        # Curses library (required for CLI/TUI)
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
        'PIL.ImageTk',
        'pystray',
        'pystray._xorg',
        'pygame',
        'pygame.mixer',
        'cryptography',
        'cryptography.fernet',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.backends',
        'cryptography.hazmat.primitives.ciphers',
        'cryptography.hazmat.primitives.ciphers.aead',
        'cryptography.hazmat.primitives.kdf',
        'cryptography.hazmat.primitives.kdf.pbkdf2',
        'cryptography.hazmat.primitives.padding',
        'cryptography.hazmat.primitives.hashes',
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
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary packages to reduce size
        'tkinter',           # Tkinter GUI (we use PyQt6)
        'matplotlib',        # Plotting (not used)
        'IPython',           # Interactive Python (not used)
        'jupyter',           # Jupyter (not used)
        'test',              # Test modules
        'unittest',          # Unit testing
        'pydoc',             # Documentation
        'xml.etree',         # XML parsing (minimal usage)
        'email',             # Email (not used)
        'http',              # HTTP server (not used)
        'urllib3',           # URL library (minimal usage)
        'setuptools',        # Setup tools (not needed at runtime)
        'pip',               # Package installer (not needed)
        'distutils',         # Distribution utils (not needed)
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
    name='fadcrypt-cli',  # CLI version with console
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,           # Strip debug symbols - ENABLED
    upx=True,             # UPX compression - ENABLED
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # CLI app, needs console for TUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,   # Strip binaries in final bundle
    upx=True,     # Compress binaries with UPX
    upx_exclude=[],
    name='FadCryptCLI'
)
