import matplotlib

from packages.helper import Helper
matplotlib.use('Qt5Agg')
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator

class NewGameDialog(QtWidgets.QDialog):
    def __init__(self, kurse, help: Helper):
        super().__init__()
        self.help = help
        self.setWindowTitle("Neues Spiel")
        layout = QtWidgets.QVBoxLayout()
        self.setFixedSize(400, 450)  # Set fixed size for the dialog window
        self.setWhatsThis("Dieser Dialog ermöglicht es dir, ein neues Spiel zu starten. "
                          "Wähle den Kurs und gib die Schlagzahlen ein.")

        self.kurs_combo = QtWidgets.QComboBox()
        self.kurs_combo.addItems(kurse)
        layout.addWidget(QtWidgets.QLabel("Kurs:"))
        layout.addWidget(self.kurs_combo)

        # Neues Layout für die Schlagzahl-Eingabe in zwei Spalten
        schlagzahl_layout = QtWidgets.QGridLayout()

        self.schlagzahl_eingabe = {}
        self.schlagzahl_labels = {}
        for i in range(1, 19):
            eingabe = QtWidgets.QLineEdit()
            eingabe.setValidator(QIntValidator())
            self.schlagzahl_eingabe[i] = eingabe
            label_text = f"Schlagzahl Loch {i}:"
            label = QtWidgets.QLabel(label_text)
            self.schlagzahl_labels[i] = label

            # Anordnung in zwei Spalten
            row = (i - 1) % 9  # Zeile 0-8
            col = (i - 1) // 9  # Spalte 0 oder 1
            schlagzahl_layout.addWidget(label, row, col * 2)  # Label in Spalte 0 oder 2
            schlagzahl_layout.addWidget(eingabe, row, col * 2 + 1)  # Eingabe in Spalte 1 oder 3

            if i > 9:
                eingabe.hide()
                label.hide()

        layout.addLayout(schlagzahl_layout)  # Hinzufügen des GridLayout zum Hauptlayout

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
  
        self.setLayout(layout)

        self.kurs_combo.currentIndexChanged.connect(self.update_schlagzahl_eingabe)


    def get_spiel_daten(self):
        kurs = self.kurs_combo.currentText()
        kurs_info = self.help.getCourseByID(kurs)
        locher = len(kurs_info["par"])
        schlagzahlen = []
        for i in range(1, locher + 1):
            try:
                schlagzahlen.append(int(self.schlagzahl_eingabe[i].text()))
            except ValueError:
                schlagzahlen.append(0)

        loch_bool = (locher == 9)
        
        self.help.addGame(kurs, schlagzahlen, loch_bool, 0, 0)


    def update_schlagzahl_eingabe(self):
        kurs_name = self.kurs_combo.currentText()
        kurs_info = self.help.getCourseByID(kurs_name)
        locher = len(kurs_info["par"])
        for i in range(1, 19):
            self.schlagzahl_eingabe[i].setVisible(i <= locher)
            self.schlagzahl_labels[i].setVisible(i <= locher)
