# Engine C: Profit Matrix (Product & Unit Economics)

> **Availability**: 🟢 Core (Unit Economics + ECLAT) | 🔵 Enterprise (LinUCB + Cross-Engine Intelligence)

This engine is the "Profit Guardian" of Tactics. It goes beyond top-line revenue to examine the **Unit Economics** of every SKU and the hidden associations between products.

## 1. Core Algorithm: Profit-Aware Associative Intelligence
We combine association rule learning with unit economics optimization to find the most profitable product configurations.

### A. Market Basket Analysis (ECLAT/Apriori)
- **Objective**: Identify which products are frequently bought together (Association).
- **Metric**: we focus on **Support** (how often it appears) and **Lift** (how much the presence of A increases the likelihood of B).
- **SOTA Application**: Instead of just recommending "frequently bought together," Engine C filters these associations by **Net Margin** to recommend bundles that maximize profit, not just volume.

### B. Unit Economics Optimizer
- **Objective**: Calculate the "True Margin" per SKU.
- **Logic**: Net Revenue = Gross Sales - COGS - Shipping - **Storage Fees** - **Cost of Caducity (Expiration Risk)** - Pauta-Atribuida.
- **Flexibility**: The model allows for optional toggling of costs (e.g., if a product doesn't expire or has zero storage fees).
- **Output**: Identification of "Profit Whales" (high margin, high velocity) and "Margin Bleeders" (low margin, high complexity).

### C. Dynamic Offer Testing (Thompson Sampling)
- **Objective**: Optimize price elasticity and volume discounts.
- **Approach**: A Multi-Armed Bandit (Bayesian) framework that tests different offers (e.g., "Buy 2 Get 1" vs. "20% Discount") and quickly shifts traffic to the one yielding the highest expected profit.

### D. Cross-Engine Intelligence (SOTA 2024)
- **Objective**: Personalize bundles based on the customer's predicted value and risk profile.
- **Logic**: Engine C consumes the output of **Engine A** (LTV segment: VIP, At Risk, New Potential) to recommend different bundles to different customer cohorts.
- **Example**: A "VIP at Risk" customer might receive a high-margin bundle with a personalized discount to increase retention, while a "New Potential" customer receives a low-risk introductory bundle.

### E. Contextual Bandit (LinUCB - SOTA 2024)
- **Objective**: Move beyond simple A/B testing to **context-aware offer optimization**.
- **Algorithm**: **LinUCB (Linear Upper Confidence Bound)**, which uses a feature vector (customer segment, time of day, cart value, etc.) to select the offer with the highest expected reward.
- **Advantage over Thompson Sampling**: LinUCB learns faster in high-dimensional environments and can generalize across customer types without needing massive sample sizes per cohort.

### 2. Technical Specifications
- **Input Data**: 
  - **Product Metadata**: Costs (COGS), inventory levels, **storage fees (fixed/variable)**, and **expiration dates (shelf life)**.
  - **Temporal Context**: **Seasonality Factors** (e.g., higher storage cost in Q4, or lower price elasticity in summer).
  - **Order Details**: Bundle compositions and discount codes used.
  - **Variable costs**: Shipping rates, handling.
- **Future Scale**: Path toward **Deep Q-Network (DQN)** for real-time reinforcement learning of replenishment and pricing strategies.

## 3. Business Applications
- **The Bundle Architect**: Recommending product pairings to increase Average Order Value (AOV) while protecting margins.
- **Seasonal Liquidation**: Using seasonality curves to predict when a product's demand will drop and suggesting bundles to liquidate stock before expiration.
- **Deadstock Rescue**: Identifying low-velocity products with high storage costs and suggesting bundles with "Whales" to clear inventory at the lowest possible cost.
- **Profit-First Discounting**: Calculating the exact discount threshold where volume offsets the margin loss.
### 🚀 Phase 9 Implementation Roadmap
- **File Target**: `core/profit.py` (New)
- **Complexity**: High (Recursive Bundle Search)
- **Data Gap**: We need to extend the `ventas` table or order-level metadata to include `product_id` and `discount_code` for the association rules to work.

### 🛠️ Proposed Class Structure
```python
class ProfitMatrixEngine:
    def calculate_basket_rules(self, transactions):
        # Uses ECLAT/Apriori for Lift/Support
        pass
        
    def optimize_unit_economics(self, product_costs, ad_spend, seasonality_factor):
        # Calculates True Margin per SKU with optional costs
        pass
        
    def simulate_offer(self, offer_type, base_margin):
        # Thompson Sampling simulation
        pass
    
    # SOTA 2024 Methods
    def get_personalized_bundle(self, customer_segment, available_products):
        # Cross-Engine: Uses Engine A output for personalization
        pass
    
    def linucb_select_offer(self, context_features, offers, alpha=1.0):
        # Contextual Bandit for context-aware offer optimization
        pass
```
