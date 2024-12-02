from tinydb import TinyDB, Query
import json
from os import listdir
from os.path import isfile, join
from pathlib import Path


def insertData(path: str, db: TinyDB):
    files = [file for file in listdir(path) if isfile(join(path, file))]

    for file in files:
        json_file = open(path + file, "r")
        data = json.load(json_file)

        db.insert(data)

    db.all()

Path("./db/").mkdir(parents=True, exist_ok=True)

gamesDB = TinyDB('./db/games-DB.json')
coursesDB = TinyDB('./db/courses-DB.json')

paths = ["./data/games/", "./data/courses/"]
DBs = [gamesDB, coursesDB]

for i in range(len(paths)):
    insertData(paths[i], DBs[i])

