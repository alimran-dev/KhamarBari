from PyQt5 import QtCore, QtGui, QtWidgets
import os, requests, json

class SignupPage(QtWidgets.QWidget):
    login_requested = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.bg = QtWidgets.QLabel(self)
        self.bg.setScaledContents(True)
        self.bg_pixmap = QtGui.QPixmap(os.path.join(self.base_dir, "images", "login_back.png"))
        
        # Semi-transparent form container
        self.form_frame = QtWidgets.QFrame(self)
        # Note: SetSizeHint or adjusting the layout might be better than fixed large min size
        self.form_frame.setMinimumSize(1200, 1200) 
        self.form_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(88, 129, 87, 204);
                border-radius: 30px; 
                border: 2px solid rgba(0, 0, 0, 0);
                padding: 20px; 
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(self.form_frame, alignment=QtCore.Qt.AlignHCenter)
        layout.addStretch()

        # Layout inside form_frame
        self.form_layout = QtWidgets.QVBoxLayout(self.form_frame)
        self.form_layout.setContentsMargins(30, 20, 30, 20)
        self.form_layout.setSpacing(15)

        # Title
        self.title = QtWidgets.QLabel("Signup")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setStyleSheet("""
            QLabel {
                font-family: 'Aladin';
                font-size: 80pt; 
                color: white;
                background: transparent;
            }
        """)
        self.form_layout.addWidget(self.title)

        # Fields
        self.owner_name = self._create_line_edit("Owner Name (Full Name)")
        self.farm_name = self._create_line_edit("Farm Name")
        self.phone_number = self._create_line_edit("Phone Number")
        self.email = self._create_line_edit("Email")
        self.password = self._create_line_edit("Password", echo_mode=QtWidgets.QLineEdit.Password)
        self.confirm_password = self._create_line_edit("Confirm Password", echo_mode=QtWidgets.QLineEdit.Password)

        # >>> FIX 1: Add all QLineEdits to the layout <<<
        self.form_layout.addWidget(self.owner_name, alignment=QtCore.Qt.AlignHCenter)
        self.form_layout.addWidget(self.farm_name, alignment=QtCore.Qt.AlignHCenter)
        self.form_layout.addWidget(self.phone_number, alignment=QtCore.Qt.AlignHCenter)
        self.form_layout.addWidget(self.email, alignment=QtCore.Qt.AlignHCenter)
        self.form_layout.addWidget(self.password, alignment=QtCore.Qt.AlignHCenter)
        self.form_layout.addWidget(self.confirm_password, alignment=QtCore.Qt.AlignHCenter)
        
        # >>> FIX 2: Setup password toggle actions for both password fields <<<
        self.password_action = self._setup_password_toggle(self.password)
        self.confirm_password_action = self._setup_password_toggle(self.confirm_password)


        # Install Event Filters for Focus Control
        self.password.installEventFilter(self)
        self.confirm_password.installEventFilter(self)

        self.form_layout.addStretch(1) 

        # Signup Button
        self.signup_button = QtWidgets.QPushButton("Signup")
        self.signup_button.setFixedWidth(250)
        self.signup_button.setStyleSheet("""
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
        self.form_layout.addWidget(self.signup_button, alignment=QtCore.Qt.AlignHCenter)

        # Login Redirect Link
        self.form_layout.addSpacing(15)
        self.login_redirect_label = QtWidgets.QLabel("Already have an account? <a href='#'>Log In</a>")
        self.login_redirect_label.setAlignment(QtCore.Qt.AlignCenter)
        self.login_redirect_label.setStyleSheet(self._get_link_style())
        
        # FIX: Use TextInteractionFlags for internal links instead of setOpenExternalLinks(True)
        self.login_redirect_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse | QtCore.Qt.LinksAccessibleByMouse)
        
        # Connect to the signal emitter method
        self.login_redirect_label.linkActivated.connect(self._handle_login_redirect)
        self.form_layout.addWidget(self.login_redirect_label, alignment=QtCore.Qt.AlignHCenter)
        
        self.form_layout.addStretch(1)

        self.signup_button.clicked.connect(self.handle_signup)

    def _create_line_edit(self, placeholder_text, echo_mode=QtWidgets.QLineEdit.Normal):
        """Helper function to create a consistently styled QLineEdit."""
        line_edit = QtWidgets.QLineEdit()
        line_edit.setPlaceholderText(placeholder_text)
        line_edit.setMinimumWidth(700)
        line_edit.setEchoMode(echo_mode)

        # ===== Updated style for all fields =====
        line_edit.setStyleSheet("""
            QLineEdit {
                background-color: #F0EFEF;
                border-radius: 15px;
                padding: 15px 25px;
                font-family: 'Amaranth';
                font-size: 12pt;
            }
        """)
        return line_edit
    
    def _get_link_style(self):
        """Helper for link styling."""
        return """
            QLabel {
                background-color: transparent; 
                border: none;
                padding: 0;
                color: #FFFFFF; 
                font-family: 'Amaranth';
                font-size: 10pt;
            }
            QLabel a {
                color: #FFFFFF; 
                text-decoration: none; 
            }
            QLabel a:hover {
                text-decoration: underline; 
                color: #A3B18A; 
            }
        """

    def eventFilter(self, source, event):
        """Custom event filter to show/hide the password toggle button based on focus and content."""
        action_to_control = None
        
        if source == self.password:
            action_to_control = self.password_action
        elif source == self.confirm_password:
            action_to_control = self.confirm_password_action
            
        if action_to_control:
            if event.type() == QtCore.QEvent.FocusIn:
                action_to_control.setVisible(True)
            elif event.type() == QtCore.QEvent.FocusOut:
                # Only hide if the field is empty and focus is lost
                if not source.text():
                    action_to_control.setVisible(False)
                # Keep visible if it contains text, even if focus is lost
                else:
                    action_to_control.setVisible(True) # This ensures the icon remains if text is present

        return super().eventFilter(source, event)

    def _setup_password_toggle(self, line_edit):
        """Sets up the 'Show/Hide Password' QAction icon and returns the action."""
        
        show_password_action = QtWidgets.QAction(line_edit)
        
        # NOTE: Assumes 'images/eye_view.png' and 'images/eye_hide.png' exist for password toggle
        icon_path_show = os.path.join(self.base_dir, "images", "eye_view.png")
        icon_path_hide = os.path.join(self.base_dir, "images", "eye_hide.png")

        # Create QPixmaps only once to avoid performance issues
        if not hasattr(self, '_icon_pixmap_show'):
            self._icon_pixmap_show = QtGui.QPixmap(icon_path_show)
            self._icon_pixmap_hide = QtGui.QPixmap(icon_path_hide)
        
        icon_size = QtCore.QSize(20, 20) 
        
        # Check if icons are loaded (and scale if necessary)
        if self._icon_pixmap_show.isNull() or self._icon_pixmap_hide.isNull():
             # Fallback if icons are missing
             show_password_action.setText("👁") 
             show_password_action.setToolTip("Toggle Password Visibility")
             self.icon_show = None # Indicate fallback mode
             self.icon_hide = None
        else:
             self.icon_show = QtGui.QIcon(self._icon_pixmap_show.scaled(icon_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
             self.icon_hide = QtGui.QIcon(self._icon_pixmap_hide.scaled(icon_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
             show_password_action.setText("")

        # Set initial icon state
        if line_edit.echoMode() == QtWidgets.QLineEdit.Password and self.icon_show:
            show_password_action.setIcon(self.icon_show)
            show_password_action.setToolTip("Show Password")
        elif self.icon_hide:
             show_password_action.setIcon(self.icon_hide)
             show_password_action.setToolTip("Hide Password")

        show_password_action.triggered.connect(lambda: self._toggle_password_visibility(line_edit, show_password_action))

        line_edit.addAction(show_password_action, QtWidgets.QLineEdit.TrailingPosition)
        
        # Hide initially, only show on focus or content
        show_password_action.setVisible(False) 
        
        return show_password_action
        
    def _toggle_password_visibility(self, line_edit, action):
        """Toggles the visibility mode of the QLineEdit and updates the icon."""
        is_password_hidden = line_edit.echoMode() == QtWidgets.QLineEdit.Password
        
        # Determine if we are in icon mode or fallback text mode
        is_using_icons = self.icon_show is not None 
        
        if is_password_hidden:
            line_edit.setEchoMode(QtWidgets.QLineEdit.Normal)
            if is_using_icons:
                action.setIcon(self.icon_hide)
            action.setToolTip("Hide Password")
        else:
            line_edit.setEchoMode(QtWidgets.QLineEdit.Password)
            if is_using_icons:
                action.setIcon(self.icon_show)
            action.setToolTip("Show Password")
            
        # Update fallback text if not using icons
        if not is_using_icons: 
             action.setText("•" if is_password_hidden else "👁")


    def handle_signup(self):
        """Handles the signup button click and API call."""
        
        owner_name_value = self.owner_name.text().strip()
        farm_name_value = self.farm_name.text().strip()
        phone_value = self.phone_number.text().strip()
        email_value = self.email.text().strip()
        password_value = self.password.text()
        confirm_password_value = self.confirm_password.text()

        print("\n--- Signup Attempt ---")
        
        if not all([owner_name_value, farm_name_value, password_value, confirm_password_value, email_value]):
             QtWidgets.QMessageBox.warning(self, "Signup Error", "Please fill in all required fields (Owner Name, Farm Name, Email, Password).")
             return

        if password_value != confirm_password_value:
             QtWidgets.QMessageBox.warning(self, "Signup Error", "Passwords do not match.")
             return

        signup_payload = {
            "owner_name": owner_name_value,
            "farm_name": farm_name_value,
            "phone_number": phone_value,
            "email": email_value,
            "password": password_value
        }
        
        API_ENDPOINT = "http://localhost:8000/signup"

        try:
            response = requests.post(API_ENDPOINT, json=signup_payload)
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                print("API Success:", response_data)
                QtWidgets.QMessageBox.information(self, "Signup Success", 
                                                    "Account created successfully! Redirecting to login.")
                self._clear_form()
                self._handle_login_redirect() # Redirect on successful sign up
            
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get("detail") or error_data.get("message") or "Unknown error."
                except json.JSONDecodeError:
                    error_message = response.text or "Server returned an invalid JSON or no error message."

                print(f"API Error ({response.status_code}): {error_message}")
                QtWidgets.QMessageBox.critical(self, "Signup Failed", 
                                                f"Signup failed with status {response.status_code}:\n{error_message}")

        except requests.exceptions.RequestException as e:
            print(f"Connection Error: {e}")
            QtWidgets.QMessageBox.critical(self, "Connection Error", 
                                            f"Could not connect to the server at {API_ENDPOINT}.")
            
    def _clear_form(self):
        """Clears all input fields."""
        self.owner_name.clear()
        self.farm_name.clear()
        self.phone_number.clear()
        self.email.clear()
        self.password.clear()
        self.confirm_password.clear()
        # Reset visibility state for password toggles
        if hasattr(self, 'password_action'): self.password_action.setVisible(False)
        if hasattr(self, 'confirm_password_action'): self.confirm_password_action.setVisible(False)
        self.owner_name.setFocus()

    def _handle_login_redirect(self):
        """Emits signal to switch to Login window."""
        print("Redirecting to Login Page!")
        self.login_requested.emit()
        

    def resizeEvent(self, event):
        if not self.bg_pixmap.isNull():
            self.bg.setPixmap(self.bg_pixmap.scaled(
                self.size(),
                QtCore.Qt.KeepAspectRatioByExpanding,
                QtCore.Qt.SmoothTransformation
            ))
        self.bg.resize(self.size())
        super().resizeEvent(event)