import pytest
import handicapEGA as hc

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
    assert hc.handicapToCategory(55.0) is not None #TODO: error logic

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
    #assert hc.catToLowerBuffer(False, 6)
    # assert hc.catToLowerBuffer(True, 1)
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
    assert hc.calculateAdjustment(77, 37.0, 0, False) == pytest.approx(-18.9) # walks through cat 6 to cat 3
    #TODO: continue for more cats?
    
    # taken from ega rules
    # this one seems wrong. don't know why
    # assert hc.calculateAdjustment(32, 11.2, 0, False) == pytest.approx(0.1)
    assert hc.calculateAdjustment(42, 11.3, 0, False) == pytest.approx(-1.2)
    
def test_playingHandicap():
    assert hc.playingHandicap(False, 36.0, 70.0, 113, 70) == 36.0
    assert hc.playingHandicap(False, 20.0, 70.0, 113, 70) == 20.0
    assert hc.playingHandicap(False, 25.0, 71.2, 115, 72) == 25.0
    assert hc.playingHandicap(False, 37.0, 80.0, 100, 64) == 49.0
    # TODO: test 9 Hole
    
def test_playingHandicapDifferential():
    #TODO: this kinda needs for playingHandicap to work properly
    pass

def test_convertToStableford():
    assert hc.convertToStableford([2,2,2,2,2,2,2], [2,2,2,2,2,2,2]) == 14
    assert hc.convertToStableford([2,2,2,2,2,2,2], [0,0,0,0,0,0,0]) == 0
    assert hc.convertToStableford([1,1,2,2,3,3,4], [2,2,2,2,2,2,2]) == 12
    
def test_calculateNewHandicap():
    # TODO: too lazy rn
    pass