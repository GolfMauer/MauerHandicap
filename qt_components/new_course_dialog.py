import matplotlib

from packages.helper import Helper
matplotlib.use('Qt5Agg')
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator

from packages.helper import Helper

class NewCourseDialog(QtWidgets.QDialog):
    def __init__(self, help: Helper):
        super().__init__()
        self.help = help

        self.setWindowTitle("Neuer Kurs")

        layout = QtWidgets.QVBoxLayout()
        self.setFixedSize(600, 800)  # Set fixed size for the dialog window

        self.setWhatsThis("Dieser Dialog ermöglicht es dir, ein neuen kurs einzutragen. "
                          "Wähle den Kurs, das kurs Rating, das Slope Rating, die Anzahl der Löcher und gib die Par Schlagzahlen ein.")
        self.kurs_name_eingabe = QtWidgets.QLineEdit()
        layout.addWidget(QtWidgets.QLabel("Kursname:"))
        layout.addWidget(self.kurs_name_eingabe)

        self.kurs_rating_eingabe = QtWidgets.QLineEdit()
        layout.addWidget(QtWidgets.QLabel("Kurs Rating:"))
        layout.addWidget(self.kurs_rating_eingabe)

        self.slope_rating_eingabe = QtWidgets.QLineEdit()
        layout.addWidget(QtWidgets.QLabel("Slope Rating:"))
        layout.addWidget(self.slope_rating_eingabe)

        self.neun_loch_radio = QtWidgets.QRadioButton("9 Löcher")
        self.achtzehn_loch_radio = QtWidgets.QRadioButton("18 Löcher")
        self.neun_loch_radio.setChecked(True)
        layout.addWidget(QtWidgets.QLabel("Anzahl Löcher:"))
        layout.addWidget(self.neun_loch_radio)
        layout.addWidget(self.achtzehn_loch_radio)

        schlagzahl_layout = QtWidgets.QGridLayout()

        self.par_eingabe = {}
        self.par_labels = {}
        for i in range(1, 19):
            eingabe = QtWidgets.QLineEdit()
            eingabe.setValidator(QIntValidator())
            self.par_eingabe[i] = eingabe
            label_text = f"Par Loch {i}:"
            label = QtWidgets.QLabel(label_text)
            self.par_labels[i] = label

            row = (i - 1) % 9
            col = (i - 1) // 9
            schlagzahl_layout.addWidget(label, row, col * 2)
            schlagzahl_layout.addWidget(eingabe, row, col * 2 + 1)

            if i > 9:
                eingabe.hide()
                label.hide()

        layout.addLayout(schlagzahl_layout)

        stroke_index_layout = QtWidgets.QGridLayout()

        self.stroke_index_eingabe = {}
        self.stroke_index_labels = {}
        for i in range(1, 19):
            eingabe = QtWidgets.QLineEdit()
            eingabe.setValidator(QIntValidator())
            self.stroke_index_eingabe[i] = eingabe
            label_text = f"Stroke Index Loch {i}:"
            label = QtWidgets.QLabel(label_text)
            self.stroke_index_labels[i] = label

            row = (i - 1) % 9  # Reset row for stroke index inputs
            col = (i - 1) // 9
            stroke_index_layout.addWidget(label, row, col * 2)
            stroke_index_layout.addWidget(eingabe, row, col * 2 + 1)

            if i > 9:
                eingabe.hide()
                label.hide()

        layout.addLayout(stroke_index_layout)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

        self.neun_loch_radio.toggled.connect(self.update_par_eingabe)
        self.achtzehn_loch_radio.toggled.connect(self.update_par_eingabe)

    def update_par_eingabe(self):
        locher = 9 if self.neun_loch_radio.isChecked() else 18
        for i in range(1, 19):
            self.par_eingabe[i].setVisible(i <= locher)
            self.par_labels[i].setVisible(i <= locher)
            self.stroke_index_eingabe[i].setVisible(i <= locher)
            self.stroke_index_labels[i].setVisible(i <= locher)

    def get_kurs_daten(self):
        kurs_name = self.kurs_name_eingabe.text()
        kurs_rating = self.kurs_rating_eingabe.text()
        slope_rating = self.slope_rating_eingabe.text()
        locher = 9 if self.neun_loch_radio.isChecked() else 18
        pars = []
        stroke_indices = []
        for i in range(1, locher + 1):
            try:
                pars.append(int(self.par_eingabe[i].text()))
            except ValueError:
                pars.append(0)
            try:
                stroke_indices.append(int(self.stroke_index_eingabe[i].text()))
            except ValueError:
                stroke_indices.append(0)

        self.help.addCourse(kurs_name, int(kurs_rating), int(slope_rating), pars, stroke_indices)