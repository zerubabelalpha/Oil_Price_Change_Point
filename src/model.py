import numpy as np
import pymc as pm
import arviz as az
from pathlib import Path

def build_changepoint_model(oil_prices, historical_mean, historical_std, marginalized=True):
    """
    Builds a Bayesian change point model.
    By default uses marginalized=True to allow efficient NUTS sampling.
    """
    n_days = len(oil_prices)
    
    with pm.Model() as oil_model:
        # Store oil_prices as a model attribute for later access
        oil_model.oil_prices = oil_prices
        # Continuous parameters (always needed)
        mu_before = pm.Normal('mu_before', mu=historical_mean, sigma=20)
        mu_after = pm.Normal('mu_after', mu=historical_mean, sigma=20)
        sigma_before = pm.HalfNormal('sigma_before', sigma=10)
        sigma_after = pm.HalfNormal('sigma_after', sigma=10)
        
        if not marginalized:
            # Original discrete model (Metropolis)
            tau = pm.DiscreteUniform('tau', lower=0, upper=n_days-1)
            idx = np.arange(n_days)
            mu = pm.math.switch(tau > idx, mu_before, mu_after)
            sigma = pm.math.switch(tau > idx, sigma_before, sigma_after)
            obs = pm.Normal('obs', mu=mu, sigma=sigma, observed=oil_prices)
        else:
            # Marginalized model: 
            # We calculate the log-likelihood for each possible change point
            # and use pm.logsumexp to marginalize out tau.
            
            # Log-likelihood of each data point under regime 1 and regime 2
            logp_before = pm.logp(pm.Normal.dist(mu=mu_before, sigma=sigma_before), oil_prices)
            logp_after = pm.logp(pm.Normal.dist(mu=mu_after, sigma=sigma_after), oil_prices)
            
            # cumulative log-likelihoods
            logp_before_cum = pm.math.cumsum(logp_before)
            logp_after_cum = pm.math.cumsum(logp_after)
            
            total_logp_after = logp_after_cum[-1]
            
            # Shift cumsums to simplify indexing
            logp_before_cum_shifted = pm.math.concatenate([[0], logp_before_cum[:-1]])
            logp_after_cum_shifted = pm.math.concatenate([[0], logp_after_cum[:-1]])
            
            # p(tau=k | ...) propto sum_{i<k} logp_before[i] + sum_{i>=k} logp_after[i]
            logp_tau = logp_before_cum_shifted + (total_logp_after - logp_after_cum_shifted)
            
            # Marginalize: log(1/N * sum(exp(logp_tau))) = logsumexp(logp_tau) - log(N)
            pm.Potential('marginal_likelihood', pm.math.logsumexp(logp_tau) - np.log(n_days))
            
            # Store logp_tau for recovery
            pm.Deterministic('logp_tau', logp_tau)
    
    return oil_model

def _recover_tau(trace):
    """Helper to recover tau samples from a marginalized model's logp_tau."""
    if 'logp_tau' not in trace.posterior:
        return None
        
    logp_tau = trace.posterior['logp_tau'].values
    
    # Softmax over n_days to get probabilities per sample
    max_logp = np.max(logp_tau, axis=-1, keepdims=True)
    probs = np.exp(logp_tau - max_logp)
    probs = probs / np.sum(probs, axis=-1, keepdims=True)
    
    chains, draws, n_days = logp_tau.shape
    tau_samples = np.zeros((chains, draws), dtype=int)
    
    for c in range(chains):
        for d in range(draws):
            tau_samples[c, d] = np.random.choice(n_days, p=probs[c, d])
            
    return tau_samples

