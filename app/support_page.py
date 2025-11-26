from PyQt5 import QtWidgets, QtCore, QtGui


class SupportPage(QtWidgets.QWidget):
    """Support Page - Currently unavailable"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        self.setStyleSheet("QWidget { background-color: #EBEAE3; }")
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Icon/Emoji
        icon_label = QtWidgets.QLabel("🛠️")
        icon_label.setAlignment(QtCore.Qt.AlignCenter)
        icon_label.setStyleSheet("""
            font-size: 120pt;
            color: #588157;
        """)
        layout.addWidget(icon_label)
        
        # Main message
        message_label = QtWidgets.QLabel("The support is not supporting right now")
        message_label.setAlignment(QtCore.Qt.AlignCenter)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            font-size: 24pt;
            font-weight: bold;
            color: #344E41;
            padding: 20px;
        """)
        layout.addWidget(message_label)
        
        # Additional info
        info_label = QtWidgets.QLabel("We apologize for the inconvenience.\nPlease check back later.")
        info_label.setAlignment(QtCore.Qt.AlignCenter)
        info_label.setStyleSheet("""
            font-size: 14pt;
            color: #588157;
            padding: 10px;
        """)
        layout.addWidget(info_label)
        
        # Spacer
        layout.addStretch()
