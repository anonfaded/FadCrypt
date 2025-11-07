"""Operation Logs Dialog - Shows operation progress and results"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont


class OperationLogsDialog(QDialog):
    """Dialog to display operation logs and results"""
    
    def __init__(self, title: str = "Operation Progress", logs: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 600, 400)
        self.setMinimumSize(500, 350)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #2d2d2d;
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 10pt;
                border: 1px solid #444444;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3366ff, stop:1 #0033cc);
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
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
            QLabel {
                color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title label
        title_label = QLabel("Operation Progress & Results")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Logs text edit
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setPlainText(logs)
        layout.addWidget(self.logs_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setMinimumWidth(100)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.center_on_screen()
    
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
    
    def set_logs(self, logs: str):
        """Update logs text"""
        self.logs_text.setPlainText(logs)
        # Scroll to bottom
        self.logs_text.verticalScrollBar().setValue(
            self.logs_text.verticalScrollBar().maximum()
        )
