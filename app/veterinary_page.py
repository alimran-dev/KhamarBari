from PyQt5 import QtWidgets, QtCore, QtGui
from datetime import datetime, date, timedelta
import requests
import os


API_BASE_URL = "http://localhost:8000"


class AddVisitDialog(QtWidgets.QDialog):
    """Dialog for adding a new veterinary visit"""
    
    def __init__(self, parent=None, cattle_list=None):
        super().__init__(parent)
        self.setWindowTitle("Add Visit")
        self.setMinimumWidth(600)
        self.setMinimumHeight(650)
        self.cattle_list = cattle_list or []
        
        self.setStyleSheet("""
            QDialog { 
                background-color: #EBEAE3; 
            }
            QLabel { 
                color: #344E41; 
                font-weight: bold; 
                font-size: 11pt; 
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                background-color: white;
                border: 1px solid #A3B18A;
                border-radius: 5px;
                padding: 8px;
                color: #344E41;
                font-size: 10pt;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QPushButton {
                background-color: #344E41;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover { 
                background-color: #588157; 
            }
            QPushButton#cancelButton {
                background-color: #ccc;
                color: #333;
            }
            QPushButton#cancelButton:hover {
                background-color: #bbb;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QtWidgets.QLabel("Add New Visit")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #344E41;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form area with scroll
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll_widget = QtWidgets.QWidget()
        form_layout = QtWidgets.QGridLayout(scroll_widget)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(10, 10, 10, 10)
        
        row = 0
        
        # Animal Tag (searchable dropdown)
        form_layout.addWidget(QtWidgets.QLabel("Animal Tag:"), row, 0)
        self.animal_tag_combo = QtWidgets.QComboBox()
        self.animal_tag_combo.setEditable(True)
        self.animal_tag_combo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.animal_tag_combo.addItem("")
        for cattle in self.cattle_list:
            tag = cattle.get('tag_number', '')
            name = cattle.get('Name', '')
            display = f"{tag} - {name}" if name else tag
            self.animal_tag_combo.addItem(display, tag)
        self.animal_tag_combo.currentIndexChanged.connect(self._on_animal_selected)
        form_layout.addWidget(self.animal_tag_combo, row, 1)
        row += 1
        
        # Animal Name (auto-filled, read-only)
        form_layout.addWidget(QtWidgets.QLabel("Animal Name:"), row, 0)
        self.animal_name_edit = QtWidgets.QLineEdit()
        self.animal_name_edit.setReadOnly(True)
        self.animal_name_edit.setPlaceholderText("Auto-filled from animal selection")
        form_layout.addWidget(self.animal_name_edit, row, 1)
        row += 1
        
        # Visit Date
        form_layout.addWidget(QtWidgets.QLabel("Date:"), row, 0)
        self.date_edit = QtWidgets.QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QtCore.QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        form_layout.addWidget(self.date_edit, row, 1)
        row += 1
        
        # Visit Type
        form_layout.addWidget(QtWidgets.QLabel("Visit Type:"), row, 0)
        self.visit_type_combo = QtWidgets.QComboBox()
        self.visit_type_combo.addItems([
            "Routine Check", "Emergency", "Follow-up", "Vaccination", "Surgery"
        ])
        form_layout.addWidget(self.visit_type_combo, row, 1)
        row += 1
        
        # Vet Name
        form_layout.addWidget(QtWidgets.QLabel("Vet Name:"), row, 0)
        self.vet_name_edit = QtWidgets.QLineEdit()
        self.vet_name_edit.setPlaceholderText("Dr. Rahim")
        form_layout.addWidget(self.vet_name_edit, row, 1)
        row += 1
        
        # Diagnosis
        form_layout.addWidget(QtWidgets.QLabel("Diagnosis:"), row, 0, QtCore.Qt.AlignTop)
        self.diagnosis_edit = QtWidgets.QTextEdit()
        self.diagnosis_edit.setPlaceholderText("Enter diagnosis details...")
        self.diagnosis_edit.setMaximumHeight(80)
        form_layout.addWidget(self.diagnosis_edit, row, 1)
        row += 1
        
        # Treatment
        form_layout.addWidget(QtWidgets.QLabel("Treatment:"), row, 0, QtCore.Qt.AlignTop)
        self.treatment_edit = QtWidgets.QTextEdit()
        self.treatment_edit.setPlaceholderText("Enter treatment details...")
        self.treatment_edit.setMaximumHeight(80)
        form_layout.addWidget(self.treatment_edit, row, 1)
        row += 1
        
        # Medicines Used
        form_layout.addWidget(QtWidgets.QLabel("Medicines Used:"), row, 0)
        self.medicines_edit = QtWidgets.QLineEdit()
        self.medicines_edit.setPlaceholderText("Penicillin, FMD-Vac, ...")
        form_layout.addWidget(self.medicines_edit, row, 1)
        row += 1
        
        # Cost
        form_layout.addWidget(QtWidgets.QLabel("Cost:"), row, 0)
        self.cost_edit = QtWidgets.QLineEdit()
        self.cost_edit.setPlaceholderText("৳ 500")
        self.cost_edit.setText("0")
        form_layout.addWidget(self.cost_edit, row, 1)
        row += 1
        
        # Vet Notes
        form_layout.addWidget(QtWidgets.QLabel("Vet Notes:"), row, 0, QtCore.Qt.AlignTop)
        self.notes_edit = QtWidgets.QTextEdit()
        self.notes_edit.setPlaceholderText("Additional notes...")
        self.notes_edit.setMaximumHeight(60)
        form_layout.addWidget(self.notes_edit, row, 1)
        row += 1
        
        # Next Visit Date (optional)
        form_layout.addWidget(QtWidgets.QLabel("Next Visit Date:"), row, 0)
        next_date_layout = QtWidgets.QHBoxLayout()
        self.next_visit_checkbox = QtWidgets.QCheckBox("Schedule next visit")
        self.next_visit_date_edit = QtWidgets.QDateEdit()
        self.next_visit_date_edit.setCalendarPopup(True)
        self.next_visit_date_edit.setDate(QtCore.QDate.currentDate().addDays(30))
        self.next_visit_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.next_visit_date_edit.setEnabled(False)
        self.next_visit_checkbox.stateChanged.connect(
            lambda state: self.next_visit_date_edit.setEnabled(state == QtCore.Qt.Checked)
        )
        next_date_layout.addWidget(self.next_visit_checkbox)
        next_date_layout.addWidget(self.next_visit_date_edit)
        form_layout.addLayout(next_date_layout, row, 1)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QtWidgets.QPushButton("Save Visit")
        save_btn.clicked.connect(self.save_visit)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def _on_animal_selected(self, index):
        """Auto-fill animal name when tag is selected"""
        if index > 0:
            tag = self.animal_tag_combo.itemData(index)
            # Find the cattle and get the name
            for cattle in self.cattle_list:
                if cattle.get('tag_number') == tag:
                    self.animal_name_edit.setText(cattle.get('Name', ''))
                    break
    
    def save_visit(self):
        """Save the veterinary visit"""
        # Validation
        if self.animal_tag_combo.currentIndex() == 0:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Please select an animal tag")
            return
        
        if not self.vet_name_edit.text().strip():
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Please enter vet name")
            return
        
        try:
            cost = float(self.cost_edit.text() or "0")
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Invalid cost value")
            return
        
        # Get animal tag
        animal_tag = self.animal_tag_combo.itemData(self.animal_tag_combo.currentIndex())
        
        # Prepare data
        visit_data = {
            "animal_tag": animal_tag,
            "animal_name": self.animal_name_edit.text() or None,
            "visit_date": self.date_edit.date().toString("yyyy-MM-dd"),
            "visit_type": self.visit_type_combo.currentText(),
            "vet_name": self.vet_name_edit.text(),
            "diagnosis": self.diagnosis_edit.toPlainText() or None,
            "treatment": self.treatment_edit.toPlainText() or None,
            "medicines_used": self.medicines_edit.text() or None,
            "cost": cost,
            "notes": self.notes_edit.toPlainText() or None,
            "next_visit_date": self.next_visit_date_edit.date().toString("yyyy-MM-dd") 
                               if self.next_visit_checkbox.isChecked() else None
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/veterinary/visits", json=visit_data)
            if response.status_code == 200:
                QtWidgets.QMessageBox.information(self, "Success", "Visit added successfully!")
                self.accept()
            else:
                error_msg = response.json().get("detail", "Unknown error")
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to add visit: {error_msg}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")


class AddTreatmentDialog(QtWidgets.QDialog):
    """Dialog for adding a new treatment"""
    
    def __init__(self, parent=None, cattle_list=None, visit_id=None):
        super().__init__(parent)
        self.setWindowTitle("Add Treatment")
        self.setMinimumWidth(550)
        self.setMinimumHeight(600)
        self.cattle_list = cattle_list or []
        self.visit_id = visit_id
        
        self.setStyleSheet("""
            QDialog { background-color: #EBEAE3; }
            QLabel { color: #344E41; font-weight: bold; font-size: 11pt; }
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                background-color: white;
                border: 1px solid #A3B18A;
                border-radius: 5px;
                padding: 8px;
                color: #344E41;
                font-size: 10pt;
            }
            QPushButton {
                background-color: #344E41;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover { background-color: #588157; }
            QPushButton#cancelButton {
                background-color: #ccc;
                color: #333;
            }
            QPushButton#cancelButton:hover { background-color: #bbb; }
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QtWidgets.QLabel("Add New Treatment")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #344E41;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form
        form_layout = QtWidgets.QGridLayout()
        form_layout.setSpacing(12)
        row = 0
        
        # Animal Tag
        form_layout.addWidget(QtWidgets.QLabel("Animal Tag:"), row, 0)
        self.animal_tag_combo = QtWidgets.QComboBox()
        self.animal_tag_combo.setEditable(True)
        self.animal_tag_combo.addItem("")
        for cattle in self.cattle_list:
            tag = cattle.get('tag_number', '')
            name = cattle.get('Name', '')
            display = f"{tag} - {name}" if name else tag
            self.animal_tag_combo.addItem(display, tag)
        form_layout.addWidget(self.animal_tag_combo, row, 1)
        row += 1
        
        # Treatment Date
        form_layout.addWidget(QtWidgets.QLabel("Date:"), row, 0)
        self.date_edit = QtWidgets.QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QtCore.QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        form_layout.addWidget(self.date_edit, row, 1)
        row += 1
        
        # Diagnosis
        form_layout.addWidget(QtWidgets.QLabel("Diagnosis:"), row, 0)
        self.diagnosis_edit = QtWidgets.QLineEdit()
        self.diagnosis_edit.setPlaceholderText("FMD, Mastitis, etc.")
        form_layout.addWidget(self.diagnosis_edit, row, 1)
        row += 1
        
        # Treatment Description
        form_layout.addWidget(QtWidgets.QLabel("Treatment:"), row, 0, QtCore.Qt.AlignTop)
        self.treatment_edit = QtWidgets.QTextEdit()
        self.treatment_edit.setPlaceholderText("Treatment description...")
        self.treatment_edit.setMaximumHeight(100)
        form_layout.addWidget(self.treatment_edit, row, 1)
        row += 1
        
        # Medicines Used
        form_layout.addWidget(QtWidgets.QLabel("Medicines:"), row, 0)
        self.medicines_edit = QtWidgets.QLineEdit()
        self.medicines_edit.setPlaceholderText("Medicine names")
        form_layout.addWidget(self.medicines_edit, row, 1)
        row += 1
        
        # Dosage
        form_layout.addWidget(QtWidgets.QLabel("Dosage:"), row, 0)
        self.dosage_edit = QtWidgets.QLineEdit()
        self.dosage_edit.setPlaceholderText("e.g., 10ml twice daily")
        form_layout.addWidget(self.dosage_edit, row, 1)
        row += 1
        
        # Duration
        form_layout.addWidget(QtWidgets.QLabel("Duration (days):"), row, 0)
        self.duration_edit = QtWidgets.QLineEdit()
        self.duration_edit.setPlaceholderText("e.g., 7")
        form_layout.addWidget(self.duration_edit, row, 1)
        row += 1
        
        # Cost
        form_layout.addWidget(QtWidgets.QLabel("Cost:"), row, 0)
        self.cost_edit = QtWidgets.QLineEdit()
        self.cost_edit.setText("0")
        form_layout.addWidget(self.cost_edit, row, 1)
        row += 1
        
        # Vet Name
        form_layout.addWidget(QtWidgets.QLabel("Vet Name:"), row, 0)
        self.vet_name_edit = QtWidgets.QLineEdit()
        form_layout.addWidget(self.vet_name_edit, row, 1)
        row += 1
        
        # Notes
        form_layout.addWidget(QtWidgets.QLabel("Notes:"), row, 0, QtCore.Qt.AlignTop)
        self.notes_edit = QtWidgets.QTextEdit()
        self.notes_edit.setMaximumHeight(70)
        form_layout.addWidget(self.notes_edit, row, 1)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QtWidgets.QPushButton("Save Treatment")
        save_btn.clicked.connect(self.save_treatment)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def save_treatment(self):
        """Save the treatment"""
        if self.animal_tag_combo.currentIndex() == 0:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Please select an animal tag")
            return
        
        if not self.treatment_edit.toPlainText().strip():
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Please enter treatment description")
            return
        
        try:
            cost = float(self.cost_edit.text() or "0")
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Invalid cost value")
            return
        
        animal_tag = self.animal_tag_combo.itemData(self.animal_tag_combo.currentIndex())
        
        treatment_data = {
            "visit_id": self.visit_id,
            "animal_tag": animal_tag,
            "treatment_date": self.date_edit.date().toString("yyyy-MM-dd"),
            "diagnosis": self.diagnosis_edit.text() or None,
            "treatment_description": self.treatment_edit.toPlainText(),
            "medicines_used": self.medicines_edit.text() or None,
            "dosage": self.dosage_edit.text() or None,
            "duration_days": int(self.duration_edit.text()) if self.duration_edit.text() else None,
            "cost": cost,
            "vet_name": self.vet_name_edit.text() or None,
            "notes": self.notes_edit.toPlainText() or None
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/veterinary/treatments", json=treatment_data)
            if response.status_code == 200:
                QtWidgets.QMessageBox.information(self, "Success", "Treatment added successfully!")
                self.accept()
            else:
                error_msg = response.json().get("detail", "Unknown error")
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to add treatment: {error_msg}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")


class VeterinaryPage(QtWidgets.QWidget):
    """Main Veterinary Page"""
    
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
    
    def __init__(self):
        super().__init__()
        self.cattle_list = []
        self.medical_history = []
        self.upcoming_visits = []
        
        # Main layout
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)
        
        # Left panel (Medical History & Actions)
        left_panel = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # Header with buttons
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(10)
        
        # Add Visit Button
        self.btn_add_visit = QtWidgets.QPushButton()
        self.btn_add_visit.setIcon(self._create_icon_with_plus())
        self.btn_add_visit.setText("Add Visit")
        self.btn_add_visit.setIconSize(QtCore.QSize(20, 20))
        self.btn_add_visit.setFixedHeight(45)
        self.btn_add_visit.setStyleSheet("""
            QPushButton {
                background-color: #344E41;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #588157;
            }
        """)
        self.btn_add_visit.clicked.connect(self.add_visit)
        header_layout.addWidget(self.btn_add_visit)
        
        # Add Treatment Button
        self.btn_add_treatment = QtWidgets.QPushButton()
        self.btn_add_treatment.setIcon(self._create_icon_with_plus())
        self.btn_add_treatment.setText("Add Treatment")
        self.btn_add_treatment.setIconSize(QtCore.QSize(20, 20))
        self.btn_add_treatment.setFixedHeight(45)
        self.btn_add_treatment.setStyleSheet("""
            QPushButton {
                background-color: #344E41;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #588157;
            }
        """)
        self.btn_add_treatment.clicked.connect(self.add_treatment)
        header_layout.addWidget(self.btn_add_treatment)
        
        header_layout.addStretch()
        left_layout.addLayout(header_layout)
        
        # Medical History Section
        history_label = QtWidgets.QLabel("Medical History")
        history_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #344E41; margin-bottom: 10px;")
        left_layout.addWidget(history_label)
        
        # Filter section
        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.setSpacing(10)
        
        # Disease filter dropdown
        filter_layout.addWidget(QtWidgets.QLabel("All Diseases"))
        self.disease_filter = QtWidgets.QComboBox()
        self.disease_filter.addItems(["All", "FMD", "Mastitis", "Bloat", "Pneumonia", "Other"])
        self.disease_filter.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #A3B18A;
                border-radius: 5px;
                padding: 5px 10px;
                min-width: 150px;
            }
        """)
        self.disease_filter.currentTextChanged.connect(self.filter_medical_history)
        filter_layout.addWidget(self.disease_filter)
        
        # Search by animal tag
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("Search by animal tag, vet name...")
        self.search_edit.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #A3B18A;
                border-radius: 5px;
                padding: 5px 10px;
            }
        """)
        self.search_edit.textChanged.connect(self.filter_medical_history)
        filter_layout.addWidget(self.search_edit)
        
        left_layout.addLayout(filter_layout)
        
        # Medical History Table
        self.history_table = QtWidgets.QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Date", "Animal Tag", "Diagnosis", "Treatment", "Vet Name", "Cost"
        ])
        self.history_table.horizontalHeader().setStretchLastSection(False)
        self.history_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        self.history_table.setColumnWidth(0, 100)
        self.history_table.setColumnWidth(1, 100)
        self.history_table.setColumnWidth(2, 150)
        self.history_table.setColumnWidth(3, 150)
        self.history_table.setColumnWidth(4, 120)
        self.history_table.setColumnWidth(5, 80)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #A3B18A;
                border-radius: 10px;
                gridline-color: #d0d0d0;
            }
            QHeaderView::section {
                background-color: #344E41;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #A3B18A;
                color: white;
            }
        """ + self.SCROLLBAR_STYLESHEET)
        
        # Context menu for table
        self.history_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.history_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Double click to view details
        self.history_table.doubleClicked.connect(self.view_cattle_profile)
        
        left_layout.addWidget(self.history_table)
        
        # Vet Cost Summary
        cost_layout = QtWidgets.QHBoxLayout()
        cost_layout.setSpacing(20)
        
        self.monthly_cost_label = QtWidgets.QLabel("Monthly Vet Costs")
        self.monthly_cost_label.setWordWrap(True)
        self.monthly_cost_label.setAlignment(QtCore.Qt.AlignCenter)
        self.monthly_cost_label.setStyleSheet("""
            QLabel {
                background-color: #A3B18A;
                color: #344E41;
                border-radius: 10px;
                padding: 15px;
                font-size: 11pt;
                font-weight: bold;
            }
        """)
        cost_layout.addWidget(self.monthly_cost_label)
        
        self.most_common_disease_label = QtWidgets.QLabel("Most Common Diseases")
        self.most_common_disease_label.setWordWrap(True)
        self.most_common_disease_label.setAlignment(QtCore.Qt.AlignCenter)
        self.most_common_disease_label.setStyleSheet("""
            QLabel {
                background-color: #588157;
                color: white;
                border-radius: 10px;
                padding: 15px;
                font-size: 11pt;
                font-weight: bold;
            }
        """)
        cost_layout.addWidget(self.most_common_disease_label)
        
        left_layout.addLayout(cost_layout)
        
        main_layout.addWidget(left_panel, 7)
        
        # Right panel (Vaccination Scheduler)
        right_panel = QtWidgets.QWidget()
        right_panel.setMinimumWidth(320)
        right_panel.setMaximumWidth(400)
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # Vaccination Scheduler Header
        scheduler_header = QtWidgets.QLabel("Vaccination Scheduler &\nUpcoming Visits")
        scheduler_header.setWordWrap(True)
        scheduler_header.setStyleSheet("""
            QLabel {
                background-color: #344E41;
                color: white;
                border-radius: 10px;
                padding: 12px 10px;
                font-size: 12pt;
                font-weight: bold;
            }
        """)
        scheduler_header.setAlignment(QtCore.Qt.AlignCenter)
        scheduler_header.setMaximumHeight(80)
        right_layout.addWidget(scheduler_header)
        
        # Upcoming list label
        upcoming_label = QtWidgets.QLabel("Upcoming Events")
        upcoming_label.setStyleSheet("font-size: 10pt; font-weight: bold; color: #344E41; padding: 5px 0;")
        right_layout.addWidget(upcoming_label)
        
        # Upcoming visits scroll area
        self.upcoming_scroll = QtWidgets.QScrollArea()
        self.upcoming_scroll.setWidgetResizable(True)
        self.upcoming_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.upcoming_scroll.setStyleSheet("QScrollArea { background-color: transparent; }" + self.SCROLLBAR_STYLESHEET)
        
        self.upcoming_container = QtWidgets.QWidget()
        self.upcoming_layout = QtWidgets.QVBoxLayout(self.upcoming_container)
        self.upcoming_layout.setSpacing(10)
        self.upcoming_layout.setContentsMargins(0, 0, 0, 0)
        self.upcoming_layout.setAlignment(QtCore.Qt.AlignTop)
        
        self.upcoming_scroll.setWidget(self.upcoming_container)
        right_layout.addWidget(self.upcoming_scroll)
        
        # View Full Calendar button
        self.btn_view_calendar = QtWidgets.QPushButton("View Full Calendar")
        self.btn_view_calendar.setFixedHeight(38)
        self.btn_view_calendar.setStyleSheet("""
            QPushButton {
                background-color: #588157;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #344E41;
            }
        """)
        self.btn_view_calendar.clicked.connect(self.view_full_calendar)
        right_layout.addWidget(self.btn_view_calendar)
        
        main_layout.addWidget(right_panel, 3)
        
        # Load initial data
        self.load_cattle_list()
        self.load_medical_history()
        self.load_upcoming_visits()
        self.update_statistics()
    
    def _create_icon_with_plus(self):
        """Create a simple plus icon"""
        pixmap = QtGui.QPixmap(20, 20)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setPen(QtGui.QPen(QtGui.QColor("white"), 2))
        painter.drawLine(10, 5, 10, 15)
        painter.drawLine(5, 10, 15, 10)
        painter.end()
        return QtGui.QIcon(pixmap)
    
    def load_cattle_list(self):
        """Load cattle list from API"""
        try:
            response = requests.get(f"{API_BASE_URL}/cattle")
            if response.status_code == 200:
                data = response.json()
                self.cattle_list = data.get('data', [])
        except Exception as e:
            print(f"Error loading cattle list: {e}")
    
    def load_medical_history(self):
        """Load medical history from API"""
        try:
            response = requests.get(f"{API_BASE_URL}/veterinary/visits?limit=200")
            if response.status_code == 200:
                data = response.json()
                self.medical_history = data.get('data', [])
                self.populate_history_table()
        except Exception as e:
            print(f"Error loading medical history: {e}")
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to load medical history: {str(e)}")
    
    def populate_history_table(self, filtered_data=None):
        """Populate the medical history table"""
        data = filtered_data if filtered_data is not None else self.medical_history
        
        self.history_table.setRowCount(0)
        
        for record in data:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            # Date
            date_item = QtWidgets.QTableWidgetItem(record.get('visit_date', ''))
            date_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.history_table.setItem(row, 0, date_item)
            
            # Animal Tag
            tag_item = QtWidgets.QTableWidgetItem(record.get('animal_tag', ''))
            tag_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.history_table.setItem(row, 1, tag_item)
            
            # Diagnosis
            diagnosis = record.get('diagnosis', '') or '-'
            self.history_table.setItem(row, 2, QtWidgets.QTableWidgetItem(diagnosis))
            
            # Treatment
            treatment = record.get('treatment', '') or '-'
            self.history_table.setItem(row, 3, QtWidgets.QTableWidgetItem(treatment))
            
            # Vet Name
            vet_item = QtWidgets.QTableWidgetItem(record.get('vet_name', ''))
            self.history_table.setItem(row, 4, vet_item)
            
            # Cost
            cost = record.get('cost', 0)
            cost_item = QtWidgets.QTableWidgetItem(f"৳{cost:.0f}")
            cost_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.history_table.setItem(row, 5, cost_item)
            
            # Store full record data in first column
            date_item.setData(QtCore.Qt.UserRole, record)
    
    def filter_medical_history(self):
        """Filter medical history based on search and disease filter"""
        search_text = self.search_edit.text().lower()
        disease_filter = self.disease_filter.currentText()
        
        filtered = []
        for record in self.medical_history:
            # Disease filter
            if disease_filter != "All":
                diagnosis = (record.get('diagnosis', '') or '').lower()
                if disease_filter.lower() not in diagnosis:
                    continue
            
            # Search filter
            if search_text:
                searchable = f"{record.get('animal_tag', '')} {record.get('vet_name', '')} {record.get('diagnosis', '')}".lower()
                if search_text not in searchable:
                    continue
            
            filtered.append(record)
        
        self.populate_history_table(filtered)
    
    def load_upcoming_visits(self):
        """Load upcoming vaccination schedules and visits from calendar"""
        try:
            # Clear existing widgets
            while self.upcoming_layout.count():
                child = self.upcoming_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            all_events = []
            
            # Load vaccination and vet visit events from calendar
            try:
                response = requests.get(f"{API_BASE_URL}/calendar/upcoming", params={"days": 30, "limit": 50})
                if response.status_code == 200:
                    calendar_data = response.json()
                    calendar_events = calendar_data.get('data', [])
                    
                    # Filter for Vaccination and Vet Visit types
                    for event in calendar_events:
                        event_type = event.get('event_type', '')
                        if event_type in ['Vaccination', 'Vet Visit']:
                            # Convert calendar event to display format
                            all_events.append({
                                'scheduled_date': event.get('event_date', ''),
                                'event_time': event.get('event_time', ''),
                                'vaccine_name': event.get('title', 'Event'),
                                'animal_tag': event.get('related_animals', 'N/A'),
                                'animal_name': '',
                                'event_type': event_type,
                                'notes': event.get('notes', ''),
                                'assigned_person': event.get('assigned_person', ''),
                                'status': event.get('status', 'Scheduled'),
                                'source': 'calendar'
                            })
            except Exception as e:
                print(f"Error loading calendar events: {e}")
            
            # Load vaccination schedules from veterinary module
            try:
                response = requests.get(f"{API_BASE_URL}/veterinary/vaccination-schedule?upcoming=true")
                if response.status_code == 200:
                    data = response.json()
                    schedules = data.get('data', [])
                    for schedule in schedules:
                        schedule['event_type'] = 'Vaccination'
                        schedule['source'] = 'veterinary'
                        all_events.append(schedule)
            except Exception as e:
                print(f"Error loading vaccination schedules: {e}")
            
            # Sort by date
            all_events.sort(key=lambda x: (x.get('scheduled_date', '9999-99-99'), x.get('event_time', '23:59:59')))
            
            if not all_events:
                no_data_label = QtWidgets.QLabel("No upcoming events")
                no_data_label.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
                no_data_label.setAlignment(QtCore.Qt.AlignCenter)
                self.upcoming_layout.addWidget(no_data_label)
            else:
                for event in all_events[:15]:  # Show max 15
                    card = self._create_upcoming_card(event)
                    self.upcoming_layout.addWidget(card)
            
            self.upcoming_layout.addStretch()
        except Exception as e:
            print(f"Error loading upcoming visits: {e}")
    
    def _create_upcoming_card(self, schedule):
        """Create a card widget for upcoming vaccination or vet visit"""
        card = QtWidgets.QFrame()
        
        # Different color based on event type
        event_type = schedule.get('event_type', 'Vaccination')
        if event_type == 'Vet Visit':
            border_color = "#dc3545"  # Red for vet visits
        else:
            border_color = "#A3B18A"  # Green for vaccinations
        
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {border_color};
                border-left: 4px solid {border_color};
                border-radius: 8px;
            }}
        """)
        card.setMinimumHeight(100)
        card.setMaximumHeight(130)
        
        layout = QtWidgets.QVBoxLayout(card)
        layout.setSpacing(4)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Date badge
        date_str = schedule.get('scheduled_date', '')
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day = date_obj.strftime('%d')
            month = date_obj.strftime('%b')
            weekday = date_obj.strftime('%a')
            
            date_layout = QtWidgets.QHBoxLayout()
            
            # Event type badge color
            badge_color = "#dc3545" if event_type == "Vet Visit" else "#344E41"
            
            date_badge = QtWidgets.QLabel(f"{weekday}\n{month}\n{day}")
            date_badge.setAlignment(QtCore.Qt.AlignCenter)
            date_badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {badge_color};
                    color: white;
                    border-radius: 5px;
                    padding: 3px;
                    font-weight: bold;
                    font-size: 9pt;
                    line-height: 1.1;
                }}
            """)
            date_badge.setFixedSize(45, 55)
            date_layout.addWidget(date_badge)
            
            info_layout = QtWidgets.QVBoxLayout()
            info_layout.setSpacing(2)
            info_layout.setContentsMargins(8, 0, 0, 0)
            
            # Event title with type indicator
            event_time = schedule.get('event_time', '')
            time_str = f" ({event_time[:5]})" if event_time else ""
            title_text = f"{schedule.get('vaccine_name', 'Event')}{time_str}"
            
            vaccine_label = QtWidgets.QLabel(title_text)
            vaccine_label.setWordWrap(True)
            vaccine_label.setStyleSheet("font-weight: bold; font-size: 10pt; color: #344E41;")
            vaccine_label.setMaximumHeight(40)
            info_layout.addWidget(vaccine_label)
            
            # Type badge
            type_badge = QtWidgets.QLabel(f"📌 {event_type}")
            type_badge.setStyleSheet(f"font-size: 7.5pt; color: {badge_color}; font-weight: bold;")
            info_layout.addWidget(type_badge)
            
            # Animal info
            animal_tag = schedule.get('animal_tag', '')
            animal_name = schedule.get('animal_name', '')
            assigned = schedule.get('assigned_person', '')
            
            if animal_tag or animal_name:
                animal_text = f"{animal_tag}"
                if animal_name:
                    animal_text += f" - {animal_name}"
                animal_label = QtWidgets.QLabel(animal_text)
                animal_label.setWordWrap(True)
                animal_label.setStyleSheet("font-size: 8.5pt; color: #666;")
                animal_label.setMaximumHeight(30)
                info_layout.addWidget(animal_label)
            elif assigned:
                assigned_label = QtWidgets.QLabel(f"👤 {assigned}")
                assigned_label.setWordWrap(True)
                assigned_label.setStyleSheet("font-size: 8.5pt; color: #666;")
                assigned_label.setMaximumHeight(30)
                info_layout.addWidget(assigned_label)
            
            # Days until
            days_until = (date_obj.date() - date.today()).days
            if days_until == 0:
                due_text = "Due Today!"
                color = "#d32f2f"
            elif days_until < 0:
                due_text = f"Overdue {abs(days_until)}d"
                color = "#d32f2f"
            elif days_until <= 7:
                due_text = f"In {days_until} day{'s' if days_until > 1 else ''}"
                color = "#ff9800"
            else:
                due_text = f"In {days_until} days"
                color = "#666"
            
            due_label = QtWidgets.QLabel(due_text)
            due_label.setWordWrap(False)
            due_label.setStyleSheet(f"font-size: 8pt; color: {color}; font-weight: bold;")
            info_layout.addWidget(due_label)
            
            date_layout.addLayout(info_layout)
            date_layout.addStretch()
            
            layout.addLayout(date_layout)
            
        except Exception as e:
            layout.addWidget(QtWidgets.QLabel(f"Error: {str(e)}"))
        
        return card
    
    def update_statistics(self):
        """Update cost and disease statistics"""
        try:
            response = requests.get(f"{API_BASE_URL}/veterinary/summary")
            if response.status_code == 200:
                data = response.json().get('data', {})
                total_cost = data.get('total_cost', 0)
                
                # Update monthly cost (approximate from total)
                self.monthly_cost_label.setText(f"Monthly Vet Costs\n৳{total_cost:,.0f}")
            
            # Calculate most common disease
            disease_count = {}
            for record in self.medical_history:
                diagnosis = record.get('diagnosis', '')
                if diagnosis:
                    diseases = [d.strip() for d in diagnosis.split(',')]
                    for disease in diseases:
                        disease_count[disease] = disease_count.get(disease, 0) + 1
            
            if disease_count:
                most_common = max(disease_count, key=disease_count.get)
                count = disease_count[most_common]
                self.most_common_disease_label.setText(f"Most Common Diseases\n{most_common} ({count})")
            else:
                self.most_common_disease_label.setText("Most Common Diseases\nNo data")
                
        except Exception as e:
            print(f"Error updating statistics: {e}")
    
    def add_visit(self):
        """Open add visit dialog"""
        dialog = AddVisitDialog(self, self.cattle_list)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.load_medical_history()
            self.update_statistics()
    
    def add_treatment(self):
        """Open add treatment dialog"""
        dialog = AddTreatmentDialog(self, self.cattle_list)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            # Treatments are separate, but we can reload history if needed
            QtWidgets.QMessageBox.information(self, "Success", "Treatment added successfully!")
    
    def show_context_menu(self, position):
        """Show context menu for table row"""
        menu = QtWidgets.QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #A3B18A;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #A3B18A;
            }
        """)
        
        view_action = menu.addAction("View Cattle Profile")
        delete_action = menu.addAction("Delete Record")
        
        action = menu.exec_(self.history_table.viewport().mapToGlobal(position))
        
        if action == view_action:
            self.view_cattle_profile()
        elif action == delete_action:
            self.delete_record()
    
    def view_cattle_profile(self):
        """View cattle profile from selected row"""
        current_row = self.history_table.currentRow()
        if current_row < 0:
            return
        
        record = self.history_table.item(current_row, 0).data(QtCore.Qt.UserRole)
        animal_tag = record.get('animal_tag', '')
        
        QtWidgets.QMessageBox.information(
            self, 
            "Cattle Profile", 
            f"Opening profile for {animal_tag}\n\n(This would navigate to cattle details page)"
        )
    
    def delete_record(self):
        """Delete selected medical history record"""
        current_row = self.history_table.currentRow()
        if current_row < 0:
            return
        
        record = self.history_table.item(current_row, 0).data(QtCore.Qt.UserRole)
        visit_id = record.get('id')
        
        reply = QtWidgets.QMessageBox.question(
            self, 
            'Confirm Delete',
            f"Are you sure you want to delete this visit record?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                response = requests.delete(f"{API_BASE_URL}/veterinary/visits/{visit_id}")
                if response.status_code == 200:
                    QtWidgets.QMessageBox.information(self, "Success", "Record deleted successfully!")
                    self.load_medical_history()
                    self.update_statistics()
                else:
                    QtWidgets.QMessageBox.warning(self, "Error", "Failed to delete record")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")
    
    def view_full_calendar(self):
        """View full vaccination calendar"""
        QtWidgets.QMessageBox.information(
            self, 
            "Calendar", 
            "Full calendar view would open here\nShowing all scheduled vaccinations and visits"
        )


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = VeterinaryPage()
    window.show()
    sys.exit(app.exec_())
