import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from statsmodels.tsa.stattools import adfuller



def plot_time_series(df, save_path=None):
    
    plt.figure(figsize=(14, 6))
    plt.plot(df['Date'], df['Price'], label='Oil Price', color='darkblue', alpha=0.7, linewidth=1.5)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price (USD)', fontsize=12)
    plt.title('Historical Oil Prices', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved time series plot to {save_path}")
    
    plt.show()


def calculate_statistics(df):
    
    stats = {
        'mean': df['Price'].mean(),
        'median': df['Price'].median(),
        'std': df['Price'].std(),
        'min': df['Price'].min(),
        'max': df['Price'].max(),
        'range': df['Price'].max() - df['Price'].min(),
        'q25': df['Price'].quantile(0.25),
        'q75': df['Price'].quantile(0.75)
    }
    
    print("\n" + "="*50)
    print("DESCRIPTIVE STATISTICS")
    print("="*50)
    print(f"Mean:       ${stats['mean']:.2f}")
    print(f"Median:     ${stats['median']:.2f}")
    print(f"Std Dev:    ${stats['std']:.2f}")
    print(f"Min:        ${stats['min']:.2f}")
    print(f"Max:        ${stats['max']:.2f}")
    print(f"Range:      ${stats['range']:.2f}")
    print(f"Q25:        ${stats['q25']:.2f}")
    print(f"Q75:        ${stats['q75']:.2f}")
    print("="*50)
    
    return stats


def plot_distribution(df, save_path=None):
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histogram
    axes[0].hist(df['Price'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    axes[0].axvline(df['Price'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: ${df["Price"].mean():.2f}')
    axes[0].axvline(df['Price'].median(), color='green', linestyle='--', linewidth=2, label=f'Median: ${df["Price"].median():.2f}')
    axes[0].set_xlabel('Price (USD)', fontsize=12)
    axes[0].set_ylabel('Frequency', fontsize=12)
    axes[0].set_title('Price Distribution', fontsize=14, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Box plot
    axes[1].boxplot(df['Price'], vert=True, patch_artist=True,
                    boxprops=dict(facecolor='lightblue', alpha=0.7),
                    medianprops=dict(color='red', linewidth=2))
    axes[1].set_ylabel('Price (USD)', fontsize=12)
    axes[1].set_title('Price Box Plot', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved distribution plot to {save_path}")
    
    plt.show()


def plot_volatility(df, window=30, save_path=None):
    
    # Calculate rolling statistics
    df['rolling_mean'] = df['Price'].rolling(window=window).mean()
    df['rolling_std'] = df['Price'].rolling(window=window).std()
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Price with rolling mean
    axes[0].plot(df['Date'], df['Price'], label='Price', alpha=0.5, color='darkblue')
    axes[0].plot(df['Date'], df['rolling_mean'], label=f'{window}-day Moving Average', 
                 color='red', linewidth=2)
    axes[0].set_xlabel('Date', fontsize=12)
    axes[0].set_ylabel('Price (USD)', fontsize=12)
    axes[0].set_title('Oil Price with Moving Average', fontsize=14, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Rolling volatility
    axes[1].plot(df['Date'], df['rolling_std'], label=f'{window}-day Rolling Std Dev', 
                 color='darkgreen', linewidth=2)
    axes[1].set_xlabel('Date', fontsize=12)
    axes[1].set_ylabel('Volatility (USD)', fontsize=12)
    axes[1].set_title('Rolling Volatility', fontsize=14, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved volatility plot to {save_path}")
    
    plt.show()


def calculate_log_returns(df):
    """
    Calculate log returns: log(price_t) - log(price_{t-1})
    """
    df = df.copy()
    # Ensure Price is float and handle any non-positive values
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df = df[df['Price'] > 0]
    
    df['Log_Price'] = np.log(df['Price'])
    df['Log_Returns'] = df['Log_Price'].diff()
    
    # Remove the first row which will be NaN
    return df.dropna(subset=['Log_Returns'])


def check_stationarity(series):
    """
    Perform Augmented Dickey-Fuller test for stationarity
    """
    print("\n" + "="*50)
    print("STATIONARITY TEST (ADF)")
    print("="*50)
    
    result = adfuller(series)
    print(f'ADF Statistic: {result[0]:.4f}')
    print(f'p-value: {result[1]:.4e}')
    print('Critical Values:')
    for key, value in result[4].items():
        print(f'   {key}: {value:.3f}')
    
    is_stationary = result[1] < 0.05
    if is_stationary:
        print("\n[OK] Result: The series is STATIONARY (reject null hypothesis)")
    else:
        print("\n[WARN] Result: The series is NON-STATIONARY (fail to reject null hypothesis)")
    print("="*50)
    
    return result


def plot_log_returns(df, save_path=None):
    """
    Plot log returns to observe volatility clustering
    """
    plt.figure(figsize=(14, 6))
    plt.plot(df['Date'], df['Log_Returns'], color='purple', alpha=0.7, linewidth=1)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Log Returns', fontsize=12)
    plt.title('Oil Price Log Returns (Volatility Clustering)', fontsize=14, fontweight='bold')
    plt.axhline(0, color='black', linestyle='--', alpha=0.3)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved log returns plot to {save_path}")
    
    plt.show()
