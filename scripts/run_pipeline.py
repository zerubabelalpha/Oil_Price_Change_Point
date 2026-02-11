
import sys
from pathlib import Path
import argparse

# Add the src directory to the path so we can import the package
# if it's not installed in the environment yet
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root / './src'))

from data import load_oil_data, clean_data, prepare_data_for_modeling
from eda import (calculate_statistics, plot_time_series, plot_distribution, 
                 plot_volatility, calculate_log_returns, check_stationarity, plot_log_returns)
from model import build_changepoint_model, sample_model, check_convergence, extract_results
from visualization import plot_changepoint_results, plot_trace_diagnostics, plot_regime_comparison
from report import generate_report

def main():
    parser = argparse.ArgumentParser(description="Run Oil Price Change Point Analysis Pipeline (Task 1)")
    parser.add_argument("--data", type=str, default=str(project_root / 'data' / 'BrentOilPrices.csv'), help="Path to input CSV data")
    parser.add_argument("--output", type=str, default=str(project_root / 'outputs'), help="Directory to save outputs")
    
    args = parser.parse_args()
    
    data_path = Path(args.data)
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print(f"Running analysis pipeline (Task 1: Data & EDA)...")
    print(f"Data: {data_path}")
    print(f"Output: {output_dir}")
    
    # 1. Load and Prepare Data
    print("\n[Step 1] Loading and Preparing Data...")
    if not data_path.exists():
        print(f"Error: Data file not found at {data_path}")
        return
        
    df = load_oil_data(data_path)
    df = clean_data(df)
    
    # Save processed data
    processed_path = output_dir / 'processed_data.csv'
    df.to_csv(processed_path, index=False)
    print(f"✓ Saved processed data to {processed_path}")
    
    data_dict = prepare_data_for_modeling(df)
    print(f"Loaded {len(df)} records. Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")

    # 2. Exploratory Data Analysis
    print("\n[Step 2] Running Exploratory Data Analysis...")
    calculate_statistics(df)
    plot_time_series(df, save_path=output_dir / 'eda_time_series.png')
    plot_distribution(df, save_path=output_dir / 'eda_distribution.png')
    plot_volatility(df, window=30, save_path=output_dir / 'eda_volatility.png')

    # 2b. Log Returns and Stationarity
    print("\n[Step 2b] Analyzing Log Returns and Stationarity...")
    df_returns = calculate_log_returns(df)
    plot_log_returns(df_returns, save_path=output_dir / 'eda_log_returns.png')
    check_stationarity(df_returns['Log_Returns'])

    # 3. Build and Sample Model
    print("\n[Step 3] Building and Sampling Bayesian Model...")
    model = build_changepoint_model(
        data_dict['oil_prices'],
        data_dict['historical_mean'],
        data_dict['historical_std']
    )
    
    trace = sample_model(
        model, 
        draws=args.draws, 
        tune=args.tune, 
        chains=args.chains
    )

    # 4. Diagnostics
    print("\n[Step 4] Checking Convergence...")
    convergence_ok = check_convergence(trace)
    
    # 5. Extract Results
    print("\n[Step 5] Extracting Results...")
    results = extract_results(trace, data_dict['dates'])

    # 6. Visualization
    print("\n[Step 6] Generating Visualizations...")
    plot_changepoint_results(
        data_dict['dates'], 
        data_dict['oil_prices'], 
        results, 
        trace,
        save_path=output_dir / 'changepoint_results.png'
    )
    
    plot_trace_diagnostics(
        trace,
        save_path=output_dir / 'trace_diagnostics.png'
    )
    
    plot_regime_comparison(
        data_dict['dates'],
        data_dict['oil_prices'],
        results,
        save_path=output_dir / 'regime_comparison.png'
    )

    # 7. Report Generation
    print("\n[Step 7] Generating Report...")
    report_path = output_dir / 'analysis_report.md'
    generate_report(results, data_dict, convergence_ok, report_path)
    
    print("\n" + "="*50)
    print("TASK 1 COMPLETE")
    print("="*50)
    print(f"check outputs in: {output_dir}")

if __name__ == "__main__":
    main()
