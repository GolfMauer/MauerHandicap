from datetime import datetime, timedelta
import pathlib
import random
from tempfile import TemporaryDirectory
import json

import pytest
from tinydb import TinyDB
from helper import Helper


# Fixture to set up and tear down the temporary database
@pytest.fixture
def helper():
    with TemporaryDirectory() as temp_dir:
        db_dir = f"{temp_dir}/test_db.json"
        # Initialize the database
        db = TinyDB(db_dir)

        # Initialize tables
        games = db.table("games", cache_size=20) # stores the games that were already calculated
        courses = db.table("courses") # stores the courses
        hcLog = db.table("hcLog", cache_size=366) # stores the old HCs max one per day

        # creating instance of Helper and setting default tables
        help = Helper(games, courses, hcLog)

        yield help
        db.close()


@pytest.fixture
def games():
    files = list(pathlib.Path("test").glob("Runde*.json"))
    games = list()
    for file in files:
        with file.open() as file:
            data = json.load(file)
        games.append(data)
    return games


@pytest.fixture
def courses():
    files = list(pathlib.Path("test/courses").glob("course_*.json"))
    courses = list()
    for file in files:
        with file.open() as file:
            data = json.load(file)
        courses.append(data)
    return courses


@pytest.fixture
def score_differential():
    return [ 37.4, 29.6, 24.1, 28.4, 18.8, 31.1, 36, 21.7, 15.4, 21.7, 28.6, 46,7 ]


@pytest.fixture
def WHS_handicap():
    # only for game 7 to 12
    return [ 29.3, 28.4 ,25.6 ,23.9 , 23.5, 23.5 ]


@pytest.fixture
def EGA_handicap():
    # just 7 for now because this is only ega data
    return [54, 37, 32.5, 27.5, 27.5, 23.7, 23.7, 23.8]



#fixture to insert 21 games
@pytest.fixture
def multiple_games(helper: Helper):
    # Generate mock data with 21 entries
    mock_data: list[dict] = []
    base_date = datetime(2024, 12, 3, 11, 41, 30)
    course_names = ["Womp Womp", "Sunny Links", "Green Meadow", "Pine Valley"]
    
    for i in range(1, 22):
        mock_data.append({
            "game_id": str(i),
            "handicap_differential": round(random.uniform(0.0, 54.0), 1),
            "courseID": random.choice(course_names),
            "date": (base_date - timedelta(days=i)).isoformat(),
            "shots": [random.randint(3, 6) for _ in range(18)]
        })

    helper.games.insert_multiple(mock_data)
    return helper


def test_addGame(helper, games, courses, score_differential, WHS_handicap, EGA_handicap):
    helper.courses.insert_multiple(courses)

    def checkChanges(helper: Helper, i: int):
        log = helper.hcLog.all()
        log.sort(key=lambda doc: datetime.fromisoformat(doc["date"]), reverse=True)
        if i <= 7:
            assert log[0]["ega"] == EGA_handicap[i]
        elif i >= 7:
            assert log[0]["whs"] == EGA_handicap[i]


    for i, game in enumerate(games):
        courseID = game["courseID"]
        shots = game["shots"]
        nineHole = game["is9Hole"]
        pcc = game["pcc"]
        cba = game["cba"]
        gameDate = game["date"]
        helper.addGame(courseID, shots, nineHole, pcc, cba, gameDate)
        checkChanges(helper, i)

def test_export_scorecard(helper: Helper, courses):
    helper.courses.insert_multiple(courses)
    helper.hcLog.insert({"whs": 40.1, "ega": 50.1, "date": datetime.now().isoformat()})
    
    helper.export_scorecard(helper.get_all_courses()[0], False, "/home/installadm/hochschule/NoCapHandicap/export.pdf")

    # this won't assert anything for now lol