# Unified Technical Engine Specifications v2.0

> **Architecture**: Strategy-based Unified Modules
> **Status**: Consolidated V2 Documentation

This document provides a unified technical specification for Tactics' intelligence engines, which have been consolidated into flexible, strategy-driven modules.

## 1. Intelligence Engine (`core/engine_v2.py`)

The Intelligence Engine consolidates Customer Intelligence (LTV & Churn) and Profit Matrix logic.

### A. Customer Intelligence (LTV/Churn)
- **Core Algorithm**: hierarchical Bayesian models for non-contractual settings.
- **Strategies**:
    - `StatisticalStrategy`: Uses BG/NBD and Gamma-Gamma (Lifetimes) for robust, efficient predictions.
    - `NeuralStrategy`: Uses LSTM networks for complex temporal pattern recognition (Enterprise Tier).
- **Key Metrics**: `Prob(Alive)`, `Predicted Purchases`, `12-month LTV`.

### B. Profit Matrix Intelligence
- **Algorithms**: ECLAT/Apriori for association rules and Thompson Sampling/LinUCB for offer optimization.
- **Personalization**: Uses output from LTV segments (Engine A) to recommend profit-optimized bundles.

---

## 2. Marketing Mix Modeling (`core/optimizer_v2.py`)

The MMM Optimizer acts as the "Strategic Advisor," attributing sales to channels and optimizing budget allocation.

### A. Response Modeling
- **Adstock**: Geometric and Weibull decay to model the carryover effect of advertising.
- **Saturation**: Hill and Michaelis-Menten functions to model diminishing returns.

### B. Solver Backends
- **Standard**: SLSQP (Scipy) for deterministic global optimization.
- **Enterprise**: PyMC-Marketing for full Bayesian inference and credible intervals.
- **Optimization**: Multi-Armed Bandit (Nevergrad) for automated hyperparameter tuning.

---

## 3. Cross-Engine Synergy

The V2 architecture enables seamless data flow between modules:
1. **LTV -> Profit**: High-risk VIP segments trigger high-retention bundles.
2. **MMM -> Forecast**: Optimized budgets feed into forward-looking financial projections.
3. **Integrity -> Engines**: Unified data validation ensures consistent intelligence quality across all tiers.
