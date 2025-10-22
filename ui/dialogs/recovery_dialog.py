"""Password Recovery Dialog - For using recovery codes to reset password"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFrame,
    QTabWidget, QScrollArea, QCheckBox, QMessageBox, QFileDialog, QProgressBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os


class RecoveryCodeDialog(QDialog):
    """Dialog for entering recovery code and creating new password"""
    
    def __init__(self, title, resource_path, parent=None, verify_callback=None):
        super().__init__(parent)
        self.resource_path = resource_path
        self.recovery_code_value = None
        self.new_password_value = None
        self.code_verified = False
        self.tab_widget = None
        self.strength_label = None
        self.strength_meter = None
        self.verify_callback = verify_callback  # Callback to verify recovery code
        
        self.setWindowTitle(title)
        self.init_ui(title)
    
    def init_ui(self, title):
        """Initialize recovery code dialog UI"""
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("QDialog { background-color: #1a1a1a; }")
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Content frame - dynamic size
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: none;
                border-radius: 10px;
            }
        """)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 25, 30, 25)
        content_layout.setSpacing(15)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel { 
                font-size: 16px; 
                font-weight: bold; 
                color: #ffffff; 
                border: none;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title_label)
        
        # Tab widget for recovery code and new password
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab { background-color: #2a2a2a; color: #e0e0e0; padding: 8px 15px; }
            QTabBar::tab:selected { background-color: #d32f2f; color: white; }
            QTabBar::tab:disabled { background-color: #1a1a1a; color: #555555; }
        """)
        
        # Tab 1: Recovery Code
        code_tab = QFrame()
        code_layout = QVBoxLayout(code_tab)
        code_layout.setContentsMargins(15, 15, 15, 15)
        code_layout.setSpacing(12)
        
        code_help = QLabel(
            "Enter one of your 10 recovery codes saved when you created your password.\n"
            "Format: XXXX-XXXX-XXXX-XXXX (or spaces: XXXX XXXX XXXX XXXX)"
        )
        code_help.setWordWrap(True)
        code_help.setStyleSheet("""
            QLabel { 
                font-size: 12px; 
                color: #a0a0a0; 
                padding: 0;
                line-height: 1.4;
            }
        """)
        code_layout.addWidget(code_help)
        
        self.recovery_code_input = QLineEdit()
        self.recovery_code_input.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        self.recovery_code_input.setFixedHeight(38)
        self.recovery_code_input.setStyleSheet("""
            QLineEdit {
                padding: 0 14px;
                font-size: 13px;
                font-family: monospace;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #d32f2f;
                background-color: #2e2e2e;
            }
        """)
        # Connect Enter key to move to next tab
        self.recovery_code_input.returnPressed.connect(self.on_code_enter_pressed)
        code_layout.addWidget(self.recovery_code_input)
        
        # Next button to proceed to password entry
        next_button = QPushButton("Next ➡️")
        next_button.setFixedHeight(36)
        next_button.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #1565c0; }
            QPushButton:pressed { background-color: #0d47a1; }
        """)
        next_button.clicked.connect(self.on_code_enter_pressed)
        code_layout.addWidget(next_button)
        
        warning_label = QLabel(
            "⚠️ Warning: Each recovery code can only be used ONCE.\n"
            "After using a code, you won't be able to use it again."
        )
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("""
            QLabel { 
                font-size: 12px; 
                color: #ff6b6b; 
                padding: 12px;
                background-color: #3a2a2a;
                border-radius: 4px;
                line-height: 1.4;
            }
        """)
        code_layout.addWidget(warning_label)
        code_layout.addStretch()
        
        self.tab_widget.addTab(code_tab, "1️⃣ Recovery Code")
        
        # Tab 2: New Password (initially disabled)
        pwd_tab = QFrame()
        pwd_layout = QVBoxLayout(pwd_tab)
        pwd_layout.setContentsMargins(15, 15, 15, 15)
        pwd_layout.setSpacing(12)
        
        pwd_help = QLabel(
            "Enter a NEW master password for your account.\n"
            "This will replace your old password completely.\n"
            "After recovery, you'll receive 10 new recovery codes."
        )
        pwd_help.setWordWrap(True)
        pwd_help.setStyleSheet("""
            QLabel { 
                font-size: 12px; 
                color: #a0a0a0; 
                padding: 0;
                line-height: 1.4;
            }
        """)
        pwd_layout.addWidget(pwd_help)
        
        pwd_label = QLabel("New Master Password:")
        pwd_label.setStyleSheet("QLabel { color: #e0e0e0; font-size: 12px; }")
        pwd_layout.addWidget(pwd_label)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setPlaceholderText("Enter new master password")
        self.new_password_input.setFixedHeight(38)
        self.new_password_input.setStyleSheet("""
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
        """)
        self.new_password_input.textChanged.connect(self.update_password_strength)
        pwd_layout.addWidget(self.new_password_input)
        
        # Password strength meter
        strength_layout = QVBoxLayout()
        strength_layout.setSpacing(4)
        strength_layout.setContentsMargins(0, 8, 0, 0)
        
        self.strength_label = QLabel("Password Strength: -")
        self.strength_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #888888;
                border: none;
            }
        """)
        strength_layout.addWidget(self.strength_label)
        
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
        pwd_layout.addLayout(strength_layout)
        
        confirm_label = QLabel("Confirm Password:")
        confirm_label.setStyleSheet("QLabel { color: #e0e0e0; font-size: 12px; }")
        pwd_layout.addWidget(confirm_label)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Confirm new password")
        self.confirm_password_input.setFixedHeight(38)
        self.confirm_password_input.setStyleSheet("""
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
        """)
        pwd_layout.addWidget(self.confirm_password_input)
        
        pwd_warning = QLabel(
            "⚠️ Important: Your new password cannot be recovered if forgotten.\n"
            "Make it strong and memorable, or you'll need a recovery code again."
        )
        pwd_warning.setWordWrap(True)
        pwd_warning.setStyleSheet("""
            QLabel { 
                font-size: 12px; 
                color: #ff6b6b; 
                padding: 12px;
                background-color: #3a2a2a;
                border-radius: 4px;
                line-height: 1.4;
            }
        """)
        pwd_layout.addWidget(pwd_warning)
        pwd_layout.addStretch()
        
        self.tab_widget.addTab(pwd_tab, "2️⃣ New Password")
        
        # Disable the new password tab initially
        self.tab_widget.setTabEnabled(1, False)
        
        content_layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
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
            QPushButton:hover { background-color: #464646; }
            QPushButton:pressed { background-color: #2e2e2e; }
        """)
        cancel_button.clicked.connect(self.reject)
        
        self.recover_button = QPushButton("Recover")
        self.recover_button.setFixedSize(120, 36)
        self.recover_button.setEnabled(False)  # Disabled until code verified
        self.recover_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover:enabled { background-color: #b71c1c; }
            QPushButton:pressed:enabled { background-color: #9a0007; }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        self.recover_button.clicked.connect(self.on_recover)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.recover_button)
        button_layout.addStretch()
        
        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(content_frame)
        self.setLayout(main_layout)
        
        # Set dynamic size
        self.setMinimumSize(550, 450)
        self.resize(550, 520)  # Slightly taller for password strength meter
        
        # Center on screen
        self.center_on_screen()
        
        # Focus on recovery code input
        self.recovery_code_input.setFocus()
    
    def center_on_screen(self):
        """Center dialog on screen"""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
    
    def on_code_enter_pressed(self):
        """Handle Enter key or Next button in recovery code tab"""
        code = self.recovery_code_input.text().strip()
        
        if not code:
            self.show_error("Recovery Code Required", "Please enter your recovery code first")
            return
        
        # Verify the recovery code if callback provided
        if self.verify_callback:
            is_valid, error_msg = self.verify_callback(code)
            if not is_valid:
                # Determine appropriate title based on error message
                if error_msg and "already been used" in error_msg:
                    title = "Recovery Code Already Used"
                elif error_msg and ("not found" in error_msg or "incorrect" in error_msg):
                    title = "Invalid Recovery Code"
                elif error_msg and "format" in error_msg:
                    title = "Invalid Code Format"
                else:
                    title = "Recovery Code Error"
                
                self.show_error(
                    title,
                    error_msg or "The recovery code you entered is invalid or has already been used.\n"
                    "Please check your codes and try again."
                )
                return
        
        # Code verified - enable new password tab and switch to it
        self.code_verified = True
        self.tab_widget.setTabEnabled(1, True)
        self.tab_widget.setCurrentIndex(1)
        
        # Enable recover button
        self.recover_button.setEnabled(True)
        
        # Focus on new password input
        self.new_password_input.setFocus()
    
    def update_password_strength(self):
        """Update password strength meter based on password input"""
        password = self.new_password_input.text()
        
        # Calculate strength
        strength, color, text = self.calculate_password_strength(password)
        
        # Update meter
        self.strength_meter.setValue(strength)
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
        self.strength_label.setText(f"Password Strength: {text}")
        self.strength_label.setStyleSheet(f"""
            QLabel {{
                font-size: 11px;
                color: {color};
                border: none;
            }}
        """)
    
    def calculate_password_strength(self, password):
        """
        Calculate password strength.
        Returns (strength_percent, color, text)
        """
        if not password:
            return (0, "#666666", "-")
        
        strength = 0
        
        # Length
        length = len(password)
        if length >= 8:
            strength += 20
        if length >= 12:
            strength += 15
        if length >= 16:
            strength += 10
        
        # Character variety
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        variety = sum([has_lower, has_upper, has_digit, has_special])
        strength += variety * 10
        
        # Bonus for length + variety
        if length >= 12 and variety >= 3:
            strength += 15
        
        # Cap at 100
        strength = min(strength, 100)
        
        # Determine level and color
        if strength < 20:
            return (strength, "#f44336", "Very Weak")  # Red
        elif strength < 40:
            return (strength, "#ff9800", "Weak")  # Orange
        elif strength < 60:
            return (strength, "#ffeb3b", "Fair")  # Yellow
        elif strength < 80:
            return (strength, "#8bc34a", "Good")  # Light Green
        else:
            return (strength, "#4caf50", "Strong")  # Green
    
    def on_recover(self):
        """Handle recovery button - validate password and proceed"""
        code = self.recovery_code_input.text().strip()
        pwd1 = self.new_password_input.text()
        pwd2 = self.confirm_password_input.text()
        
        # Validate code
        if not code:
            self.show_error("Recovery Code Required", "Please enter your recovery code in the first tab")
            return
        
        # Validate passwords
        if not pwd1:
            self.show_error("Password Required", "Please enter a new password")
            return
        
        if pwd1 != pwd2:
            self.show_error("Passwords Don't Match", "The passwords you entered do not match")
            return
        
        # NO PASSWORD RESTRICTIONS - user can set any password
        # Just warn if very weak
        strength, _, strength_text = self.calculate_password_strength(pwd1)
        if strength < 20:
            # Warn but allow
            reply = self.show_confirmation(
                "Weak Password Warning",
                f"⚠️ Your password is {strength_text}.\n\n"
                "Are you sure you want to use this password?\n"
                "We recommend using a stronger password for better security."
            )
            if not reply:
                return  # User cancelled
        
        # Store values for parent to use
        self.recovery_code_value = code
        self.new_password_value = pwd1
        self.accept()
    
    def show_error(self, title, message):
        """Show error message"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet("""
            QMessageBox { background-color: #1e1e1e; }
            QMessageBox QLabel { color: #e0e0e0; font-size: 12px; }
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                padding: 5px 20px;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #b71c1c; }
        """)
        msg_box.exec()
    
    def show_success(self, title, message):
        """Show success message"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet("""
            QMessageBox { background-color: #1e1e1e; }
            QMessageBox QLabel { color: #e0e0e0; font-size: 12px; }
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                padding: 5px 20px;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #388e3c; }
        """)
        msg_box.exec()
    
    def show_confirmation(self, title, message):
        """Show confirmation dialog - returns True if user confirms"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        msg_box.setStyleSheet("""
            QMessageBox { background-color: #1e1e1e; }
            QMessageBox QLabel { color: #e0e0e0; font-size: 12px; }
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: none;
                padding: 5px 20px;
                border-radius: 3px;
                min-width: 60px;
            }
            QPushButton:hover { background-color: #464646; }
        """)
        return msg_box.exec() == QMessageBox.StandardButton.Yes
    
    def get_recovery_code(self):
        """Get entered recovery code"""
        return self.recovery_code_value
    
    def get_new_password(self):
        """Get new password"""
        return self.new_password_value
    
    def keyPressEvent(self, event):
        """Handle key press"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


class RecoveryCodesDisplayDialog(QDialog):
    """Dialog to display generated recovery codes to user"""
    
    def __init__(self, codes: list, resource_path=None, parent=None):
        super().__init__(parent)
        self.codes = codes
        self.resource_path = resource_path
        self.saved_checkbox = None
        self.confirm_button = None
        
        self.setWindowTitle("Recovery Codes - Save These!")
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("QDialog { background-color: #1a1a1a; }")
        self.setMinimumSize(600, 550)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Warning title
        warning_title = QLabel("🔐 SAVE YOUR RECOVERY CODES")
        warning_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        warning_title.setStyleSheet("QLabel { color: #ff6b6b; }")
        warning_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(warning_title)
        
        # Important message
        message = QLabel(
            "If you forget your FadCrypt master password, you can use these codes to recover access.\n\n"
            "⚠️  IMPORTANT:\n"
            "• Each code can ONLY be used ONCE\n"
            "• Save these codes in a SAFE PLACE (print, password manager, etc.)\n"
            "• Do NOT share these codes with anyone\n"
            "• If all codes are used and you forget your password, you will lose access\n"
        )
        message.setWordWrap(True)
        message.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                padding: 15px;
                background-color: #2a2a2a;
                border-radius: 5px;
                border-left: 4px solid #ff6b6b;
            }
        """)
        main_layout.addWidget(message)
        
        # Codes display area
        scroll = QScrollArea()
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: 2px solid #3a3a3a;
                border-radius: 5px;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
            }
        """)
        scroll.setWidgetResizable(True)
        
        codes_container = QFrame()
        codes_layout = QVBoxLayout(codes_container)
        codes_layout.setContentsMargins(15, 15, 15, 15)
        codes_layout.setSpacing(10)
        
        for i, code in enumerate(self.codes, 1):
            code_label = QLabel(f"{i:2d}. {code}")
            code_label.setFont(QFont("Courier New", 11, QFont.Weight.Bold))
            code_label.setStyleSheet("""
                QLabel {
                    color: #00ff00;
                    padding: 8px;
                    background-color: #1a1a1a;
                    border: 1px solid #004400;
                    border-radius: 3px;
                    font-family: monospace;
                }
            """)
            codes_layout.addWidget(code_label)
        
        codes_layout.addStretch()
        scroll.setWidget(codes_container)
        main_layout.addWidget(scroll)
        
        # Checkbox confirmation
        self.saved_checkbox = QCheckBox("✓ I have safely saved these codes")
        self.saved_checkbox.setStyleSheet("""
            QCheckBox {
                color: #e0e0e0;
                font-size: 13px;
                font-weight: 600;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #2a2a2a;
            }
            QCheckBox::indicator:checked {
                background-color: #4caf50;
                border-color: #4caf50;
            }
            QCheckBox::indicator:hover {
                border-color: #777777;
            }
        """)
        self.saved_checkbox.stateChanged.connect(self.on_checkbox_changed)
        main_layout.addWidget(self.saved_checkbox)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        save_file_button = QPushButton("💾 Save to File")
        save_file_button.setFixedHeight(36)
        save_file_button.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                padding: 0 15px;
            }
            QPushButton:hover { background-color: #1565c0; }
            QPushButton:pressed { background-color: #0d47a1; }
        """)
        save_file_button.clicked.connect(self.save_to_file)
        button_layout.addWidget(save_file_button)
        
        copy_button = QPushButton("📋 Copy All")
        copy_button.setFixedHeight(36)
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #1a4620;
                color: #00ff00;
                border: 1px solid #004400;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #215028; }
        """)
        copy_button.clicked.connect(self.copy_codes)
        button_layout.addWidget(copy_button)
        
        button_layout.addStretch()
        
        self.confirm_button = QPushButton("I Have Saved These Codes")
        self.confirm_button.setFixedHeight(36)
        self.confirm_button.setEnabled(False)  # Disabled until checkbox checked
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                padding: 0 20px;
            }
            QPushButton:hover:enabled { background-color: #b71c1c; }
            QPushButton:pressed:enabled { background-color: #9a0007; }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        self.confirm_button.clicked.connect(self.accept)
        button_layout.addWidget(self.confirm_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Center on screen
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
    
    def on_checkbox_changed(self, state):
        """Enable/disable confirm button based on checkbox state"""
        self.confirm_button.setEnabled(state == Qt.CheckState.Checked.value)
    
    def save_to_file(self):
        """Save recovery codes to a text file"""
        # Default filename
        default_filename = "fadcrypt_recovery_codes.txt"
        
        # Open file dialog to choose save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Recovery Codes",
            os.path.expanduser(f"~/{default_filename}"),
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                # Format codes for file
                content = "FadCrypt Password Recovery Codes\n"
                content += "=" * 50 + "\n\n"
                content += "⚠️  IMPORTANT: Keep these codes safe!\n"
                content += "• Each code can only be used ONCE\n"
                content += "• You need these if you forget your master password\n"
                content += "• Do NOT share these codes with anyone\n\n"
                content += "=" * 50 + "\n\n"
                
                for i, code in enumerate(self.codes, 1):
                    content += f"{i:2d}. {code}\n"
                
                content += "\n" + "=" * 50 + "\n"
                content += f"Generated: {self._get_timestamp()}\n"
                
                # Write to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Show success message
                msg = QMessageBox(self)
                msg.setWindowTitle("Saved")
                msg.setText(f"✅ Recovery codes saved to:\n{file_path}")
                msg.setStyleSheet("""
                    QMessageBox { background-color: #1e1e1e; }
                    QMessageBox QLabel { color: #e0e0e0; }
                    QPushButton { 
                        background-color: #d32f2f; 
                        color: white; 
                        padding: 5px 20px;
                        border: none;
                        border-radius: 3px;
                    }
                    QPushButton:hover { background-color: #b71c1c; }
                """)
                msg.exec()
                
            except Exception as e:
                # Show error message
                msg = QMessageBox(self)
                msg.setWindowTitle("Error")
                msg.setText(f"❌ Failed to save file:\n{str(e)}")
                msg.setStyleSheet("""
                    QMessageBox { background-color: #1e1e1e; }
                    QMessageBox QLabel { color: #e0e0e0; }
                    QPushButton { 
                        background-color: #d32f2f; 
                        color: white; 
                        padding: 5px 20px;
                        border: none;
                        border-radius: 3px;
                    }
                """)
                msg.exec()
    
    def _get_timestamp(self):
        """Get current timestamp for file"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def copy_codes(self):
        """Copy all codes to clipboard"""
        from PyQt6.QtWidgets import QApplication
        
        text = "FadCrypt Recovery Codes:\n\n"
        for i, code in enumerate(self.codes, 1):
            text += f"{i:2d}. {code}\n"
        
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(text)
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Copied")
        msg.setText("✅ All recovery codes copied to clipboard!")
        msg.setStyleSheet("""
            QMessageBox { background-color: #1e1e1e; }
            QMessageBox QLabel { color: #e0e0e0; }
            QPushButton { 
                background-color: #d32f2f; 
                color: white; 
                padding: 5px 20px; 
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #b71c1c; }
        """)
        msg.exec()


def ask_recovery_code(resource_path=None, parent=None, verify_callback=None):
    """
    Show recovery code dialog.
    
    Args:
        resource_path: Path to resources
        parent: Parent widget
        verify_callback: Callback function to verify recovery code
                        Should accept (code: str) and return (is_valid: bool, error_msg: Optional[str])
    
    Returns:
        Tuple of (recovery_code: str, new_password: str) or (None, None) if cancelled
    """
    dialog = RecoveryCodeDialog("Recover Access with Recovery Code", resource_path, parent, verify_callback)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_recovery_code(), dialog.get_new_password()
    return None, None


def show_recovery_codes(codes: list, resource_path=None, parent=None):
    """
    Show generated recovery codes to user.
    Blocks until user confirms they have saved the codes.
    """
    dialog = RecoveryCodesDisplayDialog(codes, resource_path, parent)
    dialog.exec()
