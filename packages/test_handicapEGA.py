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
def games():
    files = list(pathlib.Path("test/real_data/games").glob("Runde*.json"))
    runden = dict()
    for file in files:
        with file.open() as file:
            data = json.load(file)
        runden[data["game_id"]] = data
    return runden

@pytest.fixture
def courses():
    files = list(pathlib.Path("test/real_data/courses").glob("Kurs*.json"))
    kurse = dict()
    for file in files:
        with file.open() as file:
            data = json.load(file)
        kurse[data["courseID"]] = data
    return kurse

@pytest.fixture
def handicap_before():
    # just 7 for now because this is only ega data
    return [54, 37, 32.5, 27.5, 27.5, 23.7, 23.7]

@pytest.fixture
def handicap_after():
    return [37, 32.5, 27.5, 27.5, 23.7, 23.7, 23.8]
    # return [37, 32.5, 27.5, 27.5, 23.6, 23.7, 23.7] # correct as per our calculation
    
def test_calculateNewHandicap(games, courses, handicap_before, handicap_after):
    # this is just to ensure oder of game 1 to 12 since it would sort as game 1, 10, 11, 12, 2, 3 ...
    # oh but we only have data for 7 games so it doesn't matter lol
    # leaving this in in case we get ega data for the other games
    rundenliste = ["Runde " + str(i+1) for i in range(7)]
    for i, runde in enumerate(rundenliste):
        assert hc.calculateNewHandicap(games[runde], int(games[runde]["pcc"]), handicap_before[i], courses[games[runde]["courseID"]]) == handicap_after[i]