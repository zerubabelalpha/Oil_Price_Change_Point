
import sys
from pathlib import Path
import argparse

# Add the src directory to the path so we can import the package
# if it's not installed in the environment yet
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root / 'src'))

from data import load_oil_data, clean_data, prepare_data_for_modeling
from eda import calculate_statistics, plot_time_series, plot_distribution, plot_volatility

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
    data_dict = prepare_data_for_modeling(df)
    print(f"Loaded {len(df)} records. Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")

    # 2. Exploratory Data Analysis
    print("\n[Step 2] Running Exploratory Data Analysis...")
    calculate_statistics(df)
    plot_time_series(df, save_path=output_dir / 'eda_time_series.png')
    plot_distribution(df, save_path=output_dir / 'eda_distribution.png')
    plot_volatility(df, window=30, save_path=output_dir / 'eda_volatility.png')

    print("\n" + "="*50)
    print("TASK 1 COMPLETE")
    print("="*50)
    print(f"check outputs in: {output_dir}")

if __name__ == "__main__":
    main()
