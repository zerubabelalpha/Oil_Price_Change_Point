import numpy as np
import matplotlib.pyplot as plt
import arviz as az
from pathlib import Path


def plot_changepoint_results(dates, oil_prices, results, trace, save_path=None):
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    
    # 1. Time series with change point
    axes[0, 0].plot(dates, oil_prices, 'o-', alpha=0.6, markersize=3, 
                    label='Actual Prices', color='darkblue')
    axes[0, 0].axvline(results['change_date'], color='red', linestyle='--', 
                       linewidth=2.5, label=f'Change Point: {results["change_date"]}')
    axes[0, 0].axvspan(results['date_lower'], results['date_upper'], 
                       alpha=0.2, color='red', label='95% Credible Interval')
    axes[0, 0].axhline(results['mu_before_mean'], color='blue', alpha=0.5, 
                       linewidth=2, label=f'Before: ${results["mu_before_mean"]:.2f}')
    axes[0, 0].axhline(results['mu_after_mean'], color='green', alpha=0.5, 
                       linewidth=2, label=f'After: ${results["mu_after_mean"]:.2f}')
    axes[0, 0].set_xlabel('Date', fontsize=11)
    axes[0, 0].set_ylabel('Price (USD)', fontsize=11)
    axes[0, 0].set_title('Oil Prices with Detected Change Point', fontsize=13, fontweight='bold')
    axes[0, 0].legend(fontsize=9, loc='best')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Posterior distribution of change point
    axes[0, 1].hist(results['tau_samples'], bins=50, edgecolor='black', alpha=0.7, color='steelblue')
    axes[0, 1].axvline(results['tau_mean'], color='red', linestyle='--', 
                       linewidth=2, label=f'Mean: Day {results["tau_mean"]}')
    axes[0, 1].axvline(results['tau_median'], color='orange', linestyle='--', 
                       linewidth=2, label=f'Median: Day {results["tau_median"]}')
    axes[0, 1].set_xlabel('Day Index', fontsize=11)
    axes[0, 1].set_ylabel('Frequency', fontsize=11)
    axes[0, 1].set_title('Posterior Distribution of Change Point (τ)', fontsize=13, fontweight='bold')
    axes[0, 1].legend(fontsize=9)
    axes[0, 1].grid(True, alpha=0.3, axis='y')
    
    # 3. Price distributions before/after
    axes[1, 0].hist(results['mu_before_samples'], bins=30, alpha=0.6, 
                    label='Before', color='blue', edgecolor='black')
    axes[1, 0].hist(results['mu_after_samples'], bins=30, alpha=0.6, 
                    label='After', color='green', edgecolor='black')
    axes[1, 0].axvline(results['mu_before_mean'], color='darkblue', 
                       linestyle='--', linewidth=2)
    axes[1, 0].axvline(results['mu_after_mean'], color='darkgreen', 
                       linestyle='--', linewidth=2)
    axes[1, 0].set_xlabel('Price (USD)', fontsize=11)
    axes[1, 0].set_ylabel('Frequency', fontsize=11)
    axes[1, 0].set_title('Price Level Distributions', fontsize=13, fontweight='bold')
    axes[1, 0].legend(fontsize=9)
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # 4. Posterior predictive check
    az.plot_ppc(trace, ax=axes[1, 1], num_pp_samples=100)
    axes[1, 1].set_title('Posterior Predictive Check', fontsize=13, fontweight='bold')
    axes[1, 1].set_xlabel('Price (USD)', fontsize=11)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved comprehensive results plot to {save_path}")
    
    plt.show()


def plot_trace_diagnostics(trace, save_path=None):
    
    az.plot_trace(trace, var_names=['tau', 'mu_before', 'mu_after', 'sigma_before', 'sigma_after'],
                  compact=True, figsize=(14, 10))
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved trace diagnostics plot to {save_path}")
    
    plt.show()


def plot_regime_comparison(dates, oil_prices, results, save_path=None):
    
    tau = results['tau_mean']
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Split data into before and after
    dates_before = dates[:tau]
    prices_before = oil_prices[:tau]
    dates_after = dates[tau:]
    prices_after = oil_prices[tau:]
    
    # Plot 1: Time series with regimes highlighted
    axes[0].plot(dates_before, prices_before, 'o-', color='blue', alpha=0.7, 
                 markersize=3, label='Before Change Point')
    axes[0].plot(dates_after, prices_after, 'o-', color='green', alpha=0.7, 
                 markersize=3, label='After Change Point')
    axes[0].axhline(results['mu_before_mean'], color='darkblue', linestyle='--', 
                    linewidth=2, alpha=0.7, label=f'Mean Before: ${results["mu_before_mean"]:.2f}')
    axes[0].axhline(results['mu_after_mean'], color='darkgreen', linestyle='--', 
                    linewidth=2, alpha=0.7, label=f'Mean After: ${results["mu_after_mean"]:.2f}')
    axes[0].axvline(results['change_date'], color='red', linestyle='--', 
                    linewidth=2.5, label='Change Point')
    axes[0].set_xlabel('Date', fontsize=12)
    axes[0].set_ylabel('Price (USD)', fontsize=12)
    axes[0].set_title('Price Regimes Before and After Change Point', fontsize=14, fontweight='bold')
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Box plots comparison
    bp = axes[1].boxplot([prices_before, prices_after], 
                          labels=['Before Change', 'After Change'],
                          patch_artist=True,
                          widths=0.6)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['boxes'][1].set_facecolor('lightgreen')
    
    axes[1].set_ylabel('Price (USD)', fontsize=12)
    axes[1].set_title('Price Distribution Comparison', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    # Add statistics text
    stats_text = f"Before: μ=${results['mu_before_mean']:.2f}, σ=${results['sigma_before_mean']:.2f}\n"
    stats_text += f"After: μ=${results['mu_after_mean']:.2f}, σ=${results['sigma_after_mean']:.2f}\n"
    stats_text += f"Change: ${results['price_change']:.2f} ({results['price_change_pct']:+.1f}%)"
    axes[1].text(0.02, 0.98, stats_text, transform=axes[1].transAxes,
                 fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved regime comparison plot to {save_path}")
    
    plt.show()
