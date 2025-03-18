from tinydb import TinyDB, Query
import json
from datetime import date, datetime, timedelta
from os import listdir
from os.path import isfile, join
import packages.handicapWHS as whs
import packages.handicapEGA as ega
import uuid
from fpdf import FPDF


class Helper:
    def __init__(self, games, courses, hcLog):
        self.games = games
        self.courses = courses
        self.hcLog = hcLog
        self.last_cr_sr_hcp = None

    # implements whs 5.4
    def updateHandicapIndex(self, game: dict, gameDate: datetime | str) -> dict:
        """
        Calculates the updated HC and inserts it into the db.
        You can turn write of you just want the current unofficial HC

        Args:
        game (dict): The game that caused the update to be triggered
        gameDate (datetime): Date on which the game that triggered the update was caused
        write (bool): By default true modifies whether you write the new handicap or not

        Return:
        dict: The handicaps as a dict
        """
        gameDate = gameDate.isoformat() if isinstance(gameDate, (date, datetime)) else gameDate

        cba = game["cba"]
        previousHandicap = self.getHCLog(m=0) if self.getHCLog(m=0) != [] else [{ "whs": 54, "ega": 54, "date": gameDate }]
        course = self.getCourses([game])[0]

        latestGames = self.getLastGames()
        latestEntry = max(latestGames, key=lambda x: x["date"])
        hcLog = self.getHCLog(startDate=latestEntry["date"]) if self.getHCLog(startDate=latestEntry["date"]) != [] else [{ "whs": 54, "ega": 54, "date": gameDate }]

        lowHandicap = min(hcLog, key=lambda x: x["date"])

        whsHC = whs.handicap(latestGames, lowHandicap["whs"])
        egaHC = ega.calculateNewHandicap(game, cba, previousHandicap[0]["ega"], course)

        data = { "whs": round(whsHC, 1), "ega": round(float(egaHC), 1), "date": gameDate }

        self.hcLog.insert(data)
        
        return data

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

    def addCourse(
        self, 
        courseID: str, 
        courseRating: int, 
        slopeRating: int, 
        par: list[int], 
        handicapStrokeIndex: list[int]
    ) -> None:
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
            raise ValueError(
                f"Invalid parameter: {slopeRating}. Must be between 55 and 155."
            )
        data = {
            "courseID": courseID,
            "course_rating": courseRating,
            "slope_rating": slopeRating,
            "par": par,
            "handicap_stroke_index": handicapStrokeIndex,
        }
        self.courses.insert(data)


    def addGame(self, 
                courseID: str, 
                shots: list[int], 
                nineHole: bool,
                pcc: int=0 ,
                cba: int=0,
                gameDate: datetime | str=datetime.now(),
                handicapAllowance: float = 1
                ) -> str:
        """
        Adds a new game to tinyDB.

        Args:
        courseID (str): e.g. the name of the course
        shots (list[int]): The shots that were needed for each whole. E.g. [2,3] 2 shots for for first hole, 3 shots for second hole
        nineHole (bool): indicate if whether the game was a 9 or 18 hole round
        pcc (float): The weather adjustment; by default 0
        cba (float): Buffer adjustment for EGA; by default 0
        gameDate (datetime| str): The date the game was played on; you can either pass the datetime object or the iso-string by default time.now()
        handicapAllowance (float): Percent value that goes into the gross score adjustment for whs. Default = 1

        Returns: str: the uuid in hex format
        """

        id = uuid.uuid4().hex
        game = { 
                "game_id": id, 
                "courseID": courseID, 
                "date": date.isoformat(gameDate) if isinstance(gameDate, (date, datetime)) else gameDate, 
                "shots": shots, 
                "pcc": pcc,
                "cba": cba,
                "is9Hole": nineHole,
                "handicap_allowance": handicapAllowance
            }

        course = self.getCourses([game])
        
        if course == []:
            raise KeyError(f"Could not find the course {courseID}. Check for typos or create it.")
        
        if not (-1 <= pcc <= 3):
            raise ValueError(f"PCC can only be between -1 and +3. Given value was { pcc }")
        elif not (-2 <= cba <= 1):
            raise ValueError(f"CBA can only be between -2 and +1. Given value was { cba }")
        elif not (0 <= handicapAllowance <=1):
            raise ValueError(f"Handicap allowance can only be between 0 and one. Given value was { handicapAllowance }")
        
        hci = self.getHCLog(m=0)[0]["whs"] if self.getHCLog(m=0) != [] else 54
        
        game = whs.handicapDifferential(game, course[0], hci)
        
        if game["exceptional_reduction"] != 0.0:
            Game = Query()
            lastGames = self.getLastGames(0, 18)

            ids = [game["game_id"] for game in lastGames]
            self.games.update(
                lambda doc: {  # for each game tinyDB iterates over it hands the current doc to the lambda function
                    "exceptional_reduction": doc.get("exceptional_reduction", 0)
                    + game["exceptional_reduction"]
                },
                Game.game_id.one_of(ids),
            )

        self.games.insert(game)

        # insert into hcLog
        self.updateHandicapIndex(game, gameDate)

        return id

    def getLastGames(self, n: int = 0, m: int = 19) -> list[dict]:
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

        sorted_games = sorted(games, key=lambda x: datetime.fromisoformat(x["date"]))

        # Validate and adjust indices
        n = max(0, n)  # Ensure n is non-negative
        m = min(len(sorted_games) - 1, max(n, m))  # Ensure m is within bounds and >= n

        return sorted_games[n : m + 1]

    def getHCLog(
        self, n: int = 0, m: int = 365, startDate: datetime = None
    ) -> list[dict]:
        """
        get n m(inclusive) HC Log data. By default set to n=0 and m=365 so last 365 days
        E.g. you want the data from the 09.01-07.02. The log looks like this [01.01, 01.02, 15.02, 01.03] you will receive [01.01, 01.02, 15.02].
        Since form the 09.01-01.02 you still have the handicap Index that was added on the 01.01. Same reasoning for the 15.02.
        Optionally a different starting date than today can be set.

        Args:
        n (int): The lower bound (in days).
        m (int): The upper bound (in days).
        startDate(datetime): The reference start date for filtering. Defaults to the current datetime if not provided.

        Returns:
        list[dict]: The handicap log entries within your timeframe. Newest entry first
        """
        if startDate is None:
            startDate = datetime.now()

        if isinstance(startDate, str):
            startDate = datetime.fromisoformat(startDate)

        log = self.hcLog.all()
        log.sort(key=lambda doc: datetime.fromisoformat(doc["date"]), reverse=True)

        data = [ doc for doc in log if n <= (startDate - datetime.fromisoformat(doc["date"])).days < m ]

        # add first game spill over
        if data != [] and (datetime.fromisoformat(data[0]["date"]) - startDate).days != 0:
            for i, doc in enumerate(log):
                if (datetime.fromisoformat(doc["date"]) - startDate).days == 0:
                    data = [log[i -1]] + data
                    break

        # add last game spill over
        if len(data) < len(log):
            data.append(log[len(data) + n])

        return data

    def get_last_hci(self, is_whs: bool) -> float:
        log = self.hcLog.all()
        log.sort(key=lambda doc: datetime.fromisoformat(doc["date"]), reverse=True)
        return 54.0 if log == [] else log[0]["whs" if is_whs else "ega"]

    def getCourses(self, games: list[dict]) -> list[dict]:
        """
        returns the courses played given n games

        Args:
        games (list[dict]): The games relevant for the query
        table (TinyDB): By default is set to courses table but can be changed by passing the reference. This should not be necessary

        Returns:
        List[dict]: A list of courses played.
        """
        unique_courses = {game["courseID"] for game in games} # Use a set for unique course IDs
        query = Query()

        result = []
        for course_id in unique_courses:
            data = self.courses.search(query.courseID == course_id)
            result.extend(data)  # Extend the result list with the search results

        return result

    def getAllCourses(self) -> list[dict]:
        """
        Returns all courses in the database.

        Returns:
        List[dict]: A list of all courses.
        """
        return self.courses.all()
    
    def getAllCourseIDs(self) -> list[str]:
        """
        Returns a list of all course IDs in the database.

        Returns:
        List[str]: A list of all course IDs.
        """
        return [course["courseID"] for course in self.courses.all()]
    
    def delete_course_item(self, courseID: str) -> bool:
        """
        Löscht einen Kurs anhand seiner ID aus der Datenbank.

        Returns:
        bool: True, wenn der Kurs erfolgreich gelöscht wurde, sonst False.
        """

        query = Query()
        result = self.courses.remove(query.courseID == courseID)

        if result:
            return True
        else:
            return False

    def getCourseByID(self, courseID: str) -> dict:
        """
        Returns a course as a dictionary given its ID.

        Args:
        courseID (str): The ID of the course to retrieve.

        Returns:
        dict: The course data.
        """
        query = Query()
        result = self.courses.get(query.courseID == courseID)
        if result is None:
            raise KeyError(f"Course with ID {courseID} not found.")
        return result


    def export_scorecard(
        self,
        course: str,
        is_whs: bool,
        filepath: str,
        cr_override: float | None = None,
        sr_override: int | None = None,
        hcp_override: list[int] | None = None,
        use_last_values: bool | None = None,
    ):
        """Generates a Scorecard as PDF and outputs it to given filepath

        Args:
            course (str): The ID of the course being played on
            hci (float): The Handicap Index of the player
            pcc (int): PCC or CBA of the game
            filepath (str): The location and filename the scorecard should be saved to
        """
        hci = self.get_last_hci(is_whs)

        # I don't trust that I won't accidentally be overwriting things
        # and I'm too lazy to copy these into their own variables
        course = self.getCourseByID(course)
        course = course.copy()
        
        
        if cr_override is not None:
            course["course_rating"] = cr_override

        if sr_override is not None:
            course["slope_rating"] = sr_override

        if hcp_override is not None:
            course["handicap_stroke_index"] = hcp_override

        if use_last_values:
            course["course_rating"] = self.last_cr_sr_hcp["cr"]
            course["slope_rating"] = self.last_cr_sr_hcp["sr"]
            course["handicap_stroke_index"] = self.last_cr_sr_hcp["hcp"]

        self.last_cr_sr_hcp = {
            "cr": course["course_rating"],
            "sr": course["slope_rating"],
            "hcp": course["handicap_stroke_index"],
        }

        data = prepare_table_data(course, hci)
        # create pdf page
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", style="B", size=22)
        pdf.cell(text=f"Kurs: {course["courseID"]}")
        pdf.ln(h=14)
        pdf.set_font("Helvetica", size=14)

        today = datetime.now().strftime("%x")  # uses local date format
        text = f"__**CR:** {course["course_rating"]}  **SR:** {course["slope_rating"]}  **PCC/CBA:** ____  **Datum:** {today}  **HCI:** {hci}  **Name:**__"
        pdf.multi_cell(
            w=pdf.get_string_width(text, markdown=True) + 2,
            text=text,
            markdown=True,
        )
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.line(x, y, pdf.w - pdf.r_margin, y)
        pdf.ln()

        with pdf.table(col_widths=(3, 3, 3, 3, 5)) as table:
            row = table.row()
            for cell in ("Loch", "Par", "HCP", "Vorgabe", "Schläge"):
                row.cell(cell)
            for data_row in data:
                row = table.row()
                for cell in data_row:
                    row.cell(cell)

        pdf.output(filepath)

    def get_all_courses(self) -> list[dict]:
        """Returns a list of dictionaries describing all courses saved.

        Returns:
            list[dict]: A list of courses.
        """
        return self.courses.all()


