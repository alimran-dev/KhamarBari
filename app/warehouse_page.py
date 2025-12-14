from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import datetime, date, timedelta
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


class AddStockDialog(QtWidgets.QDialog):
    """Modal dialog for adding new stock items."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Stock")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QtWidgets.QLabel("Add New Stock Item")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #344E41;")
        layout.addWidget(title)
        
        # Form
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        
        # Item Name
        self.item_name_input = QtWidgets.QLineEdit()
        self.item_name_input.setPlaceholderText("Enter item name")
        self.item_name_input.setStyleSheet(self._input_style())
        form_layout.addRow("Item Name:*", self.item_name_input)
        
        # Category
        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.addItems(["Feed", "Medicine", "Equipment", "Products"])
        self.category_combo.setStyleSheet(self._input_style())
        form_layout.addRow("Category:*", self.category_combo)
        
        # Batch Number
        self.batch_input = QtWidgets.QLineEdit()
        self.batch_input.setPlaceholderText("e.g., B-1023")
        self.batch_input.setStyleSheet(self._input_style())
        form_layout.addRow("Batch No:*", self.batch_input)
        
        # Quantity
        quantity_layout = QtWidgets.QHBoxLayout()
        self.quantity_input = QtWidgets.QDoubleSpinBox()
        self.quantity_input.setRange(0, 999999)
        self.quantity_input.setDecimals(2)
        self.quantity_input.setStyleSheet(self._input_style())
        quantity_layout.addWidget(self.quantity_input, 2)
        
        # Unit
        self.unit_combo = QtWidgets.QComboBox()
        self.unit_combo.addItems(["kg", "L", "Vials", "Pcs", "Bags", "Units"])
        self.unit_combo.setStyleSheet(self._input_style())
        quantity_layout.addWidget(self.unit_combo, 1)
        form_layout.addRow("Quantity:*", quantity_layout)
        
        # Expiry Date
        self.expiry_date_input = QtWidgets.QDateEdit()
        self.expiry_date_input.setCalendarPopup(True)
        self.expiry_date_input.setDate(QtCore.QDate.currentDate().addYears(1))
        self.expiry_date_input.setDisplayFormat("yyyy-MM-dd")
        self.expiry_date_input.setStyleSheet(self._input_style())
        form_layout.addRow("Expiry Date:", self.expiry_date_input)
        
        # Item Photo Upload
        photo_layout = QtWidgets.QHBoxLayout()
        self.photo_path_label = QtWidgets.QLabel("No photo selected")
        self.photo_path_label.setStyleSheet("color: #666; font-size: 9pt; padding: 8px;")
        photo_layout.addWidget(self.photo_path_label, 1)
        
        browse_btn = QtWidgets.QPushButton("Browse")
        browse_btn.setFixedWidth(80)
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #588157;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #344E41;
            }
        """)
        browse_btn.clicked.connect(self._browse_photo)
        photo_layout.addWidget(browse_btn)
        form_layout.addRow("Item Photo:", photo_layout)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setFixedSize(100, 35)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #ccc;
                color: #333;
                border: none;
                border-radius: 5px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #bbb;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QtWidgets.QPushButton("Add Stock")
        save_btn.setFixedSize(100, 35)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #344E41;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #588157;
            }
        """)
        save_btn.clicked.connect(self._validate_and_accept)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.photo_path = None
    
    def _input_style(self):
        return """
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
                padding: 8px;
                border: 1px solid #A3B18A;
                border-radius: 5px;
                background-color: white;
                font-size: 10pt;
            }
        """
    
    def _browse_photo(self):
        """Open file dialog to select photo."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Item Photo", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.photo_path = file_path
            self.photo_path_label.setText(file_path.split("/")[-1])
    
    def _validate_and_accept(self):
        """Validate form before accepting."""
        # Check required fields
        if not self.item_name_input.text().strip():
            QtWidgets.QMessageBox.warning(self, "Required Field", "Please enter an item name.")
            self.item_name_input.setFocus()
            return
        
        if not self.batch_input.text().strip():
            QtWidgets.QMessageBox.warning(self, "Required Field", "Please enter a batch number.")
            self.batch_input.setFocus()
            return
        
        if self.quantity_input.value() <= 0:
            QtWidgets.QMessageBox.warning(self, "Invalid Quantity", "Please enter a quantity greater than 0.")
            self.quantity_input.setFocus()
            return
        
        # All validation passed
        self.accept()
    
    def get_data(self):
        """Return form data."""
        return {
            "item_name": self.item_name_input.text().strip(),
            "category": self.category_combo.currentText(),
            "batch_no": self.batch_input.text().strip(),
            "quantity": self.quantity_input.value(),
            "unit": self.unit_combo.currentText(),
            "expiry_date": self.expiry_date_input.date().toString("yyyy-MM-dd"),
            "photo_path": self.photo_path
        }


