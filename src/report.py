"""
Report Generator Module
Creates markdown report with analysis findings
"""

import numpy as np
from pathlib import Path
from datetime import datetime


def generate_report(results, data_dict, convergence_ok, output_path):
    """
    Generate markdown report with analysis findings
    
    Parameters:
    -----------
    results : dict
        Results dictionary from extract_results()
    data_dict : dict
        Data dictionary from prepare_data_for_modeling()
    convergence_ok : bool
        Whether MCMC convergence was successful
    output_path : str or Path
        Path to save the report
    """
    report = []
    
    # Header
    report.append("# Oil Price Change Point Detection - Analysis Report")
    report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\n---\n")
    
    # Executive Summary
    report.append("## Executive Summary")
    report.append(f"\nThis analysis applied Bayesian change point detection to identify significant regime shifts in oil prices.")
    report.append(f"\n**Key Finding:** A significant price regime change was detected on **{results['change_date']}**.")
    report.append(f"\n- **Price before change:** ${results['mu_before_mean']:.2f} ± ${results['mu_before_std']:.2f}")
    report.append(f"- **Price after change:** ${results['mu_after_mean']:.2f} ± ${results['mu_after_std']:.2f}")
    report.append(f"- **Price change:** ${results['price_change']:.2f} ({results['price_change_pct']:+.1f}%)")
    report.append("\n---\n")
    
    # Data Overview
    report.append("## Data Overview")
    report.append(f"\n- **Dataset:** Oil price time series")
    report.append(f"- **Observations:** {data_dict['n_days']} days")
    report.append(f"- **Date range:** {data_dict['dates'][0]} to {data_dict['dates'][-1]}")
    report.append(f"- **Price range:** ${data_dict['oil_prices'].min():.2f} - ${data_dict['oil_prices'].max():.2f}")
    report.append(f"- **Overall mean:** ${data_dict['historical_mean']:.2f}")
    report.append(f"- **Overall std dev:** ${data_dict['historical_std']:.2f}")
    report.append("\n---\n")
    
    # Methodology
    report.append("## Methodology")
    report.append("\n### Bayesian Change Point Model")
    report.append("\nWe implemented a Bayesian change point detection model with the following components:")
    report.append("\n**Priors:**")
    report.append("- Change point (τ): DiscreteUniform(0, n_days-1)")
    report.append("- Price before (μ₁): Normal(historical_mean, 20)")
    report.append("- Price after (μ₂): Normal(historical_mean, 20)")
    report.append("- Volatility before (σ₁): HalfNormal(10)")
    report.append("- Volatility after (σ₂): HalfNormal(10)")
    report.append("\n**Likelihood:**")
    report.append("- Prices ~ Normal(μ, σ), switching at change point τ")
    report.append("\n**MCMC Sampling:**")
    report.append("- 2000 draws per chain")
    report.append("- 1000 tuning iterations")
    report.append("- 4 independent chains")
    report.append("\n---\n")
    
    # Results
    report.append("## Results")
    report.append("\n### Change Point Detection")
    report.append(f"\n**Most likely change point:** {results['change_date']}")
    report.append(f"\n**95% Credible Interval:** {results['date_lower']} to {results['date_upper']}")
    report.append(f"\nThe model identified day {results['tau_mean']} (out of {data_dict['n_days']}) as the most likely change point.")
    
    report.append("\n### Price Regime Analysis")
    report.append("\n#### Before Change Point")
    report.append(f"- **Mean price:** ${results['mu_before_mean']:.2f}")
    report.append(f"- **Std deviation:** ${results['mu_before_std']:.2f}")
    report.append(f"- **Volatility:** ${results['sigma_before_mean']:.2f}")
    
    report.append("\n#### After Change Point")
    report.append(f"- **Mean price:** ${results['mu_after_mean']:.2f}")
    report.append(f"- **Std deviation:** ${results['mu_after_std']:.2f}")
    report.append(f"- **Volatility:** ${results['sigma_after_mean']:.2f}")
    
    report.append("\n#### Price Change")
    report.append(f"- **Absolute change:** ${results['price_change']:.2f}")
    report.append(f"- **Percentage change:** {results['price_change_pct']:+.1f}%")
    
    if results['price_change'] < 0:
        report.append(f"\nThe analysis detected a **price decrease** of ${abs(results['price_change']):.2f}, representing a {abs(results['price_change_pct']):.1f}% drop.")
    else:
        report.append(f"\nThe analysis detected a **price increase** of ${results['price_change']:.2f}, representing a {results['price_change_pct']:.1f}% rise.")
    
    report.append("\n---\n")
    
    # Model Diagnostics
    report.append("## Model Diagnostics")
    if convergence_ok:
        report.append("\n✓ **Convergence Status:** GOOD")
        report.append("\n- All R-hat values < 1.01")
        report.append("- All ESS values > 400")
        report.append("\nThe MCMC sampling converged successfully, indicating reliable results.")
    else:
        report.append("\n⚠ **Convergence Status:** WARNING")
        report.append("\nSome convergence issues were detected. Results should be interpreted with caution.")
    
    report.append("\n---\n")
    
    # Interpretation
    report.append("## Interpretation")
    report.append("\n### Historical Context")
    report.append("\nThe detected change point should be validated against known historical events:")
    report.append("\n- OPEC production decisions")
    report.append("- Geopolitical events (wars, sanctions)")
    report.append("- Economic crises")
    report.append("- Supply/demand shocks")
    report.append("- Global health events (e.g., COVID-19 pandemic)")
    
    # Check if change point is around March 2020 (COVID crash)
    change_year = results['change_date'].astype('datetime64[Y]').astype(int) + 1970
    change_month = results['change_date'].astype('datetime64[M]').astype(int) % 12 + 1
    
    if change_year == 2020 and change_month in [2, 3, 4]:
        report.append("\n**Note:** The detected change point aligns with the COVID-19 pandemic onset (early 2020), ")
        report.append("which caused a dramatic collapse in oil demand and prices.")
    
    report.append("\n---\n")
    
    # Visualizations
    report.append("## Visualizations")
    report.append("\nThe following visualizations have been generated:")
    report.append("\n1. **changepoint_results.png** - Comprehensive dashboard showing:")
    report.append("   - Time series with detected change point")
    report.append("   - Posterior distribution of change point")
    report.append("   - Price level distributions")
    report.append("   - Posterior predictive check")
    report.append("\n2. **trace_diagnostics.png** - MCMC convergence diagnostics")
    report.append("\n3. **regime_comparison.png** - Detailed regime comparison")
    report.append("\n---\n")
    
    # Recommendations
    report.append("## Recommendations")
    report.append("\n1. **Validate findings** against historical oil market events")
    report.append("2. **Consider multiple change points** if the data spans a long period")
    report.append("3. **Incorporate external factors** (production data, geopolitical events) for richer analysis")
    report.append("4. **Use results for forecasting** by modeling each regime separately")
    report.append("\n---\n")
    
    # Conclusion
    report.append("## Conclusion")
    report.append(f"\nThe Bayesian change point analysis successfully identified a significant regime shift in oil prices on {results['change_date']}. ")
    report.append(f"The model detected a {abs(results['price_change_pct']):.1f}% {'decrease' if results['price_change'] < 0 else 'increase'} in average price levels, ")
    report.append(f"with the price changing from ${results['mu_before_mean']:.2f} to ${results['mu_after_mean']:.2f}. ")
    report.append("This analysis provides a quantitative foundation for understanding structural breaks in the oil market.")
    
    # Write report
    report_text = '\n'.join(report)
    with open(output_path, 'w') as f:
        f.write(report_text)
    
    print(f"\n✓ Report saved to {output_path}")
    return report_text
