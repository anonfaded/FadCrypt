"""
Curses-based animated menu for FadCrypt
Provides smooth continuous animation with menu navigation
"""

import curses
import time
import random
import locale
import os
from threading import Thread
from typing import List, Dict, Optional
from ..version import __version__


class AnimatedCursesMenu:
    """Animated menu using curses"""
    
    def __init__(self, stdscr, quit_text: str = "Quit"):
        self.stdscr = stdscr
        self.cursor_pos = 0
        self.running = True
        self.animation_frame = 0
        self.menu_items = []
        self.title = ""
        self.quit_text = quit_text
        
        # Set up proper encoding for emoji support
        try:
            locale.setlocale(locale.LC_ALL, '')
            os.environ.setdefault('LANG', 'en_US.UTF-8')
        except:
            pass
        
        # Force UTF-8 mode for the terminal
        try:
            curses.curs_set(0)
            self.stdscr.keypad(True)
        except:
            pass
        
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
        
        # Get terminal dimensions for centering
        height, width = self.stdscr.getmaxyx()
        
        # Calculate total content height (animation 5 rows + menu ~20 rows = 25)
        total_content_height = 25
        vertical_start = max(0, (height - total_content_height) // 2)
        
        # Calculate centered position for animation
        anim_width = min(62, width - 4)  # Max 62 chars for animation
        anim_start_col = (width - anim_width) // 2 + 2  # Slight right adjustment
        # Center text at the middle of the 60-character animation area
        padding = anim_start_col + 30 - len(text) // 2
        text_start = padding
        text_end = padding + len(text)
        
        try:
            # Row 0 & 2: Hex backgrounds - RED variants
            for row in [vertical_start, vertical_start + 2]:
                col_pos = anim_start_col
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
            row = vertical_start + 1
            col_pos = anim_start_col
            while col_pos < anim_start_col + 60:  # 20 hex * 3 = 60
                # Leave symmetric gap for text with 3-char padding on each side
                if col_pos >= text_start - 3 and col_pos <= text_end + 3:
                    col_pos += 3
                    continue
                
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
                    self.stdscr.addstr(row, padding + i, char, curses.color_pair(6) | curses.A_BOLD)
                else:
                    # Normal characters in WHITE
                    self.stdscr.addstr(row, padding + i, char, curses.color_pair(2) | curses.A_BOLD)
            
            # Add author/GitHub info right below FADCRYPT animation (with continuous glitch)
            author_row = vertical_start + 3  # Right after hex animation
            author_label = "Author: "
            author_text = "Faded"
            separator = " | "
            github_url = "github.com/anonfaded"
            
            # Build glitched "Faded" text (continuous animation each frame)
            glitched_faded = ""
            for char in author_text:
                if random.random() > 0.92:  # Same 8% glitch rate
                    glitched_faded += random.choice(glitch_chars)
                else:
                    glitched_faded += char
            
            # Calculate centered position for author line
            full_line = author_label + glitched_faded + separator + github_url
            full_line_length = len(author_label) + len(author_text) + len(separator) + len(github_url)
            author_col = (width - full_line_length) // 2
            
            try:
                # Draw "Author: " label
                self.stdscr.addstr(author_row, author_col, author_label, curses.color_pair(2))
                col_pos = author_col + len(author_label)
                
                # Draw "Faded" with glitch effect
                for i, char in enumerate(glitched_faded):
                    if char in glitch_chars:
                        self.stdscr.addstr(author_row, col_pos + i, char, curses.color_pair(6) | curses.A_BOLD)
                    else:
                        self.stdscr.addstr(author_row, col_pos + i, char, curses.color_pair(2) | curses.A_BOLD)
                col_pos += len(author_text)
                
                # Draw separator
                self.stdscr.addstr(author_row, col_pos, separator, curses.color_pair(2))
                col_pos += len(separator)
                
                # Draw GitHub link
                self.stdscr.addstr(author_row, col_pos, github_url, curses.color_pair(7))
            except curses.error:
                pass
            
            # Add footer branding near bottom of screen (with safety check)
            height, width = self.stdscr.getmaxyx()
            min_footer_space = 6  # Need 4 lines for logo + 1 for branding + 1 spacing
            footer_row = max(vertical_start + 6, height - min_footer_space)  # Don't go below animation, don't go out of bounds
            
            # Logo lines definition
            logo_lines = [
                " ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▒▒▒▒▒▒ ▒▒▒▒▒▒▒ ▒▒▒▒▒▒▒",
                " ▓▓▓▓▓▓▓ ▓▓   ▓▓▓▓    ▓▓▒▒▒▒▒▒       ▒▒ ▒▒      ▓    ▓",
                " ▓▓      ▓▓▓▓▓▓▓▓▓    ▓▓      ▒▒     ▒▒ ▒▒      ▓ ▓▓ ▓▓",
                " ▓▓      ▓▓   ▓▓▓▓▓▓▓▓▓ ▒▒▒▒▒▒▒ ▒▒▒▒▒▒▒ ▒▒▒▒▒▒▒"
            ]
            
            # Only draw footer if there's enough space
            if footer_row + min_footer_space <= height:
                # Calculate box dimensions for footer positioning
                box_width = min(60, width - 4)
                box_start_col = (width - box_width) // 2
                
                # Position ASCII block slightly left of center within the box
                ascii_block_width = len(logo_lines[0])  # Width of the ASCII art
                # Start 1 character from box left edge instead of centering
                ascii_start_col = box_start_col + 1
                
                for i, logo_line in enumerate(logo_lines):
                    self.stdscr.addstr(footer_row + i, ascii_start_col, logo_line, curses.color_pair(1))
                
                # Website and license info below the logo (centered within the box)
                branding_row = footer_row + 4
                branding_text = "https://faded.dev · © 2024–2025 · GPLv3 License"
                branding_col = box_start_col + (box_width - len(branding_text)) // 2
                self.stdscr.addstr(branding_row, branding_col, branding_text, curses.color_pair(7))
            
            self.animation_frame += 1
        except curses.error:
            pass
    
    def draw_header(self):
        """Draw static header - not used for main menu with animation"""
        pass
    
    def draw_menu(self):
        """Draw the menu - responsive and centered"""
        # Get terminal dimensions for responsive centering
        height, width = self.stdscr.getmaxyx()
        
        # Calculate responsive dimensions - increase max box width to 75 for better text display
        box_width = min(75, width - 4)  # Increased from 70 to 75
        start_col = (width - box_width) // 2
        
        # For main menu, start after animation (which is vertically centered)
        if self.title == "MAIN MENU":
            total_content_height = 25
            vertical_start = max(0, (height - total_content_height) // 2)
            start_row = vertical_start + 5  # After animation (5 rows)
        else:
            start_row = max(1, (height - 20) // 2)  # Center vertically for sub-menus
        
        current_row = start_row  # Start at centered position
        
        try:
            # Draw app header for non-main menus
            if self.title != "MAIN MENU":
                # App header - near pipe (not centered)
                header_text = f"🏴 FadCrypt v{__version__}"
                self.stdscr.addstr(current_row, start_col, "╭─ ", curses.color_pair(1))
                self.stdscr.addstr(current_row, start_col + 3, header_text, curses.color_pair(1) | curses.A_BOLD)
                current_row += 1
                
                subtitle = "File, Folder & Application Protection Suite"
                self.stdscr.addstr(current_row, start_col, "│ ", curses.color_pair(1))
                self.stdscr.addstr(current_row, start_col + 2, subtitle, curses.color_pair(2))
                current_row += 1
                
                self.stdscr.addstr(current_row, start_col, "╰" + "─" * (box_width - 2), curses.color_pair(1))
                current_row += 1
                
                # Blank line
                current_row += 1
            
            # Menu header - BOLD RED with emoji
            menu_start_row = current_row
            if self.title == "MAIN MENU":
                # For main menu, title near the pipe with emoji
                title_text = f"🏴 {self.title}"
                self.stdscr.addstr(menu_start_row, start_col, "╭─ ", curses.color_pair(1))
                self.stdscr.addstr(menu_start_row, start_col + 3, title_text, curses.color_pair(1) | curses.A_BOLD)
            else:
                # For sub-menus, title near the pipe with appropriate emoji
                if "LOCK" in self.title or "PROTECT" in self.title:
                    emoji = "🔒"
                elif "UNLOCK" in self.title or "RELEASE" in self.title:
                    emoji = "🔓"
                elif "BROWSE" in self.title or "SELECT" in self.title:
                    emoji = "📁"
                elif "SETTINGS" in self.title or "CONFIG" in self.title:
                    emoji = "⚙️"
                elif "HELP" in self.title:
                    emoji = "❓"
                else:
                    emoji = "📋"
                title_text = f"{emoji} {self.title}"
                self.stdscr.addstr(menu_start_row, start_col, "╭─ ", curses.color_pair(1))
                self.stdscr.addstr(menu_start_row, start_col + 3, title_text, curses.color_pair(1) | curses.A_BOLD)
            self.stdscr.addstr(menu_start_row + 1, start_col, "│", curses.color_pair(1))
            
            # Menu items
            for i, item in enumerate(self.menu_items):
                row = menu_start_row + 2 + i
                icon = item.get('icon', '')
                text = item.get('text', '')
                key = item.get('key', str(i + 1))
                
                if i == self.cursor_pos:
                    # Highlighted item - fill entire row with background color first
                    padding_width = max(1, box_width - 3)
                    try:
                        self.stdscr.addstr(row, start_col, "│" + " " * padding_width, curses.color_pair(3))
                    except curses.error:
                        pass
                    # Redraw the text elements on top of the red background
                    try:
                        self.stdscr.addstr(row, start_col, "│", curses.color_pair(1))
                        self.stdscr.addstr(row, start_col + 1, "❯", curses.color_pair(6) | curses.A_BOLD)
                        self.stdscr.addstr(row, start_col + 2, " ")
                        self.stdscr.addstr(row, start_col + 3, f"{key}.", curses.color_pair(3) | curses.A_BOLD)
                        self.stdscr.addstr(row, start_col + 5, " ", curses.color_pair(3) | curses.A_BOLD)
                        # Write emoji and space, then text separately
                        col_pos = start_col + 6
                        if col_pos < width - 1:
                            self.stdscr.addstr(row, col_pos, f"{icon} ", curses.color_pair(3) | curses.A_BOLD)
                        # Text goes right after - emoji (2 cols) + space (1 col) = 3 total
                        col_pos = start_col + 6 + 3
                        if col_pos < width - 1:
                            remaining = width - col_pos - 1
                            text_truncated = text[:remaining] if len(text) > remaining else text
                            self.stdscr.addstr(row, col_pos, text_truncated, curses.color_pair(3) | curses.A_BOLD)
                    except curses.error:
                        pass
                else:
                    # Normal item - clear entire row first
                    padding_width = max(1, box_width - 1)
                    try:
                        self.stdscr.addstr(row, start_col, "│" + " " * padding_width, curses.color_pair(1))
                    except curses.error:
                        pass
                    # Now redraw the text
                    try:
                        self.stdscr.addstr(row, start_col, "│", curses.color_pair(1))
                        self.stdscr.addstr(row, start_col + 1, "  ")
                        # Number and dot in gray
                        self.stdscr.addstr(row, start_col + 3, f"{key}.", curses.color_pair(7))
                        # Write emoji and space, then text separately
                        col_pos = start_col + 6
                        if col_pos < width - 1:
                            self.stdscr.addstr(row, col_pos, f"{icon} ", curses.color_pair(2))
                        # Text goes right after - emoji (2 cols) + space (1 col) = 3 total
                        col_pos = start_col + 6 + 3
                        if col_pos < width - 1:
                            remaining = width - col_pos - 1
                            text_truncated = text[:remaining] if len(text) > remaining else text
                            self.stdscr.addstr(row, col_pos, text_truncated, curses.color_pair(2))
                    except curses.error:
                        pass

            # Single refresh call at the end to ensure proper emoji rendering
            self.stdscr.noutrefresh()
            
            # Menu footer - RED color
            footer_row1 = menu_start_row + 2 + len(self.menu_items)
            footer_row2 = menu_start_row + 3 + len(self.menu_items)
            
            self.stdscr.addstr(footer_row1, start_col, "│", curses.color_pair(1))
            self.stdscr.addstr(footer_row2, start_col, "╰" + "─" * (box_width - 2), curses.color_pair(1))
            
            # Help text - RED heading, GRAY brackets/labels, WHITE commands
            help_row = menu_start_row + 5 + len(self.menu_items)
            help_text = "Navigation:"
            self.stdscr.addstr(help_row, start_col, help_text, curses.color_pair(1) | curses.A_BOLD)
            
            # Format help text responsively
            help_items = [
                ("[↑↓]", "Navigate"),
                ("[Enter]", "Select"),
                ("[B]", "Back"),
                ("[Q]", self.quit_text)
            ]
            
            help_row += 1
            col = start_col
            for bracket, label in help_items:
                if col + len(bracket) + len(label) + 2 > start_col + box_width:
                    break  # Don't overflow
                self.stdscr.addstr(help_row, col, bracket[0], curses.color_pair(7))  # [
                col += 1
                self.stdscr.addstr(help_row, col, bracket[1:-1], curses.color_pair(2))  # content
                col += len(bracket) - 2
                self.stdscr.addstr(help_row, col, bracket[-1], curses.color_pair(7))  # ]
                col += 1
                self.stdscr.addstr(help_row, col, f" {label}  ", curses.color_pair(7))
                col += len(label) + 3
        except curses.error:
            pass
        
        # Final refresh to ensure emojis display properly
        self.stdscr.noutrefresh()
    
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
                    # Only redraw menu area, not animation
                    self.draw_menu()
                    self.stdscr.noutrefresh()
                    curses.doupdate()
                    
                elif key == curses.KEY_DOWN:
                    self.cursor_pos = min(len(self.menu_items) - 1, self.cursor_pos + 1)
                    # Only redraw menu area, not animation
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
    
    # Set up UTF-8 encoding for emoji support
    try:
        import locale
        import os
        locale.setlocale(locale.LC_ALL, '')
        os.environ.setdefault('LANG', 'en_US.UTF-8')
    except:
        pass
        
except ImportError:
    CURSES_AVAILABLE = False


def show_curses_menu(title: str, items: List[Dict], quit_text: str = "Quit") -> Optional[str]:
    """
    Show curses menu with animation (wrapper function)
    
    Args:
        title: Menu title
        items: List of menu items
        quit_text: Text for Q key ("Quit" for main menu, "Back" for sub-menus)
        
    Returns:
        Selected action or None
    """
    if not CURSES_AVAILABLE:
        return None
    
    def _menu_wrapper(stdscr):
        menu = AnimatedCursesMenu(stdscr, quit_text=quit_text)
        return menu.show_menu(title, items)
    
    try:
        result = curses.wrapper(_menu_wrapper)
        # Restore terminal state and encoding after curses exits
        import sys
        import io
        sys.stdout.flush()
        sys.stderr.flush()
        # Reset to UTF-8 encoding in case curses changed it
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        return result
    except Exception:
        return None
