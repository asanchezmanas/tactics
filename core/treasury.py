"""
Tactics Treasury Engine
Manages the allocation of surplus capital (War Chest / Profit) into yield-generating assets.
Focuses on low-volatility, income-generating vehicles (REITs, Dividend ETFs, Bonds).
"""

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Asset:
    symbol: str
    name: str
    asset_type: str # 'REIT', 'ETF', 'BOND', 'CASH'
    apy: float # Annual Percentage Yield (decimal, e.g., 0.05 for 5%)
    risk_level: str # 'LOW', 'MEDIUM', 'HIGH'
    allocation_target: float # Target percentage of treasury (0.0 - 1.0)
    
@dataclass
class Position:
    asset: Asset
    balance: float
    
    @property
    def monthly_yield(self) -> float:
        """Calculates expected monthly passive income."""
        return (self.balance * self.asset.apy) / 12

class TreasuryEngine:
    """
    Manages the company's investment portfolio to maximize yield on idle cash.
    """
    def __init__(self):
        self.portfolio: Dict[str, Position] = {}
        self.available_cash = 0.0
        
        # Define Investment Strategy (Conservative Growth)
        self.assets = [
            Asset("O", "Realty Income (The Monthly Dividend Company)", "REIT", 0.055, "LOW", 0.40),
            Asset("SCHD", "Schwab US Dividend Equity ETF", "ETF", 0.035, "LOW", 0.40),
            Asset("BIL", "SPDR Bloomberg 1-3 Month T-Bill", "BOND", 0.052, "LOW", 0.20)
        ]
        
        # Initialize positions
        for asset in self.assets:
            self.portfolio[asset.symbol] = Position(asset, 0.0)

    def deposit(self, amount: float):
        """Injects capital into the treasury."""
        self.available_cash += amount
        self.rebalance()

    def rebalance(self):
        """Allocates available cash according to targets."""
        total_value = self.total_value
        
        # Simple allocation logic: Move cash into assets to meet targets
        # In a real system, this would account for trading fees and exact shares.
        # Here we simulate partial shares.
        
        for asset in self.assets:
            target_value = total_value * asset.allocation_target
            current_value = self.portfolio[asset.symbol].balance
            
            diff = target_value - current_value
            
            # If we need to buy and have cash
            if diff > 0 and self.available_cash >= diff:
                self.portfolio[asset.symbol].balance += diff
                self.available_cash -= diff
            elif diff > 0 and self.available_cash < diff:
                # Invest remaining cash
                self.portfolio[asset.symbol].balance += self.available_cash
                self.available_cash = 0
            
            # We don't sell to rebalance in this simple version, we only buy with inflows.

    @property
    def total_value(self) -> float:
        invested = sum(p.balance for p in self.portfolio.values())
        return invested + self.available_cash

    @property
    def monthly_passive_income(self) -> float:
        return sum(p.monthly_yield for p in self.portfolio.values())

    def get_portfolio_status(self) -> List[Dict]:
        status = []
        for symbol, pos in self.portfolio.items():
            status.append({
                "Symbol": symbol,
                "Name": pos.asset.name,
                "Type": pos.asset.asset_type,
                "Balance": pos.balance,
                "Allocation": f"{(pos.balance / self.total_value * 100):.1f}%" if self.total_value > 0 else "0%",
                "Monthly Income": pos.monthly_yield
            })
        return status
