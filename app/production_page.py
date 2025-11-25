from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import datetime
import requests

class CustomDateRangeDialog(QtWidgets.QDialog):
    """Dialog for selecting custom date range."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Date Range")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QtWidgets.QLabel("Select Custom Date Range")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #344E41;")
        layout.addWidget(title)
        
        # Date inputs
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(10)
        
        # Start date
        self.start_date_edit = QtWidgets.QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QtCore.QDate.currentDate().addMonths(-1))
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 1px solid #A3B18A;
                border-radius: 5px;
                background-color: white;
                font-size: 10pt;
            }
        """)
        form_layout.addRow("Start Date:", self.start_date_edit)
        
        # End date
        self.end_date_edit = QtWidgets.QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QtCore.QDate.currentDate())
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 1px solid #A3B18A;
                border-radius: 5px;
                background-color: white;
                font-size: 10pt;
            }
        """)
        form_layout.addRow("End Date:", self.end_date_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setFixedHeight(35)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #ccc;
                color: #333;
                border: none;
                border-radius: 5px;
                padding: 0 20px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #bbb;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        apply_btn = QtWidgets.QPushButton("Apply")
        apply_btn.setFixedHeight(35)
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #344E41;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 0 20px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #588157;
            }
        """)
        apply_btn.clicked.connect(self._apply_dates)
        button_layout.addWidget(apply_btn)
        
        layout.addLayout(button_layout)
        
        self.start_date = None
        self.end_date = None
    
    def _apply_dates(self):
        """Validate and apply selected dates."""
        start = self.start_date_edit.date().toPyDate()
        end = self.end_date_edit.date().toPyDate()
        
        if start > end:
            QtWidgets.QMessageBox.warning(self, "Invalid Range", "Start date must be before or equal to end date.")
            return
        
        self.start_date = start
        self.end_date = end
        self.accept()

# --- Color Scheme (Matching Cattle Page) ---
BG_COLOR_LIGHT = "#EBEAE3"
BG_COLOR_DARK = "#588157"
TEXT_COLOR_DARK = "#344E41"
INPUT_BG = "#D8E2D1"
INPUT_BORDER = "#A3B18A"
CARD_BORDER = "#B5C9A9"
TABLE_HEADER_BG = "#344E41"

SCROLLBAR_STYLESHEET = """
    QScrollBar:vertical {
        background: transparent;
        width: 8px;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background-color: #344E41;
        min-height: 20px;
        border-radius: 4px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
"""

class ProductionPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"QWidget {{ background-color: {BG_COLOR_LIGHT}; }}")
        
        # Main Layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(30, 20, 30, 30)
        self.layout.setSpacing(15)
        
        # Store for recent entries
        self.recent_entries = []
        self.archived_entries = []
        
        # Filter period
        self.current_filter = "Today"
        self.custom_start_date = None
        self.custom_end_date = None
        
        # --- 1. Custom Tab Bar ---
        self.tab_container = QtWidgets.QWidget()
        self.tab_layout = QtWidgets.QHBoxLayout(self.tab_container)
        self.tab_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_layout.setSpacing(0)
        self.tab_layout.setAlignment(QtCore.Qt.AlignHCenter)
        
        # Tab Buttons
        self.btn_overview = self._create_tab_button("Overview", position="left")
        self.btn_manage = self._create_tab_button("Manage", position="right")
        
        self.tabs = [self.btn_overview, self.btn_manage]
        
        for btn in self.tabs:
            self.tab_layout.addWidget(btn)
            btn.clicked.connect(self._handle_tab_click)
        
        self.layout.addWidget(self.tab_container)
        
        # --- 2. Content Stack ---
        self.stack = QtWidgets.QStackedWidget()
        self.layout.addWidget(self.stack)
        
        # Overview Tab
        self.overview_tab = self._create_overview_tab()
        self.stack.addWidget(self.overview_tab)
        
        # Manage Tab
        self.manage_tab = self._create_manage_tab()
        self.stack.addWidget(self.manage_tab)
        
        # Set initial state
        self._update_tab_styles(self.btn_overview)
        
        # Load initial data from backend
        self._load_initial_data()
    
    def _create_tab_button(self, text, position="center"):
        btn = QtWidgets.QPushButton(text)
        btn.setFixedSize(150, 50)
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        btn.setProperty("tab_pos", position)
        return btn
    
    def _handle_tab_click(self):
        sender = self.sender()
        self._update_tab_styles(sender)
        
        if sender == self.btn_overview:
            self.stack.setCurrentIndex(0)
            self._refresh_overview()
        elif sender == self.btn_manage:
            self.stack.setCurrentIndex(1)
    
    def _update_tab_styles(self, active_btn):
        base_style = """
            QPushButton {
                font-size: 14pt;
                font-weight: bold;
                border: 2px solid #344E41;
                border-radius: 0px;
                background-color: transparent;
                color: #344E41;
            }
        """
        
        active_style = """
            QPushButton {
                font-size: 14pt;
                font-weight: bold;
                border: 2px solid #344E41;
                border-radius: 0px;
                background-color: #344E41;
                color: white;
            }
        """
        
        for btn in self.tabs:
            pos = btn.property("tab_pos")
            style = active_style if btn == active_btn else base_style
            
            # Add position-specific border radius
            if pos == "left":
                style += "border-top-left-radius: 10px; border-bottom-left-radius: 10px;"
            elif pos == "right":
                style += "border-top-right-radius: 10px; border-bottom-right-radius: 10px;"
            
            btn.setStyleSheet(style)
    
    def _create_shadow_effect(self, blur_radius=20, offset_y=4):
        """Creates a shadow effect for modern card design."""
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur_radius)
        shadow.setColor(QtGui.QColor(0, 0, 0, 30))
        shadow.setOffset(0, offset_y)
        return shadow
    
    def _create_overview_tab(self):
        """Creates the Overview tab content."""
        # Scroll area for overview
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll_area.setStyleSheet(f"QScrollArea {{ background-color: {BG_COLOR_LIGHT}; border: none; }}" + SCROLLBAR_STYLESHEET)
        
        overview_widget = QtWidgets.QWidget()
        overview_widget.setStyleSheet(f"QWidget {{ background-color: {BG_COLOR_LIGHT}; }}")
        overview_layout = QtWidgets.QVBoxLayout(overview_widget)
        overview_layout.setContentsMargins(20, 20, 20, 20)
        overview_layout.setSpacing(20)
        
        # Header with Title and Filter Buttons
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Title
        title = QtWidgets.QLabel("Production Overview")
        title.setStyleSheet(f"""
            color: {TEXT_COLOR_DARK};
            font-size: 18pt;
            font-weight: bold;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Filter Buttons
        self.filter_buttons = []
        filter_options = ["Today", "This Week", "This Month", "Custom"]
        
        for option in filter_options:
            btn = QtWidgets.QPushButton(option)
            btn.setFixedHeight(35)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            btn.clicked.connect(lambda checked, opt=option: self._handle_filter_change(opt))
            self.filter_buttons.append(btn)
            header_layout.addWidget(btn)
        
        # Add Production Entry Button
        add_btn = QtWidgets.QPushButton("+ Add Production Entry")
        add_btn.setFixedHeight(35)
        add_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {TEXT_COLOR_DARK};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 20px;
                font-size: 10pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {BG_COLOR_DARK};
            }}
        """)
        add_btn.clicked.connect(lambda: self._handle_tab_click_by_name("Manage"))
        header_layout.addWidget(add_btn)
        
        overview_layout.addLayout(header_layout)
        
        # Update filter button styles
        self._update_filter_styles()
        
        # Summary Cards Layout
        cards_layout = QtWidgets.QHBoxLayout()
        cards_layout.setSpacing(15)
        
        # Milk Production Card
        self.milk_value_label = QtWidgets.QLabel("320 L")
        self.milk_value_label.setStyleSheet(f"""
            color: {TEXT_COLOR_DARK};
            font-size: 32pt;
            font-weight: bold;
        """)
        self.milk_subtitle_label = QtWidgets.QLabel("+5% vs. yesterday")
        milk_card = self._create_summary_card(
            "Milk Production Today (Liters)",
            self.milk_value_label,
            self.milk_subtitle_label,
            "milk_icon.png"
        )
        cards_layout.addWidget(milk_card)
        
        # Eggs Card
        self.eggs_value_label = QtWidgets.QLabel("850 Units")
        self.eggs_value_label.setStyleSheet(f"""
            color: {TEXT_COLOR_DARK};
            font-size: 32pt;
            font-weight: bold;
        """)
        self.eggs_subtitle_label = QtWidgets.QLabel("+8% vs. yesterday")
        eggs_card = self._create_summary_card(
            "Egg Count Today",
            self.eggs_value_label,
            self.eggs_subtitle_label,
            "egg_icon.png"
        )
        cards_layout.addWidget(eggs_card)
        
        # Wool Card
        self.wool_value_label = QtWidgets.QLabel("150 kg")
        self.wool_value_label.setStyleSheet(f"""
            color: {TEXT_COLOR_DARK};
            font-size: 32pt;
            font-weight: bold;
        """)
        self.wool_subtitle_label = QtWidgets.QLabel("+10% vs. last month")
        wool_card = self._create_summary_card(
            "Wool Collected (This Month)",
            self.wool_value_label,
            self.wool_subtitle_label,
            "wool_icon.png"
        )
        cards_layout.addWidget(wool_card)
        
        # Total Weekly Production Card
        self.weekly_value_label = QtWidgets.QLabel("4,500 Units")
        self.weekly_value_label.setStyleSheet(f"""
            color: {TEXT_COLOR_DARK};
            font-size: 32pt;
            font-weight: bold;
        """)
        self.weekly_subtitle_label = QtWidgets.QLabel("+5% vs. last week")
        weekly_card = self._create_summary_card(
            "Total Weekly Production",
            self.weekly_value_label,
            self.weekly_subtitle_label,
            "chart_icon.png"
        )
        cards_layout.addWidget(weekly_card)
        
        overview_layout.addLayout(cards_layout)
        
        # Production History Section
        history_header = QtWidgets.QHBoxLayout()
        history_label = QtWidgets.QLabel("Production History")
        history_label.setStyleSheet(f"""
            color: {TEXT_COLOR_DARK};
            font-size: 16pt;
            font-weight: bold;
            margin-top: 10px;
        """)
        history_header.addWidget(history_label)
        history_header.addStretch()
        overview_layout.addLayout(history_header)
        
        # Production History Table
        self.history_table = QtWidgets.QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Date", "Time", "Animal ID", "Product Type", "Quantity"])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.history_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                border: 1px solid {INPUT_BORDER};
                border-radius: 8px;
                gridline-color: {INPUT_BORDER};
            }}
            QTableWidget::item {{
                padding: 10px;
            }}
            QTableWidget::item:selected {{
                background-color: rgba(163, 177, 138, 0.3);
                color: {TEXT_COLOR_DARK};
            }}
            QTableWidget::item:alternate {{
                background-color: #F5F5F5;
            }}
            QHeaderView::section {{
                background-color: {TABLE_HEADER_BG};
                color: white;
                padding: 10px;
                font-weight: bold;
                font-size: 10pt;
                border: none;
            }}
        """ + SCROLLBAR_STYLESHEET)
        
        overview_layout.addWidget(self.history_table)
        
        scroll_area.setWidget(overview_widget)
        return scroll_area
    
    def _create_summary_card(self, title, value_widget, subtitle_widget, icon_name=""):
        """Creates a summary card widget."""
        card = QtWidgets.QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 12px;
                padding: 20px;
            }}
            QFrame:hover {{
                border: 1px solid {INPUT_BORDER};
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            }}
        """)
        card.setMinimumHeight(140)
        
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setSpacing(8)
        card_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header with icon and title
        header_layout = QtWidgets.QHBoxLayout()
        
        # Icon placeholder (emoji or text)
        icon_label = QtWidgets.QLabel()
        if "Milk" in title:
            icon_label.setText("🥛")
        elif "Egg" in title:
            icon_label.setText("🥚")
        elif "Wool" in title:
            icon_label.setText("🧶")
        elif "Total" in title or "Weekly" in title:
            icon_label.setText("📊")
        else:
            icon_label.setText("📦")
        icon_label.setStyleSheet("font-size: 24pt;")
        header_layout.addWidget(icon_label)
        header_layout.addStretch()
        
        card_layout.addLayout(header_layout)
        
        # Title
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(f"""
            color: #666;
            font-size: 9pt;
            font-weight: normal;
        """)
        title_label.setWordWrap(True)
        card_layout.addWidget(title_label)
        
        # Value
        card_layout.addWidget(value_widget)
        
        # Subtitle with comparison
        subtitle_widget.setStyleSheet(f"""
            color: #28a745;
            font-size: 9pt;
            font-weight: normal;
        """)
        card_layout.addWidget(subtitle_widget)
        
        card_layout.addStretch()
        
        return card
    
    def _create_manage_tab(self):
        """Creates the Manage tab content with the Daily Production Entry Form."""
        manage_widget = QtWidgets.QWidget()
        
        # Create scroll area for the form
        scroll_area = QtWidgets.QScrollArea(manage_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll_area.setStyleSheet(f"QScrollArea {{ background-color: {BG_COLOR_LIGHT}; border: none; }}" + SCROLLBAR_STYLESHEET)
        
        # Content widget inside scroll area
        content_widget = QtWidgets.QWidget()
        manage_layout = QtWidgets.QVBoxLayout(content_widget)
        manage_layout.setContentsMargins(20, 20, 20, 20)
        manage_layout.setSpacing(20)
        
        # Title
        title_layout = QtWidgets.QHBoxLayout()
        icon_label = QtWidgets.QLabel("+")
        icon_label.setStyleSheet(f"font-size: 24pt; font-weight: 900; color: {TEXT_COLOR_DARK};")
        title_label = QtWidgets.QLabel("Add Production Entry")
        title_label.setStyleSheet(f"font-size: 18pt; font-weight: bold; color: {TEXT_COLOR_DARK};")
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        manage_layout.addLayout(title_layout)
        manage_layout.addSpacing(5)
        
        title = QtWidgets.QLabel()  # Dummy for compatibility
        title.hide()
        manage_layout.addWidget(title)
        
        # Daily Production Entry Form (Full Width)
        form_card = self._create_production_form()
        manage_layout.addWidget(form_card)
        manage_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        
        # Main layout for manage widget
        main_manage_layout = QtWidgets.QVBoxLayout(manage_widget)
        main_manage_layout.setContentsMargins(0, 0, 0, 0)
        main_manage_layout.addWidget(scroll_area)
        
        return manage_widget
    
    def _create_production_form(self):
        """Creates the Daily Production Entry Form card."""
        form_card = QtWidgets.QFrame()
        form_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_COLOR_LIGHT};
                border: 1px solid {CARD_BORDER};
                border-radius: 20px;
            }}
            QLabel {{
                color: {TEXT_COLOR_DARK};
                font-size: 11pt;
                font-weight: bold;
                border: none;
                background: transparent;
            }}
            QLineEdit, QDateEdit, QTextEdit, QTimeEdit {{
                background-color: {INPUT_BG};
                border: 1px solid {INPUT_BORDER};
                border-radius: 8px;
                padding: 8px;
                font-size: 11pt;
                color: {TEXT_COLOR_DARK};
            }}
            QComboBox {{
                background-color: {INPUT_BG};
                border: 1px solid {INPUT_BORDER};
                border-radius: 8px;
                padding: 8px;
                font-size: 11pt;
                color: {TEXT_COLOR_DARK};
            }}
            QComboBox::drop-down {{
                border: none;
                background: transparent;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid {TEXT_COLOR_DARK};
                margin: 10px;
            }}
            QPushButton {{
                background-color: {INPUT_BG};
                border: 1px solid {INPUT_BORDER};
                border-radius: 8px;
                padding: 10px;
                color: {TEXT_COLOR_DARK};
                font-weight: bold;
            }}
        """)
        
        form_layout = QtWidgets.QVBoxLayout(form_card)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)
        
        # Form Grid
        form_grid = QtWidgets.QGridLayout()
        form_grid.setSpacing(15)
        
        # Animal Tag / Unique ID
        form_grid.addWidget(QtWidgets.QLabel("Animal Tag / Unique ID"), 0, 0)
        tag_search_layout = QtWidgets.QHBoxLayout()
        self.tag_input = QtWidgets.QLineEdit()
        self.tag_input.setPlaceholderText("Search animal tag...")
        self.tag_input.returnPressed.connect(self._search_animal)
        
        search_btn = QtWidgets.QPushButton("🔍")
        search_btn.setFixedWidth(50)
        search_btn.clicked.connect(self._search_animal)
        
        tag_search_layout.addWidget(self.tag_input)
        tag_search_layout.addWidget(search_btn)
        form_grid.addLayout(tag_search_layout, 1, 0)
        
        # Animal Name
        form_grid.addWidget(QtWidgets.QLabel("Animal Name"), 0, 1)
        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("Auto-filled")
        self.name_input.setReadOnly(True)
        form_grid.addWidget(self.name_input, 1, 1)
        
        # Product Type
        form_grid.addWidget(QtWidgets.QLabel("Product Type"), 2, 0)
        self.product_combo = QtWidgets.QComboBox()
        self.product_combo.addItems(["Milk", "Eggs", "Wool bale", "Waste bin"])
        self.product_combo.currentTextChanged.connect(self._on_product_change)
        form_grid.addWidget(self.product_combo, 3, 0)
        
        # Quantity Input
        form_grid.addWidget(QtWidgets.QLabel("Quantity"), 2, 1)
        quantity_layout = QtWidgets.QHBoxLayout()
        self.quantity_input = QtWidgets.QLineEdit()
        self.quantity_input.setPlaceholderText("Enter quantity")
        
        self.unit_label = QtWidgets.QLabel("Liters")
        self.unit_label.setAlignment(QtCore.Qt.AlignCenter)
        self.unit_label.setMinimumWidth(80)
        
        quantity_layout.addWidget(self.quantity_input, 3)
        quantity_layout.addWidget(self.unit_label, 1)
        form_grid.addLayout(quantity_layout, 3, 1)
        
        # Time of Entry
        form_grid.addWidget(QtWidgets.QLabel("Time of Entry"), 4, 0)
        self.time_edit = QtWidgets.QTimeEdit()
        self.time_edit.setTime(QtCore.QTime.currentTime())
        self.time_edit.setDisplayFormat("h:mm AP")
        self.time_edit.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        form_grid.addWidget(self.time_edit, 5, 0)
        
        # Notes
        form_grid.addWidget(QtWidgets.QLabel("Notes (Optional)"), 4, 1)
        self.notes_input = QtWidgets.QTextEdit()
        self.notes_input.setPlaceholderText("Add notes...")
        self.notes_input.setMaximumHeight(70)
        form_grid.addWidget(self.notes_input, 5, 1)
        
        form_layout.addLayout(form_grid)
        
        # Last 3 Production Entries
        form_layout.addSpacing(10)
        entries_label = QtWidgets.QLabel("Last 3 Production Entries")
        entries_label.setStyleSheet(f"""
            color: {TEXT_COLOR_DARK};
            font-size: 11pt;
            font-weight: bold;
        """)
        form_layout.addWidget(entries_label)
        
        # Table for last entries (same format as production history)
        self.entries_table = QtWidgets.QTableWidget()
        self.entries_table.setColumnCount(5)
        self.entries_table.setHorizontalHeaderLabels(["Date", "Time", "Animal ID", "Product Type", "Quantity"])
        self.entries_table.horizontalHeader().setStretchLastSection(True)
        self.entries_table.setMaximumHeight(150)
        self.entries_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.entries_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.entries_table.verticalHeader().setVisible(False)
        self.entries_table.setAlternatingRowColors(True)
        self.entries_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                border: 1px solid {INPUT_BORDER};
                border-radius: 8px;
                gridline-color: {INPUT_BORDER};
            }}
            QTableWidget::item {{
                padding: 10px;
            }}
            QTableWidget::item:selected {{
                background-color: rgba(163, 177, 138, 0.3);
                color: {TEXT_COLOR_DARK};
            }}
            QTableWidget::item:alternate {{
                background-color: #F5F5F5;
            }}
            QHeaderView::section {{
                background-color: {TABLE_HEADER_BG};
                color: white;
                padding: 10px;
                font-weight: bold;
                font-size: 10pt;
                border: none;
            }}
        """)
        
        form_layout.addWidget(self.entries_table)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(15)
        
        save_btn = QtWidgets.QPushButton("Save Entry")
        save_btn.clicked.connect(self._save_entry)
        
        clear_btn = QtWidgets.QPushButton("Clear Form")
        clear_btn.clicked.connect(self._clear_form)
        
        button_layout.addWidget(save_btn, 1)
        button_layout.addWidget(clear_btn, 1)
        
        form_layout.addLayout(button_layout)
        
        return form_card
    
    def _search_animal(self):
        """Searches for an animal by tag number."""
        tag = self.tag_input.text().strip()
        if not tag:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter an animal tag to search.")
            return
        
        try:
            response = requests.get(f"http://localhost:8000/cattle/{tag}")
            if response.status_code == 200:
                data = response.json().get("data", {})
                # Handle both 'Name' and 'name' fields
                animal_name = data.get("name") or data.get("Name", "Unknown")
                self.name_input.setText(animal_name)
            elif response.status_code == 404:
                QtWidgets.QMessageBox.warning(self, "Not Found", f"No animal found with tag: {tag}")
                self.name_input.clear()
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Failed to fetch animal data.")
                self.name_input.clear()
        except requests.exceptions.ConnectionError:
            QtWidgets.QMessageBox.warning(self, "Connection Error", "Could not connect to server. Please ensure the backend is running.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
    
    def _on_product_change(self, product_type):
        """Updates the unit label based on selected product type."""
        units = {
            "Milk": "Liters",
            "Eggs": "Pieces",
            "Wool bale": "Kg",
            "Waste bin": "Kg"
        }
        self.unit_label.setText(units.get(product_type, "Units"))
    

    
    def _save_entry(self):
        """Saves the production entry."""
        # Validate inputs
        tag = self.tag_input.text().strip()
        quantity = self.quantity_input.text().strip()
        
        if not tag:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Please enter an animal tag.")
            return
        
        if not quantity:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Please enter a quantity.")
            return
        
        try:
            float(quantity)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Quantity must be a number.")
            return
        
        # Prepare data
        entry_data = {
            "animal_tag": tag,
            "animal_name": self.name_input.text(),
            "product_type": self.product_combo.currentText(),
            "quantity": float(quantity),
            "unit": self.unit_label.text(),
            "time": self.time_edit.time().toString("HH:mm"),
            "notes": self.notes_input.toPlainText(),
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Send to backend API first
        success = self._send_to_backend(entry_data)
        
        if success:
            # Add to recent entries
            self.recent_entries.insert(0, entry_data)
            
            # Update tables
            try:
                self._update_entries_table()
                self._update_production_history()
                self._update_summary_cards()
            except Exception as e:
                print(f"Error updating tables: {e}")
            
            # Show success message
            QtWidgets.QMessageBox.information(self, "Success", "Production entry saved successfully!")
            
            # Clear form
            self._clear_form()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Failed to save production entry. Please try again.")
    
    def _update_entries_table(self):
        """Updates the entries table with last 3 production entries (same format as production history)."""
        try:
            # Load all entries from backend to get last 3
            all_entries = self._load_all_entries_from_backend()
            
            if not all_entries:
                self.entries_table.setRowCount(0)
                return
            
            # Sort by date and time (most recent first) and take only last 3
            sorted_entries = sorted(all_entries, key=lambda x: (x.get('date', ''), x.get('time', '')), reverse=True)[:3]
            
            self.entries_table.setRowCount(len(sorted_entries))
            for row, entry in enumerate(sorted_entries):
                self.entries_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(entry.get("date", ""))))
                self.entries_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(entry.get("time", ""))))
                self.entries_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(entry.get("animal_tag", ""))))
                self.entries_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(entry.get("product_type", ""))))
                quantity_str = f"{entry.get('quantity', 0)} {entry.get('unit', 'L')}"
                self.entries_table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(quantity_str)))
        except Exception as e:
            print(f"Error updating entries table: {e}")
            self.entries_table.setRowCount(0)
    
    def _update_production_history(self):
        """Updates the production history table in the Overview tab."""
        try:
            # Load all entries from backend
            all_entries = self._load_all_entries_from_backend()
            
            if not all_entries:
                self.history_table.setRowCount(0)
                return
            
            # Sort entries by date and time (most recent first)
            sorted_entries = sorted(all_entries, key=lambda x: (x.get('date', ''), x.get('time', '')), reverse=True)
            
            self.history_table.setRowCount(len(sorted_entries))
            for row, entry in enumerate(sorted_entries):
                self.history_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(entry.get("date", ""))))
                self.history_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(entry.get("time", ""))))
                self.history_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(entry.get("animal_tag", ""))))
                self.history_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(entry.get("product_type", ""))))
                quantity_str = f"{entry.get('quantity', 0)} {entry.get('unit', 'L')}"
                self.history_table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(quantity_str)))
        except Exception as e:
            print(f"Error updating production history: {e}")
            self.history_table.setRowCount(0)
    
    def _update_summary_cards(self):
        """Updates the summary cards in the Overview tab."""
        from datetime import datetime, timedelta
        
        # Load all entries from backend
        all_entries = self._load_all_entries_from_backend()
        
        # Filter entries based on current filter
        filtered_entries = self._filter_entries_by_period(all_entries)
        
        # Calculate totals
        milk_total = sum(e['quantity'] for e in filtered_entries if e['product_type'] == 'Milk')
        eggs_total = sum(e['quantity'] for e in filtered_entries if e['product_type'] == 'Eggs')
        wool_total = sum(e['quantity'] for e in filtered_entries if e['product_type'] == 'Wool bale')
        
        # Calculate weekly total (all product types)
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        weekly_entries = []
        for e in all_entries:
            try:
                normalized_date = self._normalize_date(e.get('date', ''))
                entry_date = datetime.strptime(normalized_date, '%Y-%m-%d').date()
                if entry_date >= week_start:
                    weekly_entries.append(e)
            except:
                pass
        weekly_total = len(weekly_entries)
        
        # Update labels
        self.milk_value_label.setText(f"{milk_total:.0f} L")
        self.eggs_value_label.setText(f"{int(eggs_total)} Units")
        self.wool_value_label.setText(f"{wool_total:.0f} kg")
        self.weekly_value_label.setText(f"{weekly_total:,} Units")
        
        # Update comparison texts (placeholders for now)
        self.milk_subtitle_label.setText("+5% vs. yesterday")
        self.eggs_subtitle_label.setText("+8% vs. yesterday")
        self.wool_subtitle_label.setText("+10% vs. last month")
        self.weekly_subtitle_label.setText("+5% vs. last week")
    
    def _normalize_date(self, date_str):
        """Converts various date formats to YYYY-MM-DD format."""
        if not date_str:
            return ''
        
        from datetime import datetime
        
        # Try different date formats
        formats = ['%Y-%m-%d', '%m/%d/%y', '%m/%d/%Y', '%Y/%m/%d']
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no format matches, return as-is
        return date_str
    
    def _filter_entries_by_period(self, entries):
        """Filters entries based on the current filter period."""
        from datetime import datetime, timedelta
        
        if not entries:
            return []
        
        today = datetime.now().date()
        
        if self.current_filter == "Today":
            return [e for e in entries if self._normalize_date(e.get('date', '')) == today.strftime('%Y-%m-%d')]
        elif self.current_filter == "This Week":
            week_start = today - timedelta(days=today.weekday())
            filtered = []
            for e in entries:
                try:
                    normalized_date = self._normalize_date(e.get('date', ''))
                    entry_date = datetime.strptime(normalized_date, '%Y-%m-%d').date()
                    if entry_date >= week_start:
                        filtered.append(e)
                except:
                    pass
            return filtered
        elif self.current_filter == "This Month":
            month_start = today.replace(day=1)
            filtered = []
            for e in entries:
                try:
                    normalized_date = self._normalize_date(e.get('date', ''))
                    entry_date = datetime.strptime(normalized_date, '%Y-%m-%d').date()
                    if entry_date >= month_start:
                        filtered.append(e)
                except:
                    pass
            return filtered
        elif self.current_filter == "Custom" and self.custom_start_date and self.custom_end_date:
            # Filter by custom date range
            filtered = []
            for e in entries:
                try:
                    normalized_date = self._normalize_date(e.get('date', ''))
                    entry_date = datetime.strptime(normalized_date, '%Y-%m-%d').date()
                    if self.custom_start_date <= entry_date <= self.custom_end_date:
                        filtered.append(e)
                except:
                    pass
            return filtered
        else:
            return entries
    
    def _clear_form(self):
        """Clears all form fields."""
        self.tag_input.clear()
        self.name_input.clear()
        self.product_combo.setCurrentIndex(0)
        self.quantity_input.clear()
        self.time_edit.setTime(QtCore.QTime.currentTime())
        self.notes_input.clear()
    
    def _refresh_overview(self):
        """Refreshes the overview tab with latest data."""
        self._update_summary_cards()
        self._update_activity_list()
    
    def _handle_filter_change(self, filter_option):
        """Handles filter button clicks."""
        if filter_option == "Custom":
            # Show custom date range dialog
            dialog = CustomDateRangeDialog(self)
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                self.custom_start_date = dialog.start_date
                self.custom_end_date = dialog.end_date
                self.current_filter = filter_option
                self._update_filter_styles()
                self._refresh_overview()
        else:
            self.current_filter = filter_option
            self.custom_start_date = None
            self.custom_end_date = None
            self._update_filter_styles()
            self._refresh_overview()
    
    def _handle_tab_click_by_name(self, tab_name):
        """Switches to a tab by name."""
        if tab_name == "Manage":
            self.btn_manage.click()
    
    def _update_filter_styles(self):
        """Updates filter button styles based on current selection."""
        for btn in self.filter_buttons:
            if btn.text() == self.current_filter:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {TEXT_COLOR_DARK};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 0 15px;
                        font-size: 9pt;
                        font-weight: bold;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: white;
                        color: {TEXT_COLOR_DARK};
                        border: 1px solid #D0D0D0;
                        border-radius: 8px;
                        padding: 0 15px;
                        font-size: 9pt;
                        font-weight: normal;
                    }}
                    QPushButton:hover {{
                        background-color: {INPUT_BG};
                        border: 1px solid {INPUT_BORDER};
                    }}
                """)
    
    def _load_initial_data(self):
        """Loads initial data from backend when app starts."""
        try:
            # Load all entries from backend
            all_entries = self._load_all_entries_from_backend()
            
            # Update recent entries with last 3
            if all_entries:
                sorted_entries = sorted(all_entries, key=lambda x: (self._normalize_date(x.get('date', '')), x.get('time', '')), reverse=True)
                self.recent_entries = sorted_entries[:3]
            
            # Update UI
            self._update_summary_cards()
            self._update_production_history()
            self._update_entries_table()
        except Exception as e:
            print(f"Error loading initial data: {e}")
    
    def _refresh_overview(self):
        """Refreshes the overview tab with latest data."""
        self._update_summary_cards()
        self._update_production_history()
    
    def _load_all_entries_from_backend(self):
        """Loads all production entries from the backend."""
        try:
            # Try to fetch from backend API
            response = requests.get("http://localhost:8000/production/entries", params={"limit": 1000}, timeout=2)
            if response.status_code == 200:
                response_data = response.json()
                # Extract entries from the nested response structure
                entries = response_data.get("data", [])
                
                # Convert backend format to our format
                formatted_entries = []
                for entry in entries:
                    formatted_entries.append({
                        "date": entry.get("entry_date", ""),
                        "time": entry.get("entry_time", ""),
                        "animal_tag": entry.get("animal_tag", ""),
                        "animal_name": entry.get("animal_name", ""),
                        "product_type": entry.get("product_type", ""),
                        "quantity": entry.get("quantity", 0),
                        "unit": entry.get("unit", "L"),
                        "notes": entry.get("notes", "")
                    })
                return formatted_entries
        except Exception as e:
            print(f"Error loading entries from backend: {e}")
            pass
        
        # Fallback to local entries if backend is unavailable
        return self.recent_entries
    
    def _send_to_backend(self, entry_data):
        """Sends production entry to backend API."""
        try:
            response = requests.post("http://localhost:8000/production/entry", json=entry_data, timeout=5)
            if response.status_code == 200:
                print("✓ Entry saved to backend successfully")
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                print(f"✗ Backend error: {error_detail}")
                return True  # Still return True to proceed with local save
        except requests.exceptions.ConnectionError:
            # Just log the error, don't show popup since we save locally
            print("Warning: Could not connect to backend server. Entry saved locally only.")
            return True  # Still return True to proceed with local save
        except Exception as e:
            print(f"Error sending to backend: {str(e)}")
            return True  # Still return True to proceed with local save
