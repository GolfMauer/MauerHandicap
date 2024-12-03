from tempfile import TemporaryDirectory
import unittest
from golfDB import Golf

class TestData(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory and database
        self.temp_dir = TemporaryDirectory()
        self.db_path = f"{self.temp_dir.name}/test_db.json"
        self.db = Golf(self.db_path)
        
    def insertMockGameData(self):
        # Insert mock data
        self.mock_data = [
            {'id': 1, 'date': '2024-12-01', 'name': 'Game 1'},
            {'id': 2, 'date': '2024-11-30', 'name': 'Game 2'},
            {'id': 3, 'date': '2024-11-29', 'name': 'Game 3'}
        ]
        self.db.insert_multiple(self.mock_data)
    
    def insertMockCourseData(self):
        # Insert mock data
        self.mock_data = [
            {'id': 1, 'date': '2024-12-01', 'name': 'Game 1'},
            {'id': 2, 'date': '2024-11-30', 'name': 'Game 2'},
            {'id': 3, 'date': '2024-11-29', 'name': 'Game 3'}
        ]
        self.db.insert_multiple(self.mock_data)

    def tearDown(self):
        # Close and clean up the database
        self.db.close()
        self.temp_dir.cleanup()
    
    def test_insertFromDir(self):
        db = Golf()
        db.insertFromDir("../data/courses/")
        data = db.all()
        print(data)
    
    
    def test_addGame(self):
        db = Golf()
        result = db.addGame()
    
    
    def test_getGame(self):
        db = Golf()
        result = db.getGames()

if __name__ == "__main__":
    unittest.main()