# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for FadCrypt CLI - builds console application for --cli mode
# This is SEPARATE from the GUI build (FadCrypt.spec which uses console=False)
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
        # Linux-specific core modules
        'core.linux',
        'core.linux.elevated_daemon_client',
        'core.linux.elevated_daemon',
        'core.linux.fanotify_client',
        'core.linux.file_lock_manager_linux',
        'core.linux.file_encryption_manager_linux',
        # CLI modules
        'core.cli',
        'core.cli.cli_handler_base',
        'core.cli.cli_handler_windows',
        'core.cli.cli_handler_linux',
        'core.cli.colors',
        'core.cli.curses_file_browser',
        'core.cli.curses_menu',
        'core.cli.curses_password',
        'core.cli.help_display',
        'core.cli.menu_navigator',
        'core.cli.password_prompt',
        'core.cli.tui_manager',
        # UI modules (for potential GUI usage)
        'ui',
        'ui.base',
        'ui.base.main_window_base',
        'ui.windows',
        'ui.windows.main_window_windows',
        'ui.linux',
        'ui.linux.main_window_linux',
        'ui.components',
        'ui.dialogs',
        # PyQt6
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        # Utilities
        'colorama',
        'psutil',
        'curses',
    ],
    runtime_hooks=[],
    excludedimports=[],
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
    name='fadcrypt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # CLI app with native console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='img/fadcrypt_cli_ico.ico'  # CLI icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FadCryptCLI',
)
