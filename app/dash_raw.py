import sys
from PyQt5 import QtCore, QtGui, QtWidgets

# --- Color Scheme from the Design ---
BG_COLOR_DARK = "#588157"  # Sidebar Dark Olive Green
BG_COLOR_HEADER = "#588157" # Header background (matching sidebar)
BG_COLOR_LIGHT = "#EBEAE3"  # Main Content Area Light Tan/Grey
TEXT_COLOR_DARK = "#344E41" # Dark text for contrast

class DashboardMinimal(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KhamarBari Dashboard")
        self.setStyleSheet(f"background-color: {BG_COLOR_LIGHT};")
        
        # Main Layout (Horizontal: Sidebar | Content)
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self._setup_sidebar()
        self.main_layout.addWidget(self.sidebar_frame)
        
        self._setup_main_content_frame()
        self.main_layout.addWidget(self.content_frame)
        
        self.setMinimumSize(1000, 600) 

    # --- 1. Sidebar Setup ---
    def _setup_sidebar(self):
        self.sidebar_frame = QtWidgets.QFrame()
        self.sidebar_frame.setFixedWidth(250)
        self.sidebar_frame.setStyleSheet(f"background-color: {BG_COLOR_DARK};")
        
        self.sidebar_layout = QtWidgets.QVBoxLayout(self.sidebar_frame)
        self.sidebar_layout.setContentsMargins(10, 20, 10, 10)
        
        # 1. Profile Area
        self.profile_pic = QtWidgets.QLabel()
        self.profile_pic.setFixedSize(120, 120)
        self.profile_pic.setStyleSheet("""
            QLabel {
                background-color: #D3D3D3; /* Light grey placeholder color */
                border-radius: 60px; 
            }
        """)
        
        self.user_id = QtWidgets.QLabel("UserID")
        self.user_id.setAlignment(QtCore.Qt.AlignCenter)
        self.user_id.setStyleSheet("color: white; font-size: 16pt; font-weight: bold; margin-top: 10px;")

        self.sidebar_layout.addWidget(self.profile_pic, alignment=QtCore.Qt.AlignCenter)
        self.sidebar_layout.addWidget(self.user_id)
        self.sidebar_layout.addSpacing(30)
        
        # 2. Menu List
        self.main_menu_label = QtWidgets.QLabel("Main Menu")
        self.main_menu_label.setStyleSheet("color: white; font-size: 10pt; padding: 5px 0 5px 15px; font-weight: 500;")
        self.sidebar_layout.addWidget(self.main_menu_label)
        
        self.menu_list = QtWidgets.QListWidget()
        self.menu_list.setStyleSheet(self._get_menu_style())
        
        # Menu Items (using placeholder QIcons)
        menu_items = [
            ("Dashbohard", True), ("Cattle", False), ("Production", False), 
            ("Order", False), ("Warehouse", False), ("Labour", False), 
            ("Expanse/Income", False), ("Veterinary", False), 
            ("Settings", False), ("Support", False)
        ]
        
        # Create a generic icon for demonstration (QGrid/Square icon)
        icon_size = QtCore.QSize(20, 20)
        grid_icon = QtGui.QIcon()
        # FIX: Ensure _create_grid_pixmap returns a pixmap that is used correctly
        grid_icon.addPixmap(self._create_grid_pixmap(icon_size), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        
        for text, is_active in menu_items:
            item = QtWidgets.QListWidgetItem(grid_icon, text)
            item.setSizeHint(QtCore.QSize(200, 40)) 
            self.menu_list.addItem(item)
            if is_active:
                # Set Dashboard as active and visually selected
                item.setSelected(True) 
        
        self.sidebar_layout.addWidget(self.menu_list)
        self.sidebar_layout.addStretch(1) # Push content up

    def _create_grid_pixmap(self, size):
        """Creates a simple 4-square grid pixmap for the menu icons."""
        pixmap = QtGui.QPixmap(size)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setBrush(QtGui.QBrush(QtCore.Qt.white))
        
        # FIX: Ensure w and h are integers (int() type-cast to fix TypeError)
        w = int(size.width() / 2.5) 
        h = int(size.height() / 2.5)
        
        # Draw 4 small white squares (like the dashboard icon)
        painter.drawRect(0, 0, w, h)
        painter.drawRect(size.width() - w, 0, w, h)
        painter.drawRect(0, size.height() - h, w, h)
        painter.drawRect(size.width() - w, size.height() - h, w, h)
        
        painter.end()
        return pixmap

    def _get_menu_style(self):
        """Returns QSS for the QListWidget menu to achieve the selection styling."""
        return f"""
            QListWidget {{
                background-color: {BG_COLOR_DARK};
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                color: white;
                padding: 10px 15px;
                border-radius: 5px;
                margin-bottom: 5px;
            }}
            QListWidget::item:selected {{
                background-color: {BG_COLOR_LIGHT}; /* Active item takes content BG color */
                color: {TEXT_COLOR_DARK}; /* Active item text color */
                font-weight: 600;
            }}
            QListWidget::item:hover:!selected {{
                background-color: rgba(255, 255, 255, 30); /* Subtle hover */
            }}
        """

    # --- 2. Main Content Setup ---
    def _setup_main_content_frame(self):
        self.content_frame = QtWidgets.QFrame()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # 2a. Header Area
        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setFixedHeight(80) 
        self.header_widget.setStyleSheet(f"background-color: {BG_COLOR_HEADER};")
        
        self.header_layout = QtWidgets.QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(30, 0, 30, 0)
        
        # Branding
        self.app_name = QtWidgets.QLabel("KhamarBari")
        # Using a generic serif font to mimic the custom font shown
        self.app_name.setStyleSheet(f"color: white; font-size: 28pt; font-family: 'Georgia', serif;")
        self.header_layout.addWidget(self.app_name)
        
        self.header_layout.addStretch(1)
        
        # Action Icons (Top Right Circles)
        self._add_header_action_circles(self.header_layout)

        self.content_layout.addWidget(self.header_widget)
        
        # 2b. Main Body Area (The large empty space)
        self.main_body = QtWidgets.QWidget()
        self.main_body.setStyleSheet(f"background-color: {BG_COLOR_LIGHT};")
        
        # Placeholder for main content layout
        body_layout = QtWidgets.QVBoxLayout(self.main_body)
        info_label = QtWidgets.QLabel("Dashboard Content Area (Ready to be populated)")
        info_label.setStyleSheet("color: gray; font-size: 14pt; padding: 20px;")
        body_layout.addWidget(info_label, alignment=QtCore.Qt.AlignCenter)
        
        self.content_layout.addWidget(self.main_body)

    def _add_header_action_circles(self, layout):
        """Adds the two circular placeholders to the top right of the header."""
        for _ in range(2):
            circle = QtWidgets.QLabel()
            circle.setFixedSize(35, 35)
            # Placeholder color matching the profile area
            circle.setStyleSheet("background-color: #D3D3D3; border-radius: 17px;") 
            layout.addWidget(circle)
            layout.addSpacing(10)


if __name__ == '__main__':
    # Ensure High DPI Scaling is handled correctly on modern displays
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QtWidgets.QApplication(sys.argv)

    dashboard = DashboardMinimal()
    dashboard.show()
    sys.exit(app.exec_())