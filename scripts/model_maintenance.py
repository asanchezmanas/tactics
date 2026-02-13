"""
Model Maintenance Orchestrator - Complete Version.

Philosophy:
- "First, do no harm" - Conservative by default
- Dry-run mode for safety
- Full logging for auditability
- Supports ALL algorithms

Usage:
    python scripts/model_maintenance.py --dry-run  # See what would happen
    python scripts/model_maintenance.py --live     # Execute maintenance

Algorithms Maintained:
- Thompson Sampling (A/B testing priors)
- LinUCB (Contextual bandit matrices)
- ECLAT (Market basket rules)
- LTV/Churn (Customer predictions cache)
- MMM (Channel parameters)
"""
import sys
import os
import argparse
import json
import numpy as np
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.model_registry import ModelRegistry
from core.drift_detector import DriftDetector, calculate_thompson_decay


class MaintenanceOrchestrator:
    """
    Orchestrates model maintenance with safety-first approach.
    Handles ALL algorithm types in the system.
    """
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.registry = ModelRegistry()
        self.drift_detector = DriftDetector()
        self.logs: list = []
        self.run_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.summary = {"maintained": [], "skipped": [], "errors": []}
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = datetime.now(timezone.utc).isoformat()
        entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append(entry)
        print(entry)
    
    def save_logs(self):
        """Save logs to file."""
        log_dir = Path("data/maintenance_logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = log_dir / f"maintenance_{self.run_timestamp}.log"
        with open(filepath, 'w') as f:
            f.write("\n".join(self.logs))
        
        self.log(f"Logs saved to {filepath}")
    
    # =========================================================================
    # THOMPSON SAMPLING MAINTENANCE
    # =========================================================================
    
    def run_thompson_maintenance(self):
        """
        Maintain Thompson Sampling priors.
        Actions: Check staleness ÔåÆ Apply decay if converged ÔåÆ Save new version
        """
        self.log("=" * 50)
        self.log("THOMPSON SAMPLING MAINTENANCE")
        self.log("=" * 50)
        
        current = self.registry.load_current("thompson_priors")
        
        if current is None:
            self.log("No Thompson priors found. Initializing defaults...")
            self._initialize_thompson()
            return
        
        priors = current.get("state", {})
        self.log(f"Loaded {len(priors)} arm priors from version {current['version']}")
        
        # Check for staleness
        drift_result = self.drift_detector.check_thompson_staleness(priors)
        self.log(f"Staleness check: obs={drift_result['total_observations']}, variance={drift_result['mean_variance']}")
        
        if not drift_result["drift_detected"]:
            self.log("Priors are healthy. No action needed.")
            self.summary["skipped"].append("thompson_priors")
            return
        
        if self.drift_detector.check_cooldown("thompson_priors"):
            self.log("In cooldown period. Skipping.", "WARN")
            self.summary["skipped"].append("thompson_priors")
            return
        
        # Apply decay
        self.log("Priors are stale. Applying decay (factor=0.9)...")
        decayed = calculate_thompson_decay(priors, decay_factor=0.9)
        
        if self.dry_run:
            self.log("[DRY-RUN] Would save decayed priors")
            return
        
        new_version = self.registry.save_snapshot(
            "thompson_priors", decayed,
            metrics={"decay_applied": 0.9, "arms": len(decayed)},
            reason="staleness_decay"
        )
        self.drift_detector.record_retrain("thompson_priors")
        self.log(f"Saved as {new_version}")
        self.summary["maintained"].append("thompson_priors")
    
    def _initialize_thompson(self):
        """Initialize default Thompson priors."""
        default_priors = {
            "offer_10_pct": {"alpha": 1.0, "beta": 1.0, "mean": 0.5},
            "offer_free_ship": {"alpha": 1.0, "beta": 1.0, "mean": 0.5},
            "offer_bundle": {"alpha": 1.0, "beta": 1.0, "mean": 0.5}
        }
        
        if not self.dry_run:
            self.registry.save_snapshot(
                "thompson_priors", default_priors,
                metrics={"initialized": True},
                reason="initial_setup"
            )
            self.log("Initialized Thompson priors.")
        else:
            self.log("[DRY-RUN] Would initialize Thompson priors.")
    
    # =========================================================================
    # LINUCB MAINTENANCE
    # =========================================================================
    
    def run_linucb_maintenance(self):
        """
        Maintain LinUCB contextual bandit state.
        Stores A matrices and b vectors per arm.
        """
        self.log("=" * 50)
        self.log("LINUCB MAINTENANCE")
        self.log("=" * 50)
        
        current = self.registry.load_current("linucb_state")
        
        if current is None:
            self.log("No LinUCB state found. Initializing defaults...")
            self._initialize_linucb()
            return
        
        state = current.get("state", {})
        self.log(f"Loaded {len(state)} arm states from version {current['version']}")
        
        # LinUCB doesn't need "decay" like Thompson, but we can:
        # 1. Check if matrices are becoming ill-conditioned
        # 2. Periodically reset exploration
        
        # Check for ill-conditioning (A matrices with high condition numbers)
        needs_reset = False
        for arm_id, arm_state in state.items():
            A = np.array(arm_state.get("A", [[1]]))
            try:
                cond = np.linalg.cond(A)
                if cond > 1e6:
                    self.log(f"Arm {arm_id} has ill-conditioned A (cond={cond:.0f})", "WARN")
                    needs_reset = True
            except:
                pass
        
        if not needs_reset:
            self.log("All arms are healthy. No action needed.")
            self.summary["skipped"].append("linucb_state")
            return
        
        if self.drift_detector.check_cooldown("linucb_state"):
            self.log("In cooldown period. Skipping.", "WARN")
            return
        
        # Reset to identity matrices
        self.log("Resetting ill-conditioned arms...")
        d = len(next(iter(state.values())).get("A", [[1]]))
        reset_state = {}
        for arm_id in state.keys():
            reset_state[arm_id] = {
                "A": np.eye(d).tolist(),
                "b": np.zeros(d).tolist()
            }
        
        if self.dry_run:
            self.log("[DRY-RUN] Would reset LinUCB state")
            return
        
        new_version = self.registry.save_snapshot(
            "linucb_state", reset_state,
            metrics={"reset": True, "arms": len(reset_state)},
            reason="ill_conditioning_reset"
        )
        self.drift_detector.record_retrain("linucb_state")
        self.log(f"Reset LinUCB state as {new_version}")
        self.summary["maintained"].append("linucb_state")
    
    def _initialize_linucb(self, d: int = 4):
        """Initialize default LinUCB state with identity matrices."""
        default_state = {
            "offer_premium": {"A": np.eye(d).tolist(), "b": np.zeros(d).tolist()},
            "offer_basic": {"A": np.eye(d).tolist(), "b": np.zeros(d).tolist()},
            "offer_trial": {"A": np.eye(d).tolist(), "b": np.zeros(d).tolist()}
        }
        
        if not self.dry_run:
            self.registry.save_snapshot(
                "linucb_state", default_state,
                metrics={"initialized": True, "dimensions": d},
                reason="initial_setup"
            )
            self.log(f"Initialized LinUCB state with d={d}.")
        else:
            self.log("[DRY-RUN] Would initialize LinUCB state.")
    
    # =========================================================================
    # ECLAT MAINTENANCE
    # =========================================================================
    
    def run_eclat_maintenance(self):
        """
        Maintain ECLAT market basket rules.
        Caches frequent itemsets and rules.
        """
        self.log("=" * 50)
        self.log("ECLAT MAINTENANCE")
        self.log("=" * 50)
        
        current = self.registry.load_current("eclat_rules")
        
        if current is None:
            self.log("No ECLAT rules cached. Will be generated on first data load.")
            self.summary["skipped"].append("eclat_rules")
            return
        
        state = current.get("state", {})
        metrics = current.get("metrics", {})
        
        self.log(f"Loaded ECLAT cache from {current['version']}")
        self.log(f"  - Bundles: {len(state.get('top_bundles', []))}")
        self.log(f"  - Generated: {current.get('timestamp', 'unknown')}")
        
        # Check age of cache (re-run if older than 7 days)
        cache_age_days = metrics.get("age_days", 0)
        if cache_age_days < 7:
            self.log(f"Cache is {cache_age_days} days old. Still fresh.")
            self.summary["skipped"].append("eclat_rules")
            return
        
        self.log(f"Cache is {cache_age_days} days old. Marking for refresh.")
        
        # In production, we'd fetch new transactions and regenerate
        # For now, just flag it
        if self.dry_run:
            self.log("[DRY-RUN] Would regenerate ECLAT rules from fresh data")
            return
        
        # Mark as stale (actual regeneration happens in pipeline)
        self.registry.save_snapshot(
            "eclat_rules",
            {"status": "stale", "requires_refresh": True},
            metrics={"marked_stale": True},
            reason="age_expiry"
        )
        self.log("Marked ECLAT cache as stale. Will refresh on next pipeline run.")
        self.summary["maintained"].append("eclat_rules")
    
    # =========================================================================
    # LTV/CHURN MAINTENANCE
    # =========================================================================
    
    def run_ltv_maintenance(self):
        """
        Maintain LTV/Churn prediction cache.
        """
        self.log("=" * 50)
        self.log("LTV/CHURN MAINTENANCE")
        self.log("=" * 50)
        
        current = self.registry.load_current("ltv_predictions")
        
        if current is None:
            self.log("No LTV predictions cached. Will be generated on first sync.")
            self.summary["skipped"].append("ltv_predictions")
            return
        
        metrics = current.get("metrics", {})
        
        self.log(f"Loaded LTV cache from {current['version']}")
        self.log(f"  - Customers: {metrics.get('customer_count', 'unknown')}")
        self.log(f"  - Avg CLV: ${metrics.get('avg_clv', 0):.2f}")
        
        # Check for drift in key metrics
        historical_avg_clv = metrics.get("historical_avg_clv", metrics.get("avg_clv", 100))
        current_avg_clv = metrics.get("avg_clv", 100)
        
        if historical_avg_clv > 0:
            change = abs(current_avg_clv - historical_avg_clv) / historical_avg_clv
            self.log(f"  - CLV change: {change*100:.1f}%")
            
            if change > 0.30:
                self.log("Significant CLV drift detected!", "WARN")
                if not self.dry_run:
                    self.registry.save_snapshot(
                        "ltv_predictions",
                        {"status": "drift_detected", "requires_retrain": True},
                        metrics={"clv_change": change},
                        reason="drift_detected"
                    )
                    self.summary["maintained"].append("ltv_predictions")
                else:
                    self.log("[DRY-RUN] Would mark for retraining")
                return
        
        self.log("LTV predictions are healthy.")
        self.summary["skipped"].append("ltv_predictions")
    
    # =========================================================================
    # MMM MAINTENANCE
    # =========================================================================
    
    def run_mmm_maintenance(self):
        """
        Maintain MMM channel parameters.
        """
        self.log("=" * 50)
        self.log("MMM/BUDGET OPTIMIZER MAINTENANCE")
        self.log("=" * 50)
        
        current = self.registry.load_current("mmm_params")
        
        if current is None:
            self.log("No MMM parameters cached. Initializing defaults...")
            self._initialize_mmm()
            return
        
        state = current.get("state", {})
        metrics = current.get("metrics", {})
        
        self.log(f"Loaded MMM params from {current['version']}")
        self.log(f"  - Channels: {len(state.get('channels', []))}")
        
        # Check calibration age
        calibration_age = metrics.get("calibration_age_days", 0)
        
        if calibration_age < 30:
            self.log(f"Calibration is {calibration_age} days old. Still valid.")
            self.summary["skipped"].append("mmm_params")
            return
        
        self.log(f"Calibration is {calibration_age} days old. Needs recalibration.", "WARN")
        
        if self.dry_run:
            self.log("[DRY-RUN] Would trigger recalibration")
            return
        
        # Mark for recalibration
        self.registry.save_snapshot(
            "mmm_params",
            {"status": "needs_recalibration", "channels": state.get("channels", [])},
            metrics={"marked_for_recalibration": True, "age": calibration_age},
            reason="age_expiry"
        )
        self.log("Marked MMM params for recalibration.")
        self.summary["maintained"].append("mmm_params")
    
    def _initialize_mmm(self):
        """Initialize default MMM parameters."""
        default_params = {
            "channels": [
                {"name": "Meta Ads", "alpha": 1000, "gamma": 0.8},
                {"name": "Google Ads", "alpha": 2000, "gamma": 0.5},
                {"name": "TikTok", "alpha": 500, "gamma": 0.3}
            ],
            "saturation_type": "hill",
            "adstock_type": "weibull"
        }
        
        if not self.dry_run:
            self.registry.save_snapshot(
                "mmm_params", default_params,
                metrics={"initialized": True, "calibration_age_days": 0},
                reason="initial_setup"
            )
            self.log("Initialized MMM parameters.")
        else:
            self.log("[DRY-RUN] Would initialize MMM parameters.")
    
    # =========================================================================
    # ORCHESTRATION
    # =========================================================================
    
    def run_all(self):
        """Run all maintenance tasks."""
        self.log("=" * 60)
        self.log(f"COMPLETE MODEL MAINTENANCE - {self.run_timestamp}")
        self.log(f"Mode: {'DRY-RUN' if self.dry_run else 'LIVE'}")
        self.log("=" * 60)
        
        try:
            self.run_thompson_maintenance()
            self.run_linucb_maintenance()
            self.run_eclat_maintenance()
            self.run_ltv_maintenance()
            self.run_mmm_maintenance()
            
            self.log("=" * 60)
            self.log("MAINTENANCE SUMMARY")
            self.log("=" * 60)
            self.log(f"  Maintained: {self.summary['maintained']}")
            self.log(f"  Skipped: {self.summary['skipped']}")
            self.log(f"  Errors: {self.summary['errors']}")
            self.log("=" * 60)
            
        except Exception as e:
            self.log(f"CRITICAL ERROR: {e}", "ERROR")
            self.summary["errors"].append(str(e))
            raise
        finally:
            self.save_logs()


def main():
    parser = argparse.ArgumentParser(description="Complete Model Maintenance Orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen")
    parser.add_argument("--live", action="store_true", help="Execute maintenance")
    
    args = parser.parse_args()
    dry_run = not args.live
    
    orchestrator = MaintenanceOrchestrator(dry_run=dry_run)
    orchestrator.run_all()


if __name__ == "__main__":
    main()
