import pytest
import handicapEGA as hc
import json
import pathlib

def test_handicapToCategory():
    assert hc.handicapToCategory(4.0) == 1
    assert hc.handicapToCategory(4.4) == 1
    assert hc.handicapToCategory(4.5) == 2
    assert hc.handicapToCategory(11.4) == 2
    assert hc.handicapToCategory(11.5) == 3
    assert hc.handicapToCategory(18.4) == 3
    assert hc.handicapToCategory(18.5) == 4
    assert hc.handicapToCategory(26.4) == 4
    assert hc.handicapToCategory(26.5) == 5
    assert hc.handicapToCategory(36.0) == 5
    assert hc.handicapToCategory(37.0) == 6
    assert hc.handicapToCategory(54.0) == 6

def test_initialHandicap():
    assert hc.initialHandicap(36, False) == 54
    assert hc.initialHandicap(30, False) == 54
    assert hc.initialHandicap(40, False) == 50
    assert hc.initialHandicap(18, True) == 54
    assert hc.initialHandicap(10, True) == 54
    
def test_roundHalfUp():
    assert hc.roundHalfUp(0.4) == 0
    assert hc.roundHalfUp(0.5) == 1
    assert hc.roundHalfUp(0.05) == 0
    assert hc.roundHalfUp(0.05, 1) == 0.1
    assert hc.roundHalfUp(-0.5) == 0
    
def test_catToLowerBuffer():
    assert hc.catToLowerBuffer(False, 1) == 35
    assert hc.catToLowerBuffer(False, 2) == 34
    assert hc.catToLowerBuffer(False, 3) == 33
    assert hc.catToLowerBuffer(False, 4) == 32
    assert hc.catToLowerBuffer(False, 5) == 31
    assert hc.catToLowerBuffer(True, 2) == 35
    assert hc.catToLowerBuffer(True, 3) == 35
    assert hc.catToLowerBuffer(True, 4) == 34
    assert hc.catToLowerBuffer(True, 5) == 33
    
def test_calculateAdjustment():
    assert hc.calculateAdjustment(36, 54.0, 0, False) == pytest.approx(0)
    assert hc.calculateAdjustment(38, 54.0, 0, False) == pytest.approx(-2.0)
    assert hc.calculateAdjustment(46, 54.0, 0, False) == pytest.approx(-10.0)
    assert hc.calculateAdjustment(37, 37.0, 0, False) == pytest.approx(-1.0)
    assert hc.calculateAdjustment(38, 37.0, 0, False) == pytest.approx(-1.5)
    assert hc.calculateAdjustment(56, 37.0, 0, False) == pytest.approx(-10.5)
    assert hc.calculateAdjustment(77, 37.0, 0, False) == pytest.approx(-18.9)
    assert hc.calculateAdjustment(42, 11.3, 0, False) == pytest.approx(-1.2)
    assert hc.calculateAdjustment(42, 19.1, 0, False) == pytest.approx(-2.0) # EGA p.26
    assert hc.calculateAdjustment(32, 12.0, -1, False) == pytest.approx(0) # EGA p.23
    
def test_playingHandicap():
    assert hc.playingHandicap(False, 36.0, 70.0, 113, 70) == 36.0
    assert hc.playingHandicap(False, 20.0, 70.0, 113, 70) == 20.0
    assert hc.playingHandicap(False, 25.0, 71.2, 115, 72) == 25.0
    assert hc.playingHandicap(False, 37.0, 80.0, 100, 64) == 49.0
    assert hc.playingHandicap(True, 11.8, 35.8, 122, 35) == 7.0     # EGA p.24
    assert hc.playingHandicap(True, 40.0, 35.8, 122, 35) == 22.0
    
def test_playingHandicapDifferential():
    assert hc.playingHandicapDifferential(False, 70.6, 124, 72) == 2
    assert hc.playingHandicapDifferential(False, 68.5, 120, 72) == -1
    assert hc.playingHandicapDifferential(False, 74.4, 133, 72) == 9
    assert hc.playingHandicapDifferential(False, 71.8, 125, 72) == 4

def test_convertToStableford():
    assert hc.convertToStableford([2,2,2,2,2,2,2], [2,2,2,2,2,2,2]) == 14
    assert hc.convertToStableford([2,2,2,2,2,2,2], [0,0,0,0,0,0,0]) == 0
    assert hc.convertToStableford([1,1,2,2,3,3,4], [2,2,2,2,2,2,2]) == 12
    

@pytest.fixture
def game1():
    file = pathlib.Path("test/games/game_1.json")
    with file.open() as file:
        data = json.load(file)
    return data

@pytest.fixture
def game2():
    file = pathlib.Path("test/games/game_2.json")
    with file.open() as file:
        data = json.load(file)
    return data

@pytest.fixture
def course1():
    file = pathlib.Path("test/courses/course_1.json")
    with file.open() as file:
        data = json.load(file)
    return data

@pytest.fixture
def lade1():
    return {
            "shots": [5,6,8,7,6,6,6,6,6,7,6,6,5,6,6,6,5,6],
            "is9Hole": False
    }

@pytest.fixture
def course_lade1():
    return {
        "par": [3,4,4,5,4,4,3,4,4,5,4,4,3,4,4,5,4,4],
        "handicap_stroke_index": [4,16,1,10,7,13,5,17,2,11,8,14,6,18,3,12,9,15],
        "course_rating": 70.9,
        "slope_rating": 115
    }
    
@pytest.fixture
def lade2():
    return {
            "shots": [4,5,5,6,6,5,6,9,5,5,6,6,5,6,6,6,5,6],
            "is9Hole": False
    }

@pytest.fixture
def course_lade3():
    return {
        "par": [3,4,4,5,4,4,3,4,4,5,4,4,3,4,4,5,4,4],
        "handicap_stroke_index": [16,1,10,7,13,4,17,2,11,8,14,5,18,3,12,9,15,6],
        "course_rating": 72.3,
        "slope_rating": 130
    }
    
@pytest.fixture
def lade3():
    return {
            "shots": [4,5,5,6,6,7,4,8,4,5,6,6,5,6,6,6,5,6],
            "is9Hole": False
    }
    
@pytest.fixture
def lade4():
    return {
            "shots": [5,6,6,7,6,6,4,7,6,7,6,6,5,5,6,6,5,6],
            "is9Hole": False
    }

def test_calculateNewHandicap(game1, game2, course1, lade1, course_lade1, lade2, lade3, course_lade3, lade4):
    # own test, painstakingly hand-calculated
    assert hc.calculateNewHandicap(game2, 0, 54.0, course1) == 32.0
    # lade-examples
    assert hc.calculateNewHandicap(lade1, 0, 54.0, course_lade1) == 37.0
    assert hc.calculateNewHandicap(lade2, 0, 37.0, course_lade1) == 32.5
    assert hc.calculateNewHandicap(lade3, 0, 32.5, course_lade3) == 27.5
    assert hc.calculateNewHandicap(lade4, 0, 27.5, course_lade3) == 27.5