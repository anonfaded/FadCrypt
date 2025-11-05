"""File Protection Authorization Dialog for FadCrypt"""

import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon


class FileProtectionAuthDialog(QDialog):
    """Dialog to explain and request authorization for file protection"""
    
    def __init__(self, parent=None, platform_name="Linux", file_count=3):
        super().__init__(parent)
        self.platform_name = platform_name
        self.file_count = file_count
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("File Protection Authorization Required")
        self.setFixedWidth(500)
        
        # Apply dark theme styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon + Title
        title_layout = QHBoxLayout()
        title_icon = QLabel("🛡️")
        title_icon.setStyleSheet("font-size: 32px;")
        title_layout.addWidget(title_icon)
        
        title_label = QLabel("File Protection Authorization")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        separator1.setStyleSheet("background-color: #444444;")
        layout.addWidget(separator1)
        
        # What will be protected
        what_label = QLabel("<b>What will be protected:</b>")
        layout.addWidget(what_label)
        
        files_list = QLabel(
            f"• <b>{self.file_count} critical files</b> will be protected:<br>"
            "  - Password file (encrypted_password.bin)<br>"
            "  - Recovery codes (recovery_codes.json)<br>"
            "  - Application config (apps_config.json)"
        )
        files_list.setStyleSheet("padding-left: 15px; color: #b0b0b0;")
        files_list.setWordWrap(True)
        layout.addWidget(files_list)
        
        # Why it's needed
        why_label = QLabel("<b>Why this is needed:</b>")
        layout.addWidget(why_label)
        
        why_text = QLabel(
            "These files contain sensitive security data. Protection prevents "
            "them from being deleted or modified while monitoring is active, "
            "ensuring your password and configuration remain intact."
        )
        why_text.setStyleSheet("padding-left: 15px; color: #b0b0b0;")
        why_text.setWordWrap(True)
        layout.addWidget(why_text)
        
        # How it works (platform-specific)
        how_label = QLabel("<b>How it works:</b>")
        layout.addWidget(how_label)
        
        if self.platform_name == "Windows":
            how_text = QLabel(
                "Files will be marked as Hidden + System + ReadOnly using Windows file attributes. "
                "This requires administrator permission via UAC (User Account Control) prompt."
            )
        else:  # Linux
            how_text = QLabel(
                "Files will be made <b>immutable</b> (chattr +i) - even root cannot delete them! "
                "This requires the elevated daemon service running with root permissions."
            )
        how_text.setStyleSheet("padding-left: 15px; color: #b0b0b0;")
        how_text.setWordWrap(True)
        layout.addWidget(how_text)
        
        # When unlocking
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        separator2.setStyleSheet("background-color: #444444;")
        layout.addWidget(separator2)
        
        unlock_warning = QLabel(
            "⚠️  <b>Note:</b> When you stop monitoring, you will be prompted again "
            "to authorize unlocking these files."
        )
        unlock_warning.setStyleSheet("color: #ff9800; padding: 10px; background-color: #2a2a2a; border-radius: 5px;")
        unlock_warning.setWordWrap(True)
        layout.addWidget(unlock_warning)
        
        # Spacer
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        skip_button = QPushButton("Skip Protection")
        skip_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #666666, stop:1 #444444);
                color: #e0e0e0;
                font-weight: bold;
                padding: 10px 25px;
                border: none;
                border-radius: 5px;
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
        skip_button.clicked.connect(self.reject)
        button_layout.addWidget(skip_button)
        
        grant_button = QPushButton("Grant Permission")
        grant_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00cc00, stop:1 #008800);
                color: white;
                font-weight: bold;
                padding: 10px 25px;
                border: none;
                border-radius: 5px;
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
        grant_button.clicked.connect(self.accept)
        grant_button.setDefault(True)
        button_layout.addWidget(grant_button)
        
        layout.addLayout(button_layout)
        
        # Set focus to grant button
        grant_button.setFocus()
