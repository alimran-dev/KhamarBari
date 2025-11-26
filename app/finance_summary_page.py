from PyQt5 import QtWidgets, QtCore, QtGui
import requests
import os
from datetime import datetime, timedelta
import json

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


class FinanceSummaryPage(QtWidgets.QWidget):
    """Finance Summary Dashboard with analytics"""
    
    def __init__(self, user_email):
        super().__init__()
        self.user_email = user_email
        self.entries = []
        self.summary_data = {}
        
        self.setStyleSheet("""
            QWidget {
                background-color: #EBEAE3;
                color: #344E41;
            }
            QLabel {
                color: #344E41;
                background: transparent;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #A3B18A;
                border-radius: 10px;
                gridline-color: #d0d0d0;
            }
            QTableWidget::item {
                padding: 10px;
                color: #344E41;
            }
            QTableWidget::item:selected {
                background-color: #A3B18A;
                color: white;
            }
            QHeaderView::section {
                background-color: #344E41;
                color: white;
                padding: 12px;
                font-weight: bold;
                font-size: 11pt;
                border: none;
            }
            QComboBox, QDateEdit, QPushButton#filterBtn {
                background-color: #D8E2D1;
                border: 1px solid #A3B18A;
                border-radius: 8px;
                padding: 8px;
                color: #344E41;
                min-height: 35px;
                font-size: 11pt;
            }
            QComboBox::drop-down {
                border: none;
                background: transparent;
            }
            QPushButton {
                background-color: #588157;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 11pt;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #4A6A55;
            }
            QPushButton#exportBtn {
                background-color: #588157;
            }
            QPushButton#exportBtn:hover {
                background-color: #4A6A55;
            }
            QScrollArea {
                border: none;
                background-color: #EBEAE3;
            }
        """)
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize the UI"""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)
        
        # Scroll area wrapper
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        scroll_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(scroll_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(20)
        
        # Title and Date Range
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(15)
        
        title = QtWidgets.QLabel("📊 Expense & Income Summary")
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #344E41; background: transparent;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Date Range Filter
        date_label = QtWidgets.QLabel("Period:")
        date_label.setStyleSheet("font-size: 11pt; font-weight: bold; background: transparent; padding-right: 5px;")
        header_layout.addWidget(date_label)
        
        self.period_combo = QtWidgets.QComboBox()
        self.period_combo.addItems(["Last 7 Days", "Last 30 Days", "Last 3 Months", "This Year", "All Time", "Custom"])
        self.period_combo.setCurrentIndex(1)  # Default: Last 30 Days
        self.period_combo.setMinimumWidth(150)
        self.period_combo.currentIndexChanged.connect(self.on_period_changed)
        header_layout.addWidget(self.period_combo)
        
        content_layout.addLayout(header_layout)
        
        # Summary Cards
        cards_layout = QtWidgets.QHBoxLayout()
        cards_layout.setSpacing(20)
        
        # Total Income Card
        self.income_card = self.create_summary_card(
            "Total Income (Period)",
            "৳0",
            "#588157",
            "💰"
        )
        cards_layout.addWidget(self.income_card)
        
        # Total Expense Card
        self.expense_card = self.create_summary_card(
            "Total Expense (Period)",
            "৳0",
            "#CC6666",
            "💸"
        )
        cards_layout.addWidget(self.expense_card)
        
        # Net Profit/Loss Card
        self.profit_card = self.create_summary_card(
            "Net Profit/Loss",
            "৳0",
            "#344E41",
            "📊"
        )
        cards_layout.addWidget(self.profit_card)
        
        # Top Expense Category Card
        self.top_category_card = self.create_summary_card(
            "Top Expense Category",
            "N/A",
            "#3A5A40",
            "🔝"
        )
        cards_layout.addWidget(self.top_category_card)
        
        content_layout.addLayout(cards_layout)
        
        # Charts Section
        charts_layout = QtWidgets.QHBoxLayout()
        charts_layout.setSpacing(20)
        
        # Expense vs Income Chart (Placeholder)
        chart1_group = QtWidgets.QGroupBox("📈 Expense vs Income Trend")
        chart1_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #B5C9A9;
                border-radius: 12px;
                font-weight: bold;
                font-size: 11pt;
                color: #344E41;
                padding: 20px;
                padding-top: 25px;
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                background: transparent;
            }
        """)
        chart1_layout = QtWidgets.QVBoxLayout(chart1_group)
        chart1_layout.setContentsMargins(10, 10, 10, 10)
        
        self.chart1_label = QtWidgets.QLabel()
        self.chart1_label.setAlignment(QtCore.Qt.AlignCenter)
        self.chart1_label.setMinimumHeight(220)
        self.chart1_label.setWordWrap(True)
        self.chart1_label.setStyleSheet("background-color: #F5F5F5; border-radius: 8px; padding: 20px; color: #344E41;")
        chart1_layout.addWidget(self.chart1_label)
        
        charts_layout.addWidget(chart1_group)
        
        # Category Breakdown Chart (Placeholder)
        chart2_group = QtWidgets.QGroupBox("🍰 Category Breakdown (Expense)")
        chart2_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #B5C9A9;
                border-radius: 12px;
                font-weight: bold;
                font-size: 11pt;
                color: #344E41;
                padding: 20px;
                padding-top: 25px;
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                background: transparent;
            }
        """)
        chart2_layout = QtWidgets.QVBoxLayout(chart2_group)
        chart2_layout.setContentsMargins(10, 10, 10, 10)
        
        self.chart2_label = QtWidgets.QLabel()
        self.chart2_label.setAlignment(QtCore.Qt.AlignCenter)
        self.chart2_label.setWordWrap(True)
        self.chart2_label.setMinimumHeight(220)
        self.chart2_label.setStyleSheet("background-color: #F5F5F5; border-radius: 8px; padding: 20px; color: #344E41;")
        chart2_layout.addWidget(self.chart2_label)
        
        charts_layout.addWidget(chart2_group)
        
        content_layout.addLayout(charts_layout)
        
        # Recent Entries Table
        table_header = QtWidgets.QHBoxLayout()
        table_header.setSpacing(15)
        
        table_title = QtWidgets.QLabel("📋 Recent Entries")
        table_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #344E41; background: transparent;")
        table_header.addWidget(table_title)
        
        table_header.addStretch()
        
        # Filters
        filter_label = QtWidgets.QLabel("Category:")
        filter_label.setStyleSheet("font-size: 11pt; font-weight: bold; background: transparent; padding-right: 5px;")
        table_header.addWidget(filter_label)
        
        self.category_filter = QtWidgets.QComboBox()
        self.category_filter.addItem("All", None)
        self.category_filter.setObjectName("filterBtn")
        self.category_filter.currentIndexChanged.connect(self.apply_filters)
        table_header.addWidget(self.category_filter)
        
        type_label = QtWidgets.QLabel("Type:")
        type_label.setStyleSheet("font-size: 10pt; font-weight: bold;")
        table_header.addWidget(type_label)
        
        self.type_filter = QtWidgets.QComboBox()
        self.type_filter.addItems(["All", "Expense", "Income"])
        self.type_filter.setObjectName("filterBtn")
        self.type_filter.currentIndexChanged.connect(self.apply_filters)
        table_header.addWidget(self.type_filter)
        
        # Export Buttons
        self.csv_btn = QtWidgets.QPushButton("📄 Export CSV")
        self.csv_btn.setObjectName("exportBtn")
        self.csv_btn.clicked.connect(self.export_csv)
        table_header.addWidget(self.csv_btn)
        
        self.pdf_btn = QtWidgets.QPushButton("📑 Generate Report (PDF)")
        self.pdf_btn.setObjectName("exportBtn")
        self.pdf_btn.clicked.connect(self.generate_pdf_report)
        table_header.addWidget(self.pdf_btn)
        
        main_layout.addLayout(table_header)
        
        # Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Date", "Type", "Category", "Amount", "Description", "Receipt", "Actions"
        ])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setMinimumHeight(350)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        
        content_layout.addWidget(self.table)
        
        # Set scroll widget and add to main layout
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
    
    def create_summary_card(self, title, value, color, icon):
        """Create a summary card widget"""
        card = QtWidgets.QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #B5C9A9;
                border-radius: 15px;
            }}
        """)
        card.setMinimumHeight(140)
        card.setMaximumHeight(160)
        
        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)
        
        # Icon and Title
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(10)
        icon_label = QtWidgets.QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 28pt; color: {color}; background: transparent;")
        header_layout.addWidget(icon_label)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("font-size: 10pt; font-weight: bold; color: #588157; background: transparent;")
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label, 1)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Value
        value_label = QtWidgets.QLabel(value)
        value_label.setStyleSheet(f"font-size: 22pt; font-weight: bold; color: {color}; background: transparent;")
        value_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(value_label)
        
        layout.addStretch()
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
    
    def get_date_range(self):
        """Get start and end date based on selected period"""
        period = self.period_combo.currentText()
        today = datetime.now().date()
        
        if period == "Last 7 Days":
            start_date = today - timedelta(days=7)
            return start_date, today
        elif period == "Last 30 Days":
            start_date = today - timedelta(days=30)
            return start_date, today
        elif period == "Last 3 Months":
            start_date = today - timedelta(days=90)
            return start_date, today
        elif period == "This Year":
            start_date = datetime(today.year, 1, 1).date()
            return start_date, today
        elif period == "All Time":
            return None, None
        else:  # Custom
            # TODO: Show date picker dialog
            return None, None
    
    def on_period_changed(self):
        """Handle period selection change"""
        self.load_data()
    
    def load_data(self):
        """Load financial data from API"""
        try:
            start_date, end_date = self.get_date_range()
            
            # Load summary
            params = {}
            if start_date:
                params["start_date"] = start_date.strftime("%Y-%m-%d")
            if end_date:
                params["end_date"] = end_date.strftime("%Y-%m-%d")
            
            response = requests.get(f"{API_URL}/finance/summary/{self.user_email}", params=params)
            if response.status_code == 200:
                data = response.json()
                self.summary_data = data.get("data", {})
                self.update_summary_cards()
                self.update_charts()
            
            # Load entries
            response = requests.get(f"{API_URL}/finance/entries/{self.user_email}", params=params)
            if response.status_code == 200:
                data = response.json()
                self.entries = data.get("data", [])
                self.populate_category_filter()
                self.populate_table()
        
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to load data: {str(e)}")
    
    def update_summary_cards(self):
        """Update summary card values"""
        total_income = self.summary_data.get("total_income", 0)
        total_expense = self.summary_data.get("total_expense", 0)
        net_profit = self.summary_data.get("net_profit", 0)
        top_category = self.summary_data.get("top_expense_category", "N/A")
        
        self.income_card.value_label.setText(f"৳{total_income:,.2f}")
        self.expense_card.value_label.setText(f"৳{total_expense:,.2f}")
        
        # Color code profit/loss
        if net_profit >= 0:
            self.profit_card.value_label.setText(f"+৳{net_profit:,.2f}")
            self.profit_card.value_label.setStyleSheet("font-size: 20pt; font-weight: bold; color: #588157;")
        else:
            self.profit_card.value_label.setText(f"-৳{abs(net_profit):,.2f}")
            self.profit_card.value_label.setStyleSheet("font-size: 20pt; font-weight: bold; color: #CC6666;")
        
        self.top_category_card.value_label.setText(top_category)
        self.top_category_card.value_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #3A5A40;")
    
    def update_charts(self):
        """Update chart visualizations"""
        # Get category breakdown
        breakdown = self.summary_data.get("category_breakdown", [])
        
        # Chart 1: Line chart placeholder
        daily_data = self.summary_data.get("daily_data", [])
        if daily_data:
            chart1_text = "📈 Daily Income vs Expense Trend\n\n"
            chart1_text += f"Data points: {len(daily_data)}\n"
            chart1_text += "Visual chart would be displayed here"
        else:
            chart1_text = "No data available for the selected period"
        
        self.chart1_label.setText(chart1_text)
        self.chart1_label.setStyleSheet(
            "background-color: #F5F5F5; border-radius: 8px; padding: 20px; "
            "font-size: 11pt; color: #344E41;"
        )
        
        # Chart 2: Pie chart breakdown
        expense_breakdown = [item for item in breakdown if item["type"] == "expense"]
        if expense_breakdown:
            chart2_text = "🥧 Expense Category Distribution\n\n"
            total = sum(item["amount"] for item in expense_breakdown)
            for item in expense_breakdown[:5]:  # Top 5
                percentage = (item["amount"] / total * 100) if total > 0 else 0
                chart2_text += f"{item['category']}: {percentage:.1f}%\n"
        else:
            chart2_text = "No expense data available"
        
        self.chart2_label.setText(chart2_text)
        self.chart2_label.setStyleSheet(
            "background-color: #F5F5F5; border-radius: 8px; padding: 20px; "
            "font-size: 11pt; color: #344E41;"
        )
    
    def populate_category_filter(self):
        """Populate category filter dropdown"""
        self.category_filter.clear()
        self.category_filter.addItem("All", None)
        
        # Get unique categories from entries
        categories = set()
        for entry in self.entries:
            categories.add((entry["category_id"], entry["category_name"]))
        
        for cat_id, cat_name in sorted(categories, key=lambda x: x[1]):
            self.category_filter.addItem(cat_name, cat_id)
    
    def apply_filters(self):
        """Apply filters to table"""
        self.populate_table()
    
    def populate_table(self):
        """Populate the entries table"""
        # Get filter values
        type_filter = self.type_filter.currentText().lower()
        category_id = self.category_filter.currentData()
        
        # Filter entries
        filtered_entries = []
        for entry in self.entries:
            # Type filter
            if type_filter != "all" and entry["entry_type"] != type_filter:
                continue
            
            # Category filter
            if category_id and entry["category_id"] != category_id:
                continue
            
            filtered_entries.append(entry)
        
        # Populate table
        self.table.setRowCount(len(filtered_entries))
        
        for row, entry in enumerate(filtered_entries):
            # Date
            date_item = QtWidgets.QTableWidgetItem(entry["date"])
            self.table.setItem(row, 0, date_item)
            
            # Type
            type_text = entry["entry_type"].capitalize()
            type_item = QtWidgets.QTableWidgetItem(type_text)
            if entry["entry_type"] == "income":
                type_item.setForeground(QtGui.QColor("#588157"))
            else:
                type_item.setForeground(QtGui.QColor("#CC6666"))
            type_item.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
            self.table.setItem(row, 1, type_item)
            
            # Category
            category_item = QtWidgets.QTableWidgetItem(entry["category_name"])
            self.table.setItem(row, 2, category_item)
            
            # Amount
            amount_text = f"৳{entry['amount']:,.2f}"
            amount_item = QtWidgets.QTableWidgetItem(amount_text)
            amount_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.table.setItem(row, 3, amount_item)
            
            # Description
            desc = entry.get("description", "")
            desc_item = QtWidgets.QTableWidgetItem(desc if desc else "-")
            self.table.setItem(row, 4, desc_item)
            
            # Receipt
            receipt_item = QtWidgets.QTableWidgetItem("✓ View" if entry.get("receipt_path") else "-")
            receipt_item.setTextAlignment(QtCore.Qt.AlignCenter)
            if entry.get("receipt_path"):
                receipt_item.setForeground(QtGui.QColor("#588157"))
            self.table.setItem(row, 5, receipt_item)
            
            # Actions
            actions_widget = QtWidgets.QWidget()
            actions_layout = QtWidgets.QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(5)
            
            delete_btn = QtWidgets.QPushButton("🗑️")
            delete_btn.setMaximumWidth(40)
            delete_btn.setStyleSheet("background-color: #CC6666; padding: 5px;")
            delete_btn.clicked.connect(lambda checked, eid=entry["id"]: self.delete_entry(eid))
            actions_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 6, actions_widget)
    
    def delete_entry(self, entry_id):
        """Delete a financial entry"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Delete Entry",
            "Are you sure you want to delete this entry?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                response = requests.delete(f"{API_URL}/finance/entries/{entry_id}")
                if response.status_code == 200:
                    QtWidgets.QMessageBox.information(self, "Success", "Entry deleted successfully!")
                    self.load_data()
                else:
                    error_msg = response.json().get("detail", "Unknown error")
                    QtWidgets.QMessageBox.warning(self, "Error", f"Failed to delete entry: {error_msg}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def export_csv(self):
        """Export data to CSV"""
        if not self.entries:
            QtWidgets.QMessageBox.warning(self, "No Data", "No data to export")
            return
        
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self,
            "Save CSV",
            f"financial_data_{datetime.now().strftime('%Y%m%d')}.csv",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Date", "Type", "Category", "Amount", "Description", "Notes"])
                    
                    for entry in self.entries:
                        writer.writerow([
                            entry["date"],
                            entry["entry_type"],
                            entry["category_name"],
                            entry["amount"],
                            entry.get("description", ""),
                            entry.get("notes", "")
                        ])
                
                QtWidgets.QMessageBox.information(self, "Success", f"Data exported to:\n{file_path}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")
    
    def generate_pdf_report(self):
        """Generate PDF report"""
        QtWidgets.QMessageBox.information(
            self,
            "PDF Report",
            "PDF report generation feature will be implemented with proper PDF library.\n"
            "This would include:\n"
            "- Summary statistics\n"
            "- Charts and visualizations\n"
            "- Detailed transaction list\n"
            "- Period analysis"
        )
