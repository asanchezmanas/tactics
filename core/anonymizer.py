"""
Data Anonymizer for Case Studies
Generates privacy-preserving datasets for public sharing and marketing.
"""

import pandas as pd
import numpy as np
import uuid
import hashlib
from typing import Dict, List, Any

class DataAnonymizer:
    """Anonymizes Tactics data for public case studies."""
    
    def __init__(self, salt: str = "tactics_sota"):
        self.salt = salt

    def anonymize_sales(self, df: pd.DataFrame) -> pd.DataFrame:
        """Anonymizes sales data: hashes IDs and perturbs amounts."""
        if df.empty:
            return df
            
        res = df.copy()
        
        # 1. Hash Customer IDs
        res['customer_id'] = res['customer_id'].apply(
            lambda x: hashlib.sha256(f"{x}{self.salt}".encode()).hexdigest()[:12]
        )
        
        # 2. Hash Transaction IDs
        if 'id' in res.columns:
            res['id'] = res['id'].apply(
                lambda x: f"anon_{hashlib.md5(f'{x}'.encode()).hexdigest()[:8]}"
            )
            
        # 3. Perturb Revenue (±5% noise to prevent exact reverse-engineering)
        res['revenue'] = res['revenue'] * (1 + np.random.uniform(-0.05, 0.05, size=len(res)))
        res['revenue'] = res['revenue'].round(2)
        
        # 4. Remove sensitive PII if exists
        cols_to_drop = ['email', 'name', 'phone', 'address', 'shipping_address']
        res = res.drop(columns=[c for c in cols_to_drop if c in res.columns])
        
        return res

    def anonymize_marketing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Anonymizes marketing spend data."""
        if df.empty:
            return df
            
        res = df.copy()
        
        # Perturb Spend
        res['spend'] = res['spend'] * (1 + np.random.uniform(-0.03, 0.03, size=len(res)))
        res['spend'] = res['spend'].round(2)
        
        return res

    def generate_case_study_data(self, sales_df: pd.DataFrame, marketing_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Full suite anonymization for a public case study."""
        return {
            "sales": self.anonymize_sales(sales_df),
            "marketing": self.anonymize_marketing(marketing_df)
        }
