"""Base Main Window for FadCrypt PyQt6 UI"""

import sys
import os
import json
import webbrowser
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QMessageBox, QPushButton, QFrame, QScrollArea, QTextEdit, 
    QFileDialog, QSystemTrayIcon, QMenu, QApplication
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRegularExpression
from PyQt6.QtGui import QIcon, QPixmap, QFont, QFontDatabase, QSyntaxHighlighter, QTextCharFormat, QColor

from ui.components.app_list_widget import AppListWidget
from ui.components.button_panel import ButtonPanel
from ui.components.settings_panel import SettingsPanel
from ui.components.about_panel import AboutPanel
from ui.dialogs.readme_dialog import ReadmeDialog
from ui.dialogs.password_dialog import ask_password

# Import core managers
from core.crypto_manager import CryptoManager
from core.password_manager import PasswordManager
from core.config_manager import ConfigManager
from core.application_manager import ApplicationManager
from core.activity_manager import ActivityManager
from core.statistics_manager import StatisticsManager
from core.file_protection import get_file_protection_manager

# Import version info
from version import __version__, __version_code__


class JsonSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JSON with dark theme colors"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Define formats for different JSON elements
        self.formats = {}
        
        # Keys (blue)
        key_format = QTextCharFormat()
        key_format.setForeground(QColor("#61afef"))  # Blue
        self.formats['key'] = key_format
        
        # String values (green)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#98c379"))  # Green
        self.formats['string'] = string_format
        
        # Numbers (orange)
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#d19a66"))  # Orange
        self.formats['number'] = number_format
        
        # Booleans and null (purple)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#c678dd"))  # Purple
        self.formats['keyword'] = keyword_format
        
        # Braces and brackets (white)
        brace_format = QTextCharFormat()
        brace_format.setForeground(QColor("#abb2bf"))  # Light gray
        self.formats['brace'] = brace_format
        
    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text"""
        # Highlight JSON keys (text before colon in quotes)
        key_pattern = QRegularExpression(r'"([^"]+)"\s*:')
        iterator = key_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats['key'])
        
        # Highlight string values (text in quotes after colon)
        string_pattern = QRegularExpression(r':\s*"([^"]*)"')
        iterator = string_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            start = match.capturedStart() + text[match.capturedStart():].index('"')
            length = match.capturedEnd() - start
            self.setFormat(start, length, self.formats['string'])
        
        # Highlight numbers
        number_pattern = QRegularExpression(r'\b\d+\.?\d*\b')
        iterator = number_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats['number'])
        
        # Highlight booleans and null
        keyword_pattern = QRegularExpression(r'\b(true|false|null)\b')
        iterator = keyword_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats['keyword'])
        
        # Highlight braces and brackets
        brace_pattern = QRegularExpression(r'[{}[\],]')
        iterator = brace_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats['brace'])


class MainWindowBase(QMainWindow):
    """
    Base main window class for FadCrypt application.
    
    This class provides the foundation for the FadCrypt UI with:
    - Main window setup (title, icon, geometry)
    - Menu bar structure
    - Tab widget for organizing features
    - Complete UI matching Tkinter version (banner, footer, all tabs)
    - Resource path handling for images
    """
    
    # Class-level signal for thread-safe password prompts
    password_prompt_requested = pyqtSignal(str, str)
    file_access_requested = pyqtSignal(str)  # Signal for file access from background thread
    
    def __init__(self, version=None):
        super().__init__()
        self.version = version or __version__
        self.version_code = __version_code__
        self.monitoring_active = False
        
        # Initialize log capture FIRST (before any logging)
        from ui.components.logs_tab_widget import LogCapture
        self.log_capture = LogCapture()
        self.log_capture.start()  # Start capturing all output
        
        # Flag to track if we're doing a forced exit (Ctrl+C, etc.)
        self._force_quit = False
        
        # Initialize settings (will be loaded from JSON later)
        self.password_dialog_style = "simple"
        self.wallpaper_choice = "default"
        
        # Initialize core managers - simplified for now
        self.crypto_manager = CryptoManager()
        
        # Password file path - use platform-specific folder
        fadcrypt_folder = self.get_fadcrypt_folder()
        password_file = os.path.join(fadcrypt_folder, "encrypted_password.bin")
        recovery_codes_file = os.path.join(fadcrypt_folder, "recovery_codes.json")
        
        self.password_manager = PasswordManager(
            password_file,
            self.crypto_manager,
            recovery_codes_file
        )
        
        # Initialize file lock manager (platform-specific)
        self.file_lock_manager = self.get_file_lock_manager(fadcrypt_folder)
        
        # Set password callback for fanotify (Linux)
        if self.file_lock_manager and hasattr(self.file_lock_manager, 'set_password_callback'):
            self.file_lock_manager.set_password_callback(self._handle_file_access_permission)
            print("✅ Fanotify password callback set (Linux)")
        
        # Log important paths at startup
        print("\n📁 FadCrypt File Locations:")
        print(f"   Main Config Folder: {fadcrypt_folder}")
        print(f"   Password File: {password_file}")
        print(f"   Config File: {os.path.join(fadcrypt_folder, 'apps_config.json')}")
        print(f"   Settings File: {os.path.join(fadcrypt_folder, 'settings.json')}")
        print(f"   State File: {os.path.join(fadcrypt_folder, 'monitoring_state.json')}")
        if hasattr(self, 'get_backup_folder'):
            print(f"   Backup Folder: {self.get_backup_folder()}")
        print()
        
        # Config manager (will be fully integrated later)
        self.config_manager = None
        self.app_manager = None
        
        # Activity and Statistics managers
        self.activity_manager = ActivityManager(fadcrypt_folder)
        self.statistics_manager = StatisticsManager(fadcrypt_folder)
        
        # Stats window (created on demand)
        self.stats_window = None
        
        # Monitoring state
        self.monitoring_active = False
        self.unified_monitor = None
        self.pending_password_result = None
        self.auto_monitor_mode = False  # Set to True when launched with --auto-monitor flag
        
        # System tray (will be initialized after UI)
        self.system_tray = None
        
        # Load custom font
        self.load_custom_font()
        
        # Initialize UI
        # Initialize monitoring state
        self.monitoring_state = {
            'unlocked_apps': []
        }
        self.load_monitoring_state()
        
        self.init_ui()
        
        # NOTE: Crash recovery check is called LATER after auto_monitor_mode flag is set
        # See: FadCrypt.py - it sets window.auto_monitor_mode = True before calling check_crash_recovery()
        
        # Initialize system tray after UI
        self.init_system_tray()
        
        # Load settings from file (must be after UI is initialized)
        self.load_settings()
        
        # Connect password prompt signal (for thread-safe dialog)
        self.password_prompt_requested.connect(self.show_password_prompt_for_app_sync)
        
        # Connect settings signal
        self.settings_panel.settings_changed.connect(self.on_settings_changed)
        
        # Connect recovery codes button to handler
        self.settings_panel.on_generate_recovery_codes = self.on_generate_recovery_codes_clicked
        
        # Connect cleanup button to cleanup handler
        self.settings_panel.on_cleanup_clicked = self.cleanup_before_uninstall
        
        # Center window after everything is initialized
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.center_on_screen)
        
    def load_custom_font(self):
        """Load Ubuntu Regular font for the entire application"""
        font_path = self.resource_path('core/fonts/ubuntu_regular.ttf')
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    self.app_font_family = font_families[0]
                    # Set as default font for the application
                    font = QFont(self.app_font_family, 10)
                    from PyQt6.QtWidgets import QApplication
                    QApplication.instance().setFont(font)
                    print(f"✅ Loaded custom font: {self.app_font_family}")
                else:
                    print("⚠️ Font loaded but no families found")
                    self.app_font_family = "Ubuntu"
            else:
                print(f"⚠️ Failed to load font from {font_path}")
                self.app_font_family = "Ubuntu"
        else:
            print(f"⚠️ Font file not found at {font_path}")
            self.app_font_family = "Ubuntu"
        
    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
    
    def get_platform_name(self):
        """
        Get platform name for UI display.
        Override in subclasses to provide proper platform identification.
        
        Returns:
            str: "Windows" or "Linux"
        """
        import platform
        system = platform.system()
        if system == "Windows":
            return "Windows"
        elif system == "Linux":
            return "Linux"
        else:
            return "Linux"  # Default fallback
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(f"FadCrypt v{self.version}")
        
        # Set initial size
        self.resize(950, 700)
        
        # Set darker app-wide stylesheet with solid dark background
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f0f0f;
            }
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QTabWidget::pane {
                background-color: #1a1a1a;
                border: 1px solid #2a2a2a;
            }
            QTabBar::tab {
                background: transparent;
                color: #ffffff;
                padding: 10px 20px;
                border: 1px solid #2a2a2a;
            }
            QTabBar::tab:selected {
                background-color: rgba(42, 42, 42, 0.7);
                border-bottom: 3px solid #d32f2f;
            }
            QTabBar::tab:hover {
                background-color: rgba(40, 40, 40, 0.5);
            }
            QScrollArea {
                background-color: #1a1a1a;
                border: none;
            }
            QTextEdit, QPlainTextEdit {
                background-color: rgba(34, 34, 34, 0.8);
                color: #ffffff;
                border: 1px solid #333333;
            }
        """)
        
        # Set window icon
        icon_path = self.resource_path('img/icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Note: Menu bar removed - About tab provides all needed info
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create all tabs
        self.create_main_tab()
        self.create_applications_tab()
        self.create_logs_tab()  # Logs tab for viewing application output
        self.create_activity_logs_tab()  # Activity logs tab for audit trail
        self.create_config_tab()
        self.create_settings_tab()
        self.create_about_tab()
        
    
    def init_system_tray(self):
        """Initialize system tray icon"""
        from ui.components.system_tray import SystemTray
        
        self.system_tray = SystemTray(self.resource_path, self)
        
        # Connect system tray signals
        self.system_tray.show_window_requested.connect(self.show_window_from_tray)
        self.system_tray.start_monitoring_requested.connect(self.on_start_monitoring)
        self.system_tray.stop_monitoring_requested.connect(self.on_stop_monitoring)
        self.system_tray.snake_game_requested.connect(self.on_snake_game)
        self.system_tray.stats_requested.connect(self.open_stats_window)
        self.system_tray.exit_requested.connect(self.on_exit_requested)
        
        # Show tray icon
        self.system_tray.show()
        
        print("✅ System tray initialized")
    
    def show_window_from_tray(self):
        """Show window from system tray - requires password if monitoring is active"""
        if self.monitoring_active:
            # Ask for password with recovery option
            if self.verify_password_with_recovery(
                "Show Window",
                "Enter your password to show the window:"
            ):
                self.show()
                self.activateWindow()
                self.raise_()
            else:
                if self.system_tray:
                    self.system_tray.show_message(
                        "Access Denied",
                        "Window remains hidden.",
                        QSystemTrayIcon.MessageIcon.Warning
                    )
        else:
            # Not monitoring, show without password
            self.show()
            self.activateWindow()
            self.raise_()
    
    def hide_to_tray(self):
        """Hide window to system tray"""
        self.hide()
        if self.system_tray:
            self.system_tray.show_message(
                "FadCrypt",
                "FadCrypt is running in the background.\nClick the tray icon to show the window.",
                QSystemTrayIcon.MessageIcon.Information
            )
    
    def closeEvent(self, event):
        """
        Override close event to minimize to tray instead of closing.
        Only allow true exit via tray menu "Exit FadCrypt" option or forced quit (Ctrl+C).
        """
        # If force quit flag is set (Ctrl+C), allow immediate exit
        if self._force_quit:
            event.accept()
            return
        
        # When window close button is clicked, minimize to tray instead
        event.ignore()  # Don't close the window
        self.hide_to_tray()
        print("📌 Window close button clicked - minimizing to tray")
    
    def on_exit_requested(self):
        """
        Handle exit request from system tray.
        Asks for password if monitoring is active (same as legacy).
        """
        if self.monitoring_active:
            # Ask for password when monitoring is active
            from ui.dialogs.password_dialog import ask_password
            password = ask_password(
                "Exit FadCrypt",
                "Enter your password to exit FadCrypt:",
                self.resource_path,
                style=self.password_dialog_style,
                wallpaper=self.wallpaper_choice,
                parent=self
            )
            if password and self.password_manager.verify_password(password):
                print("✅ Password verified - exiting FadCrypt")
                # Stop monitoring first
                if self.unified_monitor:
                    self.unified_monitor.stop_monitoring()
                # Unprotect critical files
                print("🔓 Unprotecting critical files on exit...")
                file_protection = get_file_protection_manager()
                file_protection.unprotect_all_files()
                # Really exit the application
                from PyQt6.QtWidgets import QApplication
                # Cleanup logs widget
                if hasattr(self, 'logs_tab_widget'):
                    self.logs_tab_widget.cleanup()
                QApplication.quit()
            else:
                print("❌ Incorrect password - exit cancelled")
                if self.system_tray:
                    self.system_tray.show_message(
                        "Access Denied",
                        "Incorrect password. FadCrypt remains running.",
                        QSystemTrayIcon.MessageIcon.Warning
                    )
        else:
            # Not monitoring, exit without password
            print("✅ Exiting FadCrypt (no monitoring active)")
            # Unprotect critical files (in case they were left protected)
            print("🔓 Unprotecting critical files on exit...")
            file_protection = get_file_protection_manager()
            file_protection.unprotect_all_files()
            from PyQt6.QtWidgets import QApplication
            # Cleanup logs widget
            if hasattr(self, 'logs_tab_widget'):
                self.logs_tab_widget.cleanup()
            QApplication.quit()
        
    def create_main_tab(self):
        """Create Main/Home tab with modern design"""
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Banner image at top (using banner-rounder.png)
        banner_path = self.resource_path('img/banner-rounded.png')
        if os.path.exists(banner_path):
            banner_label = QLabel()
            banner_pixmap = QPixmap(banner_path)
            # Resize to 700x200 like Tkinter
            scaled_pixmap = banner_pixmap.scaled(700, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            banner_label.setPixmap(scaled_pixmap)
            banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(banner_label)
        
        main_layout.addSpacing(20)
        
        # Centered buttons frame (Start Monitoring + Read Me) - compact design
        centered_buttons_layout = QHBoxLayout()
        centered_buttons_layout.addStretch()
        
        # Dynamic Monitoring Button (replaces separate Start/Stop buttons)
        self.monitoring_button = QPushButton("▶ Start Monitoring")
        self.monitoring_button.setFixedSize(180, 44)  # Consistent size
        self.monitoring_button.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 6px;
                border: none;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666666;
            }
        """)
        self.monitoring_button.clicked.connect(self.toggle_monitoring)
        centered_buttons_layout.addWidget(self.monitoring_button)
        
        centered_buttons_layout.addStretch()
        main_layout.addLayout(centered_buttons_layout)
        
        main_layout.addSpacing(20)
        
        # Content area with sidebar buttons
        content_layout = QHBoxLayout()
        
        # Left sidebar with compact vertical buttons
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(8)
        
        button_style = """
            QPushButton {
                background-color: #2a2a2a;
                color: white;
                font-weight: bold;
                padding: 8px 12px;
                border-radius: 5px;
                text-align: center;
                border: none;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:disabled {
                background-color: #1a1a1a;
                color: #555555;
            }
        """
        
        # DOCUMENTATION SECTION
        docs_label = QLabel("📖 Documentation")
        docs_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 11px;
                font-weight: bold;
                padding: 0px 0 6px 0;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
        """)
        sidebar_layout.addWidget(docs_label)
        
        readme_button = QPushButton("📄 Read Me")
        readme_button.setFixedWidth(180)
        readme_button.setStyleSheet(button_style)
        readme_button.clicked.connect(self.on_readme_clicked)
        sidebar_layout.addWidget(readme_button)
        
        sidebar_layout.addSpacing(10)
        
        # SECURITY SECTION
        security_label = QLabel("🔐 Security")
        security_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 11px;
                font-weight: bold;
                padding: 0px 0 6px 0;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
        """)
        sidebar_layout.addWidget(security_label)
        
        # Create Password button - only shown if no password exists
        self.create_pass_button = QPushButton("Create Password")
        self.create_pass_button.setFixedWidth(180)
        self.create_pass_button.setStyleSheet(button_style)
        self.create_pass_button.clicked.connect(self.on_create_password)
        sidebar_layout.addWidget(self.create_pass_button)
        
        # Change Password button - always visible
        self.change_pass_button = QPushButton("Change Password")
        self.change_pass_button.setFixedWidth(180)
        self.change_pass_button.setStyleSheet(button_style)
        self.change_pass_button.clicked.connect(self.on_change_password)
        sidebar_layout.addWidget(self.change_pass_button)
        
        sidebar_layout.addSpacing(10)
        
        # EXTRAS SECTION
        extras_label = QLabel("🎮 Extras")
        extras_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 11px;
                font-weight: bold;
                padding: 0px 0 6px 0;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
        """)
        sidebar_layout.addWidget(extras_label)
        
        snake_button = QPushButton("Snake Game 🪱")
        snake_button.setFixedWidth(180)
        snake_button.setStyleSheet("""
            QPushButton {
                background-color: #512da8;
                color: white;
                font-weight: bold;
                padding: 8px 12px;
                border-radius: 5px;
                text-align: center;
                border: none;
            }
            QPushButton:hover {
                background-color: #6a3ab2;
            }
        """)
        snake_button.clicked.connect(self.on_snake_game)
        sidebar_layout.addWidget(snake_button)
        
        stats_button = QPushButton("📊 Statistics")
        stats_button.setFixedWidth(180)
        stats_button.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                font-weight: bold;
                padding: 8px 12px;
                border-radius: 5px;
                text-align: center;
                border: none;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        stats_button.clicked.connect(self.open_stats_window)
        sidebar_layout.addWidget(stats_button)
        
        sidebar_layout.addStretch()
        
        # Update password button visibility based on password existence
        self.update_password_buttons_visibility()
        
        content_layout.addLayout(sidebar_layout)
        
        # Vertical separator
        separator_v = QFrame()
        separator_v.setFrameShape(QFrame.Shape.VLine)
        separator_v.setFrameShadow(QFrame.Shadow.Sunken)
        content_layout.addWidget(separator_v)
        
        # Right side - with background flag image at bottom
        right_layout = QVBoxLayout()
        right_layout.addStretch()
        
        # Add FadSec Lab flag image at bottom right
        flag_path = self.resource_path('img/fadseclab_flag.png')
        if os.path.exists(flag_path):
            flag_label = QLabel()
            flag_pixmap = QPixmap(flag_path)
            # Scale to reasonable size
            scaled_flag = flag_pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            flag_label.setPixmap(scaled_flag)
            flag_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
            flag_label.setStyleSheet("background-color: transparent;")
            right_layout.addWidget(flag_label)
        else:
            right_layout.addStretch()
        
        content_layout.addLayout(right_layout)
        
        main_layout.addLayout(content_layout)
        
        # Horizontal Separator before footer
        separator_h = QFrame()
        separator_h.setFrameShape(QFrame.Shape.HLine)
        separator_h.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator_h)
        
        # Footer with logo, branding, GitHub link
        footer_layout = QHBoxLayout()
        
        # Logo on left
        logo_path = self.resource_path('img/fadsec-main-footer.png')
        if os.path.exists(logo_path):
            logo_label = QLabel()
            logo_pixmap = QPixmap(logo_path)
            # Scale to 40% as in Tkinter
            scaled_logo = logo_pixmap.scaledToWidth(int(logo_pixmap.width() * 0.4), Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
            footer_layout.addWidget(logo_label)
        
        # Branding text
        branding_label = QLabel(" © 2024-2025 | faded.dev | Licensed under GPL 3.0")
        branding_label.setStyleSheet("color: gray; font-size: 12px;")
        footer_layout.addWidget(branding_label)
        
        footer_layout.addStretch()
        
        # GitHub link on right
        github_label = QLabel('<a href="https://github.com/anonfaded/FadCrypt" style="color: #FFD700; text-decoration: none;">⭐ Sponsor on GitHub</a>')
        github_label.setOpenExternalLinks(True)
        github_label.setStyleSheet("font-size: 12px;")
        footer_layout.addWidget(github_label)
        
        main_layout.addLayout(footer_layout)
        
        self.tabs.addTab(main_tab, "Main")
        
    def create_applications_tab(self):
        """Create Applications tab for managing locked apps"""
        from ui.components.app_grid_widget import AppGridWidget
        from PyQt6.QtWidgets import QLineEdit, QComboBox
        
        apps_tab = QWidget()
        apps_layout = QVBoxLayout(apps_tab)
        apps_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header with app count
        header_layout = QHBoxLayout()
        self.app_count_label = QLabel("Applications: 0")
        self.app_count_label.setStyleSheet("""
            color: #ffffff;
            font-size: 13pt;
            font-weight: bold;
        """)
        header_layout.addWidget(self.app_count_label)
        header_layout.addStretch()
        apps_layout.addLayout(header_layout)
        
        # Search and filter bar
        search_filter_layout = QHBoxLayout()
        search_filter_layout.setSpacing(10)
        
        # Search icon label
        search_icon = QLabel("🔎")
        search_icon.setStyleSheet("font-size: 16px; color: #888888;")
        search_filter_layout.addWidget(search_icon)
        
        # Search input
        self.app_search_input = QLineEdit()
        self.app_search_input.setPlaceholderText("Search applications by name or path...")
        self.app_search_input.textChanged.connect(self.filter_applications)
        self.app_search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #e5e7eb;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)
        search_filter_layout.addWidget(self.app_search_input, stretch=1)
        
        # Sort dropdown label
        sort_label = QLabel("Sort:")
        sort_label.setStyleSheet("color: #e5e7eb; font-size: 13px; padding-right: 8px;")
        search_filter_layout.addWidget(sort_label)
        
        self.app_sort_combo = QComboBox()
        self.app_sort_combo.addItems(["Name (A-Z)", "Name (Z-A)", "Recently Added", "Most Used"])
        self.app_sort_combo.currentTextChanged.connect(self.sort_applications)
        self.app_sort_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1a1a;
                color: #e5e7eb;
                border: 2px solid #333333;
                border-radius: 6px;
                padding: 8px 12px;
                padding-right: 35px;
                min-width: 140px;
                font-size: 12px;
            }
            QComboBox:hover {
                border: 2px solid #3b82f6;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
                padding-right: 8px;
            }
            QComboBox::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgMUw2IDdMMTEgMSIgc3Ryb2tlPSIjODg4ODg4IiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==);
                width: 12px;
                height: 8px;
            }
            QComboBox::down-arrow:hover {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgMUw2IDdMMTEgMSIgc3Ryb2tlPSIjZTVlN2ViIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==);
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                color: #e5e7eb;
                selection-background-color: #3b82f6;
                border: 1px solid #333333;
            }
        """)
        search_filter_layout.addWidget(self.app_sort_combo)
        
        # Clear search button
        self.clear_search_btn = QPushButton("✕")
        self.clear_search_btn.setToolTip("Clear search")
        self.clear_search_btn.clicked.connect(self.clear_search)
        self.clear_search_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #888888;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                min-width: 40px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                color: #e5e7eb;
            }
        """)
        search_filter_layout.addWidget(self.clear_search_btn)
        
        apps_layout.addLayout(search_filter_layout)
        
        # App grid widget (replaces simple list)
        self.app_list_widget = AppGridWidget()
        apps_layout.addWidget(self.app_list_widget)
        
        # Button panel
        self.button_panel = ButtonPanel()
        
        # Connect button panel signals
        self.button_panel.add_app_clicked.connect(self.add_application)
        self.button_panel.edit_app_clicked.connect(self.edit_application)
        self.button_panel.remove_app_clicked.connect(self.remove_application)
        self.button_panel.select_all_clicked.connect(self.select_all_apps)
        self.button_panel.deselect_all_clicked.connect(self.deselect_all_apps)
        
        # Connect app list widget signals
        self.app_list_widget.app_edited.connect(self.handle_app_edited)
        self.app_list_widget.app_removed.connect(self.handle_app_removed)
        self.app_list_widget.app_lock_toggled.connect(self.handle_lock_toggled)
        
        apps_layout.addWidget(self.button_panel)
        
        self.tabs.addTab(apps_tab, "Applications")
        
        # Load saved applications
        self.load_applications_config()
        
        # ============================================
        # FILES TAB - Protected Files & Folders
        # ============================================
        files_tab = QWidget()
        files_layout = QVBoxLayout(files_tab)
        files_layout.setContentsMargins(20, 20, 20, 20)
        files_layout.setSpacing(15)
        
        # Header
        files_header = QLabel("🔒 Protected Files & Folders")
        files_header.setStyleSheet("""
            QLabel {
                font-size: 18pt;
                font-weight: bold;
                color: #ffffff;
                padding: 10px;
            }
        """)
        files_layout.addWidget(files_header)
        
        # Description
        files_desc = QLabel(
            "Lock files and folders to prevent read, write, delete, or rename operations. "
            "Locked items are completely inaccessible until monitoring is stopped."
        )
        files_desc.setWordWrap(True)
        files_desc.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 10pt;
                padding: 5px;
            }
        """)
        files_layout.addWidget(files_desc)
        
        # File grid widget
        from ui.components.file_grid_widget import FileGridWidget
        self.file_grid_widget = FileGridWidget()
        files_layout.addWidget(self.file_grid_widget)
        
        # File action buttons
        file_buttons_layout = QHBoxLayout()
        file_buttons_layout.setSpacing(10)
        
        # Add File button (green)
        self.add_file_btn = QPushButton("📄 Add File")
        self.add_file_btn.clicked.connect(self.add_file)
        self.add_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        file_buttons_layout.addWidget(self.add_file_btn)
        
        # Add Folder button (blue)
        self.add_folder_btn = QPushButton("📁 Add Folder")
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.add_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        file_buttons_layout.addWidget(self.add_folder_btn)
        
        # Remove button
        self.remove_file_btn = QPushButton("🗑️  Remove")
        self.remove_file_btn.clicked.connect(self.remove_file_item)
        self.remove_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        file_buttons_layout.addWidget(self.remove_file_btn)
        
        file_buttons_layout.addStretch()
        files_layout.addLayout(file_buttons_layout)
        
        self.tabs.addTab(files_tab, "Protected Files")
        
        # Load locked files after widget is created
        self.load_locked_files()
    
    def create_logs_tab(self):
        """Create Logs tab for viewing real-time application logs"""
        from ui.components.logs_tab_widget import LogsTabWidget
        
        self.logs_tab_widget = LogsTabWidget(self.log_capture, self)
        self.tabs.addTab(self.logs_tab_widget, "Logs")
        
    def create_activity_logs_tab(self):
        """Create Activity Logs tab for viewing audit trail of lock/unlock events"""
        from ui.components.activity_logs_panel import ActivityLogsPanel
        
        activity_tab = QWidget()
        tab_layout = QVBoxLayout(activity_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        self.activity_logs_panel = ActivityLogsPanel(self.activity_manager, activity_tab)
        tab_layout.addWidget(self.activity_logs_panel)
        
        self.tabs.addTab(activity_tab, "Activity")
        
    def create_config_tab(self):
        """Create Config tab for viewing encrypted apps list"""
        config_tab = QWidget()
        
        # Scrollable content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        config_layout = QVBoxLayout(scroll_content)
        config_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title_label = QLabel("Config File")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        config_layout.addWidget(title_label)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        config_layout.addWidget(separator1)
        
        # Config text display
        self.config_text = QTextEdit()
        self.config_text.setReadOnly(True)
        self.config_text.setMinimumHeight(300)
        self.config_text.setPlaceholderText("No config yet. Add applications or lock files to create config...")
        
        # Apply JSON syntax highlighting
        self.json_highlighter = JsonSyntaxHighlighter(self.config_text.document())
        
        # Set dark background for better contrast with syntax colors
        self.config_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #abb2bf;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11pt;
            }
        """)
        
        config_layout.addWidget(self.config_text)
        
        # Description
        desc_label = QLabel(
            "This is the unified configuration containing all locked applications and files/folders.\n"
            "It is displayed in plain text here for your convenience, "
            "but rest assured, the data is encrypted when saved on your computer,\n"
            "keeping your locked items confidential."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: gray;")
        config_layout.addWidget(desc_label)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        config_layout.addWidget(separator2)
        
        # Export/Import section
        export_title = QLabel("Backup & Restore Configurations")
        export_title.setStyleSheet("font-weight: bold;")
        config_layout.addWidget(export_title)
        
        export_desc = QLabel("Export your complete configuration (applications + locked files/folders) or import a previously saved configuration.")
        export_desc.setWordWrap(True)
        export_desc.setStyleSheet("color: gray;")
        config_layout.addWidget(export_desc)
        
        # Export/Import buttons
        button_layout = QHBoxLayout()
        
        export_button = QPushButton("Export Config")
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        export_button.clicked.connect(self.on_export_config)
        button_layout.addWidget(export_button)
        
        import_button = QPushButton("Import Config")
        import_button.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        import_button.clicked.connect(self.on_import_config)
        button_layout.addWidget(import_button)
        
        button_layout.addStretch()
        config_layout.addLayout(button_layout)
        
        # Separator
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.Shape.HLine)
        separator3.setFrameShadow(QFrame.Shadow.Sunken)
        config_layout.addWidget(separator3)
        
        # File Locations Section
        locations_title = QLabel("📁 File Locations")
        locations_title.setStyleSheet("font-weight: bold; font-size: 11pt;")
        config_layout.addWidget(locations_title)
        
        locations_desc = QLabel("Click on any path to open in file manager. Right-click to copy to clipboard.")
        locations_desc.setWordWrap(True)
        locations_desc.setStyleSheet("color: gray; font-size: 9pt;")
        config_layout.addWidget(locations_desc)
        
        # Create clickable path labels
        from PyQt6.QtGui import QCursor
        import subprocess
        
        def create_path_label(label_text, path):
            """Create a clickable path label with context menu"""
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(10, 5, 10, 5)
            
            # Label text
            name_label = QLabel(label_text)
            name_label.setStyleSheet("color: #e5e7eb; font-weight: bold;")
            layout.addWidget(name_label)
            
            # Path label (clickable)
            path_label = QLabel(path)
            path_label.setStyleSheet("""
                QLabel {
                    color: #3b82f6;
                    text-decoration: underline;
                }
                QLabel:hover {
                    color: #60a5fa;
                }
            """)
            path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            path_label.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Click handler to open in file manager
            def open_in_file_manager():
                try:
                    if sys.platform.startswith('win'):
                        # Windows: open in Explorer
                        if os.path.isfile(path):
                            subprocess.Popen(['explorer', '/select,', path])
                        else:
                            subprocess.Popen(['explorer', path])
                    else:
                        # Linux: use xdg-open or nautilus
                        subprocess.Popen(['xdg-open', path])
                except Exception as e:
                    print(f"Error opening path: {e}")
            
            # Context menu for copying
            def show_context_menu(event):
                if event.button() == Qt.MouseButton.RightButton:
                    menu = QMenu()
                    menu.setStyleSheet("""
                        QMenu {
                            background-color: #1a1a1a;
                            color: #e5e7eb;
                            border: 1px solid #333333;
                        }
                        QMenu::item:selected {
                            background-color: #3b82f6;
                        }
                    """)
                    copy_action = menu.addAction("📋 Copy Path")
                    action = menu.exec(QCursor.pos())
                    if action == copy_action:
                        QApplication.clipboard().setText(path)
            
            path_label.mousePressEvent = lambda e: show_context_menu(e) if e.button() == Qt.MouseButton.RightButton else open_in_file_manager()
            
            layout.addWidget(path_label)
            layout.addStretch()
            
            return container
        
        # Get actual paths - will use platform-specific paths
        fadcrypt_folder = self.get_fadcrypt_folder()
        backup_folder = self.get_backup_folder() if hasattr(self, 'get_backup_folder') else (
            os.path.join(os.path.expanduser("~/.local/share/FadCrypt/Backup"))
            if not sys.platform.startswith('win')
            else os.path.join(os.getenv('PROGRAMDATA', 'C:\\ProgramData'), 'FadCrypt', 'Backup')
        )
        
        # Add path labels
        config_layout.addWidget(create_path_label("Config Folder:", fadcrypt_folder))
        config_layout.addWidget(create_path_label("Password File:", os.path.join(fadcrypt_folder, "encrypted_password.bin")))
        config_layout.addWidget(create_path_label("Unified Config:", os.path.join(fadcrypt_folder, "apps_config.json")))
        config_layout.addWidget(create_path_label("Settings File:", os.path.join(fadcrypt_folder, "settings.json")))
        config_layout.addWidget(create_path_label("State File:", os.path.join(fadcrypt_folder, "monitoring_state.json")))
        config_layout.addWidget(create_path_label("Backup Folder:", backup_folder))
        
        config_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        
        tab_layout = QVBoxLayout(config_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)
        
        self.tabs.addTab(config_tab, "Config")
        
        # Initial update of config display
        self.update_config_display()
        
    def create_settings_tab(self):
        """Create Settings tab"""
        settings_tab = QWidget()
        tab_layout = QVBoxLayout(settings_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # Use the enhanced settings panel with resource_path and platform name
        self.settings_panel = SettingsPanel(self.resource_path, self.get_platform_name())
        tab_layout.addWidget(self.settings_panel)
        
        self.tabs.addTab(settings_tab, "Settings")
        
    def create_about_tab(self):
        """Create About tab"""
        about_tab = QWidget()
        tab_layout = QVBoxLayout(about_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # Use the enhanced about panel (pass version, version_code, resource_path_func)
        self.about_panel = AboutPanel(self.version, self.version_code, self.resource_path)
        tab_layout.addWidget(self.about_panel)
        
        self.tabs.addTab(about_tab, "About")
        
    def show_about_dialog(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About FadCrypt",
            f"<h3>FadCrypt v{self.version}</h3>"
            "<p>An open-source application lock and encryption software.</p>"
            "<p>© 2024-2025 FadSec Lab. All rights reserved.</p>"
        )
    
    # Helper methods
    def get_fadcrypt_folder(self):
        """Get FadCrypt configuration folder path"""
        home_dir = os.path.expanduser('~')
        fadcrypt_folder = os.path.join(home_dir, '.FadCrypt')
        
        # Create if not exists
        if not os.path.exists(fadcrypt_folder):
            os.makedirs(fadcrypt_folder, exist_ok=True)
        
        return fadcrypt_folder
    
    def get_file_lock_manager(self, config_folder: str):
        """
        Get platform-specific file lock manager with access to unified config.
        To be overridden by platform-specific subclasses.
        """
        import platform
        system = platform.system()
        
        # Get app_locker reference if available
        app_locker = getattr(self, 'app_locker', None)
        
        if system == "Linux":
            from core.linux.file_lock_manager_linux import FileLockManagerLinux
            return FileLockManagerLinux(config_folder, app_locker)
        elif system == "Windows":
            from core.windows.file_lock_manager_windows import FileLockManagerWindows
            return FileLockManagerWindows(config_folder, app_locker)
        else:
            # Fallback (shouldn't happen)
            print(f"⚠️  File locking not supported on {system}")
            return None
    
    def on_settings_changed(self):
        """Handle settings changes from SettingsPanel"""
        # Get current settings
        settings = self.settings_panel.get_settings()
        
        # Update instance variables
        self.password_dialog_style = settings.get('dialog_style', 'simple')
        self.wallpaper_choice = settings.get('wallpaper', 'default')
        
        # Handle autostart
        autostart_enabled = settings.get('autostart', False)
        self.handle_autostart_setting(autostart_enabled)
        
        # Save settings to file
        self.save_settings(settings)
        
        print(f"Settings updated: style={self.password_dialog_style}, wallpaper={self.wallpaper_choice}, autostart={autostart_enabled}")
    
    def handle_autostart_setting(self, enable):
        """
        Handle autostart setting change. Platform-specific classes should override this.
        
        Args:
            enable: True to enable autostart, False to disable
        """
        # Base implementation does nothing, platform-specific classes override
        print(f"Autostart {'enabled' if enable else 'disabled'} (base implementation)")
        pass
    
    def save_settings(self, settings):
        """Save settings to JSON file"""
        import json
        settings_file = os.path.join(self.get_fadcrypt_folder(), 'settings.json')
        try:
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            print(f"Settings saved to {settings_file}")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_settings(self):
        """Load settings from JSON file and apply to UI"""
        import json
        settings_file = os.path.join(self.get_fadcrypt_folder(), 'settings.json')
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.password_dialog_style = settings.get('dialog_style', 'simple')
                    self.wallpaper_choice = settings.get('wallpaper', 'default')
                    
                    # Apply settings to SettingsPanel
                    if hasattr(self, 'settings_panel'):
                        self.settings_panel.apply_settings(settings)
                    
                    print(f"Settings loaded: {settings}")
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def center_on_screen(self):
        """Center the main window on the screen (Wayland-aware)"""
        from PyQt6.QtWidgets import QApplication
        import os
        
        # Check if running under Wayland
        session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
        wayland_display = os.environ.get('WAYLAND_DISPLAY', '')
        is_wayland = 'wayland' in session_type or wayland_display
        
        if is_wayland:
            print(f"[MainWindow] Detected Wayland session - window manager controls positioning")
            # On Wayland, window positioning is controlled by the compositor
            # We can't use move() - the window will be placed by the WM
            # The window will typically be centered automatically on first show
            return
        
        # X11 / Windows / macOS - we can control position
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            print(f"[MainWindow] Centering window at ({x}, {y})")
            print(f"   Screen size: {screen_geometry.width()}x{screen_geometry.height()}")
            print(f"   Window size: {self.width()}x{self.height()}")
            self.move(x, y)
        else:
            print("[MainWindow] ⚠️  No screen found, cannot center")
    
    def verify_password_with_recovery(self, title: str, prompt: str) -> bool:
        """
        Verify password with recovery code fallback.
        Handles "Forgot Password?" flow.
        
        Returns:
            True if password verified, False if cancelled or recovery attempted
        """
        from ui.dialogs.password_dialog import ask_password
        from ui.dialogs.recovery_dialog import ask_recovery_code, show_recovery_codes
        
        while True:
            # Ask for password with recovery code status
            password = ask_password(
                title,
                prompt,
                self.resource_path,
                style=self.password_dialog_style,
                wallpaper=self.wallpaper_choice,
                parent=self,
                has_recovery_codes=self.password_manager.has_recovery_codes()
            )
            
            # User cancelled
            if not password:
                return False
            
            # User clicked "Forgot Password?"
            if password == "RECOVER":
                if not self.password_manager.has_recovery_codes():
                    self.show_message(
                        "No Recovery Codes",
                        "No recovery codes found. You cannot recover your password.\n"
                        "Your password cannot be reset without backup codes.",
                        "error"
                    )
                    continue
                
                # Show recovery code dialog with verification callback
                code, new_pwd = ask_recovery_code(
                    self.resource_path,
                    self,
                    verify_callback=self.password_manager.verify_recovery_code
                )
                
                if not code or not new_pwd:
                    continue  # User cancelled recovery
                
                # Attempt password recovery
                success, error = self.password_manager.recover_password_with_code(
                    code,
                    new_pwd,
                    cleanup_callback=self._password_recovery_cleanup
                )
                
                if success:
                    # Update password button visibility
                    self.update_password_buttons_visibility()
                    # Ask user if they want to generate recovery codes now
                    self._offer_recovery_code_generation("Password Recovered")
                    return True
                else:
                    self.show_message(
                        "Recovery Failed",
                        f"❌ Password recovery failed:\n{error}",
                        "error"
                    )
                    continue
            
            # Verify password
            if self.password_manager.verify_password(password):
                return True
            else:
                # Invalid password - ask again
                self.show_message(
                    "Invalid Password",
                    "❌ Incorrect password. Please try again.\n"
                    "You can click 'Forgot Password?' if you don't remember your password.",
                    "error"
                )
                continue
    
    def _offer_recovery_code_generation(self, success_title: str = "Success"):
        """
        Offer user to generate recovery codes with recommendation.
        
        Args:
            success_title: Title for success message
        """
        from ui.dialogs.recovery_dialog import show_recovery_codes
        
        # Check if recovery codes already exist
        has_codes = self.password_manager.has_recovery_codes()
        
        if has_codes:
            # Codes exist - warn about invalidation
            message = (
                "✅ Password operation successful!\n\n"
                "ℹ️  You currently have existing recovery codes.\n\n"
                "🔐 Would you like to generate NEW recovery codes?\n\n"
                "⚠️  IMPORTANT: Generating new codes will INVALIDATE all old codes!\n"
                "• If you have old codes saved, they will no longer work\n"
                "• Only the new codes will be valid after generation\n\n"
                "Recommendation: Only generate new codes if:\n"
                "• You've lost your old codes\n"
                "• You want to refresh your codes for security"
            )
        else:
            # No codes exist - recommend generation
            message = (
                "✅ Password operation successful!\n\n"
                "🔐 Would you like to generate recovery codes now?\n\n"
                "Recovery codes allow you to reset your password if you forget it.\n"
                "Without recovery codes, a forgotten password cannot be recovered!\n\n"
                "⚠️  Highly recommended for account security!"
            )
        
        # Ask if user wants to generate codes now
        reply = QMessageBox.question(
            self,
            success_title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No if has_codes else QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, codes = self.password_manager.create_recovery_codes()
            if success and codes:
                show_recovery_codes(codes, self.resource_path, self)
                if has_codes:
                    self.show_message(
                        "Recovery Codes Regenerated",
                        "✅ New recovery codes generated successfully!\n"
                        "⚠️  All old codes have been invalidated.\n\n"
                        "Save the new codes in a secure place.\n\n"
                        "You can regenerate codes anytime from the main menu.",
                        "success"
                    )
                else:
                    self.show_message(
                        "Recovery Codes Generated",
                        "✅ Recovery codes generated successfully!\n"
                        "Save them in a secure place.\n\n"
                        "You can regenerate codes anytime from the main menu.",
                        "success"
                    )
        else:
            if has_codes:
                self.show_message(
                    "Recovery Codes Kept",
                    "ℹ️  Your existing recovery codes remain valid.\n\n"
                    "You can continue using your saved codes if needed.\n\n"
                    "To generate new codes later, use:\n"
                    "Settings → Generate Recovery Codes",
                    "info"
                )
            else:
                self.show_message(
                    "Recovery Codes Skipped",
                    "⚠️  You chose not to generate recovery codes.\n\n"
                    "Without recovery codes, you CANNOT reset your password if forgotten!\n\n"
                    "You can generate them later from the main menu:\n"
                    "Settings → Generate Recovery Codes",
                    "warning"
                )
    
    def _password_recovery_cleanup(self, new_password: str) -> bool:
        """
        Cleanup callback for password recovery.
        Stops monitoring, unlocks files, resets state, updates UI.
        
        Args:
            new_password: New master password (for re-encryption if needed)
        
        Returns:
            True if cleanup successful
        """
        try:
            print("[Recovery] Starting cleanup callback...")
            
            # Stop monitoring if active
            if self.monitoring_active:
                print("[Recovery] Stopping monitoring...")
                if self.unified_monitor:
                    self.unified_monitor.stop_monitoring()
                if self.file_lock_manager and hasattr(self.file_lock_manager, 'stop_monitoring'):
                    self.file_lock_manager.stop_monitoring()
                self.monitoring_active = False
            
            # Unlock all files
            if self.file_lock_manager:
                print("[Recovery] Unlocking all files...")
                self.file_lock_manager.unlock_all()
                self.file_lock_manager.unlock_fadcrypt_configs()
            
            # Reset monitoring state
            self.monitoring_state = {
                'unlocked_apps': [],
                'unlocked_files': []
            }
            self.save_monitoring_state_to_disk()
            
            # CRITICAL: Update UI buttons - enable start, disable stop
            print("[Recovery] Updating UI buttons...")
            self.update_monitoring_button_state(False)
            
            # Re-enable system tools if they were disabled
            if hasattr(self, 'settings_panel') and self.settings_panel.lock_tools_checkbox.isChecked():
                print("[Recovery] Re-enabling system tools...")
                if hasattr(self, 'enable_system_tools'):
                    self.enable_system_tools()
            
            # Disable autostart
            print("[Recovery] Disabling autostart...")
            if hasattr(self, 'handle_autostart_setting'):
                self.handle_autostart_setting(enable=False)
            
            # Update system tray status
            if self.system_tray:
                self.system_tray.set_monitoring_active(False)
            
            print("[Recovery] ✅ Cleanup complete - UI updated")
            return True
            
        except Exception as e:
            print(f"[Recovery] ❌ Error during cleanup: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def show_message(self, title, message, msg_type="info"):
        """Show a message dialog"""
        if msg_type == "info":
            QMessageBox.information(self, title, message)
        elif msg_type == "warning":
            QMessageBox.warning(self, title, message)
        elif msg_type == "error":
            QMessageBox.critical(self, title, message)
        elif msg_type == "success":
            QMessageBox.information(self, title, message)
    
    # Application management methods
    def add_application(self):
        """Open the Add Application dialog"""
        from ui.dialogs.add_application_dialog import AddApplicationDialog
        
        dialog = AddApplicationDialog(self.resource_path, self, self.get_platform_name())
        dialog.application_added.connect(self.on_application_added)
        dialog.exec()
    
    def on_application_added(self, app_name, app_path):
        """Handle application added from dialog - uses ISO format timestamp"""
        from datetime import datetime
        
        # Check if already added
        if app_name in self.app_list_widget.apps_data:
            self.show_message("Info", f"Application '{app_name}' is already in the list.", "info")
            return
        
        # Add to the grid with ISO format timestamp
        self.app_list_widget.add_app(
            app_name, 
            app_path, 
            unlock_count=0, 
            added_at=datetime.now().isoformat()
        )
        self.save_applications_config()
        self.update_app_count()
        
        # Log activity
        self.log_activity(
            'add_item',
            app_name,
            'application',
            success=True,
            details=f"Added application: {app_path}"
        )
        
        self.show_message("Success", f"Application '{app_name}' added successfully.", "success")
    
    def update_app_count(self):
        """Update the application count label"""
        count = len(self.app_list_widget.apps_data)
        self.app_count_label.setText(f"Applications: {count}")
    
    def update_password_buttons_visibility(self):
        """Update visibility of Create/Change Password buttons based on password existence"""
        password_file = os.path.join(self.get_fadcrypt_folder(), "encrypted_password.bin")
        password_exists = os.path.exists(password_file)
        
        # Show Create Password only if no password exists
        self.create_pass_button.setVisible(not password_exists)
        # Change Password is always visible
        self.change_pass_button.setVisible(True)
    
    def remove_application(self):
        """Remove selected applications from the list"""
        selected_apps = self.app_list_widget.get_selected_apps()
        
        if not selected_apps:
            self.show_message("Info", "Please select at least one application to remove.", "info")
            return
        
        # Confirm removal
        app_names = ", ".join(selected_apps)
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove:\n{app_names}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Bulk remove optimization: defer grid refresh until all apps removed
            removed_count = len(selected_apps)
            
            for app_name in selected_apps:
                # Skip grid refresh during loop (optimization)
                self.app_list_widget.remove_app(app_name, defer_refresh=True)
                
                # Log activity
                self.log_activity(
                    'remove_item',
                    app_name,
                    'application',
                    success=True,
                    details=f"Removed application from list"
                )
            
            # Single refresh at end (O(n) instead of O(n²))
            if removed_count > 0:
                print(f"[Remove] Refreshing UI after removing {removed_count} apps...")
                self.app_list_widget.refresh_grid()
            
            self.save_applications_config()
            self.update_app_count()
            self.show_message("Success", f"Removed {removed_count} application(s) successfully.", "success")
    
    def toggle_app_lock(self):
        """Toggle lock status of selected applications - NOT USED IN PyQt6 VERSION"""
        # This method is for backward compatibility but not used in new design
        pass
    
    # ========================================
    # FILE/FOLDER LOCKING METHODS
    # ========================================
    
    def add_file(self):
        """Add file(s) to protected items list - supports multi-selection"""
        if not self.file_lock_manager:
            self.show_message("Error", "File locking not available on this platform.", "error")
            return
        
        # Use native dialog for multi-file selection
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select File(s) to Protect",
            os.path.expanduser('~'),
            "All Files (*.*)"
        )
        
        if not file_paths:
            return
        
        added_count = 0
        print(f"[Add Files] Processing {len(file_paths)} file(s)...")
        
        for file_path in file_paths:
            if self.file_lock_manager.add_item(file_path, "file"):
                # Get metadata to display
                items = self.file_lock_manager.get_locked_items()
                for item in items:
                    if item['path'] == file_path:
                        self.file_grid_widget.add_item(
                            file_path,
                            "file",
                            item.get('unlock_count', 0),
                            item.get('added_at')
                        )
                        break
                added_count += 1
                
                # Process UI events periodically for large batches
                if added_count % 50 == 0:
                    QApplication.processEvents()
        
        # Force grid refresh after bulk add
        if added_count > 0:
            print(f"[Add Files] Refreshing UI with {added_count} new files...")
            self.file_grid_widget.refresh_grid()
        
        if added_count > 0:
            print(f"[Add Files] Added {added_count} file(s) successfully")
            
            # Auto-lock files if monitoring is active
            if self.monitoring_active and self.file_lock_manager:
                print(f"🔒 Auto-locking {added_count} newly added file(s)")
                # Re-lock all files (includes the new ones)
                success, failed = self.file_lock_manager.lock_all()
                if success > 0:
                    print(f"✅ Re-locked {success} items (including new files)")
                
                # Update fanotify watches if using fanotify
                if hasattr(self.file_lock_manager, 'update_monitored_items'):
                    self.file_lock_manager.update_monitored_items()
                    print(f"🔄 Updated fanotify watches")
            
            # Update config display to show new locked items
            if hasattr(self, 'update_config_display'):
                self.update_config_display()
            
            self.show_message("Success", f"Added {added_count} file(s) successfully.", "success")
        else:
            self.show_message("Error", "Failed to add files. They may already be in the list.", "error")
    
    def add_folder(self):
        """Add folder to protected items list"""
        if not self.file_lock_manager:
            self.show_message("Error", "File locking not available on this platform.", "error")
            return
        
        # Use native dialog for folder selection (single selection only)
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Protect",
            os.path.expanduser('~')
        )
        
        if not folder_path:
            return
        
        print(f"[Add Folder] Processing folder: {folder_path}")
        
        if self.file_lock_manager.add_item(folder_path, "folder"):
            # Get metadata to display
            items = self.file_lock_manager.get_locked_items()
            for item in items:
                if item['path'] == folder_path:
                    self.file_grid_widget.add_item(
                        folder_path,
                        "folder",
                        item.get('unlock_count', 0),
                        item.get('added_at')
                    )
                    break
            
            print(f"[Add Folder] Added folder successfully")
            
            # Auto-lock folder if monitoring is active
            if self.monitoring_active and self.file_lock_manager:
                print(f"🔒 Auto-locking newly added folder")
                # Re-lock all files (includes the new one)
                success, failed = self.file_lock_manager.lock_all()
                if success > 0:
                    print(f"✅ Re-locked {success} items (including new folder)")
                
                # Update fanotify watches if using fanotify
                if hasattr(self.file_lock_manager, 'update_monitored_items'):
                    self.file_lock_manager.update_monitored_items()
                    print(f"🔄 Updated fanotify watches")
            
            # Update config display to show new locked items
            if hasattr(self, 'update_config_display'):
                self.update_config_display()
            
            self.show_message("Success", f"Added folder successfully.", "success")
        else:
            self.show_message("Error", "Failed to add folder. It may already be in the list.", "error")
    
    def remove_file_item(self):
        """Remove selected file/folder from protected items list"""
        if not self.file_lock_manager:
            return
        
        # Get all selected paths (supports multi-selection)
        selected_paths = self.file_grid_widget.get_selected_paths()
        
        if not selected_paths:
            self.show_message("Info", "Please select one or more files/folders to remove.", "info")
            return
        
        # Confirm removal
        if len(selected_paths) == 1:
            item_name = os.path.basename(selected_paths[0])
            message = f"Remove {item_name} from protected items?"
        else:
            message = f"Remove {len(selected_paths)} selected items from protected items?"
        
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            removed_count = 0
            
            # Bulk remove optimization: defer grid refresh until all items removed
            for selected_path in selected_paths:
                if self.file_lock_manager.remove_item(selected_path):
                    # Skip grid refresh during loop (optimization)
                    self.file_grid_widget.remove_item(selected_path, defer_refresh=True)
                    removed_count += 1
            
            # Update fanotify watches if monitoring is active
            if self.monitoring_active and hasattr(self.file_lock_manager, 'update_monitored_items'):
                self.file_lock_manager.update_monitored_items()
                print(f"🔄 Updated fanotify watches after removal")
            
            # Single refresh at end (O(n) instead of O(n²))
            if removed_count > 0:
                print(f"[Remove] Refreshing file grid after removing {removed_count} items...")
                self.file_grid_widget.refresh_grid()
            
            
            if removed_count > 0:
                self.show_message("Success", f"Removed {removed_count} item(s) successfully.", "success")
            else:
                self.show_message("Error", "Failed to remove items.", "error")
    
    def load_locked_files(self):
        """Load locked files/folders from config and display in grid"""
        if not self.file_lock_manager:
            return
        
        self.file_grid_widget.clear()
        items = self.file_lock_manager.get_locked_items()
        
        for item in items:
            self.file_grid_widget.add_item(
                item['path'],
                item['type'],
                item.get('unlock_count', 0),  # Pass unlock_count as 3rd param
                item.get('added_at')          # Pass added_at as 4th param
            )
    
    def select_all_apps(self):
        """Select all applications in the list"""
        if not self.app_list_widget.apps_data:
            self.show_message("Info", "No applications to select.", "info")
            return
        
        self.app_list_widget.selectAll()
        self.show_message("Success", "All applications selected.", "success")
    
    def deselect_all_apps(self):
        """Deselect all applications in the list"""
        if not self.app_list_widget.apps_data:
            self.show_message("Info", "No applications to deselect.", "info")
            return
        
        self.app_list_widget.clearSelection()
        self.show_message("Success", "All applications deselected.", "success")
    
    def filter_applications(self, search_text):
        """Filter applications based on search text"""
        search_text = search_text.lower().strip()
        
        if not search_text:
            # Show all apps
            for app_name, card in self.app_list_widget.app_cards.items():
                card.show()
            self.update_app_count()
            return
        
        # Filter apps by name or path
        visible_count = 0
        for app_name, card in self.app_list_widget.app_cards.items():
            app_data = self.app_list_widget.apps_data.get(app_name, {})
            app_path = app_data.get('path', '').lower()
            
            if search_text in app_name.lower() or search_text in app_path:
                card.show()
                visible_count += 1
            else:
                card.hide()
        
        # Update count label to show filtered results
        total = len(self.app_list_widget.apps_data)
        if visible_count < total:
            self.app_count_label.setText(f"Applications: {visible_count} of {total}")
        else:
            self.app_count_label.setText(f"Applications: {total}")
    
    def sort_applications(self, sort_option):
        """Sort applications based on selected option"""
        if not self.app_list_widget.apps_data:
            return
        
        apps_list = list(self.app_list_widget.apps_data.items())
        
        if sort_option == "Name (A-Z)":
            apps_list.sort(key=lambda x: x[0].lower())
        elif sort_option == "Name (Z-A)":
            apps_list.sort(key=lambda x: x[0].lower(), reverse=True)
        elif sort_option == "Recently Added":
            # Keep original order (assuming last added are at the end)
            apps_list.reverse()
        elif sort_option == "Most Used":
            # Sort by unlock_count descending
            apps_list.sort(key=lambda x: x[1].get('unlock_count', 0), reverse=True)
        
        # Rebuild apps_data dict in sorted order
        self.app_list_widget.apps_data = dict(apps_list)
        self.app_list_widget.refresh_grid()
        
        # Reapply current search filter if any
        if hasattr(self, 'app_search_input') and self.app_search_input.text():
            self.filter_applications(self.app_search_input.text())
    
    def clear_search(self):
        """Clear search input and show all applications"""
        if hasattr(self, 'app_search_input'):
            self.app_search_input.clear()
            # filter_applications will be called automatically via textChanged signal
    
    def scan_for_applications(self):
        """Open App Scanner dialog to scan system for installed apps"""
        from ui.dialogs.app_scanner_dialog import AppScannerDialog
        
        print("[MainWindow] Opening app scanner dialog...")
        dialog = AppScannerDialog(self)
        dialog.apps_selected.connect(self.on_apps_scanned)
        dialog.exec()
    
    def on_apps_scanned(self, selected_apps):
        """Handle batch adding of scanned applications - optimized for bulk operations"""
        from datetime import datetime
        from PyQt6.QtWidgets import QApplication
        
        added_count = 0
        skipped_count = 0
        
        # Show progress for large batches
        total = len(selected_apps)
        if total > 50:
            print(f"[Scanner] Processing {total} apps (bulk add optimization enabled)...")
        
        # Defer grid refresh for all apps (optimization)
        for i, app in enumerate(selected_apps):
            app_name = app['name']
            app_path = app['path']
            
            # Progress update for large batches (every 50 apps)
            if total > 50 and (i + 1) % 50 == 0:
                QApplication.processEvents()  # Keep UI responsive
                print(f"[Scanner] Progress: {i + 1}/{total} apps processed...")
            
            # Check if already added
            if app_name in self.app_list_widget.apps_data:
                print(f"[Scanner] Skipping duplicate: {app_name}")
                skipped_count += 1
                continue
            
            # Add to grid with deferred refresh (optimization)
            self.app_list_widget.add_app(
                app_name, 
                app_path, 
                unlock_count=0,
                added_at=datetime.now().isoformat(),
                defer_refresh=True  # Don't refresh grid yet
            )
            added_count += 1
        
        # Single grid refresh at the end (huge performance boost)
        if added_count > 0:
            print(f"[Scanner] Refreshing UI with {added_count} new apps...")
            self.app_list_widget.refresh_grid()
            
            print(f"[Scanner] Saving config for {added_count} new apps...")
            self.save_applications_config()
            self.update_app_count()
        
        # Show summary
        message = f"✅ Added {added_count} application(s)"
        if skipped_count > 0:
            message += f"\n⚠️ Skipped {skipped_count} duplicate(s)"
        
        self.show_message("Scan Complete", message, "success")
        print(f"[Scanner] Added: {added_count}, Skipped: {skipped_count}")
    
    def edit_application(self):
        """Edit selected application"""
        selected_apps = self.app_list_widget.get_selected_apps()
        
        if not selected_apps:
            self.show_message("Info", "Please select an application to edit.", "info")
            return
        
        if len(selected_apps) > 1:
            self.show_message("Info", "Please select only one application to edit.", "info")
            return
        
        app_name = selected_apps[0]
        app_data = self.app_list_widget.apps_data[app_name]
        app_path = app_data['path']
        
        # Open edit dialog
        from ui.dialogs.edit_application_dialog import EditApplicationDialog
        dialog = EditApplicationDialog(app_name, app_path, self)
        dialog.app_updated.connect(self.on_application_edited)
        dialog.exec()
    
    def on_application_edited(self, old_name, new_name, new_path):
        """Handle application edit from dialog"""
        # Check if new name conflicts with existing app (excluding the old one)
        if new_name != old_name and new_name in self.app_list_widget.apps_data:
            self.show_message("Error", f"An application named '{new_name}' already exists.", "error")
            return
        
        # Get old app data
        old_data = self.app_list_widget.apps_data.get(old_name)
        if not old_data:
            print(f"[Edit] Error: Could not find old app data for '{old_name}'")
            return
        
        # Preserve unlock count
        unlock_count = old_data.get('unlock_count', 0)
        
        # Remove old entry
        self.app_list_widget.remove_app(old_name)
        
        # Add new entry
        self.app_list_widget.add_app(new_name, new_path, unlock_count=unlock_count)
        
        # Save config
        self.save_applications_config()
        self.update_app_count()
        
        self.show_message("Success", f"Application updated successfully:\n'{old_name}' → '{new_name}'", "success")
        print(f"[Edit] Updated: '{old_name}' -> '{new_name}', path: '{new_path}'")
    
    def handle_app_edited(self, old_name, new_name, new_path):
        """Handle app edit from context menu (app_list_widget signal)"""
        # Reuse the edit dialog
        app_data = self.app_list_widget.apps_data.get(old_name)
        if not app_data:
            return
        
        from ui.dialogs.edit_application_dialog import EditApplicationDialog
        dialog = EditApplicationDialog(old_name, app_data['path'], self)
        dialog.app_updated.connect(self.on_application_edited)
        dialog.exec()
    
    def handle_app_removed(self, app_name):
        """Handle app removal from context menu (app_list_widget signal)"""
        from PyQt6.QtWidgets import QMessageBox
        
        # Confirm removal
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove '{app_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove from widget
            self.app_list_widget.remove_app(app_name)
            # Save config
            self.save_applications_config()
            self.update_app_count()
            self.show_message("Success", f"Application '{app_name}' removed.", "success")
            print(f"[Remove] Removed app: {app_name}")
    
    def handle_lock_toggled(self, app_name, is_locked):
        """Handle lock toggle from context menu (app_list_widget signal)"""
        print(f"[LockToggle] {app_name} is now {'locked' if is_locked else 'unlocked'}")
        # Lock state is already updated in widget, just save config
        self.save_applications_config()
        status = "locked" if is_locked else "unlocked"
        self.show_message("Success", f"Application '{app_name}' is now {status}.", "success")
    
    def save_applications_config(self):
        """Save applications configuration to unified JSON file"""
        config_file = os.path.join(self.get_fadcrypt_folder(), 'apps_config.json')
        
        # Temporarily unlock config if needed using file_lock_manager
        should_relock = False
        if self.file_lock_manager and hasattr(self.file_lock_manager, 'temporarily_unlock_config'):
            try:
                self.file_lock_manager.temporarily_unlock_config('apps_config.json')
                should_relock = True
            except:
                pass
        
        # Load existing config to preserve locked files/folders
        existing_config = {"applications": [], "locked_files_and_folders": []}
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    existing_config = json.load(f)
            except:
                pass
        
        # Build applications array in unified format with consistent ISO timestamps
        from datetime import datetime
        applications = []
        for app_name, app_data in self.app_list_widget.apps_data.items():
            # Ensure added_at is always set to current time if missing
            added_at = app_data.get('added_at')
            if not added_at:
                added_at = datetime.now().isoformat()
                # Update the in-memory data as well
                app_data['added_at'] = added_at
                
            applications.append({
                'name': app_name,
                'path': app_data['path'],
                'unlock_count': app_data.get('unlock_count', 0),
                'added_at': added_at
            })
        
        # Create unified config - preserve locked items
        unified_config = {
            'applications': applications,
            'locked_files_and_folders': existing_config.get('locked_files_and_folders', [])
        }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(unified_config, f, indent=4)
            print(f"Applications config saved: {len(applications)} apps (preserved {len(unified_config.get('locked_files_and_folders', []))} locked items)")
            
            # Also update the config tab display
            self.update_config_display()
        except Exception as e:
            print(f"Error saving applications config: {e}")
        finally:
            # Relock config if it was unlocked using file_lock_manager
            if should_relock and self.file_lock_manager and hasattr(self.file_lock_manager, 'relock_config'):
                try:
                    self.file_lock_manager.relock_config('apps_config.json')
                except:
                    pass
    
    def update_config_display(self):
        """Update the config display in Config tab - show raw JSON with applications and locked files"""
        config_file = os.path.join(self.get_fadcrypt_folder(), 'apps_config.json')
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Display raw JSON with proper formatting
                raw_json = json.dumps(config_data, indent=4)
                self.config_text.setPlainText(raw_json)
                
                # Count items
                app_count = len(config_data.get('applications', []))
                locked_count = len(config_data.get('locked_files_and_folders', []))
                print(f"[Config Display] Updated with {app_count} apps and {locked_count} locked items")
            except Exception as e:
                error_msg = f"Error loading config: {e}"
                self.config_text.setPlainText(error_msg)
                print(f"[Config Display] {error_msg}")
        else:
            empty_msg = "No configuration file found. Add applications or lock files to create config."
            self.config_text.setPlainText(empty_msg)
            print(f"[Config Display] {empty_msg}")
    
    def load_applications_config(self):
        """Load applications configuration from JSON file"""
        config_file = os.path.join(self.get_fadcrypt_folder(), 'apps_config.json')
        
        if not os.path.exists(config_file):
            return
        
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Clear current grid
            self.app_list_widget.apps_data.clear()
            
            # Load apps from unified config format with consistent ISO timestamps
            from datetime import datetime
            apps_list = config_data.get('applications', [])
            for app in apps_list:
                # Always ensure added_at has a value (not null)
                added_at = app.get('added_at')
                if not added_at:
                    added_at = datetime.now().isoformat()
                    
                self.app_list_widget.add_app(
                    app['name'],
                    app['path'],
                    unlock_count=app.get('unlock_count', 0),
                    added_at=added_at
                )
            
            self.update_app_count()
            print(f"Applications config loaded: {len(apps_list)} apps")
            
            # Update config display to show the loaded apps (if config tab has been created)
            if hasattr(self, 'config_text'):
                self.update_config_display()
        except Exception as e:
            print(f"Error loading applications config: {e}")
        
    # Button handlers (to be overridden by subclasses)
    def toggle_monitoring(self):
        """Toggle monitoring on/off based on current state"""
        if self.monitoring_active:
            self.on_stop_monitoring()
        else:
            self.on_start_monitoring()
    
    def update_monitoring_button_state(self, is_active: bool):
        """Update the monitoring button text and style based on state"""
        if is_active:
            self.monitoring_button.setText("⏹ Stop Monitoring")
            self.monitoring_button.setStyleSheet("""
                QPushButton {
                    background-color: #d32f2f;
                    color: white;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 12px 20px;
                    border-radius: 6px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #b71c1c;
                }
            """)
        else:
            self.monitoring_button.setText("▶ Start Monitoring")
            self.monitoring_button.setStyleSheet("""
                QPushButton {
                    background-color: #2e7d32;
                    color: white;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 12px 20px;
                    border-radius: 6px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #388e3c;
                }
                QPushButton:disabled {
                    background-color: #2a2a2a;
                    color: #666666;
                }
            """)
    
    def on_start_monitoring(self):
        """Handle start monitoring button click"""
        # Check if password is set
        password_file = os.path.join(self.get_fadcrypt_folder(), "encrypted_password.bin")
        if not os.path.exists(password_file):
            self.show_message(
                "Hey!",
                "Please set your password, and I'll enjoy some biryani 🍚.\nBy the way, do you like biryani as well?",
                "info"
            )
            return
        
        # Check if any apps or locked items are added
        apps_count = len(self.app_list_widget.apps_data) if self.app_list_widget.apps_data else 0
        
        # Get locked files/folders from config - handle locked config file
        locked_items = []
        try:
            config_file = os.path.join(self.get_fadcrypt_folder(), "apps_config.json")
            if os.path.exists(config_file):
                # Temporarily unlock config if it's locked (chmod 000)
                should_relock = False
                if self.file_lock_manager and hasattr(self.file_lock_manager, 'temporarily_unlock_config'):
                    self.file_lock_manager.temporarily_unlock_config('apps_config.json')
                    should_relock = True
                
                try:
                    with open(config_file, 'r') as f:
                        import json
                        config = json.load(f)
                        locked_items = config.get('locked_files_and_folders', [])
                finally:
                    # Re-lock after reading
                    if should_relock and self.file_lock_manager and hasattr(self.file_lock_manager, 'relock_config'):
                        self.file_lock_manager.relock_config('apps_config.json')
        except Exception as e:
            print(f"⚠️  Warning reading locked items at startup: {e}")
            locked_items = []
        
        locked_count = len(locked_items) if locked_items else 0
        total_items = apps_count + locked_count
        
        if total_items == 0:
            self.show_message(
                "No Items to Monitor",
                "Please add applications or lock files/folders to monitor first.",
                "info"
            )
            return
        
        # Prepare applications list for monitoring
        applications = []
        for app_name, app_data in self.app_list_widget.apps_data.items():
            applications.append({
                'name': app_name,
                'path': app_data['path']
            })
        
        print(f"\n🚀 Starting monitoring for {len(applications)} applications...")
        for app in applications:
            print(f"   📦 {app['name']}: {app['path']}")
        
        # CRITICAL: Check for crash recovery - unlock any stuck files from previous crash
        print("🔍 Checking for crash recovery...")
        if self.file_lock_manager:
            if hasattr(self.file_lock_manager, 'unlock_all_with_configs'):
                # Unlock all items silently (in case they're stuck from crash)
                success, failed = self.file_lock_manager.unlock_all_with_configs(silent=True)
                if success > 0:
                    print(f"♻️  Crash recovery: Restored {success} stuck items from previous session")
            else:
                # Windows fallback
                success, failed = self.file_lock_manager.unlock_all()
                if success > 0:
                    print(f"♻️  Crash recovery: Restored {success} stuck items")
        
        # Initialize UnifiedMonitor
        from core.unified_monitor import UnifiedMonitor
        import platform
        
        # Detect platform
        is_linux = platform.system() == "Linux"
        
        self.unified_monitor = UnifiedMonitor(
            get_state_func=self.get_monitoring_state,
            set_state_func=self.set_monitoring_state,
            show_dialog_func=self.show_password_prompt_for_app,
            is_linux=is_linux,
            sleep_interval=1.0,
            enable_profiling=True,
            log_activity_func=self.log_activity
        )
        
        # Start monitoring
        self.unified_monitor.start_monitoring(applications)
        self.monitoring_active = True
        
        # Update button state to reflect monitoring is active
        self.update_monitoring_button_state(True)
        
        # Protect critical files from deletion/tampering (if enabled in settings)
        settings_file = os.path.join(self.get_fadcrypt_folder(), 'settings.json')
        file_protection_enabled = True  # Default: enabled
        
        try:
            if os.path.exists(settings_file):
                import json
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    file_protection_enabled = settings.get('file_protection_enabled', True)
        except Exception as e:
            print(f"[FileProtection] Could not read settings, using default: {e}")
        
        # DAEMON-ONLY: Elevated daemon handles file protection seamlessly (no password prompts)
        if file_protection_enabled:
            print("🛡️  Protecting critical files via elevated daemon...")
            file_protection = get_file_protection_manager()
            fadcrypt_folder = self.get_fadcrypt_folder()
            
            # List of critical files to protect
            critical_files = [
                os.path.join(fadcrypt_folder, "recovery_codes.json"),
                os.path.join(fadcrypt_folder, "encrypted_password.bin"),
                os.path.join(fadcrypt_folder, "apps_config.json"),
            ]
            
            # Filter to only existing files
            existing_files = [f for f in critical_files if os.path.exists(f)]
            
            if existing_files:
                success_count, errors = file_protection.protect_multiple_files(existing_files)
                if success_count > 0:
                    print(f"✅ Protected {success_count}/{len(existing_files)} critical files")
                    print(f"✅ Works seamlessly after reboot (daemon auto-starts with root permissions)")
                else:
                    error_msg = "❌ File protection failed - elevated daemon required to start monitoring"
                    print(f"[ERROR] {error_msg}")
                    self.show_message(
                        "Elevation Required",
                        "FadCrypt requires the elevated daemon service to protect critical files.\n\n"
                        "The daemon may not be:\n"
                        "  • Running (check: systemctl status fadcrypt-elevated)\n"
                        "  • Installed (check: dpkg -l | grep fadcrypt)\n"
                        "  • Available on your system\n\n"
                        "Monitoring cannot start without file protection."
                    )
                    # Stop monitoring since protection failed
                    self.unified_monitor.stop_monitoring()
                    self.monitoring_active = False
                    self.update_monitoring_button_state(False)
                    return
        else:
            print("⏭️  File protection disabled in settings")
        
        # Log monitoring start event (needed for duration calculation)
        self.log_activity(
            'start_monitoring',
            None,
            None,
            success=True,
            details=f"Monitoring started for {len(applications)} apps and {locked_count} files/folders"
        )
        
        # Save monitoring state to disk (for crash recovery)
        self.save_monitoring_state_to_disk()
        
        # Lock files and folders + start monitoring
        if self.file_lock_manager:
            print("🔒 Locking files and starting monitoring...")
            
            # Lock all items first
            success, failed = self.file_lock_manager.lock_all()
            if success > 0:
                print(f"✅ Locked {success} items")
            if failed > 0:
                print(f"⚠️  Failed to lock {failed} items")
            
            # Lock config files
            self.file_lock_manager.lock_fadcrypt_configs()
            
            # Start monitoring (fanotify on Linux, nothing on Windows yet)
            if hasattr(self.file_lock_manager, 'start_monitoring'):
                if self.file_lock_manager.start_monitoring():
                    print("✅ Fanotify monitoring started (kernel-level file access interception)")
                else:
                    print("⚠️  Failed to start fanotify monitoring")
            
            # Log lock event
            self.log_activity(
                'lock',
                'all_items',
                success=True,
                details=f"Locked {success} items"
                )
                
            # Lock FadCrypt's own config files
            print("🔒 Protecting FadCrypt config files...")
            self.file_lock_manager.lock_fadcrypt_configs()
        
        # Update UI button state
        self.update_monitoring_button_state(True)
        print("🔘 Button updated: Changed to Stop mode")
        
        # CRITICAL: Disable system tools if lock_tools setting is enabled
        # This prevents users from terminating FadCrypt via terminal/task manager
        if hasattr(self, 'settings_panel') and self.settings_panel.lock_tools_checkbox.isChecked():
            print("🔒 Disabling system tools (terminals, task manager, etc.)...")
            if hasattr(self, 'disable_system_tools'):
                self.disable_system_tools()
                print("✅ System tools disabled successfully")
            else:
                print("⚠️  Warning: disable_system_tools method not found")
        
        # CRITICAL: Enable autostart when monitoring starts (same as legacy code)
        # This ensures FadCrypt starts automatically on system boot
        print("🔧 Enabling autostart for FadCrypt...")
        if hasattr(self, 'handle_autostart_setting'):
            # Call platform-specific autostart method
            self.handle_autostart_setting(enable=True)
            print("✅ Autostart enabled successfully")
        else:
            print("⚠️  Warning: handle_autostart_setting method not found")
        
        # Update UI
        if self.system_tray:
            self.system_tray.set_monitoring_active(True)
            self.system_tray.show_message(
                "Monitoring Started",
                f"FadCrypt is now monitoring {len(applications)} application(s).",
                QSystemTrayIcon.MessageIcon.Information
            )
        
        # Hide to tray
        self.hide_to_tray()
        
        print(f"✅ Monitoring started successfully for {len(applications)} apps")
        
    def on_stop_monitoring(self):
        """Handle stop monitoring button click"""
        if not self.monitoring_active:
            self.show_message("Info", "Monitoring is not running.", "info")
            return
        
        # Ask for password with recovery option
        if self.verify_password_with_recovery(
            "Stop Monitoring",
            "Enter your password to stop monitoring:"
        ):
            # Stop monitoring
            if self.unified_monitor:
                self.unified_monitor.stop_monitoring()
                print("🛑 Monitoring stopped successfully")
            
            # Unprotect critical files (daemon handles seamlessly - no password prompt needed)
            print("🔓 Unprotecting critical files via daemon...")
            file_protection = get_file_protection_manager()
            success_count, errors = file_protection.unprotect_all_files()
            if success_count > 0:
                print(f"✅ Unprotected {success_count} critical files")
            if errors:
                for error in errors:
                    print(f"   ⚠️  {error}")
            
            # Stop file access monitoring (fanotify on Linux)
            if hasattr(self.file_lock_manager, 'stop_monitoring'):
                print("🛑 Stopping fanotify monitoring...")
                self.file_lock_manager.stop_monitoring()
                print("✅ Fanotify monitoring stopped")
            
            self.monitoring_active = False
            
            # Save monitoring state to disk (for crash recovery)
            self.save_monitoring_state_to_disk()
            
            # Unlock files and folders + config files
            if self.file_lock_manager:
                print("🔓 Unlocking files, folders, and config files...")
                success, failed = self.file_lock_manager.unlock_all()
                if success > 0:
                    print(f"✅ Unlocked {success} items")
                if failed > 0:
                    print(f"⚠️  Failed to unlock {failed} items")
                
                # Unlock config files
                self.file_lock_manager.unlock_fadcrypt_configs()
                
                # Log unlock event
                self.log_activity(
                    'unlock',
                    'all_items',
                    success=True,
                    details=f"Unlocked {success} items"
                )
            
            # Update UI button state
            self.update_monitoring_button_state(False)
            print("🔘 Button updated: Changed to Start mode")
            
            # CRITICAL: Re-enable system tools if they were disabled
            # This restores access to terminals/task manager
            if hasattr(self, 'settings_panel') and self.settings_panel.lock_tools_checkbox.isChecked():
                print("🔓 Re-enabling system tools (terminals, task manager, etc.)...")
                if hasattr(self, 'enable_system_tools'):
                    self.enable_system_tools()
                    print("✅ System tools re-enabled successfully")
                else:
                    print("⚠️  Warning: enable_system_tools method not found")
            
            # CRITICAL: Disable autostart when monitoring stops (same as legacy code)
            # This removes FadCrypt from system startup
            print("🔧 Disabling autostart for FadCrypt...")
            if hasattr(self, 'handle_autostart_setting'):
                # Call platform-specific autostart method
                self.handle_autostart_setting(enable=False)
                print("✅ Autostart disabled successfully")
            else:
                print("⚠️  Warning: handle_autostart_setting method not found")
            
            # Update UI
            if self.system_tray:
                self.system_tray.set_monitoring_active(False)
            
            # Show window
            self.show_window_from_tray()
            
            self.show_message(
                "Success",
                "Monitoring stopped successfully.",
                "success"
            )
        else:
            self.show_message(
                "Error",
                "Incorrect password. Monitoring will continue.",
                "error"
            )
    
    def get_monitoring_state(self):
        """Get current monitoring state for UnifiedMonitor"""
        return self.monitoring_state.copy()
    
    def set_monitoring_state(self, key, value):
        """Save monitoring state"""
        self.monitoring_state[key] = value
        self.save_monitoring_state()
        print(f"💾 State saved: {key} = {value}")
    
    def save_monitoring_state(self):
        """Save monitoring state to JSON file"""
        import json
        state_file = os.path.join(self.get_fadcrypt_folder(), 'monitoring_state.json')
        
        # Temporarily unlock config file if locked (for writing)
        if self.file_lock_manager and hasattr(self.file_lock_manager, 'temporarily_unlock_config'):
            self.file_lock_manager.temporarily_unlock_config('monitoring_state.json')
        
        try:
            with open(state_file, 'w') as f:
                json.dump(self.monitoring_state, f, indent=4)
        except Exception as e:
            print(f"Error saving monitoring state: {e}")
        finally:
            # Re-lock config file if monitoring is active
            if self.monitoring_active and self.file_lock_manager and hasattr(self.file_lock_manager, 'relock_config'):
                self.file_lock_manager.relock_config('monitoring_state.json')
    
    def load_monitoring_state(self):
        """Load monitoring state from JSON file"""
        import json
        state_file = os.path.join(self.get_fadcrypt_folder(), 'monitoring_state.json')
        try:
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    self.monitoring_state = json.load(f)
                    print(f"Loaded monitoring state: {len(self.monitoring_state.get('unlocked_apps', []))} unlocked apps")
            else:
                self.monitoring_state = {'unlocked_apps': []}
        except Exception as e:
            print(f"Error loading monitoring state: {e}")
            self.monitoring_state = {'unlocked_apps': []}
    
    def _handle_file_access_attempt_threadsafe(self, file_path: str) -> bool:
        """
        Thread-safe wrapper for file access attempts
        Called from watchdog observer thread - must not show Qt dialogs directly
        
        Args:
            file_path: Path to the file being accessed
        
        Returns:
            bool: Always returns False (dialog shown asynchronously in main thread)
        """
        filename = os.path.basename(file_path)
        print(f"🚨 File access attempt detected (from watchdog thread): {filename}")
        
        # Emit signal to handle in main Qt thread
        self.file_access_requested.emit(file_path)
        
        # Return False immediately (file stays locked until password entered in main thread)
        return False
    
    def _handle_file_access_from_main_thread(self, file_path: str):
        """
        Handle file access in the main Qt thread (called via QMetaObject.invokeMethod)
        """
        self._handle_file_access_attempt(file_path)
    
    def _handle_file_access_attempt(self, file_path: str) -> bool:
        """
        Handle file access attempts - show password dialog
        
        Args:
            file_path: Path to the file being accessed
        
        Returns:
            bool: True if password correct (grant access), False otherwise
        """
        from ui.dialogs.password_dialog import ask_password
        
        filename = os.path.basename(file_path)
        print(f"🚨 File access attempt detected: {filename}")
        
        # Show password dialog
        password = ask_password(
            f"File Access: {filename}",
            f"Enter password to temporarily access:\n{file_path}",
            self.resource_path,
            style=self.password_dialog_style,
            wallpaper=self.wallpaper_choice,
            parent=self
        )
        
        if password and self.password_manager.verify_password(password):
            print(f"✅ Correct password - granting temporary access to {filename}")
            
            # Unlock file and add to unlocked state (persistent tracking)
            import stat
            try:
                # Get original permissions
                original_stat = os.stat(file_path)
                is_dir = stat.S_ISDIR(original_stat.st_mode)
                
                # Make writable
                if is_dir:
                    os.chmod(file_path, 0o755)  # rwxr-xr-x
                    print(f"♻️  Unlocked folder: {filename} (will auto-lock when not in use)")
                else:
                    os.chmod(file_path, 0o644)  # rw-r--r--
                    print(f"♻️  Unlocked file: {filename} (will auto-lock when not in use)")
                
                # Add to unlocked files state (persistent tracking like unlocked_apps)
                unlocked_files = self.get_monitoring_state().get('unlocked_files', [])
                abs_path = os.path.abspath(file_path)
                if abs_path not in unlocked_files:
                    unlocked_files.append(abs_path)
                    self.set_monitoring_state('unlocked_files', unlocked_files)
                    print(f"📝 Added {filename} to unlocked files state")
                
                # Increment unlock count for tracking
                if self.file_lock_manager:
                    self.file_lock_manager.increment_unlock_count(abs_path)
                    print(f"📊 Incremented unlock count for {filename}")
                
                # Log successful unlock activity
                item_type = 'folder' if is_dir else 'file'
                self.log_activity(
                    'unlock',
                    filename,
                    item_type,
                    success=True,
                    details=f"Temporarily unlocked {item_type}"
                )
                
                # Show success dialog
                from PyQt6.QtWidgets import QMessageBox
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("File Unlocked")
                item_type_display = "Folder" if is_dir else "File"
                msg.setText(f"✅ Success! {item_type_display} unlocked and accessible.")
                msg.setInformativeText(
                    f"{item_type_display}: {filename}\n\n"
                    f"This {item_type_display.lower()} will remain unlocked while in use.\n"
                    f"It will automatically lock after 10 seconds of inactivity."
                )
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
                
                return True
            except Exception as e:
                print(f"❌ Error unlocking {filename}: {e}")
                return False
        else:
            print(f"❌ Incorrect password - access denied to {filename}")
            
            # Log failed unlock attempt for statistics
            item_type = 'folder' if os.path.isdir(file_path) else 'file'
            self.log_activity(
                'failed_unlock',
                filename,
                item_type,
                success=False,
                details='Wrong password entered'
            )
            
            return False
    
    def _handle_file_access_permission(self, file_path: str, pid: int) -> bool:
        """
        Handle file access permission request from fanotify (Linux only).
        
        This is called by the fanotify client when a locked file is accessed.
        Must be thread-safe as it's called from the fanotify client thread.
        
        Args:
            file_path: Path to the file being accessed
            pid: Process ID trying to access the file
            
        Returns:
            True if access allowed, False if denied
        """
        from PyQt6.QtCore import QMetaObject, Qt
        from ui.dialogs.password_dialog import ask_password
        
        filename = os.path.basename(file_path)
        print(f"🚨 [Fanotify] File access attempt: {filename} (PID: {pid})")
        
        # Result container for thread-safe return
        result = [False]
        
        def show_dialog():
            # Show password dialog
            password = ask_password(
                f"File Access: {filename}",
                f"Enter password to access:\n{file_path}\n\nProcess PID: {pid}",
                self.resource_path,
                style=self.password_dialog_style,
                wallpaper=self.wallpaper_choice,
                parent=self
            )
            
            if password and self.password_manager.verify_password(password):
                print(f"✅ [Fanotify] Correct password - granting access to {filename}")
                
                # Add to unlocked files state
                unlocked_files = self.get_monitoring_state().get('unlocked_files', [])
                abs_path = os.path.abspath(file_path)
                if abs_path not in unlocked_files:
                    unlocked_files.append(abs_path)
                    self.set_monitoring_state('unlocked_files', unlocked_files)
                
                # Increment unlock count
                if self.file_lock_manager:
                    self.file_lock_manager.increment_unlock_count(abs_path)
                
                # Log activity
                item_type = 'folder' if os.path.isdir(file_path) else 'file'
                self.log_activity(
                    'unlock',
                    filename,
                    item_type,
                    success=True,
                    unlock_method='password',
                    details=f'Unlocked via fanotify (PID: {pid})'
                )
                
                result[0] = True
            else:
                print(f"❌ [Fanotify] Incorrect password - access denied to {filename}")
                
                # Log failed attempt
                item_type = 'folder' if os.path.isdir(file_path) else 'file'
                self.log_activity(
                    'failed_unlock',
                    filename,
                    item_type,
                    success=False,
                    details=f'Wrong password (PID: {pid})'
                )
                
                result[0] = False
        
        # Call in main thread (blocking)
        QMetaObject.invokeMethod(
            self,
            show_dialog,
            Qt.ConnectionType.BlockingQueuedConnection
        )
        
        return result[0]
    
    def save_monitoring_state_to_disk(self):
        """Save monitoring state to JSON file including monitoring_active flag"""
        import json
        state_file = os.path.join(self.get_fadcrypt_folder(), 'monitoring_state.json')
        
        # Temporarily unlock config file if locked (for writing)
        if self.file_lock_manager and hasattr(self.file_lock_manager, 'temporarily_unlock_config'):
            self.file_lock_manager.temporarily_unlock_config('monitoring_state.json')
        
        try:
            # Add monitoring_active flag
            self.monitoring_state['monitoring_active'] = self.monitoring_active
            
            with open(state_file, 'w') as f:
                json.dump(self.monitoring_state, f, indent=2)
            print(f"💾 Saved monitoring state: active={self.monitoring_active}")
        except Exception as e:
            print(f"❌ Error saving monitoring state: {e}")
        finally:
            # Re-lock config file if monitoring is active
            if self.monitoring_active and self.file_lock_manager and hasattr(self.file_lock_manager, 'relock_config'):
                self.file_lock_manager.relock_config('monitoring_state.json')
    
    def check_crash_recovery(self):
        """
        Check if monitoring was active during last session (crash/power loss).
        If so, prompt user to unlock files since they're still locked.
        
        SKIP in auto-monitor mode - it's intentional startup, not a crash.
        """
        # Skip crash recovery in auto-monitor mode (intentional startup with monitoring)
        if self.auto_monitor_mode:
            print("⏭️  Skipping crash recovery check (auto-monitor startup)")
            return
        
        state_file = os.path.join(self.get_fadcrypt_folder(), 'monitoring_state.json')
        
        # Check if state file exists and indicates monitoring was active
        if not os.path.exists(state_file):
            return
        
        try:
            import json
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            monitoring_was_active = state.get('monitoring_active', False)
            
            if monitoring_was_active:
                print("\n🚨 CRASH RECOVERY MODE")
                print("📁 Detected that monitoring was active before app closed")
                print("🔒 Files and folders may still be locked")
                
                # Show recovery dialog
                from PyQt6.QtWidgets import QMessageBox
                from PyQt6.QtCore import QTimer, Qt
                
                # Hide main window temporarily
                was_visible = self.isVisible()
                if was_visible:
                    self.hide()
                
                def show_recovery_dialog():
                    msg_box = QMessageBox(
                        QMessageBox.Icon.Question,
                        "🚨 Crash Recovery",
                        "Monitoring was active when FadCrypt closed unexpectedly.\n\n"
                        "Protected files and folders are still locked.\n\n"
                        "Would you like to unlock them now?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        None  # No parent so it's truly independent
                    )
                    # Set window flags to keep on top and make it modal
                    msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Dialog)
                    msg_box.setModal(True)
                    reply = msg_box.exec()
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        # Ask for password
                        from ui.dialogs.password_dialog import ask_password
                        password = ask_password(
                            "Unlock Files",
                            "Enter your password to unlock files:",
                            self.resource_path,
                            style=self.password_dialog_style,
                            wallpaper=self.wallpaper_choice,
                            parent=self
                        )
                        
                        if password and self.password_manager.verify_password(password):
                            # Unlock files
                            if self.file_lock_manager:
                                print("🔓 Unlocking files and folders...")
                                success, failed = self.file_lock_manager.unlock_all()
                                if success > 0:
                                    print(f"✅ Unlocked {success} items")
                                if failed > 0:
                                    print(f"⚠️  Failed to unlock {failed} items")
                                
                                # Unlock config files
                                self.file_lock_manager.unlock_fadcrypt_configs()
                            
                            # Clear monitoring state
                            state['monitoring_active'] = False
                            with open(state_file, 'w') as f:
                                json.dump(state, f, indent=2)
                            
                            self.show_message(
                                "Success",
                                "Files unlocked successfully. Monitoring state cleared.",
                                "success"
                            )
                        else:
                            self.show_message(
                                "Failed",
                                "Incorrect password. Files remain locked.",
                                "error"
                            )
                    else:
                        # User chose not to unlock
                        self.show_message(
                            "Info",
                            "Files remain locked. Stop monitoring manually to unlock.",
                            "info"
                        )
                    
                    # Show main window again after dialog is done
                    if was_visible:
                        self.show()
                        self.activateWindow()
                        self.raise_()
                
                # Schedule dialog after UI is fully loaded
                QTimer.singleShot(500, show_recovery_dialog)
                
        except Exception as e:
            print(f"⚠️  Error during crash recovery check: {e}")
    
    def _launch_app_after_unlock(self, app_name, app_path):
        """Launch application after successful password unlock"""
        import subprocess
        import platform
        
        try:
            print(f"🚀 Launching {app_name}...")
            
            # Determine if it's a known GUI app
            gui_apps = ['chrome', 'chromium', 'firefox', 'brave', 'opera', 'edge', 
                       'vivaldi', 'code', 'slack', 'discord', 'telegram',
                       'vlc', 'gimp', 'libreoffice', 'thunderbird', 'zoom', 'teams', 
                       'obs', 'steam', 'nautilus', 'dolphin', 'kate', 'gedit', 
                       'kdenlive', 'krita', 'inkscape', 'blender', 'audacity', 
                       'shotcut', 'pycharm', 'eclipse', 'intellij', 'sublime', 
                       'virtualbox', 'postman', 'docker', 'filezilla', 'wireshark', 
                       'gparted', 'transmission', 'remmina']
            
            is_gui_app = any(gui_app in app_path.lower() or gui_app in app_name.lower() 
                            for gui_app in gui_apps)
            
            if platform.system() == "Linux":
                # Linux launch logic
                if app_path.lower().endswith('.desktop'):
                    # Launch .desktop files with xdg-open
                    subprocess.Popen(['xdg-open', app_path], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL,
                                   start_new_session=True)
                elif app_path.lower().endswith('.py'):
                    # Launch Python scripts in terminal
                    subprocess.Popen(['gnome-terminal', '--', 'python3', app_path],
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL,
                                   start_new_session=True)
                elif is_gui_app:
                    # Launch GUI apps directly
                    subprocess.Popen([app_path],
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL,
                                   start_new_session=True)
                elif any(bin_dir in app_path for bin_dir in ['/usr/bin', '/bin', '/usr/local/bin']):
                    # Launch CLI tools in terminal
                    subprocess.Popen(['gnome-terminal', '--', app_path],
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL,
                                   start_new_session=True)
                else:
                    # Launch other apps directly (assume GUI)
                    subprocess.Popen([app_path],
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL,
                                   start_new_session=True)
            else:
                # Windows launch logic
                if app_path.lower().endswith('.py'):
                    # Launch Python scripts
                    subprocess.Popen(['python', app_path],
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL,
                                   creationflags=0x00000008 | 0x00000200)  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
                else:
                    # Launch executables
                    subprocess.Popen([app_path],
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL,
                                   creationflags=0x00000008 | 0x00000200)  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
            
            print(f"✅ Successfully launched {app_name}")
            
        except Exception as e:
            print(f"❌ Error launching {app_name}: {e}")
            self.show_message("Launch Error", f"Failed to start {app_name}:\n{e}", "error")
    
    def show_password_prompt_for_app(self, app_name, app_path):
        """Show password prompt when blocked app is detected (called from monitoring thread)"""
        print(f"\n🔒 Blocked app detected: {app_name}")
        print(f"   Path: {app_path}")
        
        # Emit signal to show dialog in main thread (NON-BLOCKING - monitoring continues)
        self.password_prompt_requested.emit(app_name, app_path)
        
        # DO NOT WAIT - return immediately so monitoring thread continues killing processes
        # The dialog will handle unlocking asynchronously when user enters password
    
    def show_password_prompt_for_app_sync(self, app_name, app_path):
        """Show password dialog in main thread (thread-safe)"""
        # Use verify_password_with_recovery to handle forgot password flow
        if self.verify_password_with_recovery(
            f"Unlock {app_name}",
            f"Application '{app_name}' is locked.\n\nEnter your password to unlock it:"
        ):
            print(f"✅ Password correct - Unlocking {app_name}")
            
            # Add to unlocked apps (the monitoring thread will see this and stop blocking)
            state = self.get_monitoring_state()
            unlocked_apps = state.get('unlocked_apps', [])
            if app_name not in unlocked_apps:
                unlocked_apps.append(app_name)
                self.set_monitoring_state('unlocked_apps', unlocked_apps)
            
            # Increment unlock count
            if app_name in self.app_list_widget.apps_data:
                self.app_list_widget.apps_data[app_name]['unlock_count'] = \
                    self.app_list_widget.apps_data[app_name].get('unlock_count', 0) + 1
                self.save_applications_config()
            
            # Log successful unlock
            self.log_activity(
                'unlock',
                app_name,
                'application',
                success=True,
                details=f"Unlocked and launched {app_name}"
            )
            
            # Launch the app after successful unlock
            self._launch_app_after_unlock(app_name, app_path)
            
            # Remove from showing dialog set
            self.unified_monitor.remove_from_showing_dialog(app_name)
        else:
            print(f"❌ Password incorrect or cancelled - Keeping {app_name} locked")
            
            # Log failed unlock attempt
            self.log_activity(
                'failed_unlock',
                app_name,
                'application',
                success=False,
                details="Wrong password entered or cancelled"
            )
            
            # Remove from showing dialog set
            self.unified_monitor.remove_from_showing_dialog(app_name)
        
    def on_readme_clicked(self):
        """Handle Read Me button click - show fullscreen dialog"""
        readme_dialog = ReadmeDialog(self.resource_path, self)
        readme_dialog.exec()
    
    def cleanup_before_uninstall(self):
        """
        Cleanup function to restore all system settings before uninstallation.
        This ensures users don't have disabled settings after uninstalling FadCrypt.
        Platform-agnostic - works on both Windows and Linux.
        """
        try:
            print("\n" + "="*60, flush=True)
            print("🧹 RUNNING UNINSTALL CLEANUP...", flush=True)
            print("="*60, flush=True)
            
            # Stop monitoring if active
            if hasattr(self, 'unified_monitor') and self.unified_monitor:
                try:
                    print("⏹ Stopping monitoring system...", flush=True)
                    # The unified_monitor.stop_monitoring() method will handle cleanup
                    if hasattr(self.unified_monitor, 'stop_monitoring'):
                        self.unified_monitor.stop_monitoring()
                    # Also update button state
                    self.on_monitoring_stopped()
                    print("✅ Monitoring stopped", flush=True)
                except Exception as e:
                    print(f"❌ Error stopping monitor: {e}", flush=True)
            else:
                print("ℹ️  No active monitoring to stop", flush=True)
            
            # Re-enable system tools (platform-specific)
            # These methods are implemented in platform-specific subclasses
            if hasattr(self, 'enable_system_tools'):
                try:
                    print("🔓 Re-enabling system tools...", flush=True)
                    self.enable_system_tools()
                    print("✅ System tools re-enabled", flush=True)
                except Exception as e:
                    print(f"❌ Error re-enabling tools: {e}", flush=True)
            else:
                print("ℹ️  No system tools to re-enable", flush=True)
            
            # Remove autostart entry using autostart manager
            if hasattr(self, 'config_manager') and hasattr(self.config_manager, 'autostart_manager'):
                try:
                    print("🗑️  Removing from autostart...", flush=True)
                    from core.autostart_manager import AutostartManager
                    autostart_mgr = AutostartManager(self.get_fadcrypt_folder())
                    autostart_mgr.disable_autostart()
                    print("✅ Removed from autostart", flush=True)
                except Exception as e:
                    print(f"❌ Error removing from autostart: {e}", flush=True)
            else:
                print("ℹ️  No autostart entry to remove", flush=True)
            
            print("="*60, flush=True)
            print("✅ CLEANUP COMPLETED SUCCESSFULLY!", flush=True)
            print("="*60 + "\n", flush=True)
            
            # Show confirmation
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Cleanup Complete",
                "All system settings have been restored.\n"
                "You can now safely uninstall FadCrypt.",
                QMessageBox.StandardButton.Ok
            )
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR DURING UNINSTALL CLEANUP: {e}\n", flush=True)
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Cleanup Error",
                f"Some settings may not have been restored:\n{str(e)}\n\n"
                "Please manually check system tool permissions.",
                QMessageBox.StandardButton.Ok
            )
            return False
        
    def on_create_password(self):
        """Handle create password button click"""
        password_file = os.path.join(self.get_fadcrypt_folder(), "encrypted_password.bin")
        
        print(f"\n🔐 Create Password Request")
        print(f"   Checking password file: {password_file}")
        print(f"   File exists: {os.path.exists(password_file)}")
        
        if os.path.exists(password_file):
            print(f"   ⚠️  Password file already exists, cannot create")
            self.show_message("Info", "Password already exists. Use 'Change Password' to modify.", "info")
        else:
            # First password entry
            password = ask_password(
                "Create Password",
                "Make sure to securely note down your password.\nIf forgotten, the tool cannot be stopped,\nand recovery will be difficult!\nEnter a new password:",
                self.resource_path,
                style=self.password_dialog_style,
                wallpaper=self.wallpaper_choice,
                parent=self,
                show_forgot_password=False  # Hide forgot password during creation
            )
            if password:
                # Confirm password entry
                confirm_password = ask_password(
                    "Confirm New Password",  # Changed to include "New Password" for "Create" button
                    "Please re-enter your password to confirm:",
                    self.resource_path,
                    style=self.password_dialog_style,
                    wallpaper=self.wallpaper_choice,
                    parent=self,
                    show_forgot_password=False  # Hide forgot password during creation
                )
                
                if not confirm_password:
                    print(f"   ⚠️  Password confirmation cancelled")
                    return
                
                if password != confirm_password:
                    print(f"   ❌ Passwords don't match")
                    self.show_message("Error", "Passwords don't match. Please try again.", "error")
                    return
                
                try:
                    print(f"   Creating password file at: {password_file}")
                    self.password_manager.create_password(password)
                    print(f"   ✅ Password created successfully")
                    
                    # Update password button visibility
                    self.update_password_buttons_visibility()
                    
                    # Offer recovery code generation
                    self._offer_recovery_code_generation("Password Created")
                    
                    self.show_message("Success", "Password created successfully.", "success")
                except Exception as e:
                    print(f"   ❌ Error creating password: {e}")
                    self.show_message("Error", f"Failed to create password:\n{e}", "error")
        
    def on_change_password(self):
        """Handle change password button click"""
        password_file = os.path.join(self.get_fadcrypt_folder(), "encrypted_password.bin")
        
        print(f"\n🔄 Change Password Request")
        print(f"   Checking password file: {password_file}")
        print(f"   File exists: {os.path.exists(password_file)}")
        
        if os.path.exists(password_file):
            # Ask for old password with recovery option
            old_password = ask_password(
                "Change Password",
                "Enter your old password:",
                self.resource_path,
                style=self.password_dialog_style,
                wallpaper=self.wallpaper_choice,
                parent=self,
                show_forgot_password=True,
                has_recovery_codes=self.password_manager.has_recovery_codes()
            )
            
            if old_password == "RECOVER":
                # User clicked forgot password - show recovery dialog
                from ui.dialogs.recovery_dialog import ask_recovery_code
                
                if not self.password_manager.has_recovery_codes():
                    self.show_message(
                        "No Recovery Codes",
                        "❌ No recovery codes found!\n\n"
                        "You cannot recover your password without recovery codes.\n"
                        "Recovery codes must be generated from the Settings menu first.",
                        "error"
                    )
                    return
                
                code, new_pwd = ask_recovery_code(
                    self.resource_path,
                    self,
                    verify_callback=self.password_manager.verify_recovery_code
                )
                
                if not code or not new_pwd:
                    return  # User cancelled
                
                # Recover password
                success, error = self.password_manager.recover_password_with_code(
                    code,
                    new_pwd,
                    cleanup_callback=self._password_recovery_cleanup
                )
                
                if success:
                    self._offer_recovery_code_generation("Password Recovered")
                else:
                    self.show_message("Recovery Failed", f"❌ {error}", "error")
                return
            
            if old_password and self.password_manager.verify_password(old_password):
                print(f"   ✅ Old password verified")
                new_password = ask_password(
                    "New Password",
                    "Make sure to securely note down your password.\nIf forgotten, the tool cannot be stopped,\nand recovery will be difficult!\nEnter a new password:",
                    self.resource_path,
                    style=self.password_dialog_style,
                    wallpaper=self.wallpaper_choice,
                    parent=self,
                    show_forgot_password=False
                )
                if new_password:
                    try:
                        print(f"   Changing password at: {password_file}")
                        self.password_manager.change_password(old_password, new_password)
                        print(f"   ✅ Password changed successfully")
                        
                        # Offer recovery code generation
                        self._offer_recovery_code_generation("Password Changed")
                        
                    except Exception as e:
                        print(f"   ❌ Error changing password: {e}")
                        self.show_message("Error", f"Failed to change password:\n{e}", "error")
            else:
                print(f"   ❌ Password verification failed")
                self.show_message("Error", "Incorrect old password", "error")
        else:
            print(f"   ⚠️  No password file found")
            self.show_message("Oops!", "How do I change a password that doesn't exist? :(", "warning")
    
    def on_generate_recovery_codes_clicked(self):
        """Handle generate recovery codes button click from settings"""
        from ui.dialogs.password_dialog import ask_password
        from ui.dialogs.recovery_dialog import show_recovery_codes
        
        password_file = os.path.join(self.get_fadcrypt_folder(), "encrypted_password.bin")
        
        # Check if password exists
        if not os.path.exists(password_file):
            self.show_message(
                "No Password Set",
                "You need to create a password first before generating recovery codes.",
                "warning"
            )
            return
        
        # Ask for password to verify user identity
        password = ask_password(
            "Generate Recovery Codes",
            "Enter your master password to generate recovery codes:",
            self.resource_path,
            style=self.password_dialog_style,
            wallpaper=self.wallpaper_choice,
            parent=self,
            show_forgot_password=False
        )
        
        if not password:
            return
        
        # Verify password
        if not self.password_manager.verify_password(password):
            self.show_message(
                "Invalid Password",
                "Incorrect password. Recovery codes not generated.",
                "error"
            )
            return
        
        # Generate recovery codes
        success, codes = self.password_manager.create_recovery_codes()
        if success and codes:
            show_recovery_codes(codes, self.resource_path, self)
            self.show_message(
                "Recovery Codes Generated",
                "✅ Recovery codes generated successfully!\n\n"
                "⚠️  These replace any previous recovery codes.\n"
                "Save them in a secure place.",
                "success"
            )
        else:
            self.show_message(
                "Generation Failed",
                "Failed to generate recovery codes. Please try again.",
                "error"
            )
        
    def on_snake_game(self):
        """Handle snake game button click"""
        try:
            from core.snake_game import start_snake_game
            # Pass self as the GUI instance
            start_snake_game(self)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Snake Game Error",
                f"Failed to start snake game:\n{e}"
            )
        
    def on_export_config(self):
        """Handle export config button click"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Configuration",
            os.path.expanduser("~/fadcrypt_config.json"),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                # Build applications list from current data
                applications = []
                for app_name, app_data in self.app_list_widget.apps_data.items():
                    applications.append({
                        'name': app_name,
                        'path': app_data['path'],
                        'unlock_count': app_data.get('unlock_count', 0),
                        'date_added': app_data.get('date_added', None)
                    })
                
                # Export configuration with all data
                config_data = {
                    'version': self.version,
                    'settings': self.settings_panel.get_settings() if hasattr(self, 'settings_panel') else {},
                    'applications': applications
                }
                
                with open(file_path, 'w') as f:
                    json.dump(config_data, f, indent=4)
                
                self.show_message("Success", f"Configuration exported to:\n{file_path}", "success")
            except Exception as e:
                self.show_message("Error", f"Failed to export configuration:\n{e}", "error")
        
    def on_import_config(self):
        """Handle import config button click"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Configuration",
            os.path.expanduser("~"),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    config_data = json.load(f)
                
                # Validate config structure
                if 'applications' not in config_data:
                    self.show_message("Error", "Invalid configuration file: missing 'applications' key", "error")
                    return
                
                # Clear current applications
                self.app_list_widget.apps_data.clear()
                
                # Import applications
                imported_count = 0
                for app in config_data.get('applications', []):
                    app_name = app.get('name')
                    app_path = app.get('path')
                    
                    if app_name and app_path:
                        self.app_list_widget.add_app(
                            app_name,
                            app_path,
                            unlock_count=app.get('unlock_count', 0),
                            date_added=app.get('date_added', None)
                        )
                        imported_count += 1
                
                # Save the imported config
                self.save_applications_config()
                self.update_app_count()
                
                self.show_message("Success", f"Imported {imported_count} application(s) from:\n{file_path}", "success")
            except Exception as e:
                self.show_message("Error", f"Failed to import configuration:\n{e}", "error")

    def remove_file_item(self):
        """Remove selected file or folder from protected items"""
        selected_items = self.file_grid_widget.get_selected_paths()
        
        if not selected_items:
            self.show_message("Info", "Please select at least one item to remove.", "info")
            return
        
        # Confirm removal
        items_str = ", ".join([os.path.basename(p) for p in selected_items])
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove:\n{items_str}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for item_path in selected_items:
                self.file_grid_widget.remove_item(item_path)
                
                # Log activity
                self.log_activity(
                    'remove_item',
                    item_path,
                    'file_or_folder',
                    success=True,
                    details=f"Removed from protection list"
                )
            
            self.save_locked_files_config()
            self.show_message("Success", f"Removed {len(selected_items)} item(s) successfully.", "success")
    
    def save_locked_files_config(self):
        """Save locked files to unified config file"""
        from datetime import datetime
        
        config_file = os.path.join(self.get_fadcrypt_folder(), 'apps_config.json')
        
        # Temporarily unlock config file for writing
        should_relock = False
        if self.file_lock_manager and hasattr(self.file_lock_manager, 'temporarily_unlock_config'):
            self.file_lock_manager.temporarily_unlock_config('apps_config.json')
            should_relock = True
        
        try:
            # Load existing config to preserve applications
            existing_config = {"applications": [], "locked_files_and_folders": []}
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        existing_config = json.load(f)
                except:
                    pass
            
            # Build locked items array from file grid
            items_dict = self.file_grid_widget.cards
            locked_items = [
                {
                    'path': card.item_path,
                    'type': card.item_type,
                    'added_at': card.date_added or datetime.now().isoformat()
                }
                for card in items_dict.values()
            ]
            
            # Create unified config - preserve applications
            unified_config = {
                'applications': existing_config.get('applications', []),
                'locked_files_and_folders': locked_items
            }
            
            with open(config_file, 'w') as f:
                json.dump(unified_config, f, indent=4)
            print(f"Protected files config saved: {len(locked_items)} items (preserved {len(unified_config.get('applications', []))} apps)")
            
            # Update config tab display
            self.update_config_display()
        except Exception as e:
            print(f"Error saving locked files config: {e}")
        finally:
            # Always re-lock after writing
            if should_relock and self.file_lock_manager and hasattr(self.file_lock_manager, 'relock_config'):
                self.file_lock_manager.relock_config('apps_config.json')
    
    def open_stats_window(self):
        """Open the enhanced statistics dashboard window - requires password if monitoring active"""
        
        # Require password if monitoring is active
        if self.monitoring_active:
            from ui.dialogs.password_dialog import ask_password
            password = ask_password(
                "Statistics & Activity",
                "Enter your password to view statistics:",
                self.resource_path,
                style=self.password_dialog_style,
                wallpaper=self.wallpaper_choice,
                parent=self
            )
            if not (password and self.password_manager.verify_password(password)):
                # Incorrect password - deny access
                if self.system_tray:
                    self.system_tray.show_message(
                        "Access Denied",
                        "Incorrect password. Statistics window access denied.",
                        QSystemTrayIcon.MessageIcon.Warning
                    )
                return
        
        # Password verified or monitoring not active - proceed to show stats
        
        # Check if window already exists
        if hasattr(self, 'stats_window') and self.stats_window:
            # If it exists, just show it and bring to front
            self.stats_window.show()
            self.stats_window.raise_()
            self.stats_window.activateWindow()
            return
        
        try:
            from ui.windows.enhanced_stats_window import EnhancedStatsWindow
            
            # Create window without parent (independent window)
            stats_window = EnhancedStatsWindow(
                statistics_manager=self.statistics_manager,
                resource_path=self.resource_path,
                parent=None  # No parent - truly independent
            )
            
            # Store reference in main window for reuse
            self.stats_window = stats_window
            
            # Show the window (will run in main Qt thread but as independent window)
            stats_window.show()
            stats_window.raise_()
            stats_window.activateWindow()
            print("✅ Enhanced stats window opened as independent floating window")
        except Exception as e:
            print(f"Error opening enhanced stats window: {e}")
            import traceback
            traceback.print_exc()
    
    def log_activity(self, event_type: str, item_name: str | None = None, 
                    item_type: str | None = None, **kwargs):
        """Log an activity event"""
        if self.activity_manager:
            self.activity_manager.log_event(event_type, item_name, item_type, **kwargs)
        
        # Update tray stats after logging
        self.update_tray_stats_display()
    
    def update_tray_stats_display(self):
        """Update system tray with live protection stats"""
        if not self.statistics_manager or not self.system_tray:
            return
        
        try:
            stats = self.statistics_manager.get_stats()
            protection_percentage = int(stats.get('protection_percentage', 0))
            locked_items = stats.get('total_items', 0)
            unlock_count = stats.get('total_unlock_events', 0)
            
            self.system_tray.update_stats_display(
                protection_percentage=protection_percentage,
                locked_items_count=locked_items,
                unlock_count=unlock_count
            )
        except Exception as e:
            print(f"Error updating tray stats: {e}")


