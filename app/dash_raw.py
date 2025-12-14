import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from cattle_page import CattlePage
from production_page import ProductionPage
from order_page import OrderPage
from warehouse_page import WarehousePage
from labour_page import LabourPage
from settings_page import SettingsPage
from finance_page import FinancePage
from veterinary_page import VeterinaryPage
from calendar_page import CalendarPage
from notification_widget import NotificationWidget
from support_page import SupportPage
from dashboard_home import DashboardHome

# --- Color Scheme from the Design ---
BG_COLOR_DARK = "#588157"  # Sidebar Dark Olive Green
BG_COLOR_HEADER = "#588157" # Header background (matching sidebar)
BG_COLOR_LIGHT = "#EBEAE3"  # Main Content Area Light Tan/Grey
TEXT_COLOR_DARK = "#344E41" # Dark text for contrast

class DashboardPage(QtWidgets.QWidget):
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
        
        self.setMinimumSize(800, 500) 

    def load_user_data(self, user_info):
        """Loads user data into the dashboard."""
        data = user_info.get("data", {})
        owner_name = data.get("owner_name", "User")
        farm_name = data.get("farm_name", "Farm")
        self.user_email = data.get("email", "")
        self.user_id.setText(owner_name)
        self.farm_id_label.setText(farm_name)
        
        # Set default profile picture
        self.set_default_profile_pic()
        
        # Load user data into settings page
        self.settings_page.load_user_data(user_info)
        
        # Set user email for cattle page
        if hasattr(self, 'cattle_page'):
            self.cattle_page.set_user_email(self.user_email)
        
        # Initialize finance page with user email
        self.finance_page = FinancePage(self.user_email)
        
        # Add finance page to stack
        self.pages_stack.addWidget(self.finance_page)
        
        # Initialize dashboard home with user data
        self.dashboard_home = DashboardHome(self.user_email, farm_name)
        
        # Connect Quick Action Signals
        self.dashboard_home.action_income_expense.connect(self.go_to_income_expense)
        self.dashboard_home.action_add_feed.connect(self.go_to_add_feed)
        self.dashboard_home.action_add_cattle.connect(self.go_to_add_cattle)
        self.dashboard_home.action_add_order.connect(self.go_to_add_order)
        
        # Replace the placeholder dashboard with the real one
        old_dashboard = self.pages_stack.widget(0)
        self.pages_stack.removeWidget(old_dashboard)
        self.pages_stack.insertWidget(0, self.dashboard_home)
        self.pages_stack.setCurrentWidget(self.dashboard_home)
    
    def go_to_income_expense(self):
        """Navigate to Finance page and open entry tab."""
        self.pages_stack.setCurrentWidget(self.finance_page)
        self.finance_page.switch_to_entry_tab()
        self._update_sidebar_selection("Finance")

    def go_to_add_feed(self):
        """Navigate to Warehouse page and open add dialog."""
        self.pages_stack.setCurrentWidget(self.warehouse_page)
        self.warehouse_page.switch_to_manage_tab_and_open_add_dialog()
        self._update_sidebar_selection("Warehouse")

    def go_to_add_cattle(self):
        """Navigate to Cattle page and open add tab."""
        self.pages_stack.setCurrentWidget(self.cattle_page)
        self.cattle_page.switch_to_add_tab()
        self._update_sidebar_selection("Cattle")

    def go_to_add_order(self):
        """Navigate to Order page and open place order tab."""
        self.pages_stack.setCurrentWidget(self.order_page)
        self.order_page.switch_to_place_order_tab()
        self._update_sidebar_selection("Order")
        
    def _update_sidebar_selection(self, page_name):
        """Update the selected item in the sidebar."""
        for i in range(self.menu_list.count()):
            item = self.menu_list.item(i)
            if item.text() == page_name:
                self.menu_list.setCurrentItem(item)
                break

    def set_default_profile_pic(self):
        """Set default profile picture in sidebar."""
        pixmap = QtGui.QPixmap(120, 120)
        pixmap.fill(QtCore.Qt.transparent)
        
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw circle background
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#D3D3D3")))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(0, 0, 120, 120)
        
        # Draw person icon
        painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 3))
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#FFFFFF")))
        
        # Head
        painter.drawEllipse(44, 28, 32, 32)
        
        # Body
        path = QtGui.QPainterPath()
        path.moveTo(60, 60)
        path.arcTo(32, 60, 56, 56, 0, 180)
        painter.drawPath(path)
        
        painter.end()
        
        self.profile_pic.setPixmap(pixmap)
        self.profile_pic.setScaledContents(False)
    
    def update_profile_pic(self, file_path):
        """Update sidebar profile picture from file."""
        pixmap = QtGui.QPixmap(file_path)
        if not pixmap.isNull():
            # Scale and crop to circular
            scaled = pixmap.scaled(
                120, 120,
                QtCore.Qt.KeepAspectRatioByExpanding,
                QtCore.Qt.SmoothTransformation
            )
            
            # Create circular mask
            target = QtGui.QPixmap(120, 120)
            target.fill(QtCore.Qt.transparent)
            
            painter = QtGui.QPainter(target)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            
            path = QtGui.QPainterPath()
            path.addEllipse(0, 0, 120, 120)
            painter.setClipPath(path)
            
            # Center the image
            x = (120 - scaled.width()) // 2
            y = (120 - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            painter.end()
            
            self.profile_pic.setPixmap(target)

    # --- 1. Sidebar Setup ---
    def _setup_sidebar(self):
        self.sidebar_frame = QtWidgets.QFrame()
        self.sidebar_frame.setFixedWidth(250)
        self.sidebar_frame.setStyleSheet(f"background-color: {BG_COLOR_DARK};")
        
        self.sidebar_layout = QtWidgets.QVBoxLayout(self.sidebar_frame)
        self.sidebar_layout.setContentsMargins(10, 20, 10, 10)
        
        # 1. Profile Area (Fixed)
        self.profile_pic = QtWidgets.QLabel()
        self.profile_pic.setFixedSize(120, 120)
        self.profile_pic.setStyleSheet("""
            QLabel {
                background-color: #D3D3D3; /* Light grey placeholder color */
                border-radius: 60px; 
            }
        """)
        
        self.user_id = QtWidgets.QLabel("OwnerName")
        self.user_id.setAlignment(QtCore.Qt.AlignCenter)
        self.user_id.setStyleSheet("color: white; font-size: 16pt; font-weight: bold; margin-top: 10px;")
        
        self.farm_id_label = QtWidgets.QLabel("FarmID")
        self.farm_id_label.setAlignment(QtCore.Qt.AlignCenter)
        self.farm_id_label.setStyleSheet("color: white; font-size: 10pt; margin-top: 5px;")

        self.sidebar_layout.addWidget(self.profile_pic, alignment=QtCore.Qt.AlignCenter)
        self.sidebar_layout.addWidget(self.user_id)
        self.sidebar_layout.addWidget(self.farm_id_label)
        self.sidebar_layout.addSpacing(30)
        
        # 2. Menu List (Scrollable)
        self.main_menu_label = QtWidgets.QLabel("Main Menu")
        self.main_menu_label.setStyleSheet("color: white; font-size: 10pt; padding: 5px 0 5px 15px; font-weight: 500;")
        self.sidebar_layout.addWidget(self.main_menu_label)
        
        self.menu_list = QtWidgets.QListWidget()
        # Apply scrollbar styling to the list widget
        self.menu_list.setStyleSheet(self._get_menu_style() + f"""
            QScrollBar:vertical {{
                background: {BG_COLOR_DARK};
                width: 8px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background-color: #344E41;
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        self.menu_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.menu_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        # Menu Items with icons
        menu_items = [
            ("Dashboard", "dashboard.png", True), 
            ("Cattle", "cattles.png", False), 
            ("Production", "barn.png", False), 
            ("Order", "shopping-cart.png", False), 
            ("Warehouse", "warehouse.png", False), 
            ("Labour", "worker.png", False), 
            ("Finance", "budget.png", False), 
            ("Veterinary", "veterinarian.png", False), 
            ("Settings", "settings.png", False), 
            ("Support", None, False)
        ]
        
        # Icon base path
        # Use absolute path relative to this file to ensure icons load correctly regardless of CWD
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_base_path = os.path.join(base_dir, "../backend/uploads/sidebar_icons/")
        icon_size = QtCore.QSize(20, 20)
        
        for item_data in menu_items:
            text = item_data[0]
            icon_file = item_data[1]
            is_active = item_data[2]
            
            # Load icon if available, otherwise use grid icon
            if icon_file:
                icon_path = icon_base_path + icon_file
                icon = QtGui.QIcon(icon_path)
            else:
                # Create a generic icon for items without a specific icon
                icon = QtGui.QIcon()
                icon.addPixmap(self._create_grid_pixmap(icon_size), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            
            item = QtWidgets.QListWidgetItem(icon, text)
            item.setSizeHint(QtCore.QSize(200, 40)) 
            self.menu_list.addItem(item)
            if is_active:
                # Set Dashboard as active and visually selected
                item.setSelected(True)
        
        self.sidebar_layout.addWidget(self.menu_list)
        
        self.menu_list.itemClicked.connect(self.on_menu_click)

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
                background-color: #344E41; /* Darker green for active item */
                color: white; /* White text */
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
        
        # Stacked Widget for pages
        self.pages_stack = QtWidgets.QStackedWidget(self.main_body)
        
        # Dashboard Home (Placeholder - will be replaced with real dashboard after login)
        dashboard_placeholder = QtWidgets.QLabel("Dashboard Content Area (Ready to be populated)")
        dashboard_placeholder.setAlignment(QtCore.Qt.AlignCenter)
        dashboard_placeholder.setStyleSheet("color: gray; font-size: 14pt; padding: 20px;")
        
        # Cattle Page
        self.cattle_page = CattlePage()
        
        # Production Page
        self.production_page = ProductionPage()
        
        # Order Page
        self.order_page = OrderPage()
        
        # Warehouse Page
        self.warehouse_page = WarehousePage()
        
        # Labour Page
        self.labour_page = LabourPage()
        
        # Veterinary Page
        self.veterinary_page = VeterinaryPage()
        
        # Calendar Page
        self.calendar_page = CalendarPage()
        
        # Settings Page
        self.settings_page = SettingsPage(self)
        
        # Support Page
        self.support_page = SupportPage()
        
        self.pages_stack.addWidget(dashboard_placeholder)
        self.pages_stack.addWidget(self.cattle_page)
        self.pages_stack.addWidget(self.production_page)
        self.pages_stack.addWidget(self.order_page)
        self.pages_stack.addWidget(self.warehouse_page)
        self.pages_stack.addWidget(self.labour_page)
        self.pages_stack.addWidget(self.veterinary_page)
        self.pages_stack.addWidget(self.calendar_page)
        self.pages_stack.addWidget(self.settings_page)
        self.pages_stack.addWidget(self.support_page)
        
        body_layout = QtWidgets.QVBoxLayout(self.main_body)
        body_layout.addWidget(self.pages_stack)
        
        self.content_layout.addWidget(self.main_body)

    def on_menu_click(self, item):
        text = item.text()
        if text == "Dashboard":
            self.pages_stack.setCurrentWidget(self.dashboard_home)
        elif text == "Cattle":
            self.pages_stack.setCurrentWidget(self.cattle_page)
        elif text == "Production":
            self.pages_stack.setCurrentWidget(self.production_page)
        elif text == "Order":
            self.pages_stack.setCurrentWidget(self.order_page)
        elif text == "Warehouse":
            self.pages_stack.setCurrentWidget(self.warehouse_page)
        elif text == "Labour":
            self.pages_stack.setCurrentWidget(self.labour_page)
        elif text == "Finance":
            self.pages_stack.setCurrentWidget(self.finance_page)
        elif text == "Veterinary":
            self.pages_stack.setCurrentWidget(self.veterinary_page)
        elif text == "Settings":
            self.pages_stack.setCurrentWidget(self.settings_page)
        elif text == "Support":
            self.pages_stack.setCurrentWidget(self.support_page)

    def _add_header_action_circles(self, layout):
        """Adds the action buttons to the top right of the header."""
        # Calendar button
        self.calendar_btn = QtWidgets.QPushButton()
        self.calendar_btn.setFixedSize(40, 40)
        self.calendar_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.calendar_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border-radius: 20px;
                font-size: 16pt;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        self.calendar_btn.setText("📅")
        self.calendar_btn.setToolTip("Open Calendar")
        self.calendar_btn.clicked.connect(self.open_calendar)
        layout.addWidget(self.calendar_btn)
        layout.addSpacing(10)
        
        # Notification button
        self.notification_btn = QtWidgets.QPushButton()
        self.notification_btn.setFixedSize(40, 40)
        self.notification_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.notification_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border-radius: 20px;
                font-size: 16pt;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        self.notification_btn.setText("🔔")
        self.notification_btn.setToolTip("Notifications")
        self.notification_btn.clicked.connect(self.show_notifications)
        layout.addWidget(self.notification_btn)
        layout.addSpacing(10)
        
        # Create notification widget (hidden initially)
        self.notification_widget = NotificationWidget(self)
    
    def open_calendar(self):
        """Open the calendar page"""
        self.pages_stack.setCurrentWidget(self.calendar_page)
    
    def show_notifications(self):
        """Show the notification dropdown"""
        # Position the notification widget below the button
        button_pos = self.notification_btn.mapToGlobal(QtCore.QPoint(0, 0))
        widget_x = button_pos.x() - self.notification_widget.width() + self.notification_btn.width()
        widget_y = button_pos.y() + self.notification_btn.height() + 5
        
        self.notification_widget.move(widget_x, widget_y)
        self.notification_widget.show()
        self.notification_widget.raise_()


if __name__ == '__main__':
    # Ensure High DPI Scaling is handled correctly on modern displays
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QtWidgets.QApplication(sys.argv)

    dashboard = DashboardPage()
    dashboard.show()
    sys.exit(app.exec_())