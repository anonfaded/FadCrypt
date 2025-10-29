"""
Interactive File Selector

Allows users to select files/folders with checkboxes in TUI.
Real-time keyboard input without pressing Enter.
"""

import os
import sys
from typing import List, Dict, Optional
from datetime import datetime

# Platform-specific keyboard input
try:
    if sys.platform == 'win32':
        import msvcrt
    else:
        import termios
        import tty
except ImportError:
    pass

from .colors import Colors, print_error


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
        elif key == b' ':  # Space
            return 'space'
        elif key == b'\r':  # Enter
            return 'enter'
        elif key == b'\x1b':  # Escape
            return 'escape'
        elif key in [b'q', b'Q']:
            return 'q'
        elif key in [b'a', b'A']:
            return 'a'
        elif key in [b'n', b'N']:
            return 'n'
        elif key in [b'b', b'B']:
            return 'b'
        elif key in [b'f', b'F']:
            return 'f'
        elif key in [b'i', b'I']:
            return 'i'
        elif key in [b'x', b'X']:
            return 'x'
        elif key in [b'v', b'V']:
            return 'v'
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
                if key == '\x1b[C':  # Right arrow
                    return 'right'
                if key == '\x1b[D':  # Left arrow
                    return 'left'
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


def confirm_action(message: str) -> bool:
    """Show confirmation dialog and return True if confirmed"""
    print(f"\n{Colors.WARNING}{message} (y/n):{Colors.RESET}")
    print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
    return input().strip().lower() == 'y'


class FileSelector:
    """Interactive file/folder selector with checkboxes and real-time input"""

    def __init__(self, current_dir: Optional[str] = None):
        """
        Initialize file selector.

        Args:
            current_dir: Starting directory (default: current working directory)
        """
        self.current_dir = current_dir or os.getcwd()
        self.selected_items = set()
        self.cursor_pos = 0
        self.items = []
        self.scroll_offset = 0
        self.max_visible_items = 10  # Default items display
        self.max_visible_selected = 4  # Default selected display
        self.items_view_mode = "normal"  # "normal" (10) or "expanded" (30)
        self.selected_view_mode = "normal"  # "normal" (4) or "expanded" (30)

    def scan_directory(self) -> List[Dict]:
        """
        Scan current directory for files and folders.

        Returns:
            List of items with metadata
        """
        items = []

        try:
            entries = os.listdir(self.current_dir)
            entries.sort()

            for entry in entries:
                full_path = os.path.join(self.current_dir, entry)

                # Skip hidden files on Unix
                if entry.startswith('.') and sys.platform != 'win32':
                    continue

                is_dir = os.path.isdir(full_path)
                
                # Get file stats
                try:
                    stat = os.stat(full_path)
                    if is_dir:
                        # For directories, try to get size quickly or leave empty
                        try:
                            # Quick check - only count immediate files, not recursive
                            dir_size = 0
                            dir_entries = os.listdir(full_path)[:10]  # Limit to first 10 for speed
                            for dir_entry in dir_entries:
                                entry_path = os.path.join(full_path, dir_entry)
                                if os.path.isfile(entry_path):
                                    dir_size += os.path.getsize(entry_path)
                            size_mb = dir_size / (1024 * 1024) if dir_size > 0 else 0
                        except (OSError, PermissionError):
                            size_mb = 0
                    else:
                        size_mb = stat.st_size / (1024 * 1024)
                    
                    # Format date as readable: 25-Oct-2025 2:30 PM
                    dt = datetime.fromtimestamp(stat.st_mtime)
                    modified = dt.strftime('%d-%b-%Y %I:%M %p')
                except (OSError, PermissionError):
                    size_mb = 0
                    modified = "Unknown"

                items.append({
                    'name': entry,
                    'path': full_path,
                    'type': 'folder' if is_dir else 'file',
                    'icon': Colors.ICON_FOLDER if is_dir else Colors.ICON_FILE,
                    'size_mb': size_mb,
                    'modified': modified
                })

        except PermissionError:
            print_error(f"Permission denied: {self.current_dir}")
        except Exception as e:
            print_error(f"Error scanning directory: {e}")

        return items

    def display_selector(self):
        """Display the file selector interface"""
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')

        # Header with full path
        dir_name = os.path.basename(self.current_dir) or self.current_dir
        print(f"{Colors.BORDER}╭─ {Colors.TITLE}Select Files/Folders to Lock{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.INFO}Directory: "
              f"{Colors.HIGHLIGHT}{dir_name}{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.INFO}Full Path: "
              f"{Colors.DIM}{self.current_dir}{Colors.RESET}")
        
        # Show info about locked items if any exist
        if hasattr(self, 'locked_paths') and self.locked_paths:
            locked_count = sum(1 for item in self.items if item['path'] in self.locked_paths)
            if locked_count > 0:
                print(f"{Colors.BORDER}│{Colors.RESET} {Colors.WARNING}ℹ️  {locked_count} item(s) already locked (shown with 🔒, cannot be selected){Colors.RESET}")
        
        print(f"{Colors.BORDER}╰─────────────────────────────────────────────"
              f"─────────────────{Colors.RESET}\n")

        # Items box with view mode indicator
        if self.items_view_mode == "collapsed":
            view_indicator = "▶"
            view_text = f"ITEMS ({len(self.items)}) - collapsed"
        elif self.items_view_mode == "expanded":
            view_indicator = "▼"
            view_text = f"ITEMS (showing 30/{len(self.items)})"
        else:
            view_indicator = "▼"
            view_text = f"ITEMS (showing 10/{len(self.items)})"
        
        print(f"{Colors.BORDER}╭─ {Colors.TITLE}{view_indicator} {view_text}{Colors.RESET}")

        if not self.items:
            if self.items_view_mode != "collapsed":
                print(f"{Colors.BORDER}│{Colors.RESET} {Colors.DIM}No items found{Colors.RESET}")
        elif self.items_view_mode == "collapsed":
            print(f"{Colors.BORDER}│{Colors.RESET} {Colors.DIM}[Press [I] to show items]{Colors.RESET}")
        else:
            # Calculate visible range for scrolling
            max_items = 30 if self.items_view_mode == "expanded" else 10
            start_idx = max(0, self.cursor_pos - max_items // 2)
            if start_idx + max_items > len(self.items):
                start_idx = max(0, len(self.items) - max_items)
            end_idx = min(len(self.items), start_idx + max_items)

            for i in range(start_idx, end_idx):
                item = self.items[i]
                is_selected = item['path'] in self.selected_items
                is_cursor = i == self.cursor_pos

                # Check if item is already locked
                is_locked = hasattr(self, 'locked_paths') and item['path'] in self.locked_paths
                
                # Checkbox - grayed out if locked, can't select locked items
                if is_locked:
                    checkbox = f"{Colors.DIM}□{Colors.RESET}"  # Grayed out checkbox
                else:
                    checkbox = Colors.CHECKBOX_CHECKED if is_selected else Colors.CHECKBOX_UNCHECKED

                # Item text with file info
                icon = item['icon']
                name = item['name']
                if len(name) > 30:  # Reduced to make room for lock column
                    name = name[:27] + '...'
                
                # Lock indicator in its own column (before size)
                lock_col = "🔒" if is_locked else "  "
                
                # File info columns - consistent 8-character width
                if item['type'] == 'folder':
                    if item['size_mb'] > 0:
                        size_info = f"{Colors.DIM}{item['size_mb']:6.2f}MB{Colors.RESET}"
                    else:
                        size_info = f"{Colors.DIM}{'':>8}{Colors.RESET}"  # 8 spaces for consistent alignment
                else:
                    if item['size_mb'] < 0.01:
                        size_info = f"{Colors.DIM}{'0.01MB':>8}{Colors.RESET}"
                    else:
                        size_info = f"{Colors.DIM}{f'{item["size_mb"]:.2f}MB':>8}{Colors.RESET}"
                
                date_info = f"{Colors.DIM}{item['modified']}{Colors.RESET}"
                
                # Gray out locked items
                text_color = Colors.DIM if is_locked else Colors.TEXT

                # Cursor indicator and background
                if is_cursor:
                    # Red background covers content up to end of time column
                    line_start = f"{Colors.BORDER}│{Colors.SUCCESS}❯{Colors.RESET} {checkbox} "
                    # Format size display consistently
                    if item['type'] == 'folder':
                        if item['size_mb'] > 0:
                            size_display = f"{item['size_mb']:6.2f}MB"
                        else:
                            size_display = ""
                    else:
                        if item['size_mb'] < 0.01:
                            size_display = "0.01MB"
                        else:
                            size_display = f"{item['size_mb']:6.2f}MB"
                    
                    # Apply red background with WHITE text for better contrast
                    # \033[41m = red background, \033[97m = bright white text
                    print(f"{line_start}\033[41m\033[97m{icon} {name:<30} {lock_col} {size_display:>8} {item['modified']} \033[0m")
                else:
                    print(f"{Colors.BORDER}│{Colors.RESET}  {checkbox} {icon} "
                          f"{text_color}{name:<30}{Colors.RESET} {lock_col} {size_info} {date_info}")

            # Show scroll indicators - only show relevant direction
            max_items = 30 if self.items_view_mode == "expanded" else 10
            if len(self.items) > max_items:
                current_pos = self.cursor_pos + 1
                total_items = len(self.items)
                scroll_info = f"({current_pos}/{total_items})"

                # Only show the direction that's relevant
                if start_idx > 0 and end_idx < len(self.items):
                    # Show both if in middle
                    if self.cursor_pos < len(self.items) // 2:
                        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.DIM}↓ More items below "
                              f"{scroll_info}{Colors.RESET}")
                    else:
                        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.DIM}↑ More items above "
                              f"{scroll_info}{Colors.RESET}")
                elif start_idx > 0:
                    print(f"{Colors.BORDER}│{Colors.RESET} {Colors.DIM}↑ More items above "
                          f"{scroll_info}{Colors.RESET}")
                elif end_idx < len(self.items):
                    print(f"{Colors.BORDER}│{Colors.RESET} {Colors.DIM}↓ More items below "
                          f"{scroll_info}{Colors.RESET}")

        print(f"{Colors.BORDER}╰─────────────────────────────────────────────"
              f"─────────────────{Colors.RESET}")

        # Selected items display with view modes
        if self.selected_items or self.selected_view_mode == "collapsed":
            if self.selected_view_mode == "collapsed":
                view_indicator = "▶"
                view_text = f"SELECTED ITEMS ({len(self.selected_items)}) - collapsed"
            elif self.selected_view_mode == "expanded":
                view_indicator = "▼"
                view_text = f"SELECTED ITEMS (showing 30/{len(self.selected_items)})"
            else:
                view_indicator = "▼"
                view_text = f"SELECTED ITEMS (showing 4/{len(self.selected_items)})"
            
            print(f"\n{Colors.BORDER}╭─ {Colors.SUCCESS}{view_indicator} {view_text}{Colors.RESET}")

            if self.selected_view_mode != "collapsed" and self.selected_items:
                max_selected = 30 if self.selected_view_mode == "expanded" else 4
                display_count = min(max_selected, len(self.selected_items))
                for path in list(self.selected_items)[:display_count]:
                    name = os.path.basename(path)
                    if len(name) > 20:
                        name = name[:17] + '...'
                    file_type = "📁 Folder" if os.path.isdir(path) else "📄 File"
                    print(f"{Colors.BORDER}│{Colors.RESET} {Colors.SUCCESS}✓{Colors.RESET} "
                          f"{Colors.TEXT}{name}{Colors.RESET} {Colors.DIM}({file_type}){Colors.RESET}")

                if len(self.selected_items) > max_selected:
                    remaining = len(self.selected_items) - max_selected
                    print(f"{Colors.BORDER}│{Colors.RESET} {Colors.DIM}... and {remaining} "
                          f"more{Colors.RESET}")
            elif self.selected_view_mode == "collapsed":
                print(f"{Colors.BORDER}│{Colors.RESET} {Colors.DIM}[Press [V] to show selected items]{Colors.RESET}")
            elif not self.selected_items:
                print(f"{Colors.BORDER}│{Colors.RESET} {Colors.DIM}[No items selected]{Colors.RESET}")

            print(f"{Colors.BORDER}╰─────────────────────────────────────────────"
                  f"─────────────────{Colors.RESET}")

        # Help text - organized by category
        print(f"\n{Colors.INFO}Navigation:{Colors.RESET}")
        print(f"{Colors.DIM}[{Colors.SUCCESS}↑↓{Colors.DIM}] Navigate  "
              f"[{Colors.SUCCESS}Space{Colors.DIM}] Select  "
              f"[{Colors.SUCCESS}A{Colors.DIM}] Select All  "
              f"[{Colors.SUCCESS}N{Colors.DIM}] Clear All{Colors.RESET}")

        print(f"\n{Colors.INFO}Directory:{Colors.RESET}")
        print(f"{Colors.DIM}[{Colors.SUCCESS}B{Colors.DIM}] Back  "
              f"[{Colors.SUCCESS}F{Colors.DIM}] Enter Folder{Colors.RESET}")

        print(f"\n{Colors.INFO}View:{Colors.RESET}")
        # Show current state and next action
        if self.items_view_mode == "normal":
            items_status = "Normal → Expand"
        elif self.items_view_mode == "expanded":
            items_status = "Expanded → Collapse"
        else:
            items_status = "Collapsed → Normal"
            
        if self.selected_view_mode == "normal":
            selected_status = "Normal → Expand"
        elif self.selected_view_mode == "expanded":
            selected_status = "Expanded → Collapse"
        else:
            selected_status = "Collapsed → Normal"
            
        print(f"{Colors.DIM}[{Colors.SUCCESS}I{Colors.DIM}] Items ({items_status})  "
              f"[{Colors.SUCCESS}V{Colors.DIM}] Selected ({selected_status}){Colors.RESET}")

        print(f"\n{Colors.INFO}Actions:{Colors.RESET}")
        print(f"{Colors.DIM}[{Colors.SUCCESS}Enter{Colors.DIM}] Confirm Selection  "
              f"[{Colors.SUCCESS}Q{Colors.DIM}] Quit{Colors.RESET}\n")

    def go_back(self) -> bool:
        """Go back to parent directory"""
        parent = os.path.dirname(self.current_dir)
        if parent != self.current_dir:
            if confirm_action("Go back to parent directory?"):
                self.current_dir = parent
                self.items = self.scan_directory()
                self.cursor_pos = 0
                return True
        else:
            print(f"\n{Colors.WARNING}Already at root directory. "
                  f"Press any key to continue...{Colors.RESET}")
            get_key()
        return False

    def enter_folder(self) -> bool:
        """Enter the currently selected folder"""
        if 0 <= self.cursor_pos < len(self.items):
            current_item = self.items[self.cursor_pos]
            if current_item['type'] == 'folder':
                folder_path = current_item['path']
                folder_name = current_item['name']
                if confirm_action(f"Enter folder '{folder_name}'?"):
                    self.current_dir = folder_path
                    self.items = self.scan_directory()
                    self.cursor_pos = 0
                    return True
            else:
                print(f"\n{Colors.WARNING}Selected item is not a folder. "
                      f"Press any key to continue...{Colors.RESET}")
                get_key()
        else:
            print(f"\n{Colors.WARNING}No item selected. "
                  f"Press any key to continue...{Colors.RESET}")
            get_key()
        return False

    def select_files(self, locked_paths: set = None) -> List[str]:
        """
        Run interactive file selector.

        Args:
            locked_paths: Set of paths that are already locked (to show indicators)

        Returns:
            List of selected file paths
        """
        self.locked_paths = locked_paths or set()
        self.items = self.scan_directory()

        if not self.items:
            print_error("No files or folders found in current directory.")
            return []

        # Real-time keyboard input
        self.display_selector()  # Initial display

        while True:
            # Get key (blocking - waits for actual keypress)
            key = get_key()

            if key == 'q':
                # Quit with confirmation
                if confirm_action("Quit without selecting?"):
                    return []
                self.display_selector()
                continue

            if key == 'b':
                # Go back to parent directory
                if self.go_back():
                    self.display_selector()
                else:
                    self.display_selector()
                continue

            if key == 'f':
                # Enter the selected folder
                if self.enter_folder():
                    self.display_selector()
                else:
                    self.display_selector()
                continue

            if key in ['up', 'u']:
                self.cursor_pos = max(0, self.cursor_pos - 1)

            elif key in ['down', 'd']:
                self.cursor_pos = min(len(self.items) - 1, self.cursor_pos + 1)

            elif key in ['space', 's']:
                # Toggle selection (stay on same line)
                if 0 <= self.cursor_pos < len(self.items):
                    item_path = self.items[self.cursor_pos]['path']
                    # Don't allow selecting already-locked items
                    is_locked = hasattr(self, 'locked_paths') and item_path in self.locked_paths
                    if not is_locked:
                        if item_path in self.selected_items:
                            self.selected_items.remove(item_path)
                        else:
                            self.selected_items.add(item_path)
                    # Don't move cursor - stay on same line

            elif key in ['enter', 'e']:
                # Confirm selection with confirmation
                if self.selected_items:
                    if confirm_action(f"Confirm selection of {len(self.selected_items)} items?"):
                        return list(self.selected_items)
                    # If not confirmed, redraw and continue
                    self.display_selector()
                    continue

                print(f"\n{Colors.WARNING}No items selected. "
                      f"Press any key to continue...{Colors.RESET}")
                get_key()
                self.display_selector()
                continue

            elif key == 'a':
                # Select all
                for item in self.items:
                    self.selected_items.add(item['path'])

            elif key == 'n':
                # Clear all selections
                self.selected_items.clear()

            elif key == 'i':
                # Cycle through items view modes: normal -> expanded -> collapsed -> normal
                if self.items_view_mode == "normal":
                    self.items_view_mode = "expanded"
                elif self.items_view_mode == "expanded":
                    self.items_view_mode = "collapsed"
                else:
                    self.items_view_mode = "normal"

            elif key == 'v':
                # Cycle through selected view modes: normal -> expanded -> collapsed -> normal
                if self.selected_view_mode == "normal":
                    self.selected_view_mode = "expanded"
                elif self.selected_view_mode == "expanded":
                    self.selected_view_mode = "collapsed"
                else:
                    self.selected_view_mode = "normal"

            elif key.isdigit():
                # Quick select by number (1-9)
                idx = int(key) - 1
                if 0 <= idx < len(self.items):
                    self.cursor_pos = idx
                    item_path = self.items[idx]['path']
                    if item_path in self.selected_items:
                        self.selected_items.remove(item_path)
                    else:
                        self.selected_items.add(item_path)

            else:
                # Unknown key, don't redraw
                continue

            # Only redraw if we processed a valid key
            self.display_selector()

    def select_from_list(self, items: List[Dict], title: str = "Select Items") -> List[str]:
        """
        Select from a predefined list of items.

        Args:
            items: List of items with 'name', 'path', 'type' keys
            title: Title for the selector

        Returns:
            List of selected paths
        """
        self.items = items
        self.cursor_pos = 0
        self.selected_items = set()

        if not self.items:
            print_error("No items to select from.")
            return []

        # Initial display
        def display_list():
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')

            # Header
            print(f"{Colors.BORDER}╭─ {Colors.TITLE}{title}{Colors.RESET}")
            print(f"{Colors.BORDER}╰─────────────────────────────────────────────"
                  f"─────────────────{Colors.RESET}\n")

            # Items
            print(f"{Colors.BORDER}╭─ {Colors.TITLE}ITEMS{Colors.RESET}")

            for i, item in enumerate(self.items):
                is_selected = item['path'] in self.selected_items
                is_cursor = i == self.cursor_pos

                checkbox = Colors.CHECKBOX_CHECKED if is_selected else Colors.CHECKBOX_UNCHECKED
                icon = Colors.ICON_FOLDER if item['type'] == 'folder' else Colors.ICON_FILE
                name = item['name']
                if len(name) > 35:  # Reduced to make room for file info
                    name = name[:32] + '...'
                
                # Get file info if available
                try:
                    path = item['path']
                    if os.path.exists(path):
                        stat_info = os.stat(path)
                        size_mb = stat_info.st_size / (1024 * 1024)
                        modified_time = datetime.fromtimestamp(stat_info.st_mtime)
                        modified_str = modified_time.strftime("%d-%b-%Y %I:%M %p")
                        
                        if item['type'] == 'folder':
                            size_display = "" if size_mb == 0 else f"{size_mb:6.2f}MB"
                        else:
                            size_display = f"{max(0.01, size_mb):6.2f}MB"
                    else:
                        size_display = ""
                        modified_str = "N/A"
                except:
                    size_display = ""
                    modified_str = "N/A"

                # Cursor indicator and background
                if is_cursor:
                    # Red background with WHITE text for better contrast
                    line_start = f"{Colors.BORDER}│{Colors.SUCCESS}❯{Colors.RESET} {checkbox} "
                    line_content = f"{icon} {name:<35} {size_display:>8} {modified_str}"
                    # Apply red background with bright white text
                    print(f"{line_start}\033[41m\033[97m{line_content} \033[0m")
                else:
                    size_info = f"{Colors.DIM}{size_display:>8}{Colors.RESET}" if size_display else " " * 8
                    date_info = f"{Colors.DIM}{modified_str}{Colors.RESET}"
                    print(f"{Colors.BORDER}│{Colors.RESET}  {checkbox} {icon} "
                          f"{Colors.TEXT}{name:<35}{Colors.RESET} {size_info} {date_info}")

            # Add scroll indicators if needed
            if len(self.items) > 15:  # If more items than can fit
                current_pos = self.cursor_pos + 1
                total_items = len(self.items)
                scroll_info = f"({current_pos}/{total_items})"
                print(f"{Colors.BORDER}│{Colors.RESET} {Colors.DIM}Scroll: "
                      f"{scroll_info}{Colors.RESET}")

            print(f"{Colors.BORDER}╰─────────────────────────────────────────────"
                  f"─────────────────{Colors.RESET}")

            # Help
            print(f"\n{Colors.INFO}Controls:{Colors.RESET}")
            print(f"{Colors.DIM}[{Colors.SUCCESS}↑↓{Colors.DIM}] Navigate  "
                  f"[{Colors.SUCCESS}Space{Colors.DIM}] Select  "
                  f"[{Colors.SUCCESS}Enter{Colors.DIM}] Confirm  "
                  f"[{Colors.SUCCESS}A{Colors.DIM}] Select All  "
                  f"[{Colors.SUCCESS}N{Colors.DIM}] Clear All  "
                  f"[{Colors.SUCCESS}Q{Colors.DIM}] Quit{Colors.RESET}")
            print(f"{Colors.INFO}Selected: {Colors.HIGHLIGHT}{len(self.selected_items)} "
                  f"items{Colors.RESET}\n")

        display_list()  # Initial display

        while True:
            # Real-time keyboard input (blocking)
            key = get_key()

            if key == 'q':
                # Quit with confirmation
                if confirm_action("Quit without selecting?"):
                    return []
                display_list()
                continue

            if key in ['up', 'u']:
                self.cursor_pos = max(0, self.cursor_pos - 1)

            elif key in ['down', 'd']:
                self.cursor_pos = min(len(self.items) - 1, self.cursor_pos + 1)

            elif key in ['space', 's']:
                if 0 <= self.cursor_pos < len(self.items):
                    item_path = self.items[self.cursor_pos]['path']
                    if item_path in self.selected_items:
                        self.selected_items.remove(item_path)
                    else:
                        self.selected_items.add(item_path)
                    # Don't move cursor after selection

            elif key in ['enter', 'e']:
                if confirm_action(f"Confirm selection of {len(self.selected_items)} items?"):
                    return list(self.selected_items)
                display_list()
                continue

            elif key == 'a':
                for item in self.items:
                    self.selected_items.add(item['path'])

            elif key == 'n':
                self.selected_items.clear()

            elif key == 'i':
                # Cycle through items view modes
                if self.items_view_mode == "normal":
                    self.items_view_mode = "expanded"
                elif self.items_view_mode == "expanded":
                    self.items_view_mode = "collapsed"
                else:
                    self.items_view_mode = "normal"

            elif key == 'v':
                # Cycle through selected view modes
                if self.selected_view_mode == "normal":
                    self.selected_view_mode = "expanded"
                elif self.selected_view_mode == "expanded":
                    self.selected_view_mode = "collapsed"
                else:
                    self.selected_view_mode = "normal"

            elif key.isdigit():
                idx = int(key) - 1
                if 0 <= idx < len(self.items):
                    self.cursor_pos = idx
                    item_path = self.items[idx]['path']
                    if item_path in self.selected_items:
                        self.selected_items.remove(item_path)
                    else:
                        self.selected_items.add(item_path)

            else:
                # Unknown key, don't redraw
                continue

            # Only redraw if we processed a valid key
            display_list()