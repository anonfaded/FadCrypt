"""Context Menu Password Dialog - Shows password prompt with live operation logs"""

import sys
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont, QIcon


class OperationWorker(QThread):
    """Worker thread for long-running operations"""
    finished = pyqtSignal(bool)  # Emits success status
    
    def __init__(self, operation_func):
        super().__init__()
        self.operation_func = operation_func
    
    def run(self):
        """Run the operation in a background thread"""
        try:
            success = self.operation_func()
            self.finished.emit(success)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            self.finished.emit(False)


class ContextMenuPasswordDialog(QDialog):
    """Password dialog with integrated logs display for context menu operations"""
    
    # Signal for thread-safe log updates
    log_signal = pyqtSignal(str)
    
    def __init__(self, operation: str = "LOCK", parent=None, operation_callback=None):
        super().__init__(parent)
        self.operation = operation
        self.password_value = None
        self.logs_text = ""
        self.operation_complete = False
        self.operation_callback = operation_callback  # Callback function to perform the actual operation
        
        # Connect signal to slot for thread-safe updates
        self.log_signal.connect(self._update_logs_slot)
        
        self.setWindowTitle("FadCrypt - Security Authorization")
        self.setGeometry(100, 100, 600, 450)
        self.setMinimumSize(600, 450)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a1a, stop:1 #0d0d0d);
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 11pt;
                background: transparent;
            }
            QLineEdit {
                background-color: #2a2a2a;
                color: #ff4444;
                border: 2px solid #ff3333;
                border-radius: 6px;
                padding: 10px;
                font-size: 11pt;
                font-weight: bold;
                font-family: 'Consolas', 'Monaco', monospace;
            }
            QLineEdit:focus {
                border: 2px solid #ff5555;
                background-color: #1a1a1a;
            }
            QLineEdit:disabled {
                background-color: #151515;
                color: #666666;
                border: 2px solid #444444;
            }
            QTextEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 2px solid #ff3333;
                border-radius: 6px;
                padding: 8px;
                font-size: 9pt;
                font-family: 'Consolas', 'Monaco', monospace;
                selection-background-color: #ff3333;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff3333, stop:1 #cc0000);
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 10pt;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff5555, stop:1 #dd0000);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #cc0000, stop:1 #990000);
            }
            QPushButton:disabled {
                background: #555555;
                color: #888888;
            }
            QPushButton#CancelBtn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #666666, stop:1 #444444);
            }
            QPushButton#CancelBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #777777, stop:1 #555555);
            }
            QPushButton#CloseBtn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00aa00, stop:1 #008800);
            }
            QPushButton#CloseBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00cc00, stop:1 #00aa00);
            }
        """)
        
        self.init_ui()
        self.center_on_screen()
    
    def init_ui(self):
        """Initialize UI"""
        # Set window icon
        try:
            import sys
            import os
            def resource_path(relative_path):
                try:
                    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
                except Exception:
                    base_path = os.path.abspath(".")
                return os.path.join(base_path, relative_path)
            
            icon_path = resource_path("img/icon.ico")
            if os.path.exists(icon_path):
                from PyQt6.QtGui import QIcon
                self.setWindowIcon(QIcon(icon_path))
        except:
            pass
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title with icon
        title_label = QLabel(f"🔐 FadCrypt  |  {self.operation} Operation")
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ff3333; padding: 8px;")
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(f"Enter your password to proceed with the {self.operation.lower()} operation")
        desc_label.setStyleSheet("color: #cccccc; font-size: 10pt; padding-left: 5px;")
        layout.addWidget(desc_label)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password...")
        # Don't connect returnPressed - force user to click Authorize button
        # This prevents Qt from auto-closing dialog after Enter press
        layout.addWidget(self.password_input)
        
        # Logs label
        logs_label = QLabel("Operation Progress:")
        logs_label.setStyleSheet("color: #aaaaaa; margin-top: 15px;")
        layout.addWidget(logs_label)
        
        # Logs display
        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        self.logs_display.setMinimumHeight(150)
        self.logs_display.setMaximumHeight(200)
        layout.addWidget(self.logs_display)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.unlock_btn = QPushButton("Authorize")
        self.unlock_btn.setAutoDefault(False)  # Prevent auto-close behavior
        self.unlock_btn.setDefault(False)
        self.unlock_btn.clicked.connect(self.accept_dialog)
        self.unlock_btn.setMinimumWidth(100)
        button_layout.addWidget(self.unlock_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setObjectName("CloseBtn")
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setMinimumWidth(100)
        self.close_btn.setVisible(False)  # Hidden until operation completes
        button_layout.addWidget(self.close_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("CancelBtn")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMinimumWidth(100)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.password_input.setFocus()
    
    def accept_dialog(self):
        """Handle accept - set password, execute operation in background thread"""
        password = self.password_input.text()
        if not password:
            self.update_logs("❌ Password is required")
            return
        
        self.password_value = password
        self.password_input.setEnabled(False)
        self.password_input.setPlaceholderText("Processing...")
        self.unlock_btn.setEnabled(False)
        
        # Immediately show that we're processing
        self.update_logs("Processing...")
        self.update_logs("")
        self.update_logs("🔄 Initializing operation...")
        
        # Use QTimer to defer operation start - ensures UI is responsive first
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, lambda: self.start_operation(password))
    
    def start_operation(self, password):
        """Start the operation in a background thread"""
        # Call the operation callback in a BACKGROUND THREAD to prevent UI hanging
        if self.operation_callback:
            def run_operation():
                """Run operation in background thread"""
                try:
                    return self.operation_callback(password, self)
                except Exception as e:
                    self.update_logs(f"\n❌ Error: {str(e)}")
                    return False
            
            # Create worker thread
            self.worker = OperationWorker(run_operation)
            self.worker.finished.connect(self.on_operation_finished)
            self.worker.start()
    
    def on_operation_finished(self, success: bool):
        """Handle operation completion from worker thread"""
        if success:
            self.update_logs("\n✓ Operation completed successfully")
            self.update_logs("\n📋 Review the logs above to see what was done")
            self.mark_operation_complete(success)
        else:
            # Check if it was password error (logs will show it)
            if "Incorrect password" in self.logs_text:
                self.update_logs("\n⚠️ Please try again with the correct password")
                # Re-enable password input for retry
                self.password_input.setEnabled(True)
                self.password_input.clear()
                self.password_input.setPlaceholderText("Enter password...")
                self.password_input.setFocus()
                self.unlock_btn.setEnabled(True)
                # Clear the operation logs but keep error message (HTML format)
                self.logs_text = '<span style="color: #ff4444; font-weight: bold;">❌ Incorrect password!</span><br><br><span style="color: #ffaa00; font-weight: bold;">⚠️ Please try again with the correct password</span><br>'
                # Force update display
                if self.logs_display:
                    self.logs_display.setHtml(self.logs_text)
            else:
                self.update_logs("\n✗ Operation failed - see logs above")
                self.mark_operation_complete(False)
    
    def accept(self):
        """Override accept to log when dialog is closing via accept"""
        print("[DEBUG] Dialog.accept() called - dialog closing")
        import traceback
        traceback.print_stack()
        super().accept()
    
    def reject(self):
        """Override reject to log when dialog is closing via reject"""
        print("[DEBUG] Dialog.reject() called - dialog closing")
        super().reject()
    
    def closeEvent(self, event):
        """Override closeEvent to log when dialog is closing"""
        print("[DEBUG] Dialog.closeEvent() called - dialog closing")
        super().closeEvent(event)
    
    def mark_operation_complete(self, success=True):
        """Mark operation as complete and show close button"""
        try:
            self.operation_complete = success
            if self.unlock_btn:
                self.unlock_btn.setVisible(False)
            if self.close_btn:
                self.close_btn.setVisible(True)
                # Don't auto-focus Close button to prevent accidental Enter press
        except RuntimeError:
            # Dialog or button was deleted
            pass
    
    @pyqtSlot(str)
    def _update_logs_slot(self, message: str):
        """Thread-safe slot for updating logs with color coding"""
        # Color code based on message content
        colored_message = self._colorize_log_message(message)
        self.logs_text += colored_message
        
        try:
            if self.logs_display and self.isVisible():
                self.logs_display.setHtml(self.logs_text)
                scrollbar = self.logs_display.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
                self.logs_display.update()
        except RuntimeError:
            pass
    
    def _colorize_log_message(self, message: str) -> str:
        """Color code a log message based on its content"""
        if not message or message.strip() == "":
            return "<br>"
        
        # Error messages (red)
        if any(marker in message for marker in ['❌', '✗', 'ERROR', 'Error', 'Failed', 'failed', 'Incorrect']):
            return f'<span style="color: #ff4444; font-weight: bold;">{message}</span><br>'
        
        # Success messages (green)
        elif any(marker in message for marker in ['✓', '✔', 'Success', 'success', 'completed successfully', 'Verified']):
            return f'<span style="color: #00ff00; font-weight: bold;">{message}</span><br>'
        
        # Warning messages (yellow/orange)
        elif any(marker in message for marker in ['⚠', 'Warning', 'warning', 'Please try again']):
            return f'<span style="color: #ffaa00; font-weight: bold;">{message}</span><br>'
        
        # Info/processing messages (cyan/blue)
        elif any(marker in message for marker in ['🔄', 'Processing', 'Initializing', 'Locking', 'Unlocking']):
            return f'<span style="color: #00aaff;">{message}</span><br>'
        
        # Special markers (keep their color)
        elif '🔒' in message or '🔓' in message:
            return f'<span style="color: #ffaa00;">{message}</span><br>'
        
        elif '📋' in message:
            return f'<span style="color: #aaaaaa;">{message}</span><br>'
        
        # Default (light gray)
        else:
            return f'<span style="color: #cccccc;">{message}</span><br>'
    
    def update_logs(self, message: str):
        """Update logs display with new message (thread-safe via signal)"""
        # Use signal emission for thread-safe GUI updates
        self.log_signal.emit(message)
    
    def center_on_screen(self):
        """Center dialog on screen"""
        try:
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
        except:
            pass
    
    def close_dialog(self):
        """Close the dialog after operation completes"""
        try:
            if self.isVisible():
                self.close()
        except RuntimeError:
            # Dialog already deleted
            pass
