import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import requests
from datetime import datetime

# Color scheme
BG_COLOR_LIGHT = "#EBEAE3"
TEXT_COLOR_DARK = "#344E41"
CARD_COLOR = "#FFFFFF"
PRIMARY_COLOR = "#588157"
SECONDARY_COLOR = "#A3B18A"
ACCENT_COLOR = "#8B5A3C"

class FlowLayout(QtWidgets.QLayout):
    def __init__(self, parent=None, margin=-1, hSpacing=-1, vSpacing=-1):
        super(FlowLayout, self).__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self._hSpacing = hSpacing
        self._vSpacing = vSpacing
        self._itemList = []

    def addItem(self, item):
        self._itemList.append(item)

    def horizontalSpacing(self):
        if self._hSpacing >= 0:
            return self._hSpacing
        else:
            return self.smartSpacing(QtWidgets.QStyle.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self):
        if self._vSpacing >= 0:
            return self._vSpacing
        else:
            return self.smartSpacing(QtWidgets.QStyle.PM_LayoutVerticalSpacing)

    def count(self):
        return len(self._itemList)

    def itemAt(self, index):
        if 0 <= index < len(self._itemList):
            return self._itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._itemList):
            return self._itemList.pop(index)
        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()
        for item in self._itemList:
            size = size.expandedTo(item.minimumSize())
        size += QtCore.QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        spacingX = self.horizontalSpacing()
        spacingY = self.verticalSpacing()
        
        # First pass: determine lines
        lines = []
        current_line = []
        current_line_width = 0
        
        for item in self._itemList:
            wid = item.widget()
            spaceX = spacingX
            
            item_width = item.sizeHint().width()
            
            if current_line and (current_line_width + spaceX + item_width > rect.width()):
                lines.append(current_line)
                current_line = []
                current_line_width = 0
            
            if current_line:
                current_line_width += spaceX
            
            current_line.append(item)
            current_line_width += item_width
            
        if current_line:
            lines.append(current_line)
            
        # Second pass: place items with stretching
        y = rect.y()
        for line in lines:
            line_height = 0
            
            # Calculate total width of items in this line
            items_width = sum(item.sizeHint().width() for item in line)
            total_spacing = (len(line) - 1) * spacingX
            available_space = rect.width() - total_spacing
            
            # Distribute extra space
            extra_space = max(0, available_space - items_width)
            bonus_per_item = extra_space / len(line) if line else 0
            
            x_pos = rect.x()
            
            for item in line:
                width = item.sizeHint().width() + bonus_per_item
                height = item.sizeHint().height()
                
                if not testOnly:
                    item.setGeometry(QtCore.QRect(int(x_pos), int(y), int(width), int(height)))
                
                line_height = max(line_height, height)
                x_pos += width + spacingX
            
            y += line_height + spacingY
            
        return y - rect.y()
        
    def smartSpacing(self, pm):
        parent = self.parent()
        if parent is None:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()

