# Engine B: Marketing Mix Modeling (MMM Optimizer)

> **Availability**: 🟢 Core (SLSQP + Monte Carlo) | 🔵 Enterprise (PyMC Bayesian + Channel Synergy)

This engine acts as the "Strategic Advisor" of Tactics. It uses statistical modeling to attribute sales to various marketing channels and optimize budget allocation without relying on tracking cookies.

## 1. Core Algorithm: Multi-Channel Bayesian Optimization
Unlike traditional attribution (Last-Click), MMM looks at the relationship between aggregate spending and total sales, accounting for external factors.

### 💻 Implementation Reference
- **File**: [core/optimizer.py](file:///c:/Users/Artur/tactics/core/optimizer.py)
- **Adstock Functions**: `adstock_geometric`, `adstock_weibull`
- **Saturation Functions**: `hill_saturation`, `michaelis_menten_saturation`
- **Optimizer**: `run_budget_optimization_bayesian`
- **Objective**: Model the "carryover" effect of advertising.
- **Logic**: A dollar spent on Monday doesn't just impact Monday's sales; its effect decays over time.
- **SOTA v2.0 Implementation**: We use **Weibull Adstock**, which allows for both traditional geometric decay and complex "delayed peak" patterns (common in influencer marketing or branding).

### B. Saturation (Hill function)
- **Objective**: Model the law of diminishing returns.
- **Logic**: Increasing the budget in a channel eventually yields less marginal revenue as the audience becomes saturated.
- **Output**: The "Saturation Ceiling" for each channel, telling the user exactly when to stop spending in Meta to move budget to Google.

### C. Budget Optimizer (SLSQP)
- **Objective**: Find the global optimum budget distribution.
- **Algorithm**: Sequential Least Squares Programming (SLSQP) to maximize revenue subject to budget constraints.

## 2. Technical Specifications
- **Input Data**: 
  - Daily spend per channel (Meta, Google, TikTok, Amazon).
  - Daily organic traffic (SEO/Baseline).
  - Daily global revenue.
- **Optimization Iterations**: 100+ Monte Carlo iterations to simulate uncertainty and provide Bayesian confidence ranges for ROI.

## 3. Business Applications
- **The Budget Simulator**: A "What-If" tool where the user moves sliders to see the projected impact of different budget allocations on total revenue.
- **Waste Identification**: Automatically flagging channels where the marginal return is lower than the cost of procurement.
- **Baseline Discovery**: Quantifying how many sales are truly "Organic" (occurring without any ad spend), preventing over-counting of marketing impact.
### 🛠️ Strategic Improvements (Proposed)
1. **Dynamic Decay Fitting**: Currently, the `decay` (geometric) or `shape/scale` (weibull) factors are manual or perturbed. We should implement a "Grid Search" or "Bayesian Search" to fit these factors based on historical $R^2$.
2. **Channel Interaction**: Add a "Synergy Coefficient" to model how channels boost each other (e.g., Meta boosting Google Search volume).
3. **Automated Baseline**: Integrate [api/connectors.py](file:///c:/Users/Artur/tactics/api/connectors.py) directly with the organic traffic data to automate the `baseline` calculation.

---

## 🔵 Enterprise Tier: SOTA 2024 Features

### D. PyMC-Marketing Integration
- **Objective**: Replace SLSQP with full Bayesian inference using `pymc-marketing`.
- **Advantage**: True posterior distributions for channel coefficients, not just point estimates.
- **Output**: Credibility intervals (not just confidence intervals) that account for model uncertainty.
- **Implementation**: `core/optimizer_enterprise.py` (Future)

### E. Channel Synergy Matrix
- **Objective**: Model cross-channel interaction effects.
- **Logic**: A matrix of synergy coefficients where `synergy[Meta, Google] = 1.15` means Meta boosts Google's effectiveness by 15%.
- **Business Value**: Identifies "power combinations" of channels that work better together.

### F. Automated Hyperparameter Tuning (Nevergrad)
- **Objective**: Automatically fit adstock decay and saturation parameters.
- **Algorithm**: Nevergrad (Meta's gradient-free optimizer) to search the hyperparameter space.
- **Output**: Optimal `decay`, `shape`, `scale`, and Hill parameters per channel without manual tuning.
