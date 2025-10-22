<div align="center">
    
<img src="https://github.com/user-attachments/assets/c9fc6bd3-daae-402d-8eeb-828473ede8d4" style="width: 700px; height: auto;" >

<!-- https://github.com/user-attachments/assets/c9eeaf74-6649-4810-b420-e2c4ad4bd365 -->

<br>

| :exclamation: | This project is part of the [FadSec Lab suite](https://github.com/fadsec-lab). <br> Discover our focus on ad-free, privacy-first applications and stay updated on future releases! |
| ------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

---

<img src="https://github.com/user-attachments/assets/c730eda3-5887-458d-8df1-971a74807b73" style="width: 100px; height: auto;" >

# FadCrypt

**Advanced and elegant cross-platform app encryption – powerful, customizable, open-source, and completely free!**

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

1. **Password Creation:** When you set a password, it's encrypted and saved with the configuration file of locked apps. During monitoring, these files are backed up to a separate location:

   - **Windows:** `C:\ProgramData\FadCrypt\Backup\`
   - **Linux:** `~/.local/share/FadCrypt/Backup/`

   If detected as deleted, they are automatically recovered and restored.

2. **Elevated Daemon Service (Linux):** FadCrypt uses a systemd service that runs with root privileges to handle file protection operations seamlessly:

   - **Daemon Operations:** The daemon (`fadcrypt-elevated.service`) provides root-level file operations via Unix socket communication
   - **Capabilities:** File immutability (chattr +i/-i), permission changes, backup restoration, and kernel-level file monitoring (fanotify)
   - **Automatic Setup:** The daemon is installed and started automatically when you install the .deb package

3. **Monitoring Mode:** Press "Start Monitoring" to set FadCrypt as a startup app. It will automatically activate every time your PC starts, and will persistently run unless you press "Stop Monitoring."

4. **Security Features:** When monitoring is active, FadCrypt can't be stopped without the correct password. Optionally, users can enable system tool disabling to prevent tampering (Control Panel, Registry Editor, Task Manager, msconfig on Windows; terminal emulators and system monitors on Linux). Recovery codes provide a secure backup method to reset forgotten passwords.

5. **Mutex Protection:** FadCrypt uses mutual exclusion to ensure only one instance runs at a time, blocking new instances until the current one is closed with the password. This prevents bypass attempts.

**Note:** The password recovery feature is not available yet.

## ⬇️ Download

Download the latest `windows setup installer` file directly from the [releases page](https://github.com/anonfaded/FadCrypt/releases).

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

First, install the Tkinter library (required for GUI):

```bash
sudo apt-get install python3-tk
```

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
