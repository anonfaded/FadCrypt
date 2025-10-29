"""
Interactive File Selector

Allows users to select files/folders with checkboxes in TUI.
"""

import os
import sys
from typing import List, Dict, Optional

from .colors import Colors, print_error


class FileSelector:
    """Interactive file/folder selector with checkboxes"""
    
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
                
                items.append({
                    'name': entry,
                    'path': full_path,
                    'type': 'folder' if is_dir else 'file',
                    'icon': Colors.ICON_FOLDER if is_dir else Colors.ICON_FILE
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
        
        # Header
        print(f"{Colors.BORDER}╭─ {Colors.TITLE}Select Files/Folders to Lock{Colors.RESET}")
        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.INFO}Current directory: {Colors.HIGHLIGHT}{self.current_dir}{Colors.RESET}")
        print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}\n")
        
        # Items box
        print(f"{Colors.BORDER}╭─ {Colors.TITLE}ITEMS{Colors.RESET}")
        
        if not self.items:
            print(f"{Colors.BORDER}│{Colors.RESET} {Colors.DIM}No items found{Colors.RESET}")
        else:
            # Display items (max 15 visible)
            start_idx = max(0, self.cursor_pos - 7)
            end_idx = min(len(self.items), start_idx + 15)
            
            for i in range(start_idx, end_idx):
                item = self.items[i]
                is_selected = item['path'] in self.selected_items
                is_cursor = i == self.cursor_pos
                
                # Checkbox
                checkbox = Colors.CHECKBOX_CHECKED if is_selected else Colors.CHECKBOX_UNCHECKED
                
                # Item text
                icon = item['icon']
                name = item['name']
                if len(name) > 45:
                    name = name[:42] + '...'
                
                # Highlight cursor position
                cursor_indicator = f"{Colors.SUCCESS}❯{Colors.RESET}" if is_cursor else " "
                print(f"{Colors.BORDER}│{Colors.RESET}{cursor_indicator} {checkbox} {icon} {Colors.TEXT}{name}{Colors.RESET}")
        
        print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}")
        
        # Help text
        print(f"\n{Colors.INFO}Commands: {Colors.DIM}[u/d] Navigate  [s] Select  [e] Confirm  [b] Back  [q] Quit{Colors.RESET}")
        print(f"{Colors.INFO}Selected: {Colors.HIGHLIGHT}{len(self.selected_items)} items{Colors.RESET}\n")
    
    def select_files(self) -> List[str]:
        """
        Run interactive file selector.
        
        Returns:
            List of selected file paths
        """
        self.items = self.scan_directory()
        
        if not self.items:
            print_error("No files or folders found in current directory.")
            return []
        
        # Simple input-based selection (works everywhere)
        while True:
            self.display_selector()
            
            print(f"{Colors.PRIMARY}Enter command:")
            print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
            try:
                cmd = input().strip().lower()
            except KeyboardInterrupt:
                print()
                return []
            
            if cmd == 'q':
                return []
            elif cmd == 'b':
                # Go back to parent directory
                parent = os.path.dirname(self.current_dir)
                if parent != self.current_dir:
                    self.current_dir = parent
                    self.items = self.scan_directory()
                    self.cursor_pos = 0
            elif cmd == 'up' or cmd == 'u':
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif cmd == 'down' or cmd == 'd':
                self.cursor_pos = min(len(self.items) - 1, self.cursor_pos + 1)
            elif cmd == 'space' or cmd == 's' or cmd == '':
                # Toggle selection
                if 0 <= self.cursor_pos < len(self.items):
                    item_path = self.items[self.cursor_pos]['path']
                    if item_path in self.selected_items:
                        self.selected_items.remove(item_path)
                    else:
                        self.selected_items.add(item_path)
                    # Move to next item
                    self.cursor_pos = min(len(self.items) - 1, self.cursor_pos + 1)
            elif cmd == 'enter' or cmd == 'e':
                # Confirm selection
                return list(self.selected_items)
            elif cmd.isdigit():
                # Select by number
                idx = int(cmd) - 1
                if 0 <= idx < len(self.items):
                    self.cursor_pos = idx
                    item_path = self.items[idx]['path']
                    if item_path in self.selected_items:
                        self.selected_items.remove(item_path)
                    else:
                        self.selected_items.add(item_path)
            elif cmd == 'a':
                # Select all
                for item in self.items:
                    self.selected_items.add(item['path'])
            elif cmd == 'n':
                # Deselect all
                self.selected_items.clear()
    
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
        
        while True:
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Header
            print(f"{Colors.BORDER}╭─ {Colors.TITLE}{title}{Colors.RESET}")
            print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}\n")
            
            # Items
            print(f"{Colors.BORDER}╭─ {Colors.TITLE}ITEMS{Colors.RESET}")
            
            for i, item in enumerate(self.items):
                is_selected = item['path'] in self.selected_items
                is_cursor = i == self.cursor_pos
                
                checkbox = Colors.CHECKBOX_CHECKED if is_selected else Colors.CHECKBOX_UNCHECKED
                icon = Colors.ICON_FOLDER if item['type'] == 'folder' else Colors.ICON_FILE
                name = item['name']
                if len(name) > 45:
                    name = name[:42] + '...'
                
                cursor_indicator = f"{Colors.SUCCESS}❯{Colors.RESET}" if is_cursor else " "
                print(f"{Colors.BORDER}│{Colors.RESET}{cursor_indicator} {checkbox} {icon} {Colors.TEXT}{name}{Colors.RESET}")
            
            print(f"{Colors.BORDER}╰──────────────────────────────────────────────────────────────{Colors.RESET}")
            
            # Help
            print(f"\n{Colors.INFO}Commands: {Colors.DIM}[u/d] Navigate  [s] Select  [e] Confirm  [q] Quit{Colors.RESET}")
            print(f"{Colors.INFO}Selected: {Colors.HIGHLIGHT}{len(self.selected_items)} items{Colors.RESET}\n")
            
            print(f"{Colors.PRIMARY}Enter command:")
            print(f" {Colors.SUCCESS}❯{Colors.RESET} ", end='')
            try:
                cmd = input().strip().lower()
            except KeyboardInterrupt:
                print()
                return []
            
            if cmd == 'q':
                return []
            elif cmd == 'up' or cmd == 'u':
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif cmd == 'down' or cmd == 'd':
                self.cursor_pos = min(len(self.items) - 1, self.cursor_pos + 1)
            elif cmd == 'space' or cmd == 's' or cmd == '':
                if 0 <= self.cursor_pos < len(self.items):
                    item_path = self.items[self.cursor_pos]['path']
                    if item_path in self.selected_items:
                        self.selected_items.remove(item_path)
                    else:
                        self.selected_items.add(item_path)
                    self.cursor_pos = min(len(self.items) - 1, self.cursor_pos + 1)
            elif cmd == 'enter' or cmd == 'e':
                return list(self.selected_items)
            elif cmd.isdigit():
                idx = int(cmd) - 1
                if 0 <= idx < len(self.items):
                    self.cursor_pos = idx
                    item_path = self.items[idx]['path']
                    if item_path in self.selected_items:
                        self.selected_items.remove(item_path)
                    else:
                        self.selected_items.add(item_path)
            elif cmd == 'a':
                for item in self.items:
                    self.selected_items.add(item['path'])
            elif cmd == 'n':
                self.selected_items.clear()
