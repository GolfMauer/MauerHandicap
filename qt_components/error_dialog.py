# error_dialog.py
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton

class ErrorDialog(QDialog):
    def __init__(self, error_message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Error")

        # Layout and widgets
        layout = QVBoxLayout()
        self.label = QLabel(error_message)
        self.close_button = QPushButton("Close")

        # Connect button
        self.close_button.clicked.connect(self.close)

        # Add widgets to layout
        layout.addWidget(self.label)
        layout.addWidget(self.close_button)
        self.setLayout(layout)

        # Set dialog size
        self.resize(300, 150)