class TransferStockDialog(QtWidgets.QDialog):
    """Modal dialog for transferring stock to another category."""
    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.setWindowTitle("Transfer Stock")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QtWidgets.QLabel(f"Transfer: {item_data.get('item_name', 'Item')}")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #344E41;")
        layout.addWidget(title)
        
        # Info
        info_label = QtWidgets.QLabel(f"Current Category: {item_data.get('category', 'N/A')}")
        info_label.setStyleSheet("color: #666; font-size: 10pt; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # Form
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(12)
        
        # Target Category
        self.target_category = QtWidgets.QComboBox()
        categories = ["Feed", "Medicine", "Equipment", "Products"]
        current_category = item_data.get('category', '')
        for cat in categories:
            if cat != current_category:
                self.target_category.addItem(cat)
        self.target_category.setStyleSheet(self._input_style())
        form_layout.addRow("Transfer To:*", self.target_category)
        
        # Notes
        self.notes_input = QtWidgets.QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("Reason for transfer...")
        self.notes_input.setStyleSheet(self._input_style())
        form_layout.addRow("Notes:", self.notes_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setFixedSize(100, 35)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #ccc;
                color: #333;
                border: none;
                border-radius: 5px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #bbb;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        transfer_btn = QtWidgets.QPushButton("Transfer")
        transfer_btn.setFixedSize(100, 35)
        transfer_btn.setStyleSheet("""
            QPushButton {
                background-color: #344E41;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #588157;
            }
        """)
        transfer_btn.clicked.connect(self.accept)
        button_layout.addWidget(transfer_btn)
        
        layout.addLayout(button_layout)
    
    def _input_style(self):
        return """
            QComboBox, QTextEdit {
                padding: 8px;
                border: 1px solid #A3B18A;
                border-radius: 5px;
                background-color: white;
                font-size: 10pt;
            }
        """
    
    def get_data(self):
        """Return transfer data."""
        return {
            "target_category": self.target_category.currentText(),
            "notes": self.notes_input.toPlainText()
        }


class StockAdjustmentDialog(QtWidgets.QDialog):
    """Modal dialog for adjusting stock quantity."""
    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.setWindowTitle("Stock Adjustment")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QtWidgets.QLabel(f"Adjust: {item_data.get('item_name', 'Item')}")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #344E41;")
        layout.addWidget(title)
        
        # Current quantity info
        current_qty = item_data.get('quantity', 0)
        unit = item_data.get('unit', 'Units')
        info_label = QtWidgets.QLabel(f"Current Quantity: {current_qty} {unit}")
        info_label.setStyleSheet("color: #666; font-size: 10pt; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # Form
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(12)
        
        # Adjustment Type
        self.adjustment_type = QtWidgets.QComboBox()
        self.adjustment_type.addItems(["Add", "Remove", "Set To"])
        self.adjustment_type.setStyleSheet(self._input_style())
        form_layout.addRow("Adjustment Type:*", self.adjustment_type)
        
        # Quantity
        self.quantity_input = QtWidgets.QDoubleSpinBox()
        self.quantity_input.setMinimum(0.01)
        self.quantity_input.setRange(0, 999999)
        self.quantity_input.setDecimals(2)
        self.quantity_input.setValue(0)
        self.quantity_input.setStyleSheet(self._input_style())
        form_layout.addRow(f"Quantity ({unit}):*", self.quantity_input)
        
        # Reason
        self.reason_input = QtWidgets.QTextEdit()
        self.reason_input.setMaximumHeight(80)
        self.reason_input.setPlaceholderText("Required: Reason for adjustment...")
        self.reason_input.setStyleSheet(self._input_style())
        form_layout.addRow("Reason:*", self.reason_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setFixedSize(100, 35)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #ccc;
                color: #333;
                border: none;
                border-radius: 5px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #bbb;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QtWidgets.QPushButton("Save")
        save_btn.setFixedSize(100, 35)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #344E41;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #588157;
            }
        """)
        save_btn.clicked.connect(self._validate_and_accept)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def _input_style(self):
        return """
            QComboBox, QDoubleSpinBox, QTextEdit {
                padding: 8px;
                border: 1px solid #A3B18A;
                border-radius: 5px;
                background-color: white;
                font-size: 10pt;
            }
        """
    
    def _validate_and_accept(self):
        """Validate before accepting."""
        if not self.reason_input.toPlainText().strip():
            QtWidgets.QMessageBox.warning(self, "Required Field", "Please provide a reason for adjustment.")
            return
        self.accept()
    
    def get_data(self):
        """Return adjustment data with validation."""
        adj_type = self.adjustment_type.currentText()
        adj_qty = self.quantity_input.value()
        current_qty = self.item_data.get('quantity', 0)
        
        # Validate removal amount
        if adj_type == "Remove" and adj_qty > current_qty:
            QtWidgets.QMessageBox.warning(
                self, "Invalid Amount", 
                f"Cannot remove {adj_qty} units. Only {current_qty} units available."
            )
            return None
        
        # Confirm large adjustments
        if adj_type == "Set To" and abs(adj_qty - current_qty) > (current_qty * 0.5):
            reply = QtWidgets.QMessageBox.question(
                self, "Confirm Large Change",
                f"This will change quantity from {current_qty} to {adj_qty}.\n\nAre you sure?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if reply != QtWidgets.QMessageBox.Yes:
                return None
        
        return {
            "adjustment_type": adj_type,
            "quantity": adj_qty,
            "reason": self.reason_input.toPlainText()
        }


# --- Color Scheme ---
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


class WarehousePage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"QWidget {{ background-color: {BG_COLOR_LIGHT}; }}")
        
        # Main Layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(30, 20, 30, 30)
        self.layout.setSpacing(15)
        
        # Store data
        self.stock_items = []
        self.current_filter = "All"
        self.current_category = "All"  # Show all categories by default
        
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
        
        # Load initial data
        self.load_stock_data()
    
    def switch_to_manage_tab_and_open_add_dialog(self):
        """Switch to Manage tab and open Add Stock dialog."""
        self._update_tab_styles(self.btn_manage)
        self.stack.setCurrentIndex(1)
        self.load_stock_data()
        # Use QTimer to ensure the page is shown before opening dialog
        QtCore.QTimer.singleShot(100, self._open_add_stock_dialog)

    def _create_tab_button(self, text, position):
        """Create a styled tab button."""
        btn = QtWidgets.QPushButton(text)
        btn.setFixedHeight(45)
        btn.setFixedWidth(200)
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        
        border_radius = ""
        if position == "left":
            border_radius = "border-top-left-radius: 10px; border-bottom-left-radius: 10px;"
        elif position == "right":
            border_radius = "border-top-right-radius: 10px; border-bottom-right-radius: 10px;"
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                color: #344E41;
                border: 2px solid #588157;
                {border_radius}
                font-size: 11pt;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #f0f0f0;
            }}
        """)
        return btn
    
    def _handle_tab_click(self):
        """Handle tab button clicks."""
        sender = self.sender()
        if sender == self.btn_overview:
            self.stack.setCurrentIndex(0)
            self.load_stock_data()
        elif sender == self.btn_manage:
            self.stack.setCurrentIndex(1)
            self.load_stock_data()
        
        self._update_tab_styles(sender)
    
    def _update_tab_styles(self, active_btn):
        """Update tab button styles to reflect active tab."""
        for btn in self.tabs:
            if btn == self.btn_overview:
                border_radius = "border-top-left-radius: 10px; border-bottom-left-radius: 10px;"
            else:
                border_radius = "border-top-right-radius: 10px; border-bottom-right-radius: 10px;"
            
            if btn == active_btn:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #588157;
                        color: white;
                        border: 2px solid #588157;
                        {border_radius}
                        font-size: 11pt;
                        font-weight: bold;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: white;
                        color: #344E41;
                        border: 2px solid #588157;
                        {border_radius}
                        font-size: 11pt;
                        font-weight: 500;
                    }}
                    QPushButton:hover {{
                        background-color: #f0f0f0;
                    }}
                """)
    
    # ==================== OVERVIEW TAB ====================
    
    def _create_overview_tab(self):
        """Create the overview tab with stock cards and alerts."""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 15, 0, 0)
        
        # Scroll area for content
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }" + SCROLLBAR_STYLESHEET)
        
        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        
        # --- 1. Stock Summary Cards ---
        cards_container = QtWidgets.QWidget()
        cards_layout = QtWidgets.QHBoxLayout(cards_container)
        cards_layout.setSpacing(20)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        
        # Total Feed Stock Card
        self.feed_stock_card = self._create_stock_card("Total Feed Stock (kg)", "2,500", "🌾")
        cards_layout.addWidget(self.feed_stock_card)
        
        # Medicine Stock Card
        self.medicine_stock_card = self._create_stock_card("Medicine Stock", "150 Items", "💊")
        cards_layout.addWidget(self.medicine_stock_card)
        
        # Product Stock Card
        self.product_stock_card = self._create_stock_card("Product Stock (milk L / eggs pcs)", "500 L / 1,200 Pcs", "🥛")
        cards_layout.addWidget(self.product_stock_card)
        
        scroll_layout.addWidget(cards_container)
        
        # --- 2. Alerts Section ---
        alerts_section = self._create_alerts_section()
        scroll_layout.addWidget(alerts_section)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return tab
    
    def _create_stock_card(self, title, value, icon):
        """Create a stock summary card."""
        card = QtWidgets.QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 15px;
                border: 2px solid {CARD_BORDER};
                padding: 20px;
            }}
        """)
        card.setMinimumHeight(130)
        
        layout = QtWidgets.QVBoxLayout(card)
        layout.setSpacing(10)
        
        # Icon and Title
        header_layout = QtWidgets.QHBoxLayout()
        
        icon_label = QtWidgets.QLabel(icon)
        icon_label.setStyleSheet("font-size: 32pt; background: transparent; border: none;")
        header_layout.addWidget(icon_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Title
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(f"color: {TEXT_COLOR_DARK}; font-size: 10pt; font-weight: 500; background: transparent; border: none;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Value
        value_label = QtWidgets.QLabel(value)
        value_label.setStyleSheet(f"color: {TEXT_COLOR_DARK}; font-size: 20pt; font-weight: bold; background: transparent; border: none;")
        layout.addWidget(value_label)
        
        layout.addStretch()
        
        # Store reference for updating
        card.value_label = value_label
        
        return card
    
    def _create_alerts_section(self):
        """Create the alerts section showing low stock and expiring items."""
        section = QtWidgets.QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 15px;
                border: 2px solid {CARD_BORDER};
                padding: 20px;
            }}
        """)
        
        layout = QtWidgets.QVBoxLayout(section)
        layout.setSpacing(15)
        
        # Header
        header_layout = QtWidgets.QHBoxLayout()
        
        title = QtWidgets.QLabel("📅 Alerts Section")
        title.setStyleSheet(f"color: {TEXT_COLOR_DARK}; font-size: 14pt; font-weight: bold; background: transparent; border: none;")
        header_layout.addWidget(title)
        
        # Date/Time
        current_datetime = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p, Dhaka")
        date_label = QtWidgets.QLabel(current_datetime)
        date_label.setStyleSheet("color: #666; font-size: 9pt; background: transparent; border: none;")
        header_layout.addWidget(date_label, alignment=QtCore.Qt.AlignRight)
        
        layout.addLayout(header_layout)
        
        # Alert Content
        self.alerts_content = QtWidgets.QLabel()
        self.alerts_content.setStyleSheet("color: #344E41; font-size: 10pt; line-height: 1.5; background: transparent; border: none;")
        self.alerts_content.setWordWrap(True)
        self.alerts_content.setTextFormat(QtCore.Qt.RichText)
        layout.addWidget(self.alerts_content)
        
        return section
    
    def update_alerts(self):
        """Update alerts based on stock data."""
        low_stock_items = []
        expiring_items = []
        
        today = date.today()
        warning_date = today + timedelta(days=7)
        
        for item in self.stock_items:
            # Check for low stock
            quantity = item.get('quantity', 0)
            if quantity < 50:  # Threshold for low stock
                low_stock_items.append(f"{item.get('item_name', 'Unknown')} ({quantity} {item.get('unit', 'units')})")
            
            # Check for expiring items
            expiry_str = item.get('expiry_date', '')
            if expiry_str:
                try:
                    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                    days_until_expiry = (expiry_date - today).days
                    
                    if 0 <= days_until_expiry <= 7:
                        expiring_items.append(f"{item.get('item_name', 'Unknown')} (Expires in {days_until_expiry} days)")
                    elif days_until_expiry < 0:
                        expiring_items.append(f"{item.get('item_name', 'Unknown')} (Expired)")
                except:
                    pass
        
        # Build alert text
        alert_html = ""
        
        if low_stock_items:
            alert_html += "<b>⚠️ Low Stock:</b><br>"
            alert_html += ", ".join(low_stock_items[:5])  # Show first 5
            if len(low_stock_items) > 5:
                alert_html += f" <i>(+{len(low_stock_items) - 5} more)</i>"
            alert_html += "<br><br>"
        
        if expiring_items:
            alert_html += "<b>📆 Nearing Expiry:</b><br>"
            alert_html += ", ".join(expiring_items[:5])  # Show first 5
            if len(expiring_items) > 5:
                alert_html += f" <i>(+{len(expiring_items) - 5} more)</i>"
        
        if not alert_html:
            alert_html = "<span style='color: #28a745;'>✓ No alerts at this time. All stock levels are healthy.</span>"
        
        self.alerts_content.setText(alert_html)
    
    # ==================== MANAGE TAB ====================
    
    def _create_manage_tab(self):
        """Create the manage tab with category tabs and stock table."""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 15, 0, 0)
        
        # --- 1. Category Tabs ---
        category_container = QtWidgets.QWidget()
        category_layout = QtWidgets.QHBoxLayout(category_container)
        category_layout.setContentsMargins(0, 0, 0, 0)
        category_layout.setSpacing(10)
        
        # Category buttons
        self.category_buttons = []
        categories = [
            ("📋 All", "All"),
            ("🌾 Feed", "Feed"),
            ("💊 Medicine", "Medicine"),
            ("🔧 Equipment", "Equipment"),
            ("📦 Products", "Products")
        ]
        
        for label, category in categories:
            btn = QtWidgets.QPushButton(label)
            btn.setFixedHeight(45)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            btn.setProperty("category", category)
            btn.clicked.connect(self._handle_category_click)
            self.category_buttons.append(btn)
            category_layout.addWidget(btn)
        
        category_layout.addStretch()
        
        # Add New Stock Button (Modal)
        add_stock_btn = QtWidgets.QPushButton("+ Add New Stock (Modal)")
        add_stock_btn.setFixedHeight(45)
        add_stock_btn.setFixedWidth(200)
        add_stock_btn.setStyleSheet("""
            QPushButton {
                background-color: #344E41;
                color: white;
                border-radius: 10px;
                font-size: 10pt;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #588157;
            }
        """)
        add_stock_btn.clicked.connect(self._open_add_stock_dialog)
        category_layout.addWidget(add_stock_btn)
        
        layout.addWidget(category_container)
        
        # Update category button styles
        self._update_category_styles(self.category_buttons[0])
        
        # --- 2. Filters and Search ---
        filter_container = QtWidgets.QWidget()
        filter_layout = QtWidgets.QHBoxLayout(filter_container)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(15)
        
        # Search
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by name or batch number...")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 15px;
                border: 1px solid {INPUT_BORDER};
                border-radius: 10px;
                background-color: white;
                font-size: 10pt;
            }}
        """)
        self.search_input.textChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.search_input, 3)
        
        # Period Filter
        period_label = QtWidgets.QLabel("Filter by:")
        period_label.setStyleSheet(f"color: {TEXT_COLOR_DARK}; font-size: 10pt; font-weight: 500;")
        filter_layout.addWidget(period_label)
        
        self.period_combo = QtWidgets.QComboBox()
        self.period_combo.addItems(["All", "Low Stock", "Expiring Soon", "Expired"])
        self.period_combo.setFixedHeight(40)
        self.period_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px 15px;
                border: 1px solid {INPUT_BORDER};
                border-radius: 10px;
                background-color: white;
                font-size: 10pt;
                min-width: 150px;
            }}
        """)
        self.period_combo.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.period_combo)
        
        layout.addWidget(filter_container)
        
        # --- 3. Stock Table ---
        self.stock_table = QtWidgets.QTableWidget()
        self.stock_table.setColumnCount(8)
        self.stock_table.setHorizontalHeaderLabels([
            "Photo", "Item Name", "Category", "Batch No.", 
            "Quantity", "Unit", "Expiry Date", "Actions"
        ])
        
        # Table styling
        self.stock_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                border: 1px solid {CARD_BORDER};
                border-radius: 10px;
                gridline-color: #E0E0E0;
                font-size: 10pt;
            }}
            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid #E0E0E0;
            }}
            QHeaderView::section {{
                background-color: {TABLE_HEADER_BG};
                color: white;
                padding: 12px;
                font-size: 10pt;
                font-weight: bold;
                border: none;
            }}
        """ + SCROLLBAR_STYLESHEET)
        
        self.stock_table.horizontalHeader().setStretchLastSection(False)
        self.stock_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.stock_table.setColumnWidth(0, 70)   # Photo - slightly smaller
        self.stock_table.setColumnWidth(2, 100)  # Category - shorter
        self.stock_table.setColumnWidth(3, 110)  # Batch No - optimized
        self.stock_table.setColumnWidth(4, 100)  # Quantity - more compact
        self.stock_table.setColumnWidth(5, 70)   # Unit - shorter
        self.stock_table.setColumnWidth(6, 110)  # Expiry - optimized
        self.stock_table.setColumnWidth(7, 180)  # Actions - slightly smaller
        
        self.stock_table.verticalHeader().setVisible(False)
        self.stock_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.stock_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.stock_table)
        
        return tab
    
    def _handle_category_click(self):
        """Handle category button clicks."""
        sender = self.sender()
        self.current_category = sender.property("category")
        self._update_category_styles(sender)
        self._apply_filters()
    
    def _update_category_styles(self, active_btn):
        """Update category button styles."""
        for btn in self.category_buttons:
            if btn == active_btn:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {BG_COLOR_DARK};
                        color: white;
                        border-radius: 10px;
                        font-size: 10pt;
                        font-weight: bold;
                        border: none;
                        padding: 0 20px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: white;
                        color: {TEXT_COLOR_DARK};
                        border: 2px solid {CARD_BORDER};
                        border-radius: 10px;
                        font-size: 10pt;
                        font-weight: 500;
                        padding: 0 20px;
                    }}
                    QPushButton:hover {{
                        background-color: {INPUT_BG};
                    }}
                """)
    
    def _apply_filters(self):
        """Apply search and filter criteria to stock table."""
        search_text = self.search_input.text().lower()
        filter_type = self.period_combo.currentText()
        
        filtered_items = []
        today = date.today()
        
        for item in self.stock_items:
            # Category filter (skip if 'All' is selected)
            if self.current_category != "All" and item.get('category', '') != self.current_category:
                continue
            
            # Search filter
            if search_text:
                item_name = item.get('item_name', '').lower()
                batch_no = item.get('batch_no', '').lower()
                if search_text not in item_name and search_text not in batch_no:
                    continue
            
            # Status filter
            if filter_type == "Low Stock":
                if item.get('quantity', 0) >= 50:
                    continue
            elif filter_type == "Expiring Soon":
                expiry_str = item.get('expiry_date', '')
                if expiry_str:
                    try:
                        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                        days_until = (expiry_date - today).days
                        if not (0 <= days_until <= 7):
                            continue
                    except:
                        continue
                else:
                    continue
            elif filter_type == "Expired":
                expiry_str = item.get('expiry_date', '')
                if expiry_str:
                    try:
                        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                        if expiry_date >= today:
                            continue
                    except:
                        continue
                else:
                    continue
            
            filtered_items.append(item)
        
        self._populate_table(filtered_items)
    
    def _populate_table(self, items):
        """Populate the stock table with items."""
        self.stock_table.setRowCount(0)
        
        for row, item in enumerate(items):
            self.stock_table.insertRow(row)
            self.stock_table.setRowHeight(row, 70)
            
            # Photo
            photo_label = QtWidgets.QLabel()
            photo_label.setAlignment(QtCore.Qt.AlignCenter)
            photo_path = item.get('photo_path', '')
            if photo_path:
                pixmap = QtGui.QPixmap(photo_path)
                if not pixmap.isNull():
                    photo_label.setPixmap(pixmap.scaled(50, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
                else:
                    photo_label.setText("📦")
                    photo_label.setStyleSheet("font-size: 24pt;")
            else:
                photo_label.setText("📦")
                photo_label.setStyleSheet("font-size: 24pt;")
            self.stock_table.setCellWidget(row, 0, photo_label)
            
            # Item Name
            self.stock_table.setItem(row, 1, QtWidgets.QTableWidgetItem(item.get('item_name', '')))
            
            # Category
            self.stock_table.setItem(row, 2, QtWidgets.QTableWidgetItem(item.get('category', '')))
            
            # Batch No
            self.stock_table.setItem(row, 3, QtWidgets.QTableWidgetItem(item.get('batch_no', '')))
            
            # Quantity
            quantity = item.get('quantity', 0)
            qty_item = QtWidgets.QTableWidgetItem(str(quantity))
            
            # Color code for low stock
            if quantity < 25:
                qty_item.setBackground(QtGui.QColor("#ffcccc"))  # Red tint
            elif quantity < 50:
                qty_item.setBackground(QtGui.QColor("#fff3cd"))  # Yellow tint
            
            self.stock_table.setItem(row, 4, qty_item)
            
            # Unit
            self.stock_table.setItem(row, 5, QtWidgets.QTableWidgetItem(item.get('unit', '')))
            
            # Expiry Date with status badge
            expiry_widget = QtWidgets.QWidget()
            expiry_layout = QtWidgets.QHBoxLayout(expiry_widget)
            expiry_layout.setContentsMargins(5, 0, 5, 0)
            
            expiry_date_str = item.get('expiry_date', '')
            expiry_label = QtWidgets.QLabel(expiry_date_str)
            expiry_label.setStyleSheet("font-size: 10pt;")
            expiry_layout.addWidget(expiry_label)
            
            # Add badge if expiring or expired
            if expiry_date_str:
                try:
                    expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
                    days_until = (expiry_date - date.today()).days
                    
                    if days_until < 0:
                        badge = QtWidgets.QLabel("Expired")
                        badge.setStyleSheet("""
                            background-color: #d9534f;
                            color: white;
                            padding: 3px 8px;
                            border-radius: 8px;
                            font-size: 8pt;
                            font-weight: bold;
                        """)
                        expiry_layout.addWidget(badge)
                    elif days_until <= 7:
                        badge = QtWidgets.QLabel("Soon")
                        badge.setStyleSheet("""
                            background-color: #f0ad4e;
                            color: white;
                            padding: 3px 8px;
                            border-radius: 8px;
                            font-size: 8pt;
                            font-weight: bold;
                        """)
                        expiry_layout.addWidget(badge)
                except:
                    pass
            
            expiry_layout.addStretch()
            self.stock_table.setCellWidget(row, 6, expiry_widget)
            
            # Actions
            actions_widget = QtWidgets.QWidget()
            actions_layout = QtWidgets.QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 0, 5, 0)
            actions_layout.setSpacing(5)
            
            # Adjust Button
            adjust_btn = QtWidgets.QPushButton("Adjust")
            adjust_btn.setFixedHeight(30)
            adjust_btn.setStyleSheet("""
                QPushButton {
                    background-color: #344E41;
                    color: white;
                    border-radius: 5px;
                    padding: 5px 10px;
                    font-size: 9pt;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #588157;
                }
            """)
            adjust_btn.setProperty("item_data", item)
            adjust_btn.clicked.connect(self._open_adjustment_dialog)
            actions_layout.addWidget(adjust_btn)
            
            # Transfer Button
            transfer_btn = QtWidgets.QPushButton("Transfer")
            transfer_btn.setFixedHeight(30)
            transfer_btn.setStyleSheet("""
                QPushButton {
                    background-color: #5bc0de;
                    color: white;
                    border-radius: 5px;
                    padding: 5px 10px;
                    font-size: 9pt;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #31b0d5;
                }
            """)
            transfer_btn.setProperty("item_data", item)
            transfer_btn.clicked.connect(self._open_transfer_dialog)
            actions_layout.addWidget(transfer_btn)
            
            actions_layout.addStretch()
            self.stock_table.setCellWidget(row, 7, actions_widget)
    
    # ==================== DIALOGS ====================
    
    def _open_add_stock_dialog(self):
        """Open add stock modal dialog."""
        dialog = AddStockDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            data = dialog.get_data()
            self._add_stock_item(data)
    
    def _open_transfer_dialog(self):
        """Open transfer stock dialog."""
        sender = self.sender()
        item_data = sender.property("item_data")
        
        dialog = TransferStockDialog(item_data, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            transfer_data = dialog.get_data()
            self._transfer_stock(item_data, transfer_data)
    
    def _open_adjustment_dialog(self):
        """Open stock adjustment dialog."""
        sender = self.sender()
        item_data = sender.property("item_data")
        
        dialog = StockAdjustmentDialog(item_data, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            adjustment_data = dialog.get_data()
            if adjustment_data:  # Check if validation passed
                self._adjust_stock(item_data, adjustment_data)
    
    # ==================== API CALLS ====================
    
    def load_stock_data(self):
        """Load stock data from backend."""
        try:
            response = requests.get("http://localhost:8000/warehouse/stock")
            if response.status_code == 200:
                data = response.json()
                self.stock_items = data.get('data', [])
                self._apply_filters()
                self.update_stock_cards()
                self.update_alerts()
            else:
                # Load sample data for testing
                self._load_sample_data()
        except:
            # Load sample data if backend is not available
            self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample data for testing."""
        self.stock_items = [
            {
                "id": 1,
                "item_name": "Cattle Feed Type A",
                "category": "Feed",
                "batch_no": "B-1023",
                "quantity": 1200,
                "unit": "kg",
                "expiry_date": "2026-01-15",
                "photo_path": None
            },
            {
                "id": 2,
                "item_name": "Antibiotic X",
                "category": "Medicine",
                "batch_no": "M-0456",
                "quantity": 25,
                "unit": "Vials",
                "expiry_date": "2025-12-01",
                "photo_path": None
            },
            {
                "id": 3,
                "item_name": "Fresh Milk",
                "category": "Products",
                "batch_no": "P-3451",
                "quantity": 50,
                "unit": "L",
                "expiry_date": "2025-11-28",
                "photo_path": None
            },
            {
                "id": 4,
                "item_name": "Layer Feed",
                "category": "Feed",
                "batch_no": "B-2045",
                "quantity": 100,
                "unit": "kg",
                "expiry_date": "2026-03-20",
                "photo_path": None
            },
            {
                "id": 5,
                "item_name": "Vitamin B12",
                "category": "Medicine",
                "batch_no": "M-1122",
                "quantity": 15,
                "unit": "Vials",
                "expiry_date": "2025-12-05",
                "photo_path": None
            },
            {
                "id": 6,
                "item_name": "Milking Machine Parts",
                "category": "Equipment",
                "batch_no": "E-5678",
                "quantity": 5,
                "unit": "Pcs",
                "expiry_date": "",
                "photo_path": None
            },
        ]
        self._apply_filters()
        self.update_stock_cards()
        self.update_alerts()
    
    def update_stock_cards(self):
        """Update stock summary cards."""
        # Calculate totals
        total_feed = sum(item['quantity'] for item in self.stock_items if item['category'] == 'Feed')
        medicine_count = len([item for item in self.stock_items if item['category'] == 'Medicine'])
        
        milk_qty = sum(item['quantity'] for item in self.stock_items if item['category'] == 'Products' and 'milk' in item.get('item_name', '').lower())
        eggs_qty = sum(item['quantity'] for item in self.stock_items if item['category'] == 'Products' and 'egg' in item.get('item_name', '').lower())
        
        # Update cards
        self.feed_stock_card.value_label.setText(f"{int(total_feed):,}")
        self.medicine_stock_card.value_label.setText(f"{medicine_count} Items")
        self.product_stock_card.value_label.setText(f"{int(milk_qty)} L / {int(eggs_qty)} Pcs")
    
    def _add_stock_item(self, data):
        """Add new stock item via API."""
        try:
            # Clean up data - remove None values or convert to empty strings
            payload = {
                "item_name": data['item_name'],
                "category": data['category'],
                "batch_no": data['batch_no'],
                "quantity": data['quantity'],
                "unit": data['unit']
            }
            
            # Only add optional fields if they have values
            if data.get('expiry_date'):
                payload['expiry_date'] = data['expiry_date']
            if data.get('photo_path'):
                payload['photo_path'] = data['photo_path']
            
            response = requests.post("http://localhost:8000/warehouse/stock", json=payload)
            if response.status_code == 200:
                QtWidgets.QMessageBox.information(self, "Success", "Stock item added successfully!")
                self.load_stock_data()
            else:
                error_detail = response.json().get('detail', 'Failed to add stock item.')
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to add stock item.\n{error_detail}")
        except requests.exceptions.ConnectionError:
            # Show helpful connection error
            QtWidgets.QMessageBox.warning(
                self, "Connection Error", 
                "Cannot connect to backend server.\n\n"
                "Please ensure the backend is running:\n"
                "  cd backend && uvicorn main:app --reload"
            )
            
            # Fallback: add to local list for testing
            new_item = {
                "id": len(self.stock_items) + 1,
                "item_name": data['item_name'],
                "category": data['category'],
                "batch_no": data['batch_no'],
                "quantity": data['quantity'],
                "unit": data['unit'],
                "expiry_date": data.get('expiry_date', ''),
                "photo_path": data.get('photo_path', '')
            }
            self.stock_items.append(new_item)
            self.load_stock_data()
    
    def _transfer_stock(self, item_data, transfer_data):
        """Transfer stock to another category."""
        try:
            payload = {
                "item_id": item_data.get('id'),
                "target_category": transfer_data['target_category']
            }
            # Only add notes if provided
            if transfer_data.get('notes'):
                payload['notes'] = transfer_data['notes']
            
            response = requests.post("http://localhost:8000/warehouse/transfer", json=payload)
            if response.status_code == 200:
                QtWidgets.QMessageBox.information(self, "Success", "Stock transferred successfully!")
                self.load_stock_data()
            else:
                error_detail = response.json().get('detail', 'Failed to transfer stock.')
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to transfer stock.\n{error_detail}")
        except requests.exceptions.ConnectionError:
            QtWidgets.QMessageBox.warning(
                self, "Connection Error",
                "Cannot connect to backend server.\n\n"
                "Please ensure the backend is running:\n"
                "  cd backend && uvicorn main:app --reload"
            )
            # Fallback for testing
            for item in self.stock_items:
                if item.get('id') == item_data.get('id'):
                    item['category'] = transfer_data['target_category']
                    break
            self.load_stock_data()
    
    def _adjust_stock(self, item_data, adjustment_data):
        """Adjust stock quantity."""
        try:
            payload = {
                "item_id": item_data.get('id'),
                "adjustment_type": adjustment_data['adjustment_type'],
                "quantity": adjustment_data['quantity'],
                "reason": adjustment_data['reason']
            }
            response = requests.post("http://localhost:8000/warehouse/adjust", json=payload)
            if response.status_code == 200:
                QtWidgets.QMessageBox.information(self, "Success", "Stock adjusted successfully!")
                self.load_stock_data()
            else:
                error_detail = response.json().get('detail', 'Failed to adjust stock.')
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to adjust stock.\n{error_detail}")
        except requests.exceptions.ConnectionError:
            QtWidgets.QMessageBox.warning(
                self, "Connection Error",
                "Cannot connect to backend server.\n\n"
                "Please ensure the backend is running:\n"
                "  cd backend && uvicorn main:app --reload"
            )
            # For testing
            for item in self.stock_items:
                if item.get('id') == item_data.get('id'):
                    current_qty = item.get('quantity', 0)
                    adj_type = adjustment_data['adjustment_type']
                    adj_qty = adjustment_data['quantity']
                    
                    if adj_type == "Add":
                        item['quantity'] = current_qty + adj_qty
                    elif adj_type == "Remove":
                        item['quantity'] = max(0, current_qty - adj_qty)
                    elif adj_type == "Set To":
                        item['quantity'] = adj_qty
                    break
            QtWidgets.QMessageBox.information(self, "Success", "Stock adjusted successfully!")
            self.load_stock_data()