class DashboardHome(QtWidgets.QWidget):
    # Define signals for quick actions
    action_income_expense = QtCore.pyqtSignal()
    action_add_feed = QtCore.pyqtSignal()
    action_add_cattle = QtCore.pyqtSignal()
    action_add_order = QtCore.pyqtSignal()

    def __init__(self, user_email, farm_name):
        super().__init__()
        self.user_email = user_email
        self.farm_name = farm_name
        self.setStyleSheet(f"background-color: {BG_COLOR_LIGHT};")
        
        # Main layout with scrollable area
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create Scroll Area
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {BG_COLOR_LIGHT};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {BG_COLOR_LIGHT};
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {TEXT_COLOR_DARK};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        
        # Container widget for scroll area
        scroll_content = QtWidgets.QWidget()
        scroll_content.setStyleSheet(f"background-color: {BG_COLOR_LIGHT};")
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(30, 25, 30, 25)
        scroll_layout.setSpacing(22)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # Greeting section
        self._create_greeting_section(scroll_layout)
        
        # Stats cards row
        self._create_stats_cards(scroll_layout)
        
        # Charts row
        charts_layout = FlowLayout()
        charts_layout.setSpacing(20)
        
        self._create_production_chart(charts_layout)
        self._create_finance_chart(charts_layout)
        
        scroll_layout.addLayout(charts_layout)
        
        # Bottom row: Farm health + Quick actions
        bottom_layout = FlowLayout()
        bottom_layout.setSpacing(20)
        
        self._create_farm_health_widget(bottom_layout)
        self._create_quick_actions_widget(bottom_layout)
        
        scroll_layout.addLayout(bottom_layout)
        scroll_layout.addStretch()
        
        # Load data after widget is shown (using QTimer for delayed load)
        QtCore.QTimer.singleShot(100, self.load_dashboard_data)
    
    def _create_greeting_section(self, parent_layout):
        """Create greeting section with farm name and date"""
        greeting_widget = QtWidgets.QWidget()
        greeting_layout = QtWidgets.QVBoxLayout(greeting_widget)
        greeting_layout.setContentsMargins(0, 0, 0, 10)
        greeting_layout.setSpacing(5)
        
        # Determine greeting based on time of day
        current_hour = datetime.now().hour
        if current_hour < 12:
            greeting = "Good Morning"
        elif current_hour < 17:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"
        
        # Greeting text
        greeting_label = QtWidgets.QLabel(f"{greeting}, {self.farm_name}")
        greeting_label.setStyleSheet(f"color: #000000; font-size: 24pt; font-weight: bold; line-height: 1.3; padding: 3px 0px;")
        greeting_label.setMinimumHeight(40)
        greeting_layout.addWidget(greeting_label)
        
        # Date
        current_date = datetime.now().strftime("%d %B %Y")
        date_label = QtWidgets.QLabel(f"Today: {current_date}")
        date_label.setStyleSheet(f"color: #2A2A2A; font-size: 13pt; line-height: 1.4; padding: 2px 0px;")
        date_label.setMinimumHeight(24)
        greeting_layout.addWidget(date_label)
        
        parent_layout.addWidget(greeting_widget)
    
    def _create_stats_cards(self, parent_layout):
        """Create the three stat cards"""
        cards_layout = FlowLayout()
        cards_layout.setSpacing(20)
        
        # Total Animals Card
        self.animals_card = self._create_stat_card("Total Animals", "42", "🐄")
        cards_layout.addWidget(self.animals_card)
        
        # Today's Production Card
        self.production_card = self._create_stat_card("Today's Production", "42", "🥛")
        cards_layout.addWidget(self.production_card)
        
        # Monthly Income Card
        self.income_card = self._create_stat_card("Monthly Income", "42", "💰")
        cards_layout.addWidget(self.income_card)
        
        parent_layout.addLayout(cards_layout)
    
    def _create_stat_card(self, title, value, icon):
        """Create a single stat card"""
        card = QtWidgets.QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_COLOR};
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        card.setMinimumHeight(165)
        card.setMinimumWidth(300)
        
        layout = QtWidgets.QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(22, 25, 22, 25)
        
        # Top row with icon and title
        top_row = QtWidgets.QHBoxLayout()
        top_row.setSpacing(10)
        
        # Icon
        icon_container = QtWidgets.QLabel()
        icon_container.setFixedSize(40, 40)
        icon_container.setStyleSheet(f"""
            QLabel {{
                background-color: rgba(88, 129, 87, 0.12);
                border-radius: 20px;
                font-size: 18pt;
                padding: 8px;
            }}
        """)
        icon_container.setText(icon)
        icon_container.setAlignment(QtCore.Qt.AlignCenter)
        icon_container.setContentsMargins(0, 0, 0, 0)
        top_row.addWidget(icon_container)
        
        # Title - completely visible with proper line height
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: #000000;
                font-size: 12pt;
                font-weight: 700;
                line-height: 1.5;
                padding: 2px 0px;
            }}
        """)
        title_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        title_label.setWordWrap(False)
        title_label.setMinimumHeight(22)
        top_row.addWidget(title_label, 1)
        
        layout.addLayout(top_row)
        layout.addSpacing(8)
        
        # Value with maximum visibility and no clipping
        value_label = QtWidgets.QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: #000000;
                font-size: 38pt;
                font-weight: 700;
                font-family: 'Segoe UI', 'Arial', 'Helvetica', sans-serif;
                line-height: 1.2;
                padding: 5px 0px;
            }}
        """)
        value_label.setAlignment(QtCore.Qt.AlignCenter)
        value_label.setWordWrap(False)
        value_label.setTextFormat(QtCore.Qt.PlainText)
        value_label.setMinimumHeight(70)
        value_label.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(value_label)
        
        layout.addStretch()
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
    
    def _create_production_chart(self, parent_layout):
        """Create production trend chart"""
        chart_widget = QtWidgets.QFrame()
        chart_widget.setMinimumWidth(400)
        chart_widget.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_COLOR};
                border-radius: 15px;
                padding: 25px;
            }}
        """)
        
        layout = QtWidgets.QVBoxLayout(chart_widget)
        layout.setSpacing(12)
        layout.setContentsMargins(22, 25, 22, 25)
        
        # Title
        title_label = QtWidgets.QLabel("Production Trend (Last 7 Days)")
        title_label.setStyleSheet(f"color: #000000; font-size: 15pt; font-weight: bold; line-height: 1.4; padding: 3px 0px;")
        title_label.setMinimumHeight(28)
        layout.addWidget(title_label)
        
        # Chart placeholder (will be populated with real data)
        self.production_chart_view = QtWidgets.QLabel("Loading chart...")
        self.production_chart_view.setAlignment(QtCore.Qt.AlignCenter)
        self.production_chart_view.setMinimumHeight(240)
        self.production_chart_view.setStyleSheet(f"color: #888; font-size: 11pt; line-height: 1.6; padding: 8px;")
        self.production_chart_view.setWordWrap(True)
        layout.addWidget(self.production_chart_view)
        
        parent_layout.addWidget(chart_widget)
    
    def _create_finance_chart(self, parent_layout):
        """Create expense vs income chart"""
        chart_widget = QtWidgets.QFrame()
        chart_widget.setMinimumWidth(400)
        chart_widget.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_COLOR};
                border-radius: 15px;
                padding: 25px;
            }}
        """)
        
        layout = QtWidgets.QVBoxLayout(chart_widget)
        layout.setSpacing(12)
        layout.setContentsMargins(22, 25, 22, 25)
        
        # Title
        title_label = QtWidgets.QLabel("Expense vs. Income (Monthly)")
        title_label.setStyleSheet(f"color: #000000; font-size: 15pt; font-weight: bold; line-height: 1.4; padding: 3px 0px;")
        title_label.setMinimumHeight(28)
        layout.addWidget(title_label)
        
        # Chart placeholder
        self.finance_chart_view = QtWidgets.QLabel("Loading chart...")
        self.finance_chart_view.setAlignment(QtCore.Qt.AlignCenter)
        self.finance_chart_view.setMinimumHeight(240)
        self.finance_chart_view.setStyleSheet(f"color: #888; font-size: 11pt; line-height: 1.6; padding: 8px;")
        self.finance_chart_view.setWordWrap(True)
        layout.addWidget(self.finance_chart_view)
        
        parent_layout.addWidget(chart_widget)
    
    def _create_farm_health_widget(self, parent_layout):
        """Create farm health indicator"""
        health_widget = QtWidgets.QFrame()
        health_widget.setMinimumWidth(400)
        health_widget.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_COLOR};
                border-radius: 15px;
            }}
        """)
        health_widget.setMinimumHeight(140)
        
        # Horizontal layout for Icon | Text
        layout = QtWidgets.QHBoxLayout(health_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Icon (Left)
        icon_label = QtWidgets.QLabel("🏥")
        icon_label.setStyleSheet(f"""
            background-color: #E0E0E0;
            border-radius: 25px;
            font-size: 24pt;
            padding: 5px;
        """)
        icon_label.setFixedSize(50, 50)
        icon_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Right side container
        text_container = QtWidgets.QWidget()
        text_layout = QtWidgets.QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(5)
        
        # Title
        title_label = QtWidgets.QLabel("Farm Health: 86%")
        title_label.setStyleSheet(f"color: #000000; font-size: 16pt; font-weight: bold; line-height: 1.4;")
        text_layout.addWidget(title_label)
        
        # Subtitle
        subtitle = QtWidgets.QLabel("(Based on production and animal condition)")
        subtitle.setStyleSheet("color: #2A2A2A; font-size: 10pt; line-height: 1.4;")
        subtitle.setWordWrap(True)
        text_layout.addWidget(subtitle)
        
        # Progress bar
        self.health_progress = QtWidgets.QProgressBar()
        self.health_progress.setValue(86)
        self.health_progress.setTextVisible(False)
        self.health_progress.setFixedHeight(8)
        self.health_progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: #E0E0E0;
            }}
            QProgressBar::chunk {{
                border-radius: 4px;
                background-color: {PRIMARY_COLOR};
            }}
        """)
        text_layout.addWidget(self.health_progress)
        
        layout.addWidget(text_container, 1)
        
        # Store title for updates
        health_widget.title_label = title_label
        
        parent_layout.addWidget(health_widget)
        self.health_widget = health_widget
    
    def _create_quick_actions_widget(self, parent_layout):
        """Create quick action buttons"""
        actions_widget = QtWidgets.QWidget()
        actions_widget.setMinimumWidth(400)
        # Transparent background to match design
        
        layout = QtWidgets.QVBoxLayout(actions_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Row 1: Title + Income Button
        row1 = QtWidgets.QHBoxLayout()
        
        title_label = QtWidgets.QLabel("Quick Action")
        title_label.setStyleSheet(f"color: #000000; font-size: 16pt; font-weight: bold;")
        row1.addWidget(title_label)
        
        row1.addStretch()
        
        income_expense_btn = self._create_action_button("+ Income/Expense", ACCENT_COLOR)
        income_expense_btn.clicked.connect(self.action_income_expense.emit)
        row1.addWidget(income_expense_btn)
        
        layout.addLayout(row1)
        
        # Row 2: Other buttons
        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(10)
        
        add_feed_btn = self._create_action_button("+ Add Feed", ACCENT_COLOR)
        add_feed_btn.clicked.connect(self.action_add_feed.emit)
        row2.addWidget(add_feed_btn)
        
        add_cattle_btn = self._create_action_button("+ Add Cattle", ACCENT_COLOR)
        add_cattle_btn.clicked.connect(self.action_add_cattle.emit)
        row2.addWidget(add_cattle_btn)
        
        add_order_btn = self._create_action_button("+ Add Order", ACCENT_COLOR)
        add_order_btn.clicked.connect(self.action_add_order.emit)
        row2.addWidget(add_order_btn)
        
        layout.addLayout(row2)
        
        parent_layout.addWidget(actions_widget)
    
    def _create_action_button(self, text, color):
        """Create a quick action button"""
        button = QtWidgets.QPushButton(text)
        button.setMinimumHeight(45)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px 18px;
                font-size: 11pt;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #9D6B4D;
            }}
            QPushButton:pressed {{
                background-color: #7A5239;
            }}
        """)
        button.setCursor(QtCore.Qt.PointingHandCursor)
        return button
    
    def load_dashboard_data(self):
        """Load dashboard data from API"""
        try:
            # Make API request
            response = requests.get(
                f"http://localhost:8000/dashboard/stats/{self.user_email}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json().get("data", {})
                
                print(f"Dashboard data received: {data}")  # Debug output
                
                # Update stat cards with proper formatting
                total_animals = data.get("total_animals", 0)
                today_production = int(data.get("today_production", 0))
                monthly_income = int(data.get("monthly_income", 0))
                
                print(f"Animals: {total_animals}, Production: {today_production}, Income: {monthly_income}")
                
                self.animals_card.value_label.setText(str(total_animals))
                self.production_card.value_label.setText(str(today_production))
                self.income_card.value_label.setText(f"৳{monthly_income:,}")
                
                # Force update the labels
                self.animals_card.value_label.update()
                self.production_card.value_label.update()
                self.income_card.value_label.update()
                
                # Update farm health
                health_score = data.get("farm_health", 0)
                print(f"Farm Health: {health_score}%")
                self.health_progress.setValue(health_score)
                self.health_widget.title_label.setText(f"Farm Health: {health_score}%")
                self.health_widget.title_label.update()
                
                # Update production chart
                self._update_production_chart(data.get("production_trend", []))
                
                # Update finance chart
                self._update_finance_chart(data.get("finance_data", []))
                
            else:
                print(f"Error loading dashboard data: {response.status_code}")
                self._show_error_message(f"Server returned status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("Error: Cannot connect to backend server. Please ensure the server is running.")
            self._show_error_message("Cannot connect to server")
        except requests.exceptions.Timeout:
            print("Error: Request timed out")
            self._show_error_message("Request timed out")
        except Exception as e:
            print(f"Error connecting to backend: {str(e)}")
            self._show_error_message(f"Error: {str(e)}")
    
    def _update_production_chart(self, production_data):
        """Update production trend chart with real data"""
        if not production_data:
            return
        
        # Create a simple text representation for now
        # In a full implementation, you would use QtCharts here
        chart_text = "Production Trend:\n\n"
        for item in production_data:
            date_str = item.get("date", "")
            quantity = item.get("quantity", 0)
            chart_text += f"{date_str}: {int(quantity)} units\n"
        
        self.production_chart_view.setText(chart_text)
        self.production_chart_view.setStyleSheet(f"color: #000000; font-size: 11pt; line-height: 1.7; padding: 10px;")
        self.production_chart_view.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.production_chart_view.setWordWrap(True)
    
    def _update_finance_chart(self, finance_data):
        """Update finance chart with real data"""
        if not finance_data:
            self.finance_chart_view.setText("No financial data available")
            self.finance_chart_view.setStyleSheet(f"color: #2A2A2A; font-size: 12pt;")
            return
        
        # Group data by type
        income_total = 0
        expense_total = 0
        
        for item in finance_data:
            if item.get("type") == "income":
                income_total += item.get("amount", 0)
            else:
                expense_total += item.get("amount", 0)
        
        chart_text = "Monthly Summary:\n\n"
        chart_text += f"Total Income: ৳{int(income_total):,}\n"
        chart_text += f"Total Expense: ৳{int(expense_total):,}\n"
        chart_text += f"Net: ৳{int(income_total - expense_total):,}"
        
        self.finance_chart_view.setText(chart_text)
        self.finance_chart_view.setStyleSheet(f"color: #000000; font-size: 14pt; font-weight: 600; line-height: 1.6; padding: 10px;")
        self.finance_chart_view.setAlignment(QtCore.Qt.AlignCenter)
        self.finance_chart_view.setWordWrap(True)
    
    def _show_error_message(self, message):
        """Show error message in production and finance charts"""
        error_text = f"⚠️ {message}\n\nUsing sample data"
        self.production_chart_view.setText(error_text)
        self.production_chart_view.setStyleSheet("color: #D32F2F; font-size: 11pt;")
        self.finance_chart_view.setText(error_text)
        self.finance_chart_view.setStyleSheet("color: #D32F2F; font-size: 11pt;")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    # Test widget
    dashboard = DashboardHome("test@example.com", "Test Farm")
    dashboard.setMinimumSize(1000, 700)
    dashboard.show()
    
    sys.exit(app.exec_())
