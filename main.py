from datetime import datetime
import sys
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtWidgets, QtGui, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from qt_components.debug_button import DebugButtons

from tinydb import TinyDB
from packages.helper  import Helper
import os

class NeuesSpielDialog(QtWidgets.QDialog):
    def __init__(self, kurse):
        super().__init__()
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
            eingabe.setValidator(QtGui.QIntValidator())
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

    def update_schlagzahl_eingabe(self):
        kurs_name = self.kurs_combo.currentText()
        kurs_info = help.getCourseByID(kurs_name)
        locher = len(kurs_info["par"])
        for i in range(1, 19):
            self.schlagzahl_eingabe[i].setVisible(i <= locher)
            self.schlagzahl_labels[i].setVisible(i <= locher)

    def get_spiel_daten(self):
        kurs = self.kurs_combo.currentText()
        kurs_info = help.getCourseByID(kurs)
        locher = len(kurs_info["par"])
        schlagzahlen = []
        for i in range(1, locher + 1):
            try:
                schlagzahlen.append(int(self.schlagzahl_eingabe[i].text()))
            except ValueError:
                schlagzahlen.append(0)

        loch_bool = (locher == 9)
        
        help.addGame(kurs, schlagzahlen, loch_bool, 0, 0)
        self.neun_loch_radio.toggled.connect(self.update_schlagzahl_eingabe)
        self.achtzehn_loch_radio.toggled.connect(self.update_schlagzahl_eingabe)
class NeuerKursDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
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
            eingabe.setValidator(QtGui.QIntValidator())
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
            eingabe.setValidator(QtGui.QIntValidator())
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

        help.addCourse(kurs_name, int(kurs_rating), int(slope_rating), pars, stroke_indices)

class KursLoeschenDialog(QtWidgets.QDialog):
    def __init__(self, kurse):
        super().__init__()
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
        help.delete_course_item(current_item)
        self.close()
        
    def close_popup(self):
        self.close()

class ExportScorecardDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scorecard Exportieren")
        layout = QtWidgets.QVBoxLayout()

        self.kurs_combo = QtWidgets.QComboBox()
        kurse = help.getAllCourseIDs()
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

        self.file_path_label = QtWidgets.QLabel("Kein Dateipfad ausgewählt")
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
        kurs_info = help.getCourseByID(kurs_name)
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

        kurs_info = help.getCourseByID(kurs)

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
            

class HandicapUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Golf Handicap Rechner")

        # Dark Mode Farbpalette
        self.dark_palette = QtGui.QPalette()
        self.dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        self.dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        self.dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
        self.dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        self.dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        self.dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        self.dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        self.dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        self.dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        self.dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        self.dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        self.dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
        self.dark_palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
        self.setPalette(self.dark_palette)
        app.setStyle('Fusion')  # Stil anpassen

        layout = QtWidgets.QVBoxLayout()

        button_layout = QtWidgets.QHBoxLayout()
        self.neues_spiel_button = QtWidgets.QPushButton("Neues Spiel")
        self.neuer_kurs_button = QtWidgets.QPushButton("Neuer Kurs")
        self.kurs_löschen_button = QtWidgets.QPushButton("Kurs Löschen")
        self.export_scorecard_button = QtWidgets.QPushButton("Scorecard Exportieren")
        button_layout.addWidget(self.neues_spiel_button)
        button_layout.addWidget(self.neuer_kurs_button)
        button_layout.addWidget(self.kurs_löschen_button)
        button_layout.addWidget(self.export_scorecard_button) 
        layout.addLayout(button_layout)

        self.ega_handicap_label = QtWidgets.QLabel("Aktuelles EGA Handicap: N/A")
        self.ega_handicap_label.setStyleSheet("font-size: 20px; color: white;")
        layout.addWidget(self.ega_handicap_label)

        self.whs_handicap_label = QtWidgets.QLabel("Aktuelles WHS Handicap: N/A")
        self.whs_handicap_label.setStyleSheet("font-size: 20px; color: white;")
        layout.addWidget(self.whs_handicap_label)

        self.figure = Figure(facecolor='#353535')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.spiele_tabelle = QtWidgets.QTableWidget()
        self.spiele_tabelle.setColumnCount(3)
        self.spiele_tabelle.setHorizontalHeaderLabels(["Datum", "Kurs", "Schläge"])
        layout.addWidget(self.spiele_tabelle)


        self.debug_buttons = DebugButtons(help, self)
        layout.addWidget(self.debug_buttons)

        self.setLayout(layout)

        self.neues_spiel_button.clicked.connect(self.oeffne_neues_spiel_dialog)
        self.neuer_kurs_button.clicked.connect(self.neuer_kurs_hinzugefuegt)
        self.kurs_löschen_button.clicked.connect(self.kurs_loeschen_dialog)
        self.export_scorecard_button.clicked.connect(self.oeffne_export_scorecard_dialog) 


        
        self.update()

    def oeffne_neues_spiel_dialog(self):
        kurse = help.getAllCourseIDs()
        dialog = NeuesSpielDialog(kurse)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            dialog.get_spiel_daten()
            self.update()

    def neuer_kurs_hinzugefuegt(self):
        dialog = NeuerKursDialog()
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            dialog.get_kurs_daten()
            self.update()

    def kurs_loeschen_dialog(self):
        kurse = help.getAllCourseIDs()
        dialog = KursLoeschenDialog(kurse)
        dialog.exec_()
        
    def oeffne_export_scorecard_dialog(self):
        dialog = ExportScorecardDialog()
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            kurs, is_whs, file_path, kurs_rating, slope_rating, stroke_indices, use_last_values = dialog.get_export_daten()
            help.export_scorecard(kurs, is_whs, file_path, kurs_rating, slope_rating, stroke_indices, use_last_values)

    def update(self):
        new_games = help.getLastGames()
        try:
            new_game = new_games[-1]
            new_handicap = help.getHCLog(startDate=new_game["date"])
            self.ega_handicap_label.setText(f"Aktuelles EGA Handicap: {new_handicap["ega"]}")
            self.whs_handicap_label.setText(f"Aktuelles WHS Handicap: {new_handicap['whs']}")
        except:
            self.ega_handicap_label.setText("Aktuelles EGA Handicap: N/A")
            self.whs_handicap_label.setText("Aktuelles WHS Handicap: N/A")

        self.spiele_tabelle.setRowCount(len(new_games))
        for i, game in enumerate(new_games):
            datum = game["date"]
            kurs = game["courseID"]
            schlaege = sum(game["shots"])
            self.spiele_tabelle.setItem(i, 0, QtWidgets.QTableWidgetItem(datum))
            self.spiele_tabelle.setItem(i, 1, QtWidgets.QTableWidgetItem(kurs))
            self.spiele_tabelle.setItem(i, 2, QtWidgets.QTableWidgetItem(str(schlaege)))

        log = help.getHCLog()

        indices = list(range(1, len(log) + 1))
        ega_handicaps = [entry['ega'] for entry in log]
        whs_handicaps = [entry['whs'] for entry in log]

        self.figure.clear()
        ax = self.figure.add_subplot(111, facecolor='#202020')  # Achsenhintergrund
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.yaxis.label.set_color('white')
        ax.xaxis.label.set_color('white')
        ax.title.set_color('white')

        ax.plot(indices, ega_handicaps, label='EGA Handicap', color='blue')
        ax.plot(indices, whs_handicaps, label='WHS Handicap', color='red')
        ax.legend()

        self.canvas.draw()

        self.spiele_tabelle.resizeColumnsToContents()


if __name__ == "__main__":
    db_dir = "./db"  # should maybe be changed to %APPDATA%
    db_path = os.path.join(db_dir, "db.json")

    # Ensure the directory exists
    os.makedirs(db_dir, exist_ok=True)

    # Initialize the database
    db = TinyDB(db_path)

    # Initialize tables
    games = db.table("games", cache_size=20)  # stores the games that were already calculated
    courses = db.table("courses")  # stores the courses
    hcLog = db.table("hcLog", cache_size=366)  # stores the old HCs max one per day

    # creating instance of Helper and setting default tables
    help = Helper(games, courses, hcLog)

    app = QtWidgets.QApplication(sys.argv)
    ui = HandicapUI()
    ui.show()
    sys.exit(app.exec_())

