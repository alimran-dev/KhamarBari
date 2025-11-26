from PyQt5 import QtWidgets, QtCore
from finance_entry_page import FinanceEntryPage
from finance_summary_page import FinanceSummaryPage


BG_COLOR_LIGHT = "#EBEAE3"


class FinancePage(QtWidgets.QWidget):
    """Combined Finance Page with custom tabs for Entry and Summary"""
    
    def __init__(self, user_email):
        super().__init__()
        self.user_email = user_email
        self.setStyleSheet(f"QWidget {{ background-color: {BG_COLOR_LIGHT}; }}")
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI with custom tab bar"""
        # Main Layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(15)
        
        # Custom Tab Bar
        tab_container = QtWidgets.QWidget()
        tab_layout = QtWidgets.QHBoxLayout(tab_container)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        tab_layout.setAlignment(QtCore.Qt.AlignHCenter)
        
        # Tab Buttons
        self.btn_entry = self._create_tab_button("💰 New Entry", position="left")
        self.btn_summary = self._create_tab_button("📊 Summary", position="right")
        
        self.tabs = [self.btn_entry, self.btn_summary]
        
        for btn in self.tabs:
            tab_layout.addWidget(btn)
            btn.clicked.connect(self._handle_tab_click)
        
        main_layout.addWidget(tab_container)
        
        # Content Stack
        self.stack = QtWidgets.QStackedWidget()
        
        # Add pages
        self.entry_page = FinanceEntryPage(self.user_email)
        self.summary_page = FinanceSummaryPage(self.user_email)
        
        self.stack.addWidget(self.entry_page)
        self.stack.addWidget(self.summary_page)
        
        main_layout.addWidget(self.stack)
        
        # Set initial state
        self._update_tab_styles(self.btn_entry)
    
    def _create_tab_button(self, text, position):
        """Create a styled tab button."""
        btn = QtWidgets.QPushButton(text)
        btn.setFixedHeight(45)
        btn.setFixedWidth(200)
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        btn.setProperty("tab_pos", position)
        return btn
    
    def _handle_tab_click(self):
        """Handle tab button clicks."""
        sender = self.sender()
        if sender == self.btn_entry:
            self.stack.setCurrentIndex(0)
        elif sender == self.btn_summary:
            self.stack.setCurrentIndex(1)
            self.summary_page.load_data()
        
        self._update_tab_styles(sender)
    
    def _update_tab_styles(self, active_btn):
        """Update tab button styles to reflect active tab."""
        for btn in self.tabs:
            pos = btn.property("tab_pos")
            
            if pos == "left":
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
