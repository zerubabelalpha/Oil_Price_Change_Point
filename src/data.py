import pandas as pd
import numpy as np
from pathlib import Path


def load_oil_data(filepath):
   
    df = pd.read_csv(filepath)
    # Parse dates with mixed formats (e.g. 20-May-87 and Apr 22, 2020)
    # using format='mixed' allows pandas to infer the format for each element
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, format='mixed')
    
    # Fix potential future years (e.g. 2087 -> 1987) if mapping went to future
    current_year = pd.Timestamp.now().year
    mask = df['Date'].dt.year > current_year
    if mask.any():
        df.loc[mask, 'Date'] = df.loc[mask, 'Date'].apply(lambda x: x.replace(year=x.year - 100))
        
    return df


def clean_data(df):
   
    # Sort by date
    df = df.sort_values('Date').reset_index(drop=True)
    
    # Handle missing values using forward fill
    df['Price'] = df['Price'].fillna(method='ffill')
    
    # If there are still missing values at the start, use backward fill
    df['Price'] = df['Price'].fillna(method='bfill')
    
    # Remove any remaining rows with missing values
    df = df.dropna()
    
    return df


def prepare_data_for_modeling(df):
   
    oil_prices = df['Price'].values
    dates = df['Date'].values
    n_days = len(oil_prices)
    
    historical_mean = oil_prices.mean()
    historical_std = oil_prices.std()
    
    return {
        'oil_prices': oil_prices,
        'dates': dates,
        'n_days': n_days,
        'historical_mean': historical_mean,
        'historical_std': historical_std
    }
