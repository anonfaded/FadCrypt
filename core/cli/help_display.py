"""
Help Display for FadCrypt CLI

Beautiful, categorized, platform-aware help system with modern rounded design.
"""

import sys
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
    CYAN = Colors.INFO
    YELLOW = Colors.WARNING
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
    print(f"{RED}│{RESET}     fadcrypt --gui                {DIM}# Launch GUI{RESET}")
    print(f"{RED}│{RESET}     fadcrypt --lock file.pdf      {DIM}# Lock a file{RESET}")
    print(f"{RED}│{RESET}     fadcrypt --unlock folder/     {DIM}# Unlock a folder{RESET}")
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
        print(f"{RED}╰──────────────────────────────────────────────────────────────────────{RESET}\n")
    
    # Installation & Setup
    print(f"{RED}╭─ ⚙️  {BRIGHT_RED}INSTALLATION & SETUP (Advanced){RESET}")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--register-context{RESET}   : Add FadCrypt to Windows right-click menu")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--unregister-context{RESET} : Remove from Windows right-click menu")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--install-service{RESET}    : Install FadCrypt elevated service")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--uninstall-service{RESET}  : Uninstall FadCrypt elevated service")
    print(f"{RED}╰──────────────────────────────────────────────────────────────────────{RESET}\n")
    
    # Maintenance
    print(f"{RED}╭─ 🔧 {BRIGHT_RED}MAINTENANCE{RESET}")
    print(f"{RED}│{RESET} {DIM}•{RESET} {BRIGHT_RED}--cleanup{RESET}        : Clean up temporary files and orphaned locks")
    print(f"{RED}╰──────────────────────────────────────────────────────────────────────{RESET}\n")
    
    # Tips & Best Practices
    print(f"{RED}╭─ 💡 {BRIGHT_RED}TIPS & BEST PRACTICES{RESET}")
    print(f"{RED}│{RESET} • Always remember your master password - it cannot be recovered!")
    print(f"{RED}│{RESET} • Keep your recovery codes in a safe place")
    print(f"{RED}│{RESET} • Use --list to see what's currently locked")
    print(f"{RED}│{RESET} • Locked files are encrypted and hidden from normal view")
    print(f"{RED}│{RESET} • The GUI {DIM}(--gui){RESET} provides a visual way to manage locks")
    print(f"{RED}╰──────────────────────────────────────────────────────────────────────{RESET}\n")
    
    # ASCII Art Footer
    print(f"{RED}  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▒▒▒▒▒▒ ▒▒▒▒▒▒▒ ▒▒▒▒▒▒▒{RESET}")
    print(f"{RED}  ▓▓▓▓▓▓▓ ▓▓   ▓▓▓▓    ▓▓▒▒▒▒▒▒       ▒▒ ▒▒{RESET}")
    print(f"{RED}  ▓    ▓▓▓      ▓▓▓▓▓▓▓▓▓    ▓▓      ▒▒     ▒▒ ▒▒{RESET}")
    print(f"{RED}  ▓ ▓▓ ▓▓▓▓      ▓▓   ▓▓▓▓▓▓▓▓▓ ▒▒▒▒▒▒▒ ▒▒▒▒▒▒▒ ▒▒▒▒▒▒▒{RESET}\n")
    
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
