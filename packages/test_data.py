import unittest
import packages.data as data

class TestData(unittest.TestCase):
    def test_insertFromDir(self):
        db = data.Golf
        result = db.insertFromDir
    
    
    def test_addGame(self):
        db = data.Golf
        result = db.addGame()
    
    
    def test_getGame(self):
        db = data.Golf
        result = db.getGames()

if __name__ == "__main__":
    unittest.main()