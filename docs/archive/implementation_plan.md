# Core Algorithms Implementation Plan

This plan outlines the first phase of the "Marketing AI Insights" project: building the data science core.

## Proposed Changes

### [NEW] `core/engine.py` (file:///c:/Users/Artur/tactics/core/engine.py)
This file will contain the `DataScienceCore` class responsible for calculating Churn probability and LTV using the `lifetimes` library.
- Implementation of `prepare_data`: Transforming transaction data into RFM (Recency, Frequency, Monetary) format.
- Implementation of `predict`: Fitting BG/NBD and Gamma-Gamma models to predict `prob_alive` and `clv_12m`.

### [NEW] `core/optimizer.py` (file:///c:/Users/Artur/tactics/core/optimizer.py)
This file will handle the Marketing Mix Modeling (MMM) and budget optimization logic.
- `adstock_filter`: Implementing geometric decay for marketing spend.
- `hill_function`: Implementing non-linear saturation for marketing channels.
- `run_budget_optimization`: Using `scipy.optimize.minimize` to find the optimal budget distribution based on predicted LTV.

### [NEW] `core/segmentation.py` (file:///c:/Users/Artur/tactics/core/segmentation.py)
This file will contain the business logic to categorize customers into segments (e.g., VIP, At Risk, Loyal) based on model outputs.

### [NEW] `requirements.txt` (file:///c:/Users/Artur/tactics/requirements.txt)
Define project dependencies:
- `fastapi`
- `uvicorn[standard]`
- `pandas`
- `numpy`
- `lifetimes`
- `scipy`
- `supabase`
- `python-dotenv`

## Verification Plan

### Automated Tests
- **Unit Tests**: Create `tests/test_core.py` to verify:
  - RFM transformation works as expected with sample data.
  - Churn and LTV models produce reasonable outputs.
  - Budget optimizer correctly distributes budget given sample saturation parameters.
- **Command**: `pytest tests/test_core.py`

### Manual Verification
- Review the generated segments for a synthetic dataset to ensure the logic aligns with business requirements.
- Verify the mathematical consistency of the budget optimization (sum of budgets = total budget).
