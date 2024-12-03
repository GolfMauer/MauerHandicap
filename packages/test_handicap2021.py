import pytest
import handicap2021

def test_handicap():
    result = handicap2021.handicap()
    # Add appropriate assertions based on the expected result
    assert result is not None  # Replace with actual assertion logic

def test_handicap_differential():
    result = handicap2021.handicapDifferential()
    # Add appropriate assertions
    assert result is not None  # Replace with actual assertion logic

def test_handicap_differential_net():
    result = handicap2021.handicapDifferentialNet()
    # Add appropriate assertions
    assert result is not None  # Replace with actual assertion logic

def test_handicap_differential_stableford():
    result = handicap2021.handicapDifferentialStableford()
    # Add appropriate assertions
    assert result is not None  # Replace with actual assertion logic
