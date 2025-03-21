from datetime import date, datetime
import json
from os import listdir
from os.path import isfile, join
import uuid
from tinydb import TinyDB, Query, where
import handicapWHS as whs
import handicapEGA as ega
from fpdf import FPDF


class Helper:
    def __init__(self, games, courses, hcLog):
        self.games = games
        self.courses = courses
        self.hcLog = hcLog

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
        gameDate = (
            gameDate
            if isinstance(gameDate, (date, datetime))
            else datetime.fromisoformat(gameDate)
        )

        cba = game["cba"]
        previousHandicap = self.getHCLog(m=0)
        course = self.getCourses(game["courseID"])[0]

        latestGames = self.getLastGames()
        latestEntry = max(latestGames, key=lambda x: x["date"])
        hcLog = self.getHCLog(startDate=latestEntry["date"])

        lowHandicap = min(hcLog, key=lambda x: x["date"])

        whsHC = whs.handicap(latestGames, lowHandicap["whs"])
        egaHC = ega.calculateNewHandicap(game, cba, previousHandicap, course)

        data = {"whs": whsHC, "ega": egaHC, "date": gameDate}

        # remove current HC if it is from the same day
        HC = Query()
        self.hcLog.remove(
            HC.date.test(lambda d: datetime.fromisoformat(d).date() == gameDate)
        )

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
        self, courseID: str, courseRating: int, slopeRating: int, par: list[int]
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
            "course_id": courseID,
            "course_rating": courseRating,
            "slope_rating": slopeRating,
            "par": par,
        }
        self.courses.insert(data)

    def addGame(
        self,
        courseID: str,
        shots: list[int],
        nineHole: bool,
        pcc: float = 0,
        cba: float = 0,
        gameDate: datetime | str = datetime.now(),
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
        table (TinyDB): By default is set to courses table but can be changed by passing the reference. This should not be necessary
        courseTable (TinyDB): as this function does a query to tiny db, this allows you to change the default course table

        Returns: str: the uuid in hex format
        """
        course = self.getCourses([game], self.courses)
        if course == []:
            raise KeyError(
                f"Could not find the course {courseID}. Check for typos or create it."
            )

        if not (-1 >= pcc <= 3):
            raise ValueError(
                f"PCC can only be between -1 and +3. Given value was { pcc }"
            )
        if not (-2 >= cba <= 1):
            raise ValueError(
                f"CBA can only be between -2 and +1. Given value was { cba }"
            )

        id = uuid.uuid4().hex
        game = {
            "id": id,
            "courseID": courseID,
            "date": (
                date.isoformat() if isinstance(gameDate, (date, datetime)) else gameDate
            ),
            "shots": shots,
            "pcc": pcc,
            "cba": cba,
            "is9hole": nineHole,
        }

        game = whs.handicapDifferential(game, course, self.getHCLog(m=0))

        if game["exceptional_reduction"] != 0.0:
            Game = Query()
            ids = [game["game_id"] for game in self.getLastGames(0, 18)]
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

        sorted_games = sorted(
            games, key=lambda x: datetime.fromisoformat(x["date"]), reverse=True
        )

        # Validate and adjust indices
        n = max(0, n)  # Ensure n is non-negative
        m = min(len(sorted_games) - 1, max(n, m))  # Ensure m is within bounds and >= n

        return sorted_games[n : m + 1]

    def getHCLog(
        self, n: int = 0, m: int = 365, startDate: datetime = None
    ) -> list[dict]:
        """
        get n m(inclusive) HC Log data. By default set to n=0 and m=365 so last 365 days
        E.g. you want the 15.03 - 15.06 the last update in the time frame was on
        the 02.03. So you'll receive the data from 02.03 - 15.06
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

        log = self.hcLog.all()
        log.sort(key=lambda doc: datetime.fromisoformat(doc["date"]), reverse=True)

        data = [
            doc
            for doc in log
            if n <= (startDate - datetime.fromisoformat(doc["date"])).days < m
        ]

        if len(data) < len(log):
            data.append(log[len(data) + n])

        return data

    def get_last_hci(self, is_whs: bool) -> float:
        log = self.hcLog.all()
        log.sort(key=lambda doc: datetime.fromisoformat(doc["date"]), reverse=True)
        return log[0]["whs" if is_whs else "ega"]

    def getCourses(self, games: list[dict]) -> list[dict]:
        """
        returns the courses played given n games

        Args:
        games (list[dict]): The games relevant for the query
        table (TinyDB): By default is set to courses table but can be changed by passing the reference. This should not be necessary

        Returns:
        List[dict]: A list of courses played.
        """
        unique_courses = {
            game["courseID"] for game in games
        }  # Use a set for unique course IDs
        query = Query()

        result = []
        for course_id in unique_courses:
            data = self.courses.search(query.courseID == course_id)
            result.extend(data)  # Extend the result list with the search results

        return result

    def export_scorecard(
        self,
        filepath: str,
        course: dict,
        is_whs: bool | None = None,
        cr_override: float | None = None,
        sr_override: int | None = None,
        hcp_override: list[int] | None = None,
        use_last_values: bool | None = None,
    ):
        """Generates a Scorecard as PDF and outputs it to given filepath

        Args:
            filepath (str): Path the File will be saved to.
            course (dict): The Course being played on
            is_whs (bool | None, optional): . Defaults to None.
            cr_override (float | None, optional): Value to override course rating with. Defaults to None.
            sr_override (int | None, optional): Value to override slope rating with. Defaults to None.
            hcp_override (list[int] | None, optional): List to override hcp-index with. Defaults to None.
            use_last_values (bool | None, optional): Flag to use last values stored in course. Defaults to None.

        Raises:
            AttributeError: Raised when is_whs is missing when not using last values.
            ValueError: Raised when trying to access last values, but they are nonexistent.
        """
        if not use_last_values:
            if is_whs is None:
                raise AttributeError("Attribute is_whs missing.")

        # I don't trust that I won't accidentally be overwriting things
        course_copy = course.copy()

        if use_last_values:
            # TODO: has to be written to DB, only the attribute is pass by ref, but does not change entry in DB
            required_fields = [
                "course_rating_override",
                "slope_rating_override",
                "handicap_stroke_index_override",
                "is_whs_scorecard",
            ]
            for field in required_fields:
                if field not in course or course[field] is None:
                    # This should envoke a dialog (UI) that there are no last values avaliable
                    raise ValueError(f"Missing or unset field: {field}")

            course_copy["course_rating"] = course["course_rating_override"]
            course_copy["slope_rating"] = course["slope_rating_override"]
            course_copy["handicap_stroke_index"] = course[
                "handicap_stroke_index_override"
            ]
            course_copy["is_whs_scorecard"] = course["is_whs_scorecard"]
        else:

            course_copy["is_whs_scorecard"] = is_whs
            self.courses.update(
                {"is_whs_scorecard": is_whs}, where("courseID") == course["courseID"]
            )
            if cr_override is not None:
                course_copy["course_rating"] = cr_override
                self.courses.update(
                    {"course_rating_override": cr_override},
                    where("courseID") == course["courseID"],
                )

            if sr_override is not None:
                if not (55 <= sr_override <= 155):
                    raise ValueError(
                        f"Invalid parameter: {sr_override}. Must be between 55 and 155."
                    )
                course_copy["slope_rating"] = sr_override
                self.courses.update(
                    {"slope_rating_override": sr_override},
                    where("courseID") == course["courseID"],
                )

            if hcp_override is not None:
                if not set(hcp_override) == set(range(0,19)):
                    raise ValueError("Handicap stroke index override is incorrect. Make sure you are only using numbers from 1 to 18.")
                course_copy["handicap_stroke_index"] = hcp_override
                self.courses.update(
                    {"handicap_stroke_index_override": hcp_override},
                    where("courseID") == course["courseID"],
                )

        hci = self.get_last_hci(course_copy["is_whs_scorecard"])

        data = prepare_table_data(course_copy, hci)
        # create pdf page
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", style="B", size=22)
        pdf.cell(text=f"Kurs: {course_copy["courseID"]}")
        pdf.ln(h=14)
        pdf.set_font("Helvetica", size=14)

        today = datetime.now().strftime("%x")  # uses local date format
        text = f"__**CR:** {course_copy["course_rating"]}  **SR:** {course_copy["slope_rating"]}  **PCC/CBA:** ____  **Datum:** {today}  **HCI:** {hci}  **Name:**__"
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
    hc_strokes = ega.playingHandicap(
        False, hci, course["course_rating"], course["slope_rating"], sum(course["par"])
    )
    allocation_marker = "/"
    if hc_strokes < 0:
        allocation_marker = "="
    strokes = ega.spreadPlayingHC(course, hc_strokes, False)
    stroke_allocation = list(map(abs, [x - y for x, y in zip(strokes, par)]))
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
                    allocation_marker * stroke_allocation[i],
                    "",
                ),
            )
        )
        rows.append(row)
    rows.append(("OUT", str(sum(par[0:9])), "", "", ""))

    if len(course["par"]) == 18:
        for i in range(9, 18):
            row = tuple(
                map(
                    str,
                    (
                        i + 1,
                        par[i],
                        course["handicap_stroke_index"][i],
                        allocation_marker * stroke_allocation[i],
                        "",
                    ),
                )
            )
            rows.append(row)
        rows.append(("IN", str(sum(par[9:18])), "", "", ""))
    rows.append(("GESAMT", str(sum(par)), "", str(hc_strokes), ""))

    return rows
