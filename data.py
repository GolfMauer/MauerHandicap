from tinydb import TinyDB
import json
import datetime
from os import listdir
from os.path import isfile, join
from pathlib import Path
import uuid

class Golf(TinyDB):
    def insertFromDir(self, path: str) -> None:
        """
        Inserts all the files in the given directory into the given db/table

        Args:
        path (str): the path to the directory
        """
        files = [file for file in listdir(path) if isfile(join(path, file))]

        for file in files:
            json_file = open(path + file, "r")
            data = json.load(json_file)
            self.insert(data)

    def addGame(self, handicap: float, courseID: str, date: datetime.datetime | str, shots: list[int]) -> str:
        """
        Adds a new game to tinyDB.

        Args:
        handicap (float): handicap the game was played with
        courseID (str): e.g. the name of the course
        date (datetime.datetime | str): The date the game was played on, could als obe int he past; you can either pass the datetime object or the iso-string
        shots (list[int]): The shots that were needed for each whole. E.g. [2,3] 2 shots for for first hole, 3 shots for second hole
        
        Returns:
        str: the uuid in hex format
        """

        id = uuid.uuid4()
        game = {"game_id": id.hex,
                "handicap": handicap, 
                "courseID": courseID,
                "date": date.isoformat() if isinstance(date, (datetime.date, datetime.datetime)) else date , 
                "shots": shots
        }
        self.insert(game)

        return id.hex


    def getGames(self, n: int = 0, m: int = 20) -> list[dict]:
        """
        returns the games n to m (inclusive), where n is the lowest index and m is the highest index.
        Defaults to the last 20 games or less if there are less than 20 games

        Args:
        n (int): The starting index.
        m (int): The ending index.

        Returns:
        List[dict]: A list of games between the indices.
        """
        games = self.all()

        if not games:
            return []
    
        sorted_games = sorted(
            games, 
            key=lambda x: datetime.datetime.fromisoformat(x['date']), 
            reverse=True)
        
        # Validate and adjust indices
        n = max(0, n)  # Ensure n is non-negative
        m = min(len(sorted_games) - 1, max(n, m))  # Ensure m is within bounds and >= n

        return sorted_games[n:m + 1]

Path("./db/").mkdir(parents=True, exist_ok=True)

#init db and tables
db = TinyDB('./db/db.json')
games_table = db.table('games')
courses_table = db.table('courses')


paths = ["./data/games/", "./data/courses/"]
DBs = [games_table, courses_table]

#insert the data
#for i in range(len(paths)):
#    insertFromDir(paths[i], DBs[i])



#TODO turn data.py into package and move db into test module
#TODO get last 20 games
#TODO create handicap package
#TODO call handicap and handover PCC value
date = datetime.datetime.now()
addGame(10, "kot", date.isoformat(), [])

getGames()


db.purge_tables()