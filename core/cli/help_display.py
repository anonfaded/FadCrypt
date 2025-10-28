"""
Help Display for FadCrypt CLI

Beautiful, categorized help system with colorama.
"""

from .colors import Colors, BoxChars, print_colored


def show_help():
    """Display comprehensive help information"""
    
    # Header
    print_colored(f"\n{BoxChars.TOP_LEFT}{BoxChars.HORIZONTAL * 75}{BoxChars.TOP_RIGHT}", Colors.BORDER)
    print_colored(f"{BoxChars.VERTICAL}{Colors.ICON_LOCK} FadCrypt v2.0 - File & Folder Protection Suite{' ' * 26}{BoxChars.VERTICAL}", Colors.TITLE)
    print_colored(f"{BoxChars.BOTTOM_LEFT}{BoxChars.HORIZONTAL * 75}{BoxChars.BOTTOM_RIGHT}\n", Colors.BORDER)
    
    print_colored("Cross-platform application for locking and protecting files/folders with", Colors.TEXT)
    print_colored("password-based encryption and real-time monitoring.\n", Colors.TEXT)
    
    # Usage
    print_colored(f"{BoxChars.S_TOP_LEFT}{BoxChars.S_HORIZONTAL * 75}{BoxChars.S_TOP_RIGHT}", Colors.BORDER)
    print_colored(f"{BoxChars.S_VERTICAL} USAGE{' ' * 69}{BoxChars.S_VERTICAL}", Colors.TITLE)
    print_colored(f"{BoxChars.S_BOTTOM_LEFT}{BoxChars.S_HORIZONTAL * 75}{BoxChars.S_BOTTOM_RIGHT}\n", Colors.BORDER)
    
    print_colored("  fadcrypt [OPTIONS] [ARGUMENTS]", Colors.HIGHLIGHT)
    print_colored("  fadcrypt                    # Launch interactive TUI menu", Colors.DIM)
    print_colored("  fadcrypt --gui              # Launch graphical interface", Colors.DIM)
    print_colored("  fadcrypt --lock <path>      # Lock file/folder directly\n", Colors.DIM)
    
    # Main Commands
    print_colored(f"{BoxChars.S_TOP_LEFT}{BoxChars.S_HORIZONTAL * 75}{BoxChars.S_TOP_RIGHT}", Colors.BORDER)
    print_colored(f"{BoxChars.S_VERTICAL} MAIN COMMANDS{' ' * 62}{BoxChars.S_VERTICAL}", Colors.TITLE)
    print_colored(f"{BoxChars.S_BOTTOM_LEFT}{BoxChars.S_HORIZONTAL * 75}{BoxChars.S_BOTTOM_RIGHT}\n", Colors.BORDER)
    
    print_colored("  (no arguments)", Colors.PRIMARY)
    print_colored("      Launch interactive TUI menu with file selector and options", Colors.TEXT)
    print_colored("      Best for: Interactive file management\n", Colors.DIM)
    
    print_colored("  --cli", Colors.PRIMARY)
    print_colored("      Explicitly launch CLI/TUI mode (same as no arguments)", Colors.TEXT)
    print_colored("      Best for: Development and testing\n", Colors.DIM)
    
    print_colored("  --gui", Colors.PRIMARY)
    print_colored("      Launch PyQt6 graphical user interface", Colors.TEXT)
    print_colored("      Best for: Desktop users who prefer GUI\n", Colors.DIM)
    
    print_colored("  --help, -h", Colors.PRIMARY)
    print_colored("      Display this help message and exit\n", Colors.TEXT)
    
    # File Operations
    print_colored(f"{BoxChars.S_TOP_LEFT}{BoxChars.S_HORIZONTAL * 75}{BoxChars.S_TOP_RIGHT}", Colors.BORDER)
    print_colored(f"{BoxChars.S_VERTICAL} FILE OPERATIONS{' ' * 60}{BoxChars.S_VERTICAL}", Colors.TITLE)
    print_colored(f"{BoxChars.S_BOTTOM_LEFT}{BoxChars.S_HORIZONTAL * 75}{BoxChars.S_BOTTOM_RIGHT}\n", Colors.BORDER)
    
    print_colored("  --lock <path> [path2] [...]", Colors.PRIMARY)
    print_colored("      Lock one or more files/folders with password protection", Colors.TEXT)
    print_colored("      Example: fadcrypt --lock document.pdf folder/", Colors.DIM)
    print_colored("      Note: Requires password verification\n", Colors.DIM)
    
    print_colored("  --unlock <path> [path2] [...]", Colors.PRIMARY)
    print_colored("      Unlock one or more previously locked files/folders", Colors.TEXT)
    print_colored("      Example: fadcrypt --unlock document.pdf folder/", Colors.DIM)
    print_colored("      Note: Requires password verification\n", Colors.DIM)
    
    print_colored("  --list-locked", Colors.PRIMARY)
    print_colored("      Display a formatted list of all currently locked items", Colors.TEXT)
    print_colored("      Shows: Type, name, and path of each locked item\n", Colors.DIM)
    
    # Context Menu (Internal)
    print_colored(f"{BoxChars.S_TOP_LEFT}{BoxChars.S_HORIZONTAL * 75}{BoxChars.S_TOP_RIGHT}", Colors.BORDER)
    print_colored(f"{BoxChars.S_VERTICAL} CONTEXT MENU (Internal Use){' ' * 50}{BoxChars.S_VERTICAL}", Colors.TITLE)
    print_colored(f"{BoxChars.S_BOTTOM_LEFT}{BoxChars.S_HORIZONTAL * 75}{BoxChars.S_BOTTOM_RIGHT}\n", Colors.BORDER)
    
    print_colored("  --context-lock <path>", Colors.PRIMARY)
    print_colored("      Lock file via Windows context menu (right-click)", Colors.TEXT)
    print_colored("      Note: Called automatically by shell extension\n", Colors.DIM)
    
    print_colored("  --context-unlock <path>", Colors.PRIMARY)
    print_colored("      Unlock file via Windows context menu (right-click)", Colors.TEXT)
    print_colored("      Note: Called automatically by shell extension\n", Colors.DIM)
    
    # Installation & Setup
    print_colored(f"{BoxChars.S_TOP_LEFT}{BoxChars.S_HORIZONTAL * 75}{BoxChars.S_TOP_RIGHT}", Colors.BORDER)
    print_colored(f"{BoxChars.S_VERTICAL} INSTALLATION & SETUP (Advanced){' ' * 46}{BoxChars.S_VERTICAL}", Colors.TITLE)
    print_colored(f"{BoxChars.S_BOTTOM_LEFT}{BoxChars.S_HORIZONTAL * 75}{BoxChars.S_BOTTOM_RIGHT}\n", Colors.BORDER)
    
    print_colored("  --register-context", Colors.PRIMARY)
    print_colored("      Register FadCrypt in Windows context menu (right-click menu)", Colors.TEXT)
    print_colored("      Purpose: Adds 'Lock/Unlock with FadCrypt' to file explorer", Colors.DIM)
    print_colored("      Note: Called automatically by installer\n", Colors.DIM)
    
    print_colored("  --unregister-context", Colors.PRIMARY)
    print_colored("      Remove FadCrypt from Windows context menu", Colors.TEXT)
    print_colored("      Purpose: Clean up registry entries during uninstallation", Colors.DIM)
    print_colored("      Note: Called automatically by uninstaller\n", Colors.DIM)
    
    print_colored("  --install-service", Colors.PRIMARY)
    print_colored("      Install FadCrypt elevated service (Windows only)", Colors.TEXT)
    print_colored("      Purpose: Enables persistent admin rights for file operations", Colors.DIM)
    print_colored("      Note: Requires administrator privileges\n", Colors.DIM)
    
    print_colored("  --uninstall-service", Colors.PRIMARY)
    print_colored("      Uninstall FadCrypt elevated service (Windows only)", Colors.TEXT)
    print_colored("      Purpose: Remove service during uninstallation", Colors.DIM)
    print_colored("      Note: Requires administrator privileges\n", Colors.DIM)
    
    print_colored("  --run-service", Colors.PRIMARY)
    print_colored("      Run as Windows service (internal use only)", Colors.TEXT)
    print_colored("      Purpose: Service control manager entry point\n", Colors.DIM)
    
    # Maintenance & Cleanup
    print_colored(f"{BoxChars.S_TOP_LEFT}{BoxChars.S_HORIZONTAL * 75}{BoxChars.S_TOP_RIGHT}", Colors.BORDER)
    print_colored(f"{BoxChars.S_VERTICAL} MAINTENANCE & CLEANUP (Advanced){' ' * 47}{BoxChars.S_VERTICAL}", Colors.TITLE)
    print_colored(f"{BoxChars.S_BOTTOM_LEFT}{BoxChars.S_HORIZONTAL * 75}{BoxChars.S_BOTTOM_RIGHT}\n", Colors.BORDER)
    
    print_colored("  --cleanup", Colors.PRIMARY)
    print_colored("      Perform complete system cleanup and restore", Colors.TEXT)
    print_colored("      Actions:", Colors.DIM)
    print_colored("        • Restore disabled system tools (Task Manager, Registry, etc.)", Colors.DIM)
    print_colored("        • Remove FadCrypt from PATH environment variable", Colors.DIM)
    print_colored("        • Unregister context menu entries", Colors.DIM)
    print_colored("        • Remove configuration and data directories", Colors.DIM)
    print_colored("        • Restart File Explorer to apply changes", Colors.DIM)
    print_colored("      Note: Called automatically by uninstaller\n", Colors.DIM)
    
    print_colored("  --auto-monitor", Colors.PRIMARY)
    print_colored("      Start monitoring automatically on system boot (silent mode)", Colors.TEXT)
    print_colored("      Purpose: Auto-start functionality for system startup", Colors.DIM)
    print_colored("      Note: Used by autostart configuration\n", Colors.DIM)
    
    # Development & Testing
    print_colored(f"{BoxChars.S_TOP_LEFT}{BoxChars.S_HORIZONTAL * 75}{BoxChars.S_TOP_RIGHT}", Colors.BORDER)
    print_colored(f"{BoxChars.S_VERTICAL} DEVELOPMENT & TESTING{' ' * 53}{BoxChars.S_VERTICAL}", Colors.TITLE)
    print_colored(f"{BoxChars.S_BOTTOM_LEFT}{BoxChars.S_HORIZONTAL * 75}{BoxChars.S_BOTTOM_RIGHT}\n", Colors.BORDER)
    
    print_colored("  --windows", Colors.PRIMARY)
    print_colored("      Mock Windows environment on Linux (for testing)", Colors.TEXT)
    print_colored("      Purpose: Cross-platform development and testing\n", Colors.DIM)
    
    # Examples
    print_colored(f"{BoxChars.S_TOP_LEFT}{BoxChars.S_HORIZONTAL * 75}{BoxChars.S_TOP_RIGHT}", Colors.BORDER)
    print_colored(f"{BoxChars.S_VERTICAL} EXAMPLES{' ' * 67}{BoxChars.S_VERTICAL}", Colors.TITLE)
    print_colored(f"{BoxChars.S_BOTTOM_LEFT}{BoxChars.S_HORIZONTAL * 75}{BoxChars.S_BOTTOM_RIGHT}\n", Colors.BORDER)
    
    print_colored("  # Interactive mode with menu", Colors.SUCCESS)
    print_colored("  fadcrypt\n", Colors.TEXT)
    
    print_colored("  # Lock a single file", Colors.SUCCESS)
    print_colored("  fadcrypt --lock document.pdf\n", Colors.TEXT)
    
    print_colored("  # Lock multiple items", Colors.SUCCESS)
    print_colored("  fadcrypt --lock file1.txt file2.pdf folder/\n", Colors.TEXT)
    
    print_colored("  # Unlock files", Colors.SUCCESS)
    print_colored("  fadcrypt --unlock document.pdf folder/\n", Colors.TEXT)
    
    print_colored("  # List all locked items", Colors.SUCCESS)
    print_colored("  fadcrypt --list-locked\n", Colors.TEXT)
    
    print_colored("  # Launch GUI", Colors.SUCCESS)
    print_colored("  fadcrypt --gui\n", Colors.TEXT)
    
    # Footer
    print_colored(f"{BoxChars.S_TOP_LEFT}{BoxChars.S_HORIZONTAL * 75}{BoxChars.S_TOP_RIGHT}", Colors.BORDER)
    print_colored(f"{BoxChars.S_VERTICAL} NOTES{' ' * 69}{BoxChars.S_VERTICAL}", Colors.TITLE)
    print_colored(f"{BoxChars.S_BOTTOM_LEFT}{BoxChars.S_HORIZONTAL * 75}{BoxChars.S_BOTTOM_RIGHT}\n", Colors.BORDER)
    
    print_colored("  • All file operations require password verification", Colors.INFO)
    print_colored("  • Locked files are protected until monitoring is stopped", Colors.INFO)
    print_colored("  • Context menu integration requires Windows", Colors.INFO)
    print_colored("  • Service features are Windows-specific", Colors.INFO)
    print_colored("  • Configuration stored in %APPDATA%\\FadCrypt\\config\\ (Windows)", Colors.INFO)
    print_colored("  • Configuration stored in ~/.config/FadCrypt/ (Linux)\n", Colors.INFO)
    
    print_colored(f"{BoxChars.TOP_LEFT}{BoxChars.HORIZONTAL * 75}{BoxChars.TOP_RIGHT}", Colors.BORDER)
    print_colored(f"{BoxChars.VERTICAL} © 2024-2025 FadSec Lab • Open Source • Cross-Platform{' ' * 22}{BoxChars.VERTICAL}", Colors.DIM)
    print_colored(f"{BoxChars.BOTTOM_LEFT}{BoxChars.HORIZONTAL * 75}{BoxChars.BOTTOM_RIGHT}\n", Colors.BORDER)
