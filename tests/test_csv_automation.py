import sys
import os
import io
import pandas as pd
import pytest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.data_ingestion import DataIngestion
from core.diagnostic_engine import DiagnosticEngine

def test_data_ingestion_semicolon_automation():
    """Test that DataIngestion handles semicolon-separated CSVs with messy headers."""
    ingestion = DataIngestion("test_company")
    
    # Semicolon separated, messy spacing in headers, mixed case
    csv_content = (
        "  ORDER_ID  ;  CUSTOMER_ID  ;  ORDER_DATE  ;  REVENUE  \n"
        "ORD001;client@test.com;2023-01-01;150.50\n"
        "ORD002;client@test.com;2023-01-02;200.00"
    )
    
    result = ingestion.ingest_csv(csv_content, "ventas", source="generic", backup_to_vault=False)
    
    # Ingest CSV returns a dict with stats or results depending on internal implementation
    # We want to ensure it didn't return a "success": False
    assert result.get("success") is not False
    print("✓ DataIngestion: Semicolon + Messy Headers passed.")

def test_diagnostic_engine_tab_automation():
    """Test that DiagnosticEngine handles tab-separated CSVs with fuzzy mapping."""
    engine = DiagnosticEngine("test_diagnostic")
    
    # Tab separated, Spanish names for fuzzy mapping
    headers = "ID_CLIENTE\tFECHA_VENTA\tMONTO\tCANAL\tSKU\n"
    rows = [f"CUST{i}\t2023-01-01\t{100*i}.0\tMetaAds\tSKU_{i%3}" for i in range(21)]
    csv_content = headers + "\n".join(rows)
    
    # DiagnosticEngine expects a file-like object or path
    from io import StringIO
    result = engine.process_csv(StringIO(csv_content))
    
    if result.get("success") is not True:
        print(f"FAILED result: {result}")
    assert result.get("success") is True
    # Verify mapping worked
    assert result["metrics"]["sample_size"] == 21
    print("✓ DiagnosticEngine: Tab + Spanish Fuzzy Mapping passed.")

def test_diagnostic_engine_dirty_csv_extreme():
    """Test an extreme case of a poorly formatted CSV."""
    engine = DiagnosticEngine("test_diagnostic")
    
    # Multiple issues: 
    # 1. Pipe separator (|)
    # 2. Extreme whitespace in headers
    # 3. Trailing spaces in data
    headers = "   USUARIO_ID   |   FECHA   |   VALOR   |   REF   \n"
    rows = [f"  USER_{i:03}  |  2023-10-01  |  {50*i}.00  |  REF_{i%2}  " for i in range(21)]
    csv_content = headers + "\n".join(rows)
    
    from io import StringIO
    result = engine.process_csv(StringIO(csv_content))
    
    if result.get("success") is not True:
        print(f"FAILED result: {result}")
    assert result.get("success") is True
    assert result["metrics"]["sample_size"] == 21
    print("✓ DiagnosticEngine: Pipe + Extreme Whitespace passed.")

if __name__ == "__main__":
    print("\n--- Starting Tactics CSV Automation Tests ---\n")
    try:
        test_data_ingestion_semicolon_automation()
        test_diagnostic_engine_tab_automation()
        test_diagnostic_engine_dirty_csv_extreme()
        print("\n--- ALL TESTS PASSED SUCCESSFULLY ---\n")
    except Exception as e:
        print(f"\n--- TEST FAILED: {str(e)} ---\n")
        sys.exit(1)
