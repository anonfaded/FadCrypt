## Quick orientation for AI coding agents

This repository implements FadCrypt — a cross-platform (Windows + Linux) GUI and CLI app written in Python (PyQt6 GUI) that locks/monitors files and persists encrypted configuration.

### Architecture Overview

**Unified Codebase (Single Entry Point):**
- `FadCrypt.py` — Universal entry point handling both Windows and Linux platforms
  - Platform detection via `platform.system()`
  - Dynamic imports for platform-specific implementations
  - Single CLI interface with platform-specific backends
  - Works on both Windows and Linux with identical command syntax

**Platform-Specific Implementations:**

- **Windows Backend** (`core/windows/`):
  - File protection: ACL (`icacls`) based
  - Elevation / Service: Windows service installed by the Inno Setup installer (service is the recommended elevation mechanism)
  - Autostart: Windows Registry
  - Service: Installed/managed by the Windows installer (Inno Setup)

- **Linux Backend** (`core/linux/`):
  - File protection: chmod + chattr (immutable flags)
  - Elevation: Systemd daemon (`fadcrypt-elevated.service`) with privileged daemon handling elevated operations (installed by the `.deb` package)
  - Autostart: `.desktop` file in `~/.config/autostart/` (UI autostart / auto-monitor mode)
  - Service: Installed and enabled automatically when the `.deb` package is installed

**User Interfaces:**

- **CLI/TUI** (`core/cli/`): Cross-platform terminal interface
  - Commands: `--lock`, `--unlock`, `--list`
  - TUI: Interactive menu-based interface
  - Password management and recovery codes
  - Works identically on Windows and Linux

- **GUI** (`ui/`):
  - `ui/windows/main_window_windows.py` — Windows-specific GUI (PyQt6)
  - `ui/linux/main_window_linux.py` — Linux-specific GUI (PyQt6)
  - `ui/base/main_window_base.py` — Shared base class
  - Platform auto-detected at runtime

Read these files to understand structure:

- `FadCrypt.py` — Universal entry point with platform detection
- `core/cli/cli_handler_base.py` — Abstract CLI interface
- `core/cli/cli_handler_windows.py` — Windows CLI implementation
- `core/cli/cli_handler_linux.py` — Linux CLI implementation
- `core/file_lock_manager.py` — Base lock manager (platform-specific via subclasses)
- `core/windows/file_lock_manager_windows.py` — Windows file protection
- `core/linux/file_lock_manager_linux.py` — Linux file protection
- `README.md` — Complete feature and CLI documentation
- `BUILD_LINUX.md` — Linux building and daemon setup
- `FadCrypt.spec` — PyInstaller configuration

### Core Encryption (Both Platforms)

**Algorithm:** AES-256-GCM with PBKDF2 key derivation
- File format: `.fadcrypt` (custom format with header, metadata, encrypted content)
- Key derivation: PBKDF2-SHA256 with 100,000 iterations
- Atomic operations with temporary file pattern and rollback on errors
- SHA256 verification for data integrity

**Configuration Storage:**
- **Windows:** `%APPDATA%\FadCrypt\config\apps_config.json` + encrypted backups
- **Linux:** `~/.config/FadCrypt/config/apps_config.json` + encrypted backups
- Password stored in: `encrypted_password.bin` (encrypted with master password)
- Recovery codes: `recovery_codes.json` (encrypted storage)

### Big-Picture Architecture Notes

- **Unified CLI:** Both platforms use identical command syntax (`--lock`, `--unlock`, `--list`)
- **Platform Detection:** Runtime detection via `platform.system()` determines behavior
- **Abstraction Layer:** `CLIHandlerBase` and `FileLockManager` provide platform-agnostic interfaces
- **Daemon on Linux:** Root daemon service via systemd (installed with `.deb` package)
- **Service on Windows:** Windows Service (FadCryptElevated) with SYSTEM privileges for elevation
- **Config Locations:** Automatically platform-specific (Windows uses %APPDATA%, Linux uses ~/.config)
- **Versioning:** Manual via `__version__` and `__version_code__` in `FadCrypt.py`

### Important Runtime Flags

- `--lock <path>` — Lock file(s)/folder(s) (both platforms)
- `--unlock <path>` — Unlock file(s)/folder(s) (both platforms)
- `--list` — List all locked items (both platforms)
- `--auto-monitor` — Start monitoring mode at boot (both platforms)
- `--verbose` — Enable debug logging (both platforms)
- `--gui` — Launch GUI explicitly (both platforms)
- `--cli` — Launch TUI explicitly (both platforms)
- `--install-service` — Install Windows service (Windows only)
- `--uninstall-service` — Remove Windows service (Windows only)
- `--register-context` — Register shell context menu (Windows only)
- `--windows` — Mock Windows environment for testing on Linux

### Single-Instance Enforcement

- **Windows:** Mutex-like mechanism via `check_single_instance()`
- **Linux:** Lock file at `/tmp/fadcrypt.lock` with `fcntl` locking
- Both: Only one FadCrypt instance can run at a time (password-protected stop)

### Dependencies & How to Run

