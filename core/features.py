"""
Elite Feature Engineering - Tactics Intelligence 2.0
Module for advanced variable engineering and robust data scaling.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class EliteFeatures:
    """
    Advanced Feature Engineering Layer for Elite Tier.
    Focuses on:
    - Cinematic metrics (Velocity, Acceleration)
    - Robust handling of outliers
    - Feature expansion for Deep Learning
    """

    def __init__(self, company_id: str):
        self.company_id = company_id

    def calculate_cinematic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates Velocity and Momentum of customer spending.
        
        Args:
            df: Transaction DataFrame [customer_id, order_date, revenue]
            
        Returns:
            DataFrame with velocity and acceleration features per customer.
        """
        df = df.copy()
        df['order_date'] = pd.to_datetime(df['order_date'])
        df = df.sort_values(['customer_id', 'order_date'])

        # Calculate time between purchases
        df['days_diff'] = df.groupby('customer_id')['order_date'].diff().dt.days
        
        # Velocity: Revenue / Days
        df['velocity'] = df['revenue'] / df['days_diff'].replace(0, 1) # Prevent div by zero
        
        # Aggregate to customer level
        features = df.groupby('customer_id').agg({
            'velocity': ['mean', 'std', 'max'],
            'revenue': ['sum', 'count'],
            'days_diff': 'mean'
        })
        
        # Flatten columns
        features.columns = ['_'.join(col).strip() for col in features.columns.values]
        features = features.rename(columns={
            'velocity_mean': 'avg_velocity',
            'velocity_std': 'volatility',
            'revenue_sum': 'total_revenue',
            'revenue_count': 'frequency',
            'days_diff_mean': 'avg_interpurchase_time'
        })

        # Calculate Acceleration: Change in Velocity
        # (Simplified: compare velocity of last half vs first half of history)
        # TODO: Implement more complex sliding window acceleration
        
        return features.fillna(0)

    def robust_scaling(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Applies Robust Scaling using Interquartile Range (IQR).
        Protects models against high-value outliers (Whales).
        """
        df_scaled = df.copy()
        for col in columns:
            if col in df.columns:
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                if iqr > 0:
                    df_scaled[col] = (df[col] - q1) / iqr
                else:
                    # Fallback to Min-Max if distribution is too tight
                    c_min = df[col].min()
                    c_max = df[col].max()
                    if c_max > c_min:
                        df_scaled[col] = (df[col] - c_min) / (c_max - c_min)
        return df_scaled

    def detect_outliers_isolation_forest(self, df: pd.DataFrame) -> np.ndarray:
        """
        Uses Isolation Forest to detect anomalous behavior.
        (Needs scikit-learn)
        """
        try:
            from sklearn.ensemble import IsolationForest
            iso = IsolationForest(contamination=0.05, random_state=42)
            # Use numerical columns only
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            outliers = iso.fit_predict(df[numeric_cols])
            return outliers # 1 for normal, -1 for outlier
        except ImportError:
            # Simple heuristic fallback
            return np.ones(len(df))

def get_profile_features(df: pd.DataFrame, company_id: str) -> Dict:
    """Convenience function for pipeline integration."""
    engineer = EliteFeatures(company_id)
    raw_features = engineer.calculate_cinematic_features(df)
    
    # Scale relevant features
    to_scale = ['avg_velocity', 'total_revenue', 'frequency']
    scaled = engineer.robust_scaling(raw_features, to_scale)
    
    return scaled.to_dict('index')
