import matplotlib

from packages.helper import Helper
matplotlib.use('Qt5Agg')
from PyQt5 import QtWidgets
from qt_components.new_game_dialog import NewGameDialog
from qt_components.new_course_dialog import NewCourseDialog


class HeaderButton(QtWidgets.QWidget):
    def __init__(self, help: Helper, parent=None):
        super().__init__(parent)
        self.help = help

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

    def oeffne_neues_spiel_dialog(self):
        kurse = self.help.getAllCourseIDs()
        dialog = NewGameDialog(kurse, self.help)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            dialog.get_spiel_daten()
            self.parent().update()

    def neuer_kurs_hinzugefuegt(self):
        dialog = NewCourseDialog(self.help)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            dialog.get_kurs_daten()
            self.parent().update()

    def kurs_loeschen_dialog(self):
        kurse = self.help.getAllCourseIDs()
        dialog = KursLoeschenDialog(kurse)
        dialog.exec_()
        
    def oeffne_export_scorecard_dialog(self):
        dialog = ExportScorecardDialog()
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            kurs, is_whs, file_path, kurs_rating, slope_rating, stroke_indices, use_last_values = dialog.get_export_daten()
            self.help.export_scorecard(kurs, is_whs, file_path, kurs_rating, slope_rating, stroke_indices, use_last_values)
