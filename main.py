#!/usr/bin/env python3
"""
Cross-platform test application using PyQt6.
This is a dummy application to test the build system.
"""

import sys
import platform
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class TestApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        """Configure the main window."""
        # Load config to get app name
        config_file = 'build_config.json'
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                app_name = config['base']['app_name']
                company = config['base']['company']['name']
        except:
            app_name = "Test App"
            company = "Test Company"
        
        self.setWindowTitle(f"{app_name} by {company}")
        self.setGeometry(100, 100, 600, 400)
        
        # Center the window
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
    def create_widgets(self):
        """Create the GUI elements."""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Cross-Platform Test Application")
        title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # System Information Group
        info_group = QGroupBox("System Information")
        info_layout = QVBoxLayout()
        
        # Platform info
        platform_layout = QHBoxLayout()
        platform_label = QLabel("Platform:")
        platform_value = QLabel(platform.platform())
        platform_layout.addWidget(platform_label)
        platform_layout.addWidget(platform_value)
        platform_layout.addStretch()
        info_layout.addLayout(platform_layout)
        
        # Python Version
        python_layout = QHBoxLayout()
        python_label = QLabel("Python Version:")
        python_value = QLabel(sys.version.split()[0])
        python_layout.addWidget(python_label)
        python_layout.addWidget(python_value)
        python_layout.addStretch()
        info_layout.addLayout(python_layout)
        
        # Architecture
        arch_layout = QHBoxLayout()
        arch_label = QLabel("Architecture:")
        arch_value = QLabel(platform.architecture()[0])
        arch_layout.addWidget(arch_label)
        arch_layout.addWidget(arch_value)
        arch_layout.addStretch()
        info_layout.addLayout(arch_layout)
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)
        
        # Interactive Test Group
        interact_group = QGroupBox("Interactive Test")
        interact_layout = QVBoxLayout()
        
        # Counter
        counter_layout = QHBoxLayout()
        self.counter_label = QLabel("Counter: 0")
        counter_button = QPushButton("Increment")
        counter_button.clicked.connect(self.increment_counter)
        counter_layout.addWidget(self.counter_label)
        counter_layout.addWidget(counter_button)
        counter_layout.addStretch()
        interact_layout.addLayout(counter_layout)
        
        # Time display
        self.time_label = QLabel()
        self.update_time()
        interact_layout.addWidget(self.time_label)
        
        # Create timer for updating time
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second
        
        interact_group.setLayout(interact_layout)
        main_layout.addWidget(interact_group)
        
        # Status bar
        status_bar = QFrame()
        status_layout = QHBoxLayout(status_bar)
        status_label = QLabel("✓ Application running normally")
        status_label.setStyleSheet("color: green")
        status_layout.addWidget(status_label)
        status_layout.addStretch()
        main_layout.addWidget(status_bar)
        
        # Add stretch to push everything up
        main_layout.addStretch()
    
    def increment_counter(self):
        """Increment the counter and update display."""
        self.counter += 1
        self.counter_label.setText(f"Counter: {self.counter}")
    
    def update_time(self):
        """Update the time display."""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(f"Current Time: {current_time}")


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    window = TestApp()
    window.show()
    sys.exit(app.exec())
