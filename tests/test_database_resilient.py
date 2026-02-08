"""
Unit Tests for Resilient Database Layer
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def temp_cache_path(tmp_path):
    """Create a temporary cache database path."""
    return tmp_path / "test_cache.db"


@pytest.fixture
def local_cache(temp_cache_path):
    """Create a LocalCache instance with temp database."""
    from api.database_resilient import LocalCache
    return LocalCache(db_path=temp_cache_path)


@pytest.fixture
def sample_ventas_data():
    """Sample sales data for testing."""
    return [
        {"customer_id": "cust_1", "order_date": "2024-01-15", "revenue": 150.0},
        {"customer_id": "cust_2", "order_date": "2024-01-16", "revenue": 250.0},
        {"customer_id": "cust_1", "order_date": "2024-02-01", "revenue": 100.0},
    ]


@pytest.fixture
def sample_predictions():
    """Sample prediction data for testing."""
    return {
        "predictions": [
            {"customer_id": "cust_1", "ltv_predicted": 1500.0, "churn_prob": 0.15},
            {"customer_id": "cust_2", "ltv_predicted": 800.0, "churn_prob": 0.45},
        ],
        "model_type": "LSTM_MC_Dropout"
    }


# ============================================================
# LOCAL CACHE TESTS
# ============================================================

class TestLocalCache:
    """Tests for the LocalCache class."""
    
    def test_cache_init(self, local_cache, temp_cache_path):
        """Test cache initialization creates database."""
        assert temp_cache_path.exists()
    
    def test_cache_set_and_get(self, local_cache):
        """Test basic cache set and get operations."""
        data = {"key": "value", "number": 42}
        
        local_cache.set("test_key", data, "test_table", company_id="comp_1")
        
        result = local_cache.get("test_key")
        assert result == data
    
    def test_cache_expiration(self, local_cache):
        """Test cache TTL expiration."""
        from datetime import datetime, timedelta
        import sqlite3
        
        # Manually set an expired entry
        expired_time = (datetime.now() - timedelta(hours=1)).isoformat()
        
        with sqlite3.connect(local_cache.db_path) as conn:
            conn.execute("""
                INSERT INTO cache (cache_key, data, table_name, expires_at)
                VALUES (?, ?, ?, ?)
            """, ("expired_key", json.dumps({"old": "data"}), "test", expired_time))
        
        # Should return None for expired entry
        result = local_cache.get("expired_key")
        assert result is None
    
    def test_cache_delete(self, local_cache):
        """Test cache deletion."""
        local_cache.set("to_delete", {"data": "here"}, "test_table")
        assert local_cache.get("to_delete") is not None
        
        local_cache.delete("to_delete")
        assert local_cache.get("to_delete") is None
    
    def test_retry_queue(self, local_cache):
        """Test retry queue operations."""
        # Add to queue
        local_cache.add_to_retry_queue(
            operation="save_insights",
            table_name="insights_jsonb",
            data={"company_id": "comp_1", "value": 100},
            error_message="Connection timeout"
        )
        
        # Get pending retries (should be empty immediately due to delay)
        from datetime import datetime, timedelta
        import sqlite3
        
        # Manually update next_retry_at to now
        with sqlite3.connect(local_cache.db_path) as conn:
            conn.execute("UPDATE retry_queue SET next_retry_at = ?", 
                         (datetime.now().isoformat(),))
        
        pending = local_cache.get_pending_retries()
        assert len(pending) == 1
        assert pending[0]["operation"] == "save_insights"
    
    def test_prediction_cache(self, local_cache, sample_predictions):
        """Test prediction caching."""
        local_cache.save_prediction(
            company_id="comp_1",
            prediction_type="ltv_predictions",
            output_data=sample_predictions,
            confidence={"r2": 0.92},
            model_version="v1.0"
        )
        
        result = local_cache.get_prediction("comp_1", "ltv_predictions")
        
        assert result is not None
        assert result["output"] == sample_predictions
        assert result["confidence"]["r2"] == 0.92
        assert result["model_version"] == "v1.0"
    
    def test_prediction_cache_with_input_hash(self, local_cache):
        """Test prediction caching with input-based hashing."""
        input_data_1 = {"budget": 10000}
        input_data_2 = {"budget": 20000}
        
        local_cache.save_prediction(
            company_id="comp_1",
            prediction_type="mmm_optimization",
            output_data={"allocation": [5000, 5000]},
            input_data=input_data_1
        )
        
        local_cache.save_prediction(
            company_id="comp_1",
            prediction_type="mmm_optimization",
            output_data={"allocation": [10000, 10000]},
            input_data=input_data_2
        )
        
        # Retrieve with matching input
        result_1 = local_cache.get_prediction("comp_1", "mmm_optimization", input_data_1)
        result_2 = local_cache.get_prediction("comp_1", "mmm_optimization", input_data_2)
        
        assert result_1["output"]["allocation"] == [5000, 5000]
        assert result_2["output"]["allocation"] == [10000, 10000]


# ============================================================
# DECORATOR TESTS
# ============================================================

class TestDecorators:
    """Tests for the fallback and retry decorators."""
    
    def test_with_fallback_uses_cache_on_error(self, local_cache, sample_ventas_data):
        """Test that fallback decorator uses cache when Supabase fails."""
        from api.database_resilient import with_fallback, get_local_cache
        
        # Pre-populate cache
        cache = get_local_cache()
        cache.set("ventas:comp_1", sample_ventas_data, "ventas")
        
        @with_fallback(cache_key_fn=lambda company_id: f"ventas:{company_id}")
        def mock_get_ventas(company_id: str) -> pd.DataFrame:
            raise ConnectionError("Supabase unavailable")
        
        result = mock_get_ventas("comp_1")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
    
    def test_with_retry_queue_queues_failed_write(self, local_cache):
        """Test that retry decorator queues failed writes."""
        from api.database_resilient import with_retry_queue, get_local_cache
        
        @with_retry_queue(table_name="test_table")
        def mock_save(company_id: str, data: dict):
            raise ConnectionError("Write failed")
        
        result = mock_save("comp_1", data={"value": 100})
        
        assert result == False  # Indicates queued
        
        # Check retry queue
        cache = get_local_cache()
        
        # Update next_retry_at to now
        from datetime import datetime
        import sqlite3
        with sqlite3.connect(cache.db_path) as conn:
            conn.execute("UPDATE retry_queue SET next_retry_at = ?", 
                         (datetime.now().isoformat(),))
        
        pending = cache.get_pending_retries()
        assert len(pending) >= 1


# ============================================================
# HEALTH CHECK TESTS
# ============================================================

class TestHealthCheck:
    """Tests for database health check."""
    
    def test_health_check_no_supabase(self):
        """Test health check when Supabase is unavailable."""
        from api.database_resilient import check_database_health
        
        with patch('api.database_resilient.get_supabase', return_value=None):
            result = check_database_health()
        
        assert result["supabase_available"] == False
        assert result["local_cache_available"] == True
        assert result["status"] in ["degraded", "degraded_offline_mode"]
    
    def test_health_check_returns_pending_retries(self, local_cache):
        """Test that health check reports pending retries."""
        from api.database_resilient import check_database_health, get_local_cache
        
        # Add a pending retry
        cache = get_local_cache()
        cache.add_to_retry_queue("test_op", "test_table", {"data": 1}, "error")
        
        # Update to make it pending
        from datetime import datetime
        import sqlite3
        with sqlite3.connect(cache.db_path) as conn:
            conn.execute("UPDATE retry_queue SET next_retry_at = ?", 
                         (datetime.now().isoformat(),))
        
        with patch('api.database_resilient.get_supabase', return_value=None):
            result = check_database_health()
        
        assert result["pending_retries"] >= 1


# ============================================================
# INTEGRATION TESTS
# ============================================================

class TestResilientIntegration:
    """Integration tests for the resilient database layer."""
    
    def test_full_offline_workflow(self, local_cache, sample_ventas_data, sample_predictions):
        """Test complete offline workflow with cache."""
        from api.database_resilient import get_local_cache
        
        cache = get_local_cache()
        
        # 1. Cache sales data (simulating previous online fetch)
        cache.set("ventas:comp_1", sample_ventas_data, "ventas", company_id="comp_1")
        
        # 2. Save predictions locally
        cache.save_prediction(
            company_id="comp_1",
            prediction_type="ltv_predictions",
            output_data=sample_predictions,
            model_version="LSTM_v1"
        )
        
        # 3. Retrieve from cache
        ventas = cache.get("ventas:comp_1")
        predictions = cache.get_prediction("comp_1", "ltv_predictions")
        
        assert ventas is not None
        assert len(ventas) == 3
        assert predictions["output"]["model_type"] == "LSTM_MC_Dropout"
    
    def test_graceful_degradation_flow(self):
        """Test that the system degrades gracefully."""
        from api.database_resilient import check_database_health
        
        # Without Supabase configured
        with patch('api.database_resilient.get_supabase', return_value=None):
            health = check_database_health()
        
        # Should still have local cache
        assert health["local_cache_available"] == True
        assert health["status"] != "unhealthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
