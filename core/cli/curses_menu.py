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
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)      # White on red (highlight)
        curses.init_pair(4, curses.COLOR_CYAN, -1)                     # Cyan/blue for keys
        curses.init_pair(5, curses.COLOR_RED, -1)                      # Dim red for hex background
        curses.init_pair(6, curses.COLOR_GREEN, -1)                    # Green for glitch/commands/arrow
        curses.init_pair(7, 8, -1)                                     # Gray for numbers/brackets/links
        
        # Hide cursor
        curses.curs_set(0)
        
        # Non-blocking input
        self.stdscr.nodelay(True)
        self.stdscr.timeout(100)  # 100ms timeout
    
    def draw_animation(self):
        """Draw the animated header - red hex background with bright red FADCRYPT and green glitch"""
        text = "[ F A D C R Y P T ]"
        hex_chars = "0123456789ABCDEF"
        glitch_chars = "!@#$%^&*01"
        
        try:
            padding = (60 - len(text)) // 2
            text_start = padding
            text_end = padding + len(text)
            
            # Row 0 & 2: Hex backgrounds - RED variants
            for row in [0, 2]:
                col_pos = 2
                for _ in range(20):
                    hex_byte = random.choice(hex_chars) + random.choice(hex_chars)
                    
                    # Multiple red variants for variety
                    rand = random.random()
                    if rand > 0.7:
                        # Bright red
                        self.stdscr.addstr(row, col_pos, hex_byte + " ", curses.color_pair(1) | curses.A_BOLD)
                    elif rand > 0.4:
                        # Normal red
                        self.stdscr.addstr(row, col_pos, hex_byte + " ", curses.color_pair(1))
                    else:
                        # Dim red
                        self.stdscr.addstr(row, col_pos, hex_byte + " ", curses.color_pair(5) | curses.A_DIM)
                    col_pos += 3
            
            # Row 1: Middle row - hex background with gap for text
            col_pos = 2
            while col_pos < 62:
                # Leave gap for text
                if col_pos >= text_start - 3 and col_pos <= text_end + 3:
                    col_pos += 3
                    continue
                
                hex_byte = random.choice(hex_chars) + random.choice(hex_chars)
                
                # Multiple red variants for variety
                rand = random.random()
                if rand > 0.7:
                    # Bright red
                    self.stdscr.addstr(1, col_pos, hex_byte + " ", curses.color_pair(1) | curses.A_BOLD)
                elif rand > 0.4:
                    # Normal red
                    self.stdscr.addstr(1, col_pos, hex_byte + " ", curses.color_pair(1))
                else:
                    # Dim red
                    self.stdscr.addstr(1, col_pos, hex_byte + " ", curses.color_pair(5) | curses.A_DIM)
                col_pos += 3
            
            # Draw FADCRYPT text with glitch effect
            glitched_text = ""
            for char in text:
                if char in ['[', ']', ' ']:
                    glitched_text += char
                elif random.random() > 0.92:  # 8% chance to glitch
                    glitched_text += random.choice(glitch_chars)
                else:
                    glitched_text += char
            
            # Draw the text - WHITE with GREEN glitch
            for i, char in enumerate(glitched_text):
                if char in glitch_chars and char not in ['[', ']', ' ', '0', '1']:
                    # Glitch characters in GREEN
                    self.stdscr.addstr(1, padding + i, char, curses.color_pair(6) | curses.A_BOLD)
                else:
                    # Normal characters in WHITE
                    self.stdscr.addstr(1, padding + i, char, curses.color_pair(2) | curses.A_BOLD)
            
            # Author info below hex animation (row 3)
            # Format: "Author: Faded | github.com/anonfaded"
            author_name = "Author: Faded"
            separator = " | "
            author_link = "github.com/anonfaded"
            
            # Apply glitch effect to author name only
            glitched_author = ""
            for char in author_name:
                if char not in ['A', 'u', 't', 'h', 'o', 'r', ':', ' '] and random.random() > 0.92:
                    glitched_author += random.choice(glitch_chars)
                else:
                    glitched_author += char
            
            # Calculate total length and center it
            full_text = glitched_author + separator + author_link
            author_padding = (60 - len(full_text)) // 2
            
            # Draw glitched author name
            col_offset = 0
            for char in glitched_author:
                if char in glitch_chars:
                    # Glitch in green
                    self.stdscr.addstr(3, author_padding + col_offset, char, curses.color_pair(6) | curses.A_BOLD)
                else:
                    # Normal text in white
                    self.stdscr.addstr(3, author_padding + col_offset, char, curses.color_pair(2))
                col_offset += 1
            
            # Draw separator in gray
            self.stdscr.addstr(3, author_padding + col_offset, separator, curses.color_pair(7))
            col_offset += len(separator)
            
            # Draw link in gray
            self.stdscr.addstr(3, author_padding + col_offset, author_link, curses.color_pair(7))
            
            self.animation_frame += 1
        except curses.error:
            pass
    
    def draw_header(self):
        """Draw static header - not used for main menu with animation"""
        pass
    
    def draw_menu(self):
        """Draw the menu - styled exactly like file selector"""
        start_row = 5  # Start after animation (rows 0-2), author info (row 3), and blank row 4
        
        try:
            # Menu header - BOLD RED with emoji
            self.stdscr.addstr(start_row, 2, "╭─ ", curses.color_pair(1))
            # Add emoji before title if it's MAIN MENU
            if self.title == "MAIN MENU":
                self.stdscr.addstr(start_row, 5, "📋 ", curses.color_pair(1))
                self.stdscr.addstr(start_row, 8, self.title, curses.color_pair(1) | curses.A_BOLD)
            else:
                self.stdscr.addstr(start_row, 5, self.title, curses.color_pair(1) | curses.A_BOLD)
            self.stdscr.addstr(start_row + 1, 2, "│", curses.color_pair(1))
            
            # Menu items
            for i, item in enumerate(self.menu_items):
                row = start_row + 2 + i
                icon = item.get('icon', '')
                text = item.get('text', '')
                key = item.get('key', str(i + 1))
                
                if i == self.cursor_pos:
                    # Highlighted item - GREEN arrow, white text on red background
                    # Format: │❯ [content with white text on red background]
                    self.stdscr.addstr(row, 2, "│", curses.color_pair(1))
                    self.stdscr.addstr(row, 3, "❯", curses.color_pair(6) | curses.A_BOLD)
                    self.stdscr.addstr(row, 4, " ")
                    # White text on red background for the content
                    content = f"{key}. {icon} {text}".ljust(57)
                    self.stdscr.addstr(row, 5, content, curses.color_pair(3) | curses.A_BOLD)
                else:
                    # Normal item - RED pipes, GRAY numbers/dots, white icon/text
                    self.stdscr.addstr(row, 2, "│", curses.color_pair(1))
                    self.stdscr.addstr(row, 3, "  ")
                    # Number and dot in gray
                    self.stdscr.addstr(row, 5, f"{key}.", curses.color_pair(7))
                    # Icon and text in default white
                    self.stdscr.addstr(row, 7, f" {icon} {text}")
            
            # Menu footer - RED color
            self.stdscr.addstr(start_row + 2 + len(self.menu_items), 2, "│", curses.color_pair(1))
            self.stdscr.addstr(start_row + 3 + len(self.menu_items), 2, "╰" + "─" * 60, curses.color_pair(1))
            
            # Help text - RED heading, GRAY brackets/labels, WHITE commands
            help_row = start_row + 5 + len(self.menu_items)
            self.stdscr.addstr(help_row, 2, "Navigation:", curses.color_pair(1) | curses.A_BOLD)
            # Format: [↑↓] Navigate  [Enter] Select  [B] Back  [Q] Quit
            # Brackets and labels in gray, commands in white
            help_row += 1
            col = 2
            # [↑↓] Navigate
            self.stdscr.addstr(help_row, col, "[", curses.color_pair(7))
            col += 1
            self.stdscr.addstr(help_row, col, "↑↓", curses.color_pair(2))
            col += 2
            self.stdscr.addstr(help_row, col, "]", curses.color_pair(7))
            col += 1
            self.stdscr.addstr(help_row, col, " Navigate  ", curses.color_pair(7))
            col += 11
            # [Enter] Select
            self.stdscr.addstr(help_row, col, "[", curses.color_pair(7))
            col += 1
            self.stdscr.addstr(help_row, col, "Enter", curses.color_pair(2))
            col += 5
            self.stdscr.addstr(help_row, col, "]", curses.color_pair(7))
            col += 1
            self.stdscr.addstr(help_row, col, " Select  ", curses.color_pair(7))
            col += 9
            # [B] Back
            self.stdscr.addstr(help_row, col, "[", curses.color_pair(7))
            col += 1
            self.stdscr.addstr(help_row, col, "B", curses.color_pair(2))
            col += 1
            self.stdscr.addstr(help_row, col, "]", curses.color_pair(7))
            col += 1
            self.stdscr.addstr(help_row, col, " Back  ", curses.color_pair(7))
            col += 7
            # [Q] Quit
            self.stdscr.addstr(help_row, col, "[", curses.color_pair(7))
            col += 1
            self.stdscr.addstr(help_row, col, "Q", curses.color_pair(2))
            col += 1
            self.stdscr.addstr(help_row, col, "]", curses.color_pair(7))
            col += 1
            self.stdscr.addstr(help_row, col, " Quit", curses.color_pair(7))
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
        self.draw_menu()
        self.stdscr.noutrefresh()
        curses.doupdate()
        
        while True:
            try:
                key = self.stdscr.getch()
                
                if key == curses.KEY_UP:
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                    # Clear menu area and redraw (start from row 4)
                    for row in range(4, 25):
                        self.stdscr.addstr(row, 0, " " * 100)
                    self.draw_menu()
                    self.stdscr.noutrefresh()
                    curses.doupdate()
                    
                elif key == curses.KEY_DOWN:
                    self.cursor_pos = min(len(self.menu_items) - 1, self.cursor_pos + 1)
                    # Clear menu area and redraw (start from row 4)
                    for row in range(4, 25):
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
