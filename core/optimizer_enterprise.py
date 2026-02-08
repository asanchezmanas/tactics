"""
Engine B Enterprise: SOTA 2024 MMM Optimization
Tier: Enterprise (Strategic, Enterprise plans)

Features:
- PyMC-Marketing integration for Bayesian inference
- Channel Synergy Matrix
- Nevergrad hyperparameter auto-tuning
- Advanced Adstock and Saturation functions
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from scipy.optimize import minimize
from scipy.stats import gamma as gamma_dist
import warnings

# PyMC imports with graceful fallback
try:
    import pymc as pm
    import arviz as az
    PYMC_AVAILABLE = True
except ImportError:
    PYMC_AVAILABLE = False
    warnings.warn("PyMC not installed. Bayesian MMM will use fallback mode.")

# Nevergrad imports with graceful fallback
try:
    import nevergrad as ng
    NEVERGRAD_AVAILABLE = True
except ImportError:
    NEVERGRAD_AVAILABLE = False
    warnings.warn("Nevergrad not installed. Using scipy for hyperparameter tuning.")


class EnterpriseMMOptimizer:
    """
    Enterprise tier MMM with SOTA 2024 capabilities:
    - PyMC-Marketing integration (Bayesian inference)
    - Channel Synergy Matrix
    - Nevergrad hyperparameter auto-tuning
    """
    
    def __init__(self, random_seed: int = 42):
        self.synergy_matrix = None
        self.channel_index = {}
        self.fitted_params = {}
        self.trace = None
        self.random_seed = random_seed
        np.random.seed(random_seed)
    
    # ============================================================
    # ADSTOCK TRANSFORMATIONS
    # ============================================================
    
    @staticmethod
    def weibull_adstock(x: np.ndarray, shape: float, scale: float, 
                        max_lag: int = 8) -> np.ndarray:
        """
        Weibull-based adstock transformation for flexible decay patterns.
        
        Args:
            x: Spend time series
            shape: Weibull shape parameter (>1 = delayed peak)
            scale: Weibull scale parameter (controls decay rate)
            max_lag: Maximum lag periods to consider
        
        Returns:
            Transformed spend with carryover effects
        """
        # Create Weibull weights
        lags = np.arange(max_lag)
        weights = (shape / scale) * (lags / scale) ** (shape - 1) * np.exp(-(lags / scale) ** shape)
        weights = weights / weights.sum()  # Normalize
        
        # Apply convolution
        adstocked = np.convolve(x, weights, mode='full')[:len(x)]
        return adstocked
    
    @staticmethod
    def geometric_adstock(x: np.ndarray, decay: float) -> np.ndarray:
        """
        Classic geometric adstock with exponential decay.
        """
        result = np.zeros_like(x, dtype=float)
        result[0] = x[0]
        for t in range(1, len(x)):
            result[t] = x[t] + decay * result[t-1]
        return result
    
    # ============================================================
    # SATURATION FUNCTIONS
    # ============================================================
    
    @staticmethod
    def hill_saturation(x: np.ndarray, alpha: float, gamma: float, 
                       max_effect: float = 1.0) -> np.ndarray:
        """
        Hill function for diminishing returns.
        
        Args:
            x: Transformed spend
            alpha: Shape parameter (steepness / Hill coefficient)
            gamma: Scale parameter (half-saturation point / EC50)
            max_effect: Maximum effect ceiling (default 1.0 for normalized)
        
        Returns:
            Saturated response
            
        Note:
            Aligned with core/optimizer.py hill_saturation for consistency.
            Formula: max_effect * (x^alpha) / (gamma^alpha + x^alpha)
        """
        x = np.maximum(np.asarray(x, dtype=float), 1e-8)
        return max_effect * (x ** alpha) / ((gamma ** alpha) + (x ** alpha))
    
    @staticmethod
    def logistic_saturation(x: np.ndarray, lam: float) -> np.ndarray:
        """
        Logistic saturation function.
        """
        return (1 - np.exp(-lam * x)) / (1 + np.exp(-lam * x))
    
    @staticmethod
    def michaelis_menten_saturation(x: np.ndarray, vmax: float, km: float) -> np.ndarray:
        """
        Michaelis-Menten saturation (from biochemistry).
        Better for gradual saturation curves.
        """
        return vmax * x / (km + x)
    
    # ============================================================
    # CHANNEL SYNERGY MATRIX
    # ============================================================
    
    def set_channel_synergy(self, channels: List[str], 
                            synergy_values: Dict[Tuple[str, str], float]):
        """
        Defines the channel interaction matrix.
        Example: synergy_values = {('Meta', 'Google'): 1.15, ('TikTok', 'Meta'): 1.08}
        """
        n = len(channels)
        self.synergy_matrix = np.eye(n)  # Identity = no synergy
        self.channel_index = {ch: i for i, ch in enumerate(channels)}
        
        for (ch1, ch2), value in synergy_values.items():
            if ch1 in self.channel_index and ch2 in self.channel_index:
                i, j = self.channel_index[ch1], self.channel_index[ch2]
                self.synergy_matrix[i, j] = value
                self.synergy_matrix[j, i] = value  # Symmetric
        
        return self.synergy_matrix
    
    def apply_synergy(self, channel_effects: np.ndarray) -> np.ndarray:
        """
        Applies synergy coefficients to individual channel effects.
        Total effect = base_effects @ synergy_matrix
        """
        if self.synergy_matrix is None:
            return channel_effects
        return channel_effects @ self.synergy_matrix
    
    # ============================================================
    # PYMC BAYESIAN MMM
    # ============================================================
    
    def run_pymc_inference(self, spend_data: np.ndarray, 
                           revenue_data: np.ndarray,
                           channel_names: List[str],
                           n_samples: int = 2000,
                           n_chains: int = 2) -> Dict:
        """
        Full Bayesian inference using PyMC.
        Returns posterior distributions for channel coefficients.
        
        Args:
            spend_data: Shape (n_periods, n_channels)
            revenue_data: Shape (n_periods,)
            channel_names: List of channel names
            n_samples: MCMC samples per chain
            n_chains: Number of parallel chains
        
        Returns:
            Dictionary with posteriors and diagnostics
        """
        if not PYMC_AVAILABLE:
            return self._fallback_inference(spend_data, revenue_data, channel_names)
        
        n_periods, n_channels = spend_data.shape
        
        with pm.Model() as mmm_model:
            # Priors for adstock parameters (per channel)
            decay = pm.Beta("decay", alpha=3, beta=3, shape=n_channels)
            
            # Priors for saturation parameters
            alpha = pm.Gamma("alpha", alpha=2, beta=1, shape=n_channels)
            gamma = pm.HalfNormal("gamma", sigma=1, shape=n_channels)
            
            # Channel coefficients (positive effect)
            beta = pm.HalfNormal("beta", sigma=0.5, shape=n_channels)
            
            # Intercept (baseline sales)
            intercept = pm.Normal("intercept", mu=revenue_data.mean(), sigma=revenue_data.std())
            
            # Transform spend data
            transformed_spend = []
            for ch in range(n_channels):
                # Apply geometric adstock
                adstocked = self.geometric_adstock(spend_data[:, ch], decay[ch].eval())
                # Apply Hill saturation
                saturated = self.hill_saturation(adstocked, alpha[ch], gamma[ch])
                transformed_spend.append(saturated)
            
            # Stack transformed channels
            X_transformed = pm.math.stack(transformed_spend, axis=1)
            
            # Expected revenue
            mu = intercept + pm.math.dot(X_transformed, beta)
            
            # Likelihood
            sigma = pm.HalfNormal("sigma", sigma=revenue_data.std() / 2)
            y_obs = pm.Normal("y_obs", mu=mu, sigma=sigma, observed=revenue_data)
            
            # Sample
            self.trace = pm.sample(
                n_samples, 
                chains=n_chains,
                return_inferencedata=True,
                random_seed=self.random_seed,
                progressbar=False
            )
        
        # Extract posteriors
        posterior_beta = self.trace.posterior["beta"].values.reshape(-1, n_channels)
        
        return {
            "posterior_means": posterior_beta.mean(axis=0).tolist(),
            "posterior_stds": posterior_beta.std(axis=0).tolist(),
            "credibility_intervals_90": [
                (np.percentile(posterior_beta[:, ch], 5), 
                 np.percentile(posterior_beta[:, ch], 95))
                for ch in range(n_channels)
            ],
            "channel_names": channel_names,
            "r_hat": az.rhat(self.trace)["beta"].values.tolist() if self.trace else [1.0] * n_channels,
            "n_samples": n_samples * n_chains,
            "model_type": "pymc_bayesian"
        }
    
    def _fallback_inference(self, spend_data: np.ndarray, 
                            revenue_data: np.ndarray,
                            channel_names: List[str]) -> Dict:
        """
        Fallback inference using bootstrapped OLS when PyMC is unavailable.
        """
        from sklearn.linear_model import Ridge
        
        n_channels = spend_data.shape[1]
        
        # Bootstrap for uncertainty
        n_bootstrap = 1000
        betas = []
        
        for _ in range(n_bootstrap):
            idx = np.random.choice(len(revenue_data), len(revenue_data), replace=True)
            X_boot = spend_data[idx]
            y_boot = revenue_data[idx]
            
            model = Ridge(alpha=1.0, positive=True)
            model.fit(X_boot, y_boot)
            betas.append(model.coef_)
        
        betas = np.array(betas)
        
        return {
            "posterior_means": betas.mean(axis=0).tolist(),
            "posterior_stds": betas.std(axis=0).tolist(),
            "credibility_intervals_90": [
                (np.percentile(betas[:, ch], 5), np.percentile(betas[:, ch], 95))
                for ch in range(n_channels)
            ],
            "channel_names": channel_names,
            "r_hat": [1.0] * n_channels,  # No convergence diagnostic for OLS
            "n_samples": n_bootstrap,
            "model_type": "bootstrap_ridge_fallback"
        }
    
    # ============================================================
    # NEVERGRAD HYPERPARAMETER TUNING
    # ============================================================
    
    def auto_tune_hyperparameters(self, spend_data: np.ndarray, 
                                   revenue_data: np.ndarray,
                                   param_bounds: Dict = None,
                                   budget: int = 200) -> Dict:
        """
        Automatic hyperparameter tuning using Nevergrad.
        Finds optimal adstock decay and saturation parameters.
        
        Args:
            spend_data: Shape (n_periods, n_channels)
            revenue_data: Shape (n_periods,)
            param_bounds: Optional custom bounds
            budget: Number of optimization iterations
        
        Returns:
            Optimal parameters and tuning metadata
        """
        n_channels = spend_data.shape[1]
        
        # Default bounds
        if param_bounds is None:
            param_bounds = {
                "decay": (0.1, 0.9),
                "hill_alpha": (0.5, 3.0),
                "hill_gamma": (0.1, 2.0)
            }
        
        if NEVERGRAD_AVAILABLE:
            return self._tune_with_nevergrad(spend_data, revenue_data, param_bounds, budget, n_channels)
        else:
            return self._tune_with_scipy(spend_data, revenue_data, param_bounds, n_channels)
    
    def _tune_with_nevergrad(self, spend_data: np.ndarray, revenue_data: np.ndarray,
                              param_bounds: Dict, budget: int, n_channels: int) -> Dict:
        """
        Hyperparameter tuning using Nevergrad's NGOpt.
        """
        # Define parametrization
        params = ng.p.Dict(
            decay=ng.p.Array(shape=(n_channels,)).set_bounds(
                param_bounds["decay"][0], param_bounds["decay"][1]
            ),
            hill_alpha=ng.p.Array(shape=(n_channels,)).set_bounds(
                param_bounds["hill_alpha"][0], param_bounds["hill_alpha"][1]
            ),
            hill_gamma=ng.p.Array(shape=(n_channels,)).set_bounds(
                param_bounds["hill_gamma"][0], param_bounds["hill_gamma"][1]
            )
        )
        
        def objective(params_dict):
            """Objective: minimize negative R²."""
            try:
                # Transform spend with current parameters
                transformed = np.zeros_like(spend_data)
                for ch in range(n_channels):
                    adstocked = self.geometric_adstock(spend_data[:, ch], params_dict["decay"][ch])
                    saturated = self.hill_saturation(
                        adstocked, 
                        params_dict["hill_alpha"][ch],
                        params_dict["hill_gamma"][ch]
                    )
                    transformed[:, ch] = saturated
                
                # Fit simple linear model
                from sklearn.linear_model import LinearRegression
                model = LinearRegression()
                model.fit(transformed, revenue_data)
                predictions = model.predict(transformed)
                
                # R² score
                ss_res = np.sum((revenue_data - predictions) ** 2)
                ss_tot = np.sum((revenue_data - revenue_data.mean()) ** 2)
                r2 = 1 - (ss_res / ss_tot)
                
                return -r2  # Minimize negative R²
            except Exception:
                return 1.0  # Return worst score on error
        
        # Optimize
        optimizer = ng.optimizers.NGOpt(parametrization=params, budget=budget)
        recommendation = optimizer.minimize(objective)
        
        best_params = recommendation.value
        best_r2 = -objective(best_params)
        
        self.fitted_params = {
            "decay": best_params["decay"].tolist(),
            "hill_alpha": best_params["hill_alpha"].tolist(),
            "hill_gamma": best_params["hill_gamma"].tolist(),
            "final_r2": float(best_r2),
            "tuning_iterations": budget,
            "optimizer": "nevergrad_NGOpt"
        }
        
        return self.fitted_params
    
    def _tune_with_scipy(self, spend_data: np.ndarray, revenue_data: np.ndarray,
                          param_bounds: Dict, n_channels: int) -> Dict:
        """
        Fallback hyperparameter tuning using scipy.optimize.
        """
        from sklearn.linear_model import LinearRegression
        
        # Create bounds for scipy
        bounds = []
        for _ in range(n_channels):
            bounds.append(param_bounds["decay"])
            bounds.append(param_bounds["hill_alpha"])
            bounds.append(param_bounds["hill_gamma"])
        
        def objective(params_flat):
            try:
                transformed = np.zeros_like(spend_data)
                for ch in range(n_channels):
                    idx = ch * 3
                    decay = params_flat[idx]
                    alpha = params_flat[idx + 1]
                    gamma_val = params_flat[idx + 2]
                    
                    adstocked = self.geometric_adstock(spend_data[:, ch], decay)
                    saturated = self.hill_saturation(adstocked, alpha, gamma_val)
                    transformed[:, ch] = saturated
                
                model = LinearRegression()
                model.fit(transformed, revenue_data)
                predictions = model.predict(transformed)
                
                ss_res = np.sum((revenue_data - predictions) ** 2)
                ss_tot = np.sum((revenue_data - revenue_data.mean()) ** 2)
                r2 = 1 - (ss_res / ss_tot)
                
                return -r2
            except Exception:
                return 1.0
        
        # Initial guess
        x0 = []
        for _ in range(n_channels):
            x0.extend([0.5, 1.5, 0.5])
        
        result = minimize(objective, x0, bounds=bounds, method='L-BFGS-B')
        
        # Extract results
        decay_vals = []
        alpha_vals = []
        gamma_vals = []
        for ch in range(n_channels):
            idx = ch * 3
            decay_vals.append(result.x[idx])
            alpha_vals.append(result.x[idx + 1])
            gamma_vals.append(result.x[idx + 2])
        
        self.fitted_params = {
            "decay": decay_vals,
            "hill_alpha": alpha_vals,
            "hill_gamma": gamma_vals,
            "final_r2": float(-result.fun),
            "tuning_iterations": result.nit,
            "optimizer": "scipy_LBFGSB"
        }
        
        return self.fitted_params
    
    # ============================================================
    # BUDGET OPTIMIZATION WITH CONSTRAINTS
    # ============================================================
    
    def optimize_budget(self, total_budget: float, 
                        channel_coefficients: List[float],
                        min_per_channel: Optional[List[float]] = None,
                        max_per_channel: Optional[List[float]] = None) -> Dict:
        """
        Optimal budget allocation using fitted model parameters.
        
        Args:
            total_budget: Total budget to allocate
            channel_coefficients: Posterior mean coefficients per channel
            min_per_channel: Minimum budget constraints
            max_per_channel: Maximum budget constraints
        
        Returns:
            Optimal allocation with expected impact
        """
        n_channels = len(channel_coefficients)
        
        # Use fitted parameters or defaults
        if self.fitted_params:
            hill_alpha = np.array(self.fitted_params.get("hill_alpha", [1.5] * n_channels))
            hill_gamma = np.array(self.fitted_params.get("hill_gamma", [0.5] * n_channels))
        else:
            hill_alpha = np.ones(n_channels) * 1.5
            hill_gamma = np.ones(n_channels) * 0.5
        
        beta = np.array(channel_coefficients)
        
        def objective(allocation):
            """Maximize expected revenue (minimize negative)."""
            saturated = self.hill_saturation(allocation, hill_alpha, hill_gamma)
            revenue = np.sum(beta * saturated)
            return -revenue
        
        # Constraints
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - total_budget}]
        
        # Bounds
        if min_per_channel is None:
            min_per_channel = [0] * n_channels
        if max_per_channel is None:
            max_per_channel = [total_budget] * n_channels
        
        bounds = list(zip(min_per_channel, max_per_channel))
        
        # Initial guess: proportional to coefficients
        initial = total_budget * beta / beta.sum()
        
        result = minimize(
            objective, initial, 
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        optimal_allocation = result.x
        expected_revenue = -result.fun
        
        return {
            "optimal_allocation": optimal_allocation.tolist(),
            "expected_revenue": float(expected_revenue),
            "allocation_pct": (optimal_allocation / total_budget * 100).tolist(),
            "marginal_roas": self._calculate_marginal_roas(optimal_allocation, beta, hill_alpha, hill_gamma)
        }
    
    def _calculate_marginal_roas(self, allocation: np.ndarray, beta: np.ndarray,
                                  alpha: np.ndarray, gamma: np.ndarray) -> List[float]:
        """
        Calculate marginal ROAS at current allocation point.
        """
        epsilon = 10  # Small budget increment
        marginal_roas = []
        
        for ch in range(len(allocation)):
            # Current revenue
            saturated = self.hill_saturation(allocation, alpha, gamma)
            current_rev = np.sum(beta * saturated)
            
            # Revenue with small increment
            allocation_plus = allocation.copy()
            allocation_plus[ch] += epsilon
            saturated_plus = self.hill_saturation(allocation_plus, alpha, gamma)
            new_rev = np.sum(beta * saturated_plus)
            
            mroas = (new_rev - current_rev) / epsilon
            marginal_roas.append(float(mroas))
        
        return marginal_roas
    
    # ============================================================
    # FULL ENTERPRISE PIPELINE
    # ============================================================
    
    def run_enterprise_optimization(self, total_budget: float, 
                                     channels: List[str],
                                     spend_history: np.ndarray, 
                                     revenue_history: np.ndarray,
                                     synergy_config: Optional[Dict] = None) -> Dict:
        """
        Full enterprise optimization pipeline:
        1. Auto-tune hyperparameters
        2. Run PyMC inference
        3. Apply channel synergy
        4. Optimize budget allocation
        5. Return optimized allocation with credibility intervals
        """
        # Step 1: Auto-tune hyperparameters
        print("Step 1/4: Auto-tuning hyperparameters...")
        tuned_params = self.auto_tune_hyperparameters(spend_history, revenue_history)
        
        # Step 2: Bayesian inference
        print("Step 2/4: Running Bayesian inference...")
        posteriors = self.run_pymc_inference(spend_history, revenue_history, channels)
        
        # Step 3: Configure synergy if provided
        if synergy_config:
            print("Step 3/4: Applying channel synergy...")
            self.set_channel_synergy(channels, synergy_config)
        else:
            print("Step 3/4: No synergy config provided, skipping...")
        
        # Step 4: Optimize budget
        print("Step 4/4: Optimizing budget allocation...")
        coefficients = posteriors["posterior_means"]
        if self.synergy_matrix is not None:
            coefficients = self.apply_synergy(np.array(coefficients)).tolist()
        
        optimization = self.optimize_budget(total_budget, coefficients)
        
        return {
            "channels": channels,
            "optimal_allocation": optimization["optimal_allocation"],
            "allocation_pct": optimization["allocation_pct"],
            "expected_revenue": optimization["expected_revenue"],
            "marginal_roas": optimization["marginal_roas"],
            "posterior_coefficients": posteriors,
            "tuned_parameters": tuned_params,
            "synergy_matrix": self.synergy_matrix.tolist() if self.synergy_matrix is not None else None,
            "tier": "enterprise"
        }


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def run_enterprise_mmm_pipeline(spend_df: 'pd.DataFrame',
                                 revenue_series: 'pd.Series',
                                 total_budget: float,
                                 synergy_config: Optional[Dict] = None) -> Dict:
    """
    Complete enterprise MMM optimization pipeline.
    
    Args:
        spend_df: DataFrame with columns as channels, rows as time periods
        revenue_series: Revenue per time period
        total_budget: Budget to allocate
        synergy_config: Optional channel synergy configuration
    
    Returns:
        Complete optimization results
    """
    optimizer = EnterpriseMMOptimizer()
    
    channels = spend_df.columns.tolist()
    spend_data = spend_df.values
    revenue_data = revenue_series.values
    
    return optimizer.run_enterprise_optimization(
        total_budget=total_budget,
        channels=channels,
        spend_history=spend_data,
        revenue_history=revenue_data,
        synergy_config=synergy_config
    )
