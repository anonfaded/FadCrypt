# Building FadCrypt for Windows

## Prerequisites

```bash
pip install -r requirements.txt
pip install pyinstaller
```

## Build Steps

### 1. Build GUI Executable (console=False)
```bash
python -m PyInstaller FadCrypt.spec --clean --noconfirm
```
Creates: `dist/FadCrypt/FadCrypt.exe`

### 2. Build CLI Executable (console=True)
```bash
python -m PyInstaller FadCryptCLI.spec --clean --noconfirm
```
Creates: `dist/FadCryptCLI/fadcrypt.exe`

### 3. Build Installer (requires Inno Setup)
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" innosetup/FadCrypt-inno-setup-script.iss
```
Creates: `dist/FadCryptSetup.exe`

## Quick Build (PowerShell)
```powershell
.\build-windows.ps1
```
This builds both exes and optionally creates the installer.

## Installation
Run `FadCryptSetup.exe` to install FadCrypt with:
- GUI shortcut: "FadCrypt" (launches GUI)
- CLI shortcut: "FadCrypt CLI" (launches TUI in console)
- Both added to `%PATH%` for command-line access

## Usage

### GUI Mode
```bash
FadCrypt.exe --gui
# or just: FadCrypt.exe
```

### CLI Mode
```bash
fadcrypt --cli          # Interactive TUI
fadcrypt --lock file    # Lock a file
fadcrypt --unlock file  # Unlock a file
fadcrypt --list         # List locked items
```

## Architecture

- **FadCrypt.exe**: GUI application (PyQt6, no console window)
- **fadcrypt.exe**: CLI/TUI application (runs in native console)
- Both share same core code, differ only in console mode
   - CLI: Run `fadcrypt --cli` from any terminal/PowerShell

## Usage

### GUI Mode
```bash
FadCrypt.exe
```

### CLI/TUI Mode
```bash
fadcrypt --cli
```

### Lock Files
```bash
fadcrypt --lock "C:\path\to\file.txt"
```

### Unlock Files
```bash
fadcrypt --unlock "C:\path\to\file.txt"
```

### List Locked Items
```bash
fadcrypt --list
```

## Context Menu

After installation, you can:
- Right-click any file/folder → "🔐 Lock with FadCrypt"
- Right-click any locked file/folder → "🔓 Unlock with FadCrypt"

## Uninstall

Use Windows Control Panel → Programs → Uninstall "FadCrypt"

This will:
- Remove both executables
- Remove from PATH
- Remove context menu entries
- Remove Start Menu shortcuts
- Leave user config in `%APPDATA%\FadCrypt\` (can be manually deleted)

## Troubleshooting

**PowerShell 7+ not found for CLI:**
- Install PowerShell 7+ from: https://github.com/PowerShell/PowerShell/releases
- CLI mode requires pwsh.exe (PowerShell 7+)

**Context menu not appearing:**
- Restart File Explorer: `Ctrl+Shift+Esc` → Find explorer.exe → Restart
- Or reinstall FadCrypt

**Files in use error during unlock:**
- Close any programs using the file
- Try again

## Development

For local development without installer:

```bash
# Run GUI
python FadCrypt.py --gui

# Run CLI/TUI
python FadCrypt.py --cli

# Run with verbose logging
python FadCrypt.py --cli --verbose
```
