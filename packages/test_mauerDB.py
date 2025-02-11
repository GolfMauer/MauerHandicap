from datetime import datetime, timedelta
import random
import re
from tempfile import TemporaryDirectory
import json
from os import listdir
from os.path import isfile, join

import pytest
from mauerDB import MauerDB


# Fixture to set up and tear down the temporary database
@pytest.fixture
def temp_db():
    with TemporaryDirectory() as temp_dir:
        db_path = f"{temp_dir}/test_db.json"
        db = MauerDB(db_path)
        yield db
        db.close()

# Fixture to insert one game
@pytest.fixture
def one_game(temp_db):
    mock_data = [
        {
            "game_id": "1",
            "handicap": 0.0, 
            "courseID": "Womp Womp",
            "date": "2024-12-03T11:41:30.013870",
            "shots": [3, 4, 5, 3, 4, 5, 3, 3, 4, 3, 3, 3, 3, 5, 4, 3, 4, 5]
        }
    ]
    temp_db.insert_multiple(mock_data)
    return temp_db


#fixture to insert 21 games
@pytest.fixture
def multiple_games(temp_db):
    # Generate mock data with 21 entries
    mock_data = []
    base_date = datetime(2024, 12, 3, 11, 41, 30)
    course_names = ["Womp Womp", "Sunny Links", "Green Meadow", "Pine Valley"]
    
    for i in range(1, 22):
        mock_data.append({
            "game_id": str(i),
            "handicap": round(random.uniform(0.0, 54.0), 1),
            "courseID": random.choice(course_names),
            "date": (base_date - timedelta(days=i)).isoformat(),
            "shots": [random.randint(3, 6) for _ in range(18)]
        })

    temp_db.insert_multiple(mock_data)
    return temp_db


def test_insert_from_dir(temp_db):
    path = "test/courses/"
    temp_db.insertFromDir(path)
    db_data = temp_db.all()
    arr = []
    
    files = [file for file in listdir(path) if isfile(join(path, file))]

    for file in files:
        json_file = open(path + file, "r")
        data = json.load(json_file)
        arr.append(data)

    assert db_data == arr 


def test_add_course(temp_db):
    id = "Nimons Boulevard"
    courseRating = 67
    slopeRating = 113
    par = [3, 4, 5]
    temp_db.addCourse(id, courseRating, slopeRating, par)
    
    data = temp_db.all()
    data = data[0]
    
    assert data["course_id"] == id
    assert data["course_rating"] == courseRating
    assert data["slope_rating"] == slopeRating
    assert data["par"] == par


def test_add_course_slope_outOfBounds(temp_db):
    id = "Nimons Boulevard"
    courseRating = 67
    slopeRating = 0 # Invalid slope
    par = [3, 4, 5]

    expected_message = f"Invalid parameter: {slopeRating}. Must be between 55 and 155."
    with pytest.raises(ValueError, match=re.escape(expected_message)):
        temp_db.addCourse(id, courseRating, slopeRating, par)


def test_add_game_datetime(temp_db):
    date = datetime.now()
    handicap = 15.3
    id = "Womp Womp"
    shots = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    pcc = 2.0
    uuid = temp_db.addGame(handicap, id, date, shots, pcc)
    

    data = temp_db.all()
    data = data[0]

    assert data["handicap"] == handicap 
    assert data["courseID"] == id 
    assert data["date"] == date.isoformat()
    assert data["shots"] == shots
    assert uuid != ""
    assert data["pcc"] == pcc

def test_add_game_isoString(temp_db):
    date = datetime.now().isoformat()
    handicap = 15.3
    id = "Womp Womp"
    shots = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    pcc = 2.0
    uuid = temp_db.addGame(handicap, id, date, shots, pcc)
    

    data = temp_db.all()
    data = data[0]

    assert data["handicap"] == handicap 
    assert data["courseID"] == id 
    assert data["date"] == date
    assert data["shots"] == shots
    assert uuid != ""
    assert data["pcc"] == pcc


def test_get_games_empty (temp_db):
    result = temp_db.getGames()
    assert result == []


def test_get_games_m_to_large (one_game):
    result = one_game.getGames(0, 3)
    assert len(result) != 0 and len(result) < 3

def test_get_games_n_to_large (one_game):
    result = one_game.getGames(3, 4)
    assert result == []

def test_get_games_n_equal_m (one_game):
    result = one_game.getGames(0, 0)
    assert len(result) == 1


def test_get_games_n_larger_m (multiple_games):
    result = multiple_games.getGames(3, 0)
    assert len(result) == 1

def test_get_games(multiple_games):
    result = multiple_games.getGames()
    assert len(result) == 20

def test_get_games_sorted(multiple_games):
    result = multiple_games.getGames()

    sorted_games = sorted(
        result, 
        key=lambda x: datetime.fromisoformat(x['date']), 
        reverse=True)
    
    assert result == sorted_games

def test_get_games_slicing(multiple_games):
    result = multiple_games.getGames(3, 6)
    games = multiple_games.getGames()
    assert result == games[3:7]
