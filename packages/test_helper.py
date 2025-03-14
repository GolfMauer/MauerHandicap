from datetime import datetime, timedelta
import pathlib
import random
import re
import re
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
        games = db.table(
            "games", cache_size=20
        )  # stores the games that were already calculated
        courses = db.table("courses")  # stores the courses
        hcLog = db.table("hcLog", cache_size=366)  # stores the old HCs max one per day

        # creating instance of Helper and setting default tables
        help = Helper(games, courses, hcLog)

        yield help
        db.close()


@pytest.fixture
def games():
    files = list(
        pathlib.Path(
            "test/real_data/games/"
        ).glob("Runde*.json")
    )
    files.sort(key=lambda f: int(re.search(r"\d+", f.stem).group()))
    files = list(
        pathlib.Path(
            "test/real_data/games/"
        ).glob("Runde*.json")
    )
    files.sort(key=lambda f: int(re.search(r"\d+", f.stem).group()))
    games = list()
    for file in files:
        with file.open() as file:
            data = json.load(file)
        games.append(data)
    return games


@pytest.fixture
def courses():
    files = list(pathlib.Path("test/real_data/courses/").glob("Kurs*.json"))
    files = list(pathlib.Path("test/real_data/courses/").glob("Kurs*.json"))
    courses = list()
    for file in files:
        with file.open() as file:
            data = json.load(file)
        courses.append(data)
    return courses


@pytest.fixture
def score_differential():
    return [37.4, 29.6, 24.1, 28.4, 18.8, 31.1, 36.0, 21.7, 15.4, 21.7, 28.6, 46.7]


@pytest.fixture
def EGA_handicap():
    # just 7 for now because this is only ega data
    return [37.0, 32.5, 27.5, 27.5, 23.7, 23.7, 23.8]


@pytest.fixture
def WHS_handicap():
    # only for game 7 to 12
    return [29.3, 28.4, 25.6, 23.9, 23.5, 23.5]


# fixture to insert 21 games
@pytest.fixture
def multiple_games(helper: Helper):
    # Generate mock data with 21 entries
    mock_data: list[dict] = []
    base_date = datetime(2024, 12, 3, 11, 41, 30)
    course_names = ["Womp Womp", "Sunny Links", "Green Meadow", "Pine Valley"]

    for i in range(1, 22):
        mock_data.append(
            {
                "game_id": str(i),
                "handicap_differential": round(random.uniform(0.0, 54.0), 1),
                "courseID": random.choice(course_names),
                "date": (base_date - timedelta(days=i)).isoformat(),
                "shots": [random.randint(3, 6) for _ in range(18)],
            }
        )

    helper.games.insert_multiple(mock_data)
    return helper


def test_addGame(
    helper, games, courses, score_differential, WHS_handicap, EGA_handicap
):
    for course in courses:
        helper.addCourse(
            course["courseID"],
            course["course_rating"],
            course["slope_rating"],
            course["par"],
            course["handicap_stroke_index"],
        )

    print("\n")
    for index, game in enumerate(games):
        courseID = game["courseID"]
        shots = game["shots"]
        nineHole = game["is9Hole"]
        pcc = game["pcc"]
        cba = game["cba"]
        gameDate = game["date"]
        helper.addGame(courseID, shots, nineHole, pcc, cba, gameDate)

        log = helper.hcLog.all()
        log.sort(key=lambda doc: datetime.fromisoformat(doc["date"]), reverse=True)
        lenLog = len(log)

        if index < 7:
            print(
                f"{index} EGA {game["game_id"]} {log[lenLog -1 ]["ega"]} == {EGA_handicap[index]}"
            )

            # assert log[lenLog -1]["ega"] == EGA_handicap[index + 1]
        if index >= 6:
            print(
                f"{index} WHS {game["game_id"]} {log[lenLog -1]["whs"]} == {WHS_handicap[index - 6]}"
            )

            # assert log[lenLog -1]["whs"] == WHS_handicap[index - 6]

    print("====================================")
    games = helper.getLastGames()
    for index, game in enumerate(games):
        print(
            f"Runde {index + 1}: {game["handicap_dif"]} == {score_differential[index]}. 9Hole: {game["is9Hole"]}"
        )

        # assert game["handicap_dif"] == score_differential[index]
