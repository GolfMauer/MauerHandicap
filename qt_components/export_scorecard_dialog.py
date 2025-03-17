import matplotlib

from packages.helper import Helper
matplotlib.use('Qt5Agg')
from PyQt5 import QtWidgets, QtGui

from packages.helper import Helper

class ExportScorecardDialog(QtWidgets.QDialog):
    def __init__(self, help: Helper):
        super().__init__()
        self.help = help

        self.setWindowTitle("Scorecard Exportieren")
        layout = QtWidgets.QVBoxLayout()

        self.kurs_combo = QtWidgets.QComboBox()
        kurse = self.help.getAllCourseIDs()
        self.kurs_combo.addItems(kurse)
        layout.addWidget(QtWidgets.QLabel("Kurs:"))
        layout.addWidget(self.kurs_combo)

        self.whs_radio = QtWidgets.QRadioButton("WHS")
        self.ega_radio = QtWidgets.QRadioButton("EGA")
        self.whs_radio.setChecked(True)
        layout.addWidget(self.whs_radio)
        layout.addWidget(self.ega_radio)

        layout.addWidget(QtWidgets.QLabel("Kurs Rating überschreiben:"))
        self.kurs_rating_eingabe = QtWidgets.QLineEdit()
        self.kurs_rating_eingabe.setValidator(QtGui.QDoubleValidator())
        layout.addWidget(self.kurs_rating_eingabe)

        layout.addWidget(QtWidgets.QLabel("Slope Rating überschreiben:"))
        self.slope_rating_eingabe = QtWidgets.QLineEdit()
        self.slope_rating_eingabe.setValidator(QtGui.QIntValidator())
        layout.addWidget(self.slope_rating_eingabe)

        layout.addWidget(QtWidgets.QLabel("Stroke Index überschreiben:"))
        self.stroke_index_layout = QtWidgets.QGridLayout()
        self.stroke_index_eingabe = {}
        self.stroke_index_labels = {}
        for i in range(1, 19):
            eingabe = QtWidgets.QLineEdit()
            eingabe.setValidator(QtGui.QIntValidator())
            self.stroke_index_eingabe[i] = eingabe
            label_text = f"Stroke Index Loch {i}:"
            label = QtWidgets.QLabel(label_text)
            self.stroke_index_labels[i] = label

            row = (i - 1) % 9
            col = (i - 1) // 9
            self.stroke_index_layout.addWidget(label, row, col * 2)
            self.stroke_index_layout.addWidget(eingabe, row, col * 2 + 1)

            if i > 9:
                eingabe.hide()
                label.hide()

        layout.addLayout(self.stroke_index_layout)

        self.file_path_label = QtWidgets.QLabel("Kein Dateipfad und Name angegeben")
        layout.addWidget(self.file_path_label)

        self.file_path_button = QtWidgets.QPushButton("Dateipfad auswählen")
        self.file_path_button.clicked.connect(self.select_file_path)
        layout.addWidget(self.file_path_button)

        self.use_last_values_checkbox = QtWidgets.QCheckBox("Die letzten Werte verwenden")
        layout.addWidget(self.use_last_values_checkbox)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

        self.kurs_combo.currentIndexChanged.connect(self.update_stroke_index_eingabe)

    def update_stroke_index_eingabe(self):
        kurs_name = self.kurs_combo.currentText()
        kurs_info = self.help.getCourseByID(kurs_name)
        locher = len(kurs_info["par"])
        for i in range(1, 19):
            self.stroke_index_eingabe[i].setVisible(i <= locher)
            self.stroke_index_labels[i].setVisible(i <= locher)

    def select_file_path(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Dateipfad auswählen", "", "All Files (*);;Text Files (*.txt)", options=options)
        if file_path:
            self.file_path_label.setText(file_path)
            self.selected_file_path = file_path

    def get_export_daten(self):
        kurs = self.kurs_combo.currentText()

        kurs_info = self.help.getCourseByID(kurs)

        is_whs = self.whs_radio.isChecked()
        kurs_rating = self.kurs_rating_eingabe.text()
        kurs_rating = float(kurs_rating) if kurs_rating else None
        slope_rating = self.slope_rating_eingabe.text()
        slope_rating = int(slope_rating) if slope_rating else None
        stroke_indices = []

        locher = len(kurs_info["par"])

        for i in range(1, locher + 1):
            try:
                stroke_indices.append(int(self.stroke_index_eingabe[i].text()))
            except ValueError:
                stroke_indices.append(None)

        if all(index is None for index in stroke_indices):
            stroke_indices = None

        file_path = getattr(self, 'selected_file_path', None)
        use_last_values = self.use_last_values_checkbox.isChecked()
        return kurs, is_whs, file_path, kurs_rating, slope_rating, stroke_indices, use_last_values
