"""
Advanced Business Metrics Factory
Derives high-value BI indicators from base data and provides feedback loops for AI models.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

@dataclass
class BusinessMetricsReport:
    """Standardized report for business metrics."""
    company_id: str
    generated_at: str
    growth: Dict[str, Any]
    unit_economics: Dict[str, Any]
    retention: Dict[str, Any]
    efficiency: Dict[str, Any]
    synthesis: Dict[str, Any]
    deep_synthesis: Dict[str, Any]
    signals_for_ai: Dict[str, Any]

class BusinessMetricsFactory:
    """Engine for calculating derived business metrics and AI reinforcement signals."""
    
    def __init__(self, company_id: str):
        self.company_id = company_id

    def calculate_all(self, sales_df: pd.DataFrame, marketing_df: pd.DataFrame) -> BusinessMetricsReport:
        """Orchestrates all metric calculations."""
        # Ensure dates are datetime
        if not sales_df.empty:
            sales_df['order_date'] = pd.to_datetime(sales_df['order_date'])
        if not marketing_df.empty:
            marketing_df['fecha'] = pd.to_datetime(marketing_df['fecha'])
            
        growth = self._calculate_growth(sales_df)
        unit_economics = self._calculate_unit_economics(sales_df, marketing_df)
        retention = self._calculate_cohort_retention(sales_df)
        efficiency = self._calculate_efficiency(sales_df, marketing_df)
        synthesis = self._calculate_synthesis(sales_df, marketing_df)
        deep_synthesis = self._calculate_deep_synthesis(sales_df, marketing_df)
        
        # Signals for AI engines (Reinforced by deep synthesis)
        signals = {
            "retention_bias": retention.get("weighted_retention_rate", 0.0),
            "mer_historical_prior": efficiency.get("mer_lifetime", 0.0),
            "aov_stability": unit_economics.get("aov_stability", 1.0),
            "high_value_products": list(synthesis.get("gateway_products", {}).keys())[:3],
            "is_pareto_concentrated": deep_synthesis.get("pareto_concentration", {}).get("is_concentrated", False)
        }
        
        return BusinessMetricsReport(
            company_id=self.company_id,
            generated_at=datetime.now().isoformat(),
            growth=growth,
            unit_economics=unit_economics,
            retention=retention,
            efficiency=efficiency,
            synthesis=synthesis,
            deep_synthesis=deep_synthesis,
            signals_for_ai=signals
        )

    def _normalize_canal(self, canal: str) -> str:
        """Normalizes channel names to handle discrepancies (e.g. 'Meta' vs 'Facebook')."""
        if not canal or not isinstance(canal, str):
            return "unknown"
        
        c = canal.lower().strip()
        mapping = {
            "facebook": "meta",
            "fb": "meta",
            "instagram": "meta",
            "ig": "meta",
            "google ads": "google",
            "gads": "google",
            "search": "google",
            "youtube": "google",
            "yt": "google",
            "tiktok ads": "tiktok",
            "tt": "tiktok"
        }
        
        for key, val in mapping.items():
            if key in c:
                return val
        return c

    def _calculate_deep_synthesis(self, sales_df: pd.DataFrame, marketing_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Deep Synthesis (Intelligence 2.0 Deep Dives):
        - POAS (Profitability Over Ad Spend): Gross profit after marketing.
        - Pareto Concentration: 80/20 analysis of customers.
        - iROAS (Incremental ROAS): Diminishing returns curve (estimated).
        """
        if sales_df.empty:
            return {}

        results = {}

        # 1. Pareto Concentration (80/20)
        customer_revenue = sales_df.groupby('customer_id')['revenue'].sum().sort_values(ascending=False)
        total_rev = customer_revenue.sum()
        top_20_count = max(1, int(len(customer_revenue) * 0.2))
        top_20_rev = customer_revenue.iloc[:top_20_count].sum()
        
        concentration_ratio = top_20_rev / total_rev if total_rev > 0 else 0
        results['pareto_concentration'] = {
            "ratio_top_20": round(concentration_ratio, 2),
            "is_concentrated": concentration_ratio > 0.6,
            "top_customer_value": round(customer_revenue.iloc[0], 2) if not customer_revenue.empty else 0
        }

        # 2. POAS (Profitability Over Ad Spend)
        # Assumes a default COGS of 40% if not provided in products.
        if not marketing_df.empty:
            total_spend = marketing_df['inversion'].sum()
            total_revenue = sales_df['revenue'].sum()
            estimated_cogs = total_revenue * 0.4
            gross_profit = total_revenue - estimated_cogs
            
            poas = gross_profit / total_spend if total_spend > 0 else 0
            results['poas'] = round(poas, 2)
            results['break_even_roas'] = round(total_revenue / (total_revenue - estimated_cogs), 2) if (total_revenue - estimated_cogs) > 0 else 0

        # 3. iROAS (Diminishing Returns Heuristic)
        # We estimate the efficiency of the most recent 20% of spend vs total.
        if not marketing_df.empty and len(marketing_df) > 5:
            marketing_df = marketing_df.sort_values('fecha')
            split_idx = int(len(marketing_df) * 0.8)
            recent_spend = marketing_df.iloc[split_idx:]['inversion'].sum()
            
            # Correlate with recent sales
            sales_df = sales_df.sort_values('order_date')
            sales_split_idx = int(len(sales_df) * 0.8)
            recent_revenue = sales_df.iloc[sales_split_idx:]['revenue'].sum()
            
            recent_roas = recent_revenue / recent_spend if recent_spend > 0 else 0
            results['incremental_roas_estimate'] = round(recent_roas, 2)

        # 4. Basket Affinity (Intelligence 2.0 Feature)
        results['basket_affinity'] = self._calculate_basket_affinity(sales_df)

        return results

    def _calculate_basket_affinity(self, sales_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Market Basket Analysis (Simplified Eclat/Apriori):
        Calculates common product pairs and their lift.
        """
        if 'order_id' not in sales_df.columns or 'product_id' not in sales_df.columns:
            # Fallback if order_id is missing: use customer_id + date as proxy
            if 'customer_id' in sales_df.columns and 'order_date' in sales_df.columns:
                sales_df['order_proxy'] = sales_df['customer_id'].astype(str) + "_" + sales_df['order_date'].astype(str)
                id_col = 'order_proxy'
            else:
                return []
        else:
            id_col = 'order_id'

        import itertools
        from collections import Counter

        # Group products by order
        orders = sales_df.groupby(id_col)['product_id'].apply(list).tolist()
        orders = [list(set(o)) for o in orders if len(o) > 1] # Only orders with multi-products

        if not orders:
            return []

        # Count individual frequencies for support calculations
        item_counts = Counter()
        for order in orders:
            item_counts.update(order)
        
        total_orders = len(orders)
        
        # Count pairs
        pair_counts = Counter()
        for order in orders:
            pairs = itertools.combinations(sorted(order), 2)
            pair_counts.update(pairs)

        top_pairs = []
        for (p1, p2), count in pair_counts.most_common(5):
            support = count / total_orders
            # Simple Lift: P(A,B) / (P(A) * P(B))
            prob_p1 = item_counts[p1] / total_orders
            prob_p2 = item_counts[p2] / total_orders
            lift = support / (prob_p1 * prob_p2) if (prob_p1 * prob_p2) > 0 else 0
            
            top_pairs.append({
                "product_a": str(p1),
                "product_b": str(p2),
                "combined_orders": count,
                "lift": round(lift, 2),
                "confidence": round(count / item_counts[p1], 2)
            })

        return top_pairs

    def _calculate_synthesis(self, sales_df: pd.DataFrame, marketing_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Holistic Synthesis: Analyzes intersections between sources.
        - Gateway Products: Products that lead to higher repeat purchase.
        - Channel-LTV Alignment: Which channels bring the most valuable clients.
        """
        if sales_df.empty:
            return {}

        results = {}

        # 1. Gateway Products detection
        # Logic: Identify the first order for each customer and see which products
        # are in those orders for customers who became recurrent.
        try:
            # Sort by date
            sorted_sales = sales_df.sort_values(['customer_id', 'order_date'])
            first_orders = sorted_sales.groupby('customer_id').head(1)
            
            # Identify recurrent customers (count > 1)
            recurrent_ids = sales_df['customer_id'].value_counts()
            recurrent_ids = recurrent_ids[recurrent_ids > 1].index
            
            # Map products in first orders
            # (Assuming sales_df has a product_id or equivalent. If not, use revenue distribution)
            if 'product_id' in sales_df.columns:
                top_gateways = first_orders[first_orders['customer_id'].isin(recurrent_ids)]['product_id'].value_counts()
                results['gateway_products'] = top_gateways.head(5).to_dict()
            else:
                # Fallback: analyze by price point or channel
                results['gateway_products_fallback'] = "Missing product_id for granular analysis"
        except Exception:
            results['gateway_products_error'] = "Insufficient data for gateway analysis"

        # 2. Channel-LTV Alignment
        # Logic: Average LTV (total revenue per customer) grouped by the acquisition channel.
        if 'canal' in sales_df.columns:
            customer_ltv = sales_df.groupby('customer_id').agg({
                'revenue': 'sum',
                'canal': 'first' # Acquisition channel
            })
            channel_ltv = customer_ltv.groupby('canal')['revenue'].mean().sort_values(ascending=False)
            results['channel_ltv_alignment'] = channel_ltv.round(2).to_dict()

        # 3. Attribution Efficiency (Marketing Spend vs Sales Revenue)
        if not marketing_df.empty and 'canal' in sales_df.columns:
            channel_spend = marketing_df.groupby('canal')['inversion'].sum()
            channel_rev = sales_df.groupby('canal')['revenue'].sum()
            
            # Calculate ROAS per channel where possible
            blended_roas = (channel_rev / channel_spend).dropna()
            results['blended_roas_by_channel'] = blended_roas.round(2).to_dict()

        return results

    def _calculate_growth(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates MoM and WoW growth rates."""
        if df.empty:
            return {"mom": 0.0, "wow": 0.0}
            
        # Resample for monthly and weekly
        monthly = df.set_index('order_date').resample('ME')['revenue'].sum()
        weekly = df.set_index('order_date').resample('W')['revenue'].sum()
        
        def get_pct_change(series):
            if len(series) < 2: return 0.0
            last = series.iloc[-1]
            prev = series.iloc[-2]
            return (last - prev) / prev if prev > 0 else 0.0

        return {
            "mom": round(get_pct_change(monthly) * 100, 2),
            "wow": round(get_pct_change(weekly) * 100, 2),
            "last_month_revenue": float(monthly.iloc[-1]) if not monthly.empty else 0
        }

    def _calculate_unit_economics(self, sales_df: pd.DataFrame, marketing_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates AOV, CAC, and LTV/CAC ratio basics."""
        if sales_df.empty:
            return {"aov": 0.0, "cac": 0.0}

        aov = sales_df['revenue'].mean()
        
        # Simple CAC calculation
        total_spend = marketing_df['inversion'].sum() if not marketing_df.empty else 0
        new_customers = sales_df['customer_id'].nunique()
        cac = total_spend / new_customers if new_customers > 0 else 0
        
        # AOV Stability (Coefficient of variation of AOV over time)
        # Helper for AI model stability detection
        aov_over_time = sales_df.set_index('order_date').resample('ME')['revenue'].mean()
        stability = 1.0 - (aov_over_time.std() / aov_over_time.mean()) if len(aov_over_time) > 1 else 1.0
        
        return {
            "aov": round(float(aov), 2),
            "cac": round(float(cac), 2),
            "aov_stability": round(float(np.clip(stability, 0, 1)), 2)
        }

    def _calculate_cohort_retention(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates real cohort-based retention.
        Identifies return rates from captured users.
        """
        if df.empty or len(df) < 10:
            return {"weighted_retention_rate": 0.0}
            
        # Determine first purchase month for each customer
        df['cohort'] = df.groupby('customer_id')['order_date'].transform('min').dt.to_period('M')
        df['order_month'] = df['order_date'].dt.to_period('M')
        
        # Calculate periods since first purchase
        df['period_number'] = (df['order_month'] - df['cohort']).apply(lambda x: x.n)
        
        # Pivot to get cohort retention
        cohort_pivot = df.pivot_table(index='cohort', columns='period_number', values='customer_id', aggfunc='nunique')
        
        # Convert to percentages
        cohort_size = cohort_pivot.iloc[:, 0]
        retention_matrix = cohort_pivot.divide(cohort_size, axis=0)
        
        # Weighted retention (weighted by cohort size) for latest 3-6 months
        # Signal for "p_alive" reinforcement
        period_1_retention = retention_matrix[1].dropna() if 1 in retention_matrix.columns else pd.Series()
        
        weighted_retention = 0.0
        if not period_1_retention.empty:
            weights = cohort_size.loc[period_1_retention.index]
            weighted_retention = (period_1_retention * weights).sum() / weights.sum()
            
        return {
            "weighted_retention_rate": round(float(weighted_retention), 2),
            "matrix_summary": retention_matrix.iloc[-3:, :6].fillna(0).to_dict() if not retention_matrix.empty else {}
        }

    def _calculate_efficiency(self, sales_df: pd.DataFrame, marketing_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates MER (Marketing Efficiency Ratio)."""
        total_revenue = sales_df['revenue'].sum() if not sales_df.empty else 0
        total_spend = marketing_df['inversion'].sum() if not marketing_df.empty else 0
        
        mer = total_revenue / total_spend if total_spend > 0 else 0
        
        # Incremental MER (Latest 30 days)
        cutoff = datetime.now() - timedelta(days=30)
        recent_revenue = sales_df[sales_df['order_date'] >= cutoff]['revenue'].sum() if not sales_df.empty else 0
        recent_spend = marketing_df[marketing_df['fecha'] >= cutoff]['inversion'].sum() if not marketing_df.empty else 0
        
        recent_mer = recent_revenue / recent_spend if recent_spend > 0 else 0
        
        return {
            "mer_lifetime": round(float(mer), 2),
            "mer_recent": round(float(recent_mer), 2),
            "efficiency_status": "optimal" if mer >= 4 else "healthy" if mer >= 3 else "warning"
        }
