from PyQt5 import QtWidgets, QtCore, QtGui
import requests
from datetime import datetime
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


class FinanceEntryPage(QtWidgets.QWidget):
    """Financial Entry Form Page - Add Expense/Income"""
    
    def __init__(self, user_email):
        super().__init__()
        self.user_email = user_email
        self.categories = []
        self.templates = []
        
        self.setStyleSheet("""
            QWidget {
                background-color: #EBEAE3;
                color: #344E41;
            }
            QLabel {
                color: #344E41;
                font-weight: bold;
                font-size: 11pt;
                background: transparent;
            }
            QLineEdit, QDateEdit, QTextEdit, QComboBox, QDoubleSpinBox {
                background-color: #D8E2D1;
                border: 1px solid #A3B18A;
                border-radius: 8px;
                padding: 8px;
                color: #344E41;
                font-size: 11pt;
            }
            QLineEdit:focus, QDateEdit:focus, QTextEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #588157;
            }
            QComboBox::drop-down {
                border: none;
                background: transparent;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 2px solid #A3B18A;
                width: 0; 
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid #344E41;
                margin: 10px;
            }
            QPushButton {
                background-color: #D8E2D1;
                border: 1px solid #A3B18A;
                border-radius: 8px;
                padding: 10px;
                color: #344E41;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #C5D4BA;
            }
            QPushButton#primaryBtn {
                background-color: #588157;
                color: white;
                border: none;
            }
            QPushButton#primaryBtn:hover {
                background-color: #4A6A55;
            }
            QPushButton#templateBtn {
                background-color: #A3B18A;
                color: #344E41;
                padding: 8px 16px;
                font-size: 10pt;
            }
            QPushButton#templateBtn:hover {
                background-color: #8A9A7A;
            }
            QRadioButton {
                color: #344E41;
                font-size: 11pt;
                font-weight: bold;
                background: transparent;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:checked {
                background-color: #588157;
                border: 2px solid #344E41;
                border-radius: 9px;
            }
            QRadioButton::indicator:unchecked {
                background-color: #D8E2D1;
                border: 1px solid #A3B18A;
                border-radius: 9px;
            }
            QGroupBox {
                background-color: transparent;
                border: 1px solid #B5C9A9;
                border-radius: 12px;
                margin-top: 15px;
                padding: 20px;
                font-weight: bold;
                color: #344E41;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                color: #344E41;
            }
            QScrollArea {
                border: none;
                background-color: #EBEAE3;
            }
        """)
        
        self.init_ui()
        self.load_categories()
        self.load_templates()
    
    def init_ui(self):
        """Initialize the UI"""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)
        
        # Scroll area for form
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        # Container widget for scroll
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 10, 0)
        scroll_layout.setSpacing(0)
        
        # Card Container (matching cattle form design)
        card = QtWidgets.QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #EBEAE3;
                border: 1px solid #B5C9A9;
                border-radius: 20px;
            }
        """)
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(20)
        
        # Title
        title_layout = QtWidgets.QHBoxLayout()
        title_layout.setSpacing(10)
        icon_label = QtWidgets.QLabel("💰")
        icon_label.setStyleSheet("font-size: 24pt; font-weight: 900; color: #344E41; background: transparent;")
        title_label = QtWidgets.QLabel("New Financial Entry")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #344E41; background: transparent;")
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        card_layout.addLayout(title_layout)
        card_layout.addSpacing(10)
        
        # Entry Type Toggle (Expense/Income)
        type_container = QtWidgets.QWidget()
        type_container.setStyleSheet("background: transparent;")
        type_layout = QtWidgets.QHBoxLayout(type_container)
        type_layout.setContentsMargins(0, 0, 0, 0)
        type_layout.setSpacing(20)
        
        type_label = QtWidgets.QLabel("Entry Type:")
        type_label.setStyleSheet("color: #344E41; font-weight: bold; font-size: 11pt; background: transparent;")
        type_layout.addWidget(type_label)
        
        self.expense_radio = QtWidgets.QRadioButton("💸 Expense")
        self.income_radio = QtWidgets.QRadioButton("💰 Income")
        self.expense_radio.setChecked(True)
        self.expense_radio.toggled.connect(self.on_type_changed)
        
        type_layout.addWidget(self.expense_radio)
        type_layout.addWidget(self.income_radio)
        type_layout.addStretch()
        
        card_layout.addWidget(type_container)
        card_layout.addSpacing(10)
        
        # Form Fields Grid Layout
        form_grid = QtWidgets.QGridLayout()
        form_grid.setSpacing(12)
        form_grid.setVerticalSpacing(10)
        form_grid.setHorizontalSpacing(20)
        
        # Row 0: Category label
        cat_label = QtWidgets.QLabel("Category")
        cat_label.setStyleSheet("color: #344E41; font-weight: bold; font-size: 11pt; background: transparent;")
        form_grid.addWidget(cat_label, 0, 0)
        
        # Row 0: Date label
        date_label = QtWidgets.QLabel("Date")
        date_label.setStyleSheet("color: #344E41; font-weight: bold; font-size: 11pt; background: transparent;")
        form_grid.addWidget(date_label, 0, 1)
        
        # Row 1: Category and Date inputs
        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.setMinimumHeight(40)
        form_grid.addWidget(self.category_combo, 1, 0)
        
        self.date_edit = QtWidgets.QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QtCore.QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setMinimumHeight(40)
        form_grid.addWidget(self.date_edit, 1, 1)
        
        # Row 2: Amount label
        amt_label = QtWidgets.QLabel("Amount (৳)")
        amt_label.setStyleSheet("color: #344E41; font-weight: bold; font-size: 11pt; background: transparent;")
        form_grid.addWidget(amt_label, 2, 0)
        
        # Row 3: Amount input
        self.amount_input = QtWidgets.QDoubleSpinBox()
        self.amount_input.setMinimum(0.01)
        self.amount_input.setMaximum(999999999.99)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("৳ ")
        self.amount_input.setMinimumHeight(40)
        form_grid.addWidget(self.amount_input, 3, 0, 1, 2)
        
        self.amount_error = QtWidgets.QLabel("")
        self.amount_error.setStyleSheet("color: #CC0000; font-size: 9pt; font-weight: normal; background: transparent;")
        self.amount_error.hide()
        form_grid.addWidget(self.amount_error, 4, 0, 1, 2)
        
        # Row 5: Description label
        desc_label = QtWidgets.QLabel("Description")
        desc_label.setStyleSheet("color: #344E41; font-weight: bold; font-size: 11pt; background: transparent;")
        form_grid.addWidget(desc_label, 5, 0)
        
        # Row 6: Description input
        self.description_input = QtWidgets.QLineEdit()
        self.description_input.setPlaceholderText("Brief description...")
        self.description_input.setMinimumHeight(40)
        form_grid.addWidget(self.description_input, 6, 0, 1, 2)
        
        # Row 7: Notes label
        notes_label = QtWidgets.QLabel("Notes (Optional)")
        notes_label.setStyleSheet("color: #344E41; font-weight: bold; font-size: 11pt; background: transparent;")
        form_grid.addWidget(notes_label, 7, 0)
        
        # Row 8: Notes input
        self.notes_input = QtWidgets.QTextEdit()
        self.notes_input.setPlaceholderText("Additional details...")
        self.notes_input.setMinimumHeight(80)
        self.notes_input.setMaximumHeight(120)
        form_grid.addWidget(self.notes_input, 8, 0, 1, 2)
        
        card_layout.addLayout(form_grid)
        
        # Receipt Upload
        card_layout.addSpacing(15)
        receipt_container = QtWidgets.QWidget()
        receipt_container.setStyleSheet("background: transparent;")
        receipt_layout = QtWidgets.QVBoxLayout(receipt_container)
        receipt_layout.setContentsMargins(0, 0, 0, 0)
        receipt_layout.setSpacing(8)
        
        receipt_label = QtWidgets.QLabel("Receipt Upload (Optional)")
        receipt_label.setStyleSheet("color: #344E41; font-weight: bold; font-size: 11pt; background: transparent;")
        receipt_layout.addWidget(receipt_label)
        
        receipt_btn_layout = QtWidgets.QHBoxLayout()
        receipt_btn_layout.setSpacing(15)
        self.upload_btn = QtWidgets.QPushButton("📎 Upload Image/PDF")
        self.upload_btn.setMinimumHeight(40)
        self.upload_btn.setMinimumWidth(180)
        self.upload_btn.clicked.connect(self.upload_receipt)
        receipt_btn_layout.addWidget(self.upload_btn)
        
        self.receipt_label = QtWidgets.QLabel("No file selected")
        self.receipt_label.setStyleSheet("color: #588157; font-weight: normal; font-size: 10pt; background: transparent;")
        receipt_btn_layout.addWidget(self.receipt_label)
        receipt_btn_layout.addStretch()
        
        receipt_layout.addLayout(receipt_btn_layout)
        card_layout.addWidget(receipt_container)
        
        # Buttons
        card_layout.addSpacing(20)
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(15)
        btn_layout.addStretch()
        
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setMinimumWidth(130)
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.clicked.connect(self.cancel_entry)
        btn_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QtWidgets.QPushButton("💾 Save Entry")
        self.save_btn.setObjectName("primaryBtn")
        self.save_btn.setMinimumWidth(150)
        self.save_btn.setMinimumHeight(45)
        self.save_btn.clicked.connect(self.save_entry)
        btn_layout.addWidget(self.save_btn)
        
        card_layout.addLayout(btn_layout)
        
        # Quick Shortcuts Section
        card_layout.addSpacing(15)
        shortcuts_group = QtWidgets.QGroupBox("Quick Templates")
        shortcuts_group.setMinimumHeight(80)
        shortcuts_layout = QtWidgets.QHBoxLayout(shortcuts_group)
        shortcuts_layout.setSpacing(10)
        
        self.shortcuts_container = QtWidgets.QHBoxLayout()
        self.shortcuts_container.setSpacing(10)
        shortcuts_layout.addLayout(self.shortcuts_container)
        
        card_layout.addWidget(shortcuts_group)
        
        # Add card to scroll layout
        scroll_layout.addWidget(card)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
        self.receipt_path = None
    
    def load_categories(self):
        """Load categories from API"""
        try:
            response = requests.get(f"{API_URL}/finance/categories")
            if response.status_code == 200:
                data = response.json()
                self.categories = data.get("data", [])
                self.populate_categories()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to load categories: {str(e)}")
    
    def populate_categories(self):
        """Populate category dropdown based on selected type"""
        self.category_combo.clear()
        entry_type = "expense" if self.expense_radio.isChecked() else "income"
        
        for cat in self.categories:
            if cat["type"] == entry_type:
                self.category_combo.addItem(cat["name"], cat["id"])
    
    def on_type_changed(self):
        """Handle entry type change"""
        self.populate_categories()
    
    def load_templates(self):
        """Load expense templates from API"""
        try:
            response = requests.get(f"{API_URL}/finance/templates")
            if response.status_code == 200:
                data = response.json()
                self.templates = data.get("data", [])
                self.populate_templates()
        except Exception as e:
            print(f"Failed to load templates: {str(e)}")
    
    def populate_templates(self):
        """Populate quick shortcut buttons"""
        # Clear existing buttons
        while self.shortcuts_container.count():
            item = self.shortcuts_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add template buttons
        for template in self.templates[:3]:  # Show max 3 templates
            btn = QtWidgets.QPushButton(f"{template.get('icon', '📝')} {template['name']}")
            btn.setObjectName("templateBtn")
            btn.clicked.connect(lambda checked, t=template: self.apply_template(t))
            self.shortcuts_container.addWidget(btn)
        
        self.shortcuts_container.addStretch()
    
    def apply_template(self, template):
        """Apply a template to the form"""
        # Set category
        category_id = template.get("category_id")
        index = self.category_combo.findData(category_id)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        
        # Set description
        if template.get("description"):
            self.description_input.setText(template["description"])
        
        # Set default amount if available
        if template.get("default_amount"):
            self.amount_input.setValue(template["default_amount"])
        
        QtWidgets.QMessageBox.information(self, "Template Applied", 
                                         f"Template '{template['name']}' applied successfully!")
    
    def upload_receipt(self):
        """Open file dialog to select receipt"""
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Receipt",
            "",
            "Images and PDFs (*.jpg *.jpeg *.png *.pdf);;All Files (*)"
        )
        
        if file_path:
            self.receipt_path = file_path
            filename = os.path.basename(file_path)
            self.receipt_label.setText(f"✓ {filename}")
            self.receipt_label.setStyleSheet("color: #588157; font-weight: bold; font-size: 10pt;")
    
    def validate_form(self):
        """Validate form inputs"""
        # Validate amount
        if self.amount_input.value() <= 0:
            self.amount_error.setText("Please enter a valid amount")
            self.amount_error.show()
            return False
        else:
            self.amount_error.hide()
        
        # Validate category
        if self.category_combo.currentIndex() < 0:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Please select a category")
            return False
        
        return True
    
    def save_entry(self):
        """Save the financial entry"""
        if not self.validate_form():
            return
        
        try:
            # Prepare data
            entry_type = "expense" if self.expense_radio.isChecked() else "income"
            category_id = self.category_combo.currentData()
            amount = self.amount_input.value()
            date = self.date_edit.date().toString("yyyy-MM-dd")
            description = self.description_input.text().strip()
            notes = self.notes_input.toPlainText().strip()
            
            # Prepare multipart form data
            data = {
                "entry_type": entry_type,
                "category_id": str(category_id),
                "amount": str(amount),
                "date": date,
                "email": self.user_email,
                "description": description if description else None,
                "notes": notes if notes else None
            }
            
            files = {}
            if self.receipt_path:
                files["receipt"] = open(self.receipt_path, "rb")
            
            # Send request
            response = requests.post(f"{API_URL}/finance/entries", data=data, files=files)
            
            if files:
                files["receipt"].close()
            
            if response.status_code == 200:
                QtWidgets.QMessageBox.information(self, "Success", "Financial entry saved successfully!")
                self.clear_form()
            else:
                error_msg = response.json().get("detail", "Unknown error")
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to save entry: {error_msg}")
        
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def clear_form(self):
        """Clear all form fields"""
        self.amount_input.setValue(0)
        self.description_input.clear()
        self.notes_input.clear()
        self.linked_input.clear()
        self.receipt_path = None
        self.receipt_label.setText("No file selected")
        self.receipt_label.setStyleSheet("color: #588157; font-weight: normal; font-size: 10pt;")
        self.date_edit.setDate(QtCore.QDate.currentDate())
        self.expense_radio.setChecked(True)
        self.amount_error.hide()
    
    def cancel_entry(self):
        """Cancel and clear the form"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Cancel Entry",
            "Are you sure you want to cancel? All unsaved data will be lost.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.clear_form()
