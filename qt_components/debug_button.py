import json
import pathlib
import re
import matplotlib

from packages.helper import Helper
matplotlib.use('Qt5Agg')
from PyQt5 import QtWidgets

class DebugButtons(QtWidgets.QWidget):
    def __init__(self, help: Helper, parent=None):
        super().__init__(parent)
        self.help = help
        self.lade_games_button = QtWidgets.QPushButton("Import Lade Games", self)
        self.lade_courses_button = QtWidgets.QPushButton("Import Lade Courses", self)
        self.lade_games_button.clicked.connect(self.add_lade_games)
        self.lade_courses_button.clicked.connect(self.add_lade_courses)

        self.truncate_button = QtWidgets.QPushButton("Clear DB", self)
        self.truncate_button.clicked.connect(self.truncate_db)
        
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.lade_courses_button)
        layout.addWidget(self.lade_games_button)
        layout.addWidget(self.truncate_button)

        self.setLayout(layout)

        self.update()


    def truncate_db(self):
        self.help.games.truncate()
        self.help.courses.truncate()
        self.help.hcLog.truncate()
        self.parent().update()

    def add_lade_games(self):
        files = list(pathlib.Path("./test/real_data/games/").glob("Runde*.json"))
        files.sort(key=lambda f: int(re.search(r'\d+', f.stem).group()))
        files = list(pathlib.Path("./test/real_data/games/").glob("Runde*.json"))
        files.sort(key=lambda f: int(re.search(r'\d+', f.stem).group()))
        games = list()
        for file in files:
            with file.open() as file:
                data = json.load(file)
            games.append(data)
        
        for game in games:
            courseID = game["courseID"]
            shots = game["shots"]
            nineHole = game["is9Hole"]
            pcc = game["pcc"]
            cba = game["cba"]
            gameDate = game["date"]
            self.help.addGame(courseID, shots, nineHole, pcc, cba, gameDate)
        self.parent().update()

    def add_lade_courses(self):
        files = list(pathlib.Path("./test/real_data/courses/").glob("Kurs*.json"))
        files = list(pathlib.Path("./test/real_data/courses/").glob("Kurs*.json"))
        courses = list()
        for file in files:
            with file.open() as file:
                data = json.load(file)
            courses.append(data)
        
        for course in courses:
            self.help.addCourse(
                course["courseID"],
                course["course_rating"],
                course["slope_rating"],
                course["par"],
                course["handicap_stroke_index"],
            )
#################################################################################

