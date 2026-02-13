import os
import glob

# Extensive list of search terms based on task.md and user feedback
SEARCH_TERMS = {
    "Creative Vault": "templates/app/creative_vault.html",
    "Strategy Kanban": "templates/app/strategy_kanban.html",
    "Marketing Calendar": "templates/app/marketing_calendar.html",
    "Anomaly Inbox": "templates/app/alert_inbox.html",
    "Cohort Management": "templates/app/cohorts.html", # or where cohort logic is
    "class ModelRegistry": "core/model_registry.py",
    "class DriftDetector": "core/drift_detector.py",
    "class AlgorithmTierService": "core/algorithm_tiers.py",
    "class DataQualityAnalyzer": "core/data_quality.py",
    "class SecureVault": "core/secure_vault.py",
    "class LtvExplainer": "core/explainers/ltv_explainer.py",
    "class MmmExplainer": "core/explainers/mmm_explainer.py",
    "class ProfitExplainer": "core/explainers/profit_explainer.py",
    "class BanditExplainer": "core/explainers/bandit_explainer.py",
    "class EclatExplainer": "core/explainers/eclat_explainer.py",
    "class FinancialEngine": "core/financial_engine.py",
    "class TreasuryEngine": "core/treasury.py",
    "class ShopifyConnector": "connectors/shopify_connector.py",
    "class MetaAdsConnector": "connectors/meta_connector.py",
    "class DataIngestion": "api/data_ingestion.py",
    "def run_full_pipeline": "api/pipeline.py",
    "app = FastAPI": "api/main.py",
    "class CompanyContext": "api/auth.py",
    "Resilient Database Layer": "core/resilience.py",
    "LSTM architecture": "core/engine_enterprise.py",
    "PyMC structure": "core/optimizer_enterprise.py",
    "static/js/components/crm-dashboard.js": "static/js/components/crm-dashboard.js",
    "static/js/components/mmm-dashboard.js": "static/js/components/mmm-dashboard.js",
    "Protected by Internxt": "templates/app/connectors.html", # Look for Elite version
    "Vista General de Rendimiento": "templates/app/dashboard_saas.html",
    "Salud de Datos y Algoritmos Desbloqueados": "templates/partials/data_health_widget.html",
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
                
                matched_paths = []
                for term, path in SEARCH_TERMS.items():
                    if term in content:
                        matched_paths.append(path)
                
                if matched_paths:
                    findings.append({
                        "hash": hash_val,
                        "size": size,
                        "paths": matched_paths,
                        "preview": content[:100].replace("\n", " ")
                    })
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    # Sort by size to find the most recent/complete versions
    findings.sort(key=lambda x: x["size"], reverse=True)
    
    with os.path.join(os.getcwd(), "forensic_report.txt") as log:
        with open("forensic_report.txt", "w", encoding="utf8") as log:
            for item in findings:
                log.write(f"HASH: {item['hash']} | Size: {item['size']} | Potential Paths: {item['paths']}\n")
                log.write(f"PREVIEW: {item['preview']}\n")
                log.write("-" * 50 + "\n")

    print(f"Forensic scan complete. Found {len(findings)} blobs with matches.")

if __name__ == "__main__":
    forensic_scan()
