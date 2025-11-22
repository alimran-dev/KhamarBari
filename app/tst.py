import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import os

# Set global styles/colors based on the design
BG_COLOR_DARK = "#588157"  # Dark Olive Green (Sidebar background)
BG_COLOR_LIGHT = "#EAEAEA"  # Light Gray (Main dashboard background)
CARD_BG_COLOR = "#FFFFFF" # White card background
TEXT_COLOR_DARK = "#344E41" # Dark text
ACCENT_COLOR = "#A3B18A" # Accent color for hover/active

class DashboardPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.setWindowTitle("KhamarBari Dashboard")
        self.setStyleSheet(f"background-color: {BG_COLOR_LIGHT};")
        
        # Main Layout (HBoxLayout: Sidebar | Main Content)
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self._setup_sidebar()
        self._setup_main_content()
        
        self.main_layout.addWidget(self.sidebar_frame)
        self.main_layout.addWidget(self.content_area)
        
        # Set a reasonable initial size
        self.setMinimumSize(1200, 700) 

    # --- Sidebar Setup ---
    
    def _setup_sidebar(self):
        self.sidebar_frame = QtWidgets.QFrame()
        self.sidebar_frame.setFixedWidth(250)
        self.sidebar_frame.setStyleSheet(f"background-color: {BG_COLOR_DARK};")
        
        self.sidebar_layout = QtWidgets.QVBoxLayout(self.sidebar_frame)
        self.sidebar_layout.setContentsMargins(10, 10, 10, 10)
        
        # 1. Profile Area
        self.profile_widget = QtWidgets.QWidget()
        self.profile_layout = QtWidgets.QVBoxLayout(self.profile_widget)
        self.profile_layout.setAlignment(QtCore.Qt.AlignTop)
        
        self.profile_pic = QtWidgets.QLabel()
        self.profile_pic.setFixedSize(100, 100)
        self.profile_pic.setStyleSheet("""
            QLabel {
                background-color: #B5C9A9;
                border-radius: 50px; 
                border: 2px solid white;
            }
        """)
        self.profile_layout.addWidget(self.profile_pic, alignment=QtCore.Qt.AlignCenter)
        
        self.owner_name = QtWidgets.QLabel("OwnerName")
        self.farm_id = QtWidgets.QLabel("FarmID")
        self.owner_name.setStyleSheet("color: white; font-size: 14pt; font-weight: bold;")
        self.farm_id.setStyleSheet("color: #DDEEDD; font-size: 10pt;")
        
        self.profile_layout.addWidget(self.owner_name, alignment=QtCore.Qt.AlignCenter)
        self.profile_layout.addWidget(self.farm_id, alignment=QtCore.Qt.AlignCenter)
        self.profile_layout.addSpacing(20)
        
        self.sidebar_layout.addWidget(self.profile_widget)
        
        # 2. Menu List (Using QListWidget for easy styling of active item)
        self.main_menu_label = QtWidgets.QLabel("Main Menu")
        self.main_menu_label.setStyleSheet("color: white; font-size: 10pt; padding: 5px 0 5px 15px;")
        self.sidebar_layout.addWidget(self.main_menu_label)
        
        self.menu_list = QtWidgets.QListWidget()
        self.menu_list.setStyleSheet(self._get_menu_style())
        
        menu_items = [
            ("Dashbohard", True), ("Cattle", False), ("Production", False), 
            ("Order", False), ("Warehouse", False), ("Labour", False), 
            ("Expanse/Income", False), ("Veterinary", False), 
            ("Settings", False), ("Support", False)
        ]

        # Use an empty icon placeholder or load actual icons
        placeholder_icon = QtGui.QIcon(QtGui.QPixmap(20, 20))
        
        for text, is_active in menu_items:
            item = QtWidgets.QListWidgetItem(placeholder_icon, text)
            item.setSizeHint(QtCore.QSize(200, 40)) # Set item height
            self.menu_list.addItem(item)
            if is_active:
                item.setSelected(True) # Set Dashboard as active
        
        self.sidebar_layout.addWidget(self.menu_list)
        self.sidebar_layout.addStretch(1) # Push everything to the top

    def _get_menu_style(self):
        """Returns QSS for the QListWidget menu."""
        return f"""
            QListWidget {{
                background-color: {BG_COLOR_DARK};
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                color: white;
                padding: 10px 15px;
                border-radius: 10px;
                margin-bottom: 5px;
            }}
            QListWidget::item:selected {{
                background-color: #7A997A; /* Slightly lighter olive for active state */
                color: {TEXT_COLOR_DARK};
                font-weight: bold;
                border-left: 5px solid #A3B18A;
            }}
            QListWidget::item:hover:!selected {{
                background-color: rgba(255, 255, 255, 50); /* Subtle hover */
            }}
        """

    # --- Main Content Setup ---

    def _setup_main_content(self):
        self.content_area = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(30, 20, 30, 20)
        self.content_layout.setSpacing(20)

        # 1. Header and Date
        self.header_widget = QtWidgets.QWidget()
        self.header_layout = QtWidgets.QVBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.app_name = QtWidgets.QLabel("KhamarBari")
        self.app_name.setStyleSheet(f"color: {TEXT_COLOR_DARK}; font-size: 28pt; font-family: 'Georgia', serif;")
        
        self.greeting = QtWidgets.QLabel("Good Morning, FarmName")
        self.date_label = QtWidgets.QLabel("Today: 27 October 2025")
        self.greeting.setStyleSheet(f"color: {TEXT_COLOR_DARK}; font-size: 20pt; font-weight: bold;")
        self.date_label.setStyleSheet(f"color: gray; font-size: 10pt;")

        self.header_layout.addWidget(self.app_name)
        self.header_layout.addSpacing(10)
        self.header_layout.addWidget(self.greeting)
        self.header_layout.addWidget(self.date_label)
        self.header_layout.addSpacing(15)
        
        self.content_layout.addWidget(self.header_widget)
        
        # 2. Dashboard Grid (The main statistics and charts)
        self.dashboard_grid = QtWidgets.QGridLayout()
        self.dashboard_grid.setSpacing(20)
        
        # Row 1: Key Metrics (Total Animals, Today's Production, Monthly Income)
        self.dashboard_grid.addWidget(self._create_metric_card("Total Animals", "42"), 0, 0)
        self.dashboard_grid.addWidget(self._create_metric_card("Today's Production", "42"), 0, 1)
        self.dashboard_grid.addWidget(self._create_metric_card("Monthly Income", "42"), 0, 2)
        
        # Row 2: Charts (Production Trend, Expense vs. Income)
        self.dashboard_grid.addWidget(self._create_chart_card("Production Trend (Last 7 Days)"), 1, 0, 1, 1)
        self.dashboard_grid.addWidget(self._create_chart_card("Expense vs. Income (Monthly)"), 1, 1, 1, 2)

        # Row 3: Farm Health and Quick Actions
        self.dashboard_grid.addWidget(self._create_health_card("Farm Health: 86%"), 2, 0)
        self.dashboard_grid.addWidget(self._create_quick_actions(), 2, 1, 1, 2)
        
        # Set column stretch factors for better responsiveness
        self.dashboard_grid.setColumnStretch(0, 1)
        self.dashboard_grid.setColumnStretch(1, 1)
        self.dashboard_grid.setColumnStretch(2, 1)

        self.content_layout.addLayout(self.dashboard_grid)
        self.content_layout.addStretch(1) # Push content up

    # --- Helper Widgets ---

    def _create_card_frame(self):
        """Creates a common white, rounded card container."""
        frame = QtWidgets.QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG_COLOR};
                border-radius: 15px;
                padding: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Subtle shadow effect (QSS limitations apply) */
            }}
        """)
        return frame

    def _create_metric_card(self, title, value):
        """Creates the small metric cards (Row 1)."""
        frame = self._create_card_frame()
        frame.setFixedHeight(120)
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        # Title with custom radio-like indicator
        title_label = QtWidgets.QLabel(f"• {title}")
        title_label.setStyleSheet(f"color: gray; font-size: 10pt;")
        
        value_label = QtWidgets.QLabel(value)
        value_label.setStyleSheet(f"color: {TEXT_COLOR_DARK}; font-size: 36pt; font-weight: bold;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch(1)
        
        return frame

    def _create_chart_card(self, title):
        """Creates the larger, placeholder chart cards (Row 2)."""
        frame = self._create_card_frame()
        frame.setMinimumHeight(250)
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(f"color: {TEXT_COLOR_DARK}; font-size: 14pt; font-weight: 500;")
        layout.addWidget(title_label)
        
        # Placeholder for the actual chart (e.g., QChartView if using Qt Charts)
        chart_placeholder = QtWidgets.QLabel("Chart Placeholder Area")
        chart_placeholder.setAlignment(QtCore.Qt.AlignCenter)
        chart_placeholder.setStyleSheet("background-color: #F8F8F8; border: 1px dashed lightgray; min-height: 180px;")
        layout.addWidget(chart_placeholder)
        
        return frame

    def _create_health_card(self, title):
        """Creates the Farm Health card (Row 3, Left)."""
        frame = self._create_card_frame()
        frame.setMinimumHeight(120)
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(f"color: {TEXT_COLOR_DARK}; font-size: 18pt; font-weight: bold;")
        
        subtitle_label = QtWidgets.QLabel("(Based on production and animal condition)")
        subtitle_label.setStyleSheet("color: gray; font-size: 9pt;")
        
        # Placeholder for a progress bar (Farm Health: 86%)
        progress_bar = QtWidgets.QProgressBar()
        progress_bar.setValue(86)
        progress_bar.setTextVisible(False)
        progress_bar.setFixedSize(200, 10)
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border-radius: 5px;
                background-color: #EEEEEE;
            }}
            QProgressBar::chunk {{
                border-radius: 5px;
                background-color: {BG_COLOR_DARK};
            }}
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(progress_bar)
        layout.addWidget(subtitle_label)
        layout.addStretch(1)
        
        return frame

    def _create_quick_actions(self):
        """Creates the Quick Actions panel (Row 3, Right)."""
        frame = self._create_card_frame()
        frame.setMinimumHeight(120)
        
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QtWidgets.QLabel("Quick Action")
        title_label.setStyleSheet(f"color: {TEXT_COLOR_DARK}; font-size: 18pt; font-weight: bold;")
        layout.addWidget(title_label)

        button_row = QtWidgets.QHBoxLayout()
        button_row.setSpacing(10)
        
        # Define buttons and their styles
        def create_action_button(text, bg_color):
            btn = QtWidgets.QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: white;
                    font-size: 11pt;
                    padding: 8px 15px;
                    border-radius: 18px;
                    border: none;
                }}
                QPushButton:hover {{
                    opacity: 0.9;
                    background-color: {ACCENT_COLOR}; 
                }}
            """)
            btn.setMinimumWidth(100)
            return btn

        # Buttons in two groups based on the design image
        
        # Group 1: Income/Expense
        button_row_top = QtWidgets.QHBoxLayout()
        button_row_top.addWidget(create_action_button("+ Income/Expense", "#C28B78")) # Using a reddish/brown accent
        button_row_top.addStretch(1)

        # Group 2: Add Feed, Cattle, Order
        button_row_bottom = QtWidgets.QHBoxLayout()
        button_row_bottom.addWidget(create_action_button("+ Add Feed", BG_COLOR_DARK))
        button_row_bottom.addWidget(create_action_button("+ Add Cattle", BG_COLOR_DARK))
        button_row_bottom.addWidget(create_action_button("+ Add Order", BG_COLOR_DARK))
        button_row_bottom.addStretch(1)

        layout.addLayout(button_row_top)
        layout.addLayout(button_row_bottom)
        
        return frame


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    # Optional: Load a custom font if 'Aladin' or 'Amaranth' is required, 
    # otherwise Qt will use system defaults.
    # E.g., QtGui.QFontDatabase.addApplicationFont("/path/to/font.ttf")

    dashboard = DashboardPage()
    dashboard.show()
    sys.exit(app.exec_())