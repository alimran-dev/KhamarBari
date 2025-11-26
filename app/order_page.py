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
        apply_btn.clicked.connect(self.accept)
        button_layout.addWidget(apply_btn)
        
        layout.addLayout(button_layout)
    
    def get_dates(self):
        """Return selected start and end dates."""
        return (
            self.start_date_edit.date().toString("yyyy-MM-dd"),
            self.end_date_edit.date().toString("yyyy-MM-dd")
        )


class OrderDetailsWidget(QtWidgets.QWidget):
    """Widget to display order details in the sidebar."""
    
    closed = QtCore.pyqtSignal()
    status_changed = QtCore.pyqtSignal(str, str)  # order_id, new_status
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.order_id = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI for order details."""
        self.setStyleSheet("""
            QWidget {
                background-color: #FAFAFA;
            }
            QLabel {
                color: #344E41;
                font-size: 10pt;
                line-height: 1.6;
            }
            QLabel#titleLabel {
                font-size: 18pt;
                font-weight: bold;
                color: #344E41;
                padding: 10px 0;
            }
            QLabel#sectionLabel {
                font-size: 12pt;
                font-weight: bold;
                color: #344E41;
                margin-top: 20px;
                margin-bottom: 10px;
                padding: 8px 0;
            }
            QPushButton {
                background-color: #344E41;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 10pt;
                border: none;
            }
            QPushButton:hover {
                background-color: #588157;
            }
            QPushButton#closeBtn {
                background-color: transparent;
                color: #344E41;
                font-size: 20pt;
                font-weight: bold;
                padding: 5px;
                border: none;
            }
            QPushButton#closeBtn:hover {
                color: #d9534f;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Header with close button
        header_layout = QtWidgets.QHBoxLayout()
        self.order_id_label = QtWidgets.QLabel("#ORD-00000")
        self.order_id_label.setObjectName("titleLabel")
        header_layout.addWidget(self.order_id_label)
        header_layout.addStretch()
        
        close_btn = QtWidgets.QPushButton("×")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close_details)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # Scroll area for content
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        scroll_content = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(scroll_content)
        self.content_layout.setSpacing(10)
        
        # Order Details section
        details_label = QtWidgets.QLabel("Order Details")
        details_label.setObjectName("sectionLabel")
        self.content_layout.addWidget(details_label)
        
        self.customer_info_label = QtWidgets.QLabel()
        self.customer_info_label.setWordWrap(True)
        self.content_layout.addWidget(self.customer_info_label)
        
        # Items section
        items_label = QtWidgets.QLabel("Items")
        items_label.setObjectName("sectionLabel")
        self.content_layout.addWidget(items_label)
        
        self.items_label = QtWidgets.QLabel()
        self.items_label.setWordWrap(True)
        self.content_layout.addWidget(self.items_label)
        
        # Timeline section
        timeline_label = QtWidgets.QLabel("Order Timeline")
        timeline_label.setObjectName("sectionLabel")
        self.content_layout.addWidget(timeline_label)
        
        self.timeline_widget = QtWidgets.QWidget()
        self.timeline_layout = QtWidgets.QVBoxLayout(self.timeline_widget)
        self.timeline_layout.setSpacing(15)
        self.timeline_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addWidget(self.timeline_widget)
        
        self.content_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Action buttons
        actions_layout = QtWidgets.QVBoxLayout()
        actions_layout.setSpacing(12)
        actions_layout.setContentsMargins(0, 10, 0, 0)
        
        self.edit_btn = QtWidgets.QPushButton("✏️  Edit Status")
        self.edit_btn.setMinimumHeight(45)
        self.edit_btn.clicked.connect(self.edit_order)
        actions_layout.addWidget(self.edit_btn)
        
        self.cancel_btn = QtWidgets.QPushButton("✖  Cancel Order")
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel_order)
        actions_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(actions_layout)
    
    def load_order(self, order_id):
        """Load order details from backend."""
        self.order_id = order_id
        self.order_id_label.setText(f"#{order_id}")
        
        try:
            response = requests.get(f"http://localhost:8000/orders/{order_id}")
            response.raise_for_status()
            
            result = response.json()
            order = result['data']
            
            # Display customer info
            customer_info = f"""
            <div style='background-color: white; padding: 15px; border-radius: 8px;'>
            <p style='margin: 5px 0;'><b style='color: #588157;'>Name:</b> {order['customer_name']}</p>
            <p style='margin: 5px 0;'><b style='color: #588157;'>Email:</b> {order.get('customer_email', 'N/A')}</p>
            <p style='margin: 5px 0;'><b style='color: #588157;'>Phone:</b> {order.get('customer_phone', 'N/A')}</p>
            <p style='margin: 5px 0;'><b style='color: #588157;'>Delivery Date:</b> {order.get('delivery_date', 'N/A')}</p>
            </div>
            """
            self.customer_info_label.setText(customer_info)
            
            # Display items
            items_html = "<div style='background-color: white; padding: 15px; border-radius: 8px;'>"
            for i, item in enumerate(order['items'], 1):
                items_html += f"<p style='margin: 8px 0; padding: 8px; background-color: #F5F5F5; border-radius: 4px;'>"
                items_html += f"<b style='color: #344E41;'>{i}. {item['product_type']}</b><br>"
                items_html += f"<span style='color: #666; margin-left: 15px;'>Quantity: {item['quantity']} {item['unit']}</span>"
                items_html += f"</p>"
            items_html += "</div>"
            self.items_label.setText(items_html)
            
            # Build timeline
            self.build_timeline(order)
            
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to load order details: {str(e)}"
            )
    
    def build_timeline(self, order):
        """Build the order timeline."""
        # Clear existing timeline
        while self.timeline_layout.count():
            child = self.timeline_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Timeline stages
        stages = [
            ("Created", order.get('created_at'), True),
            ("Packed", order.get('packed_at'), order['status'] in ['Packed', 'Out for Delivery', 'Delivered']),
            ("Out for Delivery", order.get('out_for_delivery_at'), order['status'] in ['Out for Delivery', 'Delivered']),
            ("Delivered", order.get('delivered_at'), order['status'] == 'Delivered')
        ]
        
        for stage_name, timestamp, is_completed in stages:
            stage_widget = self.create_timeline_stage(stage_name, timestamp, is_completed)
            self.timeline_layout.addWidget(stage_widget)
    
    def create_timeline_stage(self, stage_name, timestamp, is_completed):
        """Create a timeline stage widget."""
        widget = QtWidgets.QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)
        
        # Status indicator
        indicator = QtWidgets.QLabel("✓" if is_completed else "○")
        indicator.setFixedSize(30, 30)
        indicator.setAlignment(QtCore.Qt.AlignCenter)
        indicator.setStyleSheet(f"""
            QLabel {{
                background-color: {'#5cb85c' if is_completed else '#e0e0e0'};
                color: {'white' if is_completed else '#999'};
                border-radius: 15px;
                font-size: 14pt;
                font-weight: bold;
            }}
        """)
        layout.addWidget(indicator)
        
        # Stage info
        info_layout = QtWidgets.QVBoxLayout()
        info_layout.setSpacing(3)
        
        name_label = QtWidgets.QLabel(stage_name)
        name_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                font-size: 11pt;
                color: {'#344E41' if is_completed else '#999'};
            }}
        """)
        info_layout.addWidget(name_label)
        
        if timestamp and is_completed:
            time_label = QtWidgets.QLabel(self.format_timestamp(timestamp))
            time_label.setStyleSheet("QLabel { color: #666; font-size: 9pt; }")
            info_layout.addWidget(time_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        return widget
    
    def format_timestamp(self, timestamp):
        """Format timestamp for display."""
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = timestamp
            return dt.strftime("%Y-%m-%d, %I:%M %p")
        except:
            return str(timestamp)
    
    def close_details(self):
        """Close the details panel."""
        self.closed.emit()
    
    def edit_order(self):
        """Edit order status."""
        if not self.order_id:
            return
        
        statuses = ["Pending", "Packed", "Out for Delivery", "Delivered", "Cancelled"]
        status, ok = QtWidgets.QInputDialog.getItem(
            self, 
            "Change Status", 
            "Select new status:", 
            statuses, 
            0, 
            False
        )
        
        if ok and status:
            self.update_status(status)
    
    def update_status(self, new_status):
        """Update order status."""
        try:
            response = requests.put(
                f"http://localhost:8000/orders/{self.order_id}/status",
                json={"status": new_status}
            )
            response.raise_for_status()
            
            QtWidgets.QMessageBox.information(
                self, 
                "Success", 
                f"Order status updated to {new_status}"
            )
            self.status_changed.emit(self.order_id, new_status)
            self.load_order(self.order_id)  # Reload
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to update status: {str(e)}"
            )
    
    def cancel_order(self):
        """Cancel the order."""
        if not self.order_id:
            return
        
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Cancellation",
            "Are you sure you want to cancel this order?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                response = requests.delete(f"http://localhost:8000/orders/{self.order_id}")
                response.raise_for_status()
                
                QtWidgets.QMessageBox.information(
                    self, 
                    "Success", 
                    "Order cancelled successfully"
                )
                self.status_changed.emit(self.order_id, "Cancelled")
                self.close_details()
            except requests.exceptions.RequestException as e:
                QtWidgets.QMessageBox.critical(
                    self, 
                    "Error", 
                    f"Failed to cancel order: {str(e)}"
                )


class OrderPage(QtWidgets.QWidget):
    """Main Order Page Widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_filter_status = "All"
        self.current_filter_product = "All"
        self.current_date_range = None
        self.setup_ui()
        self.load_orders()
    
    def setup_ui(self):
        """Setup the main UI."""
        self.setStyleSheet("""
            QWidget {
                background-color: #EBEAE3;
                color: #344E41;
            }
            QLabel {
                color: #344E41;
            }
            QPushButton {
                background-color: #344E41;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 10pt;
                border: none;
            }
            QPushButton:hover {
                background-color: #588157;
            }
            QLineEdit, QComboBox {
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
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #344E41;
                margin-right: 10px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #A3B18A;
                border-radius: 5px;
                gridline-color: #D8E2D1;
            }
            QHeaderView::section {
                background-color: #344E41;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 10pt;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #A3B18A;
                color: white;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #344E41;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Main layout with sidebar
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Main content area
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Header with tabs and button
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(10)
        
        # Tab buttons with container for centering
        tab_button_container = QtWidgets.QWidget()
        tab_button_layout = QtWidgets.QHBoxLayout(tab_button_container)
        tab_button_layout.setContentsMargins(0, 0, 0, 0)
        tab_button_layout.setSpacing(0)
        tab_button_layout.setAlignment(QtCore.Qt.AlignHCenter)
        
        self.tab_all = self.create_tab_button("All orders", True)
        self.tab_place = self.create_tab_button("Place Order", False)
        self.tab_pre = self.create_tab_button("Pre Orders", False)
        
        # Set position properties for rounded corners
        self.tab_all.setProperty("tab_pos", "left")
        self.tab_place.setProperty("tab_pos", "middle")
        self.tab_pre.setProperty("tab_pos", "right")
        
        self.tab_all.clicked.connect(lambda: self.switch_tab(0))
        self.tab_place.clicked.connect(lambda: self.switch_tab(1))
        self.tab_pre.clicked.connect(lambda: self.switch_tab(2))
        
        tab_button_layout.addWidget(self.tab_all)
        tab_button_layout.addWidget(self.tab_place)
        tab_button_layout.addWidget(self.tab_pre)
        
        header_layout.addWidget(tab_button_container)
        header_layout.addStretch()
        
        content_layout.addLayout(header_layout)
        
        # Stacked widget for tabs
        self.tabs_stack = QtWidgets.QStackedWidget()
        
        # All Orders tab content
        all_orders_widget = self.create_all_orders_tab()
        self.tabs_stack.addWidget(all_orders_widget)
        
        # Place Order tab with form
        place_order_widget = self.create_place_order_tab()
        self.tabs_stack.addWidget(place_order_widget)
        
        # Pre Orders tab (placeholder)
        pre_orders_widget = QtWidgets.QLabel("Pre Orders feature coming soon...")
        pre_orders_widget.setAlignment(QtCore.Qt.AlignCenter)
        pre_orders_widget.setStyleSheet("font-size: 14pt; color: #999; padding: 50px;")
        self.tabs_stack.addWidget(pre_orders_widget)
        
        content_layout.addWidget(self.tabs_stack)
        
        main_layout.addWidget(content_widget, 1)
        
        # Order details sidebar (initially hidden)
        self.details_widget = OrderDetailsWidget()
        self.details_widget.setFixedWidth(350)
        self.details_widget.hide()
        self.details_widget.closed.connect(self.hide_details)
        self.details_widget.status_changed.connect(self.on_order_status_changed)
        main_layout.addWidget(self.details_widget)
    
    def create_tab_button(self, text, is_active):
        """Create a styled tab button."""
        btn = QtWidgets.QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(is_active)
        btn.setFixedHeight(45)
        btn.setFixedWidth(150)
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        
        if is_active:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #588157;
                    color: white;
                    border: 2px solid #588157;
                    font-size: 11pt;
                    font-weight: bold;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: #344E41;
                    border: 2px solid #588157;
                    font-size: 11pt;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)
        
        return btn
    
    def switch_tab(self, index):
        """Switch between tabs."""
        # Update tab button styles
        tabs = [self.tab_all, self.tab_place, self.tab_pre]
        for i, tab in enumerate(tabs):
            is_active = (i == index)
            tab.setChecked(is_active)
            
            # Determine border radius based on position
            pos = tab.property("tab_pos")
            if pos == "left":
                border_radius = "border-top-left-radius: 10px; border-bottom-left-radius: 10px;"
            elif pos == "right":
                border_radius = "border-top-right-radius: 10px; border-bottom-right-radius: 10px;"
            else:
                border_radius = ""
            
            if is_active:
                tab.setStyleSheet(f"""
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
                tab.setStyleSheet(f"""
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
        
        self.tabs_stack.setCurrentIndex(index)
    
    def create_all_orders_tab(self):
        """Create the All Orders tab content."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)
        
        # Title
        title_label = QtWidgets.QLabel("All Orders")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #344E41;")
        layout.addWidget(title_label)
        
        # Filters row
        filters_layout = QtWidgets.QHBoxLayout()
        filters_layout.setSpacing(15)
        
        # Search
        search_label = QtWidgets.QLabel("Search")
        search_label.setStyleSheet("font-weight: bold;")
        filters_layout.addWidget(search_label)
        
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Search by customer, order ID")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.search_input)
        
        # Status filter
        status_label = QtWidgets.QLabel("Status")
        status_label.setStyleSheet("font-weight: bold;")
        filters_layout.addWidget(status_label)
        
        self.status_filter = QtWidgets.QComboBox()
        self.status_filter.addItems(["Pending", "Delivered", "Cancelled", "All"])
        self.status_filter.setCurrentText("Pending")
        self.status_filter.setFixedWidth(150)
        self.status_filter.currentTextChanged.connect(self.on_status_filter_changed)
        filters_layout.addWidget(self.status_filter)
        
        # Date range filter
        date_label = QtWidgets.QLabel("Date Range")
        date_label.setStyleSheet("font-weight: bold;")
        filters_layout.addWidget(date_label)
        
        self.date_filter = QtWidgets.QComboBox()
        self.date_filter.addItems(["Date Range", "Today", "Last 7 Days", "Custom"])
        self.date_filter.setFixedWidth(150)
        self.date_filter.currentTextChanged.connect(self.on_date_filter_changed)
        filters_layout.addWidget(self.date_filter)
        
        # Product type filter
        product_label = QtWidgets.QLabel("Product Type")
        product_label.setStyleSheet("font-weight: bold;")
        filters_layout.addWidget(product_label)
        
        self.product_filter = QtWidgets.QComboBox()
        self.product_filter.addItems(["All", "Milk", "Eggs", "Wool"])
        self.product_filter.setFixedWidth(150)
        self.product_filter.currentTextChanged.connect(self.on_product_filter_changed)
        filters_layout.addWidget(self.product_filter)
        
        filters_layout.addStretch()
        
        layout.addLayout(filters_layout)
        
        # Orders table
        self.orders_table = QtWidgets.QTableWidget()
        self.orders_table.setColumnCount(8)
        self.orders_table.setHorizontalHeaderLabels([
            "Order ID", "Customer", "Items Summary", "Quantity", "Total", 
            "Delivery Date", "Status", "Actions"
        ])
        
        # Set column widths
        header = self.orders_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QtWidgets.QHeaderView.Fixed)
        self.orders_table.setColumnWidth(7, 160)
        
        self.orders_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.orders_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.orders_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.verticalHeader().setVisible(False)
        self.orders_table.verticalHeader().setDefaultSectionSize(65)  # Set row height
        
        layout.addWidget(self.orders_table)
        
        # Footer with pagination and bulk actions
        footer_layout = QtWidgets.QHBoxLayout()
        footer_layout.setSpacing(15)
        
        # Pagination
        pagination_layout = QtWidgets.QHBoxLayout()
        page_label = QtWidgets.QLabel("Page:")
        page_label.setStyleSheet("font-size: 10pt; color: #344E41;")
        pagination_layout.addWidget(page_label)
        
        self.page_prev_btn = QtWidgets.QPushButton("‹")
        self.page_prev_btn.setFixedSize(30, 30)
        self.page_prev_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #344E41;
                border: 1px solid #A3B18A;
                border-radius: 5px;
                font-size: 14pt;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #A3B18A;
                color: white;
            }
        """)
        pagination_layout.addWidget(self.page_prev_btn)
        
        self.page_1_btn = QtWidgets.QPushButton("1")
        self.page_1_btn.setFixedSize(35, 35)
        self.page_1_btn.setStyleSheet("""
            QPushButton {
                background-color: #344E41;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13pt;
            }
        """)
        pagination_layout.addWidget(self.page_1_btn)
        
        self.page_next_btn = QtWidgets.QPushButton("›")
        self.page_next_btn.setFixedSize(30, 30)
        self.page_next_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #344E41;
                border: 1px solid #A3B18A;
                border-radius: 5px;
                font-size: 14pt;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #A3B18A;
                color: white;
            }
        """)
        pagination_layout.addWidget(self.page_next_btn)
        
        self.page_last_btn = QtWidgets.QPushButton("››")
        self.page_last_btn.setFixedSize(30, 30)
        self.page_last_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #344E41;
                border: 1px solid #A3B18A;
                border-radius: 5px;
                font-size: 14pt;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #A3B18A;
                color: white;
            }
        """)
        pagination_layout.addWidget(self.page_last_btn)
        
        footer_layout.addLayout(pagination_layout)
        footer_layout.addStretch()
        
        layout.addLayout(footer_layout)
        
        return widget
    
    def load_orders(self):
        """Load orders from backend."""
        try:
            params = {}
            
            if self.current_filter_status and self.current_filter_status != "All":
                params['status'] = self.current_filter_status
            
            if self.current_filter_product and self.current_filter_product != "All":
                params['product_type'] = self.current_filter_product
            
            search_text = self.search_input.text().strip() if hasattr(self, 'search_input') else ""
            if search_text:
                params['search'] = search_text
            
            if self.current_date_range:
                params['start_date'] = self.current_date_range[0]
                params['end_date'] = self.current_date_range[1]
            
            response = requests.get("http://localhost:8000/orders", params=params)
            response.raise_for_status()
            
            result = response.json()
            orders = result['data']
            
            self.populate_orders_table(orders)
            
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to load orders: {str(e)}"
            )
    
    def populate_orders_table(self, orders):
        """Populate the orders table with data."""
        self.orders_table.setRowCount(0)
        
        for order in orders:
            row = self.orders_table.rowCount()
            self.orders_table.insertRow(row)
            
            # Order ID
            self.orders_table.setItem(row, 0, QtWidgets.QTableWidgetItem(order['order_id']))
            
            # Customer
            self.orders_table.setItem(row, 1, QtWidgets.QTableWidgetItem(order['customer_name']))
            
            # Items Summary
            items_summary = order.get('products', 'N/A')
            self.orders_table.setItem(row, 2, QtWidgets.QTableWidgetItem(items_summary))
            
            # Quantity
            total_qty = order.get('total_quantity', 0)
            if total_qty:
                quantity_text = f"{float(total_qty):.2f}"
            else:
                quantity_text = "0.00"
            self.orders_table.setItem(row, 3, QtWidgets.QTableWidgetItem(quantity_text))
            
            # Total
            total = f"৳ {order.get('total_amount', 0):,.2f}"
            self.orders_table.setItem(row, 4, QtWidgets.QTableWidgetItem(total))
            
            # Delivery Date
            delivery_date = order.get('delivery_date', 'N/A')
            self.orders_table.setItem(row, 5, QtWidgets.QTableWidgetItem(str(delivery_date)))
            
            # Status badge
            status = order['status']
            status_item = QtWidgets.QTableWidgetItem(status)
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            
            # Color based on status
            if status == "Delivered":
                status_item.setBackground(QtGui.QColor("#5cb85c"))
                status_item.setForeground(QtGui.QColor("white"))
            elif status == "Pending":
                status_item.setBackground(QtGui.QColor("#f0ad4e"))
                status_item.setForeground(QtGui.QColor("white"))
            elif status == "Cancelled":
                status_item.setBackground(QtGui.QColor("#d9534f"))
                status_item.setForeground(QtGui.QColor("white"))
            else:
                status_item.setBackground(QtGui.QColor("#5bc0de"))
                status_item.setForeground(QtGui.QColor("white"))
            
            self.orders_table.setItem(row, 6, status_item)
            
            # Actions
            actions_widget = self.create_action_buttons(order['order_id'])
            self.orders_table.setCellWidget(row, 7, actions_widget)
    
    def create_status_badge(self, status):
        """Create a colored status badge."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        
        badge = QtWidgets.QLabel(status)
        badge.setAlignment(QtCore.Qt.AlignCenter)
        badge.setFixedHeight(25)
        badge.setFixedWidth(100)
        
        # Color based on status
        if status == "Delivered":
            color = "#5cb85c"
        elif status == "Pending":
            color = "#f0ad4e"
        elif status == "Cancelled":
            color = "#d9534f"
        else:
            color = "#5bc0de"
        
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                border-radius: 12px;
                padding: 2px 10px;
                font-weight: bold;
                font-size: 9pt;
            }}
        """)
        
        layout.addWidget(badge)
        return widget
    
    def create_action_buttons(self, order_id):
        """Create action buttons for each order row."""
        widget = QtWidgets.QWidget()
        widget.setStyleSheet("background-color: transparent;")
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # View button
        view_btn = QtWidgets.QPushButton("👁")
        view_btn.setFixedSize(35, 35)
        view_btn.setToolTip("View Details")
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #5bc0de;
                color: white;
                border-radius: 5px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #46b8da;
            }
        """)
        view_btn.clicked.connect(lambda: self.view_order_details(order_id))
        layout.addWidget(view_btn)
        
        # Edit button
        edit_btn = QtWidgets.QPushButton("✏")
        edit_btn.setFixedSize(35, 35)
        edit_btn.setToolTip("Edit Order")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0ad4e;
                color: white;
                border-radius: 5px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #ec971f;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_order_status(order_id))
        layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QtWidgets.QPushButton("✖")
        delete_btn.setFixedSize(35, 35)
        delete_btn.setToolTip("Cancel Order")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 5px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        delete_btn.clicked.connect(lambda: self.cancel_order(order_id))
        layout.addWidget(delete_btn)
        
        return widget
    
    def view_order_details(self, order_id):
        """View order details in sidebar."""
        self.details_widget.load_order(order_id)
        self.details_widget.show()
    
    def edit_order_status(self, order_id):
        """Edit order status."""
        statuses = ["Pending", "Packed", "Out for Delivery", "Delivered", "Cancelled"]
        status, ok = QtWidgets.QInputDialog.getItem(
            self, 
            "Change Status", 
            f"Select new status for {order_id}:", 
            statuses, 
            0, 
            False
        )
        
        if ok and status:
            try:
                response = requests.put(
                    f"http://localhost:8000/orders/{order_id}/status",
                    json={"status": status}
                )
                response.raise_for_status()
                
                QtWidgets.QMessageBox.information(
                    self, 
                    "Success", 
                    f"Order status updated to {status}"
                )
                self.load_orders()
            except requests.exceptions.RequestException as e:
                QtWidgets.QMessageBox.critical(
                    self, 
                    "Error", 
                    f"Failed to update status: {str(e)}"
                )
    
    def cancel_order(self, order_id):
        """Cancel an order."""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Cancellation",
            f"Are you sure you want to cancel order {order_id}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                response = requests.delete(f"http://localhost:8000/orders/{order_id}")
                response.raise_for_status()
                
                QtWidgets.QMessageBox.information(
                    self, 
                    "Success", 
                    "Order cancelled successfully"
                )
                self.load_orders()
            except requests.exceptions.RequestException as e:
                QtWidgets.QMessageBox.critical(
                    self, 
                    "Error", 
                    f"Failed to cancel order: {str(e)}"
                )
    
    def hide_details(self):
        """Hide the details sidebar."""
        self.details_widget.hide()
    
    def on_order_status_changed(self, order_id, new_status):
        """Handle order status change from details panel."""
        self.load_orders()
    

    
    def apply_filters(self):
        """Apply search and filters."""
        self.load_orders()
    
    def on_status_filter_changed(self, status):
        """Handle status filter change."""
        self.current_filter_status = status
        self.load_orders()
    
    def on_product_filter_changed(self, product):
        """Handle product filter change."""
        self.current_filter_product = product
        self.load_orders()
    
    def on_date_filter_changed(self, date_range):
        """Handle date range filter change."""
        if date_range == "Today":
            today = date.today()
            self.current_date_range = (today.isoformat(), today.isoformat())
            self.load_orders()
        elif date_range == "Last 7 Days":
            today = date.today()
            week_ago = today - timedelta(days=7)
            self.current_date_range = (week_ago.isoformat(), today.isoformat())
            self.load_orders()
        elif date_range == "Custom":
            dialog = CustomDateRangeDialog(self)
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                self.current_date_range = dialog.get_dates()
                self.load_orders()
        else:
            self.current_date_range = None
            self.load_orders()
    
    def create_place_order_tab(self):
        """Create the Place Order tab content with form."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title_label = QtWidgets.QLabel("Place New Order")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #344E41;")
        layout.addWidget(title_label)
        
        # Scroll area for the form
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        form_widget = QtWidgets.QWidget()
        form_layout = QtWidgets.QVBoxLayout(form_widget)
        form_layout.setSpacing(20)
        
        # Customer Information Section
        customer_group = QtWidgets.QGroupBox("Customer Information")
        customer_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                border: 2px solid #A3B18A;
                border-radius: 8px;
                margin-top: 15px;
                padding: 20px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background-color: white;
            }
        """)
        customer_layout = QtWidgets.QFormLayout()
        customer_layout.setSpacing(15)
        customer_layout.setContentsMargins(15, 25, 15, 15)
        
        self.place_customer_name = QtWidgets.QLineEdit()
        self.place_customer_name.setPlaceholderText("John Doe")
        self.place_customer_name.setMinimumHeight(40)
        customer_layout.addRow("Customer Name:*", self.place_customer_name)
        
        self.place_customer_email = QtWidgets.QLineEdit()
        self.place_customer_email.setPlaceholderText("john@gmail.com")
        self.place_customer_email.setMinimumHeight(40)
        customer_layout.addRow("Email:", self.place_customer_email)
        
        self.place_customer_phone = QtWidgets.QLineEdit()
        self.place_customer_phone.setPlaceholderText("01712345678")
        self.place_customer_phone.setMinimumHeight(40)
        customer_layout.addRow("Phone:", self.place_customer_phone)
        
        customer_group.setLayout(customer_layout)
        form_layout.addWidget(customer_group)
        
        # Order Items Section
        items_group = QtWidgets.QGroupBox("Order Items")
        items_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                border: 2px solid #A3B18A;
                border-radius: 8px;
                margin-top: 15px;
                padding: 20px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background-color: white;
            }
        """)
        items_layout = QtWidgets.QVBoxLayout()
        items_layout.setSpacing(15)
        items_layout.setContentsMargins(15, 25, 15, 15)
        
        # Add item form
        add_item_layout = QtWidgets.QHBoxLayout()
        add_item_layout.setSpacing(10)
        
        product_label = QtWidgets.QLabel("Product:")
        product_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        add_item_layout.addWidget(product_label)
        
        self.place_product_combo = QtWidgets.QComboBox()
        self.place_product_combo.addItems(["Milk", "Eggs", "Wool", "All"])
        self.place_product_combo.setMinimumHeight(40)
        add_item_layout.addWidget(self.place_product_combo, 2)
        
        qty_label = QtWidgets.QLabel("Quantity:")
        qty_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        add_item_layout.addWidget(qty_label)
        
        self.place_quantity = QtWidgets.QDoubleSpinBox()
        self.place_quantity.setMinimum(0.1)
        self.place_quantity.setMaximum(10000)
        self.place_quantity.setValue(1)
        self.place_quantity.setDecimals(2)
        self.place_quantity.setSingleStep(0.1)
        self.place_quantity.setMinimumHeight(40)
        add_item_layout.addWidget(self.place_quantity, 1)
        
        unit_label = QtWidgets.QLabel("Unit:")
        unit_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        add_item_layout.addWidget(unit_label)
        
        self.place_unit_combo = QtWidgets.QComboBox()
        self.place_unit_combo.addItems(["L", "Kg", "pcs"])
        self.place_unit_combo.setMinimumHeight(40)
        add_item_layout.addWidget(self.place_unit_combo, 1)
        
        price_label = QtWidgets.QLabel("Price/Unit:")
        price_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        add_item_layout.addWidget(price_label)
        
        self.place_price = QtWidgets.QDoubleSpinBox()
        self.place_price.setMinimum(0)
        self.place_price.setMaximum(1000000)
        self.place_price.setValue(0)
        self.place_price.setPrefix("৳ ")
        self.place_price.setMinimumHeight(40)
        add_item_layout.addWidget(self.place_price, 1)
        
        add_btn = QtWidgets.QPushButton("+ Add Item")
        add_btn.setMinimumHeight(40)
        add_btn.setFixedWidth(120)
        add_btn.clicked.connect(self.add_order_item)
        add_item_layout.addWidget(add_btn)
        
        items_layout.addLayout(add_item_layout)
        
        # Items table
        self.place_items_table = QtWidgets.QTableWidget()
        self.place_items_table.setColumnCount(6)
        self.place_items_table.setHorizontalHeaderLabels(["Product", "Quantity", "Unit", "Price/Unit", "Subtotal", "Actions"])
        self.place_items_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.place_items_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.place_items_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.place_items_table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.place_items_table.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.place_items_table.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self.place_items_table.setMinimumHeight(150)  # Minimum height for at least 3 rows
        self.place_items_table.verticalHeader().setDefaultSectionSize(45)  # Row height
        self.place_items_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #A3B18A;
                gridline-color: #D8E2D1;
            }
            QHeaderView::section {
                background-color: #344E41;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        items_layout.addWidget(self.place_items_table)
        
        items_group.setLayout(items_layout)
        form_layout.addWidget(items_group)
        
        # Additional Information
        additional_group = QtWidgets.QGroupBox("Additional Information")
        additional_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                border: 2px solid #A3B18A;
                border-radius: 8px;
                margin-top: 15px;
                padding: 20px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background-color: white;
            }
        """)
        additional_layout = QtWidgets.QFormLayout()
        additional_layout.setSpacing(15)
        additional_layout.setContentsMargins(15, 25, 15, 15)
        
        self.place_delivery_date = QtWidgets.QDateEdit()
        self.place_delivery_date.setCalendarPopup(True)
        self.place_delivery_date.setDate(QtCore.QDate.currentDate().addDays(1))
        self.place_delivery_date.setDisplayFormat("yyyy-MM-dd")
        self.place_delivery_date.setMinimumHeight(40)
        additional_layout.addRow("Delivery Date:", self.place_delivery_date)
        
        self.place_notes = QtWidgets.QTextEdit()
        self.place_notes.setMaximumHeight(100)
        self.place_notes.setPlaceholderText("Additional notes or special instructions...")
        additional_layout.addRow("Notes:", self.place_notes)
        
        additional_group.setLayout(additional_layout)
        form_layout.addWidget(additional_group)
        
        # Total display
        total_container = QtWidgets.QWidget()
        total_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        total_layout = QtWidgets.QHBoxLayout(total_container)
        total_layout.setContentsMargins(20, 15, 20, 15)
        
        total_label = QtWidgets.QLabel("Order Total:")
        total_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #344E41;")
        total_layout.addWidget(total_label)
        
        total_layout.addStretch()
        
        self.total_amount_label = QtWidgets.QLabel("৳ 0.00")
        self.total_amount_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #588157;")
        total_layout.addWidget(self.total_amount_label)
        
        form_layout.addWidget(total_container)
        
        # Submit button
        submit_layout = QtWidgets.QHBoxLayout()
        submit_layout.addStretch()
        
        clear_btn = QtWidgets.QPushButton("Clear Form")
        clear_btn.setFixedHeight(45)
        clear_btn.setFixedWidth(150)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ccc;
                color: #333;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #bbb;
            }
        """)
        clear_btn.clicked.connect(self.clear_order_form)
        submit_layout.addWidget(clear_btn)
        
        submit_btn = QtWidgets.QPushButton("Place Order")
        submit_btn.setFixedHeight(45)
        submit_btn.setFixedWidth(150)
        submit_btn.setStyleSheet("""
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
        """)
        submit_btn.clicked.connect(self.submit_order_form)
        submit_layout.addWidget(submit_btn)
        
        form_layout.addLayout(submit_layout)
        form_layout.addStretch()
        
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        # Initialize order items list
        self.place_order_items = []
        
        return widget
    
    def add_order_item(self):
        """Add an item to the order in Place Order tab."""
        product = self.place_product_combo.currentText()
        quantity = self.place_quantity.value()
        unit = self.place_unit_combo.currentText()
        price_per_unit = self.place_price.value()
        subtotal = quantity * price_per_unit
        
        self.place_order_items.append({
            "product_type": product,
            "quantity": quantity,
            "unit": unit,
            "price_per_unit": price_per_unit,
            "notes": ""
        })
        
        # Add to table
        row = self.place_items_table.rowCount()
        self.place_items_table.insertRow(row)
        
        self.place_items_table.setItem(row, 0, QtWidgets.QTableWidgetItem(product))
        self.place_items_table.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{quantity:.2f}"))
        self.place_items_table.setItem(row, 2, QtWidgets.QTableWidgetItem(unit))
        self.place_items_table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"৳ {price_per_unit:.2f}"))
        self.place_items_table.setItem(row, 4, QtWidgets.QTableWidgetItem(f"৳ {subtotal:.2f}"))
        
        # Remove button
        remove_btn = QtWidgets.QPushButton("Remove")
        remove_btn.setMinimumWidth(80)
        remove_btn.setFixedHeight(30)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 3px;
                padding: 5px 15px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_order_item(row))
        self.place_items_table.setCellWidget(row, 5, remove_btn)
        
        # Reset inputs
        self.place_quantity.setValue(1)
        self.place_price.setValue(0)
        
        # Update total
        self.update_order_total()
        
        # Adjust table height dynamically
        self.adjust_items_table_height()
    
    def remove_order_item(self, row):
        """Remove an item from the order in Place Order tab."""
        if 0 <= row < len(self.place_order_items):
            self.place_order_items.pop(row)
            self.place_items_table.removeRow(row)
            # Rebuild the table to fix indices
            self.rebuild_items_table()
            # Adjust table height after removal
            self.adjust_items_table_height()
    
    def rebuild_items_table(self):
        """Rebuild the items table after removal."""
        self.place_items_table.setRowCount(0)
        temp_items = self.place_order_items.copy()
        self.place_order_items = []
        for item in temp_items:
            row = self.place_items_table.rowCount()
            self.place_items_table.insertRow(row)
            
            self.place_items_table.setItem(row, 0, QtWidgets.QTableWidgetItem(item['product_type']))
            self.place_items_table.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{item['quantity']:.2f}"))
            self.place_items_table.setItem(row, 2, QtWidgets.QTableWidgetItem(item['unit']))
            self.place_items_table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"৳ {item['price_per_unit']:.2f}"))
            subtotal = item['quantity'] * item['price_per_unit']
            self.place_items_table.setItem(row, 4, QtWidgets.QTableWidgetItem(f"৳ {subtotal:.2f}"))
            
            remove_btn = QtWidgets.QPushButton("Remove")
            remove_btn.setMinimumWidth(80)
            remove_btn.setFixedHeight(30)
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #d9534f;
                    color: white;
                    border-radius: 3px;
                    padding: 5px 15px;
                    font-size: 10pt;
                }
                QPushButton:hover {
                    background-color: #c9302c;
                }
            """)
            remove_btn.clicked.connect(lambda checked, r=row: self.remove_order_item(r))
            self.place_items_table.setCellWidget(row, 5, remove_btn)
            
            self.place_order_items.append(item)
    
    def update_order_total(self):
        """Calculate and update the order total."""
        total = sum(item['quantity'] * item['price_per_unit'] for item in self.place_order_items)
        self.total_amount_label.setText(f"৳ {total:,.2f}")
    
    def adjust_items_table_height(self):
        """Dynamically adjust the items table height based on number of rows."""
        row_count = self.place_items_table.rowCount()
        
        if row_count == 0:
            # Minimum height for empty table
            self.place_items_table.setMaximumHeight(150)
        elif row_count <= 4:
            # Show all rows without scrolling (up to 4 items)
            header_height = self.place_items_table.horizontalHeader().height()
            row_height = self.place_items_table.verticalHeader().defaultSectionSize()
            total_height = header_height + (row_height * row_count) + 10  # +10 for borders
            self.place_items_table.setMaximumHeight(total_height)
        else:
            # Show 4 rows + scrollbar for more items
            header_height = self.place_items_table.horizontalHeader().height()
            row_height = self.place_items_table.verticalHeader().defaultSectionSize()
            total_height = header_height + (row_height * 4) + 10
            self.place_items_table.setMaximumHeight(total_height)
    
    def clear_order_form(self):
        """Clear the order form."""
        self.place_customer_name.clear()
        self.place_customer_email.clear()
        self.place_customer_phone.clear()
        self.place_delivery_date.setDate(QtCore.QDate.currentDate().addDays(1))
        self.place_notes.clear()
        self.place_items_table.setRowCount(0)
        self.place_order_items = []
        self.update_order_total()
        self.adjust_items_table_height()
    
    def submit_order_form(self):
        """Submit the order form."""
        customer_name = self.place_customer_name.text().strip()
        customer_email = self.place_customer_email.text().strip()
        customer_phone = self.place_customer_phone.text().strip()
        delivery_date = self.place_delivery_date.date().toString("yyyy-MM-dd")
        notes = self.place_notes.toPlainText().strip()
        
        # Validation
        if not customer_name:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Customer name is required!")
            return
        
        if not self.place_order_items:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Please add at least one item to the order!")
            return
        
        # Prepare request
        order_data = {
            "customer_name": customer_name,
            "customer_email": customer_email if customer_email else None,
            "customer_phone": customer_phone if customer_phone else None,
            "delivery_date": delivery_date,
            "notes": notes if notes else None,
            "items": self.place_order_items
        }
        
        try:
            response = requests.post("http://localhost:8000/orders", json=order_data)
            response.raise_for_status()
            
            result = response.json()
            QtWidgets.QMessageBox.information(
                self, 
                "Success", 
                f"Order {result['data']['order_id']} created successfully!"
            )
            
            # Clear form and switch to All Orders tab
            self.clear_order_form()
            self.switch_tab(0)
            self.load_orders()
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to create order: {str(e)}"
            )
    
    def open_place_order_dialog(self):
        """Open the place order dialog - kept for compatibility but switches to tab instead."""
        self.switch_tab(1)
