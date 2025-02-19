from tinydb import TinyDB, Query
import json
import datetime
from os import listdir
from os.path import isfile, join
import packages.handicapWHS as whs
import packages.handicapEGA as ega
import uuid

class Helper:
    def __init__(self, games, courses, cron, hcLog):
        self.games = games
        self.courses = courses
        self.cron = cron
        self.hcLog = hcLog

    # implements whs 5.4
    def updateHandicapIndex(self, game:dict, date: datetime.datetime | str):
        """
        Calculates the updated HC and inserts it into the db

        Args:
        date (datetime.datetime): date on which the game that triggered the update was caused
        help (Helper): The helper from main with the references to the tables
        """
        date = date if isinstance(date, (datetime.date, datetime.datetime)) else datetime.datetime.fromisoformat(date)

        cba = game["cba"]
        previousHandicap = self.getHCLog(m=0)
        course = self.getCourses(game["courseID"])[0]

        latestGames = self.getLastGames()
        latestEntry = max(latestGames, key=lambda x: x['date'])
        hcLog = self.getHCLog(startDate=latestEntry["date"])

        lowHandicap = min(hcLog, key=lambda x: x['date'])

        whsHC = whs.handicap(latestGames, lowHandicap["whs"])
        egaHC = ega.calculateNewHandicap(game, cba, previousHandicap, course)

        # +1 day since the update is issued one day later
        self.hcLog.insert({ "whs": whsHC, "ega": egaHC, "date": (date + datetime.timedelta(days=1)) })


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

    def addCourse(self, courseID: str, courseRating: int, slopeRating: int, par: list[int]) -> None:
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
        


        if not (55 <= slopeRating <= 155):
            raise ValueError(f"Invalid parameter: {slopeRating}. Must be between 55 and 155.")
        data = {"course_id": courseID,
                "course_rating": courseRating,
                "slope_rating": slopeRating, 
                "par": par
        }
        self.courses.insert(data)

    def addGame(self, 
                courseID: str, 
                shots: list[int], 
                pcc: float=0 ,
                cba: float=0,
                date: datetime.datetime | str=datetime.datetime.now()
                ) -> str:
        """
        Adds a new game to tinyDB.

        Args:
        courseID (str): e.g. the name of the course
        shots (list[int]): The shots that were needed for each whole. E.g. [2,3] 2 shots for for first hole, 3 shots for second hole
        pcc (float): The weather adjustment; by default 0
        cba (float): Buffer adjustment for EGA; by default 0
        date (datetime.datetime | str): The date the game was played on; you can either pass the datetime object or the iso-string by default time.now()
        table (TinyDB): By default is set to courses table but can be changed by passing the reference. This should not be necessary
        courseTable (TinyDB): as this function does a query to tiny db, this allows you to change the default course table 

        Returns: str: the uuid in hex format
        """
        #TODO check course, pcc,

        id = uuid.uuid4().hex
        game = { 
                "id": id, 
                "courseID": courseID, 
                "date": date.isoformat() if isinstance(date, (datetime.date, datetime.datetime)) else date, 
                "shots": shots, 
                "pcc": pcc,
                "cba": cba
            }
        

        # TODO see if patrick has to do anything in here
        course = self.getCourses([game], self.courses)
        game = whs.handicapDifferential(game, course, self.getHCLog(m=0))
        
        if game["exceptional_reduction"] != 0.0:
            Game = Query()
            ids = [game["game_id"] for game in self.getLastGames(0, 18)]
            self.games.update(
                lambda doc: { # for each game tinyDB iterates over it hands the current doc to the lambda function
                    "exceptional_reduction": doc.get("exceptional_reduction", 0) + game["exceptional_reduction"]
                },
                Game.game_id.one_of(ids)
            )

        self.games.insert(game)

        # insert into cron for future calculation
        self.cron.insert({ "game_id": id })

        return id


    def getLastGames(self, n: int=0, m: int=19) -> list[dict]:
        """
        returns the last n to m (inclusive) games, where n is the lowest index and m is the highest index.
        Defaults to the last 20 games or less if there are less than 20 games

        Args:
        n (int): The starting index.
        m (int): The ending index.

        Returns:
        List[dict]: A list of games between the indices.
        """
        
        games = self.games.all()

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
    

    def getHCLog(self, n: int=0, m: int=365, startDate: datetime.datetime=None) -> list[dict]:
        """
        get n m(inclusive) HC Log data. By default set to n=0 and m=365 so last 365 days
        E.g. you want the 15.03 - 15.06 the last update in the time frame was on
        the 02.03. So you'll receive the data from 02.03 - 15.06
        Optionally a different starting date than today can be set.

        Args:
        n (int): The lower bound (in days).
        m (int): The upper bound (in days).
        startDate(datetime.datetime): The reference start date for filtering. Defaults to the current datetime if not provided.

        Returns:
        list[dict]: The handicap log entries within your timeframe. Newest entry first
        """
        if startDate is None:
            startDate = datetime.datetime.now()

        log = self.cron.all()
        log.sort(key=lambda doc: datetime.datetime.fromisoformat(doc["date"]), reverse=True)

        data = [ doc for doc in log if n <= (startDate - datetime.datetime.fromisoformat(doc["date"])).days < m
        ]

        if len(data) < len(log):
            data.append(log[len(data) + n])
        
        return data


    
    def getCourses(self, games: list[dict]) -> list[dict]:
        """
        returns the courses played given n games

        Args:
        games (list[dict]): The games relevant for the query
        table (TinyDB): By default is set to courses table but can be changed by passing the reference. This should not be necessary 

        Returns:
        List[dict]: A list of courses played.
        """
        unique_courses = {game["courseID"] for game in games}  # Use a set for unique course IDs
        query = Query()

        result = []
        for course_id in unique_courses:
            data = self.courses.search(query.courseID == course_id)
            result.extend(data)  # Extend the result list with the search results

        return result


    def cronHCCalc(self, write: bool=True) -> None:
        """
        Calculates the new handicap if the current date and the date of one of the games in the cron table differ.
        Optionally you can just get the value by setting write=false

        Args:
        write (bool): By default true modifies whether you write the new handicap or not
        cronTable (TinyDB): allows you to change the default table, should not be needed
        gamesTable (TinyDB): allows you to change the default table, should not be needed
        """
        Game = Query()
        ids = self.cron.all()
        games = self.games.search(Game.game_id.one_of(ids))
        games = sorted(games, key=lambda x: datetime.datetime.fromisoformat(x['date']))

        now = datetime.datetime.now()
        for game in games:
            gameDate =  datetime.datetime.fromisoformat(game["date"])
            if now.date() != gameDate.date():
                egaHC = ega.calculateNewHandicap() # TODO
                whsHC = whs.handicap(self.getLastGames())
                if write:
                    self.hcLog.insert({ "ega": egaHC, "whs": whsHC, "date": now })



