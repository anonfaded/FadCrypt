<div align="center">
    
<img src="https://github.com/user-attachments/assets/c9fc6bd3-daae-402d-8eeb-828473ede8d4" style="width: 700px; height: auto;" >

<!-- https://github.com/user-attachments/assets/c9eeaf74-6649-4810-b420-e2c4ad4bd365 -->

<br>

| :exclamation: | This project is part of the [FadSec Lab suite](https://github.com/fadsec-lab). <br> Discover our focus on ad-free, privacy-first applications and stay updated on future releases! |
| ------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

---

<img src="https://github.com/user-attachments/assets/c730eda3-5887-458d-8df1-971a74807b73" style="width: 100px; height: auto;" >

# FadCrypt

**Advanced and elegant cross-platform encryption tool – files, folders, and applications all protected with military-grade AES-256-GCM encryption. Open-source, completely free, no telemetry!**

## 🎯 What is FadCrypt?

**FadCrypt** is a comprehensive dual-mode security solution that protects both your files and your applications:

### 🖥️ **GUI Mode: Application Locking**
Protect your installed applications (Firefox, Chrome, Brave, VS Code, etc.) with encrypted password locks. Once locked, the app cannot be launched without your master password. FadCrypt continuously monitors your system in the background and:
- **Scans for running processes** matching your protected applications (e.g., firefox.exe, chrome.exe, brave.exe)
- **Terminates processes instantly** if an app is launched without permission
- **Auto-locks after inactivity:** Once you unlock an app and provide the correct password, it stays unlocked for **10 seconds of inactivity**, then automatically re-locks for security
- Logs all access attempts and lock/unlock events for your activity dashboard

### 💾 **CLI Mode: File & Folder Encryption**
Encrypt and lock sensitive files and folders using military-grade **AES-256-GCM encryption**. All data is encrypted before storage:
- **Encryption Process:** Master password → PBKDF2 key derivation (100,000 iterations) → AES-256-GCM encryption → `.fadcrypt` file
- **Decryption Process:** Provide password → Derive key from stored salt → Verify authentication tag → Decrypt data → Restore original file
- **File Protection:** Windows uses ACL (Access Control Lists), Linux uses chmod + immutability flags
- Perfect for protecting documents, photos, archives, source code, and other sensitive data

**Key Highlights:**
- **Cross-Platform:** Windows and Linux with unified CLI and separate optimized GUIs
- **Military-Grade Encryption:** AES-256-GCM with PBKDF2 key derivation (100,000 iterations)
- **Fully Encrypted:** Configuration, passwords, and recovery codes are all encrypted
- **No External Dependencies:** Open-source and completely free with no cloud sync or telemetry

[![GitHub all releases](https://img.shields.io/github/downloads/anonfaded/FadCrypt/total?label=Downloads&logo=github)](https://github.com/anonfaded/FadCrypt/releases/)

[![ko-fi badge](https://img.shields.io/badge/buy_me_a-coffee-red)](https://ko-fi.com/D1D510FNSV)
[![Discord](https://img.shields.io/discord/1263384048194027520?label=Join%20Us%20on%20Discord&logo=discord)](https://discord.gg/kvAZvdkuuN)

<!-- <img alt="Discord" src="https://img.shields.io/discord/1263384048194027520?style=social&logo=discord&label=Join%20chat&color=red"> -->

<br>
<br>

</div>

<p align="center">
        <img src="https://raw.githubusercontent.com/bornmay/bornmay/Update/svg/Bottom.svg" alt="Github Stats" />
</p>

---

<details>
    <summary>Expand Table of Contents</summary>
    
<br>

- [FadCrypt](#fadcrypt)
  - [📱 Screenshots](#-screenshots)
  - [How FadCrypt Works:](#how-fadcrypt-works)
  - [⬇️ Download](#️-download)
  - [Features:](#features)
  - [Featured On](#featured-on)
  - [Join Community](#join-community)
  - [Support](#support)
  - [Contributions](#contributions)
    - [How to Contribute](#how-to-contribute)
- [Install Dependencies \& Build](#install-dependencies--build)
- [Reset Password](#reset-password)
  - [1. Terminate the app processes (if running)](#1-terminate-the-app-processes-if-running)
  - [2. Delete the password binary file](#2-delete-the-password-binary-file)
</details>

---

## 📱 Screenshots

<div align="center">
<!--     <img src="https://github.com/anonfaded/FadCam/assets/124708903/4a93c111-fc67-4d75-94b1-fa4e01822998" style="width: 50px; height: auto;" >
    <br>
    <em>apk icon</em> -->
    <br><br>
    <img src="https://github.com/user-attachments/assets/b81daec5-8c0f-49f0-9cac-bec61d303eef" style="width: 500px; height: auto;" >
    <img src="https://github.com/user-attachments/assets/df93ac6d-d8eb-45e7-b150-3a1e6d6a80c2" style="width: 500px; height: auto;" >
    <img src="https://github.com/user-attachments/assets/28db5d03-0b08-47fa-bdc6-01244947c124" style="width: 500px; height: auto;" >
    <img src="https://github.com/user-attachments/assets/01e1a2b1-8cdf-40a2-95e0-41109c07db5c" style="width: 500px; height: auto;" >
    <img src="https://github.com/user-attachments/assets/bcbf1b09-6920-46fb-8c3d-b475536060a0" style="width: 500px; height: auto;" >
    <img src="https://github.com/user-attachments/assets/b016d43d-0105-46b5-b2eb-5c697230fcd8" style="width: 500px; height: auto;" >
    <img src="https://github.com/user-attachments/assets/ec7dcc78-2a36-42ef-81a3-8cdda3e33195" style="width: 500px; height: auto;" >
 <br>

<!--     <br> -->
<!--     <em>UI</em> -->

</div>
<!--     <details>
        <summary><strong>More Screenshots</strong></summary>
        <img src="/img/3.png" style="width: 700px; height: auto;" >
        <br>
        <img src="/img/4.png" style="width: 700px; height: auto;" >
        <br>
        <img src="/img/5.png" style="width: 700px; height: auto;" >
    </details> -->
    
## How FadCrypt Works:

### File & Folder Encryption (CLI Mode)

**Encryption Process:**
1. You provide a file/folder path and your master password via the CLI (`fadcrypt --lock <path>`)
2. FadCrypt derives a unique encryption key from your password using PBKDF2-SHA256 (100,000 iterations)
3. The file content is encrypted using AES-256-GCM (authenticated encryption)
4. The encrypted data is written to a new `.fadcrypt` file with metadata and authentication tag
5. Original file is securely overwritten and deleted
6. File protection rules are applied (Windows ACL or Linux chmod/chattr) to prevent unauthorized access

**Decryption Process:**
1. You run `fadcrypt --unlock <path.fadcrypt>` and provide your master password
2. FadCrypt derives the same encryption key from your password using the stored salt
3. The authentication tag is verified to ensure file integrity and authenticity
4. AES-256-GCM decrypts the file content back to its original form
5. The decrypted data is written back to the original file
6. The `.fadcrypt` file is deleted after successful decryption
7. File protection is removed, returning full access to the decrypted file

**File Format (.fadcrypt):**
- Header: Custom format identifier and version
- Metadata: Original filename, file size, timestamps
- Salt: Random salt for PBKDF2 key derivation (unique per file)
- IV: Initialization vector for AES-256-GCM
- Encrypted Data: Actual file content encrypted with AES-256-GCM
- Auth Tag: GCM authentication tag for integrity verification

### Application Locking (GUI Mode)

**Lock Process:**
1. Select applications from your system in the GUI interface (e.g., Firefox, Chrome, Brave, VS Code)
2. FadCrypt registers these applications in its configuration database (stored in plain JSON for easy access by the GUI)
3. **Process Monitoring:** FadCrypt scans system processes in real-time to detect if any registered app is launched
   - For browsers: Detects Firefox, Chrome, Brave, Edge, and other Chromium-based browsers by scanning process names and command lines
   - For standard apps: Matches by executable path and process name
   - System processes are filtered out to prevent accidental termination
4. **Process Termination:** When a protected app is detected running:
   - The app process is immediately terminated (killed) and cannot execute
   - User sees a lock notification with a password prompt
   - The app remains locked until password is verified

**Unlock & Session Timeout Process:**
1. User runs the protected app → FadCrypt detects the launch attempt
2. Password dialog appears; user must enter the master password
3. **Session Grant:** If password is correct, the app is temporarily unlocked
4. **Auto-Lock on Inactivity:** The app stays unlocked for **10 seconds with no activity**
5. **Re-lock:** After 10 seconds of inactivity, FadCrypt automatically re-locks the app
6. On next launch attempt, password is required again
7. Note: Session timeout is based on inactivity of the process; actual app usage continues normally

### Core Encryption Technology (Both Modes)

**1. Encryption Algorithm: AES-256-GCM**
- **Security Level:** 256-bit keys providing military-grade encryption resistant to all known attacks
- **Authentication:** GCM (Galois/Counter Mode) provides authenticated encryption with built-in integrity checking
  - Every decryption attempt verifies the authentication tag
  - Tampering detection: If file is modified, decryption fails and returns error
  - Cannot decrypt without the exact original password

**2. Key Derivation: PBKDF2-SHA256**
- **Iterations:** 100,000 iterations (slow-by-design to prevent brute-force attacks)
- **Process:** Your master password → PBKDF2-SHA256 (100K iterations) + random salt → 256-bit key
- **Purpose:** Converts human-readable password into cryptographic key
- **Rainbow Table Prevention:** Unique salt per file/config prevents pre-computed hash attacks
- **Computational Cost:** Even with modern GPUs, brute-forcing a strong password would take centuries

**3. Encryption Process (CLI Mode - File/Folder):**
1. User selects file/folder and provides master password via CLI (`fadcrypt --lock <path>`)
2. Random salt is generated and stored in file header
3. Master password + salt → PBKDF2 derives 256-bit encryption key
4. File content is read into memory
5. AES-256-GCM encrypts file content with the derived key
6. Authentication tag is computed (ensures data integrity)
7. New `.fadcrypt` file created with:
   - Header: Format identifier and version info
   - Metadata: Original filename, file size, timestamps
   - Salt: Random salt for this file (unique per file)
   - IV (Initialization Vector): Random nonce for AES-GCM
   - Encrypted Data: The encrypted file content
   - Auth Tag: GCM authentication tag for integrity verification
8. Original file is securely overwritten with random data and deleted
9. File protection rules applied (Windows ACL or Linux chmod/chattr)

**4. Decryption Process (CLI Mode - File/Folder):**
1. User runs `fadcrypt --unlock <path.fadcrypt>` and provides master password
2. `.fadcrypt` file is read and parsed:
   - Salt is extracted from file
   - IV is extracted from file
   - Encrypted data is extracted
   - Auth tag is extracted
3. Master password + extracted salt → PBKDF2 derives the same 256-bit key
4. AES-256-GCM decryption:
   - Verifies authentication tag first (aborts if tampering detected)
   - Decrypts data using derived key and IV
   - Returns original file content
5. Decrypted content written back to original filename
6. `.fadcrypt` file deleted
7. File protection removed (original permissions restored)
8. Lock event logged to activity history

**5. Data Integrity & Atomicity:**
- **Atomic Operations:** Temporary file pattern + atomic move (no partial writes on failure)
- **Rollback on Error:** If encryption/decryption fails at any step, original file unchanged
- **Verification:** Authentication tag ensures no tampering or corruption
- **No Plaintext on Disk:** Original plaintext never remains on disk after encryption

**6. Configuration Storage (Both Modes):**
- **Windows:**
  - Config: `%APPDATA%\FadCrypt\config\apps_config.json` (plain JSON, readable by GUI)
  - Password: `encrypted_password.bin` (AES-256 encrypted master password)
  - Backup: `C:\ProgramData\FadCrypt\Backup\` (encrypted backups)
- **Linux:**
  - Config: `~/.config/FadCrypt/config/apps_config.json` (plain JSON, readable by GUI)
  - Password: `~/.config/FadCrypt/encrypted_password.bin` (AES-256 encrypted master password)
  - Backup: `~/.local/share/FadCrypt/Backup\` (encrypted backups)

### Platform-Specific Implementation

#### Windows
- **File Protection:** ACL (Access Control List) via `icacls` command
  - Backs up original ACLs before locking
  - Denies all access to locked files/folders
  - Restores ACLs atomically on unlock
- **Elevation / Service:** Windows service installed by the Inno Setup installer (service is the recommended elevation mechanism)
- **Autostart:** Windows Registry (`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`)
- **Installation:** Inno Setup installer with context menu integration

#### Linux
- **File Protection:** Permission-based via `chmod` + immutability flags via `chattr`
  - Backs up original permissions before locking
  - Sets `chmod 000` to deny all access
  - Sets `chattr +i` to make files immutable (requires root)
  - Restores permissions atomically on unlock
- **Elevation:** Root daemon service with Unix socket communication
  - `fadcrypt-elevated.service` (systemd service)
  - Seamless root operations via socket IPC
  - No password prompts during normal operation
- **Autostart:** `.desktop` file in `~/.config/autostart/`
- **Installation:** Debian package (`.deb`) with automatic daemon setup

### Unified CLI Interface (Both Platforms)

```bash
# Lock files/folders (requires master password)
fadcrypt --lock ./file.txt ./folder/

# Unlock files/folders (requires master password)
fadcrypt --unlock ./file.txt ./folder/

# List locked items
fadcrypt --list

# Start TUI (interactive menu)
fadcrypt

# Start GUI application
fadcrypt --gui

# Auto-monitor mode (startup daemon)
fadcrypt --auto-monitor
```

### Password & Recovery System (Both Platforms)

- **Master Password:** Securely encrypted using PBKDF2 key derivation
- **Recovery Codes:** Generate 10 one-time recovery codes for password reset
  - Stored encrypted in `recovery_codes.json`
  - Each code can be used once; remaining codes stay valid until used or until you choose to regenerate a fresh set
- **Password Reset:** Use recovery code to set new master password
- **Cache:** Password cached in memory during session for seamless operations

### Monitoring Mode (Both Platforms)

When monitoring (auto-monitor) is enabled:
1. **Auto-startup:** Launches automatically on system boot with the `--auto-monitor` flag or via the installed autostart entry
2. **UI-less Auto-Monitor:** Runs without showing the GUI when configured (the app continues to operate without a visible window)
3. **Scope:** Real-time monitoring primarily applies to applications managed by FadCrypt (the "Applications" protection features). File and folder locking/encryption is performed manually via the CLI or context menu (Windows) and is not automatically recovered by the monitor.
4. **Statistics & Logs:** Activity logs and statistics are stored locally for the user's dashboard only; no external telemetry is collected.
5. **Password Security:** Monitoring control requires the master password to stop or alter protection settings

### Security Features (Both Platforms)

**Mutex Protection:** Single instance enforcement prevents multiple instances

**Monitoring Control:** When monitoring is active, control operations that stop monitoring or alter protection require the master password.

**Optional System Tool Lockdown:** (User-configurable) Prevent access to certain system tools while protection is active.
  - **Windows:** Task Manager, Registry Editor, Command Prompt, Control Panel, msconfig
  - **Linux:** Terminal emulators (gnome-terminal, konsole, xterm), system monitors (htop, top, gnome-system-monitor)

**Config Protection:** Critical config files are backed up and protected; the daemon manages file immutability and restoration where applicable.

## Password Creation & Setup

When you first run FadCrypt:

1. **Password Creation:** Set a strong master password
2. **Recovery Codes:** Generate 10 emergency recovery codes and store them securely
3. **Configuration:** Choose preferences (UI theme, dialog style, etc.)
4. **Ready:** FadCrypt is now ready to lock files/folders

If you forget your password:
- Use one of the recovery codes to set a new password
- Each recovery code is single-use; other codes remain valid until used or until you regenerate a fresh set

## ⬇️ Download

Download the latest installers from the [releases page](https://github.com/anonfaded/FadCrypt/releases/).

[<img src="https://raw.githubusercontent.com/vadret/android/master/assets/get-github.png" alt="Get it on GitHub" height="70">](https://github.com/anonfaded/FadCrypt/releases)

## Features:

- **Application Locking:** Secure apps with encrypted password protection; password cannot be recovered if lost and tool cannot be stopped without it.
- **Real-time File Protection:** Detects and auto-recovers critical files/folders if deleted or modified.
- **Recovery Codes:** Generate and use recovery codes to reset forgotten password securely (non-bypassable, one-time use).
- **Auto-Startup Monitoring:** Automatically starts monitoring on system boot with seamless initialization.
- **Statistics & Activity Logging:** Detailed monitoring statistics with activity history and duration tracking.
- **Customizable UI:** Choose password dialog styles, UI themes, and system tray integration.
- **Cross-Platform:** Works on both Windows and Linux with platform-specific features.

**Security (Windows & Linux):**

- **Optional System Tools Disabled (User Configurable):**
  - **Windows:** Task Manager, Registry Editor, Command Prompt, Control Panel, msconfig
  - **Linux:** Terminal emulators (gnome-terminal, konsole, xterm), system monitors (htop, top, gnome-system-monitor)
- **Encrypted Storage:** All passwords and configuration data encrypted using industry-standard cryptography.
- **File Immutability & Elevation:**
  - **Windows:** Task Scheduler-based privilege elevation with persistent session authorization (equivalent to PolicyKit)
  - **Linux:** Root daemon service with Unix socket communication for seamless elevated operations
- **Single Instance Enforcement:** Only one FadCrypt instance can run at a time to prevent bypass attempts.
- **Professional Authorization (Both Platforms):**
  - **Windows:** Single UAC prompt cached per session via Task Scheduler
  - **Linux:** Automatic root daemon service (no authentication required)

**Extras:**

- **Snake Game:** Classic arcade Snake game available on home tab for entertainment.
- **System Tray Integration:** Quick access from system tray with minimize/restore functionality.
- **Auto-Recovery:** Crashes are detected and monitored files are recovered automatically on next startup.

**Daemon Architecture (Linux):**

FadCrypt uses a client-daemon architecture for maximum security:

- **Root Daemon:** `fadcrypt-elevated.service` runs as systemd service with full root privileges
- **Unix Socket Communication:** Secure IPC between GUI and daemon
- **Capabilities:** File protection (chattr), permissions (chmod), backup restoration, kernel monitoring (fanotify)
- **Installation:** Automatically configured with .deb package

**Implemented Features:**

✅ Password-protected app locking & monitoring
✅ Real-time file/folder protection from deletion
✅ Auto-recovery if files are deleted
✅ Recovery codes for password reset
✅ Auto-startup after system reboot (silent with --auto-monitor)
✅ Single-instance enforcement
✅ Detailed statistics & activity monitoring
✅ Customizable dialog styles & preferences
✅ Encrypted password & config storage
✅ Critical files protected from tampering
✅ Password-secured monitoring control
✅ Windows: Task Scheduler-based privilege elevation (UAC caching)
✅ Linux: Root daemon service with Unix socket communication (systemd)
✅ Cross-platform (Windows + Linux)

## Command-Line Interface (CLI)

FadCrypt provides a complete CLI interface for automation and scripting on both platforms:

### Usage Examples

```bash
# Lock a file or folder
fadcrypt --lock ./sensitive_file.txt
fadcrypt --lock /path/to/folder1 /path/to/folder2

# Unlock files/folders
fadcrypt --unlock ./sensitive_file.txt
fadcrypt --unlock /path/to/folder1 /path/to/folder2
# Note: You can also unlock using the encrypted .fadcrypt filename; it will be mapped to the same file
fadcrypt --unlock ./sensitive_file.txt.fadcrypt

# List all locked items with details
fadcrypt --list

# Start interactive TUI (Text User Interface)
fadcrypt

# Start GUI application
fadcrypt --gui

# Auto-monitor mode (runs at startup)
fadcrypt --auto-monitor

# Show version information
fadcrypt --version

# Show help
fadcrypt --help

# Enable verbose logging (shows all operations)
fadcrypt --lock ./file.txt --verbose
```

### CLI Features

**Cross-Platform Compatibility:**
- Identical command syntax on Windows and Linux
- Automatic platform detection for ACL (Windows) or chmod (Linux) operations
- Unified error messages and user feedback

**Password Management:**
- First run prompts for master password creation
- Subsequent operations require password authentication
- Recovery code support for password resets
- Password caching during session to prevent repeated prompts

**Encryption Features:**
- Files: AES-256-GCM stream encryption
- Folders: Tar archive + AES-256-GCM encryption (preserves structure)
- Metadata: Automatic hash verification and integrity checks
- Atomic Operations: Safe temporary file handling with automatic rollback on errors

**Error Handling:**
- Detailed error messages for troubleshooting
- Prevents locking of system paths
- Detects already-locked items and prevents double-locking
- Automatic recovery on interrupted operations

### Installation & Setup

#### Windows

1. **Download:** Get the installer from the [releases page](https://github.com/anonfaded/FadCrypt/releases)
2. **Install:** Run `FadCrypt-Setup.exe` and follow the wizard
3. **Run:** After installation you can run `fadcrypt` from Command Prompt or PowerShell, or search for "FadCrypt" in the Start menu and launch the GUI app
4. **Context Menu:** Right-click files/folders to lock/unlock directly (installed by the installer)

#### Linux

1. **Install Package:** `sudo apt install ./fadcrypt_X.Y.Z_amd64.deb` (or use your distribution's package manager for the release package)
   - The `.deb` package installs and enables the elevated daemon service automatically; no separate manual enable steps are required
2. **Command:** Run `fadcrypt` from terminal (also available from your desktop launcher after installation)
3. **First Run:** Set master password and generate recovery codes

### Linux-Specific Notes

**Daemon Service:**
- **Name:** `fadcrypt-elevated.service`
- **Status:** Check with `systemctl status fadcrypt-elevated.service`
- **Logs:** View with `journalctl -u fadcrypt-elevated.service -f`
- **Manual Start:** `sudo systemctl start fadcrypt-elevated.service`
- **Manual Stop:** `sudo systemctl stop fadcrypt-elevated.service`

**File Operations:**
- Lock operations use `chmod 000` + `chattr +i` (managed by daemon)
- Unlock operations restore original permissions
- All operations logged to `~/.config/FadCrypt/logs/`

**Socket Communication:**
- Client-server via Unix socket: `/run/fadcrypt/elevated.sock`
- Automatic retry on connection failure
- Timeout: 30 seconds per operation

## Featured On

- [VPN Club on Telegram](https://t.me/s/wbnet?q=fadcrypt)
- [popMods on Telegram](https://t.me/s/popmods?q=fadcrypt)
- [blog.csdn.net](https://blog.csdn.net/qq_29607687/article/details/141366524)
<!-- - [rhkb.cn](http://www.rhkb.cn/news/405585.html) -->

## Join Community

Join our [Discord server](https://discord.gg/kvAZvdkuuN) to share ideas, seek help, or connect with other users. Your feedback and contributions are welcome!

[![Discord](https://img.shields.io/discord/1263384048194027520?label=Join%20Us%20on%20Discord&logo=discord)](https://discord.gg/kvAZvdkuuN)

## Support

<a href='https://ko-fi.com/D1D510FNSV' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi3.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>

## Contributions

We welcome any contributions to improve this project! Whether it's bug fixes or new features, your help is appreciated.

### How to Contribute

1. **Discuss First**: Before starting work, please discuss your ideas:
   - Open an [issue](https://github.com/anonfaded/FadCrypt/issues) to discuss the bug or feature
   - Join our [Discord server](https://discord.gg/kvAZvdkuuN) to chat with maintainer and community
   - This helps avoid duplicate work and ensures your contribution aligns with project goals
2. **Check Issues**: Browse existing [issues](https://github.com/anonfaded/FadCrypt/issues) to see where you can help.
3. **Fork the Repo**: Once approved, fork the repository to make your changes.
4. **Submit a PR**: Create a pull request with a clear description of your changes.

**Note:** Please avoid submitting PRs without prior discussion to ensure efficient collaboration.

We look forward to your contributions!

# Install Dependencies & Build

**Linux Prerequisites:**

**Note for Emoji Rendering:** If emojis appear as white outline glyphs instead of colored emojis in your terminal, install GNOME Terminal and set it as the default:

```bash
sudo apt install gnome-terminal
sudo update-alternatives --config x-terminal-emulator
# Select gnome-terminal from the list
```

This ensures proper color emoji rendering in CLI verbose output.

**Install Python Dependencies:**

You can install all required Python packages using pip:

```bash
pip install -r requirements.txt
```

**Build the Application:**

For Windows:

```bash
python -m PyInstaller FadCrypt.spec
```

For Linux:

```bash
python3 -m PyInstaller FadCrypt_Linux.spec
```

**Linux .deb Package Installation:**

For the best Linux experience, use the pre-built .deb package:

```bash
# Download from releases and install
sudo dpkg -i fadcrypt_X.X.X_amd64.deb

# Daemon service installs and starts automatically
# No additional configuration needed
```

Includes: Main application, elevated daemon service, desktop integration, automatic cleanup.

# Reset Password

Follow the steps below to regain access to FadCrypt, or download the guide as a PDF for reference:  
[FadCrypt_Reset_Password_Guide.pdf](https://github.com/user-attachments/files/19832431/FadCrypt_Reset_Password_Guide.pdf)

## 1. Terminate the app processes (if running)

1. Open the search box: `Windows key + S`
2. Type **"PowerShell"**, right-click, and select **"Run as administrator"**
3. In the PowerShell window, enter the following command to kill all running instances of FadCrypt:

```powershell
Stop-Process -Name "fadcrypt" -Force
```

## 2. Delete the password binary file

_(This allows you to create a new password without needing the old one)_

**On Windows:**

1. Navigate to and delete the following file:

```
C:\Users\<YourUsername>\AppData\Roaming\FadCrypt\encrypted_password.bin
```

2. Also delete the backup copy from:

```
C:\ProgramData\FadCrypt\Backup\encrypted_password.bin
```

**On Linux:**

1. Navigate to and delete the following file:

```
~/.FadCrypt/encrypted_password.bin
```

2. Also delete the backup copy from:

```
~/.local/share/FadCrypt/Backup/encrypted_password.bin
```

Now you can open the app again and set a new password — it'll work like a charm!
