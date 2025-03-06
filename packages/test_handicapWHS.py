import pytest
import packages.handicapWHS as handicapWHS

from packages.helper import MauerDB
from datetime import datetime, timedelta
from tempfile import TemporaryDirectory
import random

coursePath = "./test/courses"
gamesPath = "./test/games"

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
            "handicap_differential": 0.0, 
            "courseID": "Womp Womp",
            "date": "2024-12-03T11:41:30.013870",
            "shots": [3, 4, 5, 3, 4, 5, 3, 3, 4, 3, 3, 3, 3, 5, 4, 3, 4, 5]
        }
    ]
    games = temp_db.table('games')
    courses = temp_db.table('courses')
    courses.insert_from_dir(coursePath)
    games.insert_multiple(mock_data)
    return temp_db

#fixture to insert 3 games
@pytest.fixture
def three_games(temp_db):
    # Generate mock data with 3 entries
    mock_data = []
    base_date = datetime(2024, 12, 3, 11, 41, 30)
    course_names = ["Womp Womp", "Sunny Links", "Green Meadow", "Pine Valley"]
    
    for i in range(1, 4):
        mock_data.append({
            "game_id": str(i),
            "handicap_differential": round(random.uniform(0.0, 54.0), 1),
            "courseID": random.choice(course_names),
            "date": (base_date - timedelta(days=i)).isoformat(),
            "shots": [random.randint(3, 6) for _ in range(18)]
        })

    games = temp_db.table('games')
    courses = temp_db.table('courses')
    courses.insert_from_dir(coursePath)
    games.insert_multiple(mock_data)
    return temp_db


#fixture to insert 4 games
@pytest.fixture
def four_games(temp_db):
    # Generate mock data with 4 entries
    mock_data = []
    base_date = datetime(2024, 12, 3, 11, 41, 30)
    course_names = ["Womp Womp", "Sunny Links", "Green Meadow", "Pine Valley"]
    
    for i in range(1, 5):
        mock_data.append({
            "game_id": str(i),
            "handicap_differential": round(random.uniform(0.0, 54.0), 1),
            "courseID": random.choice(course_names),
            "date": (base_date - timedelta(days=i)).isoformat(),
            "shots": [random.randint(3, 6) for _ in range(18)]
        })

    games = temp_db.table('games')
    courses = temp_db.table('courses')
    courses.insert_from_dir(coursePath)
    games.insert_multiple(mock_data)
    return temp_db


#fixture to insert 5 games
@pytest.fixture
def five_games(temp_db):
    # Generate mock data with 5 entries
    mock_data = []
    base_date = datetime(2024, 12, 3, 11, 41, 30)
    course_names = ["Womp Womp", "Sunny Links", "Green Meadow", "Pine Valley"]
    
    for i in range(1, 6):
        mock_data.append({
            "game_id": str(i),
            "handicap_differential": round(random.uniform(0.0, 54.0), 1),
            "courseID": random.choice(course_names),
            "date": (base_date - timedelta(days=i)).isoformat(),
            "shots": [random.randint(3, 6) for _ in range(18)]
        })

    games = temp_db.table('games')
    courses = temp_db.table('courses')
    courses.insert_from_dir(coursePath)
    games.insert_multiple(mock_data)
    return temp_db


#fixture to insert 6 games
@pytest.fixture
def six_games(temp_db):
    # Generate mock data with 6 entries
    mock_data = []
    base_date = datetime(2024, 12, 3, 11, 41, 30)
    course_names = ["Womp Womp", "Sunny Links", "Green Meadow", "Pine Valley"]
    
    for i in range(1, 7):
        mock_data.append({
            "game_id": str(i),
            "handicap_differential": round(random.uniform(0.0, 54.0), 1),
            "courseID": random.choice(course_names),
            "date": (base_date - timedelta(days=i)).isoformat(),
            "shots": [random.randint(3, 6) for _ in range(18)]
        })

    games = temp_db.table('games')
    courses = temp_db.table('courses')
    courses.insert_from_dir(coursePath)
    games.insert_multiple(mock_data)
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
            "handicap_differential": round(random.uniform(0.0, 54.0), 1),
            "courseID": random.choice(course_names),
            "date": (base_date - timedelta(days=i)).isoformat(),
            "shots": [random.randint(3, 6) for _ in range(18)]
        })

    games = temp_db.table('games')
    courses = temp_db.table('courses')
    courses.insert_from_dir(coursePath)
    games.insert_multiple(mock_data)
    return temp_db



def test_handicap_smaller54holes(one_game):
    result = handicapWHS.handicap()
    # Add appropriate assertions based on the expected result
    assert result is not None  # Replace with actual assertion logic


def test_handicap_3_games(three_games):
    result = handicapWHS.handicap()
    # Add appropriate assertions based on the expected result
    assert result is not None  # Replace with actual assertion logic


def test_handicap_4_games(four_games):
    result = handicapWHS.handicap()
    # Add appropriate assertions based on the expected result
    assert result is not None  # Replace with actual assertion logic

def test_handicap_5_games(five_games):
    result = handicapWHS.handicap()
    # Add appropriate assertions based on the expected result
    assert result is not None  # Replace with actual assertion logic


def test_handicap_6_games(six_games):
    result = handicapWHS.handicap()
    # Add appropriate assertions based on the expected result
    assert result is not None  # Replace with actual assertion logic

def test_handicap_21_games(multiple_games):
    result = handicapWHS.handicap()
    # Add appropriate assertions based on the expected result
    assert result is not None  # Replace with actual assertion logic


def test_handicap_differential():
    result = handicapWHS.handicapDifferential()
    # Add appropriate assertions
    assert 1 == 1  # Replace with actual assertion logic
