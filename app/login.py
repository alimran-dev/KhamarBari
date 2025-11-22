# login.py
from PyQt5 import QtCore, QtGui, QtWidgets
import os, requests, json

class LoginPage(QtWidgets.QWidget):
    signup_requested = QtCore.pyqtSignal()
    login_successful = QtCore.pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # background label (not top-level)
        self.bg = QtWidgets.QLabel(self)
        self.bg.setScaledContents(True)
        self.bg_pixmap = QtGui.QPixmap(os.path.join(self.base_dir, "images", "login_back.png"))

        # central form frame
        self.form_frame = QtWidgets.QFrame(self)
        self.form_frame.setMinimumSize(1200, 900)
        self.form_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(88, 129, 87, 204);
                border-radius: 40px;
                border: 3px solid rgba(0, 0, 0, 0);
                padding: 30px;
            }
        """)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(self.form_frame, alignment=QtCore.Qt.AlignHCenter)
        layout.addStretch()

        # Layout inside form_frame
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(40) 

        # Title
        inner = QtWidgets.QVBoxLayout(self.form_frame)
        title = QtWidgets.QLabel("Login")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-family: 'Aladin';
                font-size: 80pt; 
                color: white;
                background: transparent;
            }
        """)
        title.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        inner.addWidget(title)

        # Email Field
        self.email = QtWidgets.QLineEdit() 
        self.email.setPlaceholderText("Email") 
        self.email.setMinimumWidth(700)
        self.email.setStyleSheet("""
            QLineEdit {
                background-color: #F0EFEF;
                border-radius: 15px;
                padding: 15px 25px;
                font-family: 'Amaranth';
                font-size: 12pt;
            }
        """)
        inner.addWidget(self.email, alignment=QtCore.Qt.AlignHCenter)
        self.email.returnPressed.connect(lambda: self.password.setFocus())

        # Password
        self.password = QtWidgets.QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setMinimumWidth(700)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setStyleSheet("""
            QLineEdit {
                background-color: #F0EFEF;
                border-radius: 15px;
                padding: 15px 25px;
                font-family: 'Amaranth';
                font-size: 12pt;
            }
        """)
        inner.addWidget(self.password, alignment=QtCore.Qt.AlignHCenter)
        self.password.returnPressed.connect(self.handle_login)

        inner.addStretch(1)

        # Login Button
        self.login_button = QtWidgets.QPushButton("Login")
        self.login_button.setFixedWidth(250) 
        self.login_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                            stop: 0 #B5C9A9, stop: 1 #A3B18A);
                color: #344E41;
                font-family: 'Amaranth';
                font-size: 14pt;
                font-weight: bold; 
                border: 2px solid #344E41;
                border-radius: 20px;
                padding: 15px 30px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                            stop: 0 #C2D6B8, stop: 1 #B5C9A9);
                border: 2px solid #588157; 
            }
            QPushButton:pressed {
                background-color: #7A997A; 
                padding-top: 17px;
                padding-bottom: 13px; 
            }
        """)
        inner.addWidget(self.login_button, alignment=QtCore.Qt.AlignHCenter)
        self.login_button.clicked.connect(self.handle_login)

        # Signup redirect link
        self.signup_redirect_label = QtWidgets.QLabel("Don't have an account? <a href='#'>Sign Up</a>")
        self.signup_redirect_label.setAlignment(QtCore.Qt.AlignCenter)
        self.signup_redirect_label.setStyleSheet(self._get_link_style())
        
        # FIX: Use TextInteractionFlags for internal links instead of setOpenExternalLinks(True)
        self.signup_redirect_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse | QtCore.Qt.LinksAccessibleByMouse)
        
        # Connect to the signal emitter method
        self.signup_redirect_label.linkActivated.connect(self._handle_signup_redirect)
        inner.addWidget(self.signup_redirect_label, alignment=QtCore.Qt.AlignHCenter)

        inner.addStretch(1)

    # --- Helper Methods ---

    def _get_link_style(self):
        """Helper for link styling."""
        return """
            QLabel {
                background-color: transparent; 
                color: white; 
                font-family: 'Amaranth';
                font-size: 11pt;
            }
            QLabel a {
                color: #FFFFFF; 
                text-decoration: none; 
                font-weight: bold;
            }
            QLabel a:hover {
                text-decoration: underline; 
                color: #A3B18A; 
            }
        """
        
    def _handle_signup_redirect(self):
        """Emits signal to switch to Signup window."""
        print("Redirecting to Signup Page!")
        self.signup_requested.emit()

    def handle_login(self):
        """Handles the login button click and API call."""
        email_value = self.email.text().strip()
        password_value = self.password.text()
        
        print("\n--- Login Attempt ---")
        
        if not email_value or not password_value:
             QtWidgets.QMessageBox.warning(self, "Login Error", "Please enter both email and password.")
             return

        login_payload = {"email": email_value, "password": password_value}
        API_ENDPOINT = "http://localhost:8000/login"

        try:
            response = requests.post(API_ENDPOINT, json=login_payload)
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                print("API Success. Response Data:", response_data) 
                
                # Success Logic: Emit the signal to switch to the main app
                self.login_successful.emit(response_data)
                
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get("detail") or error_data.get("message") or "Invalid credentials or unknown server error."
                except json.JSONDecodeError:
                    error_message = response.text or "Server returned an invalid JSON or no error message."

                print(f"API Error ({response.status_code}): {error_message}")
                QtWidgets.QMessageBox.critical(self, "Login Failed", 
                                                f"Login failed:\n{error_message}")

        except requests.exceptions.RequestException as e:
            print(f"Connection Error: {e}")
            QtWidgets.QMessageBox.critical(self, "Connection Error", 
                                            f"Could not connect to the server at {API_ENDPOINT}.")

    def resizeEvent(self, event):
        """Handles background image scaling and window resizing."""
        if not self.bg_pixmap.isNull():
            self.bg.setPixmap(self.bg_pixmap.scaled(
                self.size(),
                QtCore.Qt.KeepAspectRatioByExpanding,
                QtCore.Qt.SmoothTransformation
            ))
        self.bg.resize(self.size())
        super().resizeEvent(event)

