import numpy as np
import pymc as pm
import arviz as az
from pathlib import Path


def build_changepoint_model(oil_prices, historical_mean, historical_std):
    
    n_days = len(oil_prices)
    
    with pm.Model() as oil_model:
        # Change point (which day did regime shift occur?)
        tau = pm.DiscreteUniform('tau', lower=0, upper=n_days-1)
        
        # Price levels before and after change
        mu_before = pm.Normal('mu_before', mu=historical_mean, sigma=20)
        mu_after = pm.Normal('mu_after', mu=historical_mean, sigma=20)
        
        # Volatility before and after change
        sigma_before = pm.HalfNormal('sigma_before', sigma=10)
        sigma_after = pm.HalfNormal('sigma_after', sigma=10)
        
        # Switch logic: use regime 1 before tau, regime 2 after
        idx = np.arange(n_days)
        mu = pm.math.switch(tau > idx, mu_before, mu_after)
        sigma = pm.math.switch(tau > idx, sigma_before, sigma_after)
        
        # Likelihood: observed prices follow Normal distribution
        obs = pm.Normal('obs', mu=mu, sigma=sigma, observed=oil_prices)
    
    return oil_model


def sample_model(model, draws=2000, tune=1000, chains=4, random_seed=42):
   
    print("\n" + "="*50)
    print("RUNNING MCMC SAMPLING")
    print("="*50)
    print(f"Draws per chain: {draws}")
    print(f"Tuning iterations: {tune}")
    print(f"Number of chains: {chains}")
    print("="*50)
    
    with model:
        trace = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            return_inferencedata=True,
            random_seed=random_seed,
            progressbar=True
        )
    
    print("\n✓ Sampling complete!")
    return trace


def check_convergence(trace, var_names=['tau', 'mu_before', 'mu_after', 'sigma_before', 'sigma_after']):
   
    print("\n" + "="*50)
    print("CONVERGENCE DIAGNOSTICS")
    print("="*50)
    
    summary = az.summary(trace, var_names=var_names)
    print(summary)
    
    # Check R-hat values
    rhat_check = (summary['r_hat'] < 1.01).all()
    
    # Check ESS
    ess_check = (summary['ess_bulk'] > 400).all() and (summary['ess_tail'] > 400).all()
    
    print("\n" + "="*50)
    if rhat_check and ess_check:
        print("✓ Convergence looks GOOD!")
        print("  - All R-hat values < 1.01")
        print("  - All ESS values > 400")
        convergence_ok = True
    else:
        print("⚠ WARNING: Convergence issues detected!")
        if not rhat_check:
            print("  - Some R-hat values >= 1.01")
        if not ess_check:
            print("  - Some ESS values <= 400")
        print("  - Consider increasing samples or tuning iterations")
        convergence_ok = False
    print("="*50)
    
    return convergence_ok


def extract_results(trace, dates):
    
    # Extract posterior samples
    tau_samples = trace.posterior['tau'].values.flatten()
    mu_before_samples = trace.posterior['mu_before'].values.flatten()
    mu_after_samples = trace.posterior['mu_after'].values.flatten()
    sigma_before_samples = trace.posterior['sigma_before'].values.flatten()
    sigma_after_samples = trace.posterior['sigma_after'].values.flatten()
    
    # Most likely change point
    tau_mean = int(tau_samples.mean())
    tau_median = int(np.median(tau_samples))
    change_date = dates[tau_mean]
    
    # Credible interval for change point
    tau_hdi = az.hdi(trace, var_names=['tau'], hdi_prob=0.95)
    tau_lower = int(tau_hdi['tau'].values[0])
    tau_upper = int(tau_hdi['tau'].values[1])
    
    # Price statistics
    mu_before_mean = mu_before_samples.mean()
    mu_after_mean = mu_after_samples.mean()
    price_change = mu_after_mean - mu_before_mean
    price_change_pct = (price_change / mu_before_mean) * 100
    
    results = {
        'tau_mean': tau_mean,
        'tau_median': tau_median,
        'change_date': change_date,
        'tau_lower': tau_lower,
        'tau_upper': tau_upper,
        'date_lower': dates[tau_lower],
        'date_upper': dates[tau_upper],
        'mu_before_mean': mu_before_mean,
        'mu_before_std': mu_before_samples.std(),
        'mu_after_mean': mu_after_mean,
        'mu_after_std': mu_after_samples.std(),
        'sigma_before_mean': sigma_before_samples.mean(),
        'sigma_after_mean': sigma_after_samples.mean(),
        'price_change': price_change,
        'price_change_pct': price_change_pct,
        'tau_samples': tau_samples,
        'mu_before_samples': mu_before_samples,
        'mu_after_samples': mu_after_samples
    }
    
    print("\n" + "="*50)
    print("CHANGE POINT DETECTION RESULTS")
    print("="*50)
    print(f"Most likely change point: {change_date}")
    print(f"95% Credible Interval: {dates[tau_lower]} to {dates[tau_upper]}")
    print(f"\nPrice before change: ${mu_before_mean:.2f} ± ${results['mu_before_std']:.2f}")
    print(f"Price after change:  ${mu_after_mean:.2f} ± ${results['mu_after_std']:.2f}")
    print(f"\nPrice change: ${price_change:.2f} ({price_change_pct:+.1f}%)")
    print(f"\nVolatility before: ${results['sigma_before_mean']:.2f}")
    print(f"Volatility after:  ${results['sigma_after_mean']:.2f}")
    print("="*50)
    
    return results
