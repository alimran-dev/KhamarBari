from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os

class SignupWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Signup")

        # ==== Base directory for images (Placeholder, as QIcons are often preferred in PyQt) ====
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # ==== Background image (Assuming 'signup_back.png' exists in 'images' folder) ====
        self.bg = QtWidgets.QLabel(self)
        self.bg.setScaledContents(True)
        self.bg.lower()

        bg_path = os.path.join(self.base_dir, "images", "signup_back.png") 
        self.bg_pixmap = QtGui.QPixmap(bg_path)
        # Fallback if signup_back.png is missing, use login_back.png
        if self.bg_pixmap.isNull():
             bg_path = os.path.join(self.base_dir, "images", "login_back.png")
             self.bg_pixmap = QtGui.QPixmap(bg_path)
        
        # ==== Semi-transparent form container (Resizable and Centered) ====
        self.form_frame = QtWidgets.QFrame(self)
        
        self.form_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(88, 129, 87, 204);
                border-radius: 30px; 
                border: 2px solid rgba(0, 0, 0, 0);
                padding: 20px; 
            }
        """)

        # Center the form frame using main layout with stretches
        self.main_layout = QtWidgets.QVBoxLayout(self)
        
        # Horizontal container for central alignment and proportional width
        self.horizontal_container = QtWidgets.QHBoxLayout()
        self.horizontal_container.addStretch(1) # Left stretch
        # Changed stretch factor from 1 to 0.8 to make the form occupy even less horizontal space when maximized
        self.horizontal_container.addWidget(self.form_frame, 1) # Note: QLayout is smart enough to handle this as a ratio if the side stretches are integers
        self.horizontal_container.addStretch(1) # Right stretch
        
        # Apply the horizontal container to the main vertical layout (1:4:1 ratio for height)
        self.main_layout.addStretch(1)  # Top stretch
        self.main_layout.addLayout(self.horizontal_container, 4) # Central content
        self.main_layout.addStretch(1)  # Bottom stretch
        
        # ==== Layout inside form_frame ====
        self.form_layout = QtWidgets.QVBoxLayout(self.form_frame)
        self.form_layout.setContentsMargins(30, 20, 30, 20) # Reduced margins
        self.form_layout.setSpacing(15) # Reduced spacing to 15

        # ==== Title (Fixed Misspelling and Reduced Font Size) ====
        self.title = QtWidgets.QLabel("Signup")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setStyleSheet("""
            QLabel {
                font-family: 'Aladin';
                font-size: 50pt; 
                color: white;
                background: transparent;
            }
        """)
        self.title.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.title.setFocusPolicy(QtCore.Qt.NoFocus)
        self.form_layout.addWidget(self.title)

        # --- Required Fields ---
        
        # ==== 1. Owner Name (Full Name) ====
        self.owner_name = self._create_line_edit("Owner Name (Full Name)")
        # --- Centered and Added to Layout ---
        self.form_layout.addWidget(self.owner_name, alignment=QtCore.Qt.AlignHCenter)
        self.owner_name.returnPressed.connect(lambda: self.farm_name.setFocus())
        
        # ==== 2. Farm Name ====
        self.farm_name = self._create_line_edit("Farm Name")
        self.form_layout.addWidget(self.farm_name, alignment=QtCore.Qt.AlignHCenter)
        self.farm_name.returnPressed.connect(lambda: self.phone_number.setFocus())

        
        # ==== 3. Phone Number ====
        self.phone_number = self._create_line_edit("Phone Number")
        self.phone_number.setValidator(QtGui.QIntValidator())
        self.form_layout.addWidget(self.phone_number, alignment=QtCore.Qt.AlignHCenter)
        self.phone_number.returnPressed.connect(lambda: self.email.setFocus())

        # ==== 4. Email ====
        self.email = self._create_line_edit("Email")
        self.form_layout.addWidget(self.email, alignment=QtCore.Qt.AlignHCenter)
        self.email.returnPressed.connect(lambda: self.password.setFocus())

        # --- Login Credentials ---
        
        # ==== 5. Password (Required) ====
        self.password = self._create_line_edit("Password", echo_mode=QtWidgets.QLineEdit.Password)
        # Calls the function that adds the eye icon and returns the QAction
        self.password_action = self._setup_password_toggle(self.password) 
        self.form_layout.addWidget(self.password, alignment=QtCore.Qt.AlignHCenter)
        self.password.returnPressed.connect(lambda: self.confirm_password.setFocus())
        
        # ==== 6. Confirm Password (Required) ====
        self.confirm_password = self._create_line_edit("Confirm Password", echo_mode=QtWidgets.QLineEdit.Password)
        # Calls the function that adds the eye icon and returns the QAction
        self.confirm_password_action = self._setup_password_toggle(self.confirm_password)
        self.form_layout.addWidget(self.confirm_password, alignment=QtCore.Qt.AlignHCenter)
        self.confirm_password.returnPressed.connect(self.handle_signup)

        # --- NEW: Install Event Filters for Focus Control ---
        self.password.installEventFilter(self)
        self.confirm_password.installEventFilter(self)

        # Add stretch to push the button down, changed 0.5 to 1 (integer required)
        self.form_layout.addStretch(1) 


        # ==== Signup Button ====
        self.signup_button = QtWidgets.QPushButton("Signup")
        self.signup_button.setFixedWidth(150) # Further reduced button width
        self.signup_button.setStyleSheet("""
            QPushButton {
                /* Gradient Background */
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                            stop: 0 #B5C9A9, stop: 1 #A3B18A);
                color: #344E41;
                font-family: 'Amaranth';
                font-size: 13pt; 
                font-weight: bold;
                border: 2px solid #344E41;
                border-radius: 15px; 
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                            stop: 0 #C2D6B8, stop: 1 #B5C9A9); 
                border: 2px solid #588157; 
            }
            QPushButton:pressed {
                /* Pushed down effect */
                background-color: #7A997A; 
                padding-top: 12px;
                padding-bottom: 8px; 
            }
        """)
        self.form_layout.addWidget(self.signup_button, alignment=QtCore.Qt.AlignHCenter)

        # --- NEW: Login Redirect Link (at the bottom) ---
        self.form_layout.addSpacing(15) # Spacing between button and link
        
        self.login_redirect_label = QtWidgets.QLabel("Already have an account? <a href='#'>Log In</a>")
        self.login_redirect_label.setAlignment(QtCore.Qt.AlignCenter)
        self.login_redirect_label.setStyleSheet(self._get_link_style(link_name="login"))
        self.login_redirect_label.setOpenExternalLinks(True)
        self.login_redirect_label.linkActivated.connect(self._handle_login_redirect)
        self.form_layout.addWidget(self.login_redirect_label, alignment=QtCore.Qt.AlignHCenter)
        
        # Added a small stretch after the link to push the entire content block up slightly
        self.form_layout.addStretch(1)

        self.signup_button.clicked.connect(self.handle_signup)
        
    def _create_line_edit(self, placeholder_text, echo_mode=QtWidgets.QLineEdit.Normal):
        """Helper function to create a consistently styled QLineEdit."""
        line_edit = QtWidgets.QLineEdit()
        line_edit.setPlaceholderText(placeholder_text)
        # --- Max width added here to constrain width on large screens ---
        line_edit.setMaximumWidth(450)
        # --- Min width added here to prevent it from getting too small ---
        line_edit.setMinimumWidth(350)
        line_edit.setEchoMode(echo_mode)
        line_edit.setStyleSheet("""
            QLineEdit {
                background-color: #F0EFEF;
                border-radius: 8px; 
                padding: 8px 12px; 
                font-family: 'Amaranth';
                font-size: 9pt; 
            }
            QLineEdit QToolButton {
                /* Styling the button that holds the eye icon */
                border: none;
                background-color: transparent;
                /* Push the icon further to the right edge */
                padding-right: 8px; 
            }
            QLineEdit QToolButton:hover {
                background-color: rgba(0,0,0,0.1);
            }
        """)
        return line_edit
    
    # --- NEW HELPER METHOD FOR LINK STYLING ---
    def _get_link_style(self, link_name):
        """Helper for link styling."""
        color = "#FFFFFF"            
        hover_color = "#A3B18A"    
        
        return f"""
            QLabel {{
                background-color: transparent; 
                border: none;
                padding: 0;
                color: {color}; 
                font-family: 'Amaranth';
                font-size: 10pt;
            }}
            QLabel a {{
                color: {color}; 
                text-decoration: none; 
            }}
            QLabel a:hover {{
                text-decoration: underline; 
                color: {hover_color}; 
            }}
        """

    # NEW: Event Filter to handle focus events and show/hide the button
    def eventFilter(self, source, event):
        """Custom event filter to show/hide the password toggle button based on focus and content."""
        
        action_to_control = None
        
        if source == self.password:
            action_to_control = self.password_action
        elif source == self.confirm_password:
            action_to_control = self.confirm_password_action
            
        if action_to_control:
            if event.type() == QtCore.QEvent.FocusIn:
                # Show the button when the field gets focus
                action_to_control.setVisible(True)
            elif event.type() == QtCore.QEvent.FocusOut:
                # Hide the button when the field loses focus AND the field is empty
                if not source.text():
                    action_to_control.setVisible(False)

        return super().eventFilter(source, event)


    # _setup_password_toggle method (MODIFIED to set initial visibility and return the action)
    def _setup_password_toggle(self, line_edit):
        """Sets up the 'Show/Hide Password' QAction icon and returns the action."""
        
        show_password_action = QtWidgets.QAction(line_edit)
        
        # Define Custom Icons (MATCHING USER-PROVIDED FILENAMES)
        icon_path_show = os.path.join(self.base_dir, "images", "eye_view.png")
        icon_path_hide = os.path.join(self.base_dir, "images", "eye_hide.png")

        self.icon_pixmap_show = QtGui.QPixmap(icon_path_show)
        self.icon_pixmap_hide = QtGui.QPixmap(icon_path_hide)
        
        # Fallback if icons are missing
        icon_size = QtCore.QSize(20, 20) 
        # Using instance variables for icons so they can be accessed by _toggle_password_visibility
        if not hasattr(self, 'icon_show'):
            self.icon_show = QtGui.QIcon()
            self.icon_hide = QtGui.QIcon()
        
        if self.icon_pixmap_show.isNull() or self.icon_pixmap_hide.isNull():
             # Fallback: using text if image files are not found
             show_password_action.setText("•••") 
             show_password_action.setToolTip(f"Toggle Password Visibility (Could not load: {icon_path_show} or {icon_path_hide})")
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
        
        # --- CRITICAL: Set initial visibility to hidden as requested ---
        show_password_action.setVisible(False)
        
        # Return the action reference for external control (via eventFilter)
        return show_password_action
        
    # _toggle_password_visibility method (unchanged logic)
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

    # handle_signup method (FIXED: Removed animateClick())
    def handle_signup(self):
        """
        Handles the signup button click or Enter key press.
        NOTE: Removed self.signup_button.animateClick() to prevent infinite recursion.
        """
        
        owner_name_value = self.owner_name.text()
        farm_name_value = self.farm_name.text()
        phone_value = self.phone_number.text()
        email_value = self.email.text()
        password_value = self.password.text()
        confirm_password_value = self.confirm_password.text()

        print("\n--- Signup Attempt ---")
        print("Owner Name:", owner_name_value)
        print("Farm Name:", farm_name_value)
        print("Phone:", phone_value)
        print("Email:", email_value)
        print("Password:", password_value)
        print("Confirm Password:", confirm_password_value)
        
        if not all([owner_name_value, farm_name_value, password_value, confirm_password_value]):
             print("ERROR: Required fields (Owner Name, Farm Name, Password) must be filled.")
             return

        if password_value != confirm_password_value:
             print("ERROR: Passwords do not match.")
             return

        print("Signup successful (validation passed).")

    # --- NEW HANDLER METHOD FOR LOGIN REDIRECT ---
    def _handle_login_redirect(self):
        """Handles the click event for the 'Log In' link."""
        print("Redirecting to Login Page!")
        

    # Background auto-resize (unchanged logic)
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
    window = SignupWindow()
    # Changed from showMaximized() to show() to open smaller initially
    window.show() 
    sys.exit(app.exec_())
