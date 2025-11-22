from PyQt5 import QtWidgets, QtCore
import sys
from login import LoginPage
from signup import SignupPage
from dashboard import DashboardPage

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # ===== Window Title =====
        self.setWindowTitle("KhamarBari")  # top bar name

        # ===== Window flags: keep buttons (min/max/close) =====
        self.setWindowFlags(QtCore.Qt.Window |
                            QtCore.Qt.WindowMinimizeButtonHint |
                            QtCore.Qt.WindowMaximizeButtonHint |
                            QtCore.Qt.WindowCloseButtonHint)

        # ===== Start maximized (full screen with window controls) =====
        self.showMaximized()

        # ===== Stacked widget =====
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        # ===== Pages =====
        self.login_page = LoginPage()
        self.signup_page = SignupPage()
        self.dashboard_page = DashboardPage()

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.signup_page)
        self.stack.addWidget(self.dashboard_page)

        # ===== Connect signals =====
        self.login_page.signup_requested.connect(lambda: self.show_page(self.signup_page))
        self.signup_page.login_requested.connect(lambda: self.show_page(self.login_page))
        self.login_page.login_successful.connect(self.on_login_success)

        # ===== Fullscreen toggle track =====
        self._is_fullscreen = False

        # ===== Show login page initially =====
        self.show_page(self.login_page)

    # ===== Page switch without changing window state =====
    def show_page(self, page_widget):
        self.stack.setCurrentWidget(page_widget)

    # ===== After login, show dashboard =====
    def on_login_success(self, user_info):
        self.dashboard_page.load_user_data(user_info)
        self.show_page(self.dashboard_page)

    # ===== Optional fullscreen toggle =====
    def toggle_fullscreen(self):
        if not self._is_fullscreen:
            self.showFullScreen()
            self._is_fullscreen = True
        else:
            self.showNormal()
            self._is_fullscreen = False

    # ===== Optional: F11 toggle =====
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F11:
            self.toggle_fullscreen()
        super().keyPressEvent(event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
