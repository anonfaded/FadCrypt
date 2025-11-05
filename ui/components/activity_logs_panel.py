"""Activity Logs Panel - Shows audit trail of all lock/unlock events"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ActivityLogsPanel(QWidget):
    """Panel for viewing and filtering activity logs"""
    
    def __init__(self, activity_manager=None, parent=None):
        super().__init__(parent)
        self.activity_manager = activity_manager
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("📋 Activity Log")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Complete audit trail of all lock/unlock events, configuration changes, and security events")
        desc.setStyleSheet("color: #999999;")
        layout.addWidget(desc)
        
        # Filter bar
        filter_layout = QHBoxLayout()
        
        # Search box
        search_label = QLabel("🔍 Search:")
        search_box = QLineEdit()
        search_box.setPlaceholderText("Search by item name or details...")
        search_box.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 8px;
                min-height: 30px;
            }
        """)
        self.search_box = search_box
        filter_layout.addWidget(search_label)
        filter_layout.addWidget(search_box)
        
        # Filter dropdown
        filter_label = QLabel("Filter:")
        filter_combo = QComboBox()
        filter_combo.addItems([
            "All Events",
            "Locks",
            "Unlocks",
            "Configuration",
            "Security"
        ])
        filter_combo.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 5px;
                min-height: 30px;
            }
        """)
        self.filter_combo = filter_combo
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(filter_combo)
        
        # Export button
        export_btn = QPushButton("📥 Export CSV")
        export_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00cc00, stop:1 #008800);
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
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
        export_btn.clicked.connect(self.export_logs)
        filter_layout.addWidget(export_btn)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3366ff, stop:1 #0033cc);
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
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
        refresh_btn.clicked.connect(self.load_logs)
        filter_layout.addWidget(refresh_btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Activity table
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Timestamp", "Event Type", "Item", "Status", "Details", "Method"
        ])
        table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                gridline-color: #333333;
                border: 1px solid #333333;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #e0e0e0;
                padding: 5px;
                border: none;
                border-right: 1px solid #333333;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        table.setColumnWidth(0, 200)
        table.setColumnWidth(1, 120)
        table.setColumnWidth(2, 150)
        table.setColumnWidth(3, 80)
        table.setColumnWidth(4, 200)
        table.setColumnWidth(5, 100)
        table.setAlternatingRowColors(True)
        self.activity_table = table
        layout.addWidget(table)
        
        # Load initial data
        search_box.textChanged.connect(self.on_search_changed)
        filter_combo.currentTextChanged.connect(self.on_filter_changed)
        self.load_logs()
    
    def load_logs(self):
        """Load activity logs into table"""
        if not self.activity_manager:
            return
        
        events = self.activity_manager.get_recent_events(limit=200)
        self.activity_table.setRowCount(len(events))
        
        for row, event in enumerate(reversed(events)):
            # Timestamp
            ts_item = QTableWidgetItem(event.get('timestamp', 'N/A')[:19])
            self.activity_table.setItem(row, 0, ts_item)
            
            # Event type
            type_item = QTableWidgetItem(event.get('event_type', 'unknown'))
            self.activity_table.setItem(row, 1, type_item)
            
            # Item name
            item_item = QTableWidgetItem(event.get('item_name', '-'))
            self.activity_table.setItem(row, 2, item_item)
            
            # Status (success/failure)
            success = event.get('success', True)
            status_item = QTableWidgetItem("✓" if success else "✗")
            self.activity_table.setItem(row, 3, status_item)
            
            # Details
            details = event.get('details', '')
            details_item = QTableWidgetItem(details)
            self.activity_table.setItem(row, 4, details_item)
            
            # Method
            method_item = QTableWidgetItem(event.get('unlock_method', '-'))
            self.activity_table.setItem(row, 5, method_item)
    
    def on_search_changed(self, text):
        """Handle search box changes"""
        if not self.activity_manager:
            return
        
        if not text:
            self.load_logs()
            return
        
        results = self.activity_manager.search_events(text)
        self.activity_table.setRowCount(len(results))
        
        for row, event in enumerate(results):
            # Same as load_logs but for filtered results
            ts_item = QTableWidgetItem(event.get('timestamp', 'N/A')[:19])
            self.activity_table.setItem(row, 0, ts_item)
            
            type_item = QTableWidgetItem(event.get('event_type', 'unknown'))
            self.activity_table.setItem(row, 1, type_item)
            
            item_item = QTableWidgetItem(event.get('item_name', '-'))
            self.activity_table.setItem(row, 2, item_item)
            
            success = event.get('success', True)
            status_item = QTableWidgetItem("✓" if success else "✗")
            self.activity_table.setItem(row, 3, status_item)
            
            details = event.get('details', '')
            details_item = QTableWidgetItem(details)
            self.activity_table.setItem(row, 4, details_item)
            
            method_item = QTableWidgetItem(event.get('unlock_method', '-'))
            self.activity_table.setItem(row, 5, method_item)
    
    def on_filter_changed(self, filter_text):
        """Handle filter dropdown changes"""
        self.load_logs()
    
    def export_logs(self):
        """Export logs to CSV"""
        if not self.activity_manager:
            return
        
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Activity Log",
            "activity_log.csv",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            success = self.activity_manager.export_to_csv(file_path)
            if success:
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Activity log exported to:\n{file_path}"
                )

