"""
Button Panel - Control buttons for application management
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal


class ButtonPanel(QWidget):
    """
    Panel with control buttons for managing applications.
    
    Signals:
        add_app_clicked: User wants to add a new application
        edit_app_clicked: User wants to edit selected application
        remove_app_clicked: User wants to remove selected applications
        select_all_clicked: User wants to select all applications
        deselect_all_clicked: User wants to deselect all applications
    """
    
    add_app_clicked = pyqtSignal()
    edit_app_clicked = pyqtSignal()
    remove_app_clicked = pyqtSignal()
    select_all_clicked = pyqtSignal()
    deselect_all_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Add Application button
        self.add_button = QPushButton("➕ Add Application")
        self.add_button.setMinimumHeight(40)
        self.add_button.setMinimumWidth(140)
        self.add_button.clicked.connect(self.add_app_clicked.emit)
        self.add_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00cc00, stop:1 #008800);
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 20px;
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
        layout.addWidget(self.add_button)
        
        layout.addSpacing(30)
        
        # Edit button
        self.edit_button = QPushButton("✏️ Edit")
        self.edit_button.setMinimumHeight(40)
        self.edit_button.setMinimumWidth(100)
        self.edit_button.clicked.connect(self.edit_app_clicked.emit)
        self.edit_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3366ff, stop:1 #0033cc);
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 20px;
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
        layout.addWidget(self.edit_button)
        
        # Remove button
        self.remove_button = QPushButton("🗑️ Remove")
        self.remove_button.setMinimumHeight(40)
        self.remove_button.setMinimumWidth(100)
        self.remove_button.clicked.connect(self.remove_app_clicked.emit)
        self.remove_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff3333, stop:1 #cc0000);
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 20px;
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
        layout.addWidget(self.remove_button)
        
        layout.addSpacing(30)
        
        # Select All button
        self.select_all_button = QPushButton("✅ Select All")
        self.select_all_button.setMinimumHeight(40)
        self.select_all_button.setMinimumWidth(100)
        self.select_all_button.clicked.connect(self.select_all_clicked.emit)
        self.select_all_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3366ff, stop:1 #0033cc);
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 20px;
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
        layout.addWidget(self.select_all_button)
        
        # Deselect All button
        self.deselect_all_button = QPushButton("❌ Deselect All")
        self.deselect_all_button.setMinimumHeight(40)
        self.deselect_all_button.setMinimumWidth(120)
        self.deselect_all_button.clicked.connect(self.deselect_all_clicked.emit)
        self.deselect_all_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #666666, stop:1 #444444);
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 20px;
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
        layout.addWidget(self.deselect_all_button)
        
        # Stretch at the end
        layout.addStretch()
