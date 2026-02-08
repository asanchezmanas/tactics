import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple
from .config import ALGORITHM_CONFIG

class ProfitMatrixEngine:
    def __init__(self, config=None):
        self.config = config or ALGORITHM_CONFIG.get("profit", {})
        # Thompson Sampling: Store arm priors as {offer_id: (alpha, beta)}
        self.arm_priors: Dict[str, Tuple[float, float]] = {}
        # LinUCB: Store arm matrices as {offer_id: {"A": np.array, "b": np.array, "n": int}}
        self.linucb_arms: Dict[str, Dict] = {}

    def calculate_basket_rules(self, transactions: pd.DataFrame, min_support: float = 0.05):
        """
        Uses ECLAT association analysis to find product combinations.
        Input: DataFrame with [order_id, product_id]
        """
        if transactions.empty:
            return {"top_bundles": [], "frequent_itemsets": []}
        
        # Run ECLAT to get frequent itemsets
        frequent_itemsets = self.run_eclat(transactions, min_support)
        
        # Convert to pair-based rules for backwards compatibility
        basket = transactions.groupby('order_id')['product_id'].apply(list).tolist()
        total_orders = len(basket)
        
        from collections import Counter
        item_counts = Counter()
        for items in basket:
            for item in set(items):
                item_counts[item] += 1
        
        rules = []
        for itemset, support in frequent_itemsets:
            if len(itemset) == 2:
                items = list(itemset)
                prob_a = item_counts[items[0]] / total_orders
                prob_b = item_counts[items[1]] / total_orders
                lift = support / (prob_a * prob_b) if (prob_a * prob_b) > 0 else 0
                
                rules.append({
                    "items": items,
                    "support": round(support, 4),
                    "lift": round(lift, 2),
                    "frequency": int(support * total_orders)
                })
        
        return {
            "top_bundles": sorted(rules, key=lambda x: x['lift'], reverse=True)[:5],
            "frequent_itemsets": [(list(fs), sup) for fs, sup in frequent_itemsets[:10]]
        }

    def run_eclat(self, transactions: pd.DataFrame, min_support: float = 0.05) -> List[Tuple[frozenset, float]]:
        """
        ECLAT Algorithm for Frequent Itemset Mining using vertical data format.
        
        Args:
            transactions: DataFrame with [order_id, product_id]
            min_support: Minimum support threshold (0.0 to 1.0)
            
        Returns:
            List of (itemset, support) tuples sorted by support descending.
        """
        if transactions.empty:
            return []
        
        # 1. Convert to vertical format: item -> set of transaction IDs
        vertical_db: Dict[str, set] = {}
        all_tids = set()
        
        for _, row in transactions.iterrows():
            tid = row['order_id']
            item = row['product_id']
            all_tids.add(tid)
            if item not in vertical_db:
                vertical_db[item] = set()
            vertical_db[item].add(tid)
        
        n_transactions = len(all_tids)
        min_count = min_support * n_transactions
        
        # 2. Filter single items by min_support
        frequent_1_itemsets = {
            frozenset([item]): tids 
            for item, tids in vertical_db.items() 
            if len(tids) >= min_count
        }
        
        # 3. ECLAT recursive mining
        all_frequent: List[Tuple[frozenset, float]] = []
        
        def eclat_recursive(prefix_itemset: frozenset, prefix_tids: set, remaining_items: List[frozenset]):
            for i, item_fset in enumerate(remaining_items):
                new_itemset = prefix_itemset | item_fset
                item = list(item_fset)[0]
                new_tids = prefix_tids & vertical_db.get(item, set())
                
                if len(new_tids) >= min_count:
                    support = len(new_tids) / n_transactions
                    all_frequent.append((new_itemset, support))
                    # Recurse with items that come after in the list (to avoid duplicates)
                    eclat_recursive(new_itemset, new_tids, remaining_items[i+1:])
        
        # Add 1-itemsets
        for itemset, tids in frequent_1_itemsets.items():
            all_frequent.append((itemset, len(tids) / n_transactions))
        
        # Start recursion with pairs
        sorted_items = sorted(frequent_1_itemsets.keys(), key=lambda x: list(x)[0])
        for i, itemset in enumerate(sorted_items):
            item = list(itemset)[0]
            eclat_recursive(itemset, vertical_db[item], sorted_items[i+1:])
        
        return sorted(all_frequent, key=lambda x: x[1], reverse=True)

    def calculate_unit_economics(self, product_metadata: pd.DataFrame, 
                                 marketing_data: Optional[pd.DataFrame] = None):
        """
        Calculates Net Margin per SKU.
        product_metadata: [id, name, price, cogs, shipping, storage_cost]
        marketing_data: [product_id, spend]
        """
        df = product_metadata.copy()
        
        # Gross Margin
        df['gross_margin'] = df['price'] - df['cogs']
        df['gross_margin_pct'] = (df['gross_margin'] / df['price']) * 100
        
        # Contribution Margin 1 (After Shipping)
        df['cm1'] = df['gross_margin'] - df['shipping']
        
        # Contribution Margin 2 (After Marketing/CAC - if available)
        if marketing_data is not None:
            # Assume we have units_sold to get spend per unit
            # For simplicity, if marketing_data has total_spend per product:
            df = df.merge(marketing_data, on='id', how='left').fillna(0)
            # This requires volume data which we'll simulate
        
        return df.sort_values(by='cm1', ascending=False)

    def get_personalized_bundle(self, customer_segment: str, product_pool: pd.DataFrame):
        """
        Cross-Engine Intelligence: Recommends bundles based on customer tier.
        """
        # Strategy lookup
        strategies = {
            "VIP_AT_RISK": {
                "goal": "Re-engagement",
                "discount": 0.20,
                "logic": "High LTV, bundle best-sellers with high-margin anchors"
            },
            "LOYAL": {
                "goal": "LTV Expansion",
                "discount": 0.10,
                "logic": "Upsell premium SKUs"
            },
            "NEW_POTENTIAL": {
                "goal": "Conversion",
                "discount": 0.15,
                "logic": "Low-friction 'Starter' bundle"
            }
        }
        
        strat = strategies.get(customer_segment, {"goal": "Standard", "discount": 0.05, "logic": "General offer"})
        
        # Filter products with margin > 40% to protect profit
        healthy_products = product_pool[product_pool['gross_margin_pct'] > 30]
        
        top_2 = healthy_products.sort_values(by='gross_margin', ascending=False).head(2)
        
        return {
            "segment": customer_segment,
            "recommended_items": top_2['name'].tolist(),
            "applied_discount": strat['discount'],
            "strategy_goal": strat['goal'],
            "logic": strat['logic'],
            "expected_net_margin": (top_2['cm1'].sum() * (1 - strat['discount']))
        }

    def linucb_select_offer(self, context_features: np.ndarray, offers: list, alpha=1.0):
        """
        Contextual Bandit (LinUCB) for SOTA offer selection.
        
        LEARNS from feedback via linucb_update().
        
        Input:
            context_features: np.array of shape (d,) representing customer/session context.
            offers: List of offer dicts, each with an 'id'.
            alpha: Exploration parameter (higher = more exploration).
        Output:
            Dict with selected offer and UCB scores for all arms.
        """
        d = len(context_features)
        best_offer = None
        best_ucb = -np.inf
        all_scores = {}
        
        for offer in offers:
            offer_id = offer.get('id', str(offer))
            
            # Get or initialize arm state
            arm = self.linucb_arms.setdefault(offer_id, {
                "A": np.eye(d),
                "b": np.zeros(d),
                "n": 0
            })
            
            # Compute A_inv and theta
            try:
                A_inv = np.linalg.inv(arm["A"])
            except np.linalg.LinAlgError:
                # If matrix is singular, reset to identity
                arm["A"] = np.eye(d)
                A_inv = np.eye(d)
            
            theta = A_inv @ arm["b"]
            
            # Calculate UCB
            x = context_features
            exploitation = theta.T @ x
            exploration = alpha * np.sqrt(x.T @ A_inv @ x)
            ucb = exploitation + exploration
            
            all_scores[offer_id] = {
                "ucb": float(ucb),
                "exploitation": float(exploitation),
                "exploration": float(exploration),
                "n_samples": arm["n"]
            }
            
            if ucb > best_ucb:
                best_ucb = ucb
                best_offer = offer
        
        return {
            "selected_offer": best_offer,
            "ucb_score": float(best_ucb),
            "all_scores": all_scores
        }
    
    def linucb_update(self, offer_id: str, context: np.ndarray, reward: float) -> Dict:
        """
        Updates LinUCB arm after observing reward.
        
        Args:
            offer_id: The ID of the offer that was shown.
            context: The context vector that was used for selection.
            reward: The observed reward (e.g., 1 for conversion, 0 for no conversion).
        
        Returns:
            Updated arm statistics.
        """
        d = len(context)
        arm = self.linucb_arms.setdefault(offer_id, {
            "A": np.eye(d),
            "b": np.zeros(d),
            "n": 0
        })
        
        # Update A and b
        arm["A"] = arm["A"] + np.outer(context, context)
        arm["b"] = arm["b"] + reward * context
        arm["n"] += 1
        
        # Compute current theta estimate
        try:
            A_inv = np.linalg.inv(arm["A"])
            theta = A_inv @ arm["b"]
        except np.linalg.LinAlgError:
            theta = np.zeros(d)
        
        return {
            "offer_id": offer_id,
            "n_samples": arm["n"],
            "theta_norm": float(np.linalg.norm(theta)),
            "A_condition": float(np.linalg.cond(arm["A"]))
        }
    
    def get_linucb_state(self) -> Dict[str, Dict]:
        """Returns the current state of all LinUCB arms for persistence."""
        return {
            offer_id: {
                "A": arm["A"].tolist(),
                "b": arm["b"].tolist(),
                "n": arm["n"]
            }
            for offer_id, arm in self.linucb_arms.items()
        }
    
    def load_linucb_state(self, state: Dict[str, Dict]):
        """Loads LinUCB arm state from external storage."""
        for offer_id, data in state.items():
            self.linucb_arms[offer_id] = {
                "A": np.array(data["A"]),
                "b": np.array(data["b"]),
                "n": data.get("n", 0)
            }

    # ===== THOMPSON SAMPLING (Beta-Binomial Model) =====
    
    def thompson_sampling_select(self, offers: List[Dict]) -> Dict:
        """
        Thompson Sampling for A/B testing of offer variants.
        Uses a Beta-Binomial model: each arm has a Beta(alpha, beta) prior.
        
        Args:
            offers: List of offer dicts, each with an 'id'.
            
        Returns:
            Dict with selected_offer and all sampled_values for transparency.
        """
        sampled_values = {}
        best_offer = None
        best_sample = -1.0
        
        for offer in offers:
            offer_id = offer.get('id', str(offer))
            # Get prior or initialize with uniform prior Beta(1, 1)
            alpha, beta = self.arm_priors.get(offer_id, (1.0, 1.0))
            
            # Sample from Beta distribution
            sample = np.random.beta(alpha, beta)
            sampled_values[offer_id] = {
                "sample": round(sample, 4),
                "alpha": alpha,
                "beta": beta,
                "mean": round(alpha / (alpha + beta), 4)
            }
            
            if sample > best_sample:
                best_sample = sample
                best_offer = offer
        
        return {
            "selected_offer": best_offer,
            "winning_sample": round(best_sample, 4),
            "all_samples": sampled_values
        }
    
    def thompson_sampling_update(self, offer_id: str, success: bool) -> Dict:
        """
        Updates the Thompson Sampling arm prior based on observed outcome.
        
        Args:
            offer_id: The ID of the offer that was shown.
            success: True if the offer converted (click/purchase), False otherwise.
            
        Returns:
            Updated prior for the arm.
        """
        alpha, beta = self.arm_priors.get(offer_id, (1.0, 1.0))
        
        if success:
            alpha += 1
        else:
            beta += 1
        
        self.arm_priors[offer_id] = (alpha, beta)
        
        return {
            "offer_id": offer_id,
            "new_alpha": alpha,
            "new_beta": beta,
            "estimated_ctr": round(alpha / (alpha + beta), 4)
        }
    
    def get_thompson_state(self) -> Dict[str, Dict]:
        """Returns the current state of all Thompson Sampling arms for persistence."""
        return {
            offer_id: {"alpha": a, "beta": b, "mean": round(a / (a + b), 4)}
            for offer_id, (a, b) in self.arm_priors.items()
        }
    
    def load_thompson_state(self, state: Dict[str, Dict]):
        """Loads Thompson Sampling arm state from external storage (e.g., database)."""
        for offer_id, params in state.items():
            self.arm_priors[offer_id] = (params.get('alpha', 1.0), params.get('beta', 1.0))

