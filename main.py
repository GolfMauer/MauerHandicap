import sys
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtWidgets, QtGui, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime

class NeuesSpielDialog(QtWidgets.QDialog):
    def __init__(self, kurse):
        super().__init__()
        self.setWindowTitle("Neues Spiel")
        layout = QtWidgets.QVBoxLayout()

        self.setWhatsThis("Dieser Dialog ermöglicht es dir, ein neues Spiel zu starten. "
                          "Wähle den Kurs, die Anzahl der Löcher und gib die Schlagzahlen ein.")

        self.kurs_combo = QtWidgets.QComboBox()
        self.kurs_combo.addItems(kurse)
        layout.addWidget(QtWidgets.QLabel("Kurs:"))
        layout.addWidget(self.kurs_combo)

        self.neun_loch_radio = QtWidgets.QRadioButton("9 Löcher")
        self.achtzehn_loch_radio = QtWidgets.QRadioButton("18 Löcher")
        self.neun_loch_radio.setChecked(True)
        layout.addWidget(QtWidgets.QLabel("Anzahl Löcher:"))
        layout.addWidget(self.neun_loch_radio)
        layout.addWidget(self.achtzehn_loch_radio)

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

        self.neun_loch_radio.toggled.connect(self.update_schlagzahl_eingabe)
        self.achtzehn_loch_radio.toggled.connect(self.update_schlagzahl_eingabe)

    def update_schlagzahl_eingabe(self):
        locher = 9 if self.neun_loch_radio.isChecked() else 18
        for i in range(1, 19):
            self.schlagzahl_eingabe[i].setVisible(i <= locher)
            self.schlagzahl_labels[i].setVisible(i <= locher)

    def get_spiel_daten(self):
        kurs = self.kurs_combo.currentText()
        locher = 9 if self.neun_loch_radio.isChecked() else 18
        schlagzahlen = {}
        for i in range(1, locher + 1):
            try:
                schlagzahlen[i] = int(self.schlagzahl_eingabe[i].text())
            except ValueError:
                schlagzahlen[i] = 0
        return kurs, locher, schlagzahlen

class NeuerKursDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neuer Kurs")

        layout = QtWidgets.QVBoxLayout()
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

    def get_kurs_daten(self):
        kurs_name = self.kurs_name_eingabe.text()
        kurs_rating = self.kurs_rating_eingabe.text()
        slope_rating = self.slope_rating_eingabe.text()
        locher = 9 if self.neun_loch_radio.isChecked() else 18
        pars = {}
        for i in range(1, locher + 1):
            try:
                pars[i] = int(self.par_eingabe[i].text())
            except ValueError:
                pars[i] = 0
        return kurs_name, kurs_rating, slope_rating, locher, pars

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
        app.setStyle('Fusion') # Stil anpassen


        layout = QtWidgets.QVBoxLayout()

        button_layout = QtWidgets.QHBoxLayout()
        self.neues_spiel_button = QtWidgets.QPushButton("Neues Spiel")
        self.neuer_kurs_button = QtWidgets.QPushButton("Neuer Kurs")
        button_layout.addWidget(self.neues_spiel_button)
        button_layout.addWidget(self.neuer_kurs_button)
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
        self.spiele_tabelle.setColumnCount(4)
        self.spiele_tabelle.setHorizontalHeaderLabels(["Datum", "Kurs", "Schläge", "Handicap"])
        layout.addWidget(self.spiele_tabelle)


        self.setLayout(layout)

        self.neues_spiel_button.clicked.connect(self.oeffne_neues_spiel_dialog)
        self.neuer_kurs_button.clicked.connect(self.neuer_kurs_hinzugefuegt)


        self.update()

    def oeffne_neues_spiel_dialog(self):
         #platzhalter!!!!!!!!!!!!!!!!!!!!
        kurse = ["Course A", "Course B", "Course C"]
        dialog = NeuesSpielDialog(kurse)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            kurs, locher, schlagzahlen = dialog.get_spiel_daten()
            print("Neues Spiel hinzugefügt:", kurs, locher, schlagzahlen)
            self.neues_spiel_hinzugefuegt(kurs, locher, schlagzahlen)

    def neues_spiel_hinzugefuegt(self, kurs, locher, schlagzahlen):
        datum = datetime.now().strftime("%Y-%m-%d")
        schlaege = sum(schlagzahlen.values())
        handicap = self.berechne_handicap() # Hier musst du die tatsächliche Berechnung einfügen

        # Neues Spiel in der Tabelle hinzufügen
        row_position = self.spiele_tabelle.rowCount()
        self.spiele_tabelle.insertRow(row_position)
        self.spiele_tabelle.setItem(row_position, 0, QtWidgets.QTableWidgetItem(datum))
        self.spiele_tabelle.setItem(row_position, 1, QtWidgets.QTableWidgetItem(kurs))
        self.spiele_tabelle.setItem(row_position, 2, QtWidgets.QTableWidgetItem(str(schlaege)))
        self.spiele_tabelle.setItem(row_position, 3, QtWidgets.QTableWidgetItem(str(handicap)))

    def neuer_kurs_hinzugefuegt(self):
        dialog = NeuerKursDialog()
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            kurs_name, kurs_rating, slope_rating, locher, pars = dialog.get_kurs_daten()
            print("Neuer Kurs hinzugefügt:", kurs_name, kurs_rating, slope_rating, locher, pars)
            
             #platzhalter!!!!!!!!!!!!!!!!!!!!
            # Hier die Logik zum Speichern des neuen Kurses 
            self.update()




    def update(self):
        #platzhalter!!!!!!!!!!!!!!!!!!!!
        #soll alles updaten, course und spiele pullen und pushen und graf aktualliesieren und handicap aktualliesieren und die letzt x spiele in die tabelle 
        print("Daten werden aktualisiert")

        aktuelles_ega_handicap = self.berechne_ega_handicap()
        self.ega_handicap_label.setText(f"Aktuelles EGA Handicap: {aktuelles_ega_handicap}")

        aktuelles_whs_handicap = self.berechne_whs_handicap()
        self.whs_handicap_label.setText(f"Aktuelles WHS Handicap: {aktuelles_whs_handicap}")

        x = [1, 2, 3, 4, 5]
        y = [10, 12, 11, 13, 15]

        self.figure.clear()
        ax = self.figure.add_subplot(111, facecolor='#202020') # Achsenhintergrund
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.yaxis.label.set_color('white')
        ax.xaxis.label.set_color('white')
        ax.title.set_color('white')

        ax.plot(x, y)
        self.canvas.draw()
        
        self.spiele_tabelle.resizeColumnsToContents()

    def berechne_ega_handicap(self):
        # Hier die Logik zur Berechnung des EGA-Handicaps einfügen
        return "15.5"  # Platzhalter

    def berechne_whs_handicap(self):
        # Hier die Logik zur Berechnung des WHS-Handicaps einfügen
        return "14.2"  # Platzhalter

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = HandicapUI()
    ui.show()
    sys.exit(app.exec_())
