from tinydb import TinyDB, Query
import json
import datetime
from os import listdir
from os.path import isfile, join
from pathlib import Path
import uuid


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
#for i in range(len(paths)):
#    insertData(paths[i], DBs[i])

def createGame(handicap: int, courseID: str, date: datetime, shots: list[int]) -> uuid:
    """adds a new game to tinyDB given a handicap, courseID (e.g. the name of the course), 
    a date, and a list of shots. Returns the game uuid"""

    id = uuid.uuid4()
    game = {"game_id": id.hex,
            "handicap": handicap, 
            "courseID": courseID,
            "date": date.isoformat() if isinstance(date, (datetime.date, datetime.datetime)) else date , 
            "shots": shots
    }
    games_table.insert(game)

    return id.hex


def recentGames():
    """returns the last 20 games or less if there are less than 20 games"""
    games = games_table.all()
    print(games)
    sorted_games = sorted(games, key=lambda x: datetime.datetime.fromisoformat(x['date']), reverse=True)


#TODO turn data.py into package and move db into test module
#TODO get last 20 games
#TODO create handicap package
#TODO call handicap and handover PCC value
date = datetime.datetime.now()
createGame(10, "kot", date.isoformat(), [])

recentGames()


db.purge_tables()