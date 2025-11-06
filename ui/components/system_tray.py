"""System Tray Icon Component for FadCrypt"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSignal, QObject
import os


class SystemTray(QObject):
    """System tray icon with context menu for background operation"""
    
    # Signals
    show_window_requested = pyqtSignal()
    hide_window_requested = pyqtSignal()
    start_monitoring_requested = pyqtSignal()
    stop_monitoring_requested = pyqtSignal()
    snake_game_requested = pyqtSignal()
    stats_requested = pyqtSignal()
    fadguide_requested = pyqtSignal()
    exit_requested = pyqtSignal()
    
    def __init__(self, resource_path_func, parent=None):
        super().__init__(parent)
        self.resource_path = resource_path_func
        self.tray_icon = None
        self.monitoring_active = False
        self.protection_percentage = 0
        self.locked_items_count = 0
        self.unlock_count = 0
        
        self.init_tray()
    
    def init_tray(self):
        """Initialize the system tray icon"""
        # Create tray icon
        icon_path = self.resource_path('img/icon.png')
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
        else:
            # Fallback to default icon
            icon = QIcon.fromTheme('application-x-executable')
        
        self.tray_icon = QSystemTrayIcon(icon, self.parent())
        self.tray_icon.setToolTip('FadCrypt - Application Lock')
        
        # Create context menu
        self.create_menu()
        
        # Connect signals
        self.tray_icon.activated.connect(self.on_tray_activated)
    
    def create_menu(self):
        """Create the context menu for system tray"""
        menu = QMenu()
        
        # Show Window action
        self.show_action = QAction('Show Window', self)
        self.show_action.triggered.connect(self.show_window_requested.emit)
        menu.addAction(self.show_action)
        
        # Note: Hide Window removed - window auto-hides when monitoring starts
        # and user should use system tray to manage, not manually hide
        
        menu.addSeparator()
        
        # Start/Stop Monitoring actions
        self.start_monitoring_action = QAction('▶ Start Monitoring', self)
        self.start_monitoring_action.triggered.connect(self.start_monitoring_requested.emit)
        menu.addAction(self.start_monitoring_action)
        
        self.stop_monitoring_action = QAction('⏹ Stop Monitoring', self)
        self.stop_monitoring_action.triggered.connect(self.stop_monitoring_requested.emit)
        self.stop_monitoring_action.setEnabled(False)
        menu.addAction(self.stop_monitoring_action)
        
        menu.addSeparator()
        
        # Snake Game action
        snake_action = QAction('🐍 Snake Game', self)
        snake_action.triggered.connect(self.snake_game_requested.emit)
        menu.addAction(snake_action)
        
        # Stats action
        self.stats_action = QAction('📊 Statistics & Activity', self)
        self.stats_action.triggered.connect(self.stats_requested.emit)
        menu.addAction(self.stats_action)
        
        # FadGuide action
        fadguide_action = QAction('📖 FadGuide - CLI Reference', self)
        fadguide_action.triggered.connect(self.fadguide_requested.emit)
        menu.addAction(fadguide_action)
        
        menu.addSeparator()
        
        # Exit action
        exit_action = QAction('Exit FadCrypt', self)
        exit_action.triggered.connect(self.exit_requested.emit)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
    
    def show(self):
        """Show the system tray icon"""
        if self.tray_icon:
            self.tray_icon.show()
            print("✅ System tray icon shown")
    
    def hide(self):
        """Hide the system tray icon"""
        if self.tray_icon:
            self.tray_icon.hide()
            print("❌ System tray icon hidden")
    
    def set_monitoring_active(self, active: bool):
        """Update tray icon state based on monitoring status"""
        self.monitoring_active = active
        
        if active:
            self.tray_icon.setToolTip('FadCrypt - Monitoring Active 🔒')
            self.start_monitoring_action.setEnabled(False)
            self.stop_monitoring_action.setEnabled(True)
            print("🔒 System tray: Monitoring ACTIVE")
        else:
            self.tray_icon.setToolTip('FadCrypt - Application Lock')
            self.start_monitoring_action.setEnabled(True)
            self.stop_monitoring_action.setEnabled(False)
            print("🔓 System tray: Monitoring INACTIVE")
    
    def update_stats_display(self, protection_percentage: int, locked_items_count: int, unlock_count: int = 0):
        """Update tray tooltip with live protection stats"""
        self.protection_percentage = protection_percentage
        self.locked_items_count = locked_items_count
        self.unlock_count = unlock_count
        
        # Format tooltip with stats
        if self.monitoring_active:
            tooltip = (
                f'FadCrypt - Monitoring Active 🔒\n'
                f'Protected: {locked_items_count} items ({protection_percentage}%)\n'
                f'Unlocks today: {unlock_count}'
            )
        else:
            tooltip = (
                f'FadCrypt - Ready to Monitor\n'
                f'Protected: {locked_items_count} items ({protection_percentage}%)\n'
                f'Unlocks today: {unlock_count}'
            )
        
        self.tray_icon.setToolTip(tooltip)
    
    def show_message(self, title: str, message: str, icon=QSystemTrayIcon.MessageIcon.Information):
        """Show a notification message"""
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, icon, 3000)
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation (click, double-click)"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - toggle window visibility
            self.show_window_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double click - show window
            self.show_window_requested.emit()
