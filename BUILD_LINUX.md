# Building FadCrypt .deb Package for Linux

## Prerequisites

Install build dependencies:

```bash
sudo apt install python3 python3-pip python3-dev build-essential

# Install Python dependencies from the pinned requirements file
pip install -r requirements.txt
```

## Build Process

1. **Build the .deb package:**

   ```bash
   ./build-deb.sh
   ```

2. **Install the package:**

   ```bash
   sudo dpkg -i fadcrypt_X.X.X_amd64.deb
   ```

   This will:
   - Extract FadCrypt binary to `/usr/bin/fadcrypt`
   - Install and enable the elevated daemon service (`fadcrypt-elevated.service`) automatically
   - Create desktop file for application menu

3. **Verify daemon installation:**

   ```bash
   sudo systemctl status fadcrypt-elevated.service
   ```

4. **Run FadCrypt:**

   ```bash
   fadcrypt
   ```

   Or launch from application menu or system launcher.

## Daemon Service

The `.deb` package automatically installs and enables the elevated daemon:

**Service Details:**
- **Name:** `fadcrypt-elevated.service`
- **Configuration:** `/etc/systemd/system/fadcrypt-elevated.service`
- **Socket:** `/run/fadcrypt/elevated.sock`
- **Logs:** `journalctl -u fadcrypt-elevated.service -f`

**Manual Management:**
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

## Uninstall

```bash
# Remove the package
sudo dpkg -r fadcrypt

# This will:
# - Remove FadCrypt binary
# - Stop and disable the daemon service
# - Remove desktop file and icons
# - Leave user config in ~/.config/FadCrypt/ (can be manually deleted)
```

## Package Structure

After installation:

- **Binary:** `/usr/bin/fadcrypt`
- **Daemon Script:** `/usr/share/fadcrypt/elevated-daemon.py`
- **Systemd Service:** `/etc/systemd/system/fadcrypt-elevated.service`
- **Desktop File:** `/usr/share/applications/fadcrypt.desktop`
- **Icon:** `/usr/share/pixmaps/fadcrypt.png`
- **Documentation:** `/usr/share/doc/fadcrypt/`
- **User Config:** `~/.config/FadCrypt/`
- **User Backups:** `~/.local/share/FadCrypt/Backup/`
- **User Logs:** `~/.config/FadCrypt/logs/`

## Auto-start (Monitoring Mode)

When you enable monitoring in FadCrypt UI:

1. Creates: `~/.config/autostart/FadCrypt.desktop`
2. Exec: `fadcrypt --auto-monitor`
3. Will start automatically on next system boot
4. Runs in UI-less auto-monitor mode (the application continues to operate without showing the GUI when configured)

To disable:
- Open FadCrypt and click "Stop Monitoring"
- Or delete: `~/.config/autostart/FadCrypt.desktop`

## File Protection Mechanism

### How It Works

When you lock a file or folder on Linux:

1. **Original State Backup:** Permissions saved to `~/.config/FadCrypt/permission_backups/`
2. **Permission Lock:** Applied via daemon:
   - `chmod 000` - Remove all permissions
   - `chattr +i` - Set immutable flag (managed by the daemon)
3. **Encryption:** File encrypted to `.fadcrypt` format (optional)

When you unlock:

1. **Immutability Removed:** Daemon removes immutable flag: `chattr -i`
2. **Permissions Restored:** Original permissions restored from backup
3. **Decryption:** `.fadcrypt` file decrypted back to original (optional)

### Security Notes

- File operations require root privileges (handled by daemon)
- Immutable flag prevents accidental deletion even by root
- Permissions are enforced at filesystem level (cannot bypass with standard tools)
- All operations are atomic and recoverable

## Troubleshooting

**Daemon not starting:**
```bash
sudo journalctl -u fadcrypt-elevated.service -n 20
sudo systemctl restart fadcrypt-elevated.service
```

**Permission denied errors:**
- Ensure daemon is running: `sudo systemctl status fadcrypt-elevated.service`
- Check socket exists: `ls -la /run/fadcrypt/`
- Restart daemon: `sudo systemctl restart fadcrypt-elevated.service`

**Files showing as question marks:**
- Terminal emoji support issue (try GNOME Terminal)
- See main README for emoji troubleshooting

## Development

For development and daemon testing, use the provided dev starter and run FadCrypt directly:

```bash
# Start the development daemon (test-only helper)
sudo python3 tests/start_daemon_dev.py

# Run the app (TUI by default)
python3 FadCrypt.py

# Run with verbose logging
python3 FadCrypt.py --verbose
```

Note: the installed `.deb` package performs daemon installation and enabling automatically; use the dev starter when developing locally.
