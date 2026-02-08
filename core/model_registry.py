"""
Model Registry: Versioned Model State Storage.

Philosophy:
- Immutable: Never overwrite, always create new version
- Simple: JSON files, no external dependencies
- Auditable: Full history with timestamps and metrics
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class ModelRegistry:
    """Versioned storage for model states and metrics."""
    
    def __init__(self, base_path: str = "data/models"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_model_dir(self, model_name: str) -> Path:
        """Get or create directory for a model."""
        model_dir = self.base_path / model_name
        model_dir.mkdir(parents=True, exist_ok=True)
        return model_dir
    
    def save_snapshot(
        self, 
        model_name: str, 
        state: Dict[str, Any], 
        metrics: Optional[Dict[str, float]] = None,
        reason: str = "scheduled"
    ) -> str:
        """
        Save a versioned snapshot of model state.
        Returns the version ID.
        """
        model_dir = self._get_model_dir(model_name)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        version_id = f"v_{timestamp}"
        
        snapshot = {
            "version": version_id,
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason,
            "metrics": metrics or {},
            "state": state
        }
        
        filepath = model_dir / f"{version_id}.json"
        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=2, default=str)
        
        # Update current pointer
        self._update_current(model_name, version_id)
        
        return version_id
    
    def _update_current(self, model_name: str, version_id: str):
        """Update the 'current' pointer to latest version."""
        model_dir = self._get_model_dir(model_name)
        current_file = model_dir / "current.txt"
        with open(current_file, 'w') as f:
            f.write(version_id)
    
    def load_current(self, model_name: str) -> Optional[Dict]:
        """Load the current (latest promoted) version."""
        model_dir = self._get_model_dir(model_name)
        current_file = model_dir / "current.txt"
        
        if not current_file.exists():
            return None
        
        with open(current_file, 'r') as f:
            version_id = f.read().strip()
        
        return self.load_version(model_name, version_id)
    
    def load_version(self, model_name: str, version_id: str) -> Optional[Dict]:
        """Load a specific version."""
        model_dir = self._get_model_dir(model_name)
        filepath = model_dir / f"{version_id}.json"
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def list_versions(self, model_name: str, limit: int = 10) -> List[Dict]:
        """List all versions for a model, newest first."""
        model_dir = self._get_model_dir(model_name)
        versions = []
        
        for filepath in sorted(model_dir.glob("v_*.json"), reverse=True)[:limit]:
            with open(filepath, 'r') as f:
                data = json.load(f)
                versions.append({
                    "version": data["version"],
                    "timestamp": data["timestamp"],
                    "reason": data.get("reason", "unknown"),
                    "metrics": data.get("metrics", {})
                })
        
        return versions
    
    def rollback(self, model_name: str, version_id: str) -> bool:
        """Rollback to a previous version by updating current pointer."""
        model_dir = self._get_model_dir(model_name)
        filepath = model_dir / f"{version_id}.json"
        
        if not filepath.exists():
            return False
        
        self._update_current(model_name, version_id)
        return True
    
    def get_current_version_id(self, model_name: str) -> Optional[str]:
        """Get the current version ID without loading full state."""
        model_dir = self._get_model_dir(model_name)
        current_file = model_dir / "current.txt"
        
        if not current_file.exists():
            return None
        
        with open(current_file, 'r') as f:
            return f.read().strip()
    
    def prune_old_versions(self, model_name: str, keep_last_n: int = 10) -> Dict:
        """
        Delete old version snapshots to prevent disk fill.
        Keeps the most recent N versions.
        
        Args:
            model_name: Name of the model
            keep_last_n: Number of versions to keep (default 10)
            
        Returns:
            Dict with pruned count and remaining versions
        """
        model_dir = self._get_model_dir(model_name)
        all_versions = sorted(model_dir.glob("v_*.json"), reverse=True)
        
        # Get current version to never delete it
        current = self.get_current_version_id(model_name)
        
        to_delete = all_versions[keep_last_n:]
        deleted = 0
        
        for filepath in to_delete:
            version_id = filepath.stem
            if version_id != current:  # Never delete current version
                filepath.unlink()
                deleted += 1
        
        return {
            "model": model_name,
            "deleted": deleted,
            "remaining": len(all_versions) - deleted
        }
    
    def prune_all_models(self, keep_last_n: int = 10) -> Dict[str, Dict]:
        """Prune old versions for all models."""
        results = {}
        for model_dir in self.base_path.iterdir():
            if model_dir.is_dir():
                model_name = model_dir.name
                results[model_name] = self.prune_old_versions(model_name, keep_last_n)
        return results
