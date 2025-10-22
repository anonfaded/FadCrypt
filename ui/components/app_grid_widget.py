"""Application Grid Widget for FadCrypt Qt"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QFrame, QGridLayout, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon, QMouseEvent, QCursor
import os
import subprocess


class AppCard(QFrame):
    """Individual application card widget"""
    
    clicked = pyqtSignal(str)  # app_name
    double_clicked = pyqtSignal(str)  # app_name
    context_menu_requested = pyqtSignal(str, object)  # app_name, position
    
    def __init__(self, app_name, app_path, unlock_count=0, date_added=None, parent=None):
        super().__init__(parent)
        self.app_name = app_name
        self.app_path = app_path
        self.unlock_count = unlock_count
        self.date_added = date_added
        self.is_selected = False
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the card UI"""
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setStyleSheet("""
            AppCard {
                background-color: #2a2a2a;
                border: 2px solid #444444;
                border-radius: 10px;
                padding: 12px;
            }
            AppCard:hover {
                border: 2px solid #d32f2f;
                background-color: #333333;
            }
        """)
        self.setMinimumSize(220, 220)
        self.setMaximumSize(280, 280)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(8)
        
        # Icon
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background-color: transparent;")
        try:
            icon_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            icon_label.setAutoFillBackground(False)
        except Exception:
            pass
        
        # Try to load app icon
        pixmap = self.load_app_icon()
        if pixmap:
            icon_label.setPixmap(pixmap.scaled(56, 56, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            # Fallback emoji
            icon_label.setText("📦")
            icon_label.setStyleSheet("font-size: 42px; background-color: transparent;")
        
        layout.addWidget(icon_label)
        
        # App name
        name_label = QLabel(self.app_name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setMaximumHeight(40)
        name_label.setStyleSheet("""
            color: #ffffff;
            font-size: 11pt;
            font-weight: bold;
            background-color: transparent;
        """)
        layout.addWidget(name_label)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #444444; max-height: 1px;")
        layout.addWidget(separator)
        
        # Path info
        path_display = os.path.basename(self.app_path)
        if len(path_display) > 25:
            path_display = path_display[:22] + "..."
        path_label = QLabel(f"📁 {path_display}")
        path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        path_label.setToolTip(self.app_path)  # Full path on hover
        path_label.setStyleSheet("""
            color: #888888;
            font-size: 8pt;
            background-color: transparent;
        """)
        layout.addWidget(path_label)
        
        # Date added
        if self.date_added:
            from datetime import datetime
            try:
                # If date_added is timestamp
                if isinstance(self.date_added, (int, float)):
                    date_obj = datetime.fromtimestamp(self.date_added)
                else:
                    date_obj = datetime.fromisoformat(self.date_added)
                date_str = date_obj.strftime("%b %d, %Y")
            except:
                date_str = str(self.date_added)
        else:
            date_str = "Recently added"
        
        date_label = QLabel(f"📅 {date_str}")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_label.setStyleSheet("""
            color: #888888;
            font-size: 8pt;
            background-color: transparent;
        """)
        layout.addWidget(date_label)
        
        # Stats
        stats_label = QLabel(f"🔓 {self.unlock_count}× unlocked")
        stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_label.setStyleSheet("""
            color: #888888;
            font-size: 8pt;
            background-color: transparent;
        """)
        layout.addWidget(stats_label)
        
        self.setLayout(layout)
    
    def load_app_icon(self):
        """Load icon for the application"""
        try:
            # Windows: Try to extract icon from exe file
            if os.name == 'nt':
                # First try direct extraction if it's an exe
                if self.app_path.lower().endswith('.exe'):
                    try:
                        pixmap = self._extract_windows_icon(self.app_path)
                        if pixmap:
                            return pixmap
                    except Exception as e:
                        print(f"Error extracting Windows icon from {self.app_path}: {e}")
                
                # Try to find exe path via Windows-specific methods
                exe_path = self._find_windows_icon()
                if exe_path and exe_path.lower().endswith('.exe'):
                    try:
                        pixmap = self._extract_windows_icon(exe_path)
                        if pixmap:
                            return pixmap
                    except Exception as e:
                        print(f"Error extracting Windows icon from {exe_path}: {e}")
            
            # Try to find icon from .desktop file (Linux) or Windows methods
            icon_path = self.find_desktop_icon()
            if icon_path:
                if os.name == 'nt' and icon_path.lower().endswith('.exe'):
                    # For Windows, if we found an exe, extract icon from it
                    try:
                        pixmap = self._extract_windows_icon(icon_path)
                        if pixmap:
                            return pixmap
                    except Exception as e:
                        print(f"Error extracting Windows icon from desktop icon path {icon_path}: {e}")
                elif not icon_path.endswith('.svg'):
                    # For Linux or direct icon paths
                    return QPixmap(icon_path)
            
            # Try common icon locations (Linux)
            app_name = os.path.basename(self.app_path).lower()
            icon_locations = [
                f'/usr/share/pixmaps/{app_name}.png',
                f'/usr/share/icons/hicolor/48x48/apps/{app_name}.png',
                f'/usr/share/icons/hicolor/64x64/apps/{app_name}.png',
            ]
            
            for path in icon_locations:
                if os.path.exists(path):
                    return QPixmap(path)
        except Exception as e:
            print(f"Error loading icon for {self.app_name}: {e}")
        
        return None
    
    def _extract_windows_icon(self, exe_path: str):
        """Extract icon from Windows exe file using Windows API."""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Windows API constants
            SHGFI_ICON = 0x100
            SHGFI_LARGEICON = 0x0
            
            # Load required DLLs
            user32 = ctypes.windll.user32
            shell32 = ctypes.windll.shell32
            gdi32 = ctypes.windll.gdi32
            
            # SHFILEINFO structure
            class SHFILEINFO(ctypes.Structure):
                _fields_ = [
                    ('hIcon', wintypes.HICON),
                    ('iIcon', ctypes.c_int),
                    ('dwAttributes', wintypes.DWORD),
                    ('szDisplayName', wintypes.WCHAR * 260),
                    ('szTypeName', wintypes.WCHAR * 80),
                ]
            
            # SHGetFileInfo function
            SHGetFileInfo = shell32.SHGetFileInfoW
            SHGetFileInfo.argtypes = [
                wintypes.LPWSTR,  # pszPath
                wintypes.DWORD,   # dwFileAttributes
                ctypes.POINTER(SHFILEINFO),  # psfi
                wintypes.UINT,    # cbFileInfo
                wintypes.UINT     # uFlags
            ]
            SHGetFileInfo.restype = wintypes.DWORD
            
            # Get the icon
            shfi = SHFILEINFO()
            flags = SHGFI_ICON | SHGFI_LARGEICON
            result = SHGetFileInfo(exe_path, 0, ctypes.byref(shfi), ctypes.sizeof(shfi), flags)
            
            if result and shfi.hIcon:
                try:
                    # Convert HICON to QPixmap
                    return self._hicon_to_qpixmap(shfi.hIcon)
                finally:
                    # Clean up the icon
                    user32.DestroyIcon(shfi.hIcon)
                    
        except Exception as e:
            print(f"Error in _extract_windows_icon: {e}")
        
        return None
    
    def _hicon_to_qpixmap(self, hicon):
        """Convert Windows HICON to QPixmap."""
        try:
            import ctypes
            from ctypes import wintypes
            
            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32
            
            # Get icon info
            class ICONINFO(ctypes.Structure):
                _fields_ = [
                    ('fIcon', wintypes.BOOL),
                    ('xHotspot', wintypes.DWORD),
                    ('yHotspot', wintypes.DWORD),
                    ('hbmMask', wintypes.HBITMAP),
                    ('hbmColor', wintypes.HBITMAP),
                ]
            
            GetIconInfo = user32.GetIconInfo
            GetIconInfo.argtypes = [wintypes.HICON, ctypes.POINTER(ICONINFO)]
            GetIconInfo.restype = wintypes.BOOL
            
            iconinfo = ICONINFO()
            if not GetIconInfo(hicon, ctypes.byref(iconinfo)):
                return None
            
            try:
                # Get bitmap info
                class BITMAP(ctypes.Structure):
                    _fields_ = [
                        ('bmType', wintypes.LONG),
                        ('bmWidth', wintypes.LONG),
                        ('bmHeight', wintypes.LONG),
                        ('bmWidthBytes', wintypes.LONG),
                        ('bmPlanes', wintypes.WORD),
                        ('bmBitsPixel', wintypes.WORD),
                        ('bmBits', wintypes.LPVOID),
                    ]
                
                GetObject = gdi32.GetObjectW
                GetObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.POINTER(BITMAP)]
                GetObject.restype = ctypes.c_int
                
                bitmap = BITMAP()
                if not GetObject(iconinfo.hbmColor, ctypes.sizeof(BITMAP), ctypes.byref(bitmap)):
                    return None
                
                # Create QImage from bitmap data
                width = bitmap.bmWidth
                height = bitmap.bmHeight
                
                if width <= 0 or height <= 0 or width > 256 or height > 256:
                    return None
                
                # Get bitmap bits - limit size to prevent overflow
                bmp_size = width * height * 4  # Assume 32-bit
                if bmp_size > 1024 * 1024:  # 1MB limit
                    return None
                    
                bmp_data = (ctypes.c_byte * bmp_size)()
                
                GetBitmapBits = gdi32.GetBitmapBits
                GetBitmapBits.argtypes = [wintypes.HBITMAP, wintypes.LONG, ctypes.POINTER(ctypes.c_byte)]
                GetBitmapBits.restype = wintypes.LONG
                
                bits_got = GetBitmapBits(iconinfo.hbmColor, bmp_size, bmp_data)
                if bits_got <= 0:
                    return None
                
                # Create QImage from BGRA data (Windows bitmaps are often BGRA)
                from PyQt6.QtGui import QImage
                image = QImage(bmp_data, width, height, width * 4, QImage.Format.Format_ARGB32)
                
                # Convert BGRA to RGBA
                image = image.convertToFormat(QImage.Format.Format_RGBA8888)
                
                # Create QPixmap from QImage
                pixmap = QPixmap.fromImage(image)
                
                return pixmap
                
            finally:
                # Clean up bitmaps
                if iconinfo.hbmMask:
                    gdi32.DeleteObject(iconinfo.hbmMask)
                if iconinfo.hbmColor:
                    gdi32.DeleteObject(iconinfo.hbmColor)
                    
        except Exception as e:
            print(f"Error in _hicon_to_qpixmap: {e}")
        
        return None
    
    def find_desktop_icon(self):
        """Find icon from .desktop file (Linux) or Windows shortcuts/registry (Windows)"""
        try:
            if os.name == 'nt':  # Windows
                return self._find_windows_icon()
            else:  # Linux/Unix
                return self._find_linux_icon()
        except Exception as e:
            print(f"Error finding desktop icon: {e}")
        return None
    
    def _find_linux_icon(self):
        """Find icon from .desktop file (Linux)"""
        try:
            desktop_dirs = [
                '/usr/share/applications',
                '/usr/local/share/applications',
                os.path.expanduser('~/.local/share/applications')
            ]
            
            app_name = os.path.basename(self.app_path)
            
            for desktop_dir in desktop_dirs:
                if not os.path.exists(desktop_dir):
                    continue
                
                for filename in os.listdir(desktop_dir):
                    if not filename.endswith('.desktop'):
                        continue
                    
                    filepath = os.path.join(desktop_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            exec_path = None
                            icon_path = None
                            
                            for line in f:
                                line = line.strip()
                                if line.startswith('Exec='):
                                    exec_path = line.split('=', 1)[1].split()[0]
                                elif line.startswith('Icon='):
                                    icon_path = line.split('=', 1)[1]
                            
                            if exec_path and (app_name in exec_path or exec_path in self.app_path):
                                if icon_path:
                                    # If icon_path is not absolute, search for it
                                    if not os.path.isabs(icon_path):
                                        return self.find_icon_by_name(icon_path)
                                    return icon_path
                    except:
                        continue
        except Exception as e:
            print(f"Error finding Linux desktop icon: {e}")
        return None
    
    def _find_windows_icon(self):
        """Find icon for Windows applications"""
        try:
            # If it's already an exe file, use it for icon extraction
            if self.app_path.lower().endswith('.exe') and os.path.exists(self.app_path):
                return self.app_path
            
            # Try to find the exe file if we have a shortcut or other reference
            exe_path = self._resolve_windows_exe_path()
            if exe_path and os.path.exists(exe_path):
                return exe_path
            
            # Try common icon locations for the app name
            app_name = os.path.basename(self.app_path).lower().replace('.exe', '')
            icon_locations = [
                f"C:\\Program Files\\{app_name}\\{app_name}.exe",
                f"C:\\Program Files (x86)\\{app_name}\\{app_name}.exe",
                f"C:\\Program Files\\{app_name}\\bin\\{app_name}.exe",
                f"C:\\Program Files (x86)\\{app_name}\\bin\\{app_name}.exe",
            ]
            
            for path in icon_locations:
                if os.path.exists(path):
                    return path
                    
        except Exception as e:
            print(f"Error finding Windows icon: {e}")
        return None
    
    def _resolve_windows_exe_path(self):
        """Try to resolve the actual exe path from various Windows references"""
        try:
            # If it's a .lnk file, try to parse it
            if self.app_path.lower().endswith('.lnk'):
                return self._parse_lnk_target(self.app_path)
            
            # If it's in Start Menu or Desktop, look for the actual exe
            # This is a simplified approach - in a real implementation you'd use Windows APIs
            app_name = os.path.basename(self.app_path).lower().replace('.exe', '')
            
            # Common locations to search
            search_paths = [
                r"C:\Program Files",
                r"C:\Program Files (x86)",
                r"C:\Users\Public\Desktop",
                os.path.expanduser(r"~\Desktop"),
            ]
            
            for base_path in search_paths:
                if os.path.exists(base_path):
                    for root, dirs, files in os.walk(base_path):
                        for file in files:
                            if file.lower() == f"{app_name}.exe":
                                return os.path.join(root, file)
                                
        except Exception as e:
            print(f"Error resolving Windows exe path: {e}")
        return None
    
    def _parse_lnk_target(self, lnk_path):
        """Simple .lnk file parser to extract target path"""
        try:
            # Try using win32com if available
            import pythoncom
            from win32com.shell import shell
            
            shortcut = pythoncom.CoCreateInstance(
                shell.CLSID_ShellLink,
                None,
                pythoncom.CLSCTX_INPROC_SERVER,
                shell.IID_IShellLink
            )
            
            persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
            persist_file.Load(lnk_path)
            
            target_path = shortcut.GetPath(0)[0]
            return target_path if target_path and target_path.endswith('.exe') else None
            
        except ImportError:
            # Fallback: basic binary parsing
            try:
                with open(lnk_path, 'rb') as f:
                    data = f.read()
                
                data_str = data.decode('latin-1', errors='ignore')
                
                # Look for exe paths in the binary data
                if '.exe' in data_str:
                    # Find the last .exe occurrence (usually the target)
                    exe_pos = data_str.rfind('.exe')
                    if exe_pos != -1:
                        # Look backwards for path start
                        start_pos = max(0, exe_pos - 200)  # Reasonable limit
                        path_segment = data_str[start_pos:exe_pos + 4]
                        
                        # Find potential drive letter
                        for i in range(len(path_segment) - 1, -1, -1):
                            if path_segment[i] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' and i + 1 < len(path_segment) and path_segment[i + 1] == ':':
                                potential_path = path_segment[i:]
                                if os.path.exists(potential_path):
                                    return potential_path
                                break
                                
            except Exception as e:
                print(f"Error parsing lnk file: {e}")
                
        return None
    
    def find_icon_by_name(self, icon_name):
        """Find icon by name in standard directories"""
        icon_dirs = [
            '/usr/share/icons/hicolor/48x48/apps',
            '/usr/share/icons/hicolor/64x64/apps',
            '/usr/share/pixmaps',
        ]
        
        for icon_dir in icon_dirs:
            if not os.path.exists(icon_dir):
                continue
            
            for ext in ['.png', '.xpm', '']:
                icon_path = os.path.join(icon_dir, icon_name + ext)
                if os.path.exists(icon_path):
                    return icon_path
        
        return None
    
    def set_selected(self, selected):
        """Set selection state"""
        self.is_selected = selected
        if selected:
            self.setStyleSheet("""
                AppCard {
                    background-color: #064e3b;
                    border: 2px solid #10b981;
                    border-radius: 10px;
                    padding: 10px;
                }
            """)
        else:
            self.setStyleSheet("""
                AppCard {
                    background-color: #2a2a2a;
                    border: 2px solid #444444;
                    border-radius: 10px;
                    padding: 10px;
                }
                AppCard:hover {
                    border: 2px solid #d32f2f;
                    background-color: #333333;
                }
            """)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.app_name)
        elif event.button() == Qt.MouseButton.RightButton:
            self.context_menu_requested.emit(self.app_name, event.globalPosition().toPoint())
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Handle double click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.app_name)
        super().mouseDoubleClickEvent(event)


class AppGridWidget(QWidget):
    """Grid widget for displaying application cards"""
    
    # Signals for parent communication
    app_edited = pyqtSignal(str, str, str)  # old_name, new_name, new_path
    app_removed = pyqtSignal(str)  # app_name
    app_lock_toggled = pyqtSignal(str, bool)  # app_name, is_locked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.apps_data = {}  # {app_name: {'path': path, 'unlock_count': count}}
        self.app_cards = {}  # {app_name: AppCard widget}
        self.selected_apps = set()
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #0f0f0f;
            }
        """)
        
        # Container for grid
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #0f0f0f;")
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(15)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.container.setLayout(self.grid_layout)
        
        scroll.setWidget(self.container)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
        
        # Show empty state initially
        self.empty_state_widget = None
        self.show_empty_state()
    
    def show_empty_state(self):
        """Show empty state message when no apps"""
        if self.empty_state_widget is None:
            self.empty_state_widget = QWidget()
            empty_layout = QVBoxLayout()
            empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.setSpacing(15)
            
            # Icon
            icon_label = QLabel("📭")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setStyleSheet("font-size: 72px;")
            empty_layout.addWidget(icon_label)
            
            # Title
            title_label = QLabel("No Applications Added")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("""
                color: #ffffff;
                font-size: 18pt;
                font-weight: bold;
            """)
            empty_layout.addWidget(title_label)
            
            # Description
            desc_label = QLabel("Click the 'Add Application' button below to start\nprotecting your applications with encryption")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("""
                color: #888888;
                font-size: 11pt;
            """)
            empty_layout.addWidget(desc_label)
            
            self.empty_state_widget.setLayout(empty_layout)
        
        # Add to grid (center it by spanning columns)
        self.grid_layout.addWidget(self.empty_state_widget, 0, 0, 1, 4, Qt.AlignmentFlag.AlignCenter)
        self.empty_state_widget.show()
    
    def hide_empty_state(self):
        """Hide empty state message"""
        if self.empty_state_widget:
            self.empty_state_widget.hide()
            self.grid_layout.removeWidget(self.empty_state_widget)
    
    def add_app(self, app_name, app_path, unlock_count=0, date_added=None, added_at=None, defer_refresh=False):
        """
        Add an application to the grid.
        
        Args:
            app_name: Name of the application
            app_path: Path to the executable
            unlock_count: Number of times unlocked
            date_added: Legacy parameter (use added_at instead)
            added_at: ISO format timestamp when added
            defer_refresh: If True, don't refresh grid immediately (for bulk operations)
        """
        import time
        # Support both date_added and added_at parameter names for compatibility
        timestamp = added_at or date_added or time.time()
        self.apps_data[app_name] = {
            'path': app_path,
            'unlock_count': unlock_count,
            'date_added': timestamp
        }
        
        # Only refresh if not deferred (optimization for bulk adds)
        if not defer_refresh:
            self.refresh_grid()
    
    def batch_add_apps(self, apps_list):
        """
        Efficiently add multiple applications at once.
        
        Args:
            apps_list: List of dicts with 'name', 'path', 'unlock_count', 'added_at'
        """
        import time
        from datetime import datetime
        
        for app in apps_list:
            timestamp = app.get('added_at') or app.get('date_added') or datetime.now().isoformat()
            self.apps_data[app['name']] = {
                'path': app['path'],
                'unlock_count': app.get('unlock_count', 0),
                'date_added': timestamp
            }
        
        # Single refresh at the end (O(n) instead of O(n²))
        self.refresh_grid()
    
    def remove_app(self, app_name, defer_refresh=False):
        """Remove an application from the grid
        
        Args:
            app_name: Name of the application to remove
            defer_refresh: If True, skip grid refresh (for bulk operations)
        """
        if app_name in self.apps_data:
            del self.apps_data[app_name]
            self.selected_apps.discard(app_name)
            
            # Only refresh if not deferred (optimization for bulk removes)
            if not defer_refresh:
                self.refresh_grid()
    
    def refresh_grid(self):
        """Refresh the grid display"""
        # Clear existing widgets
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
        
        self.app_cards.clear()
        
        # Show empty state if no apps
        if not self.apps_data:
            self.show_empty_state()
            return
        else:
            self.hide_empty_state()
        
        if not self.apps_data:
            # Show empty state with icon
            empty_widget = QWidget()
            empty_layout = QVBoxLayout()
            empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.setSpacing(20)
            
            # Icon
            icon_label = QLabel("📦")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setStyleSheet("font-size: 72px;")
            empty_layout.addWidget(icon_label)
            
            # Text
            text_label = QLabel("No Applications Yet")
            text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_label.setStyleSheet("""
                color: #ffffff;
                font-size: 18pt;
                font-weight: bold;
            """)
            empty_layout.addWidget(text_label)
            
            # Instruction
            instruction_label = QLabel("Click '➕ Add Application' to add your first app")
            instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            instruction_label.setStyleSheet("""
                color: #888888;
                font-size: 13pt;
            """)
            empty_layout.addWidget(instruction_label)
            
            empty_widget.setLayout(empty_layout)
            self.grid_layout.addWidget(empty_widget, 0, 0, 1, 3)
        else:
            # Create grid of cards (3 columns)
            columns = 3
            row = 0
            col = 0
            
            for app_name, app_data in self.apps_data.items():
                card = AppCard(
                    app_name,
                    app_data['path'],
                    app_data.get('unlock_count', 0),
                    app_data.get('date_added', None)
                )
                card.clicked.connect(self.on_card_clicked)
                card.double_clicked.connect(self.on_card_double_clicked)
                card.context_menu_requested.connect(self.show_context_menu)
                
                self.grid_layout.addWidget(card, row, col)
                self.app_cards[app_name] = card
                
                # Update selection state
                if app_name in self.selected_apps:
                    card.set_selected(True)
                
                col += 1
                if col >= columns:
                    col = 0
                    row += 1
    
    def on_card_clicked(self, app_name):
        """Handle card click - toggle selection"""
        if app_name in self.selected_apps:
            self.selected_apps.discard(app_name)
            self.app_cards[app_name].set_selected(False)
        else:
            self.selected_apps.add(app_name)
            self.app_cards[app_name].set_selected(True)
    
    def on_card_double_clicked(self, app_name):
        """Handle card double click - could open edit dialog"""
        print(f"Double clicked: {app_name}")
        # Emit signal to parent for edit
        app_data = self.apps_data.get(app_name)
        if app_data:
            self.app_edited.emit(app_name, app_name, app_data['path'])
    
    def show_context_menu(self, app_name, position):
        """Show right-click context menu for an app card"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a1a1a;
                color: #e5e7eb;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #3b82f6;
            }
        """)
        
        # Edit action
        edit_action = menu.addAction("✏️  Edit Application")
        edit_action.triggered.connect(lambda: self.request_edit_app(app_name))
        
        # Remove action
        remove_action = menu.addAction("🗑️  Remove Application")
        remove_action.triggered.connect(lambda: self.request_remove_app(app_name))
        
        menu.addSeparator()
        
        # Open file location
        open_location_action = menu.addAction("📁 Open File Location")
        open_location_action.triggered.connect(lambda: self.open_file_location(app_name))
        
        menu.exec(position)
    
    def request_edit_app(self, app_name):
        """Request to edit application (signal to parent)"""
        app_data = self.apps_data.get(app_name)
        if app_data:
            print(f"[AppGrid] Requesting edit for: {app_name}")
            self.app_edited.emit(app_name, app_name, app_data['path'])
    
    def request_remove_app(self, app_name):
        """Request to remove application (signal to parent)"""
        print(f"[AppGrid] Requesting removal for: {app_name}")
        self.app_removed.emit(app_name)
    
    def open_file_location(self, app_name):
        """Open the file manager at the application's location"""
        app_data = self.apps_data.get(app_name)
        if not app_data:
            return
        
        app_path = app_data['path']
        if not os.path.exists(app_path):
            print(f"File not found: {app_path}")
            return
        
        # Get directory containing the file
        file_dir = os.path.dirname(app_path)
        
        try:
            import platform
            if platform.system() == "Windows":
                # Windows: open folder and select file
                if os.path.isfile(app_path):
                    subprocess.Popen(['explorer', '/select,', app_path])
                else:
                    subprocess.Popen(['explorer', file_dir])
            else:
                # Try xdg-open first (works on most Linux DEs)
                subprocess.Popen(['xdg-open', file_dir])
        except:
            try:
                # Fallback to nautilus (GNOME)
                subprocess.Popen(['nautilus', file_dir])
            except:
                try:
                    # Fallback to dolphin (KDE)
                    subprocess.Popen(['dolphin', file_dir])
                except:
                    print(f"Could not open file manager for: {file_dir}")
    
    def selectAll(self):
        """Select all applications"""
        self.selected_apps = set(self.apps_data.keys())
        for app_name, card in self.app_cards.items():
            card.set_selected(True)
    
    def clearSelection(self):
        """Clear all selections"""
        self.selected_apps.clear()
        for card in self.app_cards.values():
            card.set_selected(False)
    
    def get_selected_apps(self):
        """Get list of selected app names"""
        return list(self.selected_apps)
