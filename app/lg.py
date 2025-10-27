from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os

class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")

        # ==== Base directory for images ====
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # ==== Background image (using your existing login_back.png) ====
        self.bg = QtWidgets.QLabel(self)
        self.bg.setScaledContents(True)
        self.bg.lower()

        bg_path = os.path.join(self.base_dir, "images", "login_back.png")
        self.bg_pixmap = QtGui.QPixmap(bg_path)
        # Fallback if the image is missing (optional, but good practice)
        if self.bg_pixmap.isNull():
            print(f"Warning: Background image not found at {bg_path}.")
        
        # ==== Semi-transparent form container (Responsive and Centered, matching visual design) ====
        self.form_frame = QtWidgets.QFrame(self)
        
        self.form_frame.setStyleSheet("""
            QFrame {
                /* Exact green from image */
                background-color: rgba(88, 129, 87, 220); 
                border-radius: 30px; 
                border: 1px solid rgba(255, 255, 255, 0.1); 
                padding: 30px; 
            }
        """)
        # Set a minimum size for the form to ensure readability on very small windows
        self.form_frame.setMinimumSize(425, 500) 
        self.form_frame.setMaximumWidth(500) 

        # Center the form frame using main layout with proportional stretches
        self.main_layout = QtWidgets.QVBoxLayout(self)
        
        self.horizontal_container = QtWidgets.QHBoxLayout()
        self.horizontal_container.addStretch(1) # Left stretch
        # Give the form a central position
        self.horizontal_container.addWidget(self.form_frame, 0) 
        self.horizontal_container.addStretch(1) # Right stretch
        
        self.main_layout.addStretch(1)  # Top stretch
        self.main_layout.addLayout(self.horizontal_container, 0) 
        self.main_layout.addStretch(1)  # Bottom stretch
        
        # ==== Layout inside form_frame ====
        self.form_layout = QtWidgets.QVBoxLayout(self.form_frame)
        self.form_layout.setContentsMargins(40, 30, 40, 30) 
        self.form_layout.setSpacing(15) 

        # ==== Title (Now using specific transparent styling) ====
        self.title = QtWidgets.QLabel("Login")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setStyleSheet("""
            QLabel {
                font-family: 'Aladin'; 
                font-size: 50pt; 
                color: white; 
                /* Ensures no bounding box or background is visible */
                background-color: transparent; 
                border: none;
                padding: 0;
                margin-bottom: 30px; 
            }
        """)
        self.title.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.title.setFocusPolicy(QtCore.Qt.NoFocus)
        self.form_layout.addWidget(self.title)

        # ==== Input Fields (White Background, Polished) ====
        self.username = self._create_line_edit("Username", icon_path="images/user.png")
        self.form_layout.addWidget(self.username)
        self.username.returnPressed.connect(lambda: self.password.setFocus())
        
        self.password = self._create_line_edit("Password", echo_mode=QtWidgets.QLineEdit.Password, icon_path="images/lock.png")
        self.form_layout.addWidget(self.password)
        self.password.returnPressed.connect(self.handle_login) # Connect Enter key press to login

        # --- Setup password toggle and install event filter ---
        self.password_action = self._setup_password_toggle(self.password)
        self.password.installEventFilter(self)
        
        # ==== Forgot Password & Register Links (Wide-Spaced and Themed Green/White) ====
        links_h_layout = QtWidgets.QHBoxLayout()
        links_h_layout.setContentsMargins(0, 0, 0, 0)
        
        # Register Link (Left Aligned)
        self.register_label = QtWidgets.QLabel("<a href='#'>Register</a>")
        self.register_label.setStyleSheet(self._get_link_style(link_name="register"))
        self.register_label.setOpenExternalLinks(True)
        self.register_label.linkActivated.connect(self._handle_register)
        links_h_layout.addWidget(self.register_label)

        links_h_layout.addStretch(1) # Stretch in the middle to push them to the sides

        # Forgot Password Link (Right Aligned)
        self.forgot_password_label = QtWidgets.QLabel("<a href='#'>Forgot password?</a>")
        self.forgot_password_label.setStyleSheet(self._get_link_style(link_name="forgot"))
        self.forgot_password_label.setOpenExternalLinks(True) 
        self.forgot_password_label.linkActivated.connect(self._handle_forgot_password)
        links_h_layout.addWidget(self.forgot_password_label)

        self.form_layout.addLayout(links_h_layout)
        self.form_layout.addSpacing(40) 

        # ==== Login Button (Centered) ====
        self.login_button = QtWidgets.QPushButton("Login")
        self.login_button.setStyleSheet("""
            QPushButton {
                /* Gradient Background matching image */
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                            stop: 0 #B5C9A9, stop: 1 #A3B18A);
                color: #344E41; 
                font-family: 'Amaranth';
                font-size: 13pt; 
                font-weight: bold;
                border: 2px solid #344E41; 
                border-radius: 15px; 
                padding: 8px 15px; 
                /* Fixed width for button matching image appearance */
                min-width: 150px; 
                max-width: 200px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                            stop: 0 #C2D6B8, stop: 1 #B5C9A9); 
                border: 2px solid #588157; 
            }
            QPushButton:pressed {
                background-color: #7A997A; 
                padding-top: 10px;
                padding-bottom: 6px; 
            }
        """)
        self.login_button.clicked.connect(self.handle_login) # Connect button click to login logic
        
        # Layout to center the button horizontally
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.login_button)
        button_layout.addStretch(1)
        self.form_layout.addLayout(button_layout)
        
        self.form_layout.addStretch(1) 

    # --- Helper Methods ---

    def _get_link_style(self, link_name):
        """Helper for link styling, now using white (#FFFFFF) for the base color."""
        
        # Set to white (#FFFFFF) as requested by the user
        color = "#FFFFFF"            
        # Using the theme's accent color for the hover state
        hover_color = "#A3B18A"    
        
        return f"""
            QLabel {{
                /* Critical: Ensure the QLabel itself is completely transparent */
                background-color: transparent; 
                border: none;
                padding: 0;
                color: {color}; /* Base color: #FFFFFF */
                font-family: 'Amaranth';
                font-size: 10pt;
            }}
            QLabel a {{
                color: {color}; /* Explicitly setting the anchor text color to white */
                text-decoration: none; 
            }}
            QLabel a:hover {{
                text-decoration: underline; 
                color: {hover_color}; /* Hover color: Soft accent green */
            }}
        """

    def _create_line_edit(self, placeholder_text, echo_mode=QtWidgets.QLineEdit.Normal, icon_path=None):
        """Helper function to create a consistently styled QLineEdit matching the image's white input fields."""
        line_edit = QtWidgets.QLineEdit()
        line_edit.setPlaceholderText(placeholder_text)
        # Apply maximum width constraint to prevent inputs from stretching too wide in the centered frame
        line_edit.setMaximumWidth(350) 
        line_edit.setEchoMode(echo_mode)

        # Style matching white input fields from the image
        style = """
            QLineEdit {
                background-color: #FFFFFF; 
                border-radius: 10px; 
                border: 1px solid rgba(0, 0, 0, 0.1); 
                padding: 8px 15px; 
                color: #344E41; 
                font-family: 'Amaranth';
                font-size: 10pt; 
            }
            QLineEdit::placeholder {
                color: #8D8D8D; 
            }
            QLineEdit:focus {
                border: 2px solid #A3B18A; 
                background-color: #FFFFFF; 
            }
            /* Style for the eye icon button inside the QLineEdit */
            QLineEdit QToolButton {
                border: none;
                background-color: transparent;
                padding-right: 8px; 
            }
            QLineEdit QToolButton:hover {
                background-color: rgba(0,0,0,0.05);
            }
        """
        
        if icon_path:
            # QAction implementation for the *leading* icon (Username/Lock)
            pixmap = QtGui.QPixmap(os.path.join(self.base_dir, icon_path))
            if not pixmap.isNull():
                # Scale the leading icon slightly
                icon_size = QtCore.QSize(18, 18) 
                icon = QtGui.QIcon(pixmap.scaled(icon_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
                action = QtWidgets.QAction(icon, "", line_edit)
                line_edit.addAction(action, QtWidgets.QLineEdit.LeadingPosition)

        line_edit.setStyleSheet(style)
        return line_edit

    # --- NEW METHODS FOR PASSWORD TOGGLE ---

    def _setup_password_toggle(self, line_edit):
        """Sets up the 'Show/Hide Password' QAction (eye icon) and returns the action."""
        
        show_password_action = QtWidgets.QAction(line_edit)
        
        # Define Custom Icons (MATCHING USER-PROVIDED FILENAMES)
        icon_path_show = os.path.join(self.base_dir, "images", "eye_view.png")
        icon_path_hide = os.path.join(self.base_dir, "images", "eye_hide.png")

        self.icon_pixmap_show = QtGui.QPixmap(icon_path_show)
        self.icon_pixmap_hide = QtGui.QPixmap(icon_path_hide)
        
        # Fallback if icons are missing
        icon_size = QtCore.QSize(20, 20) 
        if self.icon_pixmap_show.isNull() or self.icon_pixmap_hide.isNull():
             # Fallback: using text if image files are not found
             show_password_action.setText("•••") 
             show_password_action.setToolTip(f"Toggle Password Visibility (Could not load icons)")
             self.icon_show = show_password_action.icon()
             self.icon_hide = show_password_action.icon()
        else:
             # Use the loaded image icons
             self.icon_show = QtGui.QIcon(self.icon_pixmap_show.scaled(icon_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
             self.icon_hide = QtGui.QIcon(self.icon_pixmap_hide.scaled(icon_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
             # Set text to empty string when using icons
             show_password_action.setText("")

        show_password_action.setIcon(self.icon_show if line_edit.echoMode() == QtWidgets.QLineEdit.Password else self.icon_hide) 
        show_password_action.setToolTip("Show Password")

        show_password_action.triggered.connect(lambda: self._toggle_password_visibility(line_edit, show_password_action))

        # Add the action (icon/button) to the right side (TrailingPosition)
        line_edit.addAction(show_password_action, QtWidgets.QLineEdit.TrailingPosition)
        
        # CRITICAL: Set initial visibility to hidden as requested
        show_password_action.setVisible(False)
        
        # Return the action reference for external control (via eventFilter)
        return show_password_action

    def _toggle_password_visibility(self, line_edit, action):
        """Toggles the visibility mode of the QLineEdit and updates the icon."""
        is_password_hidden = line_edit.echoMode() == QtWidgets.QLineEdit.Password
        
        # Check if we are using image icons or the fallback text
        is_using_icons = action.text() == "" 
        
        if is_password_hidden:
            line_edit.setEchoMode(QtWidgets.QLineEdit.Normal)
            action.setIcon(self.icon_hide)
            action.setToolTip("Hide Password")
            if not is_using_icons: action.setText("•••") # Update fallback text if needed
        else:
            line_edit.setEchoMode(QtWidgets.QLineEdit.Password)
            action.setIcon(self.icon_show)
            action.setToolTip("Show Password")
            if not is_using_icons: action.setText("•••") # Update fallback text if needed

    # NEW: Event Filter to handle focus events and show/hide the button
    def eventFilter(self, source, event):
        """Custom event filter to show/hide the password toggle button based on focus and content."""
        
        action_to_control = None
        
        if source == self.password:
            action_to_control = self.password_action
            
        if action_to_control:
            if event.type() == QtCore.QEvent.FocusIn:
                # Show the button when the field gets focus
                action_to_control.setVisible(True)
            elif event.type() == QtCore.QEvent.FocusOut:
                # Hide the button when the field loses focus AND the field is empty
                if not source.text():
                    action_to_control.setVisible(False)

        return super().eventFilter(source, event)

    # --- Event Handlers ---

    def handle_login(self):
        """
        Handles the login button click or Enter key press.
        This function retrieves and prints the text from the input fields.
        
        NOTE: The self.login_button.animateClick() call was removed 
        to prevent recursive/infinite calls to this handler when triggered by 
        the button itself or the Enter key signal.
        """
        
        # --- Retrieving Input Box Values ---
        username_value = self.username.text()
        password_value = self.password.text()
        
        print("\n--- Login Attempt ---")
        print("Username:", username_value)
        print("Password:", password_value)
        # -----------------------------------
        
        if not all([username_value, password_value]):
             print("ERROR: Both username and password must be filled.")
             return
        
        print("Attempting login...")

    def _handle_forgot_password(self):
        print("Forgot password link clicked!")

    def _handle_register(self):
        print("Register link clicked!")

    # ==== Background auto-resize ====
    def resizeEvent(self, event):
        if not self.bg_pixmap.isNull():
            self.bg.setPixmap(self.bg_pixmap.scaled(
                self.size(),
                QtCore.Qt.KeepAspectRatioByExpanding,
                QtCore.Qt.SmoothTransformation
            ))
        self.bg.resize(self.size())
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
