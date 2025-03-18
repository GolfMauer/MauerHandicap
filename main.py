import sys
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from qt_components.debug_button import DebugButtons
from qt_components.header_buttons import HeaderButton

from tinydb import TinyDB
from packages.helper  import Helper
import os

class HandicapUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()     
        # main component
        self.layout = QtWidgets.QVBoxLayout()


        self.ega_handicap_label = QtWidgets.QLabel("Aktuelles EGA Handicap: N/A")
        self.ega_handicap_label.setStyleSheet("font-size: 20px; color: white;")
        self.ega_handicap_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.ega_handicap_label)

        self.whs_handicap_label = QtWidgets.QLabel("Aktuelles WHS Handicap: N/A")
        self.whs_handicap_label.setStyleSheet("font-size: 20px; color: white;")
        self.whs_handicap_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.whs_handicap_label)

        self.figure = Figure(facecolor='#353535')
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.spiele_tabelle = QtWidgets.QTableWidget()
        self.spiele_tabelle.setColumnCount(3)
        self.spiele_tabelle.setHorizontalHeaderLabels(["Datum", "Kurs", "Schläge"])
        self.layout.addWidget(self.spiele_tabelle)

        # new component based buttons move to top of init for correct order
        self.header_button = HeaderButton(help, self)
        self.debug_buttons = DebugButtons(help, self)
        self.initUI()

        self.setLayout(self.layout)


    def initUI(self):
        app.setStyle('Fusion') 
        self.setWindowTitle("Golf Handicap Rechner")
        self.setWindowIcon(QIcon("./mauerIcon.ico"))
        
        self.layout.addWidget(self.header_button)

        self.layout.addWidget(self.debug_buttons)


        self.update()


    def update(self):
        new_games = help.getLastGames()
        log = help.getHCLog()
        try:
            self.ega_handicap_label.setText(f"Aktuelles EGA Handicap: {log[0]["ega"]}")
            self.whs_handicap_label.setText(f"Aktuelles WHS Handicap: {log[0]['whs']}")
        except:
            self.ega_handicap_label.setText("Aktuelles EGA Handicap: Error")
            self.whs_handicap_label.setText("Aktuelles WHS Handicap: Error")

        self.spiele_tabelle.setRowCount(len(new_games))
        for i, game in enumerate(new_games):
            datum = game["date"]
            kurs = game["courseID"]
            schlaege = sum(game["shots"])
            self.spiele_tabelle.setItem(i, 0, QtWidgets.QTableWidgetItem(datum))
            self.spiele_tabelle.setItem(i, 1, QtWidgets.QTableWidgetItem(kurs))
            self.spiele_tabelle.setItem(i, 2, QtWidgets.QTableWidgetItem(str(schlaege)))

        log.reverse()
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

# moved out to make palette global
def setColors():
    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    
    return dark_palette

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
    app.setPalette(setColors())
    ui = HandicapUI()
    ui.show()
    sys.exit(app.exec_())

