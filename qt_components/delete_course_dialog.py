import matplotlib

from packages.helper import Helper
matplotlib.use('Qt5Agg')
from PyQt5 import QtWidgets

from packages.helper import Helper

class DeleteCourseDialog(QtWidgets.QDialog):
    def __init__(self, kurse, help: Helper):
        super().__init__()
        self.help = help
        
        self.setWindowTitle("Kurs Löschen")
        layout = QtWidgets.QVBoxLayout()
        self.setFixedSize(400, 450)
        
        self.kurs_combo = QtWidgets.QComboBox()
        self.kurs_combo.addItems(kurse)
        layout.addWidget(self.kurs_combo)
        
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.delete_course)
        button_box.rejected.connect(self.close_popup)
        layout.addWidget(button_box)
        
        self.setLayout(layout)

    def delete_course(self):
        current_item = self.kurs_combo.currentText()
        self.help.delete_course_item(current_item)
        self.close()
        
    def close_popup(self):
        self.close()