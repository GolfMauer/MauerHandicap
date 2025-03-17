import matplotlib

from packages.helper import Helper
matplotlib.use('Qt5Agg')
from PyQt5 import QtWidgets


class HeaderButton(QtWidgets.QWidget):
    def __init__(self, help: Helper, parent=None):
        super().__init__(parent)
        self.neues_spiel_button = QtWidgets.QPushButton("Neues Spiel")
        self.neuer_kurs_button = QtWidgets.QPushButton("Neuer Kurs")
        self.kurs_löschen_button = QtWidgets.QPushButton("Kurs Löschen")
        self.export_scorecard_button = QtWidgets.QPushButton("Scorecard Exportieren")
        
        layout = QtWidgets.QHBoxLayout()
        
        layout.addWidget(self.neues_spiel_button)
        layout.addWidget(self.neuer_kurs_button)
        layout.addWidget(self.kurs_löschen_button)
        layout.addWidget(self.export_scorecard_button)

        self.neues_spiel_button.clicked.connect(self.oeffne_neues_spiel_dialog)
        self.neuer_kurs_button.clicked.connect(self.neuer_kurs_hinzugefuegt)
        self.kurs_löschen_button.clicked.connect(self.kurs_loeschen_dialog)
        self.export_scorecard_button.clicked.connect(self.oeffne_export_scorecard_dialog) 

        self.setLayout(layout)
