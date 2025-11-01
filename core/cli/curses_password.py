"""
Curses-based animated password input for FadCrypt
Provides a beautiful animated password prompt with breathing brackets and pulse effects
"""

import curses
import time
import random
from typing import Optional


class AnimatedPasswordInput:
    """Animated password input using curses"""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.running = True
        self.animation_frame = 0
        
        # Setup colors
        curses.start_color()
        try:
            curses.use_default_colors()
        except AttributeError:
            pass
        
        curses.init_pair(1, curses.COLOR_RED, -1)      # Red
        curses.init_pair(2, curses.COLOR_WHITE, -1)    # White
        curses.init_pair(3, curses.COLOR_GREEN, -1)    # Green
        curses.init_pair(4, 8, -1)                     # Gray
        
        # Hide cursor (we'll draw our own)
        curses.curs_set(0)
        
        # Blocking input for password entry
        self.stdscr.nodelay(False)
        
        # Binary rain columns (60 columns for animation area)
        # Each column tracks its current position (0-3, or -1 if inactive)
        self.rain_columns = [random.randint(-1, 3) for _ in range(60)]
    

    
    def prompt_password(self, prompt: str = "Enter your FadCrypt password", 
                       confirm: bool = False) -> Optional[str]:
        """
        Prompt for password with animated display
        
        Args:
            prompt: Prompt text to display
            confirm: If True, ask for confirmation
            
        Returns:
            Password string or None if cancelled
        """
        self.stdscr.clear()
        
        # Left-aligned, hacker-style design
        start_col = 2
        start_row = 2
        
        # Initialize binary rain display (3 rows x 60 columns)
        # Store the character and its age for gradient effect
        rain_display = [[{'char': ' ', 'age': 0} for _ in range(60)] for _ in range(3)]
        
        # Separator line
        separator_row = start_row + 3
        self.stdscr.addstr(separator_row, start_col, "─" * 60, curses.color_pair(1))
        
        # Prompt row - capitalize and format properly
        prompt_row = separator_row + 1
        self.stdscr.addstr(prompt_row, start_col, "┃ ", curses.color_pair(1))
        self.stdscr.addstr(prompt_row, start_col + 2, "🔐 ", curses.color_pair(3))
        
        # Parse prompt to make FadCrypt red
        if "FadCrypt" in prompt:
            parts = prompt.split("FadCrypt")
            # First part (e.g., "Your ")
            self.stdscr.addstr(prompt_row, start_col + 5, parts[0].capitalize(), curses.color_pair(2))
            # FadCrypt in red
            col_offset = start_col + 5 + len(parts[0])
            self.stdscr.addstr(prompt_row, col_offset, "FadCrypt", curses.color_pair(1) | curses.A_BOLD)
            # Rest (e.g., " Password:")
            col_offset += 8
            rest = parts[1].capitalize()
            if not rest.endswith(":"):
                rest += ":"
            self.stdscr.addstr(prompt_row, col_offset, rest, curses.color_pair(2))
        else:
            # Fallback if no FadCrypt in prompt
            formatted_prompt = prompt.capitalize()
            if not formatted_prompt.endswith(":"):
                formatted_prompt += ":"
            self.stdscr.addstr(prompt_row, start_col + 5, formatted_prompt, curses.color_pair(2))
        
        # Input row
        input_row = prompt_row + 1
        
        # Help text
        help_row = input_row + 2
        self.stdscr.addstr(help_row, start_col, "┃ ", curses.color_pair(1))
        self.stdscr.addstr(help_row, start_col + 2, "[", curses.color_pair(4))
        self.stdscr.addstr(help_row, start_col + 3, "Enter", curses.color_pair(2))
        self.stdscr.addstr(help_row, start_col + 8, "] Submit  [", curses.color_pair(4))
        self.stdscr.addstr(help_row, start_col + 19, "Esc", curses.color_pair(2))
        self.stdscr.addstr(help_row, start_col + 22, "] Cancel", curses.color_pair(4))
        
        password = ""
        
        while True:
            # Age all existing characters
            for row in range(3):
                for col in range(60):
                    if rain_display[row][col]['char'] != ' ':
                        rain_display[row][col]['age'] += 1
                        # Remove old characters
                        if rain_display[row][col]['age'] > 2:
                            rain_display[row][col] = {'char': ' ', 'age': 0}
            
            # Update binary rain (Matrix-style falling effect)
            for i in range(60):
                # Random chance to start new drop
                if random.random() > 0.95:
                    self.rain_columns[i] = 0
                
                # Update column if active
                if 0 <= self.rain_columns[i] < 3:
                    bit = random.choice(['0', '1'])
                    row = self.rain_columns[i]
                    
                    # Add new character at current position
                    rain_display[row][i] = {'char': bit, 'age': 0}
                    
                    # Move to next row
                    self.rain_columns[i] += 1
                elif self.rain_columns[i] >= 3:
                    # Reset column
                    self.rain_columns[i] = -1
            
            # Draw binary rain with red gradient using curses colors
            for row_offset in range(3):
                for col in range(60):
                    cell = rain_display[row_offset][col]
                    char = cell['char']
                    age = cell['age']
                    
                    if char != ' ':
                        try:
                            # Gradient based on age (0=bright, 1=normal, 2=dim)
                            if age == 0:
                                # Bright red at head
                                self.stdscr.addstr(start_row + row_offset, start_col + col, char,
                                                 curses.color_pair(1) | curses.A_BOLD)
                            elif age == 1:
                                # Normal red
                                self.stdscr.addstr(start_row + row_offset, start_col + col, char,
                                                 curses.color_pair(1))
                            else:
                                # Dim red (fading)
                                self.stdscr.addstr(start_row + row_offset, start_col + col, char,
                                                 curses.color_pair(1) | curses.A_DIM)
                        except curses.error:
                            pass
                    else:
                        # Clear empty spaces
                        try:
                            self.stdscr.addstr(start_row + row_offset, start_col + col, ' ')
                        except curses.error:
                            pass
            
            # Animated hex prefix for input
            hex_chars = "0123456789ABCDEF"
            hex_prefix = "".join(random.choice(hex_chars) for _ in range(4))
            
            # Draw input line with animated elements
            masked = "*" * len(password)
            cursor = "▌" if self.animation_frame % 2 == 0 else " "
            
            # Clear input line
            self.stdscr.addstr(input_row, start_col, " " * 60)
            
            # Format: ┃ [0xABCD] ❯ ****▌
            self.stdscr.addstr(input_row, start_col, "┃ ", curses.color_pair(1))
            self.stdscr.addstr(input_row, start_col + 2, "[", curses.color_pair(4))
            self.stdscr.addstr(input_row, start_col + 3, f"0x{hex_prefix}", curses.color_pair(1))
            self.stdscr.addstr(input_row, start_col + 9, "]", curses.color_pair(4))
            self.stdscr.addstr(input_row, start_col + 11, "❯", curses.color_pair(3) | curses.A_BOLD)
            self.stdscr.addstr(input_row, start_col + 13, f"{masked}{cursor}", curses.color_pair(2))
            
            # Move cursor off-screen to hide it
            self.stdscr.move(0, 0)
            
            self.stdscr.refresh()
            
            # Get input with timeout for animation
            self.stdscr.timeout(120)
            try:
                key = self.stdscr.getch()
            except:
                key = -1
            
            if key == -1:
                # No input, just animate
                self.animation_frame += 1
                continue
            
            if key == 27:  # ESC
                return None
            elif key == ord('\n') or key == ord('\r'):  # Enter
                if password:
                    if confirm:
                        # Ask for confirmation
                        confirm_password = self.prompt_password("Confirm password", confirm=False)
                        if confirm_password != password:
                            # Show error
                            error_row = help_row + 1
                            self.stdscr.addstr(error_row, start_col, "┃ ", curses.color_pair(1))
                            self.stdscr.addstr(error_row, start_col + 2, "❌ Passwords do not match!", 
                                             curses.color_pair(1) | curses.A_BOLD)
                            self.stdscr.refresh()
                            time.sleep(2)
                            return None
                    return password
            elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:  # Backspace
                if password:
                    password = password[:-1]
            elif 32 <= key <= 126:  # Printable characters
                password += chr(key)
            
            self.animation_frame += 1


def prompt_password_curses(prompt: str = "Enter your FadCrypt password",
                           confirm: bool = False) -> Optional[str]:
    """
    Show curses password prompt with animation
    
    Args:
        prompt: Prompt text to display
        confirm: If True, ask for confirmation
        
    Returns:
        Password string or None if cancelled
    """
    def _password_wrapper(stdscr):
        password_input = AnimatedPasswordInput(stdscr)
        return password_input.prompt_password(prompt, confirm)
    
    try:
        return curses.wrapper(_password_wrapper)
    except Exception:
        return None


def has_curses_support() -> bool:
    """Check if curses is available"""
    try:
        import curses
        return True
    except ImportError:
        return False
