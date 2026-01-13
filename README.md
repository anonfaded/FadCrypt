<div align="center">
    
<img src="img/banner-rounded.png" style="width: 700px; height: auto;" >

<!-- https://github.com/user-attachments/assets/c9eeaf74-6649-4810-b420-e2c4ad4bd365 -->

<br>

| :exclamation: | This project is part of the [FadSec Lab suite](https://github.com/fadsec-lab). <br> Discover our focus on ad-free, privacy-first applications and stay updated on future releases! |
| ------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

---

<img src="img/icon.png" style="width: 100px; height: auto;" >

# `>_` FadCrypt

**Advanced and elegant cross-platform encryption tool – files, folders, and applications all protected with military-grade AES-256-GCM encryption. Open-source, completely free, no telemetry!**

[![GitHub all releases](https://img.shields.io/github/downloads/anonfaded/FadCrypt/total?label=Downloads&logo=github)](https://github.com/anonfaded/FadCrypt/releases/)
[![ko-fi badge](https://img.shields.io/badge/buy_me_a-coffee-red)](https://ko-fi.com/D1D510FNSV)
[![Discord](https://img.shields.io/discord/1263384048194027520?label=Join%20Us%20on%20Discord&logo=discord)](https://discord.gg/kvAZvdkuuN)

</div>

## `>_` 🎯 What is FadCrypt?

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
- **Cross-Platform:** Windows and Linux desktop platforms with unified CLI and separate optimized GUIs
- **Military-Grade Encryption:** AES-256-GCM with PBKDF2 key derivation (100,000 iterations)
- **Fully Encrypted:** Configuration, passwords, and recovery codes are all encrypted
- - **No External Dependencies:** Open-source and completely free with no cloud sync or telemetry

---

<details>
    <summary>Expand Table of Contents</summary>
    
<br>

- [FadCrypt](#fadcrypt)
  - [🎯 What is FadCrypt?](#-what-is-fadcrypt)
    - [🖥️ GUI Mode: Application Locking](#️-gui-mode-application-locking)
    - [💾 CLI Mode: File & Folder Encryption](#-cli-mode-file--folder-encryption)
  - [📱 Screenshots](#-screenshots)
    - [🖥️ GUI Mode - Application Locking](#️-gui-mode---application-locking)
    - [💻 CLI/TUI Mode - File & Folder Encryption](#-clutui-mode---file--folder-encryption)
  - [How FadCrypt Works:](#how-fadcrypt-works)
    - [File & Folder Encryption (CLI Mode)](#file--folder-encryption-cli-mode)
    - [Application Locking (GUI Mode)](#application-locking-gui-mode)
    - [Core Encryption Technology (Both Modes)](#core-encryption-technology-both-modes)
    - [Platform-Specific Implementation](#platform-specific-implementation)
    - [Unified CLI Interface (Both Platforms)](#unified-cli-interface-both-platforms)
    - [Password & Recovery System (Both Platforms)](#password--recovery-system-both-platforms)
    - [Monitoring Mode (Both Platforms)](#monitoring-mode-both-platforms)
    - [Security Features (Both Platforms)](#security-features-both-platforms)
  - [Password Creation & Setup](#-password-creation--setup)
  - [⬇️ Installation & Setup](#️-installation--setup)
    - [Windows](#windows)
    - [Linux](#linux)
    - [ℹ️ Linux-Specific Details](#️-linux-specific-details)
  - [Features:](#-features)
  - [Command-Line Interface (CLI)](#️-command-line-interface-cli)
    - [Usage Examples](#usage-examples)
    - [CLI Features](#cli-features)
    - [Tamper-Proof Protection Control](#tamper-proof-protection-control)
  - [Performance](#️-performance)
  - [Featured On](#️-featured-on)
  - [Join Community](#️-join-community)
  - [Support](#️-support)
  - [Contributions](#️-contributions)
    - [How to Contribute](#how-to-contribute)
  - [Install Dependencies & Build](#️-install-dependencies--build)
    - [📦 Build Instructions (Windows & Linux)](#-build-instructions-windows--linux)
  - [Reset Password](#-reset-password)
</details>

---

## `>_` 📱 Screenshots

### 🖥️ GUI Mode - Application Locking

<table>
<tr>
<td align="center"><img src="img/demo/gui/hometab.png" width="300"><br><em><strong>Home Tab</strong> - Dashboard with overview</em></td>
<td align="center"><img src="img/demo/gui/applicationstab.png" width="300"><br><em><strong>Applications Tab</strong> - Lock and manage apps/software</em></td>
</tr>
<tr>
<td align="center"><img src="img/demo/gui/filesandfolderstab.png" width="300"><br><em><strong>Files & Folders Tab</strong> - View encrypted files</em></td>
<td align="center"><img src="img/demo/gui/activitytab.png" width="300"><br><em><strong>Activity Tab</strong> - Track events and access</em></td>
</tr>
<tr>
<td align="center"><img src="img/demo/gui/settingstab.png" width="300"><br><em><strong>Settings Tab</strong> - Recovery codes & preferences</em></td>
<td align="center"><img src="img/demo/gui/windows_contextmenu.png" width="300"><br><em><strong>Context Menu</strong> - Right-click lock/unlock *(Windows)*</em></td>
</tr>
<tr>
<td align="center"><img src="img/demo/gui/configtab.png" width="300"><br><em><strong>Config Tab</strong> - Application configuration</em></td>
<td align="center"><img src="img/demo/gui/statswindow.png" width="300"><br><em><strong>Statistics Window</strong> - Activity & uptime</em></td>
</tr>
<tr>
<td align="center"><img src="img/demo/gui/fadguidetab1.png" width="300"><br><em><strong>FadGuide Tab 1</strong> - Interactive tutorial</em></td>
<td align="center"><img src="img/demo/gui/fadguidetab2.png" width="300"><br><em><strong>FadGuide Tab 2</strong> - More information</em></td>
</tr>
<tr>
<td align="center"><img src="img/preview1.png" width="300"><br><em><strong>Password Dialog</strong> - Secure entry prompt</em></td>
<td align="center"><img src="img/preview2.png" width="300"><br><em><strong>Password Fullscreen</strong> - With wallpaper</em></td>
</tr>
<tr>
<td align="center"><img src="img/demo/gui/readme.png" width="300"><br><em><strong>README Info</strong> - Documentation display</em></td>
<td align="center"><img src="img/demo/gui/passrecovery.png" width="300"><br><em><strong>Password Recovery</strong> - Recovery codes</em></td>
</tr>
<tr>
<td align="center" colspan="2"><img src="img/legacy/snake.png" width="300"><br><em><strong>Snake Game</strong> - Entertainment feature on home tab</em></td>
</tr>
</table>

### 💻 CLI/TUI Mode - File & Folder Encryption

<table>
<tr>
<td align="center"><img src="img/demo/cli/fadcryptcli_mainmenu.png" width="300"><br><em><strong>Main Menu</strong> - Terminal UI with animations</em></td>
<td align="center"><img src="img/demo/cli/lockscreen.png" width="300"><br><em><strong>Lock Screen</strong> - Select files to encrypt</em></td>
</tr>
<tr>
<td align="center"><img src="img/demo/cli/passwordprompt.png" width="300"><br><em><strong>Password Prompt</strong> - Secure entry</em></td>
<td align="center"><img src="img/demo/cli/lock-confirmation.png" width="300"><br><em><strong>Lock Confirmation</strong> - Review & confirm</em></td>
</tr>
<tr>
<td align="center"><img src="img/demo/cli/locked-items-list.png" width="300"><br><em><strong>Locked Items List</strong> - View encrypted files</em></td>
<td align="center"><img src="img/demo/cli/unlockscreen.png" width="300"><br><em><strong>Unlock Screen</strong> - Decrypt files</em></td>
</tr>
</table>


<!--     <details>
        <summary><strong>More Screenshots</strong></summary>
        <img src="/img/3.png" style="width: 700px; height: auto;" >
        <br>
        <img src="/img/4.png" style="width: 700px; height: auto;" >
        <br>
        <img src="/img/5.png" style="width: 700px; height: auto;" >
    </details> -->
    
## `>_` How FadCrypt Works:

<details>
<summary><strong>📚 Technical Deep Dive (Click to expand)</strong></summary>

<br>

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

</details>

## `>_` Password Creation & Setup

When you first run FadCrypt:

1. **Password Creation:** Set a strong master password
2. **Recovery Codes:** Generate 10 emergency recovery codes and store them securely
3. **Configuration:** Choose preferences (UI theme, dialog style, etc.)
4. **Ready:** FadCrypt is now ready to lock files/folders

If you forget your password:
- Use one of the recovery codes to set a new password
- Each recovery code is single-use; other codes remain valid until used or until you regenerate a fresh set

## `>_` ⬇️ Installation & Setup

Download the latest version from the [releases page](https://github.com/anonfaded/FadCrypt/releases/):

[<img src="https://raw.githubusercontent.com/vadret/android/master/assets/get-github.png" alt="Get it on GitHub" height="70">](https://github.com/anonfaded/FadCrypt/releases)

### Windows

1. **Download:** Get [`FadCryptSetup_v2.0.0.exe`](https://github.com/anonfaded/FadCrypt/releases/download/v2.0.0/FadCryptSetup_v2.0.0.exe) from [Releases](https://github.com/anonfaded/FadCrypt/releases)
2. **Install:** Run the installer and follow the wizard
3. **Run:** 
   - Search "FadCrypt" in Start menu and launch, or
   - Run `fadcrypt` from terminal
4. **Context Menu:** Right-click files/folders to lock/unlock directly

### Linux

1. **Download & Install:** Get [`FadCrypt_v2.0.0_amd64.deb`](https://github.com/anonfaded/FadCrypt/releases/download/v2.0.0/FadCrypt_v2.0.0_amd64.deb) from [Releases](https://github.com/anonfaded/FadCrypt/releases), then:
   ```bash
   sudo apt install ./FadCrypt_v2.0.0_amd64.deb
   ```
   - The daemon service installs and enables automatically
   
2. **Run:** 
   - Search "FadCrypt" in app menu, or
   - Run `fadcrypt` from terminal

3. **First Setup:** Set master password and generate recovery codes

### macOS

1. **Install Dependencies:** Ensure Homebrew is installed, then install SDL2 for pygame:
   ```bash
   brew install sdl2
   ```

2. **Install Python Packages:**
   ```bash
   pip3 install --break-system-packages -r requirements.txt
   ```

3. **Build:** Follow the build instructions for macOS (coming soon)

4. **Run:** 
   - Run `python3 FadCrypt.py` from terminal

5. **First Setup:** Set master password and generate recovery codes

<details>
<summary><strong>ℹ️ Linux-Specific Details</strong></summary>

**Daemon Service:**
- **Name:** `fadcrypt-elevated.service`
- **Check status:** `systemctl status fadcrypt-elevated.service`
- **View logs:** `journalctl -u fadcrypt-elevated.service -f`
- **Start:** `sudo systemctl start fadcrypt-elevated.service`
- **Stop:** `sudo systemctl stop fadcrypt-elevated.service`

**File Operations:**
- Lock: Uses `chmod 000` + `chattr +i` (daemon-managed)
- Unlock: Restores original permissions
- Logs: `~/.config/FadCrypt/logs/`

**Socket Communication:**
- Client-daemon via Unix socket: `/run/fadcrypt/elevated.sock`
- Auto-retry on connection failure
- Timeout: 30 seconds per operation

</details>

## `>_` Features:

✅ **Application Locking** | ✅ **File Encryption** | ✅ **Recovery Codes** | ✅ **Real-time Protection** | ✅ **Auto-Startup** | ✅ **Cross-Platform**

<details>
<summary><strong>📋 Full Feature List (Click to expand)</strong></summary>

<br>

- **Application Locking:** Secure apps with encrypted password protection; password cannot be recovered if lost and tool cannot be stopped without it.
- **Real-time File Protection:** Detects and auto-recovers critical files/folders if deleted or modified.
- **Recovery Codes:** Generate and use recovery codes to reset forgotten password securely (non-bypassable, one-time use).
- **Auto-Startup Monitoring:** Automatically starts monitoring on system boot with seamless initialization.
- **Statistics & Activity Logging:** Detailed monitoring statistics with activity history and duration tracking.
- **Customizable UI:** Choose password dialog styles, UI themes, and system tray integration.
- **Cross-Platform:** Works on both Windows and Linux with platform-specific features.
- **Snake Game:** Classic arcade Snake game available on home tab for entertainment.
- **System Tray Integration:** Quick access from system tray with minimize/restore functionality.
- **Auto-Recovery:** Crashes are detected and monitored files are recovered automatically on next startup.

### Security Features

- **Encrypted Storage:** All passwords and configuration data encrypted using industry-standard cryptography
- **Single Instance Enforcement:** Only one FadCrypt instance can run at a time to prevent bypass attempts
- **Password-Secured Monitoring Control:** Requires master password to stop or alter protection settings
- **Optional System Tools Disabled:** Prevent access to Task Manager, Registry Editor, Command Prompt, etc. (configurable)
- **File Immutability & Elevation:** Windows Service or Linux daemon for seamless elevated operations

### Daemon Architecture (Linux)

- **Root Daemon:** `fadcrypt-elevated.service` runs as systemd service with full root privileges
- **Unix Socket Communication:** Secure IPC between GUI and daemon
- **Capabilities:** File protection (chattr), permissions (chmod), backup restoration, kernel monitoring (fanotify)
- **Installation:** Automatically configured with .deb package

</details>

⚠️ **Tamper-Proof Encryption:** When a file or folder is encrypted, it becomes tamper-proof and cannot be copied, moved, deleted, or modified until decrypted. The encrypted file is write-protected and read-restricted to ensure unauthorized access is prevented.

## `>_` Command-Line Interface (CLI)

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

<details>
<summary><strong>⚙️ CLI Technical Details (Click to expand)</strong></summary>

<br>

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

</details>

### Tamper-Proof Protection Control

By default, FadCrypt applies **full tamper-proof protection** to all encrypted files, preventing them from being copied, moved, edited, or deleted until they are decrypted.

**Control Tamper-Proof Behavior:**

You can enable or disable tamper-proof protections using simple toggle flags:

```bash
# TURN OFF (Disable tamper-proof) - files become moveable and copyable
fadcrypt --0 file.txt
# or
fadcrypt --off file.txt

# TURN ON (Enable tamper-proof) - restore full protection
fadcrypt --1 TestFolder
# or
fadcrypt --on TestFolder
```

**What the Flags Do:**

| Flag | Behavior | Files Can Be... |
|------|----------|-----------------|
| `--0` or `--off` | Disable protections | Moved, Copied, Deleted (but still encrypted) |
| `--1` or `--on` | Enable protections (DEFAULT) | **Cannot** be moved, copied, edited, or deleted |

**Important: Works on ANY File!**

The `--1`/`--on` and `--0`/`--off` flags work on **any file or folder**, not just encrypted ones:
- Use them to make system files, configs, or documents immutable without encryption
- Lighter option than full encryption if you just want protection without decryption overhead
- Perfect for protecting important files you don't want accidentally modified or deleted
- Can toggle protection on/off anytime, on any file type

**When to Use Each Mode:**

- **Tamper-Proof (ON)** - Default for maximum security. Use when you want to absolutely prevent unauthorized access or modifications.
- **Non-Protected (OFF)** - Use when you need flexibility to organize or back up files while keeping them protected.
- **Immutable Without Encryption** - Use `--1` on regular files when you want read-only protection without encryption overhead.

## `>_` Performance

FadCrypt uses AES-256-GCM encryption with efficient streaming I/O and optimized cryptographic operations. Files are encrypted with authentication to ensure data integrity.

| Operation | Size | Time |
|-----------|------|------|
| Encryption | 250 MB | ~8s |
| Encryption | 500 MB | ~15s |
| Decryption | Any | ~2-3s |

> Performance varies based on CPU speed and storage type (SSD/HDD).

## `>_` Featured On

- [VPN Club on Telegram](https://t.me/s/wbnet?q=fadcrypt)
- [popMods on Telegram](https://t.me/s/popmods?q=fadcrypt)
- [blog.csdn.net](https://blog.csdn.net/qq_29607687/article/details/141366524)
<!-- - [rhkb.cn](http://www.rhkb.cn/news/405585.html) -->

## `>_` Join Community

Join our [Discord server](https://discord.gg/kvAZvdkuuN) to share ideas, seek help, or connect with other users. Your feedback and contributions are welcome!

[![Discord](https://img.shields.io/discord/1263384048194027520?label=Join%20Us%20on%20Discord&logo=discord)](https://discord.gg/kvAZvdkuuN)

## `>_` Support

<a href='https://ko-fi.com/D1D510FNSV' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi3.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>

## `>_` Contributions

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

# `>_` Install Dependencies & Build

## `>_` Prerequisites

Install Python dependencies:
```python
pip install -r requirements.txt
```

<details>
<summary><strong>📦 Build Instructions (Windows & Linux)</strong></summary>

## `>_` Windows Build

See [`BUILD_WINDOWS.md`](BUILD_WINDOWS.md) for detailed instructions.

**Quick start:**
```powershell
.\build-windows.ps1
```

This will:
- Build GUI executable
- Build CLI executable  
- Create installer with Inno Setup

## `>_` Linux Build

See [`BUILD_LINUX.md`](BUILD_LINUX.md) for detailed instructions.

**Quick start:**
```bash
chmod +x build-deb.sh
./build-deb.sh
```

This will:
- Build GUI and CLI executables
- Create .deb package
- Install daemon service automatically

</details>

## `>_` License & Commercial Use

**FadCrypt is open-source under the GNU General Public License v3.0 (GPLv3).**

**Need a commercial license?** 
If you want to use FadCrypt without GPLv3 requirements, 
contact us for commercial licensing terms.

📧 Email: fadedhood@proton.me

<details>
<summary><strong>🧪 Development Testing</strong></summary>

## Context Menu Test Flags

For developers testing context menu functionality without full registry integration:

```bash
# Test lock operation (single file)
python FadCrypt.py --test-context-lock <path>

# Test lock operation (multiple files - batch)
python FadCrypt.py --test-context-lock <path1> <path2> <path3>

# Test unlock operation (single file)
python FadCrypt.py --test-context-unlock <path>

# Test unlock operation (multiple files - batch)
python FadCrypt.py --test-context-unlock <path1> <path2> <path3>
```

**Security Note:** These test flags provide the **same security** as the real context menu:
- Require valid master password already set up
- Require correct password entry in authentication dialog
- Perform full encryption/decryption process with all security checks
- Support batch operations (multiple files with single password entry)

**Use Cases:**
- Debugging context menu integration issues
- Testing batch lock/unlock without installing registry entries
- Verifying password dialog behavior during development
- Testing file encryption/decryption logic before deployment

**Example:**
```bash
# Test locking 3 files at once
python FadCrypt.py --test-context-lock "file1.txt" "file2.txt" "file3.txt"

# A password dialog will appear - enter your master password
# All files will be processed and encrypted with progress updates
```

</details>

<details>
<summary><strong>🔑 Reset Password</strong></summary>

Follow these steps to regain access to FadCrypt:

## 1. Terminate the app processes (if running)

**Windows:**
1. Open PowerShell as Administrator: `Windows key + S` → type "PowerShell" → right-click → "Run as administrator"
2. Run:
   ```powershell
   Stop-Process -Name "fadcrypt" -Force
   ```

**Linux:**
```bash
killall fadcrypt fadcrypt-cli
```

## 2. Delete the password binary file

**Windows:**
Delete these files:
```
C:\Users\<YourUsername>\AppData\Roaming\FadCrypt\encrypted_password.bin
C:\ProgramData\FadCrypt\Backup\encrypted_password.bin
```

**Linux:**
```bash
rm ~/.config/FadCrypt/encrypted_password.bin
rm ~/.local/share/FadCrypt/Backup/encrypted_password.bin
```

Now reopen FadCrypt and set a new password!

</details>
