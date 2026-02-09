# Oil Price Change Point Detection

A comprehensive Bayesian analysis system for detecting significant regime shifts in oil prices using PyMC.

## Overview

This project implements Bayesian change point detection to identify structural breaks in oil price time series data. The analysis quantifies uncertainty through credible intervals and provides detailed visualizations of detected regime changes.

## Features

- **Bayesian Change Point Detection**: Uses PyMC to model regime shifts
- **Comprehensive Diagnostics**: MCMC convergence checks (R-hat, ESS)
- **Rich Visualizations**: Time series plots, posterior distributions, regime comparisons
- **Automated Reporting**: Generates detailed markdown reports with findings
- **Exploratory Analysis**: Statistical summaries and volatility analysis

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or navigate to the project directory:
   ```bash
   cd oil_price_changepoint
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   *Note: This project uses a flat run-script structure, so standard package installation is not required.*

## Usage

### Run the Pipeline

You can run the complete analysis pipeline using the unified script:

```bash
python scripts/run_pipeline.py
```

This will:
1. Load and clean the oil price data
2. Perform exploratory data analysis
3. Build and sample the Bayesian model
4. Check convergence diagnostics
5. Extract change point results
6. Generate visualizations
7. Create a comprehensive report

**Options:**
- `--data`: Path to input CSV data (default: `data/BrentOilPrices.csv`)
- `--output`: Directory to save outputs (default: `outputs/`)
- `--draws`: Number of MCMC draws (default: 2000)
- `--chains`: Number of MCMC chains (default: 4)

Example:
```bash
python scripts/run_pipeline.py --draws 5000 --output my_results/
```

### Interactive Notebook

For a step-by-step, interactive experience, use the Jupyter notebook:

```bash
jupyter notebook notebooks/oil_price_analysis.ipynb
```

The notebook provides:
- Cell-by-cell execution with explanations
- Inline visualizations
- Detailed interpretations
- Easy experimentation with parameters

## Project Structure

```
oil_price_changepoint/
├── data/
│   └── BrentOilPrices.csv          # Brent oil price dataset
├── notebooks/
│   ├── README.md                    # Notebook documentation
│   └── oil_price_analysis.ipynb     # Interactive analysis notebook
├── outputs/                         # Generated visualizations and reports
├── scripts/
│   └── run_pipeline.py              # Main execution script
├── src/
│   ├── __init__.py
│   ├── data.py                  # Data loading and cleaning
│   ├── eda.py                   # Exploratory data analysis
│   ├── model.py                 # Bayesian model implementation
│   ├── visualization.py         # Visualization functions
│   └── report.py                # Report generation
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## Methodology

### Bayesian Model Components

**Priors:**
- Change point (τ): DiscreteUniform(0, n_days-1)
- Price before (μ₁): Normal(historical_mean, 20)
- Price after (μ₂): Normal(historical_mean, 20)
- Volatility before (σ₁): HalfNormal(10)
- Volatility after (σ₂): HalfNormal(10)

**Likelihood:**
- Prices ~ Normal(μ, σ), switching at change point τ

## Output Files

After running the analysis, the following files are generated in the `outputs/` directory:

1. **analysis_report.md** - Comprehensive markdown report
2. **changepoint_results.png** - Main results dashboard
3. **trace_diagnostics.png** - MCMC convergence diagnostics
4. **regime_comparison.png** - Detailed regime comparison
5. **eda_time_series.png**, **eda_distribution.png**, **eda_volatility.png** - EDA plots

## License

This project is provided as-is for educational and research purposes.
