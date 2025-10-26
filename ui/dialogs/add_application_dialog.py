"""Add Application Dialog for FadCrypt"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QGroupBox, QTextEdit, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import os
import sys


class AddApplicationDialog(QDialog):
    """Dialog for adding applications with drag-and-drop support"""
    
    application_added = pyqtSignal(str, str)  # app_name, app_path
    
    def __init__(self, resource_path, parent=None, platform_name="Linux"):
        super().__init__(parent)
        self.resource_path = resource_path
        self.parent_window = parent
        self.platform_name = platform_name  # "Linux" or "Windows"
        self.setWindowTitle("Add Application to Encrypt")
        self.setMinimumSize(420, 580)
        self.setModal(True)
        
        # Apply light dialog theme for better readability against dark main app
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2d3a;
            }
            QLabel {
                color: #e5e7eb;
            }
            QGroupBox {
                background-color: #353749;
                border: 1px solid #4a4c5e;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                font-weight: bold;
                color: #e5e7eb;
            }
            QGroupBox::title {
                color: #e5e7eb;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Position on left edge
        screen_geometry = self.screen().geometry()
        x = 50
        y = (screen_geometry.height() - 580) // 2
        self.move(x, y)
        
        self.init_ui()
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Drag and Drop Area
        drop_group = QGroupBox("Drag and Drop Executable Here")
        drop_layout = QVBoxLayout()
        
        self.drop_area = QTextEdit()
        self.drop_area.setReadOnly(True)
        self.drop_area.setMinimumHeight(100)
        self.drop_area.setMaximumHeight(150)
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setStyleSheet("""
            QTextEdit {
                background-color: #404050;
                color: #93c5fd;
                font-size: 12px;
                font-weight: bold;
                border: 2px dashed #3b82f6;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.drop_area.setText("Just drop it in—I'll sort out the name and path,\nno worries")
        self.drop_area.setAcceptDrops(True)
        
        # Install event filter to handle drops on the text edit
        self.drop_area.installEventFilter(self)
        
        drop_layout.addWidget(self.drop_area)
        drop_group.setLayout(drop_layout)
        layout.addWidget(drop_group)
        
        # Manual Input Area
        manual_group = QGroupBox("Or Manually Add Application")
        manual_layout = QVBoxLayout()
        
        # Helper text (platform-specific)
        if self.platform_name == "Windows":
            helper_text = (
                "To find an executable path on Windows:\n"
                "• Use 'Browse' button below\n"
                "• Or right-click app shortcut → Properties → Target\n\n"
                "Example: C:\\Program Files\\Mozilla Firefox\\firefox.exe"
            )
        else:  # Linux
            helper_text = (
                "To find an executable path, use the 'which' command in terminal:\n"
                "❯ which firefox\n"
                "/usr/bin/firefox\n\n"
                "Paste the exact path (with slashes) in the Path field below.\n"
                "For Name, use any readable name like 'Firefox'."
            )
        
        helper_label = QLabel(helper_text)
        helper_label.setStyleSheet("""
            color: #93c5fd;
            font-size: 9pt;
            background-color: #404050;
            padding: 10px;
            border-radius: 5px;
            border-left: 3px solid #3b82f6;
        """)
        helper_label.setWordWrap(True)
        manual_layout.addWidget(helper_label)
        
        # Name input
        name_label = QLabel("Name:")
        name_label.setStyleSheet("background-color: transparent;")
        manual_layout.addWidget(name_label)
        
        self.name_entry = QLineEdit()
        # Platform-specific placeholder
        if self.platform_name == "Windows":
            self.name_entry.setPlaceholderText("e.g., Firefox or Notepad")
        else:
            self.name_entry.setPlaceholderText("e.g., Firefox")
        self.name_entry.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #4a4c5e;
                border-radius: 5px;
                background-color: #353749;
                color: #e5e7eb;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)
        manual_layout.addWidget(self.name_entry)
        
        # Path input
        path_label = QLabel("Path:")
        path_label.setStyleSheet("background-color: transparent;")
        manual_layout.addWidget(path_label)
        
        self.path_entry = QLineEdit()
        # Platform-specific placeholder
        if self.platform_name == "Windows":
            self.path_entry.setPlaceholderText("e.g., C:\\Program Files\\App\\app.exe")
        else:
            self.path_entry.setPlaceholderText("e.g., /usr/bin/firefox")
        self.path_entry.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #4a4c5e;
                border-radius: 5px;
                background-color: #353749;
                color: #e5e7eb;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)
        manual_layout.addWidget(self.path_entry)
        
        # Browse button
        browse_button = QPushButton("📁 Browse")
        browse_button.setStyleSheet("""
            QPushButton {
                background-color: #4a5568;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #5a6578;
            }
            QPushButton:pressed {
                background-color: #3a4558;
            }
        """)
        browse_button.clicked.connect(self.browse_for_file)
        manual_layout.addWidget(browse_button)
        
        manual_group.setLayout(manual_layout)
        layout.addWidget(manual_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Scan Apps Button
        scan_button = QPushButton("🔍 Scan for Apps")
        scan_button.setMinimumWidth(130)
        scan_button.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
            QPushButton:pressed {
                background-color: #5b21b6;
            }
        """)
        scan_button.clicked.connect(self.scan_for_apps)
        button_layout.addWidget(scan_button)
        
        # Save Button
        save_button = QPushButton("💾 Save")
        save_button.setMinimumWidth(120)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        save_button.clicked.connect(self.save_application)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Bind Enter key to save
        self.name_entry.returnPressed.connect(self.save_application)
        self.path_entry.returnPressed.connect(self.save_application)
    
    def eventFilter(self, obj, event):
        """Handle drag and drop events on the drop area"""
        if obj == self.drop_area:
            if event.type() == event.Type.DragEnter:
                if event.mimeData().hasUrls():
                    event.accept()
                else:
                    event.ignore()
                return True
            elif event.type() == event.Type.Drop:
                if event.mimeData().hasUrls():
                    urls = event.mimeData().urls()
                    if urls:
                        file_path = urls[0].toLocalFile()
                        self.on_drop(file_path)
                return True
        return super().eventFilter(obj, event)
    
    def dragEnterEvent(self, event):
        """Handle drag enter event on dialog"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Handle drop event on dialog"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                self.on_drop(file_path)
    
    def on_drop(self, file_path):
        """Handle dropped file"""
        # Check if file exists
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", f"The file does not exist:\n{file_path}")
            return
        
        # Check if it's executable
        if not self.is_executable(file_path):
            reply = QMessageBox.question(
                self,
                "Not Executable",
                f"The selected file is not executable.\nDo you want to add it anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Auto-fill name and path
        app_name = os.path.basename(file_path)
        # Clean up the name for display (remove .exe on Windows)
        if sys.platform.startswith('win') and app_name.endswith('.exe'):
            app_name = app_name[:-4]
        self.name_entry.setText(app_name)
        self.path_entry.setText(file_path)
        
        self.drop_area.setStyleSheet("""
            QTextEdit {
                background-color: #064e3b;
                color: #6ee7b7;
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #10b981;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.drop_area.setText(f"✓ File added:\n{app_name}\n{file_path}")
    
    def is_executable(self, file_path):
        """Check if file is executable (cross-platform)"""
        import sys
        
        if sys.platform.startswith('win'):
            # Windows executables
            windows_executables = ('.exe', '.bat', '.cmd', '.msi', '.com')
            return file_path.lower().endswith(windows_executables)
        else:
            # Linux executable extensions
            linux_executables = ('.desktop', '.sh', '.AppImage', '.run', '.bin', '.py', '.pl', '.rb')
            
            return (
                file_path.endswith(linux_executables) or
                os.access(file_path, os.X_OK) or
                self.is_elf_binary(file_path)
            )
    
    def is_elf_binary(self, file_path):
        """Check if the file is an ELF binary (Linux executable format)"""
        try:
            with open(file_path, 'rb') as f:
                return f.read(4) == b'\x7fELF'
        except (IOError, OSError):
            return False
    
    def browse_for_file(self):
        """Open file browser to select executable"""
        import sys
        
        # Set file filter based on platform
        if sys.platform.startswith('win'):
            file_filter = "Executables (*.exe *.bat *.cmd);;All Files (*)"
        else:
            file_filter = "All Files (*)"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Application Executable",
            os.path.expanduser("~"),
            file_filter
        )
        
        if file_path:
            self.path_entry.setText(file_path)
            if not self.name_entry.text():
                self.name_entry.setText(os.path.basename(file_path))
    
    def scan_for_apps(self):
        """Open app scanner dialog"""
        from ui.dialogs.app_scanner_dialog import AppScannerDialog
        
        print("[AddDialog] Opening app scanner...")
        scanner_dialog = AppScannerDialog(self)
        scanner_dialog.apps_selected.connect(self.on_apps_scanned)
        scanner_dialog.exec()
    
    def on_apps_scanned(self, selected_apps):
        """Handle apps selected from scanner"""
        if not selected_apps:
            return
        
        # For add dialog, we'll add them through parent window
        if self.parent_window and hasattr(self.parent_window, 'on_apps_scanned'):
            self.parent_window.on_apps_scanned(selected_apps)
            self.accept()  # Close the add dialog
        else:
            QMessageBox.information(
                self,
                "Apps Selected",
                f"Selected {len(selected_apps)} apps. They will be added when you close this dialog."
            )
    
    def save_application(self):
        """Save the application"""
        app_name = self.name_entry.text().strip()
        app_path = self.path_entry.text().strip()
        
        if not app_name or not app_path:
            self.show_styled_warning(
                "Missing Information",
                "Please provide both name and path for the application."
            )
            return
        
        # Normalize path separators for consistency
        app_path = os.path.normpath(app_path)

        # Check if path exists
        if not os.path.exists(app_path):
            reply = QMessageBox.question(
                self,
                "File Not Found",
                f"The path does not exist:\n{app_path}\n\nDo you want to add it anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Emit signal and close
        self.application_added.emit(app_name, app_path)
        self.accept()
    
    def show_styled_warning(self, title, message):
        """Show a styled warning dialog with transparent background"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # Apply transparent background styling
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: rgba(43, 45, 58, 240);
            }
            QMessageBox QLabel {
                color: #e5e7eb;
                background-color: transparent;
            }
            QMessageBox QPushButton {
                background-color: #3b82f6;
                color: white;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        
        msg_box.exec()
