"""Enhanced Statistics Window - Beautiful dashboard with pie/line charts and duration metrics"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QGridLayout, QFrame, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer, QEvent, QRect, QPoint
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPen, QIcon
from PyQt6.QtCore import QSize
import pyqtgraph as pg
import json


class PieChartWidget(QWidget):
    """Enhanced pie chart widget with labels below and hover information"""
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setMinimumSize(350, 400)
        self.title = title
        self.labels = []
        self.data = []
        self.category_items = {}  # Maps category index to list of items in that category
        # Material Design colors - calm and pleasant
        self.colors = [
            '#9C27B0',  # Material Purple (500)
            '#00BCD4',  # Material Cyan (500)
            '#FF9800',  # Material Orange (500)
            '#4CAF50',  # Material Green (500)
            '#F44336',  # Material Red (500)
            '#3F51B5',  # Material Indigo (500)
            '#FFC107'   # Material Amber (500)
        ]
        self.hovered_slice = -1
        self.hover_tooltip = ""
        self.setMouseTracking(True)
        self.setStyleSheet("background-color: #1e1e1e; border-radius: 4px;")
    
    def set_data(self, labels, data, category_items=None):
        """Set pie chart data"""
        self.labels = labels
        self.data = data
        self.category_items = category_items or {}
        
        # Build mapping from slice_index to label_index (for category_items lookup)
        # This is needed because category_items uses label indices, but we use slice indices
        self.slice_to_label = {}
        slice_idx = 0
        for label_idx, value in enumerate(data):
            if value > 0:
                self.slice_to_label[slice_idx] = label_idx
                slice_idx += 1
        
        self.hovered_slice = -1
        self.hover_tooltip = ""
        self.update()
    
    def _get_slice_at_position(self, x, y):
        """Get slice index at given position"""
        # Chart area dimensions (matching paintEvent layout)
        pie_size = min(self.width() // 2 - 40, 250)
        chart_x = 30
        chart_y = 40
        
        center_x = chart_x + pie_size // 2
        center_y = chart_y + pie_size // 2
        dx = x - center_x
        dy = y - center_y
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance < pie_size // 2:
            # Over the pie - calculate angle
            import math
            # Calculate angle from center
            # Qt's drawPie: 0 degrees is at 3 o'clock position, goes counter-clockwise
            # atan2 gives angle from positive x-axis (3 o'clock), ranges from -pi to pi
            angle_rad = math.atan2(-dy, dx)  # Negative dy because Qt Y-axis points down
            
            # Convert to degrees and normalize to 0-360 range (counter-clockwise from 3 o'clock)
            angle_deg = math.degrees(angle_rad)
            if angle_deg < 0:
                angle_deg += 360
            
            # Now angle_deg is 0-360 where 0 is at 3 o'clock, increases counter-clockwise
            # Our pie slices are drawn starting at 0 (3 o'clock) going counter-clockwise
            # So we can directly compare
            
            # Map angle to slice
            total = sum(self.data) if self.data else 0
            if total == 0:
                return -1
            
            current_angle = 0  # Start at 3 o'clock (0 degrees in Qt)
            slice_index = 0  # Track actual slice number, not enumerate index
            for i, value in enumerate(self.data):
                if value == 0:
                    continue
                slice_span = (value / total) * 360
                # Check if mouse angle falls within this slice's range
                end_angle = current_angle + slice_span
                if current_angle <= angle_deg < end_angle:
                    return slice_index  # Return slice index, not enumerate index
                current_angle = end_angle
                slice_index += 1  # Increment only for non-zero slices
        return -1
    
    def mouseMoveEvent(self, event):
        """Handle mouse hover for slice highlighting"""
        new_hovered = self._get_slice_at_position(event.pos().x(), event.pos().y())
        # Always update state and repaint, even if same slice (maintains hover visual)
        self.hovered_slice = new_hovered
        # Generate tooltip using slice_to_label mapping
        if new_hovered >= 0 and new_hovered in self.slice_to_label:
            label_idx = self.slice_to_label[new_hovered]
            items_list = self.category_items.get(label_idx, [])
            if items_list:
                self.hover_tooltip = f"{self.labels[label_idx]}:\n" + "\n".join([f"  • {item}" for item in items_list[:5]])
                if len(items_list) > 5:
                    self.hover_tooltip += f"\n  ... and {len(items_list) - 5} more"
            else:
                self.hover_tooltip = self.labels[label_idx]
        else:
            self.hover_tooltip = ""
        # Always repaint to maintain hover state
        self.repaint()
        # Continue processing event
        super().mouseMoveEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leaving widget"""
        if self.hovered_slice >= 0 or self.hover_tooltip:
            self.hovered_slice = -1
            self.hover_tooltip = ""
            # Force immediate repaint
            self.repaint()
        # Continue processing event
        super().leaveEvent(event)
    
    def paintEvent(self, event):
        """Draw pie chart with legend below"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor("#1e1e1e"))
        
        # Draw title
        if self.title:
            title_font = painter.font()
            title_font.setPointSize(11)
            title_font.setBold(True)
            painter.setFont(title_font)
            painter.setPen(QPen(QColor("#fff")))
            painter.drawText(0, 5, self.width(), 25, Qt.AlignmentFlag.AlignCenter, self.title)
        
        if not self.data or sum(self.data) == 0:
            painter.setPen(QPen(QColor("#999")))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No data available")
            return
        
        # Layout: Pie chart on LEFT, Legend on RIGHT
        # Pie chart dimensions (left side)
        pie_size = min(self.width() // 2 - 40, 250)
        chart_x = 30
        chart_y = 40
        
        # Legend starts on right side
        legend_x = self.width() // 2 + 20
        legend_y_start = chart_y
        
        # Draw pie slices
        total = sum(self.data)
        angle_start = 0
        
        import math
        slice_index = 0  # Track actual slice number for color mapping
        for i, (label, value) in enumerate(zip(self.labels, self.data)):
            if value == 0:
                continue
            
            angle_span = (value / total) * 360
            angle_span_qt = int(angle_span * 16)
            angle_start_qt = int(angle_start * 16)
            
            # Draw slice with hover effect - use slice_index for color, not enumerate index i
            color_hex = self.colors[slice_index % len(self.colors)]
            color = QColor(color_hex)
            if slice_index == self.hovered_slice:
                color.setAlpha(255)
                painter.setBrush(QBrush(color))
                painter.setPen(QPen(QColor("#fff"), 3))
            else:
                painter.setBrush(QBrush(color))
                painter.setPen(QPen(QColor("#2a2a2a"), 1))
            
            painter.drawPie(QRect(chart_x, chart_y, pie_size, pie_size), angle_start_qt, angle_span_qt)
            angle_start += angle_span
            slice_index += 1  # Increment slice counter
        
        # Reset painter state after drawing pie slices
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#e0e0e0"), 1))
        
        # Draw legend on RIGHT side in vertical column
        row_height = 30
        slice_index = 0
        current_y = legend_y_start
        
        for i, (label, value) in enumerate(zip(self.labels, self.data)):
            if value == 0:
                continue
            
            percentage = (value / total) * 100
            
            # Draw color swatch with correct color for this slice - explicitly set brush and pen
            color_hex = self.colors[slice_index % len(self.colors)]
            color = QColor(color_hex)
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("#555"), 1))
            painter.drawRect(legend_x, current_y - 8, 14, 14)
            
            # Draw category name and percentage to the right of swatch
            legend_font = painter.font()
            legend_font.setPointSize(10)
            painter.setFont(legend_font)
            painter.setPen(QPen(QColor("#e0e0e0")))
            
            text = f"{label} ({percentage:.1f}%)"
            max_text_width = self.width() - legend_x - 35
            painter.drawText(legend_x + 20, current_y - 8, max_text_width, 18,
                           Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
            
            current_y += row_height
            slice_index += 1
        
        # Reset painter state before drawing tooltip
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#fff"), 1))
        
        # Draw hover tooltip if hovering over a slice - positioned in top-right corner with background
        if self.hovered_slice >= 0 and self.hover_tooltip:
            tooltip_lines = self.hover_tooltip.split('\n')
            max_line_width = max([painter.fontMetrics().horizontalAdvance(line) for line in tooltip_lines])
            
            # Tooltip box dimensions
            padding = 12
            line_height = 20
            tooltip_width = min(max_line_width + padding * 2 + 25, 300)  # Extra space for color indicator
            tooltip_height = len(tooltip_lines) * line_height + padding * 2
            
            # Position in top-right corner
            tooltip_x = self.width() - tooltip_width - 10
            tooltip_y = 50
            
            # Draw DARK GRAY semi-transparent background (not category color) - explicitly set brush
            painter.setBrush(QBrush(QColor(30, 30, 30, 245)))
            painter.setPen(QPen(QColor("#555"), 2))
            painter.drawRect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
            
            # Draw category color indicator bar on the left side of tooltip
            category_color = QColor(self.colors[self.hovered_slice % len(self.colors)])
            painter.setBrush(QBrush(category_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(tooltip_x + 2, tooltip_y + 2, 6, tooltip_height - 4)
            
            # Draw tooltip text
            painter.setFont(QFont("sans-serif", 9))
            
            current_y = tooltip_y + padding
            for i, line in enumerate(tooltip_lines):
                # First line is the category name - make it bold and colored
                if i == 0:
                    font = painter.font()
                    font.setBold(True)
                    font.setPointSize(10)
                    painter.setFont(font)
                    painter.setPen(QPen(QColor("#fff")))  # White for readability
                    painter.drawText(tooltip_x + padding + 12, current_y, tooltip_width - padding * 2 - 12, line_height,
                                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, line)
                    # Reset font
                    font.setBold(False)
                    font.setPointSize(9)
                    painter.setFont(font)
                else:
                    # Item lines - light gray for good contrast on dark background
                    painter.setPen(QPen(QColor("#d0d0d0")))
                    painter.drawText(tooltip_x + padding + 12, current_y, tooltip_width - padding * 2 - 12, line_height,
                                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, line)
                current_y += line_height


class EnhancedStatsWindow(QWidget):
    """Enhanced statistics dashboard with charts"""
    
    def __init__(self, statistics_manager=None, resource_path=None, parent=None):
        super().__init__(parent)
        self.statistics_manager = statistics_manager
        self.resource_path = resource_path or self._default_resource_path
        
        # Enable antialiasing for better chart quality
        pg.setConfigOption('antialias', True)
        
        self.init_ui()
        
        # Set window icon
        icon_path = self.resource_path('img/icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Auto-refresh timer - only when window is visible
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_stats)
        self.refresh_timer.start(1000)  # Update every 1 second when visible
    
    def _default_resource_path(self, path):
        return path
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("FadCrypt Statistics & Analytics")
        self.setGeometry(100, 100, 1200, 800)
        
        # Dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #e0e0e0;
            }
            QTabWidget {
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #e0e0e0;
                padding: 8px 20px;
            }
            QTabBar::tab:selected {
                background-color: #FF6B6B;
                color: white;
            }
            QScrollArea {
                border: none;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Title
        title = QLabel("📊 FadCrypt Security Analytics")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        sep.setStyleSheet("color: #444;")
        main_layout.addWidget(sep)
        
        # Overview content directly (no tabs)
        overview_widget = self._create_overview_tab()
        main_layout.addWidget(overview_widget, 1)
    
    def changeEvent(self, event):
        """Handle visibility changes to manage refresh timer"""
        try:
            from PyQt6.QtCore import QEvent
            if event.type() == QEvent.Type.WindowDeactivate:
                if self.refresh_timer:
                    self.refresh_timer.stop()
            elif event.type() == QEvent.Type.WindowActivate:
                if self.refresh_timer:
                    self.refresh_timer.start()
            super().changeEvent(event)
        except Exception as e:
            print(f"[Stats Window] Error in changeEvent: {e}")
            import traceback
            traceback.print_exc()
    
    def closeEvent(self, event):
        """Handle window close event - minimize to tray instead of closing"""
        try:
            # Don't close the window, minimize it instead
            event.ignore()
            self.hide()
            print("📊 Stats window close button clicked - minimizing to system tray")
        except Exception as e:
            print(f"[Stats Window] Error in closeEvent: {e}")
            import traceback
            traceback.print_exc()
            event.accept()
    
    def _create_overview_tab(self) -> QWidget:
        """Create overview tab with key metrics"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Metric cards in grid
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Top metrics row
        self.metric_cards = {}
        
        # Row 1: 4 cards (Total Items, Lock Events, Unlock Events, Failed Attempts)
        # Total items
        card1 = self._create_metric_card("📦 Total Items", "0",
                                        "Total count of all applications and locked files/folders")
        self.metric_cards['total_items'] = card1
        grid.addWidget(card1, 0, 0)
        
        # Lock Events
        card2 = self._create_metric_card("🔒 Lock Events", "0",
                                        "Total number of lock operations performed")
        self.metric_cards['lock_events'] = card2
        grid.addWidget(card2, 0, 1)
        
        # Unlock Events
        card3 = self._create_metric_card("🔓 Unlock Events", "0",
                                        "Total number of unlock operations performed")
        self.metric_cards['unlock_events'] = card3
        grid.addWidget(card3, 0, 2)
        
        # Failed Attempts (moved to first row)
        card4 = self._create_metric_card("⚠️ Failed Attempts", "0",
                                        "Number of failed unlock attempts")
        self.metric_cards['failed_attempts'] = card4
        grid.addWidget(card4, 0, 3)
        
        content_layout.addLayout(grid)
        
        # Row 2: 3 cards centered using HBoxLayout with stretches
        row2_layout = QHBoxLayout()
        row2_layout.addStretch(1)  # Left stretch
        
        # Uptime
        card5 = self._create_metric_card("⏱️ FadCrypt Uptime", "0h 0m",
                                        "How long FadCrypt has been running since first startup")
        self.metric_cards['uptime'] = card5
        row2_layout.addWidget(card5)
        
        row2_layout.addSpacing(15)  # Match grid spacing
        
        # Avg Lock Duration (live-updating average of how long items have been locked)
        card6 = self._create_metric_card("⌛ Avg Lock Duration", "0s",
                                        "Average time items have been in locked state (updates live every second)",
                                        info_callback=self.show_lock_duration_details)
        self.metric_cards['avg_lock_duration'] = card6
        row2_layout.addWidget(card6)
        
        row2_layout.addSpacing(15)  # Match grid spacing
        
        # Avg Unlock Duration (live-updating average of how long items have been unlocked)
        card7 = self._create_metric_card("⏱️ Avg Unlock Duration", "0s",
                                        "Average time items have been in unlocked state (updates live every second)",
                                        info_callback=self.show_unlock_duration_details)
        self.metric_cards['avg_unlock_duration'] = card7
        row2_layout.addWidget(card7)
        
        row2_layout.addStretch(1)  # Right stretch
        
        content_layout.addLayout(row2_layout)
        
        # Pie chart and statistics section at bottom
        content_layout.addSpacing(30)
        stats_section_label = QLabel("📊 Distribution & Statistics")
        stats_font = QFont()
        stats_font.setPointSize(14)
        stats_font.setBold(True)
        stats_section_label.setFont(stats_font)
        content_layout.addWidget(stats_section_label)
        
        # Horizontal layout: Pie chart on left, statistics on right
        pie_stats_layout = QHBoxLayout()
        pie_stats_layout.setSpacing(20)
        
        # LEFT: Pie chart
        self.pie_chart = PieChartWidget(title="Item Type Distribution")
        self.pie_chart.setMinimumHeight(320)
        self.pie_chart.setMaximumHeight(400)
        pie_stats_layout.addWidget(self.pie_chart, 1)  # Takes 1 proportion
        
        # RIGHT: Statistics panel
        stats_panel = QWidget()
        stats_panel.setStyleSheet("""
            QWidget {
                background-color: #2a2a2a;
                border-radius: 8px;
                border: 1px solid #3a3a3a;
            }
        """)
        stats_panel_layout = QVBoxLayout(stats_panel)
        stats_panel_layout.setContentsMargins(20, 20, 20, 20)
        stats_panel_layout.setSpacing(15)
        
        # Most locked items
        most_locked_label = QLabel("🔒 Most Locked Items")
        most_locked_font = QFont()
        most_locked_font.setPointSize(12)
        most_locked_font.setBold(True)
        most_locked_label.setFont(most_locked_font)
        most_locked_label.setStyleSheet("""
            QLabel {
                padding: 10px 15px;
                background-color: transparent;
            }
        """)
        stats_panel_layout.addWidget(most_locked_label)
        
        self.most_locked_widget = QLabel("Loading...")
        self.most_locked_widget.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                padding: 15px;
                border-radius: 4px;
                color: #b0b0b0;
            }
        """)
        stats_panel_layout.addWidget(self.most_locked_widget)
        
        stats_panel_layout.addStretch()
        pie_stats_layout.addWidget(stats_panel, 1)  # Takes 1 proportion (equal with pie chart)
        
        content_layout.addLayout(pie_stats_layout)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return widget
    
    def _create_charts_tab(self) -> QWidget:
        """Create charts visualization tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Info text
        info_text = QLabel("ℹ️ Visual Analytics\nPie chart shows distribution of protected items by type. Line chart shows 7-day activity trend.")
        info_text.setStyleSheet("color: #999; padding: 10px; background-color: #2a2a2a; border-radius: 4px;")
        layout.addWidget(info_text)
        
        # Horizontal layout for charts (equal spacing)
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)
        
        # Pie chart - item type distribution
        pie_label = QLabel("Item Type Distribution")
        pie_font = QFont()
        pie_font.setPointSize(11)
        pie_font.setBold(True)
        pie_label.setFont(pie_font)
        
        self.pie_chart = PieChartWidget(title="Item Distribution (Apps & Locked Files)")
        self.pie_chart.setMinimumHeight(300)
        
        pie_container = QVBoxLayout()
        pie_container.setContentsMargins(0, 15, 0, 0)  # Added 15px top margin for spacing from heading
        pie_container.setSpacing(8)  # Add spacing between label and chart
        pie_container.addWidget(pie_label)
        pie_container.addWidget(self.pie_chart, 1)
        pie_container_widget = QWidget()
        pie_container_widget.setLayout(pie_container)
        charts_layout.addWidget(pie_container_widget, 1)
        
        # Line chart - lock/unlock timeline
        timeline_label = QLabel("Lock/Unlock Timeline (7 days)")
        timeline_font = QFont()
        timeline_font.setPointSize(11)
        timeline_font.setBold(True)
        timeline_label.setFont(timeline_font)
        
        self.line_chart = pg.PlotWidget(title="")
        self.line_chart.setLabel('left', 'Events')
        self.line_chart.setLabel('bottom', 'Date')
        self.line_chart.showGrid(True, True)
        self.line_chart.setMouseEnabled(x=True, y=False)  # Allow x-axis hover
        self.line_chart.setMinimumHeight(300)
        
        timeline_container = QVBoxLayout()
        timeline_container.setContentsMargins(0, 15, 0, 0)  # Added 15px top margin for consistency
        timeline_container.setSpacing(8)  # Add spacing between label and chart
        timeline_container.addWidget(timeline_label)
        timeline_container.addWidget(self.line_chart, 1)
        timeline_container_widget = QWidget()
        timeline_container_widget.setLayout(timeline_container)
        charts_layout.addWidget(timeline_container_widget, 1)
        
        layout.addLayout(charts_layout, 1)
        return widget
    
    def _create_metric_card(self, title: str, value: str, tooltip: str = "", info_callback=None) -> QFrame:
        """Create a metric display card with optional info button"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 8px;
                border: 1px solid #3a3a3a;
            }
        """)
        card.setMinimumHeight(120)  # Increased from 100 to 120
        card.setMaximumHeight(120)  # Fixed height to prevent expanding
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 20, 25, 20)  # Increased inner padding for more space from borders
        layout.setSpacing(12)  # Increased space between title and value
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # Vertically center content
        
        # Title with optional info button
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_row.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(10)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #999; padding: 4px 8px;")  # Added inner padding to label
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center text horizontally
        
        title_row.addStretch()
        title_row.addWidget(title_label)
        
        # Add info button if callback provided
        if info_callback:
            info_btn = QPushButton("ℹ️")
            info_btn.setFixedSize(24, 24)
            info_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a3a;
                    border: 1px solid #4a4a4a;
                    border-radius: 12px;
                    color: #9C27B0;
                    font-size: 14px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                    border-color: #9C27B0;
                }
                QPushButton:pressed {
                    background-color: #5a5a5a;
                }
            """)
            info_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            info_btn.clicked.connect(info_callback)
            info_btn.setToolTip("Click for detailed breakdown")
            title_row.addWidget(info_btn)
        
        title_row.addStretch()
        
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(20)  # Increased from 18 to 20
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet("color: #FF6B6B; padding: 4px 8px;")  # Added inner padding to label
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center text horizontally
        
        layout.addStretch()  # Top stretch
        layout.addLayout(title_row)
        layout.addWidget(value_label)
        layout.addStretch()  # Bottom stretch
        
        # Add tooltip if provided
        if tooltip:
            card.setToolTip(tooltip)
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
    
    def refresh_stats(self):
        """Refresh all statistics"""
        # Don't refresh if window is not visible (minimized/hidden)
        if not self.isVisible():
            return
        
        if not self.statistics_manager:
            return
        
        try:
            stats = self.statistics_manager.get_comprehensive_stats()
            self._update_overview(stats)
            self._update_charts(stats)
        except Exception as e:
            print(f"Error refreshing stats: {e}")
    
    def _update_overview(self, stats: dict):
        """Update overview tab metrics"""
        try:
            summary = stats.get('summary', {})
            activity = stats.get('activity', {})
            
            self.metric_cards['total_items'].value_label.setText(
                str(summary.get('total_items', 0))
            )
            self.metric_cards['lock_events'].value_label.setText(
                str(activity.get('total_lock_events', 0))
            )
            self.metric_cards['unlock_events'].value_label.setText(
                str(activity.get('total_unlock_events', 0))
            )
            
            # Failed attempts (show live data)
            self.metric_cards['failed_attempts'].value_label.setText(
                str(activity.get('failed_unlock_attempts', 0))
            )
            
            uptime = stats.get('session_uptime', {})
            uptime_str = uptime.get('uptime_formatted', 'N/A')
            self.metric_cards['uptime'].value_label.setText(uptime_str)
            
            durations = stats.get('durations', {})
            avg_lock = durations.get('averages', {}).get('avg_lock_duration_seconds', 0)
            self._format_duration_card(self.metric_cards['avg_lock_duration'], avg_lock)
            
            # Average unlock duration (show live data)
            avg_unlock = durations.get('averages', {}).get('avg_unlock_duration_seconds', 0)
            self._format_duration_card(self.metric_cards['avg_unlock_duration'], avg_unlock)
            
            # Most locked items
            items = stats.get('items', {}).get('most_locked', [])
            items_text = "\n".join([f"• {item[0]}: {item[1]} times" for item in items[:5]]) if items else "No data yet"
            self.most_locked_widget.setText(items_text)
        except Exception as e:
            print(f"Error updating overview: {e}")
    
    def _update_charts(self, stats: dict):
        """Update pie and line charts"""
        try:
            # Pie chart - item type distribution
            pie_data = stats.get('pie_chart', {})
            labels = pie_data.get('labels', [])
            data = pie_data.get('data', [])
            
            if data and sum(data) > 0:
                self._draw_pie_chart(labels, data)
        except Exception as e:
            print(f"Error updating charts: {e}")
    
    def _draw_pie_chart(self, labels: list, data: list):
        """Draw circular pie chart visualization"""
        try:
            # Ensure data is numeric and non-negative
            numeric_data = [max(0, int(float(d)) if d else 0) for d in data]
            
            # Skip if no data
            if not numeric_data or sum(numeric_data) == 0:
                self.pie_chart.set_data([], [])
                return
            
            # Get category items from config for hover tooltip
            category_items = {}
            try:
                # Try to get from pie_chart stats (newer format)
                if hasattr(self, 'statistics_manager') and self.statistics_manager:
                    pie_stats = self.statistics_manager.get_pie_chart_data()
                    category_items = pie_stats.get('category_items', {})
            except:
                pass
            
            self.pie_chart.set_data(labels, numeric_data, category_items)
            
        except Exception as e:
            print(f"Error drawing pie chart: {e}")
    
    @staticmethod
    def _format_timestamp(timestamp_str: str) -> str:
        """Format ISO timestamp to 12-hour AM/PM format like '24th June 2024, 03:45 PM'"""
        if not timestamp_str or timestamp_str == 'N/A':
            return 'N/A'
        
        try:
            from datetime import datetime
            # Parse ISO format: "2025-10-19T14:30:45"
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
            # Format as: "24th June 2024, 03:45 PM"
            day = dt.day
            # Get ordinal suffix (st, nd, rd, th)
            if day in [1, 21, 31]:
                day_suffix = 'st'
            elif day in [2, 22]:
                day_suffix = 'nd'
            elif day in [3, 23]:
                day_suffix = 'rd'
            else:
                day_suffix = 'th'
            
            month = dt.strftime('%B')  # Full month name
            year = dt.year
            time_12h = dt.strftime('%I:%M %p')  # 12-hour format with AM/PM
            
            return f"{day}{day_suffix} {month} {year}, {time_12h}"
        except:
            return timestamp_str[:19] if timestamp_str else 'N/A'
    
    @staticmethod
    def _format_duration_card(card: QFrame, seconds: float):
        """Format duration into human readable form"""
        card.value_label.setText(EnhancedStatsWindow._format_seconds(seconds))
    
    @staticmethod
    def _format_seconds(seconds: float) -> str:
        """Convert seconds to human readable format - only show non-zero values"""
        seconds = int(seconds)
        
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            # Only show seconds if non-zero
            if secs > 0:
                return f"{minutes}m {secs}s"
            return f"{minutes}m"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            # Build result with non-zero values only
            parts = []
            if hours > 0:
                parts.append(f"{hours}h")
            if minutes > 0:
                parts.append(f"{minutes}m")
            if secs > 0:
                parts.append(f"{secs}s")
            return " ".join(parts) if parts else "0s"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            # Build result with non-zero values only
            parts = []
            if days > 0:
                parts.append(f"{days}d")
            if hours > 0:
                parts.append(f"{hours}h")
            if minutes > 0:
                parts.append(f"{minutes}m")
            if secs > 0:
                parts.append(f"{secs}s")
            return " ".join(parts) if parts else "0s"
    
    def show_lock_duration_details(self):
        """Show detailed breakdown of lock durations per item"""
        if not self.statistics_manager:
            return
        
        try:
            stats = self.statistics_manager.get_comprehensive_stats()
            durations = stats.get('durations', {})
            by_item = durations.get('by_item', {})
            
            # Build detailed message
            message = "🔒 Lock Duration Breakdown\n\n"
            message += "Shows how long each item has been in locked state.\n"
            message += "Includes both completed cycles and currently locked items (live).\n\n"
            
            if not by_item:
                message += "No lock duration data yet.\n"
                message += "Items will appear here once they've been locked."
            else:
                # Sort by lock duration (descending)
                sorted_items = sorted(
                    by_item.items(),
                    key=lambda x: x[1].get('avg_lock_duration_seconds', 0),
                    reverse=True
                )
                
                for item_name, data in sorted_items[:10]:  # Top 10 items
                    lock_dur = data.get('avg_lock_duration_seconds', 0)
                    lock_sessions = data.get('total_lock_sessions', 0)
                    if lock_dur > 0:
                        dur_str = self._format_seconds(lock_dur)
                        message += f"• {item_name}\n"
                        message += f"  Avg locked: {dur_str} ({lock_sessions} sessions)\n\n"
            
            # Show in message box
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle("Lock Duration Details")
            msg.setText(message)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #2a2a2a;
                }
                QMessageBox QLabel {
                    color: #e0e0e0;
                    font-size: 11pt;
                    background-color: transparent;
                }
                QMessageBox QPushButton {
                    background-color: #9C27B0;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #7B1FA2;
                }
            """)
            msg.exec()
        except Exception as e:
            print(f"Error showing lock duration details: {e}")
    
    def show_unlock_duration_details(self):
        """Show detailed breakdown of unlock durations per item"""
        if not self.statistics_manager:
            return
        
        try:
            stats = self.statistics_manager.get_comprehensive_stats()
            durations = stats.get('durations', {})
            by_item = durations.get('by_item', {})
            
            # Build detailed message
            message = "🔓 Unlock Duration Breakdown\n\n"
            message += "Shows how long each item has been in unlocked state.\n"
            message += "Includes both completed cycles and currently unlocked items (live).\n\n"
            
            if not by_item:
                message += "No unlock duration data yet.\n"
                message += "Items will appear here once they've been unlocked."
            else:
                # Sort by unlock duration (descending)
                sorted_items = sorted(
                    by_item.items(),
                    key=lambda x: x[1].get('avg_unlock_duration_seconds', 0),
                    reverse=True
                )
                
                for item_name, data in sorted_items[:10]:  # Top 10 items
                    unlock_dur = data.get('avg_unlock_duration_seconds', 0)
                    unlock_sessions = data.get('total_unlock_sessions', 0)
                    if unlock_dur > 0:
                        dur_str = self._format_seconds(unlock_dur)
                        message += f"• {item_name}\n"
                        message += f"  Avg unlocked: {dur_str} ({unlock_sessions} sessions)\n\n"
            
            # Show in message box
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle("Unlock Duration Details")
            msg.setText(message)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #2a2a2a;
                }
                QMessageBox QLabel {
                    color: #e0e0e0;
                    font-size: 11pt;
                    background-color: transparent;
                }
                QMessageBox QPushButton {
                    background-color: #9C27B0;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #7B1FA2;
                }
            """)
            msg.exec()
        except Exception as e:
            print(f"Error showing unlock duration details: {e}")

