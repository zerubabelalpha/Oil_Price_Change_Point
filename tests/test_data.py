
import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'src'))

from data import clean_data, prepare_data_for_modeling

@pytest.fixture
def sample_data():
    dates = pd.date_range(start='2020-01-01', periods=10, freq='D')
    prices = [50.0, 52.0, np.nan, 55.0, 53.0, 58.0, 60.0, 62.0, 61.0, 65.0]
    return pd.DataFrame({'Date': dates, 'Price': prices})

def test_clean_data(sample_data):
    # Test that NaN values are handled (dropped or filled, assuming implementation drops)
    # The current implementation drops NaNs
    df_clean = clean_data(sample_data)
    assert len(df_clean) == 9  # One NaN should be removed
    assert df_clean['Price'].isna().sum() == 0
    assert 'Date' in df_clean.columns
    assert 'Price' in df_clean.columns

def test_prepare_data_for_modeling(sample_data):
    df_clean = clean_data(sample_data)
    data_dict = prepare_data_for_modeling(df_clean)
    
    assert 'n_days' in data_dict
    assert 'oil_prices' in data_dict
    assert 'historical_mean' in data_dict
    assert data_dict['n_days'] == 9
    assert len(data_dict['oil_prices']) == 9
    assert np.isclose(data_dict['historical_mean'], df_clean['Price'].mean())

def test_data_types(sample_data):
    df_clean = clean_data(sample_data)
    data_dict = prepare_data_for_modeling(df_clean)
    
    assert isinstance(data_dict['n_days'], int)
    assert isinstance(data_dict['oil_prices'], np.ndarray)
