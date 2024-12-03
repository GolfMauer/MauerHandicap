import unittest
import handicap2021

shots = [5, 5 , 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5] #example shots with 18 entries
games = [shots, shots, shots]

class TestHandicap2021(unittest.TestCase):
    def test_handicap(self):
        result = handicap2021.handicap()
    
    
    def test_handicapDifferential():
        result = handicap2021.handicapDifferential()
    
    
    def test_handicapDifferentialNet():
        result = handicap2021.handicapDifferentialNet
    
    
    def test_handicapDifferentialStableford():
        result = handicap2021.handicapDifferentialStableford

if __name__ == "__main__":
    unittest.main()