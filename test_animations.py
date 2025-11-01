"""
Test different animation styles for FadCrypt
Press Ctrl+C to stop any animation and move to the next one
"""

import os
import sys
import time
import random

# ANSI escape codes
class ANSI:
    CLEAR = '\033[2J'
    HOME = '\033[H'
    HIDE_CURSOR = '\033[?25l'
    SHOW_CURSOR = '\033[?25h'
    SAVE_POS = '\033[s'
    RESTORE_POS = '\033[u'
    
    @staticmethod
    def move_to(row, col):
        return f'\033[{row};{col}H'
    
    @staticmethod
    def color(r, g, b):
        return f'\033[38;2;{r};{g};{b}m'
    
    RESET = '\033[0m'
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    DIM = '\033[2m'
    BRIGHT = '\033[1m'


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


# ============================================================================
# Animation 1: Matrix Rain (Classic)
# ============================================================================
def matrix_rain_animation():
    """Classic Matrix falling characters"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 1: Matrix Rain (Classic)")
    print("="*60 + "\n")
    
    width = 60
    height = 5
    columns = [random.randint(0, height) for _ in range(width)]
    
    chars = "01アイウエオカキクケコサシスセソタチツテト"
    
    try:
        for frame in range(100):
            for i in range(width):
                if random.random() > 0.95:
                    columns[i] = 0
                
                if columns[i] < height:
                    char = random.choice(chars)
                    row = 5 + columns[i]
                    col = i + 1
                    
                    if columns[i] == 0:
                        print(f"{ANSI.move_to(row, col)}{ANSI.BRIGHT}{ANSI.GREEN}{char}{ANSI.RESET}", end='')
                    else:
                        intensity = 255 - (columns[i] * 50)
                        print(f"{ANSI.move_to(row, col)}{ANSI.color(0, max(100, intensity), 0)}{char}{ANSI.RESET}", end='')
                    
                    columns[i] += 1
            
            sys.stdout.flush()
            time.sleep(0.05)
        
        print(ANSI.SHOW_CURSOR)
        input("\n\nPress Enter to continue...")
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)


# ============================================================================
# Animation 2: Binary Stream
# ============================================================================
def binary_stream_animation():
    """Flowing binary numbers"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 2: Binary Stream")
    print("="*60 + "\n")
    
    width = 60
    height = 5
    
    try:
        for frame in range(100):
            for row in range(height):
                line = ""
                for col in range(width):
                    if random.random() > 0.5:
                        bit = random.choice(['0', '1'])
                        if bit == '1':
                            line += f"{ANSI.CYAN}{bit}{ANSI.RESET}"
                        else:
                            line += f"{ANSI.DIM}{bit}{ANSI.RESET}"
                    else:
                        line += " "
                
                print(f"{ANSI.move_to(5 + row, 1)}{line}", end='')
            
            sys.stdout.flush()
            time.sleep(0.1)
        
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\n\nPress Enter to continue...")
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)


# ============================================================================
# Animation 3: Hex Scanner
# ============================================================================
def hex_scanner_animation():
    """Scanning hex values like a hacker terminal"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 3: Hex Scanner")
    print("="*60 + "\n")
    
    hex_chars = "0123456789ABCDEF"
    width = 60
    height = 5
    
    try:
        for frame in range(100):
            for row in range(height):
                line = ""
                for col in range(0, width, 3):
                    hex_byte = random.choice(hex_chars) + random.choice(hex_chars)
                    if random.random() > 0.7:
                        line += f"{ANSI.GREEN}{hex_byte}{ANSI.RESET} "
                    else:
                        line += f"{ANSI.DIM}{hex_byte}{ANSI.RESET} "
                
                print(f"{ANSI.move_to(5 + row, 1)}{line}", end='')
            
            sys.stdout.flush()
            time.sleep(0.15)
        
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\n\nPress Enter to continue...")
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)


# ============================================================================
# Animation 4: Glitch Effect
# ============================================================================
def glitch_animation():
    """Glitchy text effect"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 4: Glitch Effect")
    print("="*60 + "\n")
    
    text = ">>> FADCRYPT SECURE ENCRYPTION SYSTEM <<<"
    glitch_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
    
    try:
        for frame in range(100):
            glitched = ""
            for char in text:
                if random.random() > 0.9:
                    glitched += f"{ANSI.GREEN}{random.choice(glitch_chars)}{ANSI.RESET}"
                elif random.random() > 0.95:
                    glitched += f"{ANSI.CYAN}{char}{ANSI.RESET}"
                else:
                    glitched += char
            
            padding = (60 - len(text)) // 2
            print(f"{ANSI.move_to(7, padding)}{glitched}", end='')
            
            sys.stdout.flush()
            time.sleep(0.1)
        
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)


# ============================================================================
# Animation 5: Minimal Pulse (Subtle)
# ============================================================================
def pulse_animation():
    """Subtle pulsing effect - minimal distraction"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 5: Minimal Pulse (Subtle)")
    print("="*60 + "\n")
    
    symbols = ["◆", "◇", "◈", "◉", "◊"]
    
    try:
        for frame in range(100):
            symbol = symbols[frame % len(symbols)]
            
            line = ""
            for i in range(60):
                if i % 10 == (frame % 10):
                    line += f"{ANSI.GREEN}{symbol}{ANSI.RESET}"
                else:
                    line += f"{ANSI.DIM}·{ANSI.RESET}"
            
            print(f"{ANSI.move_to(7, 1)}{line}", end='')
            
            sys.stdout.flush()
            time.sleep(0.2)
        
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)


# ============================================================================
# Animation 6: Static with UI (Demo of how it would work)
# ============================================================================
def static_ui_with_animation():
    """Demo: Animation at top with static UI below"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    
    ui_start_row = 8
    ui = [
        "╭─ 🏴 FadCrypt v2.0.0",
        "│ File, Folder & Application Protection Suite",
        "╰──────────────────────────────────────────────────────────────",
        "",
        "╭─ MAIN MENU",
        "│",
        "│❯  1. 🔒 Lock Files/Folders",
        "│   2. 🔓 Unlock Files/Folders",
        "│   3. 📋 List Locked Items",
        "│   4. 💻 Open GUI Application",
        "│   5. 🔧 Settings",
        "│   6. ❌ Exit",
        "│",
        "╰──────────────────────────────────────────────────────────────",
    ]
    
    for i, line in enumerate(ui):
        print(f"{ANSI.move_to(ui_start_row + i, 1)}{line}")
    
    print("\n" + "="*60)
    print("ANIMATION 6: Live Demo - Animation + Static UI")
    print("Notice how the animation runs at top without affecting UI below")
    print("="*60)
    
    width = 60
    height = 3
    columns = [random.randint(0, height) for _ in range(width)]
    chars = "01"
    
    try:
        for frame in range(150):
            for i in range(width):
                if random.random() > 0.95:
                    columns[i] = 0
                
                if columns[i] < height:
                    char = random.choice(chars)
                    row = 2 + columns[i]
                    col = i + 1
                    
                    if columns[i] == 0:
                        print(f"{ANSI.move_to(row, col)}{ANSI.BRIGHT}{ANSI.GREEN}{char}{ANSI.RESET}", end='')
                    else:
                        print(f"{ANSI.move_to(row, col)}{ANSI.DIM}{char}{ANSI.RESET}", end='')
                    
                    columns[i] += 1
            
            sys.stdout.flush()
            time.sleep(0.05)
        
        print(ANSI.SHOW_CURSOR)
        print(f"{ANSI.move_to(25, 1)}")
        input("\nPress Enter to finish...")
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)



# ============================================================================
# Animation 7: FadCrypt Typewriter with Hex Background
# ============================================================================
def fadcrypt_typewriter_hex():
    """FadCrypt text appears with hex background"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 7: FadCrypt Typewriter + Hex Background")
    print("="*60 + "\n")
    
    text = "F A D C R Y P T"
    hex_chars = "0123456789ABCDEF"
    width = 60
    
    try:
        # Phase 1: Hex background builds up
        for frame in range(30):
            for row in range(3):
                line = ""
                for col in range(0, width, 3):
                    if random.random() < frame / 30:
                        hex_byte = random.choice(hex_chars) + random.choice(hex_chars)
                        line += f"{ANSI.DIM}{hex_byte}{ANSI.RESET} "
                    else:
                        line += "   "
                print(f"{ANSI.move_to(5 + row, 1)}{line}", end='')
            sys.stdout.flush()
            time.sleep(0.05)
        
        # Phase 2: FadCrypt text types in
        for i in range(len(text) + 1):
            current_text = text[:i]
            padding = (60 - len(text)) // 2
            
            for row in [5, 7]:
                line = ""
                for col in range(0, width, 3):
                    hex_byte = random.choice(hex_chars) + random.choice(hex_chars)
                    line += f"{ANSI.DIM}{hex_byte}{ANSI.RESET} "
                print(f"{ANSI.move_to(row, 1)}{line}", end='')
            
            print(f"{ANSI.move_to(6, padding)}{ANSI.BRIGHT}{ANSI.GREEN}{current_text}{ANSI.RESET}", end='')
            sys.stdout.flush()
            time.sleep(0.15)
        
        # Phase 3: Hold and flicker
        for frame in range(30):
            padding = (60 - len(text)) // 2
            
            for row in [5, 7]:
                line = ""
                for col in range(0, width, 3):
                    hex_byte = random.choice(hex_chars) + random.choice(hex_chars)
                    if random.random() > 0.7:
                        line += f"{ANSI.GREEN}{hex_byte}{ANSI.RESET} "
                    else:
                        line += f"{ANSI.DIM}{hex_byte}{ANSI.RESET} "
                print(f"{ANSI.move_to(row, 1)}{line}", end='')
            
            if frame % 2 == 0:
                print(f"{ANSI.move_to(6, padding)}{ANSI.BRIGHT}{ANSI.GREEN}{text}{ANSI.RESET}", end='')
            else:
                print(f"{ANSI.move_to(6, padding)}{ANSI.GREEN}{text}{ANSI.RESET}", end='')
            
            sys.stdout.flush()
            time.sleep(0.1)
        
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)


# ============================================================================
# Animation 8: FadCrypt Binary Reveal
# ============================================================================
def fadcrypt_binary_reveal():
    """FadCrypt text reveals from binary noise"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 8: FadCrypt Binary Reveal")
    print("="*60 + "\n")
    
    text = ">>> FADCRYPT <<<"
    width = 60
    
    try:
        # Phase 1: Binary noise
        for frame in range(40):
            padding = (60 - len(text)) // 2
            line = ""
            
            for i, char in enumerate(text):
                if random.random() < frame / 40:
                    if char == ' ':
                        line += ' '
                    else:
                        line += f"{ANSI.BRIGHT}{ANSI.GREEN}{char}{ANSI.RESET}"
                else:
                    line += f"{ANSI.CYAN}{random.choice('01')}{ANSI.RESET}"
            
            print(f"{ANSI.move_to(6, padding)}{line}", end='')
            
            for row in [5, 7]:
                bg_line = ""
                for col in range(width):
                    if random.random() > 0.5:
                        bg_line += f"{ANSI.DIM}{random.choice('01')}{ANSI.RESET}"
                    else:
                        bg_line += " "
                print(f"{ANSI.move_to(row, 1)}{bg_line}", end='')
            
            sys.stdout.flush()
            time.sleep(0.08)
        
        # Phase 2: Hold with subtle binary background
        for frame in range(30):
            padding = (60 - len(text)) // 2
            print(f"{ANSI.move_to(6, padding)}{ANSI.BRIGHT}{ANSI.GREEN}{text}{ANSI.RESET}", end='')
            
            for row in [5, 7]:
                bg_line = ""
                for col in range(width):
                    if random.random() > 0.8:
                        bg_line += f"{ANSI.DIM}{random.choice('01')}{ANSI.RESET}"
                    else:
                        bg_line += " "
                print(f"{ANSI.move_to(row, 1)}{bg_line}", end='')
            
            sys.stdout.flush()
            time.sleep(0.1)
        
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)


# ============================================================================
# Animation 9: FadCrypt Glitch Materialize
# ============================================================================
def fadcrypt_glitch_materialize():
    """FadCrypt materializes from glitchy chaos"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 9: FadCrypt Glitch Materialize")
    print("="*60 + "\n")
    
    text = "[ F A D C R Y P T ]"
    glitch_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
    
    try:
        # Phase 1: Chaos
        for frame in range(30):
            padding = (60 - len(text)) // 2
            line = ""
            
            for char in text:
                if char == ' ':
                    line += ' '
                else:
                    line += f"{ANSI.GREEN}{random.choice(glitch_chars)}{ANSI.RESET}"
            
            print(f"{ANSI.move_to(6, padding)}{line}", end='')
            sys.stdout.flush()
            time.sleep(0.05)
        
        # Phase 2: Gradual stabilization
        for frame in range(50):
            padding = (60 - len(text)) // 2
            line = ""
            
            for i, char in enumerate(text):
                if char == ' ':
                    line += ' '
                elif random.random() < (frame / 50) * 0.9:
                    line += f"{ANSI.BRIGHT}{ANSI.GREEN}{char}{ANSI.RESET}"
                else:
                    line += f"{ANSI.CYAN}{random.choice(glitch_chars)}{ANSI.RESET}"
            
            print(f"{ANSI.move_to(6, padding)}{line}", end='')
            sys.stdout.flush()
            time.sleep(0.06)
        
        # Phase 3: Stable with occasional glitch
        for frame in range(40):
            padding = (60 - len(text)) // 2
            line = ""
            
            for char in text:
                if char == ' ':
                    line += ' '
                elif random.random() > 0.95:
                    line += f"{ANSI.CYAN}{random.choice(glitch_chars)}{ANSI.RESET}"
                else:
                    line += f"{ANSI.BRIGHT}{ANSI.GREEN}{char}{ANSI.RESET}"
            
            print(f"{ANSI.move_to(6, padding)}{line}", end='')
            sys.stdout.flush()
            time.sleep(0.1)
        
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)


# ============================================================================
# Animation 10: Password Input Pulse (Subtle)
# ============================================================================
def password_pulse_animation():
    """Subtle pulse for password input - non-distracting"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 10: Password Input Pulse")
    print("Perfect for password prompts - subtle and calming")
    print("="*60 + "\n")
    
    symbols = ["●", "◉", "○", "◌"]
    
    try:
        for frame in range(100):
            symbol = symbols[frame % len(symbols)]
            
            line = ""
            for i in range(40):
                if i == 20:
                    line += f"{ANSI.GREEN}{symbol}{ANSI.RESET}"
                elif abs(i - 20) < 3:
                    line += f"{ANSI.color(0, 200, 0)}·{ANSI.RESET}"
                else:
                    line += f"{ANSI.DIM}·{ANSI.RESET}"
            
            print(f"{ANSI.move_to(6, 10)}{line}", end='')
            
            print(f"{ANSI.move_to(8, 10)}{ANSI.GREEN}🔒 Enter Password:{ANSI.RESET} ", end='')
            print(f"{ANSI.move_to(9, 10)}{ANSI.DIM}{'_' * 30}{ANSI.RESET}", end='')
            
            sys.stdout.flush()
            time.sleep(0.15)
        
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)


# ============================================================================
# Animation 11: Breathing Brackets (Input Indicator)
# ============================================================================
def breathing_brackets_animation():
    """Breathing brackets around input - shows activity"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 11: Breathing Brackets")
    print("Great for any input field - shows system is ready")
    print("="*60 + "\n")
    
    try:
        for frame in range(100):
            breath = abs((frame % 20) - 10) / 10
            spacing = int(30 + breath * 4)
            intensity = int(150 + breath * 105)
            
            left_bracket = f"{ANSI.color(0, intensity, 0)}[{ANSI.RESET}"
            right_bracket = f"{ANSI.color(0, intensity, 0)}]{ANSI.RESET}"
            
            prompt_text = "Enter your choice"
            total_width = len(prompt_text) + spacing
            left_padding = (60 - total_width) // 2
            
            line = " " * left_padding + left_bracket + " " * (spacing // 2) + prompt_text + " " * (spacing // 2) + right_bracket
            
            print(f"{ANSI.move_to(8, 1)}{line}", end='')
            
            cursor = "▌" if frame % 2 == 0 else " "
            print(f"{ANSI.move_to(10, 30)}{ANSI.GREEN}{cursor}{ANSI.RESET}", end='')
            
            sys.stdout.flush()
            time.sleep(0.1)
        
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)


# ============================================================================
# Animation 12: Scanning Line (Loading/Processing)
# ============================================================================
def scanning_line_animation():
    """Scanning line effect - perfect for loading/processing"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 12: Scanning Line")
    print("Perfect for 'Processing...', 'Encrypting...', etc.")
    print("="*60 + "\n")
    
    width = 50
    
    try:
        for frame in range(100):
            pos = frame % width
            
            line = ""
            for i in range(width):
                if i == pos:
                    line += f"{ANSI.BRIGHT}{ANSI.GREEN}█{ANSI.RESET}"
                elif abs(i - pos) < 3:
                    line += f"{ANSI.GREEN}▓{ANSI.RESET}"
                elif abs(i - pos) < 5:
                    line += f"{ANSI.color(0, 150, 0)}▒{ANSI.RESET}"
                else:
                    line += f"{ANSI.DIM}░{ANSI.RESET}"
            
            print(f"{ANSI.move_to(7, 5)}{line}", end='')
            print(f"{ANSI.move_to(9, 5)}{ANSI.GREEN}Processing encryption...{ANSI.RESET}", end='')
            
            sys.stdout.flush()
            time.sleep(0.05)
        
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)


# ============================================================================
# Animation 13: Wave Pulse (Elegant)
# ============================================================================
def wave_pulse_animation():
    """Elegant wave pulse - sophisticated look"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 13: Wave Pulse")
    print("Elegant and sophisticated - good for main menu")
    print("="*60 + "\n")
    
    width = 60
    
    try:
        for frame in range(100):
            line = ""
            
            for i in range(width):
                wave = abs(((i + frame) % 20) - 10) / 10
                
                if wave > 0.7:
                    line += f"{ANSI.BRIGHT}{ANSI.GREEN}●{ANSI.RESET}"
                elif wave > 0.4:
                    line += f"{ANSI.GREEN}○{ANSI.RESET}"
                else:
                    line += f"{ANSI.DIM}·{ANSI.RESET}"
            
            print(f"{ANSI.move_to(6, 1)}{line}", end='')
            
            sys.stdout.flush()
            time.sleep(0.08)
        
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)


# ============================================================================
# Animation 14: Corner Brackets (Framing Effect)
# ============================================================================
def corner_brackets_animation():
    """Animated corner brackets - frames content nicely"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 14: Corner Brackets")
    print("Frames your content with animated corners")
    print("="*60 + "\n")
    
    corners = [
        ("╔", "╗", "╚", "╝"),
        ("┏", "┓", "┗", "┛"),
        ("┌", "┐", "└", "┘"),
        ("╭", "╮", "╰", "╯"),
    ]
    
    try:
        for frame in range(100):
            corner_set = corners[frame % len(corners)]
            tl, tr, bl, br = corner_set
            
            if frame % 4 < 2:
                color = ANSI.BRIGHT + ANSI.GREEN
            else:
                color = ANSI.GREEN
            
            print(f"{ANSI.move_to(6, 15)}{color}{tl}{ANSI.RESET}", end='')
            print(f"{ANSI.move_to(6, 45)}{color}{tr}{ANSI.RESET}", end='')
            print(f"{ANSI.move_to(10, 15)}{color}{bl}{ANSI.RESET}", end='')
            print(f"{ANSI.move_to(10, 45)}{color}{br}{ANSI.RESET}", end='')
            
            print(f"{ANSI.move_to(8, 20)}{ANSI.GREEN}FADCRYPT READY{ANSI.RESET}", end='')
            
            sys.stdout.flush()
            time.sleep(0.2)
        
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)


# ============================================================================
# Animation 15: FadCrypt Hex RED (Continuous Loop)
# ============================================================================
def fadcrypt_hex_red_loop():
    """FadCrypt with RED hex background - continuous loop"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 15: FadCrypt Hex RED (Continuous)")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    text = "F A D C R Y P T"
    hex_chars = "0123456789ABCDEF"
    width = 60
    
    try:
        frame = 0
        while True:
            for row in [5, 7]:
                line = ""
                for col in range(0, width, 3):
                    hex_byte = random.choice(hex_chars) + random.choice(hex_chars)
                    if random.random() > 0.7:
                        line += f"\033[38;2;255;0;0m{hex_byte}\033[0m "
                    else:
                        line += f"\033[38;2;100;0;0m{hex_byte}\033[0m "
                print(f"{ANSI.move_to(row, 1)}{line}", end='')
            
            padding = (60 - len(text)) // 2
            if frame % 4 < 2:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[97m{text}\033[0m", end='')
            else:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[91m{text}\033[0m", end='')
            
            sys.stdout.flush()
            time.sleep(0.15)
            frame += 1
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")


def fadcrypt_binary_matrix_red():
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 16: FadCrypt Binary Matrix RED")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    text = ">>> FADCRYPT <<<"
    width = 60
    height = 3
    columns = [random.randint(0, height) for _ in range(width)]
    
    try:
        frame = 0
        while True:
            for i in range(width):
                if random.random() > 0.95:
                    columns[i] = 0
                
                if columns[i] < height:
                    bit = random.choice('01')
                    row = 5 + columns[i]
                    col = i + 1
                    
                    if columns[i] == 0:
                        print(f"{ANSI.move_to(row, col)}\033[1m\033[91m{bit}\033[0m", end='')
                    else:
                        intensity = 200 - (columns[i] * 60)
                        print(f"{ANSI.move_to(row, col)}\033[38;2;{max(50, intensity)};0;0m{bit}\033[0m", end='')
                    
                    columns[i] += 1
            
            padding = (60 - len(text)) // 2
            if frame % 3 == 0:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[97m{text}\033[0m", end='')
            else:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[91m{text}\033[0m", end='')
            
            sys.stdout.flush()
            time.sleep(0.08)
            frame += 1
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")


def fadcrypt_binary_wave():
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 17: FadCrypt Binary Wave")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    text = "[ FADCRYPT ]"
    width = 60
    
    try:
        frame = 0
        while True:
            for row in [5, 7]:
                line = ""
                for i in range(width):
                    wave_pos = (i + frame) % 20
                    if wave_pos < 10:
                        intensity = wave_pos * 25
                    else:
                        intensity = (20 - wave_pos) * 25
                    
                    bit = random.choice('01')
                    if intensity > 150:
                        line += f"\033[38;2;255;{intensity};0m{bit}\033[0m"
                    else:
                        line += f"\033[38;2;{intensity};0;0m{bit}\033[0m"
                
                print(f"{ANSI.move_to(row, 1)}{line}", end='')
            
            padding = (60 - len(text)) // 2
            if frame % 2 == 0:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[97m{text}\033[0m", end='')
            else:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[91m{text}\033[0m", end='')
            
            sys.stdout.flush()
            time.sleep(0.1)
            frame += 1
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")


def fadcrypt_binary_pulse():
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 18: FadCrypt Binary Pulse")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    text = "F A D C R Y P T"
    width = 60
    
    try:
        frame = 0
        while True:
            pulse = abs((frame % 20) - 10) / 10
            
            for row in [5, 7]:
                line = ""
                for i in range(width):
                    if random.random() > 0.5:
                        bit = random.choice('01')
                        intensity = int(50 + pulse * 200)
                        line += f"\033[38;2;{intensity};0;0m{bit}\033[0m"
                    else:
                        line += " "
                
                print(f"{ANSI.move_to(row, 1)}{line}", end='')
            
            padding = (60 - len(text)) // 2
            text_intensity = int(200 + pulse * 55)
            print(f"{ANSI.move_to(6, padding)}\033[1m\033[38;2;{text_intensity};{text_intensity};{text_intensity}m{text}\033[0m", end='')
            
            sys.stdout.flush()
            time.sleep(0.1)
            frame += 1
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")


def fadcrypt_binary_scan():
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 19: FadCrypt Binary Scan")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    text = ">>> FADCRYPT <<<"
    width = 60
    
    try:
        frame = 0
        while True:
            scan_pos = frame % width
            
            for row in [5, 7]:
                line = ""
                for i in range(width):
                    bit = random.choice('01')
                    
                    if abs(i - scan_pos) < 3:
                        line += f"\033[1m\033[91m{bit}\033[0m"
                    elif abs(i - scan_pos) < 6:
                        line += f"\033[38;2;200;0;0m{bit}\033[0m"
                    else:
                        line += f"\033[38;2;80;0;0m{bit}\033[0m"
                
                print(f"{ANSI.move_to(row, 1)}{line}", end='')
            
            padding = (60 - len(text)) // 2
            if frame % 2 == 0:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[97m{text}\033[0m", end='')
            else:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[91m{text}\033[0m", end='')
            
            sys.stdout.flush()
            time.sleep(0.05)
            frame += 1
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")


def fadcrypt_hex_binary_mix_red():
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 20: FadCrypt Hex + Binary Mix RED")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    text = "[ F A D C R Y P T ]"
    hex_chars = "0123456789ABCDEF"
    width = 60
    
    try:
        frame = 0
        while True:
            line_hex = ""
            for col in range(0, width, 3):
                hex_byte = random.choice(hex_chars) + random.choice(hex_chars)
                if random.random() > 0.7:
                    line_hex += f"\033[38;2;255;0;0m{hex_byte}\033[0m "
                else:
                    line_hex += f"\033[38;2;100;0;0m{hex_byte}\033[0m "
            print(f"{ANSI.move_to(5, 1)}{line_hex}", end='')
            
            line_bin = ""
            for i in range(width):
                bit = random.choice('01')
                if random.random() > 0.6:
                    line_bin += f"\033[38;2;255;0;0m{bit}\033[0m"
                else:
                    line_bin += f"\033[38;2;80;0;0m{bit}\033[0m"
            print(f"{ANSI.move_to(7, 1)}{line_bin}", end='')
            
            padding = (60 - len(text)) // 2
            if frame % 3 == 0:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[97m{text}\033[0m", end='')
            elif frame % 3 == 1:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[91m{text}\033[0m", end='')
            else:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[38;2;255;100;0m{text}\033[0m", end='')
            
            sys.stdout.flush()
            time.sleep(0.12)
            frame += 1
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")


def fadcrypt_binary_glitch_red():
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 21: FadCrypt Binary Glitch RED")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    text = "FADCRYPT"
    width = 60
    
    try:
        frame = 0
        while True:
            for row in [5, 7]:
                line = ""
                for i in range(width):
                    if random.random() > 0.3:
                        bit = random.choice('01')
                        if random.random() > 0.9:
                            line += f"\033[1m\033[91m{bit}\033[0m"
                        elif random.random() > 0.7:
                            line += f"\033[38;2;255;0;0m{bit}\033[0m"
                        else:
                            line += f"\033[38;2;{random.randint(50, 150)};0;0m{bit}\033[0m"
                    else:
                        line += " "
                
                print(f"{ANSI.move_to(row, 1)}{line}", end='')
            
            padding = (60 - len(text)) // 2
            glitched_text = ""
            for char in text:
                if random.random() > 0.95:
                    glitched_text += f"\033[1m\033[91m{random.choice('01')}\033[0m"
                elif random.random() > 0.9:
                    glitched_text += f"\033[38;2;255;50;50m{char}\033[0m"
                else:
                    glitched_text += f"\033[1m\033[97m{char}\033[0m"
            
            print(f"{ANSI.move_to(6, padding)}{glitched_text}", end='')
            
            sys.stdout.flush()
            time.sleep(0.08)
            frame += 1
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")


# ============================================================================
# Main Menu
# ============================================================================
def main():
    animations = [
        ("Matrix Rain (Classic)", matrix_rain_animation),
        ("Binary Stream", binary_stream_animation),
        ("Hex Scanner", hex_scanner_animation),
        ("Glitch Effect", glitch_animation),
        ("Minimal Pulse (Subtle)", pulse_animation),
        ("Live Demo: Animation + UI", static_ui_with_animation),
        ("", None),
        ("=== FADCRYPT TEXT ANIMATIONS ===", None),
        ("FadCrypt Typewriter + Hex", fadcrypt_typewriter_hex),
        ("FadCrypt Binary Reveal", fadcrypt_binary_reveal),
        ("FadCrypt Glitch Materialize", fadcrypt_glitch_materialize),
        ("", None),
        ("=== RED CONTINUOUS ANIMATIONS ===", None),
        ("FadCrypt Hex RED (Continuous)", fadcrypt_hex_red_loop),
        ("FadCrypt Binary Matrix RED", fadcrypt_binary_matrix_red),
        ("FadCrypt Binary Wave", fadcrypt_binary_wave),
        ("FadCrypt Binary Pulse", fadcrypt_binary_pulse),
        ("FadCrypt Binary Scan", fadcrypt_binary_scan),
        ("FadCrypt Hex+Binary Mix RED", fadcrypt_hex_binary_mix_red),
        ("FadCrypt Binary Glitch RED", fadcrypt_binary_glitch_red),
        ("", None),
        ("=== INPUT/PROMPT ANIMATIONS ===", None),
        ("Password Input Pulse", password_pulse_animation),
        ("Breathing Brackets", breathing_brackets_animation),
        ("Scanning Line (Processing)", scanning_line_animation),
        ("Wave Pulse (Elegant)", wave_pulse_animation),
        ("Corner Brackets (Framing)", corner_brackets_animation),
    ]
    
    while True:
        clear_screen()
        print("\n" + "="*60)
        print("FadCrypt Animation Test Suite")
        print("="*60 + "\n")
        
        menu_num = 1
        for name, func in animations:
            if name == "":
                print()
            elif func is None:
                print(f"\n{name}")
            else:
                print(f"  {menu_num}. {name}")
                menu_num += 1
        
        print(f"\n  {menu_num}. Exit")
        print("\n" + "="*60)
        
        try:
            choice = input("\nSelect animation to test (or 'q' to quit): ").strip()
            
            actual_animations = [(name, func) for name, func in animations if func is not None]
            
            if choice.lower() == 'q' or choice == str(len(actual_animations) + 1):
                print("\nExiting...")
                break
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(actual_animations):
                actual_animations[choice_num - 1][1]()
            else:
                print("Invalid choice!")
                time.sleep(1)
                
        except ValueError:
            print("Invalid input!")
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
    
    print(ANSI.SHOW_CURSOR)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)
        print("\n\nExiting...")



# ============================================================================
# Animation 15: FadCrypt Hex RED (Continuous Loop)
# ============================================================================
def fadcrypt_hex_red_loop():
    """FadCrypt with RED hex background - continuous loop"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 15: FadCrypt Hex RED (Continuous)")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    text = "F A D C R Y P T"
    hex_chars = "0123456789ABCDEF"
    width = 60
    
    try:
        frame = 0
        while True:  # Continuous loop
            # Flickering hex background in RED
            for row in [5, 7]:
                line = ""
                for col in range(0, width, 3):
                    hex_byte = random.choice(hex_chars) + random.choice(hex_chars)
                    if random.random() > 0.7:
                        # Bright red
                        line += f"\033[38;2;255;0;0m{hex_byte}\033[0m "
                    else:
                        # Dim red
                        line += f"\033[38;2;100;0;0m{hex_byte}\033[0m "
                print(f"{ANSI.move_to(row, 1)}{line}", end='')
            
            # Pulsing FadCrypt text in bright red/white
            padding = (60 - len(text)) // 2
            if frame % 4 < 2:
                # Bright white
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[97m{text}\033[0m", end='')
            else:
                # Bright red
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[91m{text}\033[0m", end='')
            
            sys.stdout.flush()
            time.sleep(0.15)
            frame += 1
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")


# ============================================================================
# Animation 16: FadCrypt Binary Matrix RED (Continuous)
# ============================================================================
def fadcrypt_binary_matrix_red():
    """FadCrypt with falling binary in RED - Matrix style"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 16: FadCrypt Binary Matrix RED")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    text = ">>> FADCRYPT <<<"
    width = 60
    height = 3
    columns = [random.randint(0, height) for _ in range(width)]
    
    try:
        frame = 0
        while True:
            # Update falling binary
            for i in range(width):
                if random.random() > 0.95:
                    columns[i] = 0
                
                if columns[i] < height:
                    bit = random.choice('01')
                    row = 5 + columns[i]
                    col = i + 1
                    
                    if columns[i] == 0:
                        # Bright red for head
                        print(f"{ANSI.move_to(row, col)}\033[1m\033[91m{bit}\033[0m", end='')
                    else:
                        # Dim red for trail
                        intensity = 200 - (columns[i] * 60)
                        print(f"{ANSI.move_to(row, col)}\033[38;2;{max(50, intensity)};0;0m{bit}\033[0m", end='')
                    
                    columns[i] += 1
            
            # FadCrypt text in center - alternating bright
            padding = (60 - len(text)) // 2
            if frame % 3 == 0:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[97m{text}\033[0m", end='')
            else:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[91m{text}\033[0m", end='')
            
            sys.stdout.flush()
            time.sleep(0.08)
            frame += 1
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")


# ============================================================================
# Animation 17: FadCrypt Binary Wave (Continuous)
# ============================================================================
def fadcrypt_binary_wave():
    """FadCrypt with binary wave effect - continuous"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 17: FadCrypt Binary Wave")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    text = "[ FADCRYPT ]"
    width = 60
    
    try:
        frame = 0
        while True:
            # Binary wave above and below
            for row in [5, 7]:
                line = ""
                for i in range(width):
                    # Create wave pattern
                    wave_pos = (i + frame) % 20
                    if wave_pos < 10:
                        intensity = wave_pos * 25
                    else:
                        intensity = (20 - wave_pos) * 25
                    
                    bit = random.choice('01')
                    if intensity > 150:
                        line += f"\033[38;2;255;{intensity};0m{bit}\033[0m"
                    else:
                        line += f"\033[38;2;{intensity};0;0m{bit}\033[0m"
                
                print(f"{ANSI.move_to(row, 1)}{line}", end='')
            
            # FadCrypt text
            padding = (60 - len(text)) // 2
            if frame % 2 == 0:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[97m{text}\033[0m", end='')
            else:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[91m{text}\033[0m", end='')
            
            sys.stdout.flush()
            time.sleep(0.1)
            frame += 1
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")


# ============================================================================
# Animation 18: FadCrypt Binary Pulse (Continuous)
# ============================================================================
def fadcrypt_binary_pulse():
    """FadCrypt with pulsing binary background"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 18: FadCrypt Binary Pulse")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    text = "F A D C R Y P T"
    width = 60
    
    try:
        frame = 0
        while True:
            # Pulsing binary background
            pulse = abs((frame % 20) - 10) / 10  # 0 to 1 and back
            
            for row in [5, 7]:
                line = ""
                for i in range(width):
                    if random.random() > 0.5:
                        bit = random.choice('01')
                        # Red intensity based on pulse
                        intensity = int(50 + pulse * 200)
                        line += f"\033[38;2;{intensity};0;0m{bit}\033[0m"
                    else:
                        line += " "
                
                print(f"{ANSI.move_to(row, 1)}{line}", end='')
            
            # FadCrypt text with pulse
            padding = (60 - len(text)) // 2
            text_intensity = int(200 + pulse * 55)
            print(f"{ANSI.move_to(6, padding)}\033[1m\033[38;2;{text_intensity};{text_intensity};{text_intensity}m{text}\033[0m", end='')
            
            sys.stdout.flush()
            time.sleep(0.1)
            frame += 1
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")


# ============================================================================
# Animation 19: FadCrypt Binary Scan (Continuous)
# ============================================================================
def fadcrypt_binary_scan():
    """FadCrypt with scanning binary lines"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 19: FadCrypt Binary Scan")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    text = ">>> FADCRYPT <<<"
    width = 60
    
    try:
        frame = 0
        while True:
            scan_pos = frame % width
            
            # Binary background with scan line
            for row in [5, 7]:
                line = ""
                for i in range(width):
                    bit = random.choice('01')
                    
                    # Scan line effect
                    if abs(i - scan_pos) < 3:
                        # Bright red scan line
                        line += f"\033[1m\033[91m{bit}\033[0m"
                    elif abs(i - scan_pos) < 6:
                        # Medium red
                        line += f"\033[38;2;200;0;0m{bit}\033[0m"
                    else:
                        # Dim red
                        line += f"\033[38;2;80;0;0m{bit}\033[0m"
                
                print(f"{ANSI.move_to(row, 1)}{line}", end='')
            
            # FadCrypt text
            padding = (60 - len(text)) // 2
            if frame % 2 == 0:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[97m{text}\033[0m", end='')
            else:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[91m{text}\033[0m", end='')
            
            sys.stdout.flush()
            time.sleep(0.05)
            frame += 1
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")


# ============================================================================
# Animation 20: FadCrypt Hex + Binary Mix RED (Continuous)
# ============================================================================
def fadcrypt_hex_binary_mix_red():
    """FadCrypt with mixed hex and binary in RED"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 20: FadCrypt Hex + Binary Mix RED")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    text = "[ F A D C R Y P T ]"
    hex_chars = "0123456789ABCDEF"
    width = 60
    
    try:
        frame = 0
        while True:
            # Top row: Hex
            line_hex = ""
            for col in range(0, width, 3):
                hex_byte = random.choice(hex_chars) + random.choice(hex_chars)
                if random.random() > 0.7:
                    line_hex += f"\033[38;2;255;0;0m{hex_byte}\033[0m "
                else:
                    line_hex += f"\033[38;2;100;0;0m{hex_byte}\033[0m "
            print(f"{ANSI.move_to(5, 1)}{line_hex}", end='')
            
            # Bottom row: Binary
            line_bin = ""
            for i in range(width):
                bit = random.choice('01')
                if random.random() > 0.6:
                    line_bin += f"\033[38;2;255;0;0m{bit}\033[0m"
                else:
                    line_bin += f"\033[38;2;80;0;0m{bit}\033[0m"
            print(f"{ANSI.move_to(7, 1)}{line_bin}", end='')
            
            # FadCrypt text
            padding = (60 - len(text)) // 2
            if frame % 3 == 0:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[97m{text}\033[0m", end='')
            elif frame % 3 == 1:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[91m{text}\033[0m", end='')
            else:
                print(f"{ANSI.move_to(6, padding)}\033[1m\033[38;2;255;100;0m{text}\033[0m", end='')
            
            sys.stdout.flush()
            time.sleep(0.12)
            frame += 1
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")


# ============================================================================
# Animation 21: FadCrypt Binary Glitch RED (Continuous)
# ============================================================================
def fadcrypt_binary_glitch_red():
    """FadCrypt with glitchy binary in RED"""
    print(ANSI.CLEAR + ANSI.HOME)
    print(ANSI.HIDE_CURSOR)
    print("\n" + "="*60)
    print("ANIMATION 21: FadCrypt Binary Glitch RED")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    text = "FADCRYPT"
    width = 60
    
    try:
        frame = 0
        while True:
            # Glitchy binary background
            for row in [5, 7]:
                line = ""
                for i in range(width):
                    if random.random() > 0.3:
                        bit = random.choice('01')
                        # Random red intensities for glitch effect
                        if random.random() > 0.9:
                            line += f"\033[1m\033[91m{bit}\033[0m"
                        elif random.random() > 0.7:
                            line += f"\033[38;2;255;0;0m{bit}\033[0m"
                        else:
                            line += f"\033[38;2;{random.randint(50, 150)};0;0m{bit}\033[0m"
                    else:
                        line += " "
                
                print(f"{ANSI.move_to(row, 1)}{line}", end='')
            
            # Glitchy FadCrypt text
            padding = (60 - len(text)) // 2
            glitched_text = ""
            for char in text:
                if random.random() > 0.95:
                    # Glitch character
                    glitched_text += f"\033[1m\033[91m{random.choice('01')}\033[0m"
                elif random.random() > 0.9:
                    # Offset character
                    glitched_text += f"\033[38;2;255;50;50m{char}\033[0m"
                else:
                    # Normal
                    glitched_text += f"\033[1m\033[97m{char}\033[0m"
            
            print(f"{ANSI.move_to(6, padding)}{glitched_text}", end='')
            
            sys.stdout.flush()
            time.sleep(0.08)
            frame += 1
        
    except KeyboardInterrupt:
        print(ANSI.SHOW_CURSOR)
        input("\n\n\n\n\nPress Enter to continue...")
