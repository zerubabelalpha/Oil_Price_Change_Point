import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path



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
