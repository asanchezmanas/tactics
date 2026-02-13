import os
import glob

RECOVERY_DIR = 'recovery_temp'
MAPPING_FILE = 'blob_mapping.txt'

# Patterns to look for in the first few lines
DETERMINISTIC_PATTERNS = {
    "# Task: Marketing SaaS Project Development": "task.md",
    "def run_full_pipeline": "api/pipeline.py",
    "class ShopifyConnector": "connectors/shopify_connector.py",
    "class MetaAdsConnector": "connectors/meta_connector.py",
    "class DataIngestion": "api/data_ingestion.py",
    "class FinancialEngine": "core/financial_engine.py",
    "class DataQualityAnalyzer": "core/data_quality.py",
    "class AlgorithmTier": "core/algorithm_tiers.py",
    "class SecureVault": "core/secure_vault.py",
    "class TreasuryEngine": "core/treasury.py",
    "class MindbodyConnector": "connectors/mindbody.py",
    "class GlofoxConnector": "connectors/glofox.py",
    "<!DOCTYPE html>": "templates/base_dashboard.html", # Initial guess
    "{% extends \"base_dashboard.html\" %}": "dashboard.html", # Initial guess
    "import os": "api/main.py", # Initial guess
}

def analyze_blobs():
    mapping = []
    files = glob.glob(f"{RECOVERY_DIR}/*.txt")
    
    for f in files:
        hash_val = os.path.basename(f).replace('.txt', '')
        try:
            with open(f, 'r', encoding='utf8', errors='ignore') as infile:
                content = infile.read(2000) # Read first 2KB
                guess = "Unknown"
                
                # Try to find specific markers
                for pattern, path in DETERMINISTIC_PATTERNS.items():
                    if pattern in content:
                        guess = path
                        break
                
                # Refine HTML guesses
                if guess == "templates/base_dashboard.html":
                    if "Tactics Dashboard" in content:
                        guess = "templates/base_dashboard.html"
                
                if guess == "dashboard.html":
                    if "class ShopifyConnector" in content:
                        guess = "connectors/shopify_connector.py"

                # Check for other markers
                if "app/dashboard_saas.html" in content:
                    guess = "templates/app/dashboard_saas.html"
                if "app/connectors.html" in content:
                    guess = "templates/app/connectors.html"
                if "static/js/core/api.js" in content:
                    guess = "static/js/core/api.js"
                
                mapping.append(f"{hash_val} | {guess} | {content.splitlines()[0][:50]}")
        except Exception as e:
            mapping.append(f"{hash_val} | ERROR | {str(e)}")
            
    with open(MAPPING_FILE, 'w', encoding='utf8') as outfile:
        outfile.write("\n".join(mapping))

if __name__ == "__main__":
    analyze_blobs()
    print("Mapping complete.")
