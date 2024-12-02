from tinydb import TinyDB, Query
import json
import datetime
from os import listdir
from os.path import isfile, join
from pathlib import Path


def insertData(path: str, table) -> None:
    files = [file for file in listdir(path) if isfile(join(path, file))]

    for file in files:
        json_file = open(path + file, "r")
        data = json.load(json_file)
        table.insert(data)


Path("./db/").mkdir(parents=True, exist_ok=True)

#init db and tables
db = TinyDB('./db/db.json')
games_table = db.table('games')
courses_table = db.table('courses')

paths = ["./data/games/", "./data/courses/"]
DBs = [games_table, courses_table]

#insert the data
for i in range(len(paths)):
    insertData(paths[i], DBs[i])

def createGame(handicap: int, courseID: str, date: datetime, shots: list[int]):
    id = "asdf"
    game = {"game_id": id,
            "handicap": handicap, 
            "courseID": courseID,
            "date": date,
            "shots": shots
    }
    games_table.insert(game)
print(datetime.datetime.now())
#TODO create new game with python date
#TODO get last 20 games
#TODO create handicap package
#TODO call handicap and handover PCC value


db.purge_tables()