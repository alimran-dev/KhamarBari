from PyQt5 import QtWidgets, QtCore, QtGui
import requests
import os
from datetime import datetime


class SettingsPage(QtWidgets.QWidget):
    """Settings page for profile management."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_data = {}
        self.profile_photo_path = None
        self.dashboard_parent = parent
        self.init_ui()
    
    def init_ui(self):
        """Initialize the settings page UI."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QtWidgets.QLabel("Settings")
        title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #344E41; padding: 10px;")
        layout.addWidget(title)
        
        # Scroll area for form
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        # Form container
        form_widget = QtWidgets.QWidget()
        form_layout = QtWidgets.QVBoxLayout(form_widget)
        form_layout.setSpacing(20)
        
        # Profile Photo Section
        self.create_photo_section(form_layout)
        
        # Profile Information Form
        self.create_profile_form(form_layout)
        
        # Save Button
        save_btn = QtWidgets.QPushButton("Save Changes")
        save_btn.setFixedHeight(50)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #588157;
                color: white;
                border-radius: 8px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #344E41;
            }
        """)
        save_btn.clicked.connect(self.save_changes)
        form_layout.addWidget(save_btn)
        
        form_layout.addStretch()
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
    
    def create_photo_section(self, layout):
        """Create the profile photo management section."""
        photo_container = QtWidgets.QWidget()
        photo_container.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA;
                border: 2px solid #588157;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        photo_layout = QtWidgets.QVBoxLayout(photo_container)
        
        title = QtWidgets.QLabel("Profile Photo")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #344E41; background: transparent; border: none; padding: 0;")
        photo_layout.addWidget(title)
        
        # Photo display and buttons
        photo_row = QtWidgets.QHBoxLayout()
        photo_row.setSpacing(30)
        
        # Photo display with ring effect (matching sidebar)
        photo_frame = QtWidgets.QWidget()
        photo_frame.setFixedSize(160, 160)
        photo_frame.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #588157, stop:0.5 #A3B18A, stop:1 #588157);
                border-radius: 80px;
                border: none;
                padding: 0;
            }
        """)
        
        photo_frame_layout = QtWidgets.QVBoxLayout(photo_frame)
        photo_frame_layout.setContentsMargins(5, 5, 5, 5)
        
        self.photo_label = QtWidgets.QLabel()
        self.photo_label.setFixedSize(150, 150)
        self.photo_label.setStyleSheet("""
            QLabel {
                background-color: #D3D3D3;
                border-radius: 75px;
                border: none;
            }
        """)
        self.photo_label.setAlignment(QtCore.Qt.AlignCenter)
        self.set_default_photo()
        photo_frame_layout.addWidget(self.photo_label)
        
        photo_row.addWidget(photo_frame)
        
        # Buttons
        button_layout = QtWidgets.QVBoxLayout()
        button_layout.setSpacing(15)
        
        upload_btn = QtWidgets.QPushButton("Upload Photo")
        upload_btn.setFixedSize(180, 45)
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #588157;
                color: white;
                border-radius: 5px;
                font-size: 11pt;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #344E41;
            }
        """)
        upload_btn.clicked.connect(self.upload_photo)
        button_layout.addWidget(upload_btn)
        
        remove_btn = QtWidgets.QPushButton("Remove Photo")
        remove_btn.setFixedSize(180, 45)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 5px;
                font-size: 11pt;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        remove_btn.clicked.connect(self.remove_photo)
        button_layout.addWidget(remove_btn)
        
        button_layout.addStretch()
        photo_row.addLayout(button_layout)
        photo_row.addStretch()
        
        photo_layout.addLayout(photo_row)
        layout.addWidget(photo_container)
    
    def create_profile_form(self, layout):
        """Create the editable profile form."""
        form_container = QtWidgets.QWidget()
        form_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #A3B18A;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        form_layout = QtWidgets.QFormLayout(form_container)
        form_layout.setSpacing(20)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        
        # Form title
        form_title = QtWidgets.QLabel("Profile Information")
        form_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #344E41; background: transparent; border: none; padding: 0;")
        form_layout.addRow(form_title)
        
        # Owner Name
        self.owner_name_input = QtWidgets.QLineEdit()
        self.owner_name_input.setPlaceholderText("Enter your full name")
        self.style_input(self.owner_name_input)
        label = QtWidgets.QLabel("Owner Name:")
        label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #344E41; background: transparent; border: none;")
        form_layout.addRow(label, self.owner_name_input)
        
        # Farm Name
        self.farm_name_input = QtWidgets.QLineEdit()
        self.farm_name_input.setPlaceholderText("Enter farm name")
        self.style_input(self.farm_name_input)
        label = QtWidgets.QLabel("Farm Name:")
        label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #344E41; background: transparent; border: none;")
        form_layout.addRow(label, self.farm_name_input)
        
        # Phone Number
        self.phone_input = QtWidgets.QLineEdit()
        self.phone_input.setPlaceholderText("Enter phone number")
        self.style_input(self.phone_input)
        label = QtWidgets.QLabel("Phone Number:")
        label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #344E41; background: transparent; border: none;")
        form_layout.addRow(label, self.phone_input)
        
        # Email (Read-only)
        self.email_display = QtWidgets.QLineEdit()
        self.email_display.setReadOnly(True)
        self.email_display.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #EBEAE3;
                border-radius: 5px;
                font-size: 11pt;
                background-color: #F8F9FA;
                color: #6c757d;
            }
        """)
        label = QtWidgets.QLabel("Email:")
        label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #344E41; background: transparent; border: none;")
        email_container = QtWidgets.QHBoxLayout()
        email_container.addWidget(self.email_display)
        lock_icon = QtWidgets.QLabel("🔒")
        lock_icon.setStyleSheet("font-size: 16pt; background: transparent; border: none;")
        email_container.addWidget(lock_icon)
        form_layout.addRow(label, email_container)
        
        layout.addWidget(form_container)
    
    def style_input(self, widget):
        """Apply styling to input widgets."""
        widget.setStyleSheet("""
            QLineEdit, QTextEdit {
                padding: 12px;
                border: 2px solid #A3B18A;
                border-radius: 5px;
                font-size: 11pt;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #588157;
            }
        """)
        widget.setMinimumHeight(45)
    
    def set_default_photo(self):
        """Set default profile photo icon."""
        pixmap = QtGui.QPixmap(150, 150)
        pixmap.fill(QtCore.Qt.transparent)
        
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw circle background
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#D3D3D3")))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(0, 0, 150, 150)
        
        # Draw person icon
        painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 3))
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#FFFFFF")))
        
        # Head
        painter.drawEllipse(55, 35, 40, 40)
        
        # Body
        path = QtGui.QPainterPath()
        path.moveTo(75, 75)
        path.arcTo(40, 75, 70, 70, 0, 180)
        painter.drawPath(path)
        
        painter.end()
        
        self.photo_label.setPixmap(pixmap)
        self.photo_label.setScaledContents(False)
    
    def upload_photo(self):
        """Handle photo upload."""
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Profile Photo",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            try:
                # Upload to backend
                email = self.user_data.get('email', '')
                if not email:
                    QtWidgets.QMessageBox.critical(self, "Error", "No email found. Please log in again.")
                    return
                
                with open(file_path, 'rb') as f:
                    files = {'photo': (os.path.basename(file_path), f, 'image/jpeg')}
                    response = requests.post(
                        f"http://localhost:8000/owner/{email}/upload-photo",
                        files=files
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    photo_url = result.get('photo_url')
                    
                    # Update local data
                    self.user_data['photo_url'] = photo_url
                    self.profile_photo_path = file_path
                    
                    # Display photo locally
                    self.display_photo(file_path)
                    
                    # Update sidebar profile picture
                    if self.dashboard_parent and hasattr(self.dashboard_parent, 'update_profile_pic'):
                        self.dashboard_parent.update_profile_pic(file_path)
                    
                    QtWidgets.QMessageBox.information(self, "Success", "Profile photo uploaded successfully!")
            
            except requests.exceptions.RequestException as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to upload photo: {str(e)}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def display_photo(self, file_path):
        """Display the selected photo."""
        pixmap = QtGui.QPixmap(file_path)
        if not pixmap.isNull():
            # Scale and crop to circular
            scaled = pixmap.scaled(
                150, 150,
                QtCore.Qt.KeepAspectRatioByExpanding,
                QtCore.Qt.SmoothTransformation
            )
            
            # Create circular mask
            target = QtGui.QPixmap(150, 150)
            target.fill(QtCore.Qt.transparent)
            
            painter = QtGui.QPainter(target)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            
            path = QtGui.QPainterPath()
            path.addEllipse(0, 0, 150, 150)
            painter.setClipPath(path)
            
            # Center the image
            x = (150 - scaled.width()) // 2
            y = (150 - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            painter.end()
            
            self.photo_label.setPixmap(target)
    
    def remove_photo(self):
        """Remove the profile photo."""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Remove",
            "Are you sure you want to remove your profile photo?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                # Delete from backend
                email = self.user_data.get('email', '')
                if not email:
                    QtWidgets.QMessageBox.critical(self, "Error", "No email found. Please log in again.")
                    return
                
                response = requests.delete(f"http://localhost:8000/owner/{email}/photo")
                response.raise_for_status()
                
                # Update local data
                self.user_data['photo_url'] = None
                self.profile_photo_path = None
                self.set_default_photo()
                
                # Update sidebar to default profile picture
                if self.dashboard_parent and hasattr(self.dashboard_parent, 'set_default_profile_pic'):
                    self.dashboard_parent.set_default_profile_pic()
                
                QtWidgets.QMessageBox.information(self, "Success", "Profile photo removed!")
            
            except requests.exceptions.RequestException as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to remove photo: {str(e)}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def load_user_data(self, user_data):
        """Load user data into the form."""
        self.user_data = user_data.get('data', {})
        
        self.owner_name_input.setText(self.user_data.get('owner_name', ''))
        self.farm_name_input.setText(self.user_data.get('farm_name', ''))
        self.phone_input.setText(self.user_data.get('phone_number', ''))
        self.email_display.setText(self.user_data.get('email', ''))
        
        # Load profile photo if exists
        photo_url = self.user_data.get('photo_url')
        if photo_url:
            try:
                # Convert URL to local file path
                file_path = photo_url.lstrip('/')
                # Construct full path relative to backend directory
                backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
                full_path = os.path.join(backend_dir, file_path)
                
                if os.path.exists(full_path):
                    self.profile_photo_path = full_path
                    self.display_photo(full_path)
                    
                    # Update sidebar profile picture
                    if self.dashboard_parent and hasattr(self.dashboard_parent, 'update_profile_pic'):
                        self.dashboard_parent.update_profile_pic(full_path)
            except Exception as e:
                print(f"Failed to load profile photo: {e}")
    
    def save_changes(self):
        """Save the profile changes."""
        try:
            # Validate inputs
            owner_name = self.owner_name_input.text().strip()
            farm_name = self.farm_name_input.text().strip()
            phone_number = self.phone_input.text().strip()
            
            if not owner_name:
                QtWidgets.QMessageBox.warning(self, "Validation Error", "Owner name is required!")
                return
            
            if not farm_name:
                QtWidgets.QMessageBox.warning(self, "Validation Error", "Farm name is required!")
                return
            
            if not phone_number:
                QtWidgets.QMessageBox.warning(self, "Validation Error", "Phone number is required!")
                return
            
            # Prepare update payload
            payload = {
                "owner_name": owner_name,
                "farm_name": farm_name,
                "phone_number": phone_number
            }
            
            # TODO: Handle photo upload to server
            if self.profile_photo_path:
                # Upload photo and get URL
                pass
            
            # Get email from current user data
            email = self.user_data.get('email', '')
            
            if not email:
                QtWidgets.QMessageBox.critical(self, "Error", "No email found. Please log in again.")
                return
            
            # Update profile via API
            response = requests.put(
                f"http://localhost:8000/owner/{email}",
                json=payload
            )
            
            if response.status_code == 404:
                QtWidgets.QMessageBox.critical(
                    self, 
                    "Error", 
                    f"User not found with email: {email}\n\nPlease verify:\n1. You are logged in\n2. The email '{email}' exists in the database\n3. Backend server is running"
                )
                return
            elif response.status_code == 400:
                error_detail = response.json().get('detail', 'Invalid request')
                QtWidgets.QMessageBox.critical(self, "Error", f"Validation Error: {error_detail}")
                return
            
            response.raise_for_status()
            
            QtWidgets.QMessageBox.information(self, "Success", "Profile updated successfully!")
            
            # Refresh user data
            self.user_data.update(payload)
            
        except requests.exceptions.ConnectionError:
            QtWidgets.QMessageBox.critical(
                self, 
                "Connection Error", 
                "Cannot connect to the server.\n\nPlease ensure:\n1. Backend server is running\n2. Server is accessible at http://localhost:8000"
            )
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "404" in error_msg:
                QtWidgets.QMessageBox.critical(
                    self,
                    "User Not Found",
                    f"The user account could not be found.\n\nEmail: {email}\n\nPlease contact support or try logging in again."
                )
            else:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to update profile: {error_msg}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")
