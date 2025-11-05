"""Settings Panel Component for FadCrypt"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, 
    QCheckBox, QPushButton, QFrame, QScrollArea, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap


# Signals for export/import actions
class SettingsPanelSignals(QWidget):
    """Signals for settings panel actions"""
    export_config_requested = pyqtSignal()
    import_config_requested = pyqtSignal()


class SettingsPanel(QWidget):
    """Settings panel for FadCrypt configuration with preview sections"""
    
    # Signals for settings changes
    settings_changed = pyqtSignal(dict)
    export_config_requested = pyqtSignal()
    import_config_requested = pyqtSignal()
    
    def __init__(self, resource_path_func=None, platform_name="Linux"):
        super().__init__()
        self.resource_path = resource_path_func or self._default_resource_path
        self.platform_name = platform_name  # "Linux" or "Windows"
        self.init_ui()
        
    def _default_resource_path(self, path):
        """Default resource path if none provided"""
        return os.path.join(os.path.abspath("."), path)
        
    def init_ui(self):
        """Initialize the settings panel UI"""
        # Main scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Title
        title_label = QLabel("Preferences")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Plain)
        separator1.setLineWidth(1)
        separator1.setStyleSheet("background-color: #2a2a2a; border: none; border-radius: 1px; margin: 5px 0px; max-height: 1px; min-height: 1px;")
        layout.addWidget(separator1)
        
        # Top frame (radio buttons + preview)
        top_frame = QHBoxLayout()
        
        # Left frame for radio buttons
        left_frame = QVBoxLayout()
        left_frame.setSpacing(10)
        
        # Password Dialog Style
        dialog_style_label = QLabel("🎨 Password Dialog Style")
        dialog_style_label.setStyleSheet("font-size: 11px; font-weight: bold;")
        left_frame.addWidget(dialog_style_label)
        
        self.dialog_style_group = QButtonGroup()
        self.simple_dialog_radio = QRadioButton("Simple Dialog")
        self.simple_dialog_radio.setChecked(True)
        self.simple_dialog_radio.setStyleSheet("""
            QRadioButton {
                color: #e0e0e0;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #666666;
                background-color: #2a2a2a;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #d32f2f;
                background-color: #d32f2f;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #888888;
            }
        """)
        self.dialog_style_group.addButton(self.simple_dialog_radio, 0)
        left_frame.addWidget(self.simple_dialog_radio)
        
        self.fullscreen_dialog_radio = QRadioButton("Full Screen")
        self.fullscreen_dialog_radio.setStyleSheet("""
            QRadioButton {
                color: #e0e0e0;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #666666;
                background-color: #2a2a2a;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #d32f2f;
                background-color: #d32f2f;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #888888;
            }
        """)
        self.dialog_style_group.addButton(self.fullscreen_dialog_radio, 1)
        left_frame.addWidget(self.fullscreen_dialog_radio)
        
        left_frame.addSpacing(20)
        
        # Wallpaper Choice
        wallpaper_label = QLabel("🖼️  Full Screen Wallpaper")
        wallpaper_label.setStyleSheet("font-size: 11px; font-weight: bold;")
        left_frame.addWidget(wallpaper_label)
        
        self.wallpaper_group = QButtonGroup()
        
        # Common radio button style for wallpaper options
        wallpaper_radio_style = """
            QRadioButton {
                color: #e0e0e0;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #666666;
                background-color: #2a2a2a;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #d32f2f;
                background-color: #d32f2f;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #888888;
            }
        """
        
        self.lab_wallpaper_radio = QRadioButton("Lab (Default)")
        self.lab_wallpaper_radio.setChecked(True)
        self.lab_wallpaper_radio.setStyleSheet(wallpaper_radio_style)
        self.wallpaper_group.addButton(self.lab_wallpaper_radio, 0)
        left_frame.addWidget(self.lab_wallpaper_radio)
        
        self.hacker_wallpaper_radio = QRadioButton("H4ck3r")
        self.hacker_wallpaper_radio.setStyleSheet(wallpaper_radio_style)
        self.wallpaper_group.addButton(self.hacker_wallpaper_radio, 1)
        left_frame.addWidget(self.hacker_wallpaper_radio)
        
        self.binary_wallpaper_radio = QRadioButton("Binary")
        self.binary_wallpaper_radio.setStyleSheet(wallpaper_radio_style)
        self.wallpaper_group.addButton(self.binary_wallpaper_radio, 2)
        left_frame.addWidget(self.binary_wallpaper_radio)
        
        self.encrypted_wallpaper_radio = QRadioButton("Encryptedddddd")
        self.encrypted_wallpaper_radio.setStyleSheet(wallpaper_radio_style)
        self.wallpaper_group.addButton(self.encrypted_wallpaper_radio, 3)
        left_frame.addWidget(self.encrypted_wallpaper_radio)
        
        left_frame.addStretch()
        
        # Right frame for preview
        right_frame = QVBoxLayout()
        right_frame.setSpacing(10)
        
        preview_label = QLabel("👁️  Dialog Preview")
        preview_label.setStyleSheet("font-size: 11px; font-weight: bold;")
        right_frame.addWidget(preview_label)
        
        # Preview frame - no border, just dark background
        self.preview_frame = QFrame()
        self.preview_frame.setFrameStyle(QFrame.Shape.NoFrame)
        self.preview_frame.setMinimumSize(400, 250)
        self.preview_frame.setMaximumSize(400, 250)
        self.preview_frame.setStyleSheet("background-color: #1a1a1a; border: none;")
        
        preview_layout = QVBoxLayout(self.preview_frame)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Don't use setScaledContents - we'll handle scaling manually with SmoothTransformation
        preview_layout.addWidget(self.preview_label)
        
        right_frame.addWidget(self.preview_frame)
        right_frame.addStretch()
        
        top_frame.addLayout(left_frame, 1)
        top_frame.addLayout(right_frame, 2)
        
        layout.addLayout(top_frame)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Plain)
        separator2.setLineWidth(1)
        separator2.setStyleSheet("background-color: #2a2a2a; border: none; border-radius: 1px; margin: 5px 0px; max-height: 1px; min-height: 1px;")
        layout.addWidget(separator2)
        
        # Bottom frame for checkboxes and info
        bottom_frame = QVBoxLayout()
        bottom_frame.setSpacing(10)
        
        # Disable Main Loopholes
        loopholes_title = QLabel("🔒 Disable Main Loopholes")
        loopholes_title.setStyleSheet("font-size: 11px; font-weight: bold;")
        bottom_frame.addWidget(loopholes_title)
        
        self.lock_tools_checkbox = QCheckBox(
            self._get_lock_tools_checkbox_text()
        )
        self.lock_tools_checkbox.setChecked(False)  # Default: Disabled for safety
        self.lock_tools_checkbox.setStyleSheet("""
            QCheckBox {
                color: #e0e0e0;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #666666;
                border-radius: 3px;
                background-color: #2a2a2a;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #d32f2f;
                background-color: #d32f2f;
                image: url(none);
            }
            QCheckBox::indicator:hover {
                border: 2px solid #888888;
            }
        """)
        bottom_frame.addWidget(self.lock_tools_checkbox)
        
        # Info text below checkbox in darker color - platform-specific
        lock_tools_info = QLabel(self._get_lock_tools_info_text())
        lock_tools_info.setStyleSheet("color: #666666; font-size: 11px; padding-left: 26px;")
        lock_tools_info.setWordWrap(True)
        bottom_frame.addWidget(lock_tools_info)
        
        # File Protection Section
        separator_file_protection = QFrame()
        separator_file_protection.setFrameShape(QFrame.Shape.HLine)
        separator_file_protection.setFrameShadow(QFrame.Shadow.Plain)
        separator_file_protection.setLineWidth(1)
        separator_file_protection.setStyleSheet("background-color: #2a2a2a; border: none; border-radius: 1px; margin: 5px 0px; max-height: 1px; min-height: 1px;")
        bottom_frame.addWidget(separator_file_protection)
        
        file_protection_title = QLabel("🛡️  Critical File Protection")
        file_protection_title.setStyleSheet("font-size: 11px; font-weight: bold;")
        bottom_frame.addWidget(file_protection_title)
        
        self.file_protection_checkbox = QCheckBox(
            "Enable file protection during monitoring (Recommended)"
        )
        self.file_protection_checkbox.setChecked(True)  # Default: Enabled
        self.file_protection_checkbox.setStyleSheet("""
            QCheckBox {
                color: #e0e0e0;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #666666;
                border-radius: 3px;
                background-color: #2a2a2a;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #d32f2f;
                background-color: #d32f2f;
                image: url(none);
            }
            QCheckBox::indicator:hover {
                border: 2px solid #888888;
            }
        """)
        bottom_frame.addWidget(self.file_protection_checkbox)
        
        # Info text below checkbox
        file_protection_info = QLabel(
            self._get_file_protection_info_text()
        )
        file_protection_info.setStyleSheet("color: #666666; font-size: 11px; padding-left: 26px;")
        file_protection_info.setWordWrap(True)
        bottom_frame.addWidget(file_protection_info)

        # Process Scanning Interval Section
        separator_scanning = QFrame()
        separator_scanning.setFrameShape(QFrame.Shape.HLine)
        separator_scanning.setFrameShadow(QFrame.Shadow.Plain)
        separator_scanning.setLineWidth(1)
        separator_scanning.setStyleSheet("background-color: #2a2a2a; border: none; border-radius: 1px; margin: 5px 0px; max-height: 1px; min-height: 1px;")
        bottom_frame.addWidget(separator_scanning)

        scanning_title = QLabel("⚡ Process Scanning Interval")
        scanning_title.setStyleSheet("font-size: 11px; font-weight: bold;")
        bottom_frame.addWidget(scanning_title)

        # Scanning interval input
        from PyQt6.QtWidgets import QDoubleSpinBox
        scanning_layout = QHBoxLayout()

        scanning_layout.addWidget(QLabel("Scan every"))
        self.scanning_interval_spinbox = QDoubleSpinBox()
        self.scanning_interval_spinbox.setRange(0.5, 5.0)  # 0.5 to 5 seconds
        self.scanning_interval_spinbox.setSingleStep(0.5)
        self.scanning_interval_spinbox.setValue(1.0)  # Default: 1.0 seconds
        self.scanning_interval_spinbox.setSuffix(" seconds")
        self.scanning_interval_spinbox.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 4px;
                min-width: 150px;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                background-color: #444444;
                border: none;
                width: 16px;
            }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #555555;
            }
        """)
        scanning_layout.addWidget(self.scanning_interval_spinbox)
        scanning_layout.addStretch()
        bottom_frame.addLayout(scanning_layout)

        # Info text for scanning interval
        scanning_info = QLabel(
            "How often FadCrypt scans for running applications (0.5-5.0 seconds).\n"
            "⚠️  Lower values = faster detection but higher CPU usage and battery drain.\n"
            "⚠️  Higher values = slower detection but better performance.\n"
            "Default: 1.0 seconds (recommended for most users)."
        )
        scanning_info.setStyleSheet("color: #666666; font-size: 11px; padding-left: 0px;")
        scanning_info.setWordWrap(True)
        bottom_frame.addWidget(scanning_info)

        # Uninstall Cleanup
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.Shape.HLine)
        separator3.setFrameShadow(QFrame.Shadow.Plain)
        separator3.setLineWidth(1)
        separator3.setStyleSheet("background-color: #2a2a2a; border: none; border-radius: 1px; margin: 5px 0px; max-height: 1px; min-height: 1px;")
        bottom_frame.addWidget(separator3)
        
        # Recovery Codes Section
        recovery_title = QLabel("🔐 Recovery Codes")
        recovery_title.setStyleSheet("font-size: 11px; font-weight: bold;")
        bottom_frame.addWidget(recovery_title)
        
        recovery_info = QLabel(
            "Generate or regenerate recovery codes for password recovery.\n"
            "Keep these codes safe - they allow you to reset your password if forgotten."
        )
        recovery_info.setStyleSheet("color: #888888;")
        recovery_info.setWordWrap(True)
        bottom_frame.addWidget(recovery_info)
        
        recovery_button = QPushButton("Generate Recovery Codes")
        recovery_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff3333, stop:1 #cc0000);
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff5555, stop:1 #dd0000);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #cc0000, stop:1 #990000);
            }
        """)
        recovery_button.clicked.connect(lambda: self.on_generate_recovery_codes())
        recovery_button.setMaximumWidth(250)
        bottom_frame.addWidget(recovery_button)
        
        bottom_frame.addSpacing(20)
        
        # Context Menu Refresh (Windows only)
        if self.platform_name == "Windows":
            context_menu_title = QLabel("🖱️ Context Menu")
            context_menu_title.setStyleSheet("font-size: 11px; font-weight: bold;")
            bottom_frame.addWidget(context_menu_title)
            
            context_menu_info = QLabel(
                "Refresh Windows Explorer context menu entries for Lock/Unlock options.\n"
                "Use this if right-click options are missing or not working."
            )
            context_menu_info.setStyleSheet("color: #888888;")
            context_menu_info.setWordWrap(True)
            bottom_frame.addWidget(context_menu_info)
            
            context_menu_button = QPushButton("Refresh Context Menu")
            context_menu_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3366ff, stop:1 #0033cc);
                    color: white;
                    font-weight: bold;
                    padding: 8px 20px;
                    border-radius: 5px;
                    border: none;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5588ff, stop:1 #0055ff);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #0033cc, stop:1 #001a99);
                }
            """)
            context_menu_button.clicked.connect(lambda: self.on_refresh_context_menu())
            context_menu_button.setMaximumWidth(200)
            bottom_frame.addWidget(context_menu_button)
            
            bottom_frame.addSpacing(20)
        
        # Dangerous Operations Section - Encryption
        separator_dangerous = QFrame()
        separator_dangerous.setFrameShape(QFrame.Shape.HLine)
        separator_dangerous.setFrameShadow(QFrame.Shadow.Sunken)
        bottom_frame.addWidget(separator_dangerous)
        
        dangerous_title = QLabel("⚠️  Dangerous Operations")
        dangerous_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #ff6b6b;")
        bottom_frame.addWidget(dangerous_title)
        
        # Platform-specific checkbox text
        if self.platform_name == "Windows":
            checkbox_text = "Enable File/Folder Encryption on Lock (stored as .fadcrypt binary)"
        else:  # Linux
            checkbox_text = "Enable File/Folder Encryption on Lock (stored as .fadcrypt binary)"
        
        self.encryption_checkbox = QCheckBox(checkbox_text)
        self.encryption_checkbox.setChecked(False)  # Default: Disabled for safety
        self.encryption_checkbox.setStyleSheet("""
            QCheckBox {
                color: #e0e0e0;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #666666;
                border-radius: 3px;
                background-color: #2a2a2a;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #d32f2f;
                background-color: #d32f2f;
                image: url(none);
            }
            QCheckBox::indicator:hover {
                border: 2px solid #888888;
            }
        """)
        bottom_frame.addWidget(self.encryption_checkbox)
        
        # Warning text below checkbox
        if self.platform_name == "Windows":
            encryption_warning_text = (
                "⚠️  When disabled (default): Files locked via ACL only, readable when unlocked.\n"
                "⚠️  When enabled: Files encrypted to .fadcrypt (AES-256), stored as binary blob.\n"
                "⚠️  ACL still applied to .fadcrypt file for dual-layer protection.\n"
                "⚠️  If password forgotten: Use recovery codes to reset password and unlock encrypted files.\n"
                "⚠️  Keep recovery codes safe - encryption is irreversible without them."
            )
        else:  # Linux
            encryption_warning_text = (
                "⚠️  When disabled (default): Files locked via permissions (000) + immutable flag.\n"
                "⚠️  When enabled: Files encrypted to .fadcrypt (AES-256), stored as binary blob.\n"
                "⚠️  Permissions (000) + immutable still applied to .fadcrypt for dual-layer protection.\n"
                "⚠️  If password forgotten: Use recovery codes to reset password and unlock encrypted files.\n"
                "⚠️  Keep recovery codes safe - encryption is irreversible without them."
            )
        
        encryption_warning = QLabel(encryption_warning_text)
        encryption_warning.setStyleSheet("color: #ffb74d; font-size: 11px; padding-left: 26px; line-height: 1.6; font-weight: 500;")
        encryption_warning.setWordWrap(True)
        bottom_frame.addWidget(encryption_warning)
        
        bottom_frame.addSpacing(20)
        
        cleanup_title = QLabel("🔧 Uninstall Cleanup")
        cleanup_title.setStyleSheet("font-size: 11px; font-weight: bold;")
        bottom_frame.addWidget(cleanup_title)
        
        cleanup_info = QLabel(
            "🧹 Complete system cleanup before uninstalling FadCrypt.\n\n"
            "This will:\n"
            "• Stop any active file monitoring\n"
            "• Re-enable disabled system tools (Command Prompt, Task Manager, etc.)\n"
            "• Remove FadCrypt from Windows startup\n"
            "• Remove Windows Explorer context menu entries\n"
            "• Delete all FadCrypt data directories and files\n"
            "• Restart File Explorer to apply changes\n\n"
            "Run this before uninstalling to ensure a clean system state."
        )
        cleanup_info.setStyleSheet("color: #888888;")
        cleanup_info.setWordWrap(True)
        bottom_frame.addWidget(cleanup_info)
        
        cleanup_button = QPushButton("Run Uninstall Cleanup")
        cleanup_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff3333, stop:1 #cc0000);
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff5555, stop:1 #dd0000);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #cc0000, stop:1 #990000);
            }
        """)
        cleanup_button.clicked.connect(lambda: self.on_cleanup_clicked())
        cleanup_button.setMaximumWidth(200)
        bottom_frame.addWidget(cleanup_button)
        
        bottom_frame.addSpacing(20)
        
        # Configuration Backup Section
        backup_title = QLabel("💾 Configuration Backup")
        backup_title.setStyleSheet("font-size: 11px; font-weight: bold;")
        bottom_frame.addWidget(backup_title)
        
        backup_info = QLabel(
            "Export your configuration (applications, locked files, settings) to a JSON file.\n"
            "Import a previously exported configuration to restore your setup.\n"
            "Useful for backup, migration, or sharing setups across devices."
        )
        backup_info.setStyleSheet("color: #888888;")
        backup_info.setWordWrap(True)
        bottom_frame.addWidget(backup_info)
        
        # Export/Import buttons in horizontal layout
        backup_buttons = QHBoxLayout()
        backup_buttons.setSpacing(10)
        
        export_button = QPushButton("📥 Export Config")
        export_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #666666, stop:1 #444444);
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #777777, stop:1 #555555);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #555555, stop:1 #333333);
            }
        """)
        export_button.clicked.connect(self.on_export_config_clicked)
        export_button.setMaximumWidth(150)
        backup_buttons.addWidget(export_button)
        
        import_button = QPushButton("📤 Import Config")
        import_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00cc00, stop:1 #008800);
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ff00, stop:1 #00aa00);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #008800, stop:1 #005500);
            }
        """)
        import_button.clicked.connect(self.on_import_config_clicked)
        import_button.setMaximumWidth(150)
        backup_buttons.addWidget(import_button)
        
        backup_buttons.addStretch()
        bottom_frame.addLayout(backup_buttons)
        layout.addLayout(bottom_frame)
        layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
        # Connect signals
        self.dialog_style_group.buttonClicked.connect(self.on_settings_changed)
        self.wallpaper_group.buttonClicked.connect(self.on_settings_changed)
        self.lock_tools_checkbox.stateChanged.connect(self.on_settings_changed)
        self.file_protection_checkbox.stateChanged.connect(self.on_settings_changed)
        self.scanning_interval_spinbox.valueChanged.connect(self.on_settings_changed)
        self.encryption_checkbox.stateChanged.connect(self.on_settings_changed)
        
        # Initial preview update
        self.update_preview()
        
    def update_preview(self):
        """Update the preview image based on current settings"""
        dialog_style = "simple" if self.simple_dialog_radio.isChecked() else "fullscreen"
        wallpaper = self.get_wallpaper_choice()
        
        # Determine preview path based on selection
        if dialog_style == "simple":
            preview_path = self.resource_path("img/preview1.png")
        else:  # fullscreen
            if wallpaper == "default":
                preview_path = self.resource_path("img/wall1.png")
            elif wallpaper == "H4ck3r":
                preview_path = self.resource_path("img/wall2.png")
            elif wallpaper == "Binary":
                preview_path = self.resource_path("img/wall3.png")
            elif wallpaper == "encrypted":
                preview_path = self.resource_path("img/wall4.png")
            else:
                preview_path = self.resource_path("img/preview2.png")
        
        # Load and display preview image
        if os.path.exists(preview_path):
            pixmap = QPixmap(preview_path)
            scaled_pixmap = pixmap.scaled(400, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)
        else:
            self.preview_label.setText(f"Preview not found:\n{os.path.basename(preview_path)}")
            self.preview_label.setStyleSheet("color: #999; font-size: 12px;")
        
    def on_settings_changed(self):
        """Emit settings changed signal and update preview"""
        settings = self.get_settings()
        self.settings_changed.emit(settings)
        self.update_preview()
        
    def on_generate_recovery_codes(self):
        """Handle recovery codes button click"""
        # To be implemented by main window
        pass
    
    def on_refresh_context_menu(self):
        """Handle context menu refresh button click"""
        # To be implemented by main window
        pass
    
    def on_cleanup_clicked(self):
        """Handle cleanup button click"""
        # To be implemented by main window
        pass
        
    def on_export_config_clicked(self):
        """Handle export config button click"""
        self.export_config_requested.emit()
    
    def on_import_config_clicked(self):
        """Handle import config button click"""
        self.import_config_requested.emit()
        
    def get_settings(self):
        """Get current settings as dictionary"""
        return {
            'dialog_style': 'simple' if self.simple_dialog_radio.isChecked() else 'fullscreen',
            'wallpaper': self.get_wallpaper_choice(),
            'lock_tools': self.lock_tools_checkbox.isChecked(),
            'file_protection_enabled': self.file_protection_checkbox.isChecked(),
            'scanning_interval': self.scanning_interval_spinbox.value(),
            'encryption_enabled': self.encryption_checkbox.isChecked()
        }
        
    def get_wallpaper_choice(self):
        """Get selected wallpaper"""
        if self.lab_wallpaper_radio.isChecked():
            return 'default'
        elif self.hacker_wallpaper_radio.isChecked():
            return 'H4ck3r'
        elif self.binary_wallpaper_radio.isChecked():
            return 'Binary'
        elif self.encrypted_wallpaper_radio.isChecked():
            return 'encrypted'
        return 'default'
        
    def set_settings(self, settings):
        """Set settings from dictionary"""
        dialog_style = settings.get('dialog_style', 'simple')
        if dialog_style == 'fullscreen':
            self.fullscreen_dialog_radio.setChecked(True)
        else:
            self.simple_dialog_radio.setChecked(True)
            
        wallpaper = settings.get('wallpaper', 'default')
        if wallpaper == 'H4ck3r':
            self.hacker_wallpaper_radio.setChecked(True)
        elif wallpaper == 'Binary':
            self.binary_wallpaper_radio.setChecked(True)
        elif wallpaper == 'encrypted':
            self.encrypted_wallpaper_radio.setChecked(True)
        else:
            self.lab_wallpaper_radio.setChecked(True)
            
        self.lock_tools_checkbox.setChecked(settings.get('lock_tools', False))  # Default: False for safety
        self.file_protection_checkbox.setChecked(settings.get('file_protection_enabled', True))  # Default: True (enabled)
        self.scanning_interval_spinbox.setValue(settings.get('scanning_interval', 1.0))  # Default: 1.0 seconds
        self.encryption_checkbox.setChecked(settings.get('encryption_enabled', False))  # Default: False for safety
        
        self.on_settings_changed()
    
    def apply_settings(self, settings):
        """Alias for set_settings - apply settings from dictionary"""
        self.set_settings(settings)
    
    def _get_lock_tools_checkbox_text(self):
        """Get platform-specific checkbox text for lock tools"""
        if self.platform_name == "Windows":
            return "Disable Command Prompt, Registry Editor, Control Panel, msconfig, and Task Manager during monitoring."
        else:  # Linux
            return "Disable common terminals and system monitors during monitoring."
    
    def _get_lock_tools_info_text(self):
        """Get platform-specific info text for lock tools"""
        if self.platform_name == "Windows":
            return (
                "Enable this to COMPLETELY LOCK OUT these tools (no access at all). "
                "For password-protected access instead, keep this DISABLED and add tools to the Application tab. "
                "(Tools: Command Prompt, Registry Editor, Control Panel, msconfig, Task Manager)"
            )
        else:  # Linux
            return (
                "Enable this to COMPLETELY LOCK OUT these tools (no access at all). "
                "For password-protected access instead, keep this DISABLED and add terminals to the Application tab. "
                "(Tools: gnome-terminal, konsole, xterm, gnome-system-monitor, htop, top)"
            )
    
    def _get_file_protection_info_text(self):
        """Get platform-specific info text for file protection"""
        if self.platform_name == "Windows":
            return (
                "Protects critical files (config, password, recovery codes) from deletion/modification during monitoring. "
                "Files are made Hidden + System + ReadOnly. "
                "When you stop monitoring, files will be automatically unlocked. "
                "⚠️  Note: Requires administrator permission to protect and unprotect files."
            )
        else:  # Linux
            return (
                "Protects critical files (config, password, recovery codes) from deletion/modification during monitoring. "
                "Files are made immutable (chattr +i) - even root cannot delete them! "
                "When you stop monitoring, files will be automatically unlocked. "
            )
