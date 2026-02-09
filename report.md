# Analysis Report: Time Series Properties & Change Point Modeling Context

This report provides the theoretical and analytical foundation for the Oil Price Change Point Detection project.

## a. Key References and Concepts

The project relies on the following key concepts and methodologies:

1.  **Bayesian Change Point Detection**: A probabilistic approach to identifying points in a time series where the statistical properties (mean, variance) change abruptly. Unlike frequentist methods, it provides a distribution over possible change points, quantifying uncertainty.
    *   *Reference*: "Bayesian Data Analysis" by Gelman et al. (for hierarchical modeling principles).
    *   *Tool*: `PyMC` (Probabilistic Programming in Python) is used to implement the model using Markov Chain Monte Carlo (MCMC) sampling.

2.  **Time Series Analysis**: The study of data points collected over time to extract meaningful statistics and characteristics.
    *   *Reference*: "Time Series Analysis and Its Applications" by Shumway and Stoffer.

## b. Analysis of Time Series Properties

Before modeling, we investigated the Brent oil price data properties.

### i. Trend Analysis
Visual inspection of the time series reveals a **non-linear, stochastic trend**. The data does not follow a simple upward or downward path but exhibits distinct "regimes" or periods of relative stability followed by structural breaks (e.g., the 2008 financial crisis spike and crash, the 2014 decline, and the 2020 COVID-19 shock). There is no single global trend that fits the entire history well.

### ii. Stationarity Testing
We performed an **Augmented Dickey-Fuller (ADF) test** to check for stationarity (constant mean and variance over time).

*   **ADF Statistic**: -1.9939
*   **Result**: The p-value is > 0.05, meaning we **fail to reject the null hypothesis**.
*   **Conclusion**: The time series is **NON-STATIONARY**.

### iii. Volatility Patterns
Volatility is not constant (heteroscedasticity). We observe **volatility clustering**, where periods of high volatility (large price swings) tend to be followed by high volatility, and low by low.
*   *Observation*: Significant volatility spikes align with major geopolitical events (as listed in `Event.csv`).

### iv. Informing Modeling Choices
*   Since the data is **non-stationary** and has **structural breaks**, standard linear regression or simple ARIMA models (without differencing) are insufficient for capturing the price levels.
*   Differencing the data (to achieve stationarity) would lose the absolute price level information, which is critical for regime detection.
*   **Therefore, a Change Point Model is theoretically appropriate.** It explicitly models the non-stationarity by assuming the data is piece-wise stationary (constant within each regime), allowing us to capture the shifts in mean and volatility directly.

## c. Explanation of Change Point Models

**Purpose**: Change point models are designed to handle time series data that experience abrupt structural changes. In the context of oil prices, these models help us:
1.  **Identify Regimes**: Segment the timeline into distinct periods (e.g., "Pre-Crisis High Growth", "Post-Crisis Crash").
2.  **Quantify Shifts**: Estimate the magnitude of change in average price and volatility at each break.
3.  **Detect Structural Breaks**: Mathematically pinpoint the dates when the underlying market dynamics shifted, rather than relying on subjective visual inspection.

**Mechanism**: The model assumes that at some unknown time $\tau$, the parameters $\theta$ (mean $\mu$, variance $\sigma$) of the data generating process change from $\theta_1$ to $\theta_2$. The goal is to estimate the posterior distribution of $\tau$ and the parameters for each segment.

## d. Expected Outputs and Limitations

### Expected Outputs
The Change Point Analysis (Task 2) will generate:
1.  **Dates of Change**: Specific dates (with credible intervals) where structural breaks occurred.
2.  **Regime Parameters**:
    *   **Mean Price ($\mu$)** for each regime.
    *   **Volatility ($\sigma$)** for each regime.
3.  **Probability of Change**: A probability curve over time indicating the likelihood of a change point occurring at each date.

### Limitations
1.  **Lag in Detection**: The model (especially offline) identifies changes retrospectively. Real-time detection has a lag.
2.  **Number of Change Points**: The number of change points ($k$) often needs to be specified a priori or inferred, which adds complexity.
3.  **Independence Assumption**: Basic models assume observations within a regime are independent (IID), which might violate the autocorrelation present in daily financial data.
