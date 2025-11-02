"""
Color Theme for FadCrypt TUI

Red-themed color scheme using colorama for cross-platform support.
"""

from colorama import Fore, Back, Style, just_fix_windows_console

# Initialize colorama for Windows support - use just_fix_windows_console for proper emoji support
just_fix_windows_console()


class Colors:
    """FadCrypt red-themed color palette"""
    
    # Primary colors
    PRIMARY = Fore.RED
    SECONDARY = Fore.LIGHTRED_EX
    
    # Status colors
    SUCCESS = Fore.GREEN
    ERROR = Fore.RED + Style.BRIGHT
    WARNING = Fore.YELLOW
    INFO = Fore.CYAN
    
    # UI elements
    BORDER = Fore.RED
    TITLE = Fore.RED + Style.BRIGHT
    TEXT = Fore.WHITE
    DIM = Fore.LIGHTBLACK_EX
    
    # Interactive elements
    SELECTED = Back.RED + Fore.WHITE + Style.BRIGHT
    UNSELECTED = Fore.WHITE
    HIGHLIGHT = Fore.LIGHTRED_EX + Style.BRIGHT
    
    # Checkboxes
    CHECKBOX_CHECKED = Fore.GREEN + '✓'
    CHECKBOX_UNCHECKED = Fore.LIGHTBLACK_EX + '□'  # Empty square box
    
    # Icons
    ICON_LOCK = '🔒'
    ICON_UNLOCK = '🔓'
    ICON_FILE = '📄'
    ICON_FOLDER = '📁'
    ICON_SUCCESS = '✅'
    ICON_ERROR = '❌'
    ICON_WARNING = '⚠️'
    ICON_INFO = 'ℹ️'
    
    # Reset
    RESET = Style.RESET_ALL


class BoxChars:
    """Box drawing characters for TUI"""
    
    # Double line box
    TOP_LEFT = '╔'
    TOP_RIGHT = '╗'
    BOTTOM_LEFT = '╚'
    BOTTOM_RIGHT = '╝'
    HORIZONTAL = '═'
    VERTICAL = '║'
    
    # Single line box
    S_TOP_LEFT = '┌'
    S_TOP_RIGHT = '┐'
    S_BOTTOM_LEFT = '└'
    S_BOTTOM_RIGHT = '┘'
    S_HORIZONTAL = '─'
    S_VERTICAL = '│'
    S_CROSS = '┼'
    S_T_DOWN = '┬'
    S_T_UP = '┴'
    S_T_RIGHT = '├'
    S_T_LEFT = '┤'
    
    # Rounded box (modern style)
    R_TOP_LEFT = '╭'
    R_TOP_RIGHT = '╮'
    R_BOTTOM_LEFT = '╰'
    R_BOTTOM_RIGHT = '╯'
    R_HORIZONTAL = '─'
    R_VERTICAL = '│'
    R_T_RIGHT = '├'
    R_T_LEFT = '┤'


def print_colored(text: str, color: str = Colors.TEXT, end: str = '\n'):
    """Print colored text"""
    print(f"{color}{text}{Colors.RESET}", end=end)


def print_success(text: str):
    """Print success message"""
    print_colored(f"{Colors.ICON_SUCCESS} {text}", Colors.SUCCESS)


def print_error(text: str):
    """Print error message"""
    print_colored(f"{Colors.ICON_ERROR} {text}", Colors.ERROR)


def print_warning(text: str):
    """Print warning message"""
    print_colored(f"{Colors.ICON_WARNING} {text}", Colors.WARNING)


def print_info(text: str):
    """Print info message"""
    print_colored(f"{Colors.ICON_INFO} {text}", Colors.INFO)
