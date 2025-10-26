from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os

class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.resize(2700, 1800)  # initial size

        # ==== Background image ====
        self.bg = QtWidgets.QLabel(self)
        self.bg.setScaledContents(True)  # auto scale
        self.bg.lower()  # behind everything

        # Load background image from same directory /images folder
        base_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(base_dir, "images", "login_back.png")
        self.bg_pixmap = QtGui.QPixmap(bg_path)

        # ==== Semi-transparent form container (fixed size, centered) ====
        self.form_frame = QtWidgets.QFrame(self)
        self.form_frame.setFixedSize(1200, 900)
        self.form_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(88, 129, 87, 204);
                border-radius: 40px;
                border: 3px solid rgba(0, 0, 0, 0);
                padding: 30px;
            }
        """)

        # Center the form frame using main layout with stretches
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addStretch()  # top stretch
        self.main_layout.addWidget(self.form_frame, alignment=QtCore.Qt.AlignHCenter)
        self.main_layout.addStretch()  # bottom stretch

        # ==== Layout inside form_frame ====
        self.form_layout = QtWidgets.QVBoxLayout(self.form_frame)
        self.form_layout.setContentsMargins(40, 30, 40, 30)
        self.form_layout.setSpacing(40)

        # ==== Title ====
        self.title = QtWidgets.QLabel("Login")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setStyleSheet("""
            QLabel {
                font-family: 'Aladin';
                font-size: 96pt;
                color: white;
                background: transparent;
            }
        """)
        self.title.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.title.setFocusPolicy(QtCore.Qt.NoFocus)
        self.form_layout.addWidget(self.title)

        # ==== Username ====
        self.username = QtWidgets.QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setFixedWidth(750) 
        self.username.setStyleSheet("""
            QLineEdit {
                background-color: #F0EFEF;
                border-radius: 15px;
                padding: 15px 25px;
                font-family: 'Amaranth';
                font-size: 12pt;
            }
        """)
        self.form_layout.addWidget(self.username, alignment=QtCore.Qt.AlignHCenter)
        self.username.returnPressed.connect(lambda: self.password.setFocus())

        # ==== Password ====
        self.password = QtWidgets.QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setFixedWidth(750) 
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
        self.form_layout.addWidget(self.password, alignment=QtCore.Qt.AlignHCenter)
        self.password.returnPressed.connect(self.handle_login)


        # ==== Login Button ====
        self.login_button = QtWidgets.QPushButton("Login")
        self.login_button.setFixedWidth(250) 
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #A3B18A;
                color: #344E41;
                font-family: 'Amaranth';
                font-size: 12pt;
                border: 2px solid #344E41;
                border-radius: 20px;
                padding: 20px;
            }
            QPushButton:hover {
                background-color: #8C9B7A;
            }
        """)
        self.form_layout.addWidget(self.login_button, alignment=QtCore.Qt.AlignHCenter)

        self.login_button.clicked.connect(self.handle_login)
        def handle_login(self):
            # optional: show button press animation
            self.login_button.animateClick()  # simulates button click (hover/press effect)
            # baki login logic ekhane
            print("Login pressed")


    # input recived
    def handle_login(self):
        username_value = self.username.text()
        password_value = self.password.text()
        print("Username:", username_value)
        print("Password:", password_value)

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
    window.showMaximized()  # start maximized with normal window controls
    sys.exit(app.exec_())
