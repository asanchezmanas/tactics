import subprocess
import re

KEYWORDS = [
    "ShopifyConnector", "MetaAdsConnector", "StripeConnector", "KlaviyoConnector",
    "GoogleAdsConnector", "GlofoxConnector", "MindbodyConnector", "DataIngestion",
    "DataQualityAnalyzer", "AlgorithmTier", "SecureVault", "run_full_pipeline",
    "FinancialEngine", "financial_engine", "ExplainResult"
]

def get_blobs():
    result = subprocess.run(["git", "fsck", "--lost-found"], capture_output=True, text=True)
    blobs = re.findall(r"dangling blob ([a-f0-9]{40})", result.stdout)
    return blobs

def scan_blobs(blobs):
    inventory = []
    for blob in blobs:
        result = subprocess.run(["git", "cat-file", "-p", blob], capture_output=True, text=True, errors='ignore')
        content = result.stdout
        found_keywords = [k for k in KEYWORDS if k in content]
        if found_keywords:
            # Check for class definitions to find file headers
            lines = content.splitlines()
            header = lines[0] if lines else ""
            inventory.append({
                "blob": blob,
                "keywords": found_keywords,
                "header": header,
                "size": len(content)
            })
    return inventory

if __name__ == "__main__":
    blobs = get_blobs()
    print(f"Scanning {len(blobs)} blobs...")
    inventory = scan_blobs(blobs)
    for item in sorted(inventory, key=lambda x: x['size'], reverse=True):
        print(f"BLOB: {item['blob']} | Size: {item['size']} | Keywords: {item['keywords']}")
        print(f"Header: {item['header']}")
        print("-" * 40)