**Install all dependencies:**
```bash
# Use the pinned dependency file for reproducible installs
pip install -r requirements.txt
```

**Run on any platform:**
```bash
python3 FadCrypt.py              # Start TUI/GUI (detects platform)
python3 FadCrypt.py --lock file   # Lock file
python3 FadCrypt.py --unlock file # Unlock file
python3 FadCrypt.py --list        # List locked items
python3 FadCrypt.py --gui         # Start GUI explicitly
```

**Build distributables:**
- **Windows:** `python3 -m PyInstaller FadCrypt.spec` (creates .exe)
- **Linux:** `./build-deb.sh` (creates .deb package with daemon service)

### Common Change Patterns

**Adding a feature to both platforms:**

1. Update `core/file_lock_manager.py` (base class method)
2. Implement in `core/windows/file_lock_manager_windows.py` 
3. Implement in `core/linux/file_lock_manager_linux.py`
4. Test on both Windows and Linux

**Adding CLI functionality:**

1. Update `core/cli/cli_handler_base.py` (add method to base class)
2. Implement in `core/cli/cli_handler_windows.py`
3. Implement in `core/cli/cli_handler_linux.py`
4. Call from `handle_direct_cli_commands()` in `FadCrypt.py`

**Fixing UI issues:**

1. For GUI: Update `ui/base/main_window_base.py` (shared) and platform-specific windows
2. For TUI: Update `core/cli/tui_manager.py` (cross-platform)
3. For colors/formatting: Update `core/cli/colors.py` (both TUI and CLI)

**File Protection Logic:**

- Windows: Modify `core/windows/file_lock_manager_windows.py` (_backup_acl, _restore_acl methods)
- Linux: Modify `core/linux/file_lock_manager_linux.py` (_backup_permissions, _restore_permissions methods)
- Base logic: `core/file_lock_manager.py` (add_item, remove_item methods)

### Resource Loading

- PyInstaller bundling uses `resource_path()` function (see `FadCrypt.py`)
- Resources expected at: `img/` and `ui/` directories
- At runtime with PyInstaller: Uses `_MEIPASS` for extracted bundle
- Development mode: Uses current directory

### Safe-Change Checklist

1. Install dependencies: `pip install -r requirements.txt`
2. Test on correct platform or use `--windows` mock flag on Linux
3. For core changes: Update both Windows and Linux implementations
4. For encryption/config changes: Add migration logic and test data recovery
5. For CLI changes: Test with `--lock`, `--unlock`, `--list` commands
6. For UI changes: Test both GUI and TUI modes
7. Encryption changes: Test `.fadcrypt` file format compatibility
8. Update `README.md` and `BUILD_LINUX.md` if adding new features

### Key Files and What They Do

| File | Purpose |
|------|---------|
| `FadCrypt.py` | Universal entry point, platform detection, CLI routing |
| `core/cli/cli_handler_base.py` | Abstract CLI interface, base lock/unlock logic |
| `core/cli/cli_handler_windows.py` | Windows-specific CLI handler |
| `core/cli/cli_handler_linux.py` | Linux-specific CLI handler |
| `core/file_lock_manager.py` | Base file protection logic, abstract methods |
| `core/windows/file_lock_manager_windows.py` | Windows ACL-based protection |
| `core/linux/file_lock_manager_linux.py` | Linux chmod+chattr protection |
| `core/file_encryption_manager.py` | Base encryption logic (AES-256-GCM) |
| `core/windows/file_encryption_manager_windows.py` | Windows-specific encryption setup |
| `core/linux/file_encryption_manager_linux.py` | Linux-specific encryption setup |
| `core/crypto_manager.py` | Core encryption/decryption implementation |
| `core/password_manager.py` | Password handling and recovery codes |
| `core/cli/tui_manager.py` | Text UI menu system (both platforms) |
| `core/linux/elevated_daemon.py` | Linux root daemon service (systemd) |
| `ui/windows/main_window_windows.py` | Windows GUI (PyQt6) |
| `ui/linux/main_window_linux.py` | Linux GUI (PyQt6) |

### Where to Look for Examples

- **CLI commands:** `handle_direct_cli_commands()` in `FadCrypt.py` (lines 1140-1350)
- **Autostart creation:** `AutostartManagerLinux.enable_autostart()` in `core/autostart_manager.py`
- **File locking:** `add_item()` method in `core/file_lock_manager.py`
- **Encryption:** `encrypt_file()` in `core/file_encryption_manager.py`
- **Password recovery:** `verify_password_with_recovery()` in `core/cli/password_prompt.py`
- **TUI:** `TUIManager.run()` in `core/cli/tui_manager.py`
- **GUI:** `MainWindowBase` in `ui/base/main_window_base.py`
- Single-instance lock: search for `fcntl`, `/tmp/fadcrypt.lock`, and any `SingleInstance` class definitions.
- Drag-and-drop and executable detection: look at `on_drop()` and `is_elf_binary()` in `FadCrypt_Linux.py`.

If anything in this file is unclear or you need more specifics (packaging targets, CI steps, or where persistent state is created), tell me which area you want expanded and I will iterate.
