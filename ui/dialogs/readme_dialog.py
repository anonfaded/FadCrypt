"""Fullscreen Readme Dialog with animated text"""

from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont
import webbrowser


class ReadmeDialog(QDialog):
    def __init__(self, resource_path, parent=None):
        # Make it independent top-level window (no parent) so it stays visible
        super().__init__(None)
        self.resource_path = resource_path
        self.current_index = 0
        self.animation_timer = None
        
        # Full readme text
        self.full_text = (
            "Welcome to FadCrypt!\n\n"
            "Advanced cross-platform security for apps and files.\n\n"
            "Core Features:\n"
            "• Password-protected app locking & monitoring\n"
            "• Real-time file/folder protection from deletion\n"
            "• Auto-recovery if files are deleted\n"
            "• Recovery codes for password reset\n"
            "• Auto-startup after system reboot\n"
            "• Single-instance enforcement (prevent bypasses)\n\n"
            "Security:\n"
            "• System tools blocked during monitoring:\n"
            "  - Windows: Task Manager, Registry, Control Panel, CMD\n"
            "  - Linux: Terminals & system monitors\n"
            "• Encrypted password & config storage\n"
            "• Critical files protected from tampering\n"
            "• Password-secured monitoring control\n\n"
            "Additional Features:\n"
            "• Detailed statistics & activity monitoring\n"
            "• Customizable dialog styles & preferences\n"
            "• System tray integration\n"
            "• Snake game (bonus)\n\n"
            "Setup:\n"
            "1. Create password → 2. Generate recovery codes\n"
            "3. Add apps or files → 4. Start monitoring\n"
            "5. Stop only with password\n\n"
            "Love FadCrypt? Join our Discord community!\n"
            "Share feedback, get help, and connect with other users."
        )
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the fullscreen dialog UI"""
        # Set fullscreen and remove window decorations - truly independent window
        self.setWindowFlags(
            Qt.WindowType.Window |  # Independent window (not child)
            Qt.WindowType.FramelessWindowHint |  # No title bar
            Qt.WindowType.WindowStaysOnTopHint |  # Always on top
            Qt.WindowType.BypassWindowManagerHint  # Bypass window manager
        )
        # Make dialog modal
        self.setModal(True)
        
        # Show fullscreen
        self.showFullScreen()
        
        # Force activation
        self.activateWindow()
        self.raise_()
        
        # Dark background theme
        self.setStyleSheet("QDialog { background-color: #1a1a1a; }")
        
        # Main layout - use grid for image + text
        from PyQt6.QtWidgets import QGridLayout, QSizePolicy
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(20)
        
        # Content grid (text on left, image on right)
        content_grid = QGridLayout()
        content_grid.setSpacing(30)
        
        # Text label with dark theme (spans full height)
        self.text_label = QLabel("")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("QLabel { color: white; background-color: transparent; }")
        self.text_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Set font
        font = QFont("Ubuntu", 15)
        if not font.exactMatch():
            font = QFont("Arial", 15)
        self.text_label.setFont(font)
        
        # Image label - smaller size, anchored to bottom
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        self.image_label.setStyleSheet("background-color: transparent;")
        self.image_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        
        # Create text column layout (with Discord button at bottom)
        text_column_layout = QVBoxLayout()
        text_column_layout.addWidget(self.text_label, 1)
        
        # Discord Button at bottom of text column (left-aligned with text)
        discord_button = QPushButton("💬 Join Discord Community")
        discord_button.setFixedSize(220, 40)
        discord_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3366ff, stop:1 #0033cc);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
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
        discord_button.clicked.connect(lambda: webbrowser.open("https://discord.gg/kvAZvdkuuN"))
        discord_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        discord_layout = QHBoxLayout()
        discord_layout.addWidget(discord_button, alignment=Qt.AlignmentFlag.AlignLeft)
        discord_layout.addStretch()
        text_column_layout.addLayout(discord_layout)
        
        # Add text column to grid (left side)
        content_grid.addLayout(text_column_layout, 0, 0, 1, 1)
        
        # Add image to grid (bottom right)
        content_grid.addWidget(self.image_label, 0, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        content_grid.setColumnStretch(0, 1)
        content_grid.setColumnStretch(1, 0)
        
        main_layout.addLayout(content_grid, 1)
        
        # OK Button (red theme)
        self.ok_button = QPushButton("OK")
        self.ok_button.setFixedSize(150, 40)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff3333, stop:1 #cc0000);
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
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
        self.ok_button.clicked.connect(self.accept)
        
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.ok_button, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(button_layout)
        
        # Footer with FadSec Lab logo inline (all together at bottom center)
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 10, 0, 20)
        footer_layout.setSpacing(5)
        
        # Left spacer to center the footer
        footer_layout.addStretch()
        
        # "Made with ❤️ at " text
        footer_left = QLabel("Made with ❤️ at")
        footer_left.setStyleSheet("""
            QLabel {
                color: #888888;
                background-color: transparent;
                font-size: 11px;
            }
        """)
        footer_layout.addWidget(footer_left)
        
        # Load FadSec Lab footer image (inline)
        self.footer_logo = QLabel()
        self.footer_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_logo.setStyleSheet("background-color: transparent;")
        footer_layout.addWidget(self.footer_logo)
        
        # " in Pakistan 🇵🇰" text
        footer_right = QLabel("in Pakistan 🇵🇰")
        footer_right.setStyleSheet("""
            QLabel {
                color: #888888;
                background-color: transparent;
                font-size: 11px;
            }
        """)
        footer_layout.addWidget(footer_right)
        
        # Right spacer to center the footer
        footer_layout.addStretch()
        
        main_layout.addLayout(footer_layout)
        
        self.setLayout(main_layout)
        
        self.load_readme_image()
        self.load_footer_image()
        self.start_animation()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def load_footer_image(self):
        """Load and display the FadSec Lab footer image"""
        import os
        try:
            img_path = self.resource_path("img/fadsec-main-footer.png")
            print(f"\n[FOOTER IMAGE] Loading from: {img_path}")
            
            if not os.path.exists(img_path):
                print(f"[FOOTER IMAGE] ❌ File not found!")
                return
            
            pixmap = QPixmap(img_path)
            if pixmap.isNull():
                print(f"[FOOTER IMAGE] ❌ Failed to load pixmap")
                return
            
            print(f"[FOOTER IMAGE] Original size: {pixmap.width()}x{pixmap.height()}")
            
            # Scale to small size for footer
            scaled_pixmap = pixmap.scaled(
                100, 30,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            print(f"[FOOTER IMAGE] Scaled size: {scaled_pixmap.width()}x{scaled_pixmap.height()}")
            
            self.footer_logo.setPixmap(scaled_pixmap)
            
            print(f"[FOOTER IMAGE] ✅ Image loaded and displayed")
            
        except Exception as e:
            print(f"[FOOTER IMAGE] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
    def load_readme_image(self):
        """Load and display the readme image using layout"""
        import os
        try:
            img_path = self.resource_path("img/readme.png")
            print(f"\n[README IMAGE] Loading from: {img_path}")
            
            if not os.path.exists(img_path):
                print(f"[README IMAGE] ❌ File not found!")
                return
            
            pixmap = QPixmap(img_path)
            if pixmap.isNull():
                print(f"[README IMAGE] ❌ Failed to load pixmap")
                return
            
            print(f"[README IMAGE] Original size: {pixmap.width()}x{pixmap.height()}")
            
            # Scale to smaller size (250px instead of 400px)
            scaled_pixmap = pixmap.scaled(
                250, 250,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            print(f"[README IMAGE] Scaled size: {scaled_pixmap.width()}x{scaled_pixmap.height()}")
            
            self.image_label.setPixmap(scaled_pixmap)
            # Don't set fixed size - let it expand to fill column height
            
            print(f"[README IMAGE] ✅ Image loaded and displayed")
            
        except Exception as e:
            print(f"[README IMAGE] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def start_animation(self):
        """Start the typewriter animation with fast speed"""
        self.current_index = 0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate_text)
        # Fast speed: 1ms per character for quick display
        self.animation_timer.start(1)
    
    def animate_text(self):
        """Animate text character by character"""
        if self.current_index < len(self.full_text):
            self.text_label.setText(self.full_text[:self.current_index + 1])
            self.current_index += 1
        else:
            if self.animation_timer:
                self.animation_timer.stop()
                print("[README] Animation complete")
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Escape):
            self.accept()
        else:
            super().keyPressEvent(event)