def sample_model(model, draws=1000, tune=1000, chains=4, random_seed=42):
    print("\n" + "="*50)
    print("RUNNING MCMC SAMPLING")
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
        
        # Generate posterior predictive samples
        print("\nGenerating posterior predictive samples...")
        if 'logp_tau' in trace.posterior:
            tau_samples = _recover_tau(trace)
            mu_before = trace.posterior['mu_before'].values
            mu_after = trace.posterior['mu_after'].values
            sigma_before = trace.posterior['sigma_before'].values
            sigma_after = trace.posterior['sigma_after'].values
            
            chains, draws, n_days = trace.posterior['logp_tau'].shape
            ppc_obs = np.zeros((chains, draws, n_days))
            
            for c in range(chains):
                for d in range(draws):
                    t = tau_samples[c, d]
                    if t > 0:
                        ppc_obs[c, d, :t] = np.random.normal(mu_before[c, d], sigma_before[c, d], size=t)
                    if t < n_days:
                        ppc_obs[c, d, t:] = np.random.normal(mu_after[c, d], sigma_after[c, d], size=n_days-t)
            
            import xarray as xr
            ppc_data = xr.Dataset(
                {"obs": (["chain", "draw", "obs_dim_0"], ppc_obs)},
                coords={"chain": np.arange(chains), "draw": np.arange(draws), "obs_dim_0": np.arange(n_days)}
            )
            
            # Create observed_data group - get from model attribute
            oil_prices_data = model.oil_prices
            
            obs_data = xr.Dataset(
                {"obs": (["obs_dim_0"], oil_prices_data)},
                coords={"obs_dim_0": np.arange(n_days)}
            )
            
            trace.add_groups({
                "posterior_predictive": ppc_data,
                "observed_data": obs_data
            })
        else:
            ppc = pm.sample_posterior_predictive(trace, random_seed=random_seed, progressbar=False)
            trace.extend(ppc)
    
    print("\nDONE: Sampling complete!")
    return trace

def check_convergence(trace, var_names=None):
    if var_names is None:
        var_names = ['mu_before', 'mu_after', 'sigma_before', 'sigma_after']
    summary = az.summary(trace, var_names=var_names)
    print("\nConvergence Summary:")
    print(summary)
    
    rhat_check = (summary['r_hat'] < 1.01).all()
    if rhat_check:
        print("\nv Convergence looks GOOD!")
    else:
        print("\nWAARNING: Convergence issues detected!")
    return rhat_check

def extract_results(trace, dates):
    # Extract params
    mu_before_samples = trace.posterior['mu_before'].values.flatten()
    mu_after_samples = trace.posterior['mu_after'].values.flatten()
    sigma_before_mean = trace.posterior['sigma_before'].values.mean()
    sigma_after_mean = trace.posterior['sigma_after'].values.mean()
    
    if 'logp_tau' in trace.posterior:
        tau_samples_grid = _recover_tau(trace)
        tau_samples = tau_samples_grid.flatten()
        logp_tau = trace.posterior['logp_tau'].values
        max_logp = np.max(logp_tau, axis=-1, keepdims=True)
        probs = np.exp(logp_tau - max_logp)
        probs = probs / np.sum(probs, axis=-1, keepdims=True)
        mean_probs = probs.mean(axis=(0, 1))
        
        tau_mean = int(np.argmax(mean_probs))
        tau_median = int(np.median(tau_samples))
        tau_hdi = az.hdi(tau_samples, hdi_prob=0.95)
        tau_lower, tau_upper = int(tau_hdi[0]), int(tau_hdi[1])
    else:
        tau_samples = trace.posterior['tau'].values.flatten()
        tau_mean = int(tau_samples.mean())
        tau_median = int(np.median(tau_samples))
        tau_hdi = az.hdi(trace, var_names=['tau'], hdi_prob=0.95)
        tau_lower, tau_upper = int(tau_hdi['tau'].values[0]), int(tau_hdi['tau'].values[1])

    mu_b_mean = mu_before_samples.mean()
    mu_a_mean = mu_after_samples.mean()
    
    results = {
        'tau_mean': tau_mean,
        'tau_median': tau_median,
        'change_date': dates[tau_mean],
        'tau_lower': tau_lower,
        'tau_upper': tau_upper,
        'date_lower': dates[max(0, tau_lower)],
        'date_upper': dates[min(len(dates)-1, tau_upper)],
        'mu_before_mean': mu_b_mean,
        'mu_before_std': mu_before_samples.std(),
        'mu_after_mean': mu_a_mean,
        'mu_after_std': mu_after_samples.std(),
        'sigma_before_mean': sigma_before_mean,
        'sigma_after_mean': sigma_after_mean,
        'price_change': mu_a_mean - mu_b_mean,
        'price_change_pct': ((mu_a_mean - mu_b_mean) / mu_b_mean) * 100,
        'tau_samples': tau_samples,
        'mu_before_samples': mu_before_samples,
        'mu_after_samples': mu_after_samples
    }
    
    print("\n" + "="*50)
    print("CHANGE POINT DETECTION RESULTS")
    print("="*50)
    print(f"Change point: {results['change_date']}")
    print(f"95% CI: {results['date_lower']} to {results['date_upper']}")
    print(f"Shift: ${mu_b_mean:.2f} to ${mu_a_mean:.2f} ({results['price_change_pct']:+.1f}%)")
    print("="*50)
    
    return results
