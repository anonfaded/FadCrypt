"""
Edit Application Dialog - For renaming and editing app paths
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QMessageBox,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import os
import sys


class EditApplicationDialog(QDialog):
    """
    Dialog for editing an existing application.
    
    Allows user to:
    - Change application name
    - Change application path
    - Browse for new executable
    
    Signals:
        app_updated: Emitted when app is updated (old_name, new_name, new_path)
    """
    
    app_updated = pyqtSignal(str, str, str)  # old_name, new_name, new_path
    
    def __init__(self, app_name: str, app_path: str, parent=None):
        super().__init__(parent)
        
        self.old_name = app_name
        self.old_path = app_path
        
        self.setWindowTitle("Edit Application")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.init_ui()
        self.center_on_screen()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel("✏️ Edit Application")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Plain)
        separator.setLineWidth(1)
        separator.setStyleSheet("background-color: #2a2a2a; border: none; border-radius: 1px; margin: 5px 0px; max-height: 1px; min-height: 1px;")
        layout.addWidget(separator)
        
        layout.addSpacing(10)
        
        # Name field
        name_label = QLabel("Application Name:")
        name_label_font = QFont()
        name_label_font.setBold(True)
        name_label.setFont(name_label_font)
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setText(self.old_name)
        self.name_input.setPlaceholderText("Enter application name...")
        self.name_input.setMinimumHeight(36)
        layout.addWidget(self.name_input)
        
        layout.addSpacing(10)
        
        # Path field
        path_label = QLabel("Application Path:")
        path_label.setFont(name_label_font)
        layout.addWidget(path_label)
        
        path_layout = QHBoxLayout()
        
        self.path_input = QLineEdit()
        self.path_input.setText(self.old_path)
        self.path_input.setPlaceholderText("Enter or browse for executable...")
        self.path_input.setMinimumHeight(36)
        path_layout.addWidget(self.path_input, stretch=1)
        
        browse_btn = QPushButton("📁 Browse")
        browse_btn.setMinimumHeight(36)
        browse_btn.setMinimumWidth(100)
        browse_btn.clicked.connect(self.browse_for_file)
        browse_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3366ff, stop:1 #0033cc);
                color: white;
                border: none;
                border-radius: 4px;
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
        path_layout.addWidget(browse_btn)
        
        layout.addLayout(path_layout)
        
        # Info label
        info_label = QLabel("💡 Tip: You can change both the display name and the executable path")
        info_label.setStyleSheet("color: #888888; font-size: 11px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(10)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Plain)
        separator2.setLineWidth(1)
        separator2.setStyleSheet("background-color: #2a2a2a; border: none; border-radius: 1px; margin: 5px 0px; max-height: 1px; min-height: 1px;")
        layout.addWidget(separator2)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(36)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #666666, stop:1 #444444);
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
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
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Save Changes")
        save_btn.setMinimumHeight(36)
        save_btn.setMinimumWidth(120)
        save_btn.clicked.connect(self.save_changes)
        save_btn.setDefault(True)
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff3333, stop:1 #cc0000);
                color: white;
                border: none;
                border-radius: 4px;
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
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Focus on name input
        self.name_input.setFocus()
        self.name_input.selectAll()
        
    def browse_for_file(self):
        """Open file browser to select executable."""
        if sys.platform.startswith('linux'):
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Executable",
                "",
                "All Files (*)"
            )
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Executable",
                "",
                "Executable Files (*.exe);;All Files (*)"
            )
        
        if file_path:
            self.path_input.setText(file_path)
            
            # Auto-suggest name from filename if name hasn't been changed
            if self.name_input.text() == self.old_name:
                suggested_name = os.path.splitext(os.path.basename(file_path))[0]
                self.name_input.setText(suggested_name)
    
    def save_changes(self):
        """Validate and save changes."""
        new_name = self.name_input.text().strip()
        new_path = self.path_input.text().strip()
        
        # Validation
        if not new_name:
            QMessageBox.warning(
                self,
                "Invalid Name",
                "Please enter an application name."
            )
            self.name_input.setFocus()
            return
        
        if not new_path:
            QMessageBox.warning(
                self,
                "Invalid Path",
                "Please enter or select an executable path."
            )
            self.path_input.setFocus()
            return
        
        if not os.path.exists(new_path):
            reply = QMessageBox.question(
                self,
                "File Not Found",
                f"The path does not exist:\n{new_path}\n\nDo you want to save anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Check if anything changed
        if new_name == self.old_name and new_path == self.old_path:
            QMessageBox.information(
                self,
                "No Changes",
                "No changes were made to the application."
            )
            self.reject()
            return
        
        # Emit signal and close
        self.app_updated.emit(self.old_name, new_name, new_path)
        self.accept()
        
        print(f"[EditDialog] Updated: '{self.old_name}' -> '{new_name}'")
        print(f"[EditDialog] Path: '{self.old_path}' -> '{new_path}'")
    
    def center_on_screen(self):
        """Center dialog on parent or screen."""
        from PyQt6.QtWidgets import QApplication
        
        self.adjustSize()
        
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            screen_x = screen_geometry.x()
            screen_y = screen_geometry.y()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            
            dialog_width = self.width()
            dialog_height = self.height()
            
            center_x = screen_x + (screen_width - dialog_width) // 2
            center_y = screen_y + (screen_height - dialog_height) // 2
            
            self.move(center_x, center_y)
