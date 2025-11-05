"""Logs Tab Widget for FadCrypt Qt - Real-time log viewer"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLineEdit, QTextEdit, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QTextCursor, QFont
import sys
from io import StringIO
from datetime import datetime


class LogCapture:
    """Captures stdout/stderr and stores in buffer"""
    
    def __init__(self):
        self.buffer = StringIO()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.enabled = False
        
    def start(self):
        """Start capturing output"""
        if not self.enabled:
            # Only capture if streams are available (not None)
            if sys.stdout is not None:
                sys.stdout = TeeOutput(sys.stdout, self.buffer)
            if sys.stderr is not None:
                sys.stderr = TeeOutput(sys.stderr, self.buffer)
            self.enabled = True
            
    def stop(self):
        """Stop capturing output"""
        if self.enabled:
            # Restore original streams if they exist
            if self.original_stdout is not None:
                sys.stdout = self.original_stdout
            if self.original_stderr is not None:
                sys.stderr = self.original_stderr
            self.enabled = False
    
    def get_logs(self) -> str:
        """Get captured logs"""
        return self.buffer.getvalue()
    
    def clear(self):
        """Clear buffer"""
        self.buffer = StringIO()
        if self.enabled:
            # Re-attach stdout/stderr to new buffer
            sys.stdout = TeeOutput(self.original_stdout, self.buffer)
            sys.stderr = TeeOutput(self.original_stderr, self.buffer)


class TeeOutput:
    """Write to both original stream and buffer"""
    
    def __init__(self, original, buffer):
        self.original = original
        self.buffer = buffer
    
    def write(self, text):
        if self.original is not None:
            self.original.write(text)
            self.original.flush()
        self.buffer.write(text)
    
    def flush(self):
        if self.original is not None:
            self.original.flush()


class LogsTabWidget(QWidget):
    """Logs tab widget with search and filtering"""
    
    def __init__(self, log_capture: LogCapture, parent=None):
        super().__init__(parent)
        self.log_capture = log_capture
        self.all_logs = ""
        self.current_search = ""
        self.init_ui()
        
        # Update logs every 500ms (lightweight polling)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_logs)
        self.update_timer.start(500)
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar = QWidget()
        toolbar.setStyleSheet("background-color: #1a1a1a; padding: 8px;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        
        # Search bar
        search_label = QLabel("🔍 Search:")
        search_label.setStyleSheet("color: #ffffff; font-size: 10pt;")
        toolbar_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search logs...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 2px solid #444444;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 2px solid #10b981;
            }
        """)
        self.search_input.textChanged.connect(self.filter_logs)
        toolbar_layout.addWidget(self.search_input, stretch=1)
        
        # Clear button
        clear_btn = QPushButton("🗑️ Clear Logs")
        clear_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff3333, stop:1 #cc0000);
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 10pt;
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
        clear_btn.clicked.connect(self.clear_logs)
        toolbar_layout.addWidget(clear_btn)
        
        # Auto-scroll toggle
        self.autoscroll_btn = QPushButton("📌 Auto-scroll: ON")
        self.autoscroll_enabled = True
        self.autoscroll_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00cc00, stop:1 #008800);
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 10pt;
                font-weight: bold;
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
        self.autoscroll_btn.clicked.connect(self.toggle_autoscroll)
        toolbar_layout.addWidget(self.autoscroll_btn)
        
        layout.addWidget(toolbar)
        
        # Log viewer (read-only text edit)
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet("""
            QTextEdit {
                background-color: #0a0a0a;
                color: #00ff00;
                font-family: 'Courier New', Consolas, monospace;
                font-size: 9pt;
                border: none;
                padding: 10px;
            }
        """)
        
        # Set monospace font for terminal-like appearance
        font = QFont("Courier New", 9)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.log_viewer.setFont(font)
        
        layout.addWidget(self.log_viewer)
        
        # Status bar
        self.status_label = QLabel("📊 Logs: 0 lines")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                color: #888888;
                padding: 5px 10px;
                font-size: 9pt;
            }
        """)
        layout.addWidget(self.status_label)
    
    def update_logs(self):
        """Update log viewer with new content (lightweight polling)"""
        new_logs = self.log_capture.get_logs()
        
        # Only update if there are new logs
        if new_logs != self.all_logs:
            self.all_logs = new_logs
            
            # Apply search filter if active
            if self.current_search:
                self.filter_logs(self.current_search)
            else:
                self.log_viewer.setPlainText(self.all_logs)
                
            # Auto-scroll to bottom if enabled
            if self.autoscroll_enabled:
                self.scroll_to_bottom()
            
            # Update status
            line_count = self.all_logs.count('\n')
            self.status_label.setText(f"📊 Logs: {line_count} lines")
    
    def filter_logs(self, search_text: str = None):
        """Filter logs by search text"""
        if search_text is None:
            search_text = self.search_input.text()
        
        self.current_search = search_text.lower().strip()
        
        if not self.current_search:
            # No filter - show all logs
            self.log_viewer.setPlainText(self.all_logs)
        else:
            # Filter lines containing search text
            filtered_lines = []
            for line in self.all_logs.split('\n'):
                if self.current_search in line.lower():
                    filtered_lines.append(line)
            
            filtered_text = '\n'.join(filtered_lines)
            self.log_viewer.setPlainText(filtered_text)
            
            # Update status with filter count
            match_count = len(filtered_lines)
            total_count = self.all_logs.count('\n')
            self.status_label.setText(f"📊 Logs: {match_count}/{total_count} lines (filtered)")
    
    def clear_logs(self):
        """Clear all logs"""
        self.log_capture.clear()
        self.all_logs = ""
        self.log_viewer.clear()
        self.status_label.setText("📊 Logs: 0 lines (cleared)")
    
    def toggle_autoscroll(self):
        """Toggle auto-scroll feature"""
        self.autoscroll_enabled = not self.autoscroll_enabled
        
        if self.autoscroll_enabled:
            self.autoscroll_btn.setText("📌 Auto-scroll: ON")
            self.autoscroll_btn.setStyleSheet("""
                QPushButton {
                    background-color: #10b981;
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 16px;
                    font-size: 10pt;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)
            self.scroll_to_bottom()
        else:
            self.autoscroll_btn.setText("📌 Auto-scroll: OFF")
            self.autoscroll_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6b7280;
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 16px;
                    font-size: 10pt;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #4b5563;
                }
            """)
    
    def scroll_to_bottom(self):
        """Scroll to bottom of log viewer"""
        scrollbar = self.log_viewer.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def cleanup(self):
        """Cleanup when widget is destroyed"""
        self.update_timer.stop()
