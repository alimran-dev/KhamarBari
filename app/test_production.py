#!/usr/bin/env python3
"""
Test script for the Production Page UI
Run this to test the production page independently
"""

import sys
from PyQt5 import QtWidgets, QtCore

# Add parent directory to path
sys.path.insert(0, '/home/alimran/Public/Projects/KhamarBari/app')

from production_page import ProductionPage

class TestWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Production Page Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create production page
        self.production_page = ProductionPage()
        self.setCentralWidget(self.production_page)

if __name__ == '__main__':
    # Enable High DPI
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    
    app = QtWidgets.QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec_())
