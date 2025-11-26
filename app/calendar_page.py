from PyQt5 import QtWidgets, QtCore, QtGui
from datetime import datetime, date, timedelta
import requests
import json


API_BASE_URL = "http://localhost:8000"


class AddEventDialog(QtWidgets.QDialog):
    """Dialog for adding/editing calendar events"""
    
    def __init__(self, parent=None, event_data=None, cattle_list=None):
        super().__init__(parent)
        self.event_data = event_data
        self.cattle_list = cattle_list or []
        
        is_edit = event_data is not None
        self.setWindowTitle("Edit Event" if is_edit else "Add New Event")
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)
        
        self.setStyleSheet("""
            QDialog { 
                background-color: #EBEAE3; 
            }
            QLabel { 
                color: #344E41; 
                font-weight: bold; 
                font-size: 11pt; 
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit, QSpinBox {
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
            QCheckBox {
                color: #344E41;
                font-size: 10pt;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QtWidgets.QLabel("Edit Event" if is_edit else "Add New Event")
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
        
        # Event Title
        form_layout.addWidget(QtWidgets.QLabel("Title:"), row, 0)
        self.title_input = QtWidgets.QLineEdit()
        self.title_input.setPlaceholderText("Event title")
        form_layout.addWidget(self.title_input, row, 1)
        row += 1
        
        # Event Type
        form_layout.addWidget(QtWidgets.QLabel("Type:"), row, 0)
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["Vaccination", "Breeding", "Vet Visit", "Order", "Labour", "Other"])
        form_layout.addWidget(self.type_combo, row, 1)
        row += 1
        
        # Event Date
        form_layout.addWidget(QtWidgets.QLabel("Date:"), row, 0)
        self.date_input = QtWidgets.QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QtCore.QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        form_layout.addWidget(self.date_input, row, 1)
        row += 1
        
        # Event Time
        form_layout.addWidget(QtWidgets.QLabel("Time:"), row, 0)
        time_layout = QtWidgets.QHBoxLayout()
        self.time_input = QtWidgets.QTimeEdit()
        self.time_input.setDisplayFormat("HH:mm")
        self.time_input.setTime(QtCore.QTime.currentTime())
        self.time_checkbox = QtWidgets.QCheckBox("Set specific time")
        self.time_checkbox.setChecked(False)
        self.time_input.setEnabled(False)
        self.time_checkbox.toggled.connect(self.time_input.setEnabled)
        time_layout.addWidget(self.time_checkbox)
        time_layout.addWidget(self.time_input)
        time_layout.addStretch()
        form_layout.addLayout(time_layout, row, 1)
        row += 1
        
        # End Date (optional)
        form_layout.addWidget(QtWidgets.QLabel("End Date:"), row, 0)
        end_date_layout = QtWidgets.QHBoxLayout()
        self.end_date_input = QtWidgets.QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QtCore.QDate.currentDate())
        self.end_date_input.setDisplayFormat("yyyy-MM-dd")
        self.end_date_checkbox = QtWidgets.QCheckBox("Multi-day event")
        self.end_date_checkbox.setChecked(False)
        self.end_date_input.setEnabled(False)
        self.end_date_checkbox.toggled.connect(self.end_date_input.setEnabled)
        end_date_layout.addWidget(self.end_date_checkbox)
        end_date_layout.addWidget(self.end_date_input)
        end_date_layout.addStretch()
        form_layout.addLayout(end_date_layout, row, 1)
        row += 1
        
        # Related Animals
        form_layout.addWidget(QtWidgets.QLabel("Related Animals:"), row, 0)
        self.animals_input = QtWidgets.QComboBox()
        self.animals_input.setEditable(True)
        self.animals_input.addItem("None")
        for cattle in self.cattle_list:
            tag = cattle.get('tag_number', '')
            name = cattle.get('Name', '')
            display = f"{tag} - {name}" if name else tag
            self.animals_input.addItem(display, tag)
        form_layout.addWidget(self.animals_input, row, 1)
        row += 1
        
        # Assigned Person
        form_layout.addWidget(QtWidgets.QLabel("Assigned Person:"), row, 0)
        self.person_input = QtWidgets.QLineEdit()
        self.person_input.setPlaceholderText("Person responsible")
        form_layout.addWidget(self.person_input, row, 1)
        row += 1
        
        # Location
        form_layout.addWidget(QtWidgets.QLabel("Location:"), row, 0)
        self.location_input = QtWidgets.QLineEdit()
        self.location_input.setPlaceholderText("Event location")
        form_layout.addWidget(self.location_input, row, 1)
        row += 1
        
        # Status
        form_layout.addWidget(QtWidgets.QLabel("Status:"), row, 0)
        self.status_combo = QtWidgets.QComboBox()
        self.status_combo.addItems(["Scheduled", "In Progress", "Completed", "Cancelled"])
        form_layout.addWidget(self.status_combo, row, 1)
        row += 1
        
        # Description/Notes
        form_layout.addWidget(QtWidgets.QLabel("Notes:"), row, 0, QtCore.Qt.AlignTop)
        self.notes_input = QtWidgets.QTextEdit()
        self.notes_input.setPlaceholderText("Additional notes or details")
        self.notes_input.setMaximumHeight(100)
        form_layout.addWidget(self.notes_input, row, 1)
        row += 1
        
        # Reminders section
        reminders_label = QtWidgets.QLabel("Reminders")
        reminders_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #588157; margin-top: 10px;")
        form_layout.addWidget(reminders_label, row, 0, 1, 2)
        row += 1
        
        # Email Reminder
        form_layout.addWidget(QtWidgets.QLabel("Email Reminder:"), row, 0)
        email_layout = QtWidgets.QHBoxLayout()
        self.email_checkbox = QtWidgets.QCheckBox("Enable")
        self.email_hours = QtWidgets.QSpinBox()
        self.email_hours.setMinimum(1)
        self.email_hours.setMaximum(168)  # 7 days
        self.email_hours.setValue(24)
        self.email_hours.setSuffix(" hours before")
        self.email_hours.setEnabled(False)
        self.email_checkbox.toggled.connect(self.email_hours.setEnabled)
        email_layout.addWidget(self.email_checkbox)
        email_layout.addWidget(self.email_hours)
        email_layout.addStretch()
        form_layout.addLayout(email_layout, row, 1)
        row += 1
        
        # SMS Reminder
        form_layout.addWidget(QtWidgets.QLabel("SMS Reminder:"), row, 0)
        sms_layout = QtWidgets.QHBoxLayout()
        self.sms_checkbox = QtWidgets.QCheckBox("Enable")
        self.sms_hours = QtWidgets.QSpinBox()
        self.sms_hours.setMinimum(1)
        self.sms_hours.setMaximum(168)
        self.sms_hours.setValue(4)
        self.sms_hours.setSuffix(" hours before")
        self.sms_hours.setEnabled(False)
        self.sms_checkbox.toggled.connect(self.sms_hours.setEnabled)
        sms_layout.addWidget(self.sms_checkbox)
        sms_layout.addWidget(self.sms_hours)
        sms_layout.addStretch()
        form_layout.addLayout(sms_layout, row, 1)
        row += 1
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QtWidgets.QPushButton("Save Event" if is_edit else "Add Event")
        save_btn.clicked.connect(self.save_event)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        # Load event data if editing
        if event_data:
            self._load_event_data()
    
    def _load_event_data(self):
        """Load event data into form fields"""
        data = self.event_data
        
        self.title_input.setText(data.get('title', ''))
        self.type_combo.setCurrentText(data.get('event_type', 'Other'))
        
        # Parse date
        event_date = data.get('event_date', '')
        if event_date:
            qdate = QtCore.QDate.fromString(event_date, "yyyy-MM-dd")
            self.date_input.setDate(qdate)
        
        # Parse time
        event_time = data.get('event_time')
        if event_time:
            self.time_checkbox.setChecked(True)
            qtime = QtCore.QTime.fromString(str(event_time), "HH:mm:ss")
            self.time_input.setTime(qtime)
        
        # End date
        end_date = data.get('end_date')
        if end_date:
            self.end_date_checkbox.setChecked(True)
            qdate = QtCore.QDate.fromString(end_date, "yyyy-MM-dd")
            self.end_date_input.setDate(qdate)
        
        # Other fields
        self.person_input.setText(data.get('assigned_person', ''))
        self.location_input.setText(data.get('location', ''))
        self.status_combo.setCurrentText(data.get('status', 'Scheduled'))
        self.notes_input.setPlainText(data.get('notes', ''))
        
        # Reminders
        reminders = data.get('reminders', [])
        for reminder in reminders:
            if reminder['type'] == 'Email':
                self.email_checkbox.setChecked(True)
                self.email_hours.setValue(reminder['hours_before'])
            elif reminder['type'] == 'SMS':
                self.sms_checkbox.setChecked(True)
                self.sms_hours.setValue(reminder['hours_before'])
    
    def save_event(self):
        """Save the event data"""
        title = self.title_input.text().strip()
        if not title:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Please enter an event title")
            return
        
        # Prepare event data
        event_data = {
            "title": title,
            "event_type": self.type_combo.currentText(),
            "event_date": self.date_input.date().toString("yyyy-MM-dd"),
            "event_time": self.time_input.time().toString("HH:mm:ss") if self.time_checkbox.isChecked() else None,
            "end_date": self.end_date_input.date().toString("yyyy-MM-dd") if self.end_date_checkbox.isChecked() else None,
            "end_time": None,
            "notes": self.notes_input.toPlainText().strip() or None,
            "related_animals": self.animals_input.currentData() if self.animals_input.currentIndex() > 0 else None,
            "assigned_person": self.person_input.text().strip() or None,
            "location": self.location_input.text().strip() or None,
            "status": self.status_combo.currentText(),
            "color": None,
            "email_reminder": self.email_hours.value() if self.email_checkbox.isChecked() else None,
            "sms_reminder": self.sms_hours.value() if self.sms_checkbox.isChecked() else None
        }
        
        self.event_data = event_data
        self.accept()
    
    def get_event_data(self):
        """Return the event data"""
        return self.event_data


class CalendarPage(QtWidgets.QWidget):
    """Calendar page for managing farm events"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cattle_list = []
        self.events_cache = []
        self.current_month = date.today().replace(day=1)
        
        self.setup_ui()
        self.load_cattle_list()
        self.load_events()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header with title and actions
        header_layout = QtWidgets.QHBoxLayout()
        
        title = QtWidgets.QLabel("Farm Calendar")
        title.setStyleSheet("font-size: 22pt; font-weight: bold; color: #344E41;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # View selector
        self.view_combo = QtWidgets.QComboBox()
        self.view_combo.addItems(["Month View", "Week View", "List View"])
        self.view_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #A3B18A;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 10pt;
                color: #344E41;
                min-width: 120px;
            }
        """)
        self.view_combo.currentTextChanged.connect(self.change_view)
        header_layout.addWidget(self.view_combo)
        
        # Add Event button
        add_btn = QtWidgets.QPushButton("+ Add Event")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #588157;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #344E41;
            }
        """)
        add_btn.clicked.connect(self.show_add_event_dialog)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Statistics cards
        stats_layout = QtWidgets.QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.total_card = self._create_stat_card("Total Events", "0", "#588157")
        self.upcoming_card = self._create_stat_card("Upcoming (7d)", "0", "#A3B18A")
        self.today_card = self._create_stat_card("Today", "0", "#344E41")
        self.overdue_card = self._create_stat_card("Overdue", "0", "#dc3545")
        
        stats_layout.addWidget(self.total_card)
        stats_layout.addWidget(self.upcoming_card)
        stats_layout.addWidget(self.today_card)
        stats_layout.addWidget(self.overdue_card)
        
        layout.addLayout(stats_layout)
        
        # Stacked widget for different views
        self.view_stack = QtWidgets.QStackedWidget()
        
        # Month View
        self.month_view = self._create_month_view()
        self.view_stack.addWidget(self.month_view)
        
        # Week View
        self.week_view = self._create_week_view()
        self.view_stack.addWidget(self.week_view)
        
        # List View
        self.list_view = self._create_list_view()
        self.view_stack.addWidget(self.list_view)
        
        layout.addWidget(self.view_stack)
    
    def _create_stat_card(self, title, value, color):
        """Create a statistics card"""
        card = QtWidgets.QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border-left: 5px solid {color};
            }}
        """)
        card.setMinimumHeight(100)
        
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(15, 10, 15, 10)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(f"color: {color}; font-size: 10pt; font-weight: bold;")
        card_layout.addWidget(title_label)
        
        value_label = QtWidgets.QLabel(value)
        value_label.setObjectName("valueLabel")
        value_label.setStyleSheet("color: #344E41; font-size: 24pt; font-weight: bold;")
        card_layout.addWidget(value_label)
        
        return card
    
    def _create_month_view(self):
        """Create the monthly calendar view"""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setSpacing(10)
        
        # Navigation header
        nav_layout = QtWidgets.QHBoxLayout()
        
        prev_btn = QtWidgets.QPushButton("← Previous")
        prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #A3B18A;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #588157; }
        """)
        prev_btn.clicked.connect(self.previous_month)
        nav_layout.addWidget(prev_btn)
        
        self.month_label = QtWidgets.QLabel()
        self.month_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #344E41;")
        self.month_label.setAlignment(QtCore.Qt.AlignCenter)
        nav_layout.addWidget(self.month_label, 1)
        
        next_btn = QtWidgets.QPushButton("Next →")
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: #A3B18A;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #588157; }
        """)
        next_btn.clicked.connect(self.next_month)
        nav_layout.addWidget(next_btn)
        
        today_btn = QtWidgets.QPushButton("Today")
        today_btn.setStyleSheet("""
            QPushButton {
                background-color: #344E41;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #588157; }
        """)
        today_btn.clicked.connect(self.go_to_today)
        nav_layout.addWidget(today_btn)
        
        layout.addLayout(nav_layout)
        
        # Calendar grid
        self.calendar_grid = QtWidgets.QGridLayout()
        self.calendar_grid.setSpacing(5)
        
        # Day headers
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for col, day in enumerate(days):
            header = QtWidgets.QLabel(day)
            header.setStyleSheet("""
                background-color: #588157;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            """)
            header.setAlignment(QtCore.Qt.AlignCenter)
            self.calendar_grid.addWidget(header, 0, col)
        
        # Calendar cells (will be populated by render_calendar)
        self.calendar_cells = []
        for row in range(1, 7):  # 6 weeks max
            week_cells = []
            for col in range(7):
                cell = self._create_calendar_cell()
                self.calendar_grid.addWidget(cell, row, col)
                week_cells.append(cell)
            self.calendar_cells.append(week_cells)
        
        layout.addLayout(self.calendar_grid)
        
        return container
    
    def _create_calendar_cell(self):
        """Create a single calendar cell"""
        cell = QtWidgets.QFrame()
        cell.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QFrame:hover {
                border: 2px solid #588157;
            }
        """)
        cell.setMinimumHeight(100)
        
        cell_layout = QtWidgets.QVBoxLayout(cell)
        cell_layout.setContentsMargins(5, 5, 5, 5)
        cell_layout.setSpacing(3)
        
        # Day number
        day_label = QtWidgets.QLabel()
        day_label.setObjectName("dayLabel")
        day_label.setStyleSheet("font-weight: bold; color: #344E41; font-size: 10pt;")
        cell_layout.addWidget(day_label)
        
        # Events container (scrollable)
        events_scroll = QtWidgets.QScrollArea()
        events_scroll.setWidgetResizable(True)
        events_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        events_scroll.setStyleSheet("background: transparent;")
        
        events_widget = QtWidgets.QWidget()
        events_widget.setStyleSheet("background: transparent;")
        events_layout = QtWidgets.QVBoxLayout(events_widget)
        events_layout.setContentsMargins(0, 0, 0, 0)
        events_layout.setSpacing(2)
        events_layout.addStretch()
        
        events_scroll.setWidget(events_widget)
        cell_layout.addWidget(events_scroll)
        
        cell.mousePressEvent = lambda event: self._on_cell_clicked(cell)
        
        return cell
    
    def _create_week_view(self):
        """Create the weekly view"""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        
        label = QtWidgets.QLabel("Week View - Coming Soon")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet("font-size: 14pt; color: #588157;")
        layout.addWidget(label)
        
        return container
    
    def _create_list_view(self):
        """Create the list view with event table"""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setSpacing(10)
        
        # Filters
        filter_layout = QtWidgets.QHBoxLayout()
        
        filter_layout.addWidget(QtWidgets.QLabel("Type:"))
        self.filter_type = QtWidgets.QComboBox()
        self.filter_type.addItems(["All", "Vaccination", "Breeding", "Vet Visit", "Order", "Labour", "Other"])
        self.filter_type.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.filter_type)
        
        filter_layout.addWidget(QtWidgets.QLabel("Status:"))
        self.filter_status = QtWidgets.QComboBox()
        self.filter_status.addItems(["All", "Scheduled", "In Progress", "Completed", "Cancelled"])
        self.filter_status.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.filter_status)
        
        filter_layout.addStretch()
        
        refresh_btn = QtWidgets.QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_events)
        filter_layout.addWidget(refresh_btn)
        
        layout.addLayout(filter_layout)
        
        # Events table
        self.events_table = QtWidgets.QTableWidget()
        self.events_table.setColumnCount(6)
        self.events_table.setHorizontalHeaderLabels([
            "Date", "Title", "Type", "Status", "Assigned", "Actions"
        ])
        self.events_table.horizontalHeader().setStretchLastSection(True)
        self.events_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.events_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.events_table.setAlternatingRowColors(True)
        self.events_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #588157;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)
        
        layout.addWidget(self.events_table)
        
        return container
    
    def _on_cell_clicked(self, cell):
        """Handle calendar cell click"""
        day_label = cell.findChild(QtWidgets.QLabel, "dayLabel")
        if day_label:
            day_num = day_label.text()
            if day_num.isdigit():
                # Show events for this day or open add event dialog
                pass
    
    def change_view(self, view_name):
        """Change the calendar view"""
        view_map = {
            "Month View": 0,
            "Week View": 1,
            "List View": 2
        }
        self.view_stack.setCurrentIndex(view_map.get(view_name, 0))
        
        if view_name == "Month View":
            self.render_calendar()
        elif view_name == "List View":
            self.populate_list_view()
    
    def previous_month(self):
        """Go to previous month"""
        if self.current_month.month == 1:
            self.current_month = self.current_month.replace(year=self.current_month.year - 1, month=12)
        else:
            self.current_month = self.current_month.replace(month=self.current_month.month - 1)
        self.render_calendar()
    
    def next_month(self):
        """Go to next month"""
        if self.current_month.month == 12:
            self.current_month = self.current_month.replace(year=self.current_month.year + 1, month=1)
        else:
            self.current_month = self.current_month.replace(month=self.current_month.month + 1)
        self.render_calendar()
    
    def go_to_today(self):
        """Go to current month"""
        self.current_month = date.today().replace(day=1)
        self.render_calendar()
    
    def render_calendar(self):
        """Render the calendar for current month"""
        self.month_label.setText(self.current_month.strftime("%B %Y"))
        
        # Get first day of month and number of days
        first_day = self.current_month
        if self.current_month.month == 12:
            last_day = self.current_month.replace(month=1, year=self.current_month.year + 1, day=1) - timedelta(days=1)
        else:
            last_day = self.current_month.replace(month=self.current_month.month + 1, day=1) - timedelta(days=1)
        
        # Get starting weekday (0=Monday, 6=Sunday)
        start_weekday = first_day.weekday()
        
        # Clear all cells
        for week in self.calendar_cells:
            for cell in week:
                day_label = cell.findChild(QtWidgets.QLabel, "dayLabel")
                if day_label:
                    day_label.setText("")
                
                # Clear events
                scroll = cell.findChild(QtWidgets.QScrollArea)
                if scroll and scroll.widget():
                    events_layout = scroll.widget().layout()
                    while events_layout.count() > 1:  # Keep the stretch
                        item = events_layout.takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()
        
        # Fill in days
        current_day = 1
        for week_idx, week in enumerate(self.calendar_cells):
            for day_idx, cell in enumerate(week):
                cell_date_index = week_idx * 7 + day_idx
                
                if cell_date_index >= start_weekday and current_day <= last_day.day:
                    # Set day number
                    day_label = cell.findChild(QtWidgets.QLabel, "dayLabel")
                    if day_label:
                        day_label.setText(str(current_day))
                    
                    # Get events for this day
                    cell_date = self.current_month.replace(day=current_day)
                    day_events = [e for e in self.events_cache 
                                 if e.get('event_date', '')[:10] == cell_date.strftime("%Y-%m-%d")]
                    
                    # Add event indicators
                    scroll = cell.findChild(QtWidgets.QScrollArea)
                    if scroll and scroll.widget():
                        events_layout = scroll.widget().layout()
                        
                        for event in day_events[:3]:  # Show max 3 events
                            event_badge = self._create_event_badge(event)
                            events_layout.insertWidget(events_layout.count() - 1, event_badge)
                        
                        if len(day_events) > 3:
                            more_label = QtWidgets.QLabel(f"+{len(day_events) - 3} more")
                            more_label.setStyleSheet("color: #588157; font-size: 8pt; font-style: italic;")
                            events_layout.insertWidget(events_layout.count() - 1, more_label)
                    
                    # Highlight today
                    if cell_date == date.today():
                        cell.setStyleSheet("""
                            QFrame {
                                background-color: #fffacd;
                                border: 2px solid #588157;
                                border-radius: 5px;
                            }
                        """)
                    
                    current_day += 1
    
    def _create_event_badge(self, event):
        """Create a small event badge for calendar cell"""
        badge = QtWidgets.QLabel(event.get('title', 'Event')[:15])
        
        # Color based on event type
        colors = {
            "Vaccination": "#007bff",
            "Breeding": "#28a745",
            "Vet Visit": "#dc3545",
            "Order": "#ffc107",
            "Labour": "#6f42c1",
            "Other": "#6c757d"
        }
        color = colors.get(event.get('event_type'), "#6c757d")
        
        badge.setStyleSheet(f"""
            background-color: {color};
            color: white;
            padding: 2px 5px;
            border-radius: 3px;
            font-size: 8pt;
            font-weight: bold;
        """)
        badge.setMaximumHeight(20)
        badge.setToolTip(event.get('title', ''))
        
        return badge
    
    def populate_list_view(self):
        """Populate the list view table"""
        self.events_table.setRowCount(0)
        
        filtered_events = self.get_filtered_events()
        
        for event in filtered_events:
            row = self.events_table.rowCount()
            self.events_table.insertRow(row)
            
            # Date
            event_date = event.get('event_date', '')
            event_time = event.get('event_time', '')
            date_str = event_date
            if event_time:
                date_str += f" {event_time[:5]}"
            self.events_table.setItem(row, 0, QtWidgets.QTableWidgetItem(date_str))
            
            # Title
            self.events_table.setItem(row, 1, QtWidgets.QTableWidgetItem(event.get('title', '')))
            
            # Type
            self.events_table.setItem(row, 2, QtWidgets.QTableWidgetItem(event.get('event_type', '')))
            
            # Status
            self.events_table.setItem(row, 3, QtWidgets.QTableWidgetItem(event.get('status', '')))
            
            # Assigned
            self.events_table.setItem(row, 4, QtWidgets.QTableWidgetItem(event.get('assigned_person', '')))
            
            # Actions
            actions_widget = QtWidgets.QWidget()
            actions_layout = QtWidgets.QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 0, 5, 0)
            actions_layout.setSpacing(5)
            
            edit_btn = QtWidgets.QPushButton("Edit")
            edit_btn.setStyleSheet("background-color: #588157; color: white; padding: 5px 10px; border-radius: 3px;")
            edit_btn.clicked.connect(lambda checked, e=event: self.edit_event(e))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QtWidgets.QPushButton("Delete")
            delete_btn.setStyleSheet("background-color: #dc3545; color: white; padding: 5px 10px; border-radius: 3px;")
            delete_btn.clicked.connect(lambda checked, e=event: self.delete_event(e))
            actions_layout.addWidget(delete_btn)
            
            self.events_table.setCellWidget(row, 5, actions_widget)
        
        self.events_table.resizeColumnsToContents()
    
    def get_filtered_events(self):
        """Get filtered events based on current filters"""
        filtered = self.events_cache
        
        if hasattr(self, 'filter_type'):
            event_type = self.filter_type.currentText()
            if event_type != "All":
                filtered = [e for e in filtered if e.get('event_type') == event_type]
        
        if hasattr(self, 'filter_status'):
            status = self.filter_status.currentText()
            if status != "All":
                filtered = [e for e in filtered if e.get('status') == status]
        
        return filtered
    
    def apply_filters(self):
        """Apply filters to list view"""
        if self.view_combo.currentText() == "List View":
            self.populate_list_view()
    
    def load_cattle_list(self):
        """Load cattle list from API"""
        try:
            response = requests.get(f"{API_BASE_URL}/cattle")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.cattle_list = data.get('data', [])
        except Exception as e:
            print(f"Error loading cattle: {e}")
    
    def load_events(self):
        """Load events from API"""
        try:
            response = requests.get(f"{API_BASE_URL}/calendar/events", params={"limit": 500})
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.events_cache = data.get('data', [])
                    self.update_statistics()
                    self.render_calendar()
                    if self.view_combo.currentText() == "List View":
                        self.populate_list_view()
        except Exception as e:
            print(f"Error loading events: {e}")
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to load events: {str(e)}")
    
    def update_statistics(self):
        """Update statistics cards"""
        try:
            # Get summary from API
            response = requests.get(f"{API_BASE_URL}/calendar/summary")
            if response.status_code == 200:
                data = response.json().get('data', {})
                
                # Update cards
                self.total_card.findChild(QtWidgets.QLabel, "valueLabel").setText(
                    str(data.get('total_events', 0))
                )
                self.upcoming_card.findChild(QtWidgets.QLabel, "valueLabel").setText(
                    str(data.get('upcoming_7_days', 0))
                )
                self.overdue_card.findChild(QtWidgets.QLabel, "valueLabel").setText(
                    str(data.get('overdue', 0))
                )
                
                # Today's events
                today_str = date.today().strftime("%Y-%m-%d")
                today_events = [e for e in self.events_cache 
                               if e.get('event_date', '')[:10] == today_str]
                self.today_card.findChild(QtWidgets.QLabel, "valueLabel").setText(
                    str(len(today_events))
                )
        except Exception as e:
            print(f"Error updating statistics: {e}")
    
    def show_add_event_dialog(self):
        """Show dialog to add new event"""
        dialog = AddEventDialog(self, cattle_list=self.cattle_list)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            event_data = dialog.get_event_data()
            self.create_event(event_data)
    
    def create_event(self, event_data):
        """Create a new event via API"""
        try:
            response = requests.post(f"{API_BASE_URL}/calendar/events", json=event_data)
            if response.status_code == 200:
                QtWidgets.QMessageBox.information(self, "Success", "Event created successfully")
                self.load_events()
            else:
                error_msg = response.json().get('detail', 'Unknown error')
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to create event: {error_msg}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to create event: {str(e)}")
    
    def edit_event(self, event):
        """Edit an existing event"""
        dialog = AddEventDialog(self, event_data=event, cattle_list=self.cattle_list)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            updated_data = dialog.get_event_data()
            self.update_event(event['id'], updated_data)
    
    def update_event(self, event_id, event_data):
        """Update an event via API"""
        try:
            response = requests.put(f"{API_BASE_URL}/calendar/events/{event_id}", json=event_data)
            if response.status_code == 200:
                QtWidgets.QMessageBox.information(self, "Success", "Event updated successfully")
                self.load_events()
            else:
                error_msg = response.json().get('detail', 'Unknown error')
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to update event: {error_msg}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to update event: {str(e)}")
    
    def delete_event(self, event):
        """Delete an event"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the event '{event.get('title')}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                response = requests.delete(f"{API_BASE_URL}/calendar/events/{event['id']}")
                if response.status_code == 200:
                    QtWidgets.QMessageBox.information(self, "Success", "Event deleted successfully")
                    self.load_events()
                else:
                    error_msg = response.json().get('detail', 'Unknown error')
                    QtWidgets.QMessageBox.warning(self, "Error", f"Failed to delete event: {error_msg}")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to delete event: {str(e)}")
