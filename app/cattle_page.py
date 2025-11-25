from PyQt5 import QtWidgets, QtCore, QtGui
import requests

import json

class VaccinationDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Vaccination / Medical History")
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog { background-color: #EBEAE3; }
            QLabel { color: #344E41; font-weight: bold; font-size: 11pt; }
            QLineEdit, QDateEdit, QTextEdit {
                background-color: #D8E2D1;
                border: 1px solid #A3B18A;
                border-radius: 5px;
                padding: 8px;
                color: #344E41;
            }
            QPushButton {
                background-color: #344E41;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #4A6A55; }
            QTableWidget {
                background-color: white;
                border: 1px solid #A3B18A;
                gridline-color: #A3B18A;
            }
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
            QHeaderView::section {
                background-color: #344E41;
                color: white;
                padding: 5px;
            }
        """)
        
        self.history_data = []
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Form Area
        form_group = QtWidgets.QGroupBox("New Entry")
        form_layout = QtWidgets.QGridLayout(form_group)
        
        form_layout.addWidget(QtWidgets.QLabel("Date:"), 0, 0)
        self.date_edit = QtWidgets.QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QtCore.QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        form_layout.addWidget(self.date_edit, 0, 1)
        
        form_layout.addWidget(QtWidgets.QLabel("Name (Vaccine/Medicine):"), 1, 0)
        self.name_edit = QtWidgets.QLineEdit()
        form_layout.addWidget(self.name_edit, 1, 1)
        
        form_layout.addWidget(QtWidgets.QLabel("Diagnosis/Notes:"), 2, 0)
        self.diagnosis_edit = QtWidgets.QLineEdit()
        form_layout.addWidget(self.diagnosis_edit, 2, 1)
        
        self.btn_add = QtWidgets.QPushButton("Add Entry")
        self.btn_add.clicked.connect(self.add_entry)
        form_layout.addWidget(self.btn_add, 3, 1, alignment=QtCore.Qt.AlignRight)
        
        layout.addWidget(form_group)
        
        # List Area
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Date", "Name", "Diagnosis"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        # Dialog Buttons
        btn_box = QtWidgets.QHBoxLayout()
        self.btn_done = QtWidgets.QPushButton("Done")
        self.btn_done.clicked.connect(self.accept)
        btn_box.addStretch()
        btn_box.addWidget(self.btn_done)
        
        layout.addLayout(btn_box)

    def add_entry(self):
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        name = self.name_edit.text().strip()
        diagnosis = self.diagnosis_edit.text().strip()
        
        if not name:
            QtWidgets.QMessageBox.warning(self, "Warning", "Name is required.")
            return
            
        # Add to data list
        self.history_data.append({
            "date": date_str,
            "name": name,
            "diagnosis": diagnosis
        })
        
        # Add to table
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(date_str))
        self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(name))
        self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(diagnosis))
        
        # Clear inputs
        self.name_edit.clear()
        self.diagnosis_edit.clear()
        self.name_edit.setFocus()

    def get_data(self):
        return self.history_data


class CattleCard(QtWidgets.QFrame):
    def __init__(self, data):
        super().__init__()
        self.setFixedSize(250, 300)
        self.setStyleSheet("""
            QFrame {
                background-color: #A3B18A;
                border-radius: 20px;
            }
            QLabel {
                color: #344E41;
                font-weight: bold;
                background: transparent;
            }
            QPushButton {
                background-color: #344E41;
                color: white;
                border-radius: 10px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2A3E33;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        # Image
        self.image_label = QtWidgets.QLabel()
        self.image_label.setFixedSize(220, 140)
        self.image_label.setStyleSheet("background-color: #D3D3D3; border-radius: 10px;")
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setScaledContents(True)
        
        # Load Image
        if data.get("photo_path"):
            # Construct URL: http://localhost:8000/ + path
            # Note: photo_path in DB is like "uploads/C-123/img.jpg"
            # API mount is at /uploads
            # So http://localhost:8000/uploads/C-123/img.jpg works if mount is correct
            image_url = f"http://localhost:8000/{data['photo_path']}"
            self._load_image_from_url(image_url)
        else:
            self.image_label.setText("No Image")
            
        layout.addWidget(self.image_label, alignment=QtCore.Qt.AlignHCenter)
        
        # Info
        layout.addSpacing(5)
        
        id_label = QtWidgets.QLabel(f"ID: {data.get('tag_number', 'N/A')}")
        id_label.setAlignment(QtCore.Qt.AlignCenter)
        id_label.setStyleSheet("font-size: 10pt;")
        layout.addWidget(id_label)
        
        breed_label = QtWidgets.QLabel(f"Breed: {data.get('breed', 'N/A')}")
        breed_label.setAlignment(QtCore.Qt.AlignCenter)
        breed_label.setStyleSheet("font-size: 10pt;")
        layout.addWidget(breed_label)
        
        weight_label = QtWidgets.QLabel(f"Weight: {data.get('current_weight', 0)} kg")
        weight_label.setAlignment(QtCore.Qt.AlignCenter)
        weight_label.setStyleSheet("font-size: 10pt;")
        layout.addWidget(weight_label)
        
        # Condition (using health notes as proxy or just static for now)
        condition = "Well" # Logic to derive condition can be added
        cond_label = QtWidgets.QLabel(f"Condition: {condition}")
        cond_label.setAlignment(QtCore.Qt.AlignCenter)
        cond_label.setStyleSheet("font-size: 10pt;")
        layout.addWidget(cond_label)
        
        layout.addStretch()
        
        # Details Button
        self.btn_details = QtWidgets.QPushButton("Details")
        self.btn_details.setCursor(QtCore.Qt.PointingHandCursor)
        layout.addWidget(self.btn_details)

    def _load_image_from_url(self, url):
        # Run in a separate thread to avoid freezing UI? 
        # For simplicity, using simple request here, but ideally use QNetworkAccessManager
        try:
            import requests
            response = requests.get(url)
            if response.status_code == 200:
                pixmap = QtGui.QPixmap()
                pixmap.loadFromData(response.content)
                self.image_label.setPixmap(pixmap)
        except:
            self.image_label.setText("Error")


class CattlePage(QtWidgets.QWidget):
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
        self.medical_history = [] # Store history here

        
        # Main Layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(30, 20, 30, 30) # Reduced top margin
        self.layout.setSpacing(15)

        # --- 1. Custom Tab Bar ---
        self.tab_container = QtWidgets.QWidget()
        self.tab_layout = QtWidgets.QHBoxLayout(self.tab_container)
        self.tab_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_layout.setSpacing(0)
        self.tab_layout.setAlignment(QtCore.Qt.AlignHCenter)

        # Tab Buttons
        self.btn_add = self._create_tab_button("Add", position="left")
        self.btn_view = self._create_tab_button("View", position="center")
        self.btn_archive = self._create_tab_button("Archive", position="right")

        self.tabs = [self.btn_add, self.btn_view, self.btn_archive]
        
        for btn in self.tabs:
            self.tab_layout.addWidget(btn)
            # Use a separate method for connection to avoid lambda closure issues
            btn.clicked.connect(self._handle_tab_click)

        self.layout.addWidget(self.tab_container)

        # --- 2. Content Stack ---
        self.stack = QtWidgets.QStackedWidget()
        self.layout.addWidget(self.stack)

        # --- 3. Add Page Content ---
        self.add_page = self._create_add_page()
        self.stack.addWidget(self.add_page)
        
        # Placeholders
        self.view_page = QtWidgets.QLabel("View Records (Coming Soon)")
        self.view_page.setAlignment(QtCore.Qt.AlignCenter)
        self.stack.addWidget(self.view_page)
        
        self.archive_page = QtWidgets.QLabel("Archive (Coming Soon)")
        self.archive_page.setAlignment(QtCore.Qt.AlignCenter)
        self.stack.addWidget(self.archive_page)

        # Set initial state
        self._update_tab_styles(self.btn_add)

    def _create_tab_button(self, text, position="center"):
        btn = QtWidgets.QPushButton(text)
        btn.setFixedSize(150, 50)
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        btn.setProperty("tab_pos", position) # Store position for styling
        return btn

    def _handle_tab_click(self):
        sender = self.sender()
        self._update_tab_styles(sender)
        
        if sender == self.btn_add:
            self.stack.setCurrentIndex(0)
        elif sender == self.btn_view:
            self.stack.setCurrentIndex(1)
        elif sender == self.btn_archive:
            self.stack.setCurrentIndex(2)

    def _update_tab_styles(self, active_btn):
        base_style = """
            QPushButton {
                font-family: 'Amaranth';
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
                font-family: 'Amaranth';
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
            
            # Determine which base style to use
            style = active_style if btn == active_btn else base_style
            
            # Add radius based on position
            if pos == "left":
                style += "QPushButton { border-top-left-radius: 10px; border-bottom-left-radius: 10px; }"
            elif pos == "right":
                style += "QPushButton { border-top-right-radius: 10px; border-bottom-right-radius: 10px; }"
                
            btn.setStyleSheet(style)

    def _create_add_page(self):
        page = QtWidgets.QWidget()
        
        # Card Container
        card = QtWidgets.QFrame(page)
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(15)
        
        # Style the card
        card.setStyleSheet("""
            QFrame {
                background-color: #EBEAE3; 
                border: 1px solid #B5C9A9;
                border-radius: 20px;
            }
            QLabel {
                color: #344E41;
                font-size: 11pt;
                font-weight: bold;
                border: none;
                background: transparent;
            }
            QLineEdit, QDateEdit, QTextEdit {
                background-color: #D8E2D1;
                border: 1px solid #A3B18A;
                border-radius: 8px;
                padding: 8px;
                font-size: 11pt;
                color: #344E41;
            }
            QComboBox {
                background-color: #D8E2D1;
                border: 1px solid #A3B18A;
                border-radius: 8px;
                padding: 8px;
                font-size: 11pt;
                color: #344E41;
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
            }
        """)

        # Title
        title_layout = QtWidgets.QHBoxLayout()
        icon_label = QtWidgets.QLabel("+") 
        icon_label.setStyleSheet("font-size: 24pt; font-weight: 900; color: #344E41;")
        title_label = QtWidgets.QLabel("Add New Cattle Record")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #344E41;")
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        card_layout.addLayout(title_layout)
        card_layout.addSpacing(5)

        # Form Grid
        form_grid = QtWidgets.QGridLayout()
        form_grid.setSpacing(15)
        
        # --- Row 1 ---
        # Name (Full width or half?) - Let's put Name and Breed on top
        form_grid.addWidget(QtWidgets.QLabel("Name"), 0, 0)
        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("Cattle Name")
        form_grid.addWidget(self.name_input, 1, 0)

        # Breed
        form_grid.addWidget(QtWidgets.QLabel("Breed"), 0, 1)
        self.breed_input = QtWidgets.QComboBox()
        self.breed_input.addItems(["Select Breed", "Holstein", "Jersey", "Sahiwal", "Red Chittagong", "Brahman", "Other"])
        form_grid.addWidget(self.breed_input, 1, 1)

        # --- Row 2 ---
        # Purpose
        form_grid.addWidget(QtWidgets.QLabel("Purpose"), 2, 0)
        self.purpose_input = QtWidgets.QComboBox()
        self.purpose_input.addItems(["Select Purpose", "Dairy", "Meat (Fattening)", "Breeding", "Draft"])
        form_grid.addWidget(self.purpose_input, 3, 0)

        # Gender
        form_grid.addWidget(QtWidgets.QLabel("Gender"), 2, 1)
        self.gender_input = QtWidgets.QComboBox()
        self.gender_input.addItems(["Select Gender", "Male", "Female"])
        form_grid.addWidget(self.gender_input, 3, 1)

        # --- Row 3 ---
        # DOB
        form_grid.addWidget(QtWidgets.QLabel("Date of Birth"), 4, 0)
        self.dob_input = QtWidgets.QDateEdit()
        self.dob_input.setDisplayFormat("yyyy-MM-dd")
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDate(QtCore.QDate.currentDate())
        form_grid.addWidget(self.dob_input, 5, 0)

        # Entry Date
        form_grid.addWidget(QtWidgets.QLabel("Date of Entry"), 4, 1)
        self.entry_input = QtWidgets.QDateEdit()
        self.entry_input.setDisplayFormat("yyyy-MM-dd")
        self.entry_input.setCalendarPopup(True)
        self.entry_input.setDate(QtCore.QDate.currentDate())
        form_grid.addWidget(self.entry_input, 5, 1)

        # --- Row 4 ---
        # Weights (Aligned properly now)
        form_grid.addWidget(QtWidgets.QLabel("Initial Weight (kg)"), 6, 0)
        self.initial_weight_input = QtWidgets.QLineEdit()
        self.initial_weight_input.setPlaceholderText("0.0")
        self.initial_weight_input.setValidator(QtGui.QDoubleValidator())
        form_grid.addWidget(self.initial_weight_input, 7, 0)

        form_grid.addWidget(QtWidgets.QLabel("Current Weight (kg)"), 6, 1)
        self.current_weight_input = QtWidgets.QLineEdit()
        self.current_weight_input.setPlaceholderText("0.0")
        self.current_weight_input.setValidator(QtGui.QDoubleValidator())
        form_grid.addWidget(self.current_weight_input, 7, 1)

        # --- Row 5 ---
        # Seller Info (Split)
        seller_group = QtWidgets.QGroupBox("Seller Information")
        seller_group.setStyleSheet("QGroupBox { font-weight: bold; color: #344E41; border: 1px solid #A3B18A; border-radius: 5px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
        seller_layout = QtWidgets.QHBoxLayout(seller_group)
        
        self.seller_name = QtWidgets.QLineEdit()
        self.seller_name.setPlaceholderText("Seller Name")
        
        self.seller_address = QtWidgets.QLineEdit()
        self.seller_address.setPlaceholderText("Address")
        
        self.seller_phone = QtWidgets.QLineEdit()
        self.seller_phone.setPlaceholderText("Phone")
        
        seller_layout.addWidget(self.seller_name)
        seller_layout.addWidget(self.seller_address)
        seller_layout.addWidget(self.seller_phone)
        
        form_grid.addWidget(seller_group, 8, 0, 1, 2)

        # --- Row 6 ---
        # Health Notes
        form_grid.addWidget(QtWidgets.QLabel("Health Notes"), 9, 0, 1, 2)
        self.health_input = QtWidgets.QTextEdit()
        self.health_input.setPlaceholderText("Any initial health conditions, marks, or notes...")
        self.health_input.setMaximumHeight(80)
        form_grid.addWidget(self.health_input, 10, 0, 1, 2)

        # --- Row 7 ---
        # Buttons
        self.btn_vaccine = QtWidgets.QPushButton("+ Add Vaccination / Medical History")
        self.btn_vaccine.clicked.connect(self.open_vaccination_dialog)
        form_grid.addWidget(self.btn_vaccine, 11, 0)
        
        # File Uploads
        upload_layout = QtWidgets.QHBoxLayout()
        self.btn_photo = QtWidgets.QPushButton("📷 Upload Photo")
        self.btn_docs = QtWidgets.QPushButton("📄 Upload Documents")
        upload_layout.addWidget(self.btn_photo)
        upload_layout.addWidget(self.btn_docs)
        form_grid.addLayout(upload_layout, 11, 1)

        card_layout.addLayout(form_grid)
        card_layout.addSpacing(20)
        
        # Save Button
        self.btn_save = QtWidgets.QPushButton("Save Record")
        self.btn_save.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #344E41;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 25px;
                padding: 15px 40px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #4A6A55;
            }
        """)
        self.btn_save.clicked.connect(self.save_cattle_record)
        
        btn_save_container = QtWidgets.QHBoxLayout()
        btn_save_container.addStretch()
        btn_save_container.addWidget(self.btn_save)
        btn_save_container.addStretch()
        
        card_layout.addLayout(btn_save_container)
        
        # Scroll Area
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(card)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;" + self.SCROLLBAR_STYLESHEET)
        
        page_layout = QtWidgets.QVBoxLayout(page)
        page_layout.setContentsMargins(0,0,0,0)
        page_layout.addWidget(scroll)
        
        # Store file paths
        self.photo_path = None
        self.docs_path = None
        
        # Connect upload buttons
        self.btn_photo.clicked.connect(self.upload_photo)
        self.btn_docs.clicked.connect(self.upload_docs)

        return page

    def upload_photo(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home', "Image files (*.jpg *.png *.webp *.jpeg)")
        if fname:
            self.photo_path = fname
            self.btn_photo.setText(f"📷 {fname.split('/')[-1]}")
            self.btn_photo.setStyleSheet("background-color: #A3B18A; color: #344E41;")

    def upload_docs(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home', "Document files (*.pdf *.docx *.txt)")
        if fname:
            self.docs_path = fname
            self.btn_docs.setText(f"📄 {fname.split('/')[-1]}")
            self.btn_docs.setStyleSheet("background-color: #A3B18A; color: #344E41;")

    def open_vaccination_dialog(self):
        dialog = VaccinationDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_data = dialog.get_data()
            self.medical_history.extend(new_data)
            if new_data:
                self.btn_vaccine.setText(f"Vaccination History ({len(self.medical_history)} items added)")
                self.btn_vaccine.setStyleSheet("background-color: #A3B18A; color: #344E41; font-weight: bold;")

    def save_cattle_record(self):
        # Gather Data
        data = {
            "name": self.name_input.text(),
            "breed": self.breed_input.currentText(),
            "purpose": self.purpose_input.currentText(),
            "gender": self.gender_input.currentText(),
            "dob": self.dob_input.date().toString("yyyy-MM-dd"),
            "entry_date": self.entry_input.date().toString("yyyy-MM-dd"),
            "initial_weight": self.initial_weight_input.text(),
            "current_weight": self.current_weight_input.text(),
            "seller_name": self.seller_name.text(),
            "seller_address": self.seller_address.text(),
            "seller_phone": self.seller_phone.text(),
            "health_notes": self.health_input.toPlainText(),
            "medical_history": json.dumps(self.medical_history)
        }
        
        # Basic Validation
        if not data["name"]:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Name is required.")
            return

        # Prepare Multipart Upload
        url = "http://localhost:8000/cattle"
        files = []
        if self.photo_path:
            files.append(('photo', open(self.photo_path, 'rb')))
        if self.docs_path:
            files.append(('documents', open(self.docs_path, 'rb')))
            
        try:
            response = requests.post(url, data=data, files=files)
            if response.status_code == 200:
                QtWidgets.QMessageBox.information(self, "Success", "Cattle record saved successfully!")
                # Reset form
                self.name_input.clear()
                self.initial_weight_input.clear()
                self.current_weight_input.clear()
                self.seller_name.clear()
                self.seller_address.clear()
                self.seller_phone.clear()
                self.health_input.clear()
                self.medical_history = []
                self.btn_vaccine.setText("+ Add Vaccination / Medical History")
                self.btn_vaccine.setStyleSheet("")
                self.btn_photo.setText("📷 Upload Photo")
                self.btn_docs.setText("📄 Upload Documents")
                self.photo_path = None
                self.docs_path = None
            else:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save: {response.text}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Connection Error", str(e))
        finally:
            # Close files
            for _, f in files:
                f.close()
