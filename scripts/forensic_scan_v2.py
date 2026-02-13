import os
import glob

# Extensive list of search terms based on task.md and user feedback
SEARCH_TERMS = {
    "Creative Vault": "templates/app/creative_vault.html",
    "Strategy Kanban": "templates/app/strategy_kanban.html",
    "Marketing Calendar": "templates/app/marketing_calendar.html",
    "Anomaly Inbox": "templates/app/alert_inbox.html",
    "Cohort Management": "templates/app/cohorts.html",
    "Predictive LTV": "templates/app/ltv_predict.html",
    "Inversión de Marketing": "templates/app/mmm_pro.html",
    "class ModelRegistry": "core/model_registry.py",
    "class DriftDetector": "core/drift_detector.py",
    "class AlgorithmTierService": "core/algorithm_tiers.py",
    "class DataQualityAnalyzer": "core/data_quality.py",
    "class SecureVault": "core/secure_vault.py",
    "class LtvExplainer": "core/explainers/ltv_explainer.py",
    "class MMMExplainer": "core/explainers/mmm_explainer.py",
    "class EnterpriseEngine": "core/engine_enterprise.py",
    "class EnterpriseOptimizer": "core/optimizer_enterprise.py",
    "def run_enterprise_ltv_pipeline": "core/engine_enterprise.py",
    "def run_enterprise_mmm_pipeline": "core/optimizer_enterprise.py",
    "LSTM": "core/engine_enterprise.py",
    "PyMC": "core/optimizer_enterprise.py",
    "class CashFlowManager": "core/financial_engine.py",
    "class AccountAllocator": "core/financial_engine.py",
    "class TreasuryEngine": "core/treasury.py",
    "from .database_resilient import": "api/pipeline.py",
    "class IngestWizard": "api/data_ingestion.py",
}

RECOVERY_DIR = "recovery_temp"

def forensic_scan():
    files = glob.glob(f"{RECOVERY_DIR}/*.txt")
    print(f"Scanning {len(files)} blobs with full content analysis...")
    
    findings = []
    
    for f in files:
        hash_val = os.path.basename(f).replace(".txt", "")
        size = os.path.getsize(f)
        try:
            with open(f, "r", encoding="utf8", errors="ignore") as infile:
                content = infile.read()
                
                matches = []
                for term, path in SEARCH_TERMS.items():
                    if term in content:
                        matches.append((term, path))
                
                if matches:
                    findings.append({
                        "hash": hash_val,
                        "size": size,
                        "matches": matches,
                        "preview": content[:200].replace("\n", " ")
                    })
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    # Sort by size to find the most recent/complete versions
    findings.sort(key=lambda x: x["size"], reverse=True)
    
    report_path = "forensic_report_v2.txt"
    with open(report_path, "w", encoding="utf8") as log:
        for item in findings:
            log.write(f"HASH: {item['hash']} | Size: {item['size']} | Potential Paths: {list(set([m[1] for m in item['matches']]))}\n")
            log.write(f"MATCHED TERMS: {list(set([m[0] for m in item['matches']]))}\n")
            log.write(f"PREVIEW: {item['preview']}\n")
            log.write("-" * 80 + "\n")

    print(f"Forensic scan complete. Found {len(findings)} blobs with matches. Report saved to {report_path}")

if __name__ == "__main__":
    forensic_scan()
