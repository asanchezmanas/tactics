"""
Tactics Financial Engine v2.0
Internal-only financial analytics for Tactics operations.

Features:
- Burn Rate & Runway Calculation
- LTV/CAC Analysis with Payback Period
- Break-even Analysis
- Cohort-based Revenue Analysis
- Automated Fund Allocation (Profit First)
- Monthly P&L Generation
- Integration with SecureVault for encrypted backup

NOT for client use - this is Tactics' own financial brain.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import json

# Try vault for encrypted backup
try:
    from .secure_vault import SecureVault
    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class Transaction:
    """Single financial transaction."""
    date: datetime
    amount: float  # Positive = inflow, Negative = outflow
    category: str  # 'revenue', 'cogs', 'opex', 'marketing', 'tax', etc.
    description: str = ""
    client_id: Optional[str] = None
    recurring: bool = False


@dataclass
class CohortMetrics:
    """Revenue metrics for a customer cohort."""
    cohort_month: str  # YYYY-MM
    customers: int
    revenue_m0: float
    revenue_m1: float = 0
    revenue_m2: float = 0
    revenue_m3: float = 0
    revenue_m6: float = 0
    revenue_m12: float = 0
    churn_rate: float = 0


@dataclass
class TacticsFinancials:
    """Tactics-specific financial state."""
    mrr: float = 0  # Monthly Recurring Revenue
    arr: float = 0  # Annual Run Rate
    cac: float = 0  # Customer Acquisition Cost
    ltv: float = 0  # Lifetime Value
    clients_active: int = 0
    clients_churned: int = 0
    cash_balance: float = 0
    burn_rate: float = 0  # Monthly
    runway_months: float = 0


# ============================================================
# CASH FLOW MANAGER
# ============================================================

class CashFlowManager:
    """
    Tracks inflows and outflows over time to predict liquidity.
    Enhanced with categorization and forecasting.
    """
    def __init__(self):
        self.transactions: List[Transaction] = []
        self.recurring_items: List[Dict] = []  # {amount, category, frequency, next_date}

    def add_transaction(self, date: str, amount: float, category: str, 
                        description: str = "", client_id: str = None,
                        t_type: str = "inflow"):
        """Add a single transaction."""
        tx = Transaction(
            date=pd.to_datetime(date),
            amount=amount if t_type == "inflow" else -abs(amount),
            category=category,
            description=description,
            client_id=client_id
        )
        self.transactions.append(tx)

    def add_recurring(self, amount: float, category: str, frequency: str = "monthly",
                      start_date: str = None):
        """Add a recurring expense/income (e.g., subscriptions, payroll)."""
        self.recurring_items.append({
            "amount": amount,
            "category": category,
            "frequency": frequency,
            "start_date": pd.to_datetime(start_date) if start_date else datetime.now()
        })

    def get_monthly_summary(self) -> pd.DataFrame:
        """Monthly cash flow summary."""
        if not self.transactions:
            return pd.DataFrame(columns=["Net Cash Flow", "Inflows", "Outflows"])
        
        df = pd.DataFrame([
            {"date": tx.date, "amount": tx.amount, "category": tx.category}
            for tx in self.transactions
        ])
        df.set_index('date', inplace=True)
        
        monthly = df.resample('ME').agg({
            'amount': 'sum'
        }).rename(columns={'amount': 'Net Cash Flow'})
        
        # Add inflows/outflows breakdown
        df['inflow'] = df['amount'].apply(lambda x: x if x > 0 else 0)
        df['outflow'] = df['amount'].apply(lambda x: abs(x) if x < 0 else 0)
        
        monthly['Inflows'] = df.resample('ME')['inflow'].sum()
        monthly['Outflows'] = df.resample('ME')['outflow'].sum()
        
        return monthly

    def get_category_breakdown(self, start_date: str = None, end_date: str = None) -> Dict[str, float]:
        """Breakdown of cash flow by category."""
        df = pd.DataFrame([
            {"date": tx.date, "amount": tx.amount, "category": tx.category}
            for tx in self.transactions
        ])
        
        if start_date:
            df = df[df['date'] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df['date'] <= pd.to_datetime(end_date)]
        
        return df.groupby('category')['amount'].sum().to_dict()

    def forecast_runway(self, current_balance: float, months: int = 12) -> pd.DataFrame:
        """Forecast cash runway based on recurring items and average burn."""
        monthly_recurring = sum(
            item['amount'] for item in self.recurring_items 
            if item['frequency'] == 'monthly'
        )
        
        # Also factor in average non-recurring
        monthly_summary = self.get_monthly_summary()
        avg_monthly_net = monthly_summary['Net Cash Flow'].mean() if len(monthly_summary) > 0 else 0
        
        forecast = []
        balance = current_balance
        
        for i in range(months):
            month_date = datetime.now() + timedelta(days=30*i)
            projected_flow = monthly_recurring + avg_monthly_net * 0.5  # Conservative
            balance += projected_flow
            
            forecast.append({
                "month": month_date.strftime("%Y-%m"),
                "projected_balance": round(balance, 2),
                "monthly_flow": round(projected_flow, 2),
                "runway_depleted": balance < 0
            })
            
            if balance < 0:
                break
        
        return pd.DataFrame(forecast)


# ============================================================
# ACCOUNT ALLOCATOR (Profit First)
# ============================================================

class AccountAllocator:
    """
    Automated fund distribution system (Profit First inspired).
    Aggressive Growth Mode by default, optimized for SaaS scaling.
    """
    
    # Allocation profiles
    PROFILES = {
        "aggressive_growth": {
            "TAX": 0.15,
            "PROFIT": 0.00,
            "OPEX": 0.20,
            "BUFFER": 0.25,
            "GROWTH": 0.40
        },
        "balanced": {
            "TAX": 0.15,
            "PROFIT": 0.10,
            "OPEX": 0.30,
            "BUFFER": 0.25,
            "GROWTH": 0.20
        },
        "cash_preservation": {
            "TAX": 0.15,
            "PROFIT": 0.20,
            "OPEX": 0.25,
            "BUFFER": 0.35,
            "GROWTH": 0.05
        },
        "bootstrap": {
            "TAX": 0.10,
            "PROFIT": 0.00,
            "OPEX": 0.40,
            "BUFFER": 0.10,
            "GROWTH": 0.40
        }
    }

    def __init__(self, profile: str = "aggressive_growth", 
                 custom_rules: Optional[Dict[str, float]] = None):
        self.profile = profile
        self.rules = custom_rules or self.PROFILES.get(profile, self.PROFILES["balanced"])
        self.accounts: Dict[str, float] = {k: 0.0 for k in self.rules.keys()}
        
    def distribute(self, revenue: float, source: str = "mrr") -> Dict[str, float]:
        """Distribute incoming revenue into accounts."""
        distribution = {}
        
        for account, pct in self.rules.items():
            amount = revenue * pct
            self.accounts[account] += amount
            distribution[account] = amount
        
        distribution["TOTAL_INFLOW"] = revenue
        distribution["source"] = source
        distribution["timestamp"] = datetime.now().isoformat()
        
        return distribution

    def get_balances(self) -> Dict[str, float]:
        """Get current account balances."""
        return self.accounts.copy()

    def withdraw(self, account: str, amount: float) -> Dict:
        """Withdraw from an account."""
        if account not in self.accounts:
            return {"success": False, "error": f"Unknown account: {account}"}
        
        if self.accounts[account] < amount:
            return {"success": False, "error": "Insufficient funds", 
                    "available": self.accounts[account]}
        
        self.accounts[account] -= amount
        return {"success": True, "withdrawn": amount, "remaining": self.accounts[account]}

    def recommend_action(self) -> List[str]:
        """AI-driven recommendations based on account balances."""
        recommendations = []
        
        if self.accounts.get("BUFFER", 0) > 10000:
            recommendations.append("💰 High Buffer (€{:.0f}): Consider opportunistic investment or dividend.".format(
                self.accounts["BUFFER"]))
        
        if self.accounts.get("BUFFER", 0) < 2000:
            recommendations.append("⚠️ Low Buffer: Build emergency reserves before scaling.")
        
        if self.accounts.get("GROWTH", 0) < 500:
            recommendations.append("🚨 Low Growth fund: Scaling capacity limited. Prioritize revenue.")
        
        if self.accounts.get("GROWTH", 0) > 5000:
            recommendations.append("🚀 Strong Growth fund: Deploy into acquisition channels.")
        
        tax_reserve = self.accounts.get("TAX", 0)
        if tax_reserve > 0:
            recommendations.append(f"📋 Tax Reserve: €{tax_reserve:.0f} set aside for quarterly taxes.")
        
        return recommendations


# ============================================================
# FINANCIAL ENGINE (Main)
# ============================================================

class FinancialEngine:
    """
    Tactics' internal financial brain.
    Handles all financial metrics, analysis, and reporting.
    """
    
    def __init__(self, company_id: str = "tactics_internal", currency: str = "EUR"):
        self.company_id = company_id
        self.currency = currency
        self.cash_flow = CashFlowManager()
        self.allocator = AccountAllocator()
        self.cohorts: Dict[str, CohortMetrics] = {}
        self.clients: Dict[str, Dict] = {}  # client_id -> {mrr, start_date, status}
        
        # Tactics-specific costs (internal use)
        self.fixed_costs = {
            "supabase": 25,      # Database
            "vercel": 20,       # Hosting
            "openai": 50,       # AI (variable based on usage)
            "domain": 2,        # Annual/12
            "misc": 10          # Buffer
        }
        
        # Vault for encrypted backup (Zero-Knowledge)
        self.vault = None
        if VAULT_AVAILABLE:
            try:
                self.vault = SecureVault(company_id=self.company_id)
            except Exception as e:
                print(f"[Financial] Vault init failed for {self.company_id}: {e}")
    
    # ─────────────────────────────────────────────────────────
    # CLIENT MANAGEMENT
    # ─────────────────────────────────────────────────────────
    
    def add_client(self, client_id: str, mrr: float, start_date: str = None):
        """Add a new paying client."""
        self.clients[client_id] = {
            "mrr": mrr,
            "start_date": pd.to_datetime(start_date) if start_date else datetime.now(),
            "status": "active",
            "lifetime_revenue": mrr
        }
        
        # Track in cohort
        cohort_month = (pd.to_datetime(start_date) if start_date else datetime.now()).strftime("%Y-%m")
        if cohort_month not in self.cohorts:
            self.cohorts[cohort_month] = CohortMetrics(
                cohort_month=cohort_month,
                customers=0,
                revenue_m0=0
            )
        self.cohorts[cohort_month].customers += 1
        self.cohorts[cohort_month].revenue_m0 += mrr

    def churn_client(self, client_id: str, churn_date: str = None):
        """Mark client as churned."""
        if client_id in self.clients:
            self.clients[client_id]["status"] = "churned"
            self.clients[client_id]["churn_date"] = pd.to_datetime(churn_date) if churn_date else datetime.now()

    def update_client_mrr(self, client_id: str, new_mrr: float):
        """Update client MRR (upgrade/downgrade)."""
        if client_id in self.clients:
            old_mrr = self.clients[client_id]["mrr"]
            self.clients[client_id]["mrr"] = new_mrr
            return {"old_mrr": old_mrr, "new_mrr": new_mrr, "delta": new_mrr - old_mrr}
        return {"error": "Client not found"}

    # ─────────────────────────────────────────────────────────
    # CORE METRICS
    # ─────────────────────────────────────────────────────────
    
    def calculate_mrr(self) -> float:
        """Calculate current Monthly Recurring Revenue."""
        return sum(c["mrr"] for c in self.clients.values() if c["status"] == "active")

    def calculate_arr(self) -> float:
        """Annual Run Rate."""
        return self.calculate_mrr() * 12

    def calculate_burn_rate(self) -> float:
        """Monthly burn rate (fixed costs + average variable)."""
        fixed = sum(self.fixed_costs.values())
        
        # Add average from cash flow if available
        monthly_summary = self.cash_flow.get_monthly_summary()
        if len(monthly_summary) > 0:
            avg_outflows = monthly_summary['Outflows'].mean()
            return max(fixed, avg_outflows)
        
        return fixed

    def calculate_runway(self, current_cash: float) -> Dict:
        """Calculate runway in months."""
        burn_rate = self.calculate_burn_rate()
        mrr = self.calculate_mrr()
        
        net_burn = burn_rate - mrr
        
        if net_burn <= 0:
            return {
                "runway_months": float('inf'),
                "status": "PROFITABLE",
                "net_monthly": mrr - burn_rate,
                "burn_rate": burn_rate,
                "mrr": mrr
            }
        
        runway = current_cash / net_burn
        
        status = "CRITICAL"
        if runway > 12:
            status = "HEALTHY"
        elif runway > 6:
            status = "CAUTION"
        elif runway > 3:
            status = "WARNING"
        
        return {
            "runway_months": round(runway, 1),
            "status": status,
            "net_burn": round(net_burn, 2),
            "burn_rate": round(burn_rate, 2),
            "mrr": round(mrr, 2),
            "current_cash": current_cash
        }

    # ─────────────────────────────────────────────────────────
    # LTV/CAC ANALYSIS
    # ─────────────────────────────────────────────────────────
    
    def calculate_ltv(self, avg_mrr: float = None, churn_rate: float = None) -> float:
        """
        Calculate Lifetime Value.
        LTV = ARPU / Churn Rate (simple formula)
        """
        if avg_mrr is None:
            active_clients = [c for c in self.clients.values() if c["status"] == "active"]
            avg_mrr = sum(c["mrr"] for c in active_clients) / len(active_clients) if active_clients else 0
        
        if churn_rate is None:
            total_clients = len(self.clients)
            churned = len([c for c in self.clients.values() if c["status"] == "churned"])
            churn_rate = churned / total_clients if total_clients > 0 else 0.10  # Default 10%
        
        if churn_rate == 0:
            return avg_mrr * 60  # Cap at 5 years
        
        return avg_mrr / churn_rate

    def calculate_cac(self, marketing_spend: float, new_customers: int) -> float:
        """Customer Acquisition Cost."""
        if new_customers == 0:
            return 0
        return marketing_spend / new_customers

    def ltv_cac_analysis(self, marketing_spend: float = 0, new_customers: int = 0) -> Dict:
        """Complete LTV/CAC analysis with payback period."""
        ltv = self.calculate_ltv()
        cac = self.calculate_cac(marketing_spend, new_customers) if new_customers > 0 else 0
        
        ratio = ltv / cac if cac > 0 else float('inf')
        
        # Calculate payback period
        avg_mrr = self.calculate_mrr() / max(1, len([c for c in self.clients.values() if c["status"] == "active"]))
        payback_months = cac / avg_mrr if avg_mrr > 0 else float('inf')
        
        # Status
        if ratio >= 5.0:
            status = "EXCELLENT"
            recommendation = "Increase marketing spend - strong unit economics"
        elif ratio >= 3.0:
            status = "HEALTHY"
            recommendation = "Good balance - optimize CAC for better margins"
        elif ratio >= 1.0:
            status = "WARNING"
            recommendation = "Improve retention or reduce CAC"
        else:
            status = "CRITICAL"
            recommendation = "Stop paid acquisition - fix fundamentals first"
        
        return {
            "ltv": round(ltv, 2),
            "cac": round(cac, 2),
            "ratio": round(ratio, 2),
            "payback_months": round(payback_months, 1) if payback_months != float('inf') else "N/A",
            "status": status,
            "recommendation": recommendation
        }

    # ─────────────────────────────────────────────────────────
    # BREAK-EVEN ANALYSIS
    # ─────────────────────────────────────────────────────────
    
    def break_even_analysis(self, fixed_costs: float = None, 
                            avg_price_per_user: float = None,
                            variable_cost_per_user: float = None) -> Dict:
        """Calculate break-even point in clients."""
        if fixed_costs is None:
            fixed_costs = sum(self.fixed_costs.values())
        
        if avg_price_per_user is None:
            active = [c for c in self.clients.values() if c["status"] == "active"]
            avg_price_per_user = sum(c["mrr"] for c in active) / len(active) if active else 99  # Default tier
        
        if variable_cost_per_user is None:
            # Estimate: API usage, support time
            variable_cost_per_user = 5  # €5 per client per month
        
        margin_per_user = avg_price_per_user - variable_cost_per_user
        
        if margin_per_user <= 0:
            return {"error": "Negative margin - pricing issue", "margin": margin_per_user}
        
        units_needed = fixed_costs / margin_per_user
        
        current_clients = len([c for c in self.clients.values() if c["status"] == "active"])
        
        return {
            "break_even_clients": int(np.ceil(units_needed)),
            "current_clients": current_clients,
            "clients_to_break_even": max(0, int(np.ceil(units_needed)) - current_clients),
            "fixed_costs": round(fixed_costs, 2),
            "margin_per_client": round(margin_per_user, 2),
            "avg_revenue_per_client": round(avg_price_per_user, 2),
            "is_profitable": current_clients >= units_needed
        }

    # ─────────────────────────────────────────────────────────
    # P&L REPORTING
    # ─────────────────────────────────────────────────────────
    
    def generate_pnl(self, month: str = None) -> Dict:
        """Generate P&L statement for a month (or current)."""
        if month is None:
            month = datetime.now().strftime("%Y-%m")
        
        mrr = self.calculate_mrr()
        cogs = self.fixed_costs.get("supabase", 0) + self.fixed_costs.get("openai", 0)
        opex = sum(self.fixed_costs.values()) - cogs
        
        gross_profit = mrr - cogs
        ebitda = gross_profit - opex
        
        return {
            "period": month,
            "revenue": {
                "mrr": round(mrr, 2),
                "other": 0
            },
            "cogs": {
                "infrastructure": round(cogs, 2),
                "total": round(cogs, 2)
            },
            "gross_profit": round(gross_profit, 2),
            "gross_margin_pct": round((gross_profit / mrr * 100) if mrr > 0 else 0, 1),
            "opex": {
                "marketing": 0,
                "admin": round(opex, 2),
                "total": round(opex, 2)
            },
            "ebitda": round(ebitda, 2),
            "ebitda_margin_pct": round((ebitda / mrr * 100) if mrr > 0 else 0, 1),
            "net_income": round(ebitda, 2),  # No taxes yet
            "is_profitable": ebitda > 0
        }

    def analyze_efficiency(self, revenue: float, cogs: float, opex: float) -> Dict:
        """Burn rate and margin analysis."""
        gross_profit = revenue - cogs
        ebitda = gross_profit - opex
        
        return {
            "gross_profit": round(gross_profit, 2),
            "ebitda": round(ebitda, 2),
            "gross_margin_pct": round((gross_profit / revenue) * 100 if revenue > 0 else 0, 1),
            "ebitda_margin_pct": round((ebitda / revenue) * 100 if revenue > 0 else 0, 1),
            "is_profitable": ebitda > 0,
            "burn_rate": round(max(0, -ebitda), 2)
        }

    # ─────────────────────────────────────────────────────────
    # EXPORT & BACKUP
    # ─────────────────────────────────────────────────────────
    
    def export_state(self) -> Dict:
        """Export complete financial state for backup."""
        return {
            "timestamp": datetime.now().isoformat(),
            "clients": self.clients,
            "cohorts": {k: v.__dict__ for k, v in self.cohorts.items()},
            "allocator_balances": self.allocator.get_balances(),
            "fixed_costs": self.fixed_costs,
            "metrics": {
                "mrr": self.calculate_mrr(),
                "arr": self.calculate_arr(),
                "burn_rate": self.calculate_burn_rate()
            }
        }

    def backup_to_vault(self) -> Dict:
        """
        Backup financial state to SecureVault (Internxt).
        Ensures data is encrypted before it leaves the server.
        """
        if not self.vault:
            return {"success": False, "error": "Vault not available"}
        
        state = self.export_state()
        filename = f"financial_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return self.vault.store_audit_document(
            doc_type="financial_audit",
            content=json.dumps(state, default=str).encode('utf-8'),
            doc_name=filename
        )

    def generate_financial_report(self, data: Dict = None) -> pd.DataFrame:
        """Generate formatted financial report DataFrame."""
        if data is None:
            data = {
                "Revenue": {"MRR": self.calculate_mrr(), "ARR": self.calculate_arr()},
                "Costs": self.fixed_costs,
                "Metrics": {
                    "Clients": len([c for c in self.clients.values() if c["status"] == "active"]),
                    "Burn Rate": self.calculate_burn_rate()
                }
            }
        
        report_data = []
        for category, metrics in data.items():
            if isinstance(metrics, dict):
                for k, v in metrics.items():
                    report_data.append({
                        "Category": category, 
                        "Metric": k, 
                        "Value": f"€{v:.2f}" if isinstance(v, (int, float)) else v
                    })
            else:
                report_data.append({
                    "Category": "General", 
                    "Metric": category, 
                    "Value": metrics
                })
        
        return pd.DataFrame(report_data)


# ============================================================
# QUICK ACCESS FUNCTIONS
# ============================================================

def get_tactics_financials() -> FinancialEngine:
    """Get a configured FinancialEngine for Tactics operations."""
    return FinancialEngine(currency="EUR")


def quick_runway_check(current_cash: float, mrr: float, burn_rate: float) -> Dict:
    """Quick runway calculation without full engine setup."""
    net_burn = burn_rate - mrr
    
    if net_burn <= 0:
        return {"runway_months": "Infinite (Profitable)", "net_monthly": mrr - burn_rate}
    
    runway = current_cash / net_burn
    return {
        "runway_months": round(runway, 1),
        "net_burn": round(net_burn, 2),
        "status": "HEALTHY" if runway > 12 else "WARNING" if runway > 6 else "CRITICAL"
    }
