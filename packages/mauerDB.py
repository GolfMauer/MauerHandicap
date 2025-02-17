from tinydb import TinyDB, Query
import json
import datetime
from os import listdir
from os.path import isfile, join
import packages.handicapWHS as hc
import uuid

class MauerDB(TinyDB):
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

    def addCourse(self, courseID: str, courseRating: int, slopeRating: int, par: list[int]) -> None:
        """
        Adds a new game to tinyDB.

        Args:
        courseID (str): e.g. the name of the course
        courseRating (int): The difficulty rating of the course usually between 67 and 77. Should be the sum of the par's if I understand it correctly
        slopeRating (int): The difficulty rating of the course, between 55 and 155 with the average being 113
        par (list[int]): The shots that that are expected for each hole
        
        Returns:
        None
        """

        if not (55 <= slopeRating <= 155):
            raise ValueError(f"Invalid parameter: {slopeRating}. Must be between 55 and 155.")
        data = {"course_id": courseID,
                "course_rating": courseRating,
                "slope_rating": slopeRating, 
                "par": par
        }
        self.insert(data)

    def addGame(self, courseID: str, date: datetime.datetime | str, shots: list[int], pcc: float) -> str:
        """
        Adds a new game to tinyDB.

        Args:
        courseID (str): e.g. the name of the course
        date (datetime.datetime | str): The date the game was played on, could als obe int he past; you can either pass the datetime object or the iso-string
        shots (list[int]): The shots that were needed for each whole. E.g. [2,3] 2 shots for for first hole, 3 shots for second hole
        
        Returns: str: the uuid in hex format
        """

        #TODO check course, pcc,
        #TODO check max amount of shots (Net-Double-Bogey)

        course = self.getCourses([{"courseID": courseID}])
        id = uuid.uuid4().hex
        game = { 
                "id": id, 
                "courseID": courseID, 
                "date": date.isoformat() if isinstance(date, (datetime.date, datetime.datetime)) else date, 
                "shots": shots, 
                "pcc": pcc 
            }
        
        # TODO implement handicapIndex table and getter
        game = hc.handicapDifferential(game, course, handicapIndex)
        
        self.insert(game)

        return id


    def getGames(self, n: int = 0, m: int = 19) -> list[dict]:
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
    
    
    def getCourses(self, games: list[dict]) -> list[dict]:
        """
        returns the courses played given n games

        Args:
        games (list[dict]): The games relevant for the query

        Returns:
        List[dict]: A list of courses played.
        """

        unique_courses = {game["course_ID"] for game in games}  # Use a set for unique course IDs
        query = Query()

        result = []
        for course_id in unique_courses:
            #TODO shouldnt this be self.search instead
            data = self.table.search(query.courseID == course_id)  # Assuming self.table is a TinyDB table
            result.extend(data)  # Extend the result list with the search results

        return result

