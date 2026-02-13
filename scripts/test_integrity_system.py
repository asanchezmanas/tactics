import pandas as pd
import numpy as np
from core.integrity_guard import IntegrityGuard
from api.ingestion_audit import IngestionAuditor
from core.data_quality import DataQualityAnalyzer
import uuid

def test_integrity_guard():
    print("Testing IntegrityGuard...")
    # Create noisy data
    df = pd.DataFrame({
        'order_id': ['A', 'A', 'B', 'C', 'D'], # Duplicate A
        'revenue': [100, 100, np.nan, 300, 400], # NaN in B
        'customer_id': ['C1', 'C1', 'C2', 'C3', 'C4'],
        'order_date': pd.to_datetime(['2024-01-01', '2024-01-01', '2024-01-01', '2024-02-01', '2024-02-02']) # Gap between Jan and Feb
    })
    
    guard = IntegrityGuard()
    issues = guard.scan(df, context="ventas")
    
    for issue in issues:
        print(f"[{issue.severity.upper()}] {issue.type}: {issue.message} (Col: {issue.column}, Rows: {issue.affected_rows})")
    
    assert len(issues) >= 3, "Should detect duplicate, NaN, and gap"
    print("IntegrityGuard test PASSED.")

def test_ingestion_audit():
    print("\nTesting IngestionAuditor...")
    auditor = IngestionAuditor(company_id="test_comp")
    batch_id = auditor.create_batch_id()
    print(f"Generated Batch ID: {batch_id}")
    
    # Mock successful receipt
    receipt = auditor.generate_receipt(
        batch_id=batch_id,
        source="unit_test",
        data_type="ventas",
        input_row_count=100,
        success_count=95,
        error_count=5,
        checksum="sha256:mock",
        errors=["Row 5: Invalid price"]
    )
    
    print(f"Receipt Created: {receipt.batch_id} - Status: {receipt.status}")
    assert receipt.status == "partial"
    assert receipt.input_row_count == 100
    print("IngestionAuditor test PASSED.")

if __name__ == "__main__":
    try:
        test_integrity_guard()
        test_ingestion_audit()
        print("\nALL INTEGRITY TESTS PASSED.")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        exit(1)
