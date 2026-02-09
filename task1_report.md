# Task 1 Report: Oil Price Analysis & Exploratory Findings

## 1. Planned Analysis Steps

For the initial phase (Task 1) of the Oil Price Change Point Detection project, the following steps were executed:

### 1.1 Data Loading and Preprocessing
- **Source**: `BrentOilPrices.csv` containing historical Brent crude oil prices.
- **Date Parsing**: Implemented robust parsing for mixed date formats (e.g., `20-May-87` and `Apr 22, 2020`) to ensure temporal consistency.
- **Cleaning**:
  - Sorted data chronologically.
  - Handled missing values using forward-fill (to propagate last known price) and backward-fill for initial gaps.
  - Validated data types (Date as datetime objects, Price as float).

### 1.2 Exploratory Data Analysis (EDA)
- **Descriptive Statistics**: Calculated mean, standard deviation, min, and max values to understand the data distribution.
- **Visualization**:
  - **Time Series Plot**: To visualize the long-term trend and identify obvious structural breaks.
  - **Distribution Plot**: To checks for normality and skewness in price data.
  - **Volatility Analysis**: Calculated 30-day rolling standard deviation to identify periods of market instability.

---

## 2. Assumptions and Limitations

### Assumptions
- **Data Continuity**: We assume the dataset provides a representative daily time series of Brent crude spot prices.
- **Market Efficiency**: We assume prices reflect available market information, and large shifts correspond to significant external events or structural changes.

### Limitations
- **Missing Data**: The dataset required imputation (forward-fill). While standard for financial time series, this may slightly underestimate volatility during periods of missing reporting.
- **Single Variable**: The analysis is univariate (Price only). It does not purely account for inflation or external covariates (like production volume or geopolitical events) at this stage.
- **Stationarity**: Oil prices are non-stationary. Simple statistical measures (like global mean) may not be sufficient for long-term forecasting without differencing or regime-switching models.

---

## 3. Initial EDA Findings

The analysis of Brent oil prices from **May 20, 1987** to **November 14, 2022** revealed:

- **Price Range**: The prices varied significantly, from a low of **$9.10** to a high of **$143.95**.
- **Central Tendency**: The average price over the period was **$48.42** with a standard deviation of **$32.86**, indicating high variability.
- **Volatility Clusters**: Visual inspection of the volatility plot shows distinct periods of high instability, likely corresponding to major global events (e.g., 2008 Financial Crisis, 2014 Oil Price Crash, 2020 COVID-19 Pandemic).
- **Distribution**: The price distribution is right-skewed, with a long tail towards higher prices, suggesting that extreme high-price events are more common/extreme than price collapses below production costs.

---

## 4. Future Work

To deepen the analysis and provide actionable insights, the next phases will focus on:

### 4.1 Change Point Modeling (Task 2)
- Implement a **Bayesian Change Point Detection** model using PyMC.
- This will mathematically identify the exact dates of structural breaks (regime shifts) rather than relying on visual inspection.
- We will model distinct price regimes (mean and volatility) before and after these break points.

### 4.2 Insight Generation
- Correlate detected change points with historical geopolitical and economic events.
- Quantify the probability of regime shifts.

### 4.3 Interactive Dashboard
- Develop a web-based dashboard (using Streamlit or Dash) to allow users to:
  - Interactively explore the time series.
  - Select custom date ranges.
  - Visualize the fitted change point model and credible intervals in real-time.
