import pytest
import handicapWHS as hc

import json
import pathlib

@pytest.fixture
def games():
    files = list(pathlib.Path("test").glob("Runde*.json"))
    game = list()
    for file in files:
        with file.open() as file:
            data = json.load(file)
        game.append(data)
    return game

@pytest.fixture
def courses():
    files = list(pathlib.Path("test").glob("Kurs*.json"))
    courses = dict()
    for file in files:
        with file.open() as file:
            data = json.load(file)
        courses[data["courseID"]] = data
    return courses

@pytest.fixture
def score_differential():
    return [ 37.4, 29.6, 24.1, 28.4, 18.8, 31.1, 36, 21.7, 15.4, 21.7, 28.6, 46,7 ]

@pytest.fixture
def handicap_before():
    # only for game 8 to 12
    return [ 29.3, 28.4 ,25.6 ,23.9 , 23.5 ]

@pytest.fixture
def handicap_after():
    return [ 28.4 ,25.6 ,23.9 , 23.5, 23.5 ]

def test_handicapDifferential(games, courses, score_differential):
    for i, game in enumerate(games):
        course = courses[game["courseID"]]
        assert score_differential[i] == hc.handicapDifferential(game, course, hci)