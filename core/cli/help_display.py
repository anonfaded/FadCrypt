"""
Help Display for FadCrypt CLI

Beautiful, categorized, platform-aware help system with modern rounded design.
"""

import sys
import os
import platform
from .colors import Colors


def show_help():
    """Display comprehensive help information with modern rounded design"""
    from FadCrypt import __version__
    
    system = platform.system()
    
    # Color codes
    RED = Colors.BORDER
    BRIGHT_RED = Colors.TITLE
    DIM = Colors.DIM
    CYAN = Colors.SECONDARY  # Changed from INFO (blue) to SECONDARY (light red)
    YELLOW = Colors.WARNING
    GREEN = Colors.SUCCESS
    RESET = Colors.RESET
    
    # Header
    print(f"\n{RED}╭─ 🏴 FadCrypt v{__version__}{RESET}")
    print(f"{RED}│{RESET} {BRIGHT_RED}Open-Source File, Folder & Application Protection Suite{RESET}")
    print(f"{RED}├──────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{RED}│{RESET} Cross-platform tool for locking files, folders, and applications")
    print(f"{RED}│{RESET} with password-based encryption and real-time monitoring.")
    print(f"{RED}├──────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{RED}│{RESET} {CYAN}Discord:{RESET} https://discord.gg/kvAZvdkuuN")
    print(f"{RED}│{RESET} {CYAN}GitHub:{RESET} https://github.com/anonfaded/FadCrypt")
    print(f"{RED}│{RESET} {CYAN}Support & Buy Me a Ko-fi:{RESET} https://ko-fi.com/fadedx")
    print(f"{RED}╰──────────────────────────────────────────────────────────────────────{RESET}\n")
    
    # Usage
    print(f"{RED}╭─ 📖 {BRIGHT_RED}USAGE{RESET}")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}fadcrypt{RESET} [OPTIONS] [ARGUMENTS]")
    print(f"{RED}│{RESET}")
    print(f"{RED}│{RESET}   {CYAN}OPTIONS:{RESET}   Flags that control FadCrypt's behavior")
    print(f"{RED}│{RESET}   {CYAN}ARGUMENTS:{RESET} Paths to files or folders you want to lock/unlock")
    print(f"{RED}│{RESET}")
    print(f"{RED}│{RESET}   {CYAN}Examples:{RESET}")
    print(f"{RED}│{RESET}     fadcrypt                      {DIM}# Interactive menu{RESET}")
    print(f"{RED}│{RESET}     fadcrypt {GREEN}--gui{RESET}                {DIM}# Launch GUI{RESET}")
    print(f"{RED}│{RESET}     fadcrypt {GREEN}--lock{RESET} file.pdf      {DIM}# Lock a file{RESET}")
    print(f"{RED}│{RESET}     fadcrypt {GREEN}--unlock{RESET} folder/     {DIM}# Unlock a folder{RESET}")
    print(f"{RED}╰──────────────────────────────────────────────────────────────────────{RESET}\n")
    
    # Main Commands
    print(f"{RED}╭─ 🎯 {BRIGHT_RED}MAIN COMMANDS{RESET}")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}(no options){RESET}     : Launch interactive menu with file selector")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--cli{RESET}            : Same as no options - interactive menu")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--gui{RESET}            : Launch graphical interface (PyQt6)")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--help, -h{RESET}       : Show this help message")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--version, -v{RESET}    : Show version information")
    print(f"{RED}╰──────────────────────────────────────────────────────────────────────{RESET}\n")
    
    # File Operations
    print(f"{RED}╭─ 📁 {BRIGHT_RED}FILE OPERATIONS{RESET}")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--lock <path>{RESET}    : Lock files or folders")
    print(f"{RED}│{RESET}                      {DIM}Example: fadcrypt --lock document.pdf photos/{RESET}")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--unlock <path>{RESET}  : Unlock files or folders")
    print(f"{RED}│{RESET}                      {DIM}Example: fadcrypt --unlock document.pdf{RESET}")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--list{RESET}           : Show all currently locked items")
    print(f"{RED}│{RESET}                      {DIM}Example: fadcrypt --list{RESET}")
    print(f"{RED}╰──────────────────────────────────────────────────────────────────────{RESET}\n")
    
    # Tamper-Proof Protection
    print(f"{RED}╭─ 🔐 {BRIGHT_RED}TAMPER-PROOF PROTECTION{RESET}")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--0 or --off{RESET}     : Disable tamper-proof protections (switch OFF)")
    print(f"{RED}│{RESET}                      {DIM}Files become moveable, copyable, and deletable{RESET}")
    print(f"{RED}│{RESET}                      {DIM}Example: fadcrypt --0 file.txt{RESET}")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--1 or --on{RESET}      : Enable tamper-proof protections (switch ON)")
    print(f"{RED}│{RESET}                      {DIM}Files cannot be moved, copied, edited, or deleted{RESET}")
    print(f"{RED}│{RESET}                      {DIM}Works on ANY file, encrypted or not!{RESET}")
    print(f"{RED}│{RESET}                      {DIM}Lighter option than encryption - no decryption needed{RESET}")
    print(f"{RED}│{RESET}                      {DIM}Example: fadcrypt --1 TestFolder{RESET}")
    print(f"{RED}│{RESET}")
    print(f"{RED}│{RESET} {YELLOW}Note:{RESET} Use --1/--on to make files immutable without encryption.")
    print(f"{RED}│{RESET}       Perfect for system files or configs you don't want modified.")
    print(f"{RED}│{RESET} {YELLOW}Default:{RESET} All locked files get full tamper-proof protection (ON)")
    print(f"{RED}╰──────────────────────────────────────────────────────────────────────{RESET}\n")
    
    # Windows-specific context menu section
    if system == "Windows":
        print(f"{RED}╭─ 🖱️  {BRIGHT_RED}CONTEXT MENU (Windows){RESET}")
        print(f"{RED}│{RESET} Right-click on any file or folder in File Explorer to see:")
        print(f"{RED}│{RESET}   • Lock with FadCrypt")
        print(f"{RED}│{RESET}   • Unlock with FadCrypt")
        print(f"{RED}│{RESET}")
        print(f"{RED}│{RESET} These options use the following flags internally:")
        print(f"{RED}│{RESET}   --context-lock <path>    {DIM}(called by context menu){RESET}")
        print(f"{RED}│{RESET}   --context-unlock <path>  {DIM}(called by context menu){RESET}")
        print(f"{RED}│{RESET}")
        print(f"{RED}│{RESET} {DIM}DEV MODE (Testing without registry):{RESET}")
        print(f"{RED}│{RESET}   --test-context-lock <path>   {DIM}(test lock without registry){RESET}")
        print(f"{RED}│{RESET}   --test-context-unlock <path> {DIM}(test unlock without registry){RESET}")
        print(f"{RED}╰──────────────────────────────────────────────────────────────────────{RESET}\n")
    
    # Installation & Setup
    print(f"{RED}╭─ ⚙️  {BRIGHT_RED}INSTALLATION & SETUP (Advanced){RESET}")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--register-context{RESET}   : Add FadCrypt to Windows right-click menu")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--unregister-context{RESET} : Remove from Windows right-click menu")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--install-service{RESET}    : Install FadCrypt elevated service")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--uninstall-service{RESET}  : Uninstall FadCrypt elevated service")
    print(f"{RED}╰──────────────────────────────────────────────────────────────────────{RESET}\n")
    
    # Dangerous Operations
    print(f"{RED}╭─ ⚠️  {YELLOW}DANGEROUS OPERATIONS (Use with Caution!){RESET}")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--cleanup{RESET}        : {YELLOW}Complete system cleanup and uninstall{RESET}")
    
    if system == "Windows":
        print(f"{RED}│{RESET}   {DIM}This will:{RESET}")
        print(f"{RED}│{RESET}     {DIM}• Restore Task Manager, Registry Editor, Control Panel{RESET}")
        print(f"{RED}│{RESET}     {DIM}• Remove FadCrypt from Windows startup{RESET}")
        print(f"{RED}│{RESET}     {DIM}• Remove context menu entries{RESET}")
        print(f"{RED}│{RESET}     {DIM}• Delete config folder: %APPDATA%\\FadCrypt\\config{RESET}")
        print(f"{RED}│{RESET}     {DIM}• Delete backup folder: %APPDATA%\\FadCrypt\\backup{RESET}")
        print(f"{RED}│{RESET}     {DIM}• Restart File Explorer{RESET}")
    else:
        print(f"{RED}│{RESET}   {DIM}This will:{RESET}")
        print(f"{RED}│{RESET}     {DIM}• Remove immutable flags from protected files{RESET}")
        print(f"{RED}│{RESET}     {DIM}• Restore disabled system tools (terminal, system monitor, etc.){RESET}")
        print(f"{RED}│{RESET}     {DIM}• Delete config folder: ~/.config/FadCrypt{RESET}")
        print(f"{RED}│{RESET}     {DIM}• Delete backup folder: ~/.local/share/FadCrypt/Backup{RESET}")
        print(f"{RED}│{RESET}     {DIM}• Remove lock files{RESET}")
    
    print(f"{RED}╰──────────────────────────────────────────────────────────────────────{RESET}\n")
    
    # File Locations
    print(f"{RED}╭─ 📍 {BRIGHT_RED}FILE LOCATIONS{RESET}")
    
    if system == "Windows":
        appdata = os.environ.get('APPDATA', 'C:\\Users\\YourUser\\AppData\\Roaming')
        print(f"{RED}│{RESET} {CYAN}Config Folder:{RESET} {appdata}\\FadCrypt\\config")
        print(f"{RED}│{RESET}   {DIM}• encrypted_password.bin - Your master password{RESET}")
        print(f"{RED}│{RESET}   {DIM}• recovery_codes.json - Recovery codes for password reset{RESET}")
        print(f"{RED}│{RESET}   {DIM}• apps_config.json - Application lock settings{RESET}")
        print(f"{RED}│{RESET}   {DIM}• settings.json - FadCrypt settings{RESET}")
        print(f"{RED}│{RESET}   {DIM}• monitoring_state.json - Monitoring status{RESET}")
        print(f"{RED}│{RESET}")
        print(f"{RED}│{RESET} {CYAN}Backup Folder:{RESET} {appdata}\\FadCrypt\\backup")
        print(f"{RED}│{RESET}   {DIM}• Stores original files before encryption{RESET}")
    else:
        home = os.path.expanduser('~')
        print(f"{RED}│{RESET} {CYAN}Config Folder:{RESET} {home}/.config/FadCrypt")
        print(f"{RED}│{RESET}   {DIM}• encrypted_password.bin - Your master password{RESET}")
        print(f"{RED}│{RESET}   {DIM}• recovery_codes.json - Recovery codes for password reset{RESET}")
        print(f"{RED}│{RESET}   {DIM}• apps_config.json - Application lock settings{RESET}")
        print(f"{RED}│{RESET}   {DIM}• settings.json - FadCrypt settings{RESET}")
        print(f"{RED}│{RESET}   {DIM}• monitoring_state.json - Monitoring status{RESET}")
        print(f"{RED}│{RESET}")
        print(f"{RED}│{RESET} {CYAN}Backup Folder:{RESET} {home}/.local/share/FadCrypt/Backup")
        print(f"{RED}│{RESET}   {DIM}• Stores original files before encryption{RESET}")
    
    print(f"{RED}╰──────────────────────────────────────────────────────────────────────{RESET}\n")
    
    # Tips & Best Practices
    print(f"{RED}╭─ 💡 {BRIGHT_RED}TIPS & BEST PRACTICES{RESET}")
    print(f"{RED}│{RESET} • Remember your master password or use recovery codes to reset it")
    print(f"{RED}│{RESET} • Keep your recovery codes in a safe place")
    print(f"{RED}│{RESET} • Use {DIM}--list{RESET} to see what's currently locked")
    print(f"{RED}│{RESET} • Locked files are encrypted and protected")
    print(f"{RED}│{RESET} • The GUI {DIM}(--gui){RESET} provides a visual way to manage locks")
    print(f"{RED}╰──────────────────────────────────────────────────────────────────────{RESET}\n")
    
    # ASCII Art Footer
    print(f"""
          {RED} 
 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▒▒▒▒▒▒ ▒▒▒▒▒▒▒ ▒▒▒▒▒▒▒
 ▓▓▓▓▓▓▓ ▓▓   ▓▓▓▓    ▓▓▒▒▒▒▒▒       ▒▒ ▒▒      ▓    ▓
 ▓▓      ▓▓▓▓▓▓▓▓▓    ▓▓      ▒▒     ▒▒ ▒▒      ▓ ▓▓ ▓▓
 ▓▓      ▓▓   ▓▓▓▓▓▓▓▓▓ ▒▒▒▒▒▒▒ ▒▒▒▒▒▒▒ ▒▒▒▒▒▒▒
          {RESET}
          """)
    
    print(f"{YELLOW}Found an issue or have a feature request?{RESET}")
    print(f"{YELLOW}Please open an issue on GitHub:{RESET}")
    print(f"{CYAN}https://github.com/anonfaded/FadCrypt/issues{RESET}\n")


def show_version():
    """Display version information with modern rounded design"""
    from FadCrypt import __version__, __version_code__
    from .colors import Colors
    
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    system = platform.system()
    
    RED = Colors.BORDER
    BRIGHT_RED = Colors.TITLE
    RESET = Colors.RESET
    
    print(f"\n{RED}╭─ 🔒 FadCrypt Version{RESET}")
    print(f"{RED}│{RESET} Version: {BRIGHT_RED}v{__version__}{RESET}")
    print(f"{RED}│{RESET} Version Code: {__version_code__}")
    print(f"{RED}│{RESET} Platform: {system}")
    print(f"{RED}│{RESET} Python: {python_version}")
    print(f"{RED}╰───────────────────{RESET}\n")
