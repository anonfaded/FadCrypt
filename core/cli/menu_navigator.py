"""
Menu Navigator

Provides arrow-key navigation for menus with consistent UI using curses.
"""

from typing import List, Dict, Optional, Callable
from .curses_menu import show_curses_menu





class MenuNavigator:
    """Interactive menu navigator using curses"""
    
    def __init__(self):
        """Initialize menu navigator"""
        pass
    
    def show_menu(self, title: str, items: List[Dict], header_func: Optional[Callable] = None) -> Optional[str]:
        """
        Show interactive menu with arrow navigation using curses.
        
        Args:
            title: Menu title
            items: List of menu items with 'key', 'icon', 'text', 'action' keys
            header_func: Optional function to display header
        
        Returns:
            Selected item key or None if cancelled
        """
        # If header_func is provided, call it first (it will print to terminal)
        # Then immediately launch curses which will take over the screen
        if header_func:
            try:
                header_func()
            except:
                pass
        
        # Use curses menu
        return show_curses_menu(title, items)