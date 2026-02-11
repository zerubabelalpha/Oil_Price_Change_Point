import os
import re
import pandas as pd
import numpy as np
from flask import Flask, jsonify
from flask_cors import CORS
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'processed_data.csv'
EVENT_PATH = PROJECT_ROOT / 'Event.csv'
REPORT_PATH = PROJECT_ROOT / 'outputs' / 'analysis_report.md'

def parse_analysis_report(report_path):
    if not report_path.exists():
        return None
    
    content = report_path.read_text()
    results = {}
    
    # Extract Change Point Date
    cp_match = re.search(r"Most likely CP:\s+(\d{4}-\d{2}-\d{2})", content)
    if cp_match:
        results['change_point_date'] = cp_match.group(1)
    
    # Extract 95% CI
    ci_match = re.search(r"95% CI:\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})", content)
    if ci_match:
        results['ci_lower'] = ci_match.group(1)
        results['ci_upper'] = ci_match.group(2)
        
    # Extract Mean Prices
    means_match = re.findall(r"\$(\d+\.\d+)", content)
    if len(means_match) >= 2:
        results['mu_before'] = float(means_match[0])
        results['mu_after'] = float(means_match[1])
        
    # Extract Volatility
    # The table structure is a bit more complex, let's look for the regime analysis section
    regime_section = re.search(r"## Regime Analysis(.*?)(?=---|$)", content, re.DOTALL)
    if regime_section:
        table_lines = regime_section.group(1).strip().split('\n')
        for line in table_lines:
            if 'Volatility' in line:
                vols = re.findall(r"\$(\d+\.\d+)", line)
                if len(vols) >= 2:
                    results['sigma_before'] = float(vols[0])
                    results['sigma_after'] = float(vols[1])

    return results

@app.route('/api/historical-prices', methods=['GET'])
def get_historical_prices():
    if not DATA_PATH.exists():
        return jsonify({"error": "Data not found"}), 404
    
    df = pd.read_csv(DATA_PATH)
    # Return a simplified version for charting (X: Date, Y: Price)
    data = df.to_dict(orient='records')
    return jsonify(data)

@app.route('/api/change-points', methods=['GET'])
def get_change_points():
    results = parse_analysis_report(REPORT_PATH)
    if not results:
        return jsonify({"error": "Results not found"}), 404
    return jsonify(results)

@app.route('/api/events', methods=['GET'])
def get_events():
    if not EVENT_PATH.exists():
        return jsonify({"error": "Events not found"}), 404
    
    df = pd.read_csv(EVENT_PATH)
    data = df.to_dict(orient='records')
    return jsonify(data)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    results = parse_analysis_report(REPORT_PATH)
    if not results:
        return jsonify({"error": "Stats not found"}), 404
    
    price_change = results.get('mu_after', 0) - results.get('mu_before', 0)
    price_change_pct = (price_change / results.get('mu_before', 1)) * 100
    
    stats = {
        "mu_before": results.get('mu_before'),
        "mu_after": results.get('mu_after'),
        "sigma_before": results.get('sigma_before'),
        "sigma_after": results.get('sigma_after'),
        "price_change": round(price_change, 2),
        "price_change_pct": round(price_change_pct, 2)
    }
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
