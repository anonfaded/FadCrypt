"""
Curses-based animated menu for FadCrypt
Provides smooth continuous animation with menu navigation
"""

import curses
import time
import random
from threading import Thread
from typing import List, Dict, Optional


class AnimatedCursesMenu:
    """Animated menu using curses"""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.cursor_pos = 0
        self.running = True
        self.animation_frame = 0
        self.menu_items = []
        self.title = ""
        
        # Setup colors
        curses.start_color()
        try:
            curses.use_default_colors()  # Use terminal's default colors
        except AttributeError:
            pass  # Not available in all curses implementations
        
        curses.init_pair(1, curses.COLOR_RED, -1)                      # Red on default
        curses.init_pair(2, curses.COLOR_WHITE, -1)                    # White on default
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_RED)      # Black on red (highlight)
        
        # Hide cursor
        curses.curs_set(0)
        
        # Non-blocking input
        self.stdscr.nodelay(True)
        self.stdscr.timeout(100)  # 100ms timeout
    
    def draw_animation(self):
        """Draw the animated header - red hex codes and pulsing FADCRYPT"""
        text = "F A D C R Y P T"
        hex_chars = "0123456789ABCDEF"
        
        try:
            # Row 1: Hex background (top)
            line = ""
            for _ in range(20):
                hex_byte = random.choice(hex_chars) + random.choice(hex_chars)
                line += hex_byte + " "
            
            color = curses.color_pair(1) if self.animation_frame % 4 < 2 else curses.color_pair(1) | curses.A_BOLD
            self.stdscr.addstr(1, 2, line[:60], color)
            
            # Row 2: FadCrypt text (middle) - pulse between white and red
            padding = (60 - len(text)) // 2
            text_color = curses.color_pair(2) | curses.A_BOLD if self.animation_frame % 4 < 2 else curses.color_pair(1) | curses.A_BOLD
            self.stdscr.addstr(2, padding, text, text_color)
            
            # Row 3: Hex background (bottom)
            line = ""
            for _ in range(20):
                hex_byte = random.choice(hex_chars) + random.choice(hex_chars)
                line += hex_byte + " "
            self.stdscr.addstr(3, 2, line[:60], color)
            
            self.animation_frame += 1
        except curses.error:
            pass
    
    def draw_header(self):
        """Draw static header"""
        try:
            from FadCrypt import __version__
            self.stdscr.addstr(0, 2, f"╭─ 🏴 FadCrypt v{__version__}", curses.A_BOLD)
        except:
            self.stdscr.addstr(0, 2, "╭─ 🏴 FadCrypt", curses.A_BOLD)
    
    def draw_menu(self):
        """Draw the menu"""
        start_row = 5
        
        try:
            # Menu header
            self.stdscr.addstr(start_row, 2, f"╭─ {self.title}", curses.A_BOLD)
            self.stdscr.addstr(start_row + 1, 2, "│")
            
            # Menu items
            for i, item in enumerate(self.menu_items):
                row = start_row + 2 + i
                icon = item.get('icon', '')
                text = item.get('text', '')
                key = item.get('key', str(i + 1))
                
                if i == self.cursor_pos:
                    # Highlighted item
                    prefix = f"│❯ {key}. {icon} {text}"
                    padded = prefix.ljust(62)
                    self.stdscr.addstr(row, 2, padded, curses.color_pair(3) | curses.A_BOLD)
                else:
                    # Normal item
                    self.stdscr.addstr(row, 2, f"│  {key}. {icon} {text}")
            
            # Menu footer
            self.stdscr.addstr(start_row + 2 + len(self.menu_items), 2, "│")
            self.stdscr.addstr(start_row + 3 + len(self.menu_items), 2, "╰" + "─" * 60)
            
            # Help text
            help_row = start_row + 5 + len(self.menu_items)
            self.stdscr.addstr(help_row, 2, "Navigation:", curses.A_BOLD)
            self.stdscr.addstr(help_row + 1, 2, "[↑↓] Navigate  [Enter] Select  [B] Back  [Q] Quit")
        except curses.error:
            pass
    
    def animation_loop(self):
        """Continuous animation loop in background"""
        while self.running:
            try:
                self.draw_animation()
                self.stdscr.noutrefresh()
                curses.doupdate()
                time.sleep(0.15)
            except:
                pass
    
    def show_menu(self, title: str, items: List[Dict]) -> Optional[str]:
        """
        Show animated menu
        
        Args:
            title: Menu title
            items: List of menu items with 'key', 'icon', 'text', 'action' keys
            
        Returns:
            Selected action or None
        """
        self.title = title
        self.menu_items = items
        self.cursor_pos = 0
        
        # Start animation thread only for main menu
        anim_thread = None
        if title == "MAIN MENU":
            anim_thread = Thread(target=self.animation_loop, daemon=True)
            anim_thread.start()
        
        # Initial draw
        self.stdscr.clear()
        self.draw_header()
        if title == "MAIN MENU":
            # Space for animation
            pass
        self.draw_menu()
        self.stdscr.noutrefresh()
        curses.doupdate()
        
        while True:
            try:
                key = self.stdscr.getch()
                
                if key == curses.KEY_UP:
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                    # Clear menu area and redraw
                    for row in range(5, 25):
                        self.stdscr.addstr(row, 0, " " * 100)
                    self.draw_menu()
                    self.stdscr.noutrefresh()
                    curses.doupdate()
                    
                elif key == curses.KEY_DOWN:
                    self.cursor_pos = min(len(self.menu_items) - 1, self.cursor_pos + 1)
                    # Clear menu area and redraw
                    for row in range(5, 25):
                        self.stdscr.addstr(row, 0, " " * 100)
                    self.draw_menu()
                    self.stdscr.noutrefresh()
                    curses.doupdate()
                    
                elif key == ord('\n') or key == ord('\r'):
                    # Enter pressed
                    self.running = False
                    return self.menu_items[self.cursor_pos]['key']
                    
                elif key == ord('b') or key == ord('B'):
                    # Back
                    self.running = False
                    return 'back'
                    
                elif key == ord('q') or key == ord('Q'):
                    # Quit
                    self.running = False
                    return 'quit'
                    
                elif key >= ord('1') and key <= ord('9'):
                    # Number key pressed
                    num = chr(key)
                    for item in self.menu_items:
                        if item['key'] == num:
                            self.running = False
                            return item['key']
            except:
                pass
            
            time.sleep(0.05)


def has_curses_support() -> bool:
    """Check if curses is available"""
    try:
        import curses
        return True
    except ImportError:
        return False



# Check if curses is available
try:
    import curses
    CURSES_AVAILABLE = True
except ImportError:
    CURSES_AVAILABLE = False


def show_curses_menu(title: str, items: List[Dict]) -> Optional[str]:
    """
    Show curses menu with animation (wrapper function)
    
    Args:
        title: Menu title
        items: List of menu items
        
    Returns:
        Selected action or None
    """
    if not CURSES_AVAILABLE:
        return None
    
    def _menu_wrapper(stdscr):
        menu = AnimatedCursesMenu(stdscr)
        return menu.show_menu(title, items)
    
    try:
        return curses.wrapper(_menu_wrapper)
    except Exception:
        return None
