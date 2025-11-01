"""
Terminal animations for FadCrypt TUI
Simple frame-based animation that updates on menu redraw
"""

import random


class ANSI:
    """ANSI escape codes for terminal control"""
    
    @staticmethod
    def color(r, g, b):
        return f'\033[38;2;{r};{g};{b}m'
    
    RESET = '\033[0m'
    BRIGHT_RED = '\033[1m\033[91m'
    BRIGHT_WHITE = '\033[1m\033[97m'


class HeaderAnimation:
    """Simple frame-based animation"""
    
    def __init__(self):
        self.frame = 0
    
    def get_frame(self):
        """Get current animation frame as printable lines"""
        text = "F A D C R Y P T"
        hex_chars = "0123456789ABCDEF"
        width = 60
        
        lines = []
        
        # Top row: Hex background
        line = ""
        for _ in range(0, width, 3):
            hex_byte = random.choice(hex_chars) + random.choice(hex_chars)
            if random.random() > 0.7:
                line += f"{ANSI.color(255, 0, 0)}{hex_byte}{ANSI.RESET} "
            else:
                line += f"{ANSI.color(100, 0, 0)}{hex_byte}{ANSI.RESET} "
        lines.append(line)
        
        # Middle row: FadCrypt text
        padding = (60 - len(text)) // 2
        if self.frame % 4 < 2:
            text_line = " " * padding + f"{ANSI.BRIGHT_WHITE}{text}{ANSI.RESET}"
        else:
            text_line = " " * padding + f"{ANSI.BRIGHT_RED}{text}{ANSI.RESET}"
        lines.append(text_line)
        
        # Bottom row: Hex background
        line = ""
        for _ in range(0, width, 3):
            hex_byte = random.choice(hex_chars) + random.choice(hex_chars)
            if random.random() > 0.7:
                line += f"{ANSI.color(255, 0, 0)}{hex_byte}{ANSI.RESET} "
            else:
                line += f"{ANSI.color(100, 0, 0)}{hex_byte}{ANSI.RESET} "
        lines.append(line)
        
        self.frame += 1
        return lines


# Global animation instance
_animation = HeaderAnimation()


def start_header_animation():
    """Initialize animation (no-op for compatibility)"""
    pass


def stop_header_animation():
    """Stop animation (no-op for compatibility)"""
    pass


def get_animation_frame():
    """Get current animation frame"""
    return _animation.get_frame()
