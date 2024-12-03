from tempfile import TemporaryDirectory
import pytest
from golfDB import Golf

# Fixture to set up and tear down the temporary database
@pytest.fixture
def temp_db():
    with TemporaryDirectory() as temp_dir:
        db_path = f"{temp_dir}/test_db.json"
        db = Golf(db_path)
        yield db
        db.close()

# Fixture to insert mock game data
@pytest.fixture
def mock_game_data(temp_db):
    mock_data = [
        {'id': 1, 'date': '2024-12-01', 'name': 'Game 1'},
        {'id': 2, 'date': '2024-11-30', 'name': 'Game 2'},
        {'id': 3, 'date': '2024-11-29', 'name': 'Game 3'}
    ]
    temp_db.insert_multiple(mock_data)
    return temp_db

# Fixture to insert mock course data
@pytest.fixture
def mock_course_data(temp_db):
    mock_data = [
        {'id': 1, 'date': '2024-12-01', 'name': 'Game 1'},
        {'id': 2, 'date': '2024-11-30', 'name': 'Game 2'},
        {'id': 3, 'date': '2024-11-29', 'name': 'Game 3'}
    ]
    temp_db.insert_multiple(mock_data)
    return temp_db

def test_insert_from_dir(temp_db):
    temp_db.insertFromDir("../data/courses/")
    data = temp_db.all()
    assert len(data) > 0  # Adjust assertion based on expected results

def test_add_game(temp_db):
    result = temp_db.addGame()
    # Add specific assertions for `result` based on its expected value or side effects

def test_get_games(mock_game_data):
    result = mock_game_data.getGames()
    assert len(result) == 3  # Replace with actual expected results
