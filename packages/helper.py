from tinydb import TinyDB, Query
import json
import datetime
from os import listdir
from os.path import isfile, join
import packages.handicapWHS as hc
import uuid

class Helper:
    def __init__(self, games, courses, cron, hcLog):
        self.games = games
        self.courses = courses
        self.cron= cron
        self.hcLog = hcLog


    def insertFromDir(self, table: TinyDB, path: str) -> None:
        """
        Inserts all the files in the given directory into the given db/table

        Args:
        path (str): the path to the directory
        """
        path = path if path[-1] == "/" else path + "/"
        files = [file for file in listdir(path) if isfile(join(path, file))]

        for file in files:
            json_file = open(path + file, "r")
            data = json.load(json_file)
            table.insert(data)

    def addCourse(self, courseID: str, courseRating: int, slopeRating: int, par: list[int], table: TinyDB=None) -> None:
        """
        Adds a new game to tinyDB.

        Args:
        courseID (str): e.g. the name of the course
        courseRating (int): The difficulty rating of the course usually between 67 and 77. Should be the sum of the par's if I understand it correctly
        slopeRating (int): The difficulty rating of the course, between 55 and 155 with the average being 113
        par (list[int]): The shots that that are expected for each hole
        table (TinyDB): By default is set to courses table but can be changed by passing the reference. This should not be necessary 
        
        Returns:
        None
        """
        table = self.courses if table == None else table


        if not (55 <= slopeRating <= 155):
            raise ValueError(f"Invalid parameter: {slopeRating}. Must be between 55 and 155.")
        data = {"course_id": courseID,
                "course_rating": courseRating,
                "slope_rating": slopeRating, 
                "par": par
        }
        table.insert(data)

    def addGame(self, courseID: str, shots: list[int], pcc: float=0 , date: datetime.datetime | str=datetime.datetime.now(), table: TinyDB=None, courseTable: TinyDB=None) -> str:
        """
        Adds a new game to tinyDB.

        Args:
        courseID (str): e.g. the name of the course
        shots (list[int]): The shots that were needed for each whole. E.g. [2,3] 2 shots for for first hole, 3 shots for second hole
        pcc (float): The weather adjustment; by default 0
        date (datetime.datetime | str): The date the game was played on; you can either pass the datetime object or the iso-string by default time.now()
        table (TinyDB): By default is set to courses table but can be changed by passing the reference. This should not be necessary
        courseTable (TinyDB): as this function does a query to tiny db, this allows you to change the default course table 

        Returns: str: the uuid in hex format
        """
        table = self.games if table == None else table

        #TODO check course, pcc,
        #TODO check max amount of shots (Net-Double-Bogey)

        id = uuid.uuid4().hex
        game = { 
                "id": id, 
                "courseID": courseID, 
                "date": date.isoformat() if isinstance(date, (datetime.date, datetime.datetime)) else date, 
                "shots": shots, 
                "pcc": pcc 
            }
        
        # TODO implement handicapIndex table and getter
        course = self.getCourses([game], courseTable)
        #game = hc.handicapDifferential(game, course, handicapIndex)
        
        table.insert(game)

        return id


    def getGames(self, n: int=0, m: int=19, table: TinyDB=None) -> list[dict]:
        """
        returns the last n to m (inclusive) games, where n is the lowest index and m is the highest index.
        Defaults to the last 20 games or less if there are less than 20 games

        Args:
        n (int): The starting index.
        m (int): The ending index.

        Returns:
        List[dict]: A list of games between the indices.
        """
        table = self.games if table == None else table

        games = table.all()

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
    
    
    def getCourses(self, games: list[dict], table: TinyDB=None) -> list[dict]:
        """
        returns the courses played given n games

        Args:
        games (list[dict]): The games relevant for the query
        table (TinyDB): By default is set to courses table but can be changed by passing the reference. This should not be necessary 

        Returns:
        List[dict]: A list of courses played.
        """
        table = self.courses if table == None else table

        unique_courses = {game["courseID"] for game in games}  # Use a set for unique course IDs
        query = Query()

        result = []
        for course_id in unique_courses:
            data = table.search(query.courseID == course_id)
            result.extend(data)  # Extend the result list with the search results

        return result

