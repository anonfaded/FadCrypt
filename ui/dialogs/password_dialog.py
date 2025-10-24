"""Password Dialog for FadCrypt"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFrame, QProgressBar, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont, QIcon


class PasswordDialog(QDialog):
    """Custom password dialog with optional fullscreen wallpaper background"""
    
    def __init__(self, title, prompt, resource_path, fullscreen=False, wallpaper_choice=None, parent=None, show_forgot_password=True, has_recovery_codes=True):
        # For fullscreen mode, don't use parent to avoid being hidden when parent is minimized
        if fullscreen:
            super().__init__(None)  # Independent top-level window
        else:
            super().__init__(parent)
        
        self.resource_path = resource_path
        self.fullscreen = fullscreen
        self.wallpaper_choice = wallpaper_choice
        self.password_value = None
        self.show_forgot_password = show_forgot_password
        self.has_recovery_codes = has_recovery_codes
        
        self.setWindowTitle(title)
        
        # Set window icon
        icon_path = self.resource_path('img/icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.init_ui(title, prompt)
        
    def init_ui(self, title, prompt):
        """Initialize the password dialog UI"""
        if self.fullscreen:
            # Fullscreen mode with wallpaper - truly independent top-level window
            self.setWindowFlags(
                Qt.WindowType.Window |  # Independent window (not child)
                Qt.WindowType.FramelessWindowHint |  # No title bar
                Qt.WindowType.WindowStaysOnTopHint  # Always on top
                # Removed BypassWindowManagerHint as it can cause positioning issues
            )
            # Make dialog modal to block all other windows
            self.setModal(True)
            
            # Get screen size and manually set fullscreen
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                print(f"[Fullscreen] Setting dialog to screen geometry: {screen_geometry.width()}x{screen_geometry.height()}")
                self.setGeometry(screen_geometry)  # Set to full screen geometry
                self.move(0, 0)  # Ensure positioned at top-left
                self.show()  # Show first, then set wallpaper
                print(f"[Fullscreen] Dialog geometry after show: {self.geometry()}")
            else:
                # Fallback if no screen found
                print("[Fullscreen] No primary screen found, using showFullScreen()")
                self.showFullScreen()
            
            # Force activation and raise to top
            self.activateWindow()
            self.raise_()
            
            print(f"[Fullscreen] Dialog visible: {self.isVisible()}, active: {self.isActiveWindow()}")
            print(f"[Fullscreen] Dialog modal: {self.isModal()}")
            
            # Wallpaper will be set after UI initialization
        else:
            # Simple dialog mode - responsive design
            self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
            # Don't set size yet - let it calculate based on content
            self.setStyleSheet("QDialog { background-color: #1a1a1a; }")
        
        # Main layout
        main_layout = QVBoxLayout()
        
        if self.fullscreen:
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
        
        # Content frame - compact dark theme without border
        content_frame = QFrame()
        if self.fullscreen:
            print(f"[Fullscreen] Creating content frame for fullscreen mode")
            content_frame.setStyleSheet("""
                QFrame {
                    background-color: #1e1e1e;
                    border: none;
                    border-radius: 15px;
                }
            """)
        else:
            content_frame.setStyleSheet("""
                QFrame {
                    background-color: #1e1e1e;
                    border: none;
                    border-radius: 10px;
                }
            """)
        
        if self.fullscreen:
            # Set minimum size but allow dynamic expansion
            content_frame.setMinimumSize(440, 240)
            content_frame.setMaximumWidth(600)  # Max width for readability
        
        content_layout = QVBoxLayout(content_frame)
        if self.fullscreen:
            content_layout.setContentsMargins(40, 30, 40, 30)  # More padding for fullscreen
            content_layout.setSpacing(15)  # More spacing for fullscreen
        else:
            content_layout.setContentsMargins(30, 25, 30, 25)
            content_layout.setSpacing(12)
        
        # Title label - compact
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel { 
                font-size: 16px; 
                font-weight: bold; 
                color: #ffffff; 
                border: none;
                padding: 0;
                margin: 0;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title_label)
        
        # Prompt label - responsive with proper wrapping
        prompt_label = QLabel(prompt)
        prompt_label.setWordWrap(True)
        prompt_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )
        # Set maximum width for text wrapping based on mode
        if self.fullscreen:
            prompt_label.setMaximumWidth(520)  # Wider for fullscreen
        else:
            prompt_label.setMaximumWidth(380)
        
        prompt_label.setStyleSheet("""
            QLabel { 
                font-size: 11px; 
                color: #a0a0a0; 
                border: none;
                padding: 8px 0;
                margin: 0;
                line-height: 1.5;
            }
        """)
        prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(prompt_label)
        
        # Spacer
        content_layout.addSpacing(8)
        
        # Password input - compact design with red theme
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setFixedHeight(38)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 0 14px;
                font-size: 13px;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #d32f2f;
                background-color: #2e2e2e;
            }
            QLineEdit::placeholder {
                color: #666666;
            }
        """)
        self.password_input.returnPressed.connect(self.on_ok)
        content_layout.addWidget(self.password_input)
        
        # Password strength meter - only show during password creation
        if title and ("Create" in title or "New Password" in title):
            # Strength meter container
            strength_layout = QVBoxLayout()
            strength_layout.setSpacing(4)
            strength_layout.setContentsMargins(0, 8, 0, 0)
            
            # Strength meter label
            self.strength_label = QLabel("Password Strength: -")
            self.strength_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #888888;
                    border: none;
                }
            """)
            strength_layout.addWidget(self.strength_label)
            
            # Strength meter bar
            self.strength_meter = QProgressBar()
            self.strength_meter.setFixedHeight(8)
            self.strength_meter.setTextVisible(False)
            self.strength_meter.setRange(0, 100)
            self.strength_meter.setValue(0)
            self.strength_meter.setStyleSheet("""
                QProgressBar {
                    border: none;
                    background-color: #2b2b2b;
                    border-radius: 4px;
                }
                QProgressBar::chunk {
                    background-color: #666666;
                    border-radius: 4px;
                }
            """)
            strength_layout.addWidget(self.strength_meter)
            
            content_layout.addLayout(strength_layout)
            
            # Connect password input to strength meter
            self.password_input.textChanged.connect(self.update_password_strength)
        else:
            self.strength_label = None
            self.strength_meter = None
        
        # Spacer before buttons
        content_layout.addSpacing(10)
        
        # "Forgot Password?" link - only show if enabled
        if self.show_forgot_password:
            forgot_link = QPushButton("🔑 Forgot Password?")
            forgot_link.setFlat(True)
            forgot_link.setCursor(self.cursor())
            forgot_link.setStyleSheet("""
                QPushButton {
                    color: #d32f2f;
                    border: none;
                    background: transparent;
                    padding: 0;
                    font-size: 12px;
                    text-decoration: none;
                }
                QPushButton:hover {
                    color: #b71c1c;
                }
            """)
            forgot_link.clicked.connect(self.on_forgot_password)
            forgot_layout = QHBoxLayout()
            forgot_layout.addStretch()
            forgot_layout.addWidget(forgot_link)
            forgot_layout.addStretch()
            content_layout.addLayout(forgot_layout)
            
            # Warning if no recovery codes
            if not self.has_recovery_codes:
                warning_label = QLabel(
                    "WARN  No recovery codes generated!\n"
                    "Generate them from Settings → Generate Recovery Codes"
                )
                warning_label.setStyleSheet("""
                    QLabel {
                        color: #ff9800;
                        font-size: 11px;
                        background-color: #2a2a2a;
                        border: 1px solid #ff9800;
                        border-radius: 4px;
                        padding: 8px;
                    }
                """)
                warning_label.setWordWrap(True)
                warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                content_layout.addWidget(warning_label)
            
            content_layout.addSpacing(10)
        
        # Buttons - compact design
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(120, 36)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #464646;
            }
            QPushButton:pressed {
                background-color: #2e2e2e;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        # OK button - dynamic text based on dialog type
        if title and ("Create" in title or "New Password" in title):
            button_text = "Create"
        else:
            button_text = "Unlock"
        
        ok_button = QPushButton(button_text)
        ok_button.setFixedSize(120, 36)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
            QPushButton:pressed {
                background-color: #9a0007;
            }
        """)
        ok_button.clicked.connect(self.on_ok)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        
        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(content_frame)
        self.setLayout(main_layout)
        
        if self.fullscreen:
            print(f"[Fullscreen] Content frame added to layout, frame size: {content_frame.size()}")
            print(f"[Fullscreen] Main layout alignment: {main_layout.alignment()}")
        else:
            # Adjust dialog size to fit content (only for non-fullscreen mode)
            self.adjustSize()
        
        if self.fullscreen:
            print(f"[Fullscreen] Skipping size adjustment for fullscreen mode")
        else:
            # Set minimum size after calculating content size (only for non-fullscreen mode)
            min_width = max(440, self.width())
            min_height = max(240, self.height())
            self.setMinimumSize(min_width, min_height)
            self.resize(min_width, min_height)
        
        # Center dialog on screen (must be done after setLayout and adjustSize)
        if not self.fullscreen:
            self.center_on_screen()
        
        # Focus on password input
        self.password_input.setFocus()
        
        # For fullscreen mode, set wallpaper after everything is initialized
        if self.fullscreen:
            print(f"[Fullscreen] Setting wallpaper after UI initialization")
            self.set_wallpaper_background()
    
    def center_on_screen(self):
        """Center the dialog on the screen"""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            print(f"[PasswordDialog] Centering dialog at ({x}, {y})")
            print(f"   Screen size: {screen_geometry.width()}x{screen_geometry.height()}")
            print(f"   Dialog size: {self.width()}x{self.height()}")
            self.move(x, y)
        else:
            print("[PasswordDialog] WARN  No screen found, cannot center")
        
    def set_wallpaper_background(self):
        """Set wallpaper background for fullscreen mode"""
        print(f"[Wallpaper] Setting wallpaper background, choice: {self.wallpaper_choice}")
        try:
            # Map wallpaper choices to actual wallpaper image files (.jpg, not preview .png)
            wallpaper_map = {
                'default': 'wall1.jpg',
                'H4ck3r': 'wall2.jpg',
                'Binary': 'wall3.jpg',
                'encrypted': 'wall4.jpg'
            }
            
            wallpaper_file = wallpaper_map.get(self.wallpaper_choice or 'default', 'wall1.jpg')
            wallpaper_path = self.resource_path(f"img/{wallpaper_file}")
            
            pixmap = QPixmap(wallpaper_path)
            if not pixmap.isNull():
                # Get screen size
                screen = self.screen()
                if screen:
                    screen_size = screen.size()
                    screen_width = screen_size.width()
                    screen_height = screen_size.height()
                else:
                    screen_width = self.width()
                    screen_height = self.height()
                
                # Scale to fit screen while maintaining aspect ratio (centered, not tiled)
                scaled_pixmap = pixmap.scaled(
                    screen_width, 
                    screen_height, 
                    Qt.AspectRatioMode.KeepAspectRatio,  # Maintain aspect ratio, centered
                    Qt.TransformationMode.SmoothTransformation
                )
                
                # Create a full-screen pixmap with black background
                full_pixmap = QPixmap(screen_width, screen_height)
                full_pixmap.fill(Qt.GlobalColor.black)
                
                # Draw the scaled image centered on the black background
                from PyQt6.QtGui import QPainter
                painter = QPainter(full_pixmap)
                x = (screen_width - scaled_pixmap.width()) // 2
                y = (screen_height - scaled_pixmap.height()) // 2
                painter.drawPixmap(x, y, scaled_pixmap)
                painter.end()
                
                # Set as background using palette
                from PyQt6.QtGui import QPalette, QBrush
                palette = self.palette()
                palette.setBrush(QPalette.ColorRole.Window, QBrush(full_pixmap))
                self.setPalette(palette)
                
                # Also try setting stylesheet as backup
                self.setStyleSheet("")
                
                print(f"[Wallpaper] Applied wallpaper via palette to dialog")
                print(f"[Wallpaper] Loaded: {wallpaper_file}")
                print(f"   Original: {pixmap.width()}x{pixmap.height()}")
                print(f"   Scaled: {scaled_pixmap.width()}x{scaled_pixmap.height()}")
                print(f"   Centered at: ({x}, {y})")
        except Exception as e:
            print(f"Error loading wallpaper: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to dark background
            self.setStyleSheet("QDialog { background-color: #1a1a1a; }")
    
    def calculate_password_strength(self, password: str) -> tuple[int, str, str]:
        """
        Calculate password strength score and return (score, label, color).
        
        Args:
            password: Password to evaluate
            
        Returns:
            Tuple of (score 0-100, strength label, color hex)
        """
        if not password:
            return (0, "-", "#666666")
        
        score = 0
        length = len(password)
        
        # Length scoring (0-40 points)
        if length >= 1:
            score += min(length * 3, 40)
        
        # Character variety (0-60 points)
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        variety_score = 0
        if has_lower: variety_score += 10
        if has_upper: variety_score += 10
        if has_digit: variety_score += 15
        if has_special: variety_score += 25
        
        score += variety_score
        
        # Cap at 100
        score = min(score, 100)
        
        # Determine strength label and color
        if score < 25:
            return (score, "Very Weak", "#d32f2f")  # Red
        elif score < 45:
            return (score, "Weak", "#ff5722")  # Deep Orange
        elif score < 65:
            return (score, "Fair", "#ff9800")  # Orange
        elif score < 85:
            return (score, "Good", "#4caf50")  # Green
        else:
            return (score, "Strong", "#2e7d32")  # Dark Green
    
    def update_password_strength(self, text: str):
        """Update password strength meter based on input"""
        if self.strength_meter and self.strength_label:
            score, label, color = self.calculate_password_strength(text)
            
            # Update meter value
            self.strength_meter.setValue(score)
            
            # Update meter color
            self.strength_meter.setStyleSheet(f"""
                QProgressBar {{
                    border: none;
                    background-color: #2b2b2b;
                    border-radius: 4px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 4px;
                }}
            """)
            
            # Update label
            self.strength_label.setText(f"Password Strength: {label}")
            self.strength_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 11px;
                    color: {color};
                    border: none;
                    font-weight: bold;
                }}
            """)
    
    def on_ok(self):
        """Handle OK button click"""
        self.password_value = self.password_input.text()
        if self.password_value:
            self.accept()
    
    def on_forgot_password(self):
        """Handle forgot password - user needs to recover with code"""
        self.password_value = "RECOVER"  # Special marker for recovery flow
        self.accept()
    
    def get_password(self):
        """Get the entered password"""
        return self.password_value
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


def ask_password(title, prompt, resource_path, style="simple", wallpaper="default", parent=None, show_forgot_password=True, has_recovery_codes=True):
    """
    Helper function to show password dialog.
    
    Args:
        title: Dialog title
        prompt: Prompt text
        resource_path: Function to get resource paths
        style: "simple" or "fullscreen"
        wallpaper: Wallpaper choice ("default", "H4ck3r", "Binary", "encrypted")
        parent: Parent widget
        show_forgot_password: Show "Forgot Password?" link (default: True)
        has_recovery_codes: Whether recovery codes exist (for warning message)
    
    Returns:
        Password string or None if cancelled
    """
    fullscreen = (style == "fullscreen")
    dialog = PasswordDialog(title, prompt, resource_path, fullscreen, wallpaper, parent, show_forgot_password, has_recovery_codes)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_password()
    return None
