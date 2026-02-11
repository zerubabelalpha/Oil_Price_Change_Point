import numpy as np
import matplotlib.pyplot as plt
import arviz as az
import pandas as pd
from pathlib import Path

def plot_changepoint_results(dates, oil_prices, results, trace, events_df=None, save_path=None):
    """
    Plots the results of the single change point detection.
    Overlays the detected change point and optionally historical events.
    """
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    
    # 1. Time series with change point
    axes[0, 0].plot(dates, oil_prices, '-', alpha=0.4, label='Actual Prices', color='gray')
    
    # Plot detected CP
    cp_date = pd.Timestamp(results['change_date'])
    axes[0, 0].axvline(cp_date, color='red', linestyle='--', linewidth=2, label=f'Change Point: {cp_date.strftime("%Y-%m-%d")}')
    axes[0, 0].axvspan(pd.Timestamp(results['date_lower']), pd.Timestamp(results['date_upper']), alpha=0.2, color='red', label='95% Credible Interval')
    
    # Plot Regime Means
    tau_mean = results['tau_mean']
    axes[0, 0].hlines(results['mu_before_mean'], dates[0], dates[tau_mean], color='blue', linewidth=3, label='Before Mean')
    axes[0, 0].hlines(results['mu_after_mean'], dates[tau_mean], dates[-1], color='green', linewidth=3, label='After Mean')

    # Overlay Events if provided
    if events_df is not None:
        # Work with a copy and ensure Start_Date is datetime for comparison and plotting
        events_df = events_df.copy()
        events_df['Start_Date'] = pd.to_datetime(events_df['Start_Date'])
        
        mask = (events_df['Start_Date'] >= pd.Timestamp(dates[0])) & \
               (events_df['Start_Date'] <= pd.Timestamp(dates[-1]))
        relevant_events = events_df[mask]
        
        y_max = oil_prices.max()
        for _, row in relevant_events.iterrows():
            axes[0, 0].annotate(row['Event_Name'], xy=(row['Start_Date'], y_max), xytext=(5, 5),
                                 textcoords='offset points', rotation=90, va='bottom', fontsize=8,
                                 arrowprops=dict(arrowstyle='->', alpha=0.3))

    axes[0, 0].set_title('Oil Prices with Detected Change Point and Events', fontsize=14, fontweight='bold')
    axes[0, 0].legend(fontsize=8, loc='best')
    axes[0, 0].grid(True, alpha=0.2)
    
    # 2. Posterior distribution of tau
    axes[0, 1].hist(results['tau_samples'], bins=100, alpha=0.5, color='red', density=True)
    axes[0, 1].set_title('Posterior Distribution of Change Point (tau)', fontsize=14, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.2)
    
    # 3. Regime Mus
    axes[1, 0].hist(results['mu_before_samples'], bins=50, alpha=0.5, label='mu_before', density=True)
    axes[1, 0].hist(results['mu_after_samples'], bins=50, alpha=0.5, label='mu_after', density=True)
    axes[1, 0].set_title('Price Level Distributions', fontsize=14, fontweight='bold')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.2)
    
    # 4. Posterior predictive check
    az.plot_ppc(trace, ax=axes[1, 1])
    axes[1, 1].set_title('Posterior Predictive Check', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_trace_diagnostics(trace, save_path=None):
    az.plot_trace(trace, var_names=['mu_before', 'mu_after', 'sigma_before', 'sigma_after'], compact=True)
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_regime_comparison(dates, oil_prices, results, save_path=None):
    fig, ax = plt.subplots(figsize=(14, 6))
    t = results['tau_mean']
    ax.plot(dates[:t], oil_prices[:t], label='Regime 1', alpha=0.8)
    ax.plot(dates[t:], oil_prices[t:], label='Regime 2', alpha=0.8)
    ax.axhline(results['mu_before_mean'], color='blue', linestyle='--', alpha=0.5)
    ax.axhline(results['mu_after_mean'], color='green', linestyle='--', alpha=0.5)
    ax.set_title('Price Regime Comparison', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.2)
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
