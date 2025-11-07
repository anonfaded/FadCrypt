"""Statistics Window - Beautiful dashboard with charts and metrics"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QBrush
import json


class StatsWindow(QWidget):
    """Standalone statistics dashboard window"""
    
    def __init__(self, statistics_manager=None, resource_path=None, parent=None):
        super().__init__(parent)
        self.statistics_manager = statistics_manager
        self.resource_path = resource_path or self._default_resource_path
        self.init_ui()
        
        # Auto-refresh every 60 seconds
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_stats)
        self.refresh_timer.start(60000)
    
    def _default_resource_path(self, path):
        return path
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("FadCrypt Statistics")
        self.setGeometry(100, 100, 900, 700)
        
        # Dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #e0e0e0;
            }
            QScrollArea {
                border: none;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title
        title = QLabel("📊 Security Statistics Dashboard")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(sep)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # Create metric cards grid
        cards_layout = QGridLayout()
        cards_layout.setSpacing(15)
        
        self.metric_cards = {}
        metrics = [
            ('total_items', '📦 Total Items', '0'),
            ('protection_pct', '🛡️ Protection %', '0%'),
            ('lock_streak', '🔥 Lock Streak', '0 days'),
            ('peak_hour', '🕐 Peak Lock Hour', '9 AM')
        ]
        
        for i, (key, label, default) in enumerate(metrics):
            card = self.create_metric_card(label, default)
            self.metric_cards[key] = card
            cards_layout.addWidget(card, i // 2, i % 2)
        
        metric_container = QWidget()
        metric_container.setLayout(cards_layout)
        scroll_layout.addWidget(metric_container)
        
        # Activity info
        activity_label = QLabel("📋 Recent Activity")
        activity_font = QFont()
        activity_font.setBold(True)
        activity_font.setPointSize(12)
        activity_label.setFont(activity_font)
        scroll_layout.addWidget(activity_label)
        
        self.activity_label = QLabel("No recent activity")
        self.activity_label.setStyleSheet("color: #999999;")
        self.activity_label.setWordWrap(True)
        scroll_layout.addWidget(self.activity_label)
        
        # Top locked items
        top_label = QLabel("🔒 Most Locked Items")
        top_font = QFont()
        top_font.setBold(True)
        top_font.setPointSize(12)
        top_label.setFont(top_font)
        scroll_layout.addWidget(top_label)
        
        self.top_items_label = QLabel("Loading...")
        self.top_items_label.setStyleSheet("color: #999999;")
        self.top_items_label.setWordWrap(True)
        scroll_layout.addWidget(self.top_items_label)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff3333, stop:1 #cc0000);
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
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
        refresh_btn.clicked.connect(self.refresh_stats)
        main_layout.addWidget(refresh_btn)
        
        # Load initial stats
        self.refresh_stats()
    
    def create_metric_card(self, label: str, value: str) -> QWidget:
        """Create a metric card widget"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #999999; font-size: 11pt;")
        layout.addWidget(label_widget)
        
        value_widget = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(24)
        value_font.setBold(True)
        value_widget.setFont(value_font)
        value_widget.setStyleSheet("color: #d32f2f;")
        layout.addWidget(value_widget)
        
        card._value_widget = value_widget
        return card
    
    def refresh_stats(self):
        """Refresh statistics from manager"""
        if not self.statistics_manager:
            return
        
        stats = self.statistics_manager.get_stats(use_cache=False)
        
        summary = stats.get('summary', {})
        activity = stats.get('activity', {})
        items = stats.get('items', {})
        
        # Update metric cards
        self.metric_cards['total_items']._value_widget.setText(
            str(summary.get('total_items', 0))
        )
        self.metric_cards['protection_pct']._value_widget.setText(
            f"{summary.get('protection_percentage', 0)}%"
        )
        self.metric_cards['lock_streak']._value_widget.setText(
            f"{summary.get('lock_streak_days', 0)} days"
        )
        
        peak_hour = activity.get('peak_lock_hour', 0)
        self.metric_cards['peak_hour']._value_widget.setText(
            f"{peak_hour}:00"
        )
        
        # Update activity
        last_activity = activity.get('last_activity')
        if last_activity:
            activity_text = f"Last: {last_activity.get('type', 'unknown')} - {last_activity.get('item', 'N/A')}"
            self.activity_label.setText(activity_text)
        else:
            self.activity_label.setText("No recent activity")
        
        # Update top items
        most_locked = items.get('most_locked', [])
        if most_locked:
            top_text = "\n".join([f"• {name}: {count} unlocks" for name, count in most_locked])
            self.top_items_label.setText(top_text)
        else:
            self.top_items_label.setText("No locked items yet")
    
    def closeEvent(self, event):
        """Handle window close event - minimize to tray instead of closing"""
        try:
            # Don't close the window, minimize it instead
            event.ignore()
            self.hide()
            if self.refresh_timer:
                self.refresh_timer.stop()
            print("📊 Stats window close button clicked - minimizing to system tray")
        except Exception as e:
            print(f"[Stats Window] Error in closeEvent: {e}")
            event.accept()
