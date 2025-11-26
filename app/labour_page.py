"""
Labour Management Page for KhamarBari Farm Management System
Includes: Labour List, Attendance Manager, and Payroll Processor
"""

import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import requests
from datetime import datetime, timedelta
import calendar


class LabourPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the Labour management page UI."""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Main content area
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Header with tab buttons
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(10)
        
        # Tab buttons
        self.tab_labour = self.create_tab_button("Labour List", True)
        self.tab_attendance = self.create_tab_button("Attendance Manager", False)
        self.tab_payroll = self.create_tab_button("Payroll Processor", False)
        
        self.tab_labour.clicked.connect(lambda: self.switch_tab(0))
        self.tab_attendance.clicked.connect(lambda: self.switch_tab(1))
        self.tab_payroll.clicked.connect(lambda: self.switch_tab(2))
        
        header_layout.addWidget(self.tab_labour)
        header_layout.addWidget(self.tab_attendance)
        header_layout.addWidget(self.tab_payroll)
        header_layout.addStretch()
        
        content_layout.addLayout(header_layout)
        
        # Stacked widget for tabs
        self.tabs_stack = QtWidgets.QStackedWidget()
        
        # Add tab contents
        self.tabs_stack.addWidget(self.create_labour_list_tab())
        self.tabs_stack.addWidget(self.create_attendance_tab())
        self.tabs_stack.addWidget(self.create_payroll_tab())
        
        content_layout.addWidget(self.tabs_stack)
        
        main_layout.addWidget(content_widget)
        
        # Load initial data
        self.load_labourers()
    
    def create_tab_button(self, text, is_active):
        """Create a styled tab button."""
        btn = QtWidgets.QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(is_active)
        btn.setFixedHeight(40)
        btn.setMinimumWidth(140)
        
        if is_active:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #344E41;
                    color: white;
                    border-radius: 5px 5px 0 0;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 10pt;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #D8E2D1;
                    color: #344E41;
                    border-radius: 5px 5px 0 0;
                    padding: 10px 20px;
                    font-weight: normal;
                    font-size: 10pt;
                }
                QPushButton:hover {
                    background-color: #A3B18A;
                    color: white;
                }
            """)
        
        return btn
    
    def switch_tab(self, index):
        """Switch between tabs."""
        self.tabs_stack.setCurrentIndex(index)
        
        # Update button styles
        buttons = [self.tab_labour, self.tab_attendance, self.tab_payroll]
        for i, btn in enumerate(buttons):
            btn.setChecked(i == index)
            if i == index:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #344E41;
                        color: white;
                        border-radius: 5px 5px 0 0;
                        padding: 10px 20px;
                        font-weight: bold;
                        font-size: 10pt;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #D8E2D1;
                        color: #344E41;
                        border-radius: 5px 5px 0 0;
                        padding: 10px 20px;
                        font-weight: normal;
                        font-size: 10pt;
                    }
                    QPushButton:hover {
                        background-color: #A3B18A;
                        color: white;
                    }
                """)
        
    def create_header(self):
        """Create the page header."""
        header = QtWidgets.QWidget()
        header.setStyleSheet("background-color: #344E41; padding: 15px;")
        header.setFixedHeight(70)
        
        layout = QtWidgets.QHBoxLayout(header)
        
        title = QtWidgets.QLabel("Labour Management")
        title.setStyleSheet("color: white; font-size: 20pt; font-weight: bold;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Stats summary
        self.stats_label = QtWidgets.QLabel()
        self.stats_label.setStyleSheet("color: white; font-size: 10pt;")
        layout.addWidget(self.stats_label)
        
        self.load_stats()
        
        return header
    
    def create_labour_list_tab(self):
        """Create the labour list tab."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Top controls
        controls_layout = QtWidgets.QHBoxLayout()
        
        # Filters
        status_label = QtWidgets.QLabel("Status:")
        status_label.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(status_label)
        
        self.status_filter = QtWidgets.QComboBox()
        self.status_filter.addItems(["All", "Active", "Inactive"])
        self.status_filter.setFixedWidth(150)
        self.status_filter.currentTextChanged.connect(self.load_labourers)
        controls_layout.addWidget(self.status_filter)
        
        controls_layout.addSpacing(20)
        
        position_label = QtWidgets.QLabel("Position:")
        position_label.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(position_label)
        
        self.position_filter = QtWidgets.QComboBox()
        self.position_filter.addItems(["All", "Supervisor", "Farmhand", "Driver", "Guard", "Cleaner"])
        self.position_filter.setFixedWidth(150)
        self.position_filter.currentTextChanged.connect(self.load_labourers)
        controls_layout.addWidget(self.position_filter)
        
        controls_layout.addStretch()
        
        # Add Labour button
        add_btn = QtWidgets.QPushButton("+ Add New Labour")
        add_btn.setFixedHeight(40)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #588157;
                color: white;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #344E41;
            }
        """)
        add_btn.clicked.connect(self.open_add_labour_dialog)
        controls_layout.addWidget(add_btn)
        
        layout.addLayout(controls_layout)
        
        # Labour table
        self.labour_table = QtWidgets.QTableWidget()
        self.labour_table.setColumnCount(8)
        self.labour_table.setHorizontalHeaderLabels([
            "Name", "Position", "Phone", "Pay Type", "Base Rate", "Status", "Joining Date", "Actions"
        ])
        
        header = self.labour_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QtWidgets.QHeaderView.Fixed)
        self.labour_table.setColumnWidth(7, 200)
        
        self.labour_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.labour_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.labour_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.labour_table.setAlternatingRowColors(True)
        self.labour_table.verticalHeader().setVisible(False)
        self.labour_table.verticalHeader().setDefaultSectionSize(55)
        
        self.labour_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #EBEAE3;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #588157;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.labour_table)
        
        return widget
    
    def create_attendance_tab(self):
        """Create the attendance manager tab."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Date selector and quick actions
        top_layout = QtWidgets.QHBoxLayout()
        
        # Date section
        date_section = QtWidgets.QHBoxLayout()
        date_label = QtWidgets.QLabel("Mark Attendance for:")
        date_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        date_section.addWidget(date_label)
        
        self.attendance_date = QtWidgets.QDateEdit()
        self.attendance_date.setDate(QtCore.QDate.currentDate())
        self.attendance_date.setCalendarPopup(True)
        self.attendance_date.setFixedWidth(150)
        self.attendance_date.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 2px solid #A3B18A;
                border-radius: 4px;
                font-size: 10pt;
            }
        """)
        self.attendance_date.dateChanged.connect(self.load_attendance_for_date)
        date_section.addWidget(self.attendance_date)
        
        # Today button
        today_btn = QtWidgets.QPushButton("Today")
        today_btn.setFixedHeight(35)
        today_btn.setStyleSheet("""
            QPushButton {
                background-color: #A3B18A;
                color: white;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #588157;
            }
        """)
        today_btn.clicked.connect(lambda: self.attendance_date.setDate(QtCore.QDate.currentDate()))
        date_section.addWidget(today_btn)
        
        top_layout.addLayout(date_section)
        top_layout.addSpacing(30)
        
        # Quick action buttons
        quick_actions = QtWidgets.QHBoxLayout()
        quick_actions.addWidget(QtWidgets.QLabel("Quick Mark:"))
        
        mark_all_present = QtWidgets.QPushButton("✓ All Present")
        mark_all_present.setFixedHeight(35)
        mark_all_present.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
        """)
        mark_all_present.clicked.connect(self.mark_all_present)
        quick_actions.addWidget(mark_all_present)
        
        mark_all_absent = QtWidgets.QPushButton("✗ All Absent")
        mark_all_absent.setFixedHeight(35)
        mark_all_absent.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        mark_all_absent.clicked.connect(self.mark_all_absent)
        quick_actions.addWidget(mark_all_absent)
        
        top_layout.addLayout(quick_actions)
        top_layout.addStretch()
        
        # Save attendance button
        save_btn = QtWidgets.QPushButton("💾 Save Attendance")
        save_btn.setFixedHeight(40)
        save_btn.setFixedWidth(180)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #588157;
                color: white;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #344E41;
            }
        """)
        save_btn.clicked.connect(self.save_bulk_attendance)
        top_layout.addWidget(save_btn)
        
        layout.addLayout(top_layout)
        layout.addSpacing(15)
        
        # Summary stats
        stats_widget = QtWidgets.QWidget()
        stats_widget.setStyleSheet("""
            QWidget {
                background-color: #EBEAE3;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        stats_layout = QtWidgets.QHBoxLayout(stats_widget)
        
        self.stats_present = QtWidgets.QLabel("Present: 0")
        self.stats_present.setStyleSheet("color: #5cb85c; font-weight: bold; font-size: 11pt;")
        stats_layout.addWidget(self.stats_present)
        
        self.stats_absent = QtWidgets.QLabel("Absent: 0")
        self.stats_absent.setStyleSheet("color: #d9534f; font-weight: bold; font-size: 11pt;")
        stats_layout.addWidget(self.stats_absent)
        
        self.stats_half = QtWidgets.QLabel("Half-Day: 0")
        self.stats_half.setStyleSheet("color: #f0ad4e; font-weight: bold; font-size: 11pt;")
        stats_layout.addWidget(self.stats_half)
        
        self.stats_total = QtWidgets.QLabel("Total: 0")
        self.stats_total.setStyleSheet("color: #344E41; font-weight: bold; font-size: 11pt;")
        stats_layout.addWidget(self.stats_total)
        
        stats_layout.addStretch()
        
        # View history button
        view_history_btn = QtWidgets.QPushButton("📅 View Monthly History")
        view_history_btn.setStyleSheet("""
            QPushButton {
                background-color: #A3B18A;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #588157;
            }
        """)
        view_history_btn.clicked.connect(self.show_monthly_attendance_dialog)
        stats_layout.addWidget(view_history_btn)
        
        layout.addWidget(stats_widget)
        layout.addSpacing(10)
        
        # Attendance table
        self.attendance_table = QtWidgets.QTableWidget()
        self.attendance_table.setColumnCount(7)
        self.attendance_table.setHorizontalHeaderLabels([
            "Select", "Name", "Position", "Status", "Overtime (hrs)", "Notes", "Actions"
        ])
        
        header = self.attendance_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(6, QtWidgets.QHeaderView.Fixed)
        self.attendance_table.setColumnWidth(0, 60)
        self.attendance_table.setColumnWidth(1, 150)
        self.attendance_table.setColumnWidth(3, 320)
        self.attendance_table.setColumnWidth(4, 120)
        self.attendance_table.setColumnWidth(6, 140)
        
        self.attendance_table.verticalHeader().setVisible(False)
        self.attendance_table.verticalHeader().setDefaultSectionSize(60)
        self.attendance_table.setAlternatingRowColors(True)
        
        self.attendance_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #EBEAE3;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #588157;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 10pt;
            }
        """)
        
        layout.addWidget(self.attendance_table)
        
        # Load today's attendance
        self.load_attendance_for_date()
        
        return widget
    
    def create_payroll_tab(self):
        """Create the payroll processor tab."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Summary statistics panel
        stats_panel = QtWidgets.QFrame()
        stats_panel.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 2px solid #588157;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        stats_layout = QtWidgets.QHBoxLayout(stats_panel)
        
        self.payroll_stats_total = QtWidgets.QLabel("Total: ৳ 0.00")
        self.payroll_stats_total.setStyleSheet("font-size: 13pt; font-weight: bold; color: #344E41;")
        stats_layout.addWidget(self.payroll_stats_total)
        
        self.payroll_stats_pending = QtWidgets.QLabel("Pending: ৳ 0.00")
        self.payroll_stats_pending.setStyleSheet("font-size: 12pt; color: #f0ad4e;")
        stats_layout.addWidget(self.payroll_stats_pending)
        
        self.payroll_stats_paid = QtWidgets.QLabel("Paid: ৳ 0.00")
        self.payroll_stats_paid.setStyleSheet("font-size: 12pt; color: #5cb85c;")
        stats_layout.addWidget(self.payroll_stats_paid)
        
        self.payroll_stats_count = QtWidgets.QLabel("Labourers: 0")
        self.payroll_stats_count.setStyleSheet("font-size: 11pt; color: #344E41;")
        stats_layout.addWidget(self.payroll_stats_count)
        
        self.payroll_stats_avg = QtWidgets.QLabel("Average: ৳ 0.00")
        self.payroll_stats_avg.setStyleSheet("font-size: 11pt; color: #588157;")
        stats_layout.addWidget(self.payroll_stats_avg)
        
        stats_layout.addStretch()
        layout.addWidget(stats_panel)
        layout.addSpacing(10)
        
        # Month/Year selector
        controls_layout = QtWidgets.QHBoxLayout()
        
        month_label = QtWidgets.QLabel("Select Month:")
        month_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        controls_layout.addWidget(month_label)
        
        self.payroll_month = QtWidgets.QComboBox()
        self.payroll_month.addItems([
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ])
        self.payroll_month.setCurrentIndex(datetime.now().month - 1)
        self.payroll_month.setFixedWidth(120)
        controls_layout.addWidget(self.payroll_month)
        
        self.payroll_year = QtWidgets.QSpinBox()
        self.payroll_year.setRange(2020, 2100)
        self.payroll_year.setValue(datetime.now().year)
        self.payroll_year.setFixedWidth(80)
        controls_layout.addWidget(self.payroll_year)
        
        load_payroll_btn = QtWidgets.QPushButton("Load Payroll")
        load_payroll_btn.clicked.connect(self.load_payroll)
        load_payroll_btn.setStyleSheet("""
            QPushButton {
                background-color: #A3B18A;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #588157;
            }
        """)
        controls_layout.addWidget(load_payroll_btn)
        
        controls_layout.addSpacing(20)
        
        # Status filter
        status_label = QtWidgets.QLabel("Payment Status:")
        status_label.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(status_label)
        
        self.payroll_status_filter = QtWidgets.QComboBox()
        self.payroll_status_filter.addItems(["All", "Pending", "Paid"])
        self.payroll_status_filter.setFixedWidth(120)
        self.payroll_status_filter.currentTextChanged.connect(self.load_payroll)
        controls_layout.addWidget(self.payroll_status_filter)
        
        controls_layout.addStretch()
        
        # Export button
        export_btn = QtWidgets.QPushButton("📊 Export CSV")
        export_btn.setFixedHeight(40)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #A3B18A;
                color: white;
                border-radius: 4px;
                padding: 10px 15px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #588157;
            }
        """)
        export_btn.clicked.connect(self.export_payroll_csv)
        controls_layout.addWidget(export_btn)
        
        # Mark All Paid button
        mark_all_btn = QtWidgets.QPushButton("✓ Mark All Paid")
        mark_all_btn.setFixedHeight(40)
        mark_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                border-radius: 4px;
                padding: 10px 15px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
        """)
        mark_all_btn.clicked.connect(self.mark_all_pending_paid)
        controls_layout.addWidget(mark_all_btn)
        
        # Calculate All button
        calc_all_btn = QtWidgets.QPushButton("⚡ Calculate All")
        calc_all_btn.setFixedHeight(40)
        calc_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #588157;
                color: white;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #344E41;
            }
        """)
        calc_all_btn.clicked.connect(self.calculate_all_payroll)
        controls_layout.addWidget(calc_all_btn)
        
        layout.addLayout(controls_layout)
        
        # Payroll table
        self.payroll_table = QtWidgets.QTableWidget()
        self.payroll_table.setColumnCount(10)
        self.payroll_table.setHorizontalHeaderLabels([
            "Name", "Position", "Pay Type", "Working Days", "Base Earning", 
            "Bonus", "Deduction", "Total Payable", "Status", "Actions"
        ])
        
        header = self.payroll_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        for i in range(1, 10):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        
        self.payroll_table.verticalHeader().setVisible(False)
        self.payroll_table.verticalHeader().setDefaultSectionSize(55)
        self.payroll_table.setAlternatingRowColors(True)
        
        self.payroll_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #EBEAE3;
                border-radius: 4px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #588157;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.payroll_table)
        
        # Load initial payroll data
        self.load_payroll()
        
        return widget
    
    def load_stats(self):
        """Load labour statistics."""
        try:
            response = requests.get("http://localhost:8000/labourers/stats/summary")
            response.raise_for_status()
            
            result = response.json()
            stats = result['data']
            
            self.stats_label.setText(
                f"Total: {stats['total_labourers']} | "
                f"Active: {stats['active_labourers']} | "
                f"Monthly: {stats['monthly_employees']} | "
                f"Daily: {stats['daily_workers']}"
            )
        except:
            pass
    
    def load_labourers(self):
        """Load labourers list."""
        try:
            params = {}
            
            status = self.status_filter.currentText()
            if status != "All":
                params['status'] = status
            
            position = self.position_filter.currentText()
            if position != "All":
                params['position'] = position
            
            response = requests.get("http://localhost:8000/labourers", params=params)
            response.raise_for_status()
            
            result = response.json()
            labourers = result['data']
            
            self.populate_labour_table(labourers)
            self.load_stats()
            
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load labourers: {str(e)}")
    
    def populate_labour_table(self, labourers):
        """Populate the labour table with data."""
        self.labour_table.setRowCount(0)
        
        for labour in labourers:
            row = self.labour_table.rowCount()
            self.labour_table.insertRow(row)
            
            # Name
            self.labour_table.setItem(row, 0, QtWidgets.QTableWidgetItem(labour['full_name']))
            
            # Position
            self.labour_table.setItem(row, 1, QtWidgets.QTableWidgetItem(labour['position']))
            
            # Phone
            phone = labour.get('phone_number', 'N/A')
            self.labour_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(phone)))
            
            # Pay Type
            pay_type = labour['pay_type'].replace('_', ' ')
            self.labour_table.setItem(row, 3, QtWidgets.QTableWidgetItem(pay_type))
            
            # Base Rate
            self.labour_table.setItem(row, 4, QtWidgets.QTableWidgetItem(f"৳ {labour['base_rate']:,.2f}"))
            
            # Status
            status = labour['status']
            status_item = QtWidgets.QTableWidgetItem(status)
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            if status == "Active":
                status_item.setBackground(QtGui.QColor("#5cb85c"))
                status_item.setForeground(QtGui.QColor("white"))
            else:
                status_item.setBackground(QtGui.QColor("#d9534f"))
                status_item.setForeground(QtGui.QColor("white"))
            self.labour_table.setItem(row, 5, status_item)
            
            # Joining Date
            self.labour_table.setItem(row, 6, QtWidgets.QTableWidgetItem(str(labour['joining_date'])))
            
            # Actions
            actions_widget = self.create_labour_actions(labour['id'])
            self.labour_table.setCellWidget(row, 7, actions_widget)
    
    def create_labour_actions(self, labour_id):
        """Create action buttons for labour row."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Edit button
        edit_btn = QtWidgets.QPushButton("Edit")
        edit_btn.setFixedSize(60, 30)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #5bc0de;
                color: white;
                border-radius: 3px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #31b0d5;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_labourer(labour_id))
        layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QtWidgets.QPushButton("Delete")
        delete_btn.setFixedSize(60, 30)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 3px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_labourer(labour_id))
        layout.addWidget(delete_btn)
        
        layout.addStretch()
        
        return widget
    
    def open_add_labour_dialog(self):
        """Open dialog to add new labourer."""
        dialog = LabourDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.load_labourers()
    
    def edit_labourer(self, labour_id):
        """Open dialog to edit labourer."""
        dialog = LabourDialog(self, labour_id)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.load_labourers()
    
    def delete_labourer(self, labour_id):
        """Delete (deactivate) a labourer."""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to deactivate this labourer?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                response = requests.delete(f"http://localhost:8000/labourers/{labour_id}")
                response.raise_for_status()
                
                QtWidgets.QMessageBox.information(self, "Success", "Labourer deactivated successfully!")
                self.load_labourers()
                
            except requests.exceptions.RequestException as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to deactivate labourer: {str(e)}")
    
    def load_attendance_for_date(self):
        """Load attendance for selected date."""
        try:
            date = self.attendance_date.date().toString("yyyy-MM-dd")
            
            response = requests.get("http://localhost:8000/attendance", params={"date": date})
            response.raise_for_status()
            
            result = response.json()
            attendance_records = result['data']
            
            # Get all active labourers
            response = requests.get("http://localhost:8000/labourers", params={"status": "Active"})
            response.raise_for_status()
            labourers = response.json()['data']
            
            # Create attendance map
            attendance_map = {rec['labour_id']: rec for rec in attendance_records}
            
            # Populate table
            self.attendance_table.setRowCount(0)
            
            present_count = 0
            absent_count = 0
            half_day_count = 0
            
            for labour in labourers:
                row = self.attendance_table.rowCount()
                self.attendance_table.insertRow(row)
                
                # Checkbox
                checkbox = QtWidgets.QCheckBox()
                checkbox.setStyleSheet("QCheckBox { margin-left: 20px; }")
                checkbox_widget = QtWidgets.QWidget()
                checkbox_layout = QtWidgets.QHBoxLayout(checkbox_widget)
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(QtCore.Qt.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                self.attendance_table.setCellWidget(row, 0, checkbox_widget)
                
                # Name
                name_item = QtWidgets.QTableWidgetItem(labour['full_name'])
                name_item.setData(QtCore.Qt.UserRole, labour['id'])
                self.attendance_table.setItem(row, 1, name_item)
                
                # Position
                self.attendance_table.setItem(row, 2, QtWidgets.QTableWidgetItem(labour['position']))
                
                # Status buttons
                status_widget = QtWidgets.QWidget()
                status_layout = QtWidgets.QHBoxLayout(status_widget)
                status_layout.setContentsMargins(8, 5, 8, 5)
                status_layout.setSpacing(10)
                
                current_status = "Present"
                if labour['id'] in attendance_map:
                    current_status = attendance_map[labour['id']]['status']
                
                if current_status == "Present":
                    present_count += 1
                elif current_status == "Absent":
                    absent_count += 1
                elif current_status == "Half-Day":
                    half_day_count += 1
                
                present_btn = QtWidgets.QPushButton("Present")
                present_btn.setFixedSize(95, 32)
                present_btn.setCheckable(True)
                present_btn.setChecked(current_status == "Present")
                present_btn.setStyleSheet(self.get_status_button_style("Present", current_status == "Present"))
                present_btn.clicked.connect(lambda checked, r=row: self.set_status(r, "Present"))
                
                absent_btn = QtWidgets.QPushButton("Absent")
                absent_btn.setFixedSize(95, 32)
                absent_btn.setCheckable(True)
                absent_btn.setChecked(current_status == "Absent")
                absent_btn.setStyleSheet(self.get_status_button_style("Absent", current_status == "Absent"))
                absent_btn.clicked.connect(lambda checked, r=row: self.set_status(r, "Absent"))
                
                half_btn = QtWidgets.QPushButton("Half-Day")
                half_btn.setFixedSize(95, 32)
                half_btn.setCheckable(True)
                half_btn.setChecked(current_status == "Half-Day")
                half_btn.setStyleSheet(self.get_status_button_style("Half-Day", current_status == "Half-Day"))
                half_btn.clicked.connect(lambda checked, r=row: self.set_status(r, "Half-Day"))
                
                status_layout.addWidget(present_btn)
                status_layout.addWidget(absent_btn)
                status_layout.addWidget(half_btn)
                
                self.attendance_table.setCellWidget(row, 3, status_widget)
                
                # Overtime hours
                overtime_spin = QtWidgets.QSpinBox()
                overtime_spin.setRange(0, 12)
                overtime_spin.setStyleSheet("""
                    QSpinBox {
                        padding: 5px;
                        border: 1px solid #A3B18A;
                        border-radius: 3px;
                    }
                """)
                if labour['id'] in attendance_map:
                    overtime_spin.setValue(attendance_map[labour['id']]['overtime_hours'])
                self.attendance_table.setCellWidget(row, 4, overtime_spin)
                
                # Notes
                notes_item = QtWidgets.QTableWidgetItem()
                if labour['id'] in attendance_map:
                    notes_item.setText(attendance_map[labour['id']].get('notes', ''))
                self.attendance_table.setItem(row, 5, notes_item)
                
                # Quick actions
                actions_widget = QtWidgets.QWidget()
                actions_layout = QtWidgets.QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 5, 5, 5)
                
                copy_btn = QtWidgets.QPushButton("📋")
                copy_btn.setFixedSize(35, 30)
                copy_btn.setToolTip("Copy yesterday's status")
                copy_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #A3B18A;
                        color: white;
                        border-radius: 3px;
                        font-size: 12pt;
                    }
                    QPushButton:hover {
                        background-color: #588157;
                    }
                """)
                actions_layout.addWidget(copy_btn)
                actions_layout.addStretch()
                
                self.attendance_table.setCellWidget(row, 6, actions_widget)
            
            # Update stats
            self.stats_present.setText(f"Present: {present_count}")
            self.stats_absent.setText(f"Absent: {absent_count}")
            self.stats_half.setText(f"Half-Day: {half_day_count}")
            self.stats_total.setText(f"Total: {len(labourers)}")
                
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load attendance: {str(e)}")
    
    def get_status_button_style(self, status_type, is_checked):
        """Get style for status button."""
        if status_type == "Present":
            if is_checked:
                return """
                    QPushButton {
                        background-color: #5cb85c;
                        color: white;
                        border: 2px solid #4cae4c;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                """
            else:
                return """
                    QPushButton {
                        background-color: white;
                        color: #5cb85c;
                        border: 2px solid #5cb85c;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #5cb85c;
                        color: white;
                    }
                """
        elif status_type == "Absent":
            if is_checked:
                return """
                    QPushButton {
                        background-color: #d9534f;
                        color: white;
                        border: 2px solid #c9302c;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                """
            else:
                return """
                    QPushButton {
                        background-color: white;
                        color: #d9534f;
                        border: 2px solid #d9534f;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #d9534f;
                        color: white;
                    }
                """
        else:  # Half-Day
            if is_checked:
                return """
                    QPushButton {
                        background-color: #f0ad4e;
                        color: white;
                        border: 2px solid #eea236;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                """
            else:
                return """
                    QPushButton {
                        background-color: white;
                        color: #f0ad4e;
                        border: 2px solid #f0ad4e;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #f0ad4e;
                        color: white;
                    }
                """
    
    def set_status(self, row, status):
        """Set attendance status for a row."""
        status_widget = self.attendance_table.cellWidget(row, 3)
        if status_widget:
            buttons = status_widget.findChildren(QtWidgets.QPushButton)
            for btn in buttons:
                if btn.text() == status:
                    btn.setChecked(True)
                    btn.setStyleSheet(self.get_status_button_style(status, True))
                else:
                    btn.setChecked(False)
                    btn.setStyleSheet(self.get_status_button_style(btn.text(), False))
        
        self.update_attendance_stats()
    
    def update_attendance_stats(self):
        """Update attendance statistics."""
        present_count = 0
        absent_count = 0
        half_day_count = 0
        
        for row in range(self.attendance_table.rowCount()):
            status_widget = self.attendance_table.cellWidget(row, 3)
            if status_widget:
                buttons = status_widget.findChildren(QtWidgets.QPushButton)
                for btn in buttons:
                    if btn.isChecked():
                        if btn.text() == "Present":
                            present_count += 1
                        elif btn.text() == "Absent":
                            absent_count += 1
                        elif btn.text() == "Half-Day":
                            half_day_count += 1
        
        self.stats_present.setText(f"Present: {present_count}")
        self.stats_absent.setText(f"Absent: {absent_count}")
        self.stats_half.setText(f"Half-Day: {half_day_count}")
        self.stats_total.setText(f"Total: {self.attendance_table.rowCount()}")
    
    def mark_all_present(self):
        """Mark all labourers as present."""
        for row in range(self.attendance_table.rowCount()):
            self.set_status(row, "Present")
    
    def mark_all_absent(self):
        """Mark all labourers as absent."""
        for row in range(self.attendance_table.rowCount()):
            self.set_status(row, "Absent")
    
    def show_monthly_attendance_dialog(self):
        """Show monthly attendance history dialog."""
        dialog = MonthlyAttendanceDialog(self)
        dialog.exec_()
    
    def save_bulk_attendance(self):
        """Save attendance for all labourers on selected date."""
        try:
            date = self.attendance_date.date().toString("yyyy-MM-dd")
            attendance_records = []
            
            for row in range(self.attendance_table.rowCount()):
                labour_id = self.attendance_table.item(row, 1).data(QtCore.Qt.UserRole)
                
                # Get status from buttons
                status = "Present"
                status_widget = self.attendance_table.cellWidget(row, 3)
                if status_widget:
                    buttons = status_widget.findChildren(QtWidgets.QPushButton)
                    for btn in buttons:
                        if btn.isChecked():
                            status = btn.text()
                            break
                
                overtime_spin = self.attendance_table.cellWidget(row, 4)
                notes_item = self.attendance_table.item(row, 5)
                
                attendance_records.append({
                    "labour_id": labour_id,
                    "status": status,
                    "overtime_hours": overtime_spin.value() if overtime_spin else 0,
                    "notes": notes_item.text() if notes_item else ""
                })
            
            payload = {
                "date": date,
                "attendance_records": attendance_records
            }
            
            response = requests.post("http://localhost:8000/attendance/bulk", json=payload)
            response.raise_for_status()
            
            QtWidgets.QMessageBox.information(self, "Success", "Attendance saved successfully!")
            
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save attendance: {str(e)}")
    
    def load_monthly_attendance(self):
        """Load attendance for entire month."""
        try:
            month = self.attendance_month.currentIndex() + 1
            year = self.attendance_year.value()
            
            response = requests.get("http://localhost:8000/attendance", params={"month": month, "year": year})
            response.raise_for_status()
            
            result = response.json()
            attendance_records = result['data']
            
            self.attendance_table.setRowCount(0)
            
            for record in attendance_records:
                row = self.attendance_table.rowCount()
                self.attendance_table.insertRow(row)
                
                self.attendance_table.setItem(row, 0, QtWidgets.QTableWidgetItem(record['full_name']))
                self.attendance_table.setItem(row, 1, QtWidgets.QTableWidgetItem(record['position']))
                
                # Status (read-only)
                status_item = QtWidgets.QTableWidgetItem(record['status'])
                status_item.setFlags(status_item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.attendance_table.setItem(row, 2, status_item)
                
                # Overtime (read-only)
                overtime_item = QtWidgets.QTableWidgetItem(str(record['overtime_hours']))
                overtime_item.setFlags(overtime_item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.attendance_table.setItem(row, 3, overtime_item)
                
                # Notes
                notes_item = QtWidgets.QTableWidgetItem(record.get('notes', ''))
                self.attendance_table.setItem(row, 4, notes_item)
                
                # Date
                self.attendance_table.setItem(row, 5, QtWidgets.QTableWidgetItem(str(record['date'])))
            
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load monthly attendance: {str(e)}")
    
    def calculate_all_payroll(self):
        """Calculate payroll for all active labourers."""
        try:
            month = self.payroll_month.currentIndex() + 1
            year = self.payroll_year.value()
            
            # Get all active labourers
            response = requests.get("http://localhost:8000/labourers", params={"status": "Active"})
            response.raise_for_status()
            labourers = response.json()['data']
            
            success_count = 0
            for labour in labourers:
                try:
                    payload = {
                        "labour_id": labour['id'],
                        "month": month,
                        "year": year,
                        "bonus_amount": 0.0,
                        "deduction_amount": 0.0
                    }
                    
                    response = requests.post("http://localhost:8000/payroll/calculate", json=payload)
                    response.raise_for_status()
                    success_count += 1
                except:
                    continue
            
            QtWidgets.QMessageBox.information(
                self, 
                "Success", 
                f"Calculated payroll for {success_count} labourers!"
            )
            self.load_payroll()
            
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to calculate payroll: {str(e)}")
    
    def load_payroll(self):
        """Load payroll records."""
        try:
            month = self.payroll_month.currentIndex() + 1
            year = self.payroll_year.value()
            status = self.payroll_status_filter.currentText()
            
            params = {"month": month, "year": year}
            if status != "All":
                params['status'] = status
            
            response = requests.get("http://localhost:8000/payroll", params=params)
            response.raise_for_status()
            
            result = response.json()
            payroll_records = result['data']
            
            self.populate_payroll_table(payroll_records)
            self.update_payroll_statistics(payroll_records)
            
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load payroll: {str(e)}")
    
    def populate_payroll_table(self, payroll_records):
        """Populate payroll table with data."""
        self.payroll_table.setRowCount(0)
        
        for payroll in payroll_records:
            row = self.payroll_table.rowCount()
            self.payroll_table.insertRow(row)
            
            # Store payroll data
            name_item = QtWidgets.QTableWidgetItem(payroll['full_name'])
            name_item.setData(QtCore.Qt.UserRole, payroll)
            self.payroll_table.setItem(row, 0, name_item)
            
            # Position
            self.payroll_table.setItem(row, 1, QtWidgets.QTableWidgetItem(payroll['position']))
            
            # Pay Type
            pay_type = payroll['pay_type'].replace('_', ' ')
            self.payroll_table.setItem(row, 2, QtWidgets.QTableWidgetItem(pay_type))
            
            # Working Days
            self.payroll_table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{payroll['total_working_days']:.1f}"))
            
            # Base Earning
            self.payroll_table.setItem(row, 4, QtWidgets.QTableWidgetItem(f"৳ {payroll['base_earning']:,.2f}"))
            
            # Bonus - Editable spinbox
            bonus_spin = QtWidgets.QDoubleSpinBox()
            bonus_spin.setRange(0, 999999)
            bonus_spin.setValue(float(payroll['bonus_amount']))
            bonus_spin.setPrefix("৳ ")
            bonus_spin.setDecimals(2)
            bonus_spin.setStyleSheet("""
                QDoubleSpinBox {
                    padding: 5px;
                    border: 2px solid #A3B18A;
                    border-radius: 3px;
                }
            """)
            bonus_spin.valueChanged.connect(lambda val, r=row: self.update_payroll_total(r))
            self.payroll_table.setCellWidget(row, 5, bonus_spin)
            
            # Deduction - Editable spinbox
            deduction_spin = QtWidgets.QDoubleSpinBox()
            deduction_spin.setRange(0, 999999)
            deduction_spin.setValue(float(payroll['deduction_amount']))
            deduction_spin.setPrefix("৳ ")
            deduction_spin.setDecimals(2)
            deduction_spin.setStyleSheet("""
                QDoubleSpinBox {
                    padding: 5px;
                    border: 2px solid #d9534f;
                    border-radius: 3px;
                }
            """)
            deduction_spin.valueChanged.connect(lambda val, r=row: self.update_payroll_total(r))
            self.payroll_table.setCellWidget(row, 6, deduction_spin)
            
            # Total Payable
            total_item = QtWidgets.QTableWidgetItem(f"৳ {payroll['total_payable']:,.2f}")
            total_item.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
            total_item.setForeground(QtGui.QColor("#344E41"))
            self.payroll_table.setItem(row, 7, total_item)
            
            # Status
            status = payroll['payment_status']
            status_item = QtWidgets.QTableWidgetItem(status)
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            if status == "Paid":
                status_item.setBackground(QtGui.QColor("#5cb85c"))
                status_item.setForeground(QtGui.QColor("white"))
            else:
                status_item.setBackground(QtGui.QColor("#f0ad4e"))
                status_item.setForeground(QtGui.QColor("white"))
            self.payroll_table.setItem(row, 8, status_item)
            
            # Actions
            actions_widget = self.create_payroll_actions(payroll['id'], payroll['labour_id'], status)
            self.payroll_table.setCellWidget(row, 9, actions_widget)
    
    def update_payroll_statistics(self, payroll_records):
        """Update payroll summary statistics."""
        if not payroll_records:
            self.payroll_stats_total.setText("Total: ৳ 0.00")
            self.payroll_stats_pending.setText("Pending: ৳ 0.00")
            self.payroll_stats_paid.setText("Paid: ৳ 0.00")
            self.payroll_stats_count.setText("Labourers: 0")
            self.payroll_stats_avg.setText("Average: ৳ 0.00")
            return
        
        total_amount = sum(float(p['total_payable']) for p in payroll_records)
        pending_amount = sum(float(p['total_payable']) for p in payroll_records if p['payment_status'] == 'Pending')
        paid_amount = sum(float(p['total_payable']) for p in payroll_records if p['payment_status'] == 'Paid')
        count = len(payroll_records)
        avg_amount = total_amount / count if count > 0 else 0
        
        self.payroll_stats_total.setText(f"Total: ৳ {total_amount:,.2f}")
        self.payroll_stats_pending.setText(f"Pending: ৳ {pending_amount:,.2f}")
        self.payroll_stats_paid.setText(f"Paid: ৳ {paid_amount:,.2f}")
        self.payroll_stats_count.setText(f"Labourers: {count}")
        self.payroll_stats_avg.setText(f"Average: ৳ {avg_amount:,.2f}")
    
    def update_payroll_total(self, row):
        """Recalculate total payable when bonus or deduction changes."""
        try:
            # Get base earning from payroll data
            name_item = self.payroll_table.item(row, 0)
            payroll_data = name_item.data(QtCore.Qt.UserRole)
            base_earning = float(payroll_data['base_earning'])
            
            # Get current bonus and deduction from spinboxes
            bonus_widget = self.payroll_table.cellWidget(row, 5)
            deduction_widget = self.payroll_table.cellWidget(row, 6)
            
            bonus = bonus_widget.value()
            deduction = deduction_widget.value()
            
            # Calculate new total
            total_payable = base_earning + bonus - deduction
            
            # Update total column
            total_item = self.payroll_table.item(row, 7)
            total_item.setText(f"৳ {total_payable:,.2f}")
            
            # Update stored data
            payroll_data['bonus_amount'] = bonus
            payroll_data['deduction_amount'] = deduction
            payroll_data['total_payable'] = total_payable
            name_item.setData(QtCore.Qt.UserRole, payroll_data)
            
        except Exception as e:
            print(f"Error updating payroll total: {e}")
    
    def create_payroll_actions(self, payroll_id, labour_id, current_status):
        """Create action buttons for payroll row."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        if current_status == "Pending":
            # Recalculate button
            recalc_btn = QtWidgets.QPushButton("🔄")
            recalc_btn.setFixedSize(35, 30)
            recalc_btn.setToolTip("Recalculate payroll")
            recalc_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border-radius: 3px;
                    font-size: 12pt;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            recalc_btn.clicked.connect(lambda: self.recalculate_individual_payroll(payroll_id, labour_id))
            layout.addWidget(recalc_btn)
            
            # Save button to update bonus/deduction
            save_btn = QtWidgets.QPushButton("Save")
            save_btn.setFixedSize(60, 30)
            save_btn.setStyleSheet("""
                QPushButton {
                    background-color: #588157;
                    color: white;
                    border-radius: 3px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #344E41;
                }
            """)
            save_btn.clicked.connect(lambda: self.save_payroll_changes(payroll_id))
            layout.addWidget(save_btn)
            
            # Mark Paid button
            pay_btn = QtWidgets.QPushButton("Mark Paid")
            pay_btn.setFixedSize(80, 30)
            pay_btn.setStyleSheet("""
                QPushButton {
                    background-color: #5cb85c;
                    color: white;
                    border-radius: 3px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #4cae4c;
                }
            """)
            pay_btn.clicked.connect(lambda: self.mark_payroll_paid(payroll_id))
            layout.addWidget(pay_btn)
            
            # Delete button
            delete_btn = QtWidgets.QPushButton("🗑")
            delete_btn.setFixedSize(35, 30)
            delete_btn.setToolTip("Delete payroll")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #d9534f;
                    color: white;
                    border-radius: 3px;
                    font-size: 12pt;
                }
                QPushButton:hover {
                    background-color: #c9302c;
                }
            """)
            delete_btn.clicked.connect(lambda: self.delete_payroll(payroll_id))
            layout.addWidget(delete_btn)
        else:
            paid_label = QtWidgets.QLabel("✓ Paid")
            paid_label.setStyleSheet("color: #5cb85c; font-weight: bold;")
            layout.addWidget(paid_label)
        
        # View History button (always show)
        history_btn = QtWidgets.QPushButton("📋")
        history_btn.setFixedSize(35, 30)
        history_btn.setToolTip("View payment history")
        history_btn.setStyleSheet("""
            QPushButton {
                background-color: #588157;
                color: white;
                border-radius: 3px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #344E41;
            }
        """)
        history_btn.clicked.connect(lambda: self.view_payment_history(labour_id))
        layout.addWidget(history_btn)
        
        layout.addStretch()
        
        return widget
    
    def save_payroll_changes(self, payroll_id):
        """Save bonus/deduction changes without marking as paid."""
        try:
            # Find the row with this payroll_id
            payroll_data = None
            target_row = -1
            for row in range(self.payroll_table.rowCount()):
                name_item = self.payroll_table.item(row, 0)
                data = name_item.data(QtCore.Qt.UserRole)
                if data['id'] == payroll_id:
                    payroll_data = data
                    target_row = row
                    break
            
            if not payroll_data or target_row == -1:
                raise Exception("Payroll record not found in table")
            
            # Get current values directly from spinboxes (most up-to-date)
            bonus_widget = self.payroll_table.cellWidget(target_row, 5)
            deduction_widget = self.payroll_table.cellWidget(target_row, 6)
            
            if not bonus_widget or not deduction_widget:
                raise Exception("Could not find bonus/deduction widgets")
            
            bonus_amount = bonus_widget.value()
            deduction_amount = deduction_widget.value()
            
            # Calculate total
            base_earning = float(payroll_data['base_earning'])
            total_payable = base_earning + bonus_amount - deduction_amount
            
            # Update only bonus/deduction/total
            payload = {
                "bonus_amount": float(bonus_amount),
                "deduction_amount": float(deduction_amount),
                "total_payable": float(total_payable)
            }
            
            response = requests.put(f"http://localhost:8000/payroll/{payroll_id}", json=payload)
            response.raise_for_status()
            
            # Update stored data to keep it in sync
            payroll_data['bonus_amount'] = bonus_amount
            payroll_data['deduction_amount'] = deduction_amount
            payroll_data['total_payable'] = total_payable
            name_item = self.payroll_table.item(target_row, 0)
            name_item.setData(QtCore.Qt.UserRole, payroll_data)
            
            QtWidgets.QMessageBox.information(self, "Success", "Payroll updated successfully!")
            
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "404" in error_msg:
                QtWidgets.QMessageBox.critical(
                    self, 
                    "Error", 
                    f"Payroll record not found (ID: {payroll_id}). Try reloading the payroll data."
                )
            else:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to update payroll: {error_msg}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def mark_payroll_paid(self, payroll_id):
        """Mark payroll as paid."""
        try:
            # Find the row with this payroll_id
            payroll_data = None
            target_row = -1
            for row in range(self.payroll_table.rowCount()):
                name_item = self.payroll_table.item(row, 0)
                data = name_item.data(QtCore.Qt.UserRole)
                if data['id'] == payroll_id:
                    payroll_data = data
                    target_row = row
                    break
            
            if not payroll_data or target_row == -1:
                raise Exception("Payroll record not found in table")
            
            # Get current values directly from spinboxes (most up-to-date)
            bonus_widget = self.payroll_table.cellWidget(target_row, 5)
            deduction_widget = self.payroll_table.cellWidget(target_row, 6)
            
            if bonus_widget and deduction_widget:
                bonus_amount = bonus_widget.value()
                deduction_amount = deduction_widget.value()
                base_earning = float(payroll_data['base_earning'])
                total_payable = base_earning + bonus_amount - deduction_amount
            else:
                # Fallback to stored data if widgets not found
                bonus_amount = float(payroll_data['bonus_amount'])
                deduction_amount = float(payroll_data['deduction_amount'])
                total_payable = float(payroll_data['total_payable'])
            
            # Update with current bonus/deduction values
            payload = {
                "payment_status": "Paid",
                "payment_date": datetime.now().strftime("%Y-%m-%d"),
                "bonus_amount": float(bonus_amount),
                "deduction_amount": float(deduction_amount),
                "total_payable": float(total_payable)
            }
            
            response = requests.put(f"http://localhost:8000/payroll/{payroll_id}", json=payload)
            response.raise_for_status()
            
            QtWidgets.QMessageBox.information(self, "Success", "Payment marked as completed!")
            self.load_payroll()
            
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "404" in error_msg:
                QtWidgets.QMessageBox.critical(
                    self, 
                    "Error", 
                    f"Payroll record not found (ID: {payroll_id}). Try reloading the payroll data."
                )
            else:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to update payment status: {error_msg}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def recalculate_individual_payroll(self, payroll_id, labour_id):
        """Recalculate payroll for a single labour."""
        try:
            month = self.payroll_month.currentIndex() + 1
            year = self.payroll_year.value()
            
            # Get current bonus/deduction from table
            payroll_data = None
            for row in range(self.payroll_table.rowCount()):
                name_item = self.payroll_table.item(row, 0)
                data = name_item.data(QtCore.Qt.UserRole)
                if data['id'] == payroll_id:
                    payroll_data = data
                    break
            
            if not payroll_data:
                raise Exception("Payroll record not found")
            
            # Recalculate with updated attendance (backend will update existing record)
            # The UNIQUE KEY on (labour_id, month, year) ensures ON DUPLICATE KEY UPDATE works
            payload = {
                "labour_id": labour_id,
                "month": month,
                "year": year,
                "bonus_amount": float(payroll_data['bonus_amount']),
                "deduction_amount": float(payroll_data['deduction_amount'])
            }
            
            response = requests.post("http://localhost:8000/payroll/calculate", json=payload)
            response.raise_for_status()
            
            QtWidgets.QMessageBox.information(self, "Success", "Payroll recalculated successfully!")
            self.load_payroll()
            
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to recalculate payroll: {str(e)}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def delete_payroll(self, payroll_id):
        """Delete a payroll record (only pending)."""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this payroll record?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                response = requests.delete(f"http://localhost:8000/payroll/{payroll_id}")
                response.raise_for_status()
                
                QtWidgets.QMessageBox.information(self, "Success", "Payroll deleted successfully!")
                self.load_payroll()
                
            except requests.exceptions.RequestException as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to delete payroll: {str(e)}")
    
    def mark_all_pending_paid(self):
        """Mark all pending payroll as paid."""
        try:
            # Get all pending payroll from current table
            pending_ids = []
            for row in range(self.payroll_table.rowCount()):
                name_item = self.payroll_table.item(row, 0)
                payroll_data = name_item.data(QtCore.Qt.UserRole)
                if payroll_data['payment_status'] == 'Pending':
                    pending_ids.append(payroll_data['id'])
            
            if not pending_ids:
                QtWidgets.QMessageBox.information(self, "Info", "No pending payments to process!")
                return
            
            reply = QtWidgets.QMessageBox.question(
                self,
                "Confirm Bulk Payment",
                f"Mark {len(pending_ids)} pending payments as paid?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            
            if reply == QtWidgets.QMessageBox.Yes:
                success_count = 0
                for payroll_id in pending_ids:
                    try:
                        # Get payroll data and row
                        payroll_data = None
                        target_row = -1
                        for row in range(self.payroll_table.rowCount()):
                            name_item = self.payroll_table.item(row, 0)
                            data = name_item.data(QtCore.Qt.UserRole)
                            if data['id'] == payroll_id:
                                payroll_data = data
                                target_row = row
                                break
                        
                        if payroll_data and target_row >= 0:
                            # Get current values from spinboxes
                            bonus_widget = self.payroll_table.cellWidget(target_row, 5)
                            deduction_widget = self.payroll_table.cellWidget(target_row, 6)
                            
                            if bonus_widget and deduction_widget:
                                bonus_amount = bonus_widget.value()
                                deduction_amount = deduction_widget.value()
                                base_earning = float(payroll_data['base_earning'])
                                total_payable = base_earning + bonus_amount - deduction_amount
                            else:
                                bonus_amount = float(payroll_data['bonus_amount'])
                                deduction_amount = float(payroll_data['deduction_amount'])
                                total_payable = float(payroll_data['total_payable'])
                            
                            payload = {
                                "payment_status": "Paid",
                                "payment_date": datetime.now().strftime("%Y-%m-%d"),
                                "bonus_amount": float(bonus_amount),
                                "deduction_amount": float(deduction_amount),
                                "total_payable": float(total_payable)
                            }
                            
                            response = requests.put(f"http://localhost:8000/payroll/{payroll_id}", json=payload)
                            response.raise_for_status()
                            success_count += 1
                    except:
                        continue
                
                QtWidgets.QMessageBox.information(
                    self, 
                    "Success", 
                    f"Marked {success_count} payments as paid!"
                )
                self.load_payroll()
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def export_payroll_csv(self):
        """Export payroll data to CSV."""
        try:
            import csv
            from datetime import datetime
            
            if self.payroll_table.rowCount() == 0:
                QtWidgets.QMessageBox.information(self, "Info", "No payroll data to export!")
                return
            
            month = self.payroll_month.currentText()
            year = self.payroll_year.value()
            
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Export Payroll",
                f"Payroll_{month}_{year}.csv",
                "CSV Files (*.csv)"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Header
                    writer.writerow([
                        "Name", "Position", "Pay Type", "Working Days",
                        "Base Earning", "Bonus", "Deduction", "Total Payable",
                        "Status", "Month", "Year"
                    ])
                    
                    # Data rows
                    for row in range(self.payroll_table.rowCount()):
                        name_item = self.payroll_table.item(row, 0)
                        payroll_data = name_item.data(QtCore.Qt.UserRole)
                        
                        writer.writerow([
                            payroll_data['full_name'],
                            payroll_data['position'],
                            payroll_data['pay_type'],
                            f"{payroll_data['total_working_days']:.1f}",
                            f"{payroll_data['base_earning']:.2f}",
                            f"{payroll_data['bonus_amount']:.2f}",
                            f"{payroll_data['deduction_amount']:.2f}",
                            f"{payroll_data['total_payable']:.2f}",
                            payroll_data['payment_status'],
                            month,
                            year
                        ])
                
                QtWidgets.QMessageBox.information(self, "Success", f"Payroll exported to {filename}!")
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to export payroll: {str(e)}")
    
    def view_payment_history(self, labour_id):
        """View payment history for a labour."""
        try:
            response = requests.get(f"http://localhost:8000/payroll", params={"labour_id": labour_id})
            response.raise_for_status()
            
            result = response.json()
            history = result['data']
            
            if not history:
                QtWidgets.QMessageBox.information(self, "Info", "No payment history found!")
                return
            
            # Create history dialog
            dialog = PaymentHistoryDialog(self, labour_id, history)
            dialog.exec_()
            
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load payment history: {str(e)}")


class LabourDialog(QtWidgets.QDialog):
    """Dialog for adding/editing labourer."""
    
    def __init__(self, parent=None, labour_id=None):
        super().__init__(parent)
        self.labour_id = labour_id
        self.init_ui()
        
        if labour_id:
            self.load_labourer_data()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle("Add Labour" if not self.labour_id else "Edit Labour")
        self.setMinimumWidth(500)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Form layout
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(15)
        
        # Full Name
        self.name_input = QtWidgets.QLineEdit()
        form_layout.addRow("Full Name *:", self.name_input)
        
        # Phone
        self.phone_input = QtWidgets.QLineEdit()
        form_layout.addRow("Phone Number:", self.phone_input)
        
        # National ID
        self.nid_input = QtWidgets.QLineEdit()
        form_layout.addRow("National ID:", self.nid_input)
        
        # Address
        self.address_input = QtWidgets.QTextEdit()
        self.address_input.setMaximumHeight(80)
        form_layout.addRow("Address:", self.address_input)
        
        # Position
        self.position_input = QtWidgets.QComboBox()
        self.position_input.addItems(["Supervisor", "Farmhand", "Driver", "Guard", "Cleaner", "Other"])
        self.position_input.setEditable(True)
        form_layout.addRow("Position *:", self.position_input)
        
        # Joining Date
        self.joining_date_input = QtWidgets.QDateEdit()
        self.joining_date_input.setDate(QtCore.QDate.currentDate())
        self.joining_date_input.setCalendarPopup(True)
        form_layout.addRow("Joining Date *:", self.joining_date_input)
        
        # Pay Type
        self.pay_type_input = QtWidgets.QComboBox()
        self.pay_type_input.addItems(["Monthly_Salary", "Daily_Wage"])
        form_layout.addRow("Pay Type *:", self.pay_type_input)
        
        # Base Rate
        self.base_rate_input = QtWidgets.QDoubleSpinBox()
        self.base_rate_input.setRange(0, 1000000)
        self.base_rate_input.setDecimals(2)
        self.base_rate_input.setPrefix("৳ ")
        form_layout.addRow("Base Rate *:", self.base_rate_input)
        
        # Status
        self.status_input = QtWidgets.QComboBox()
        self.status_input.addItems(["Active", "Inactive"])
        form_layout.addRow("Status:", self.status_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QtWidgets.QPushButton("Save")
        save_btn.clicked.connect(self.save_labourer)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #588157;
                color: white;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #344E41;
            }
        """)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def load_labourer_data(self):
        """Load existing labourer data."""
        try:
            response = requests.get(f"http://localhost:8000/labourers/{self.labour_id}")
            response.raise_for_status()
            
            labour = response.json()['data']
            
            self.name_input.setText(labour['full_name'])
            self.phone_input.setText(labour.get('phone_number', ''))
            self.nid_input.setText(labour.get('national_id', ''))
            self.address_input.setPlainText(labour.get('address', ''))
            self.position_input.setCurrentText(labour['position'])
            
            # Set joining date
            date_parts = str(labour['joining_date']).split('-')
            if len(date_parts) == 3:
                self.joining_date_input.setDate(QtCore.QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
            
            self.pay_type_input.setCurrentText(labour['pay_type'])
            self.base_rate_input.setValue(float(labour['base_rate']))
            self.status_input.setCurrentText(labour['status'])
            
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load labourer data: {str(e)}")
    
    def save_labourer(self):
        """Save labourer data."""
        # Validation
        if not self.name_input.text().strip():
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Full name is required!")
            return
        
        if not self.position_input.currentText().strip():
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Position is required!")
            return
        
        if self.base_rate_input.value() <= 0:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Base rate must be greater than 0!")
            return
        
        # Prepare data
        data = {
            "full_name": self.name_input.text().strip(),
            "phone_number": self.phone_input.text().strip() or None,
            "national_id": self.nid_input.text().strip() or None,
            "address": self.address_input.toPlainText().strip() or None,
            "position": self.position_input.currentText().strip(),
            "joining_date": self.joining_date_input.date().toString("yyyy-MM-dd"),
            "pay_type": self.pay_type_input.currentText(),
            "base_rate": self.base_rate_input.value(),
            "status": self.status_input.currentText()
        }
        
        try:
            if self.labour_id:
                # Update existing
                response = requests.put(f"http://localhost:8000/labourers/{self.labour_id}", json=data)
            else:
                # Create new
                response = requests.post("http://localhost:8000/labourers", json=data)
            
            response.raise_for_status()
            
            QtWidgets.QMessageBox.information(self, "Success", "Labourer saved successfully!")
            self.accept()
            
        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            try:
                if hasattr(e, 'response') and e.response is not None:
                    error_data = e.response.json()
                    error_detail = error_data.get('detail', str(e))
            except:
                pass
            
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save labourer:\n\n{error_detail}")


class MonthlyAttendanceDialog(QtWidgets.QDialog):
    """Dialog for viewing monthly attendance history."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_page = parent
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle("Monthly Attendance History")
        self.setMinimumSize(900, 600)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Month/Year selector
        controls_layout = QtWidgets.QHBoxLayout()
        
        month_label = QtWidgets.QLabel("Select Month:")
        month_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        controls_layout.addWidget(month_label)
        
        self.month_combo = QtWidgets.QComboBox()
        self.month_combo.addItems([
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ])
        self.month_combo.setCurrentIndex(datetime.now().month - 1)
        self.month_combo.setFixedWidth(120)
        controls_layout.addWidget(self.month_combo)
        
        self.year_spin = QtWidgets.QSpinBox()
        self.year_spin.setRange(2020, 2100)
        self.year_spin.setValue(datetime.now().year)
        self.year_spin.setFixedWidth(80)
        controls_layout.addWidget(self.year_spin)
        
        load_btn = QtWidgets.QPushButton("Load")
        load_btn.clicked.connect(self.load_monthly_data)
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #588157;
                color: white;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #344E41;
            }
        """)
        controls_layout.addWidget(load_btn)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Attendance table
        self.history_table = QtWidgets.QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Name", "Position", "Date", "Status", "Overtime Hours", "Notes"
        ])
        
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        for i in range(1, 6):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setAlternatingRowColors(True)
        
        self.history_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #EBEAE3;
                border-radius: 4px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #588157;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.history_table)
        
        # Close button
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        layout.addWidget(close_btn, alignment=QtCore.Qt.AlignRight)
        
        # Load initial data
        self.load_monthly_data()
    
    def load_monthly_data(self):
        """Load monthly attendance data."""
        try:
            month = self.month_combo.currentIndex() + 1
            year = self.year_spin.value()
            
            response = requests.get("http://localhost:8000/attendance", params={"month": month, "year": year})
            response.raise_for_status()
            
            result = response.json()
            attendance_records = result['data']
            
            self.history_table.setRowCount(0)
            
            for record in attendance_records:
                row = self.history_table.rowCount()
                self.history_table.insertRow(row)
                
                self.history_table.setItem(row, 0, QtWidgets.QTableWidgetItem(record['full_name']))
                self.history_table.setItem(row, 1, QtWidgets.QTableWidgetItem(record['position']))
                self.history_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(record['date'])))
                
                # Status with color
                status_item = QtWidgets.QTableWidgetItem(record['status'])
                status_item.setTextAlignment(QtCore.Qt.AlignCenter)
                if record['status'] == "Present":
                    status_item.setBackground(QtGui.QColor("#5cb85c"))
                    status_item.setForeground(QtGui.QColor("white"))
                elif record['status'] == "Absent":
                    status_item.setBackground(QtGui.QColor("#d9534f"))
                    status_item.setForeground(QtGui.QColor("white"))
                else:
                    status_item.setBackground(QtGui.QColor("#f0ad4e"))
                    status_item.setForeground(QtGui.QColor("white"))
                self.history_table.setItem(row, 3, status_item)
                
                self.history_table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(record['overtime_hours'])))
                self.history_table.setItem(row, 5, QtWidgets.QTableWidgetItem(record.get('notes', '')))
            
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load monthly attendance: {str(e)}")


class PaymentHistoryDialog(QtWidgets.QDialog):
    """Dialog for viewing payment history of a labour."""
    
    def __init__(self, parent, labour_id, history_data):
        super().__init__(parent)
        self.labour_id = labour_id
        self.history_data = history_data
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        # Get labour name from first record
        labour_name = self.history_data[0]['full_name'] if self.history_data else "Unknown"
        self.setWindowTitle(f"Payment History - {labour_name}")
        self.setMinimumSize(900, 500)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Title
        title = QtWidgets.QLabel(f"Payment History for {labour_name}")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #344E41; padding: 10px;")
        layout.addWidget(title)
        
        # Statistics
        stats_layout = QtWidgets.QHBoxLayout()
        
        total_payments = len(self.history_data)
        total_amount = sum(float(h['total_payable']) for h in self.history_data)
        paid_amount = sum(float(h['total_payable']) for h in self.history_data if h['payment_status'] == 'Paid')
        pending_amount = sum(float(h['total_payable']) for h in self.history_data if h['payment_status'] == 'Pending')
        
        stats_label = QtWidgets.QLabel(
            f"Total Records: {total_payments} | "
            f"Total Amount: ৳ {total_amount:,.2f} | "
            f"Paid: ৳ {paid_amount:,.2f} | "
            f"Pending: ৳ {pending_amount:,.2f}"
        )
        stats_label.setStyleSheet("""
            background-color: #F8F9FA;
            border: 2px solid #588157;
            border-radius: 5px;
            padding: 10px;
            font-size: 11pt;
            color: #344E41;
        """)
        stats_layout.addWidget(stats_label)
        layout.addLayout(stats_layout)
        
        # History table
        self.history_table = QtWidgets.QTableWidget()
        self.history_table.setColumnCount(10)
        self.history_table.setHorizontalHeaderLabels([
            "Month", "Year", "Working Days", "Base Earning", 
            "Bonus", "Deduction", "Total", "Status", "Payment Date", "Created"
        ])
        
        header = self.history_table.horizontalHeader()
        for i in range(10):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        
        self.history_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #EBEAE3;
                border-radius: 4px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #588157;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Populate table
        for record in self.history_data:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            # Month
            month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            month_text = month_names[record['month'] - 1] if 1 <= record['month'] <= 12 else str(record['month'])
            self.history_table.setItem(row, 0, QtWidgets.QTableWidgetItem(month_text))
            
            # Year
            self.history_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(record['year'])))
            
            # Working Days
            self.history_table.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{record['total_working_days']:.1f}"))
            
            # Base Earning
            self.history_table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"৳ {record['base_earning']:,.2f}"))
            
            # Bonus
            self.history_table.setItem(row, 4, QtWidgets.QTableWidgetItem(f"৳ {record['bonus_amount']:,.2f}"))
            
            # Deduction
            self.history_table.setItem(row, 5, QtWidgets.QTableWidgetItem(f"৳ {record['deduction_amount']:,.2f}"))
            
            # Total
            total_item = QtWidgets.QTableWidgetItem(f"৳ {record['total_payable']:,.2f}")
            total_item.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
            self.history_table.setItem(row, 6, total_item)
            
            # Status
            status = record['payment_status']
            status_item = QtWidgets.QTableWidgetItem(status)
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            if status == "Paid":
                status_item.setBackground(QtGui.QColor("#5cb85c"))
                status_item.setForeground(QtGui.QColor("white"))
            else:
                status_item.setBackground(QtGui.QColor("#f0ad4e"))
                status_item.setForeground(QtGui.QColor("white"))
            self.history_table.setItem(row, 7, status_item)
            
            # Payment Date
            payment_date = str(record.get('payment_date', 'N/A'))
            self.history_table.setItem(row, 8, QtWidgets.QTableWidgetItem(payment_date))
            
            # Created Date
            created = str(record.get('created_at', 'N/A'))[:10]
            self.history_table.setItem(row, 9, QtWidgets.QTableWidgetItem(created))
        
        layout.addWidget(self.history_table)
        
        # Close button
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.setFixedHeight(35)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #588157;
                color: white;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #344E41;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=QtCore.Qt.AlignRight)
