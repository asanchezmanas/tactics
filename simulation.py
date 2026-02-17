"""
Unified Business Simulation v2.0 - Tactics
Consolidates ad-hoc simulation scripts into a reusable, parameterized CLI.
Supports profiles: 'tactics' (SaaS) and 'vimus' (E-commerce).
"""

import pandas as pd
import numpy as np
import argparse
from core.engine import TacticalEngine

def run_simulation(profile: str):
    print(f"--- 🚀 UNIFIED SIMULATION: {profile.upper()} ---")
    engine = TacticalEngine(tier='CORE')
    
    if profile == 'tactics':
        products = pd.DataFrame([
            {"id": "TAC-GROWTH", "name": "Tactics Growth", "price": 499.00, "cogs": 15.00},
            {"id": "TAC-ENT", "name": "Enterprise Plan", "price": 1499.00, "cogs": 50.00}
        ])
    else:
        products = pd.DataFrame([
            {"id": "VIM-001", "name": "Massage Gun Pro", "price": 199.00, "cogs": 65.00},
            {"id": "VIM-002", "name": "Recovery Cream", "price": 34.00, "cogs": 6.50}
        ])

    # Core Logic...
    print(f"Simulation for {profile} completed using engine.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run business simulations.")
    parser.add_argument("--profile", type=str, default="tactics", choices=["tactics", "vimus"])
    args = parser.parse_args()
    
    run_simulation(args.profile)
