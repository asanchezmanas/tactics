# Engine A: Customer Intelligence (LTV & Churn)

> **Availability**: 🟢 Core (BG/NBD) | 🔵 Enterprise (Deep Learning LSTM)

This engine is the "Predictive CRM" of Tactics. It transforms historical transaction data into a forward-looking map of customer value and risk.

## 1. Core Algorithm: Pareto/NBD & Gamma-Gamma
We use a hierarchical Bayesian approach to model customer behavior in non-contractual settings (where customers don't "cancel" explicitly but stop buying).

### A. Transaction Model (Pareto/NBD)
- **Objective**: Determine if a customer is still "Alive" (Prob(Alive)) and how many purchases they will make in the future.
- **Parameters**: 
  - `r`, `alpha`: Shape and scale for the Gamma distribution of the purchase rate ($\lambda$).
  - `s`, `beta`: Shape and scale for the Gamma distribution of the death rate ($\mu$).
- **Business Logic**: Unlike a simple RFM, this model accounts for the *recency* of a customer relative to their total *age* (T). A customer who bought once 2 years ago is different from one who bought once 2 days ago.

### B. Monetary Model (Gamma-Gamma)
- **Objective**: Predict the average transaction value (Monetary Value).
- **Assumption**: We assume that the monetary value is independent of the purchase frequency.
- **Output**: The "True" average spend per customer, adjusted for the noise of one-off high/low transactions.

## 2. Technical Specifications
- **Input Data**: `customer_id`, `order_date`, `revenue`.
- **Pre-processing (RFM Transformation)**:
  - **Frequency**: Count of repeat purchases (Recurrence).
  - **Recency**: Duration between the first and last purchase.
  - **T (Age)**: Duration between the first purchase and the current analysis date.
- **Uncertainty**: Monte Carlo simulations (30+ iterations) generate 90% confidence intervals for 12-month LTV, moving from point estimates to risk-aware projections.

### 💻 Implementation Reference
- **File**: [core/engine.py](file:///c:/Users/Artur/tactics/core/engine.py)
- **Class**: `DataScienceCore`
- **Method**: `predict()`
- **Validation**: `validate_model()`

### 🛠️ Strategic Improvements (Proposed)
1. **Mathematical Uncertainty**: Replace the current `np.random.normal` factor in `predict()` with a rigorous **Standard Error** perturbation of the BG/NBD parameters ($r, \alpha, a, b$) to produce true Bayesian intervals.
2. **True Holdout Validation**: Upgrade `validate_model()` to use `lifetimes.utils.calibration_and_holdout_data`, calculating MAE (Mean Absolute Error) for predicted transactions vs actual.
3. **Cohort Drift Detection**: Add a monitor that detects if new cohorts (e.g., Black Friday acquisition) have significantly different LTV profiles than expected.

---

## 🔵 Enterprise Tier: SOTA 2024 Features

### D. Deep Learning LTV (LSTM)
- **Objective**: Achieve R² > 0.90 for datasets with +50k customers.
- **Architecture**: LSTM (Long Short-Term Memory) network that processes sequential purchase history.
- **Advantage**: Captures complex temporal patterns that BG/NBD cannot model (seasonal behavior, event-driven purchases).
- **Implementation**: `core/engine_enterprise.py` (Future)

### E. Multi-Source Feature Expansion
- **Objective**: Go beyond RFM to include web engagement, email opens, and demographic data.
- **Logic**: A feature vector per customer that feeds into the LSTM, dramatically improving prediction quality.

### F. Cohort Drift Detection
- **Objective**: Alert when new customer cohorts deviate from historical patterns.
- **Metric**: KL-Divergence between the LTV distribution of new cohorts vs historical baseline.
- **Trigger**: Automatic alert in Dashboard when divergence exceeds threshold.

## 3. Business Applications
- **Churn Radar**: Identify "VIP at Risk" customers (High LTV + Low Prob(Alive)) to trigger rescue campaigns via Meta/Klaviyo.
- **Potential Whales**: Identify new customers who exhibit signatures of high-value recurrence despite low historical spend.
- **Financial Projections**: Forecast the next 12 months of revenue from the existing customer base with quantified certainty.
