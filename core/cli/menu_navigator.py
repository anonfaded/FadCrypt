"""
Menu Navigator

Provides arrow-key navigation for menus with consistent UI.
"""

import sys
# Optional dependency to compute terminal display width for Unicode characters
try:
    from wcwidth import wcwidth
    _HAS_WCWIDTH = True
except ImportError:
    _HAS_WCWIDTH = False
from typing import List, Dict, Optional, Callable

# Platform-specific keyboard input
try:
    if sys.platform == 'win32':
        import msvcrt
    else:
        import termios
        import tty
except ImportError:
    pass

from .colors import Colors


def confirm_action(message: str) -> bool:
    """Show confirmation dialog and return True if confirmed"""
    print(f"\n{Colors.WARNING}{message} (y/n):{Colors.RESET}")
    print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
    return input().strip().lower() == 'y'


def get_key():
    """Get a single keypress without pressing Enter - blocking version"""
    if sys.platform == 'win32':
        # Windows - blocking wait for key
        key = msvcrt.getch()
        if key == b'\xe0':  # Special key prefix
            key = msvcrt.getch()
            if key == b'H':  # Up arrow
                return 'up'
            if key == b'P':  # Down arrow
                return 'down'
            if key == b'K':  # Left arrow
                return 'left'
            if key == b'M':  # Right arrow
                return 'right'
            return None  # Unknown special key
        elif key == b' ':  # Space
            return 'space'
        elif key == b'\r':  # Enter
            return 'enter'
        elif key == b'\x1b':  # Escape
            return 'escape'
        elif key in [b'q', b'Q']:
            return 'q'
        elif key in [b'b', b'B']:
            return 'b'
        else:
            return key.decode('utf-8', errors='ignore').lower()
    else:
        # Unix/Linux - blocking wait for key
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
            if key == '\x1b':  # Escape sequence
                key += sys.stdin.read(2)
                if key == '\x1b[A':  # Up arrow
                    return 'up'
                if key == '\x1b[B':  # Down arrow
                    return 'down'
            elif key == ' ':  # Space
                return 'space'
            elif key in ('\r', '\n'):  # Enter
                return 'enter'
            elif key == '\x1b':  # Escape
                return 'escape'
            else:
                return key.lower()
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


class MenuNavigator:
    """Interactive menu navigator with arrow keys and red background highlighting"""
    
    def __init__(self):
        """Initialize menu navigator"""
        self.cursor_pos = 0
        self.menu_items = []
    
    def show_menu(self, title: str, items: List[Dict], header_func: Optional[Callable] = None) -> Optional[str]:
        """
        Show interactive menu with arrow navigation.
        
        Args:
            title: Menu title
            items: List of menu items with 'key', 'icon', 'text', 'action' keys
            header_func: Optional function to display header
        
        Returns:
            Selected item key or None if cancelled
        """
        self.menu_items = items
        self.cursor_pos = 0
        
        while True:
            # Clear screen and show header
            if header_func:
                header_func()
            
            # Display menu
            print(f"{Colors.BORDER}╭─ {Colors.TITLE}{title}{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET}")
            
            # Define the inner width used for menu content so we can pad lines to a
            # consistent displayed length. Using wcwidth (if available) gives a
            # more accurate visual width for emojis and wide characters.
            INNER_WIDTH = 60

            def _display_width(s: str) -> int:
                if _HAS_WCWIDTH:
                    # Sum the display width of each codepoint; wcwidth returns -1
                    # for non-printable chars so clamp to 0.
                    w = 0
                    for ch in s:
                        try:
                            cw = wcwidth(ch)
                        except TypeError:
                            cw = 1
                        w += max(0, cw)
                    return w
                # Fallback: use Python length (codepoints)
                return len(s)

            for i, item in enumerate(self.menu_items):
                is_cursor = i == self.cursor_pos

                number = f" {item['key']}.'" if False else f" {item['key']}."
                icon = item['icon']
                text = item['text']

                # Build the raw content for the line (number + icon + separator + text)
                raw = f"{number} {icon} {text}"

                # Compute padding based on display width
                pad_len = max(0, INNER_WIDTH - _display_width(raw))
                padded = raw + (' ' * pad_len)

                if is_cursor:
                    # Highlight the padded area for selected row
                    print(f"{Colors.BORDER}│{Colors.SUCCESS}❯{Colors.RESET} \033[41m{padded}\033[0m")
                else:
                    # Non-selected: explicitly print number, icon, and text with
                    # explicit single spaces between them to avoid any cases
                    # where emoji/variation selectors could visually collapse a
                    # separating space when concatenated from slices.
                    # We reuse pad_len to append trailing spaces to match width.
                    padded_rest = ' ' * pad_len
                    print(f"{Colors.BORDER}│{Colors.RESET}  {Colors.DIM}{number}{Colors.RESET} {Colors.TEXT}{icon} {text}{padded_rest}{Colors.RESET}")
            
            print(f"{Colors.BORDER}│{Colors.RESET}")
            print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}\n")
            
            # Help text
            print(f"{Colors.INFO}Navigation:{Colors.RESET}")
            print(f"{Colors.DIM}[{Colors.SUCCESS}↑↓{Colors.DIM}] Navigate  "
                  f"[{Colors.SUCCESS}Enter{Colors.DIM}] Select  "
                  f"[{Colors.SUCCESS}B{Colors.DIM}] Back  "
                  f"[{Colors.SUCCESS}Q{Colors.DIM}] Quit{Colors.RESET}\n")
            
            # Get key input
            key = get_key()
            
            # Skip if key is None (unknown special key like right/left arrow)
            if key is None:
                continue
            
            if key == 'up':
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif key == 'down':
                self.cursor_pos = min(len(self.menu_items) - 1, self.cursor_pos + 1)
            elif key == 'enter':
                return self.menu_items[self.cursor_pos]['key']
            elif key == 'b':
                return 'back'
            elif key == 'q':
                if confirm_action("Are you sure you want to quit?"):
                    return 'quit'
            elif key and key.isdigit():
                # Direct number selection
                num = int(key)
                for item in self.menu_items:
                    if item['key'] == str(num):
                        return item['key']
            # Continue loop for other keys