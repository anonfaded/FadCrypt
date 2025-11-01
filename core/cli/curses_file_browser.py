"""
Professional Curses-based file browser for FadCrypt
Automatically adjusts to terminal size with full feature set
"""

import curses
import os
from typing import List, Dict, Optional, Set
from datetime import datetime


class CursesFileBrowser:
    """Professional curses-based file browser with full feature set"""
    
    def __init__(self, stdscr, current_dir: str = None, mode: str = "lock", locked_paths: Set[str] = None):
        self.stdscr = stdscr
        self.current_dir = current_dir or os.getcwd()
        self.cursor_pos = 0
        self.running = True
        self.selected_items = set()
        self.items = []
        self.mode = mode  # "lock" or "unlock"
        self.locked_paths = locked_paths or set()
        
        # View modes
        self.items_view_mode = "normal"  # "normal", "expanded", "collapsed"
        self.selected_view_mode = "normal"
        self.unlock_filter_mode = "current"
        
        # Setup colors
        curses.start_color()
        try:
            curses.use_default_colors()
        except AttributeError:
            pass
        
        curses.init_pair(1, curses.COLOR_RED, -1)      # Red
        curses.init_pair(2, curses.COLOR_WHITE, -1)    # White
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)  # White on red
        curses.init_pair(4, curses.COLOR_CYAN, -1)     # Cyan
        curses.init_pair(5, curses.COLOR_GREEN, -1)    # Green
        curses.init_pair(6, 8, -1)                     # Gray
        curses.init_pair(7, curses.COLOR_YELLOW, -1)   # Yellow
        
        # Hide cursor
        curses.curs_set(0)
        
        # Load directory contents
        if mode == "lock":
            self.load_directory()
    
    def get_terminal_size(self):
        """Get terminal dimensions"""
        try:
            height, width = self.stdscr.getmaxyx()
            return height, width
        except:
            return 24, 80  # Default fallback
    
    def load_directory(self):
        """Load directory contents"""
        try:
            entries = []
            for item in os.listdir(self.current_dir):
                item_path = os.path.join(self.current_dir, item)
                
                # Skip hidden files on Unix
                if item.startswith('.') and os.name != 'nt':
                    continue
                
                try:
                    stat = os.stat(item_path)
                    is_dir = os.path.isdir(item_path)
                    
                    if is_dir:
                        # For directories, try to get size quickly
                        try:
                            dir_size = 0
                            dir_entries = os.listdir(item_path)[:10]
                            for dir_entry in dir_entries:
                                entry_path = os.path.join(item_path, dir_entry)
                                if os.path.isfile(entry_path):
                                    dir_size += os.path.getsize(entry_path)
                            size_mb = dir_size / (1024 * 1024) if dir_size > 0 else 0
                        except (OSError, PermissionError):
                            size_mb = 0
                        icon = "📁"
                    else:
                        size_mb = stat.st_size / (1024 * 1024)
                        icon = "📄"
                    
                    dt = datetime.fromtimestamp(stat.st_mtime)
                    modified = dt.strftime('%d-%b-%Y %I:%M %p')
                    
                    entries.append({
                        'name': item,
                        'path': item_path,
                        'type': 'folder' if is_dir else 'file',
                        'icon': icon,
                        'size_mb': size_mb,
                        'modified': modified,
                        'is_dir': is_dir
                    })
                except (OSError, PermissionError):
                    continue
            
            entries.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
            self.items = entries
            
        except (OSError, PermissionError):
            self.items = []
    
    def draw_interface(self):
        """Draw the complete responsive interface"""
        height, width = self.get_terminal_size()
        
        # Clear screen
        self.stdscr.clear()
        
        # Calculate layout
        header_height = 4
        help_height = 6  # Updated to 6 for help + current item path
        available_height = height - header_height - help_height
        
        # Determine items display count based on available space
        if self.items_view_mode == "collapsed":
            items_display = 0
        elif self.items_view_mode == "expanded":
            items_display = max(10, available_height - 8)  # More space for expanded
        else:  # normal
            items_display = max(5, (available_height - 8) // 2)  # Half space for normal
        
        # Selected items display count
        selected_display = max(2, available_height - items_display - 6)
        
        current_row = 0
        
        # Draw header
        current_row = self.draw_header(current_row, width)
        
        # Draw items
        current_row = self.draw_items(current_row, width, items_display)
        
        # Draw selected items (if space allows)
        if current_row < height - help_height - 2:
            current_row = self.draw_selected_items(current_row, width, selected_display)
        
        # Draw help at bottom
        self.draw_help(height - help_height, width)
        
        self.stdscr.refresh()
    
    def draw_header(self, start_row, width):
        """Draw compact header"""
        try:
            # App header
            self.stdscr.addstr(start_row, 2, "╭─ ", curses.color_pair(1))
            self.stdscr.addstr(start_row, 5, "FadCrypt v2.0.0", curses.color_pair(1) | curses.A_BOLD)
            
            self.stdscr.addstr(start_row + 1, 2, "│ ", curses.color_pair(1))
            title = "🔒 Lock Files/Folders" if self.mode == "lock" else "🔓 Unlock Items"
            self.stdscr.addstr(start_row + 1, 4, title, curses.color_pair(2))
            
            # Path and filter info (for unlock mode) or locked items warning (for lock mode)
            if hasattr(self, 'current_dir') and self.current_dir:
                self.stdscr.addstr(start_row + 2, 2, "│ ", curses.color_pair(1))
                if self.mode == "unlock":
                    filter_text = "Current Dir" if self.unlock_filter_mode == "current" else "All Locations"
                    path_display = f"Filter: {filter_text} | {self.current_dir}"
                    if len(path_display) > width - 10:
                        path_display = "..." + path_display[-(width-13):]
                    self.stdscr.addstr(start_row + 2, 4, path_display, curses.color_pair(6))
                else:
                    # Lock mode - show path and locked items warning if any
                    path_display = self.current_dir
                    if len(path_display) > width - 10:
                        path_display = "..." + path_display[-(width-13):]
                    self.stdscr.addstr(start_row + 2, 4, path_display, curses.color_pair(6))
                    
                    # Add warning about locked items if any exist
                    if hasattr(self, 'locked_paths') and self.locked_paths:
                        locked_count = len([item for item in self.items if item['path'] in self.locked_paths])
                        if locked_count > 0:
                            self.stdscr.addstr(start_row + 3, 2, "│ ", curses.color_pair(1))
                            warning_text = f"⚠️  {locked_count} item(s) already locked (🔒 - cannot be selected)"
                            if len(warning_text) > width - 10:
                                warning_text = f"⚠️  {locked_count} locked items (🔒 - cannot select)"
                            self.stdscr.addstr(start_row + 3, 4, warning_text, curses.color_pair(7))  # Yellow warning
                            self.stdscr.addstr(start_row + 4, 2, "╰" + "─" * min(60, width-5), curses.color_pair(1))
                            return start_row + 5
            
            self.stdscr.addstr(start_row + 3, 2, "╰" + "─" * min(60, width-5), curses.color_pair(1))
            
        except curses.error:
            pass
        
        return start_row + 4
    
    def draw_items(self, start_row, width, max_display):
        """Draw items section responsively"""
        try:
            # Items header
            if self.items_view_mode == "collapsed":
                view_text = f"▶ ITEMS ({len(self.items)}) - collapsed"
            else:
                view_text = f"▼ ITEMS (showing {min(max_display, len(self.items))}/{len(self.items)})"
            
            self.stdscr.addstr(start_row, 2, "╭─ ", curses.color_pair(1))
            self.stdscr.addstr(start_row, 5, view_text, curses.color_pair(1) | curses.A_BOLD)
            
            current_row = start_row + 1
            
            if not self.items:
                self.stdscr.addstr(current_row, 2, "│ ", curses.color_pair(1))
                self.stdscr.addstr(current_row, 4, "No items found", curses.color_pair(6))
                current_row += 1
            elif self.items_view_mode == "collapsed":
                self.stdscr.addstr(current_row, 2, "│ ", curses.color_pair(1))
                self.stdscr.addstr(current_row, 4, "[Press [I] to show items]", curses.color_pair(6))
                current_row += 1
            else:
                # Calculate scrolling
                if len(self.items) <= max_display:
                    start_idx = 0
                    end_idx = len(self.items)
                else:
                    half_view = max_display // 2
                    start_idx = max(0, self.cursor_pos - half_view)
                    if start_idx + max_display > len(self.items):
                        start_idx = len(self.items) - max_display
                    end_idx = min(len(self.items), start_idx + max_display)
                
                # Draw items
                for i in range(start_idx, end_idx):
                    item = self.items[i]
                    
                    is_selected = item['path'] in self.selected_items
                    is_cursor = i == self.cursor_pos
                    is_locked = self.mode == "lock" and item['path'] in self.locked_paths
                    
                    # Checkbox - use green checkmark for selected items
                    if is_locked:
                        checkbox = "□"  # Gray checkbox for locked items
                    elif is_selected:
                        checkbox = "✓"  # Green checkmark for selected items
                    else:
                        checkbox = "☐"  # Empty checkbox for unselected items
                    
                    # Format name, size, and date like the old version
                    name = item['name'][:30] + "..." if len(item['name']) > 30 else item['name']
                    
                    if item['type'] == 'folder':
                        size_display = f"{item['size_mb']:6.2f}MB" if item['size_mb'] > 0 else ""
                    else:
                        size_display = f"{max(0.01, item['size_mb']):6.2f}MB"
                    
                    # Lock indicator column (like old version)
                    lock_col = "🔒" if is_locked else "  "
                    
                    # Date/time column
                    date_display = item['modified']
                    
                    # Draw row
                    self.stdscr.addstr(current_row, 2, "│", curses.color_pair(1))
                    
                    if is_cursor:
                        # Cursor row - fix spacing and alignment like curses menu
                        self.stdscr.addstr(current_row, 3, "❯", curses.color_pair(5) | curses.A_BOLD)
                        # Add space after arrow WITHOUT red background
                        self.stdscr.addstr(current_row, 4, " ")
                        
                        # Draw each column separately with consistent positioning
                        # Checkbox with red background for cursor row
                        self.stdscr.addstr(current_row, 5, checkbox, curses.color_pair(3) | curses.A_BOLD)  # All checkboxes with red background
                        
                        # Icon and name with red background
                        self.stdscr.addstr(current_row, 6, f" {item['icon']} {name:<30}", curses.color_pair(3) | curses.A_BOLD)
                        
                        # Lock indicator with red background
                        self.stdscr.addstr(current_row, 40, f" {lock_col} ", curses.color_pair(3) | curses.A_BOLD)
                        
                        # Fill gap before size with red background
                        self.stdscr.addstr(current_row, 43, " ", curses.color_pair(3) | curses.A_BOLD)
                        
                        # Size with red background
                        self.stdscr.addstr(current_row, 44, f"{size_display:>8}", curses.color_pair(3) | curses.A_BOLD)
                        
                        # Fill gap between size and date with red background
                        self.stdscr.addstr(current_row, 52, " ", curses.color_pair(3) | curses.A_BOLD)
                        
                        # Date with red background - consistent position
                        self.stdscr.addstr(current_row, 53, f" {date_display}", curses.color_pair(3) | curses.A_BOLD)
                    else:
                        # Normal row with all columns - match cursor row positions exactly
                        text_color = curses.color_pair(6) if is_locked else curses.color_pair(2)
                        self.stdscr.addstr(current_row, 3, "  ")  # Two spaces to match cursor row spacing
                        
                        # Checkbox with appropriate color
                        if is_selected:
                            self.stdscr.addstr(current_row, 5, checkbox, curses.color_pair(5))  # Green checkmark
                        else:
                            self.stdscr.addstr(current_row, 5, checkbox, text_color)  # Normal color
                        
                        # Icon and name
                        self.stdscr.addstr(current_row, 6, f" {item['icon']} {name:<30}", text_color)
                        
                        # Lock indicator
                        self.stdscr.addstr(current_row, 40, f" {lock_col} ", text_color)
                        
                        # Size
                        self.stdscr.addstr(current_row, 44, f"{size_display:>8}", curses.color_pair(6))
                        
                        # Date - consistent position
                        self.stdscr.addstr(current_row, 53, f" {date_display}", curses.color_pair(6))
                    
                    current_row += 1
                
                # Scroll indicator
                if len(self.items) > max_display:
                    self.stdscr.addstr(current_row, 2, "│ ", curses.color_pair(1))
                    scroll_info = f"({self.cursor_pos + 1}/{len(self.items)})"
                    if start_idx > 0 and end_idx < len(self.items):
                        self.stdscr.addstr(current_row, 4, f"↑↓ Scroll {scroll_info}", curses.color_pair(6))
                    elif start_idx > 0:
                        self.stdscr.addstr(current_row, 4, f"↑ More above {scroll_info}", curses.color_pair(6))
                    elif end_idx < len(self.items):
                        self.stdscr.addstr(current_row, 4, f"↓ More below {scroll_info}", curses.color_pair(6))
                    current_row += 1
            
            # Footer
            self.stdscr.addstr(current_row, 2, "╰" + "─" * min(60, width-5), curses.color_pair(1))
            current_row += 1
            
        except curses.error:
            pass
        
        return current_row
    
    def draw_selected_items(self, start_row, width, max_display):
        """Draw selected items section"""
        if not self.selected_items and self.selected_view_mode != "collapsed":
            return start_row
        
        try:
            # Header
            if self.selected_view_mode == "collapsed":
                view_text = f"▶ SELECTED ({len(self.selected_items)}) - collapsed"
            else:
                view_text = f"▼ SELECTED ({min(max_display, len(self.selected_items))}/{len(self.selected_items)})"
            
            self.stdscr.addstr(start_row, 2, "╭─ ", curses.color_pair(1))
            self.stdscr.addstr(start_row, 5, view_text, curses.color_pair(5) | curses.A_BOLD)
            
            current_row = start_row + 1
            
            if self.selected_view_mode == "collapsed":
                self.stdscr.addstr(current_row, 2, "│ ", curses.color_pair(1))
                self.stdscr.addstr(current_row, 4, "[Press [V] to show selected]", curses.color_pair(6))
                current_row += 1
            elif self.selected_items:
                # Show selected items
                for i, path in enumerate(list(self.selected_items)[:max_display]):
                    name = os.path.basename(path)[:20] + "..." if len(os.path.basename(path)) > 20 else os.path.basename(path)
                    file_type = "📁 Folder" if os.path.isdir(path) else "📄 File"
                    
                    self.stdscr.addstr(current_row, 2, "│ ", curses.color_pair(1))
                    self.stdscr.addstr(current_row, 4, "✓ ", curses.color_pair(5))
                    self.stdscr.addstr(current_row, 6, f"{name} ({file_type})", curses.color_pair(2))
                    current_row += 1
                
                if len(self.selected_items) > max_display:
                    remaining = len(self.selected_items) - max_display
                    self.stdscr.addstr(current_row, 2, "│ ", curses.color_pair(1))
                    self.stdscr.addstr(current_row, 4, f"... and {remaining} more", curses.color_pair(6))
                    current_row += 1
            
            # Footer
            self.stdscr.addstr(current_row, 2, "╰" + "─" * min(60, width-5), curses.color_pair(1))
            current_row += 1
            
        except curses.error:
            pass
        
        return current_row
    
    def draw_help(self, start_row, width):
        """Draw categorized help like the old version - organized and clean"""
        try:
            # Navigation category
            self.stdscr.addstr(start_row, 2, "Navigation:", curses.color_pair(1) | curses.A_BOLD)
            self.stdscr.addstr(start_row, 14, "[", curses.color_pair(6))
            self.stdscr.addstr(start_row, 15, "↑↓", curses.color_pair(2))
            self.stdscr.addstr(start_row, 17, "] Navigate  [", curses.color_pair(6))
            self.stdscr.addstr(start_row, 30, "Space", curses.color_pair(2))
            self.stdscr.addstr(start_row, 35, "] Select  [", curses.color_pair(6))
            self.stdscr.addstr(start_row, 46, "A", curses.color_pair(2))
            self.stdscr.addstr(start_row, 47, "] All  [", curses.color_pair(6))
            self.stdscr.addstr(start_row, 55, "N", curses.color_pair(2))
            self.stdscr.addstr(start_row, 56, "] Clear", curses.color_pair(6))
            
            # Directory category (mode specific)
            if self.mode == "lock":
                self.stdscr.addstr(start_row + 1, 2, "Directory:", curses.color_pair(1) | curses.A_BOLD)
                self.stdscr.addstr(start_row + 1, 14, "[", curses.color_pair(6))
                self.stdscr.addstr(start_row + 1, 15, "B", curses.color_pair(2))
                self.stdscr.addstr(start_row + 1, 16, "] Back  [", curses.color_pair(6))
                self.stdscr.addstr(start_row + 1, 25, "F", curses.color_pair(2))
                self.stdscr.addstr(start_row + 1, 26, "] Folder  [", curses.color_pair(6))
                self.stdscr.addstr(start_row + 1, 37, "T", curses.color_pair(2))
                self.stdscr.addstr(start_row + 1, 38, "] Teleport", curses.color_pair(6))
            else:
                self.stdscr.addstr(start_row + 1, 2, "Directory:", curses.color_pair(1) | curses.A_BOLD)
                filter_text = "Current Dir" if self.unlock_filter_mode == "current" else "All Locations"
                self.stdscr.addstr(start_row + 1, 14, "[", curses.color_pair(6))
                self.stdscr.addstr(start_row + 1, 15, "D", curses.color_pair(2))
                self.stdscr.addstr(start_row + 1, 16, f"] Filter: {filter_text}  [", curses.color_pair(6))
                pos = 16 + len(f"] Filter: {filter_text}  [")
                self.stdscr.addstr(start_row + 1, pos, "T", curses.color_pair(2))
                self.stdscr.addstr(start_row + 1, pos + 1, "] Teleport", curses.color_pair(6))
            
            # View category with dynamic status like old version
            self.stdscr.addstr(start_row + 2, 2, "View:", curses.color_pair(1) | curses.A_BOLD)
            
            # Show current state and next action for items
            if self.items_view_mode == "normal":
                items_status = "Normal → Expand"
            elif self.items_view_mode == "expanded":
                items_status = "Expanded → Collapse"
            else:
                items_status = "Collapsed → Normal"
                
            # Show current state and next action for selected
            if self.selected_view_mode == "normal":
                selected_status = "Normal → Expand"
            elif self.selected_view_mode == "expanded":
                selected_status = "Expanded → Collapse"
            else:
                selected_status = "Collapsed → Normal"
            
            self.stdscr.addstr(start_row + 2, 14, "[", curses.color_pair(6))
            self.stdscr.addstr(start_row + 2, 15, "I", curses.color_pair(2))
            self.stdscr.addstr(start_row + 2, 16, f"] Items ({items_status})  [", curses.color_pair(6))
            pos = 16 + len(f"] Items ({items_status})  [")
            self.stdscr.addstr(start_row + 2, pos, "V", curses.color_pair(2))
            self.stdscr.addstr(start_row + 2, pos + 1, f"] Selected ({selected_status})", curses.color_pair(6))
            
            # Actions category
            self.stdscr.addstr(start_row + 3, 2, "Actions:", curses.color_pair(1) | curses.A_BOLD)
            self.stdscr.addstr(start_row + 3, 14, "[", curses.color_pair(6))
            self.stdscr.addstr(start_row + 3, 15, "Enter", curses.color_pair(2))
            self.stdscr.addstr(start_row + 3, 20, "] Confirm  [", curses.color_pair(6))
            self.stdscr.addstr(start_row + 3, 32, "S", curses.color_pair(2))
            self.stdscr.addstr(start_row + 3, 33, "] Switch  [", curses.color_pair(6))
            self.stdscr.addstr(start_row + 3, 44, "Q", curses.color_pair(2))
            self.stdscr.addstr(start_row + 3, 45, "] Back", curses.color_pair(6))
            
            # Selection count at the end
            self.stdscr.addstr(start_row + 3, 55, f"Selected: {len(self.selected_items)}", curses.color_pair(7) | curses.A_BOLD)
            
            # Show current cursor item path (especially useful for unlock mode)
            if self.items and 0 <= self.cursor_pos < len(self.items):
                cursor_item_path = self.items[self.cursor_pos]['path']
                self.stdscr.addstr(start_row + 4, 2, "Current Item Path:", curses.color_pair(1) | curses.A_BOLD)
                # Show full path - truncate if too long for screen
                max_path_width = width - 25  # Leave space for label
                if len(cursor_item_path) > max_path_width:
                    # Show beginning and end of path
                    path_display = cursor_item_path[:max_path_width//2-3] + "..." + cursor_item_path[-(max_path_width//2):]
                else:
                    path_display = cursor_item_path
                self.stdscr.addstr(start_row + 4, 22, path_display, curses.color_pair(6))
            
        except curses.error:
            pass
    
    def go_back(self) -> bool:
        """Go back to parent directory"""
        parent = os.path.dirname(self.current_dir)
        if parent != self.current_dir:
            self.current_dir = parent
            self.load_directory()
            self.cursor_pos = 0
            return True
        return False
    
    def enter_folder(self) -> bool:
        """Enter the currently selected folder"""
        if 0 <= self.cursor_pos < len(self.items):
            current_item = self.items[self.cursor_pos]
            if current_item['type'] == 'folder':
                folder_path = current_item['path']
                self.current_dir = folder_path
                self.load_directory()
                self.cursor_pos = 0
                return True
        return False
    
    def select_files(self) -> List[str]:
        """Main file selection loop with responsive interface"""
        while self.running:
            self.draw_interface()
            
            # Get input
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif key == curses.KEY_DOWN:
                self.cursor_pos = min(len(self.items) - 1, self.cursor_pos + 1)
            elif key == ord(' '):  # Space - toggle selection
                if self.cursor_pos < len(self.items):
                    item_path = self.items[self.cursor_pos]['path']
                    is_locked = self.mode == "lock" and item_path in self.locked_paths
                    if not is_locked:
                        if item_path in self.selected_items:
                            self.selected_items.remove(item_path)
                        else:
                            self.selected_items.add(item_path)
            elif key == ord('\n') or key == ord('\r'):  # Enter - confirm
                if self.selected_items:
                    return list(self.selected_items)
            elif key == ord('q') or key == ord('Q'):  # Quit
                return []
            elif key == ord('a') or key == ord('A'):  # Select all
                for item in self.items:
                    is_locked = self.mode == "lock" and item['path'] in self.locked_paths
                    if not is_locked:
                        self.selected_items.add(item['path'])
            elif key == ord('n') or key == ord('N'):  # Clear all
                self.selected_items.clear()
            elif key == ord('s') or key == ord('S'):  # Switch modes
                if self.mode == "lock":
                    return ['__SWITCH_TO_UNLOCK__']
                else:
                    return ['__SWITCH_TO_LOCK__']
            elif key == ord('t') or key == ord('T'):  # Teleport
                return ['__TELEPORT__']
            elif key == ord('i') or key == ord('I'):  # Cycle items view
                if self.items_view_mode == "normal":
                    self.items_view_mode = "expanded"
                elif self.items_view_mode == "expanded":
                    self.items_view_mode = "collapsed"
                else:
                    self.items_view_mode = "normal"
            elif key == ord('v') or key == ord('V'):  # Cycle selected view
                if self.selected_view_mode == "normal":
                    self.selected_view_mode = "expanded"
                elif self.selected_view_mode == "expanded":
                    self.selected_view_mode = "collapsed"
                else:
                    self.selected_view_mode = "normal"
            elif key == ord('d') or key == ord('D'):  # Toggle filter (unlock mode)
                if self.mode == "unlock":
                    self.unlock_filter_mode = "all" if self.unlock_filter_mode == "current" else "current"
                    return ['__REFILTER__']
            elif key == ord('b') or key == ord('B'):  # Go back (lock mode)
                if self.mode == "lock":
                    self.go_back()
            elif key == ord('f') or key == ord('F'):  # Enter folder (lock mode)
                if self.mode == "lock":
                    self.enter_folder()
            elif key >= ord('1') and key <= ord('9'):  # Quick select
                idx = key - ord('1')
                if 0 <= idx < len(self.items):
                    self.cursor_pos = idx
                    item_path = self.items[idx]['path']
                    is_locked = self.mode == "lock" and item_path in self.locked_paths
                    if not is_locked:
                        if item_path in self.selected_items:
                            self.selected_items.remove(item_path)
                        else:
                            self.selected_items.add(item_path)
        
        return []
    
    def select_from_list(self, items: List[Dict], title: str = "Select Items") -> List[str]:
        """Select from a predefined list of items (for unlock mode)"""
        # Convert locked items format to display format and apply filtering
        self.items = self.filter_locked_items(items)
        self.cursor_pos = 0
        self.selected_items = set()
        
        # If no items after filtering, show appropriate message
        if not self.items:
            return self.handle_empty_unlock_list()
        
        return self.select_files()
    
    def filter_locked_items(self, locked_items: List[Dict]) -> List[Dict]:
        """Filter and convert locked items based on current filter mode"""
        filtered_items = []
        
        for item in locked_items:
            # Apply directory filter
            if self.unlock_filter_mode == "current":
                # Only show items in current directory - normalize paths for comparison
                item_dir = os.path.normpath(os.path.dirname(item['path']))
                current_dir_norm = os.path.normpath(self.current_dir)
                if item_dir != current_dir_norm:
                    continue
            
            # Convert to display format
            try:
                # Get file stats for size and date
                if os.path.exists(item['path']):
                    stat = os.stat(item['path'])
                    size_mb = stat.st_size / (1024 * 1024)
                    dt = datetime.fromtimestamp(stat.st_mtime)
                    modified = dt.strftime('%d-%b-%Y %I:%M %p')
                else:
                    # File might be locked and inaccessible
                    size_mb = 0
                    modified = "Unknown"
                
                # Determine icon
                icon = "📁" if item['type'] == 'folder' else "📄"
                
                filtered_items.append({
                    'name': item['name'],
                    'path': item['path'],
                    'type': item['type'],
                    'icon': icon,
                    'size_mb': size_mb,
                    'modified': modified,
                    'is_dir': item['type'] == 'folder'
                })
            except (OSError, PermissionError):
                # Add item even if we can't get stats (it's locked)
                filtered_items.append({
                    'name': item['name'],
                    'path': item['path'],
                    'type': item['type'],
                    'icon': "📁" if item['type'] == 'folder' else "📄",
                    'size_mb': 0,
                    'modified': "Locked",
                    'is_dir': item['type'] == 'folder'
                })
        
        return filtered_items
    
    def handle_empty_unlock_list(self) -> List[str]:
        """Handle empty unlock list with proper user feedback"""
        # Show a message screen using curses
        self.stdscr.clear()
        height, width = self.get_terminal_size()
        
        try:
            # Header
            self.stdscr.addstr(2, 2, "╭─ ", curses.color_pair(1))
            self.stdscr.addstr(2, 5, "🔓 Unlock Items", curses.color_pair(1) | curses.A_BOLD)
            self.stdscr.addstr(3, 2, "╰" + "─" * 60, curses.color_pair(1))
            
            # Message based on filter mode
            if self.unlock_filter_mode == "current":
                msg1 = "No locked items found in current directory."
                msg2 = f"Current directory: {self.current_dir}"
                msg3 = "Press [D] to show all locations, or [Q] to quit."
            else:
                msg1 = "No locked items found in any location."
                msg2 = "All files and folders are currently unlocked."
                msg3 = "Press [Q] to return to main menu."
            
            # Center the messages
            start_row = height // 2 - 2
            self.stdscr.addstr(start_row, (width - len(msg1)) // 2, msg1, curses.color_pair(7))
            self.stdscr.addstr(start_row + 1, (width - len(msg2)) // 2, msg2, curses.color_pair(6))
            self.stdscr.addstr(start_row + 3, (width - len(msg3)) // 2, msg3, curses.color_pair(2))
            
            self.stdscr.refresh()
            
            # Wait for user input
            while True:
                key = self.stdscr.getch()
                if key == ord('q') or key == ord('Q'):
                    return []
                elif key == ord('d') or key == ord('D'):
                    if self.unlock_filter_mode == "current":
                        return ['__REFILTER__']
                elif key == ord('s') or key == ord('S'):
                    return ['__SWITCH_TO_LOCK__']
                    
        except curses.error:
            pass
        
        return []


def show_file_browser(current_dir: str = None, mode: str = "lock", locked_paths: Set[str] = None) -> List[str]:
    """Show curses file browser"""
    def _selector_wrapper(stdscr):
        selector = CursesFileBrowser(stdscr, current_dir, mode, locked_paths)
        return selector.select_files()
    
    try:
        return curses.wrapper(_selector_wrapper)
    except Exception:
        return []


def show_unlock_browser(items: List[Dict], title: str = "Select Items to Unlock", current_dir: str = None, filter_mode: str = "current") -> List[str]:
    """Show curses file browser for unlock mode"""
    def _selector_wrapper(stdscr):
        selector = CursesFileBrowser(stdscr, current_dir=current_dir or os.getcwd(), mode="unlock")
        selector.unlock_filter_mode = filter_mode  # Set the filter mode
        return selector.select_from_list(items, title)
    
    try:
        return curses.wrapper(_selector_wrapper)
    except Exception:
        return []