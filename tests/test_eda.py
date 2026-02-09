
import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'src'))

from eda import calculate_statistics

@pytest.fixture
def sample_df():
    dates = pd.date_range(start='2020-01-01', periods=5)
    prices = [10.0, 20.0, 30.0, 40.0, 50.0]
    return pd.DataFrame({'Date': dates, 'Price': prices})

def test_calculate_statistics(sample_df):
    stats = calculate_statistics(sample_df)
    
    assert 'mean' in stats
    assert 'std' in stats
    assert 'min' in stats
    assert 'max' in stats
    
    assert stats['mean'] == 30.0
    assert stats['min'] == 10.0
    assert stats['max'] == 50.0
    # std of [10, 20, 30, 40, 50] is 15.811...
    assert np.isclose(stats['std'], 15.811388)

def test_calculate_statistics_empty():
    empty_df = pd.DataFrame({'Date': [], 'Price': []})
    # Depending on implementation, this might raise error or return NaNs
    # Just checking it doesn't crash immediately is a good start, 
    # but let's assume valid input for now or check if it handles it gracefully
    try:
        stats = calculate_statistics(empty_df)
        assert pd.isna(stats['mean']) or stats['mean'] == 0
    except (ValueError, KeyError):
        pass # Acceptable behavior for empty input