def prepare_table_data(
    course: dict, hci: float
) -> list[tuple[str, str, str, str, str]]:
    """Generates a tuple of tuples representing rows in the scorecard table

    Args:
        course (dict): The course played on
        hci (float): The handicap of the player
        pcc (int): PCC/CBA of the game

    Returns:
        tuple[tuple[str, str, str, str, str], ...]:
        A tuple of tuples representing the rows of the table
    """
    par = course["par"].copy()
    
    is9Hole = True if len(course["par"]) == 9 else False
    hc_strokes = ega.playingHandicap(
        is9Hole, hci, course["course_rating"], course["slope_rating"], sum(course["par"])
    )
    strokes = ega.spreadPlayingHC(course, hc_strokes, is9Hole)
    stroke_allocation = [x - y for x, y in zip(strokes, par)]
    # Hole#, Par, HCP, hcp-strokes, shots taken (empty)
    rows = []
    for i in range(0, 9):
        row = tuple(
            map(
                str,
                (
                    i + 1,
                    par[i],
                    course["handicap_stroke_index"][i],
                    "/" * stroke_allocation[i],
                    "",
                ),
            )
        )
        rows.append(row)
    rows.append(("OUT", str(sum(par[0:9])), "", "", ""))

    for i in range(9, 18):
        row = tuple(
            map(
                str,
                (
                    i + 1,
                    par[i],
                    course["handicap_stroke_index"][i],
                    stroke_allocation[i] * "/",
                    "",
                ),
            )
        )
        rows.append(row)
    rows.append(("IN", str(sum(par[9:18])), "", "", ""))
    rows.append(("GESAMT", str(sum(par)), "", "", ""))

    return rows
