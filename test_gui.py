#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quick test script to verify the enhanced GUI components work correctly
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt

# Test basic GUI components
def test_gui():
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("PandaDock GUI Test")
    window.setGeometry(100, 100, 400, 300)
    
    # Test logo loading
    mainpath = os.path.dirname(__file__)
    logo_path = os.path.join(mainpath, "Images", "logo_new.png")
    
    print(f"Logo path: {logo_path}")
    print(f"Logo exists: {os.path.exists(logo_path)}")
    
    # Create central widget
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Test logo display
    if os.path.exists(logo_path):
        logo_label = QLabel()
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
            print("✓ Logo loaded successfully")
        else:
            print("✗ Logo pixmap is null")
    else:
        print("✗ Logo file not found")
    
    # Add test label
    test_label = QLabel("🐼 PandaDock GUI Test - Enhanced Version")
    test_label.setAlignment(Qt.AlignCenter)
    test_label.setStyleSheet("""
        QLabel {
            font-size: 16px;
            font-weight: bold;
            color: #2C3E50;
            padding: 20px;
        }
    """)
    layout.addWidget(test_label)
    
    window.setCentralWidget(central_widget)
    window.show()
    
    print("✓ GUI test window displayed")
    print("Close the window to exit test")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_gui())