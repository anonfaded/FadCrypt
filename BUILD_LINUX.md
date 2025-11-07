# Building FadCrypt for Linux

## Prerequisites

Install build dependencies:

```bash
sudo apt install python3 python3-pip python3-dev build-essential

# Install Python dependencies from the pinned requirements file
pip install -r requirements.txt
pip install pyinstaller
```

## Build Steps

### 1. Build GUI Executable (console=False)
```bash
pyinstaller --clean FadCrypt_Linux.spec
```
Creates: `dist/fadcrypt`

### 2. Build CLI Executable (console=True)
```bash
pyinstaller --clean FadCrypt_Linux_CLI.spec
```
Creates: `dist/fadcrypt-cli`

### 3. Create .deb Package (includes both binaries)
```bash
chmod +x build-deb.sh
./build-deb.sh
```
Creates: `fadcrypt_<version>_amd64.deb`

## Installation

### From .deb package
```bash
sudo dpkg -i fadcrypt_<version>_amd64.deb
```

### Manual installation (without package)
```bash
sudo cp dist/fadcrypt /usr/bin/
sudo cp dist/fadcrypt-cli /usr/bin/
sudo cp debian/fadcrypt.desktop /usr/share/applications/
sudo cp debian/fadcrypt-cli.desktop /usr/share/applications/
sudo cp img/1.png /usr/share/pixmaps/fadcrypt.png
sudo cp img/fadcrypt_cli.png /usr/share/pixmaps/fadcrypt_cli.png
```

## Usage

### GUI Mode
- From application menu: Search for "FadCrypt"
- Or run: `fadcrypt` or `fadcrypt --gui`

### CLI/TUI Mode
- From application menu: Search for "FadCrypt CLI"
- Or run: `fadcrypt-cli` or `fadcrypt-cli --cli`

### Direct Commands
```bash
fadcrypt-cli --lock file       # Lock a file
fadcrypt-cli --unlock file     # Unlock a file
fadcrypt-cli --list            # List locked items
```

## Package Structure

After installation, the .deb provides:

- **GUI Binary:** `/usr/bin/fadcrypt` (console=False, launches GUI)
- **CLI Binary:** `/usr/bin/fadcrypt-cli` (console=True, launches TUI)
- **Daemon Script:** `/usr/share/fadcrypt/elevated-daemon.py`
- **Systemd Service:** `/etc/systemd/system/fadcrypt-elevated.service`
- **Desktop Files:** 
  - `/usr/share/applications/fadcrypt.desktop` (GUI launcher)
  - `/usr/share/applications/fadcrypt-cli.desktop` (CLI launcher)
- **Icons:** 
  - `/usr/share/pixmaps/fadcrypt.png` (GUI)
  - `/usr/share/pixmaps/fadcrypt_cli.png` (CLI)
- **Documentation:** `/usr/share/doc/fadcrypt/`
- **User Config:** `~/.config/FadCrypt/`
- **User Backups:** `~/.local/share/FadCrypt/Backup/`

## Daemon Service

The `.deb` package automatically installs and enables the systemd daemon:

```bash
# View status
sudo systemctl status fadcrypt-elevated.service

# View logs
sudo journalctl -u fadcrypt-elevated.service -f

# Restart service
sudo systemctl restart fadcrypt-elevated.service

# Stop service
sudo systemctl stop fadcrypt-elevated.service

# Start service
sudo systemctl start fadcrypt-elevated.service
```

**Service Details:**
- **Name:** `fadcrypt-elevated.service`
- **Configuration:** `/etc/systemd/system/fadcrypt-elevated.service`
- **Socket:** `/run/fadcrypt/elevated.sock`

## Auto-start (Monitoring Mode)

When you enable monitoring in FadCrypt GUI:

1. Creates: `~/.config/autostart/FadCrypt.desktop`
2. Exec: `fadcrypt --auto-monitor`
3. Will start automatically on next system boot

To disable:
- Open FadCrypt GUI and click "Stop Monitoring"
- Or delete: `~/.config/autostart/FadCrypt.desktop`

## File Protection Mechanism

### How It Works

When you lock a file or folder:

1. **Backup:** Original permissions saved to `~/.config/FadCrypt/permission_backups/`
2. **Lock:** Applied via daemon:
   - `chmod 000` - Remove all permissions
   - `chattr +i` - Set immutable flag
3. **Encryption:** File encrypted to `.fadcrypt` format (optional)

When you unlock:

1. **Immutability Removed:** Daemon removes immutable flag
2. **Permissions Restored:** Original permissions restored
3. **Decryption:** `.fadcrypt` file decrypted (optional)

### Security Notes

- File operations require root privileges (handled by daemon)
- Immutable flag prevents accidental deletion even by root
- Permissions enforced at filesystem level
- All operations are atomic and recoverable

## Uninstall

```bash
sudo dpkg -r fadcrypt
```

This removes:
- Both GUI and CLI binaries
- Daemon service
- Desktop files and icons
- User config is preserved in `~/.config/FadCrypt/`

## Troubleshooting

**Daemon not starting:**
```bash
sudo journalctl -u fadcrypt-elevated.service -n 20
sudo systemctl restart fadcrypt-elevated.service
```

**Permission denied errors:**
```bash
# Ensure daemon is running
sudo systemctl status fadcrypt-elevated.service

# Check socket exists
ls -la /run/fadcrypt/

# Restart daemon
sudo systemctl restart fadcrypt-elevated.service
```

## Development

For development and testing, run directly from source:

```bash
# Start the development daemon (test-only helper)
sudo python3 tests/start_daemon_dev.py

# Run GUI mode
python3 FadCrypt.py --gui

# Run CLI/TUI mode
python3 FadCrypt.py --cli

# Run with verbose logging
python3 FadCrypt.py --cli --verbose
```


