import os
import glob
import re

RECOVERY_DIR = 'recovery_temp'
MAPPING_LOG = 'recovery_log.txt'

# Mapping Strategy: Regex Pattern -> Final Path
PATTERNS = [
    (r"Task: Marketing SaaS Project Development", "task.md"),
    (r"def run_full_pipeline", "api/pipeline.py"),
    (r"class ShopifyConnector", "connectors/shopify_connector.py"),
    (r"class MetaAdsConnector", "connectors/meta_connector.py"),
    (r"class DataIngestion", "api/data_ingestion.py"),
    (r"class FinancialEngine", "core/financial_engine.py"),
    (r"class DataQualityAnalyzer", "core/data_quality.py"),
    (r"class AlgorithmTier", "core/algorithm_tiers.py"),
    (r"class SecureVault", "core/secure_vault.py"),
    (r"class TreasuryEngine", "core/treasury.py"),
    (r"class MindbodyConnector", "connectors/mindbody.py"),
    (r"class GlofoxConnector", "connectors/glofox.py"),
    (r"class StripeConnector", "connectors/stripe.py"),
    (r"class KlaviyoConnector", "connectors/klaviyo.py"),
    (r"class GoogleAdsConnector", "connectors/google_ads.py"),
    (r"class GoogleCalendarConnector", "connectors/google_calendar.py"),
    (r"class StripeFitnessConnector", "connectors/stripe_fitness.py"),
    (r"class FitnessConnectorBase", "connectors/fitness_base.py"),
    (r"Resilient Database Layer", "core/resilience.py"),
    (r"Template Store for Explainer Engine", "core/explainers/templates.py"),
    (r"class ExplainResult", "core/explainers/base.py"),
    (r"class LtvExplainer", "core/explainers/ltv_explainer.py"),
    (r"class MmmExplainer", "core/explainers/mmm_explainer.py"),
    (r"class ProfitExplainer", "core/explainers/profit_explainer.py"),
    (r"Demo Showcase Dataset Importer", "scripts/import_datasets.py"),
    (r"Model Maintenance Orchestrator", "scripts/model_maintenance.py"),
    (r"Showcase Accuracy Proof", "scripts/accuracy_proof.py"),
    (r"static/js/core/api.js", "static/js/core/api.js"),
    (r"static/js/core/store.js", "static/js/core/store.js"),
    (r"Main Application Entry Point", "static/js/main.js"),
    (r"Metric Explainer Component", "static/js/components/metric_explainer.js"),
    (r"Vista General de Rendimiento", "templates/app/dashboard_saas.html"),
    (r"Tactics Dashboard", "templates/app/dashboard.html"),
    (r"Marketplace de Conectores", "templates/app/connectors.html"),
    (r"Showcase Gallery", "templates/app/showcase_gallery.html"),
    (r"Showcase Insights", "templates/app/showcase_insights.html"),
    (r"E-commerce Insights Detail", "templates/app/ecommerce_detail.html"),
    (r"MMM Insights Detail", "templates/app/mmm_detail.html"),
    (r"Digital MMM Insights", "templates/app/digital_mmm_detail.html"),
    (r"Churn Insights Detail", "templates/app/churn_detail.html"),
    (r"Banking Churn Insights", "templates/app/banking_churn_insights.html"),
    (r"SaaS LTV InsightsDetail", "templates/app/saas_ltv_detail.html"),
    (r"System Health & Resilience", "templates/app/system_health.html"),
    (r"Alertas Bayesianas", "templates/app/alerts.html"),
    (r"Asistente AI Estrat\u00e9gico", "templates/app/asistente.html"),
    (r"Facturaci\u00f3n", "templates/app/billing.html"),
    (r"Configuraci\u00f3n", "templates/app/settings.html"),
    (r"Importar Datos", "templates/app/importar_datos.html"),
    (r"Data Health Widget", "templates/partials/data_health_widget.html"),
    (r"Explainer Modal", "templates/partials/explainer_modal.html"),
    (r"Public Landing", "templates/public/landing.html"),
    (r"Blog de Estrategia", "templates/public/blog.html"),
    (r"Preguntas Frecuentes", "templates/public/faqs.html"),
    (r"base_dashboard.html", "templates/base_dashboard.html"),
    (r"app = FastAPI", "api/main.py"),
]

# Direct Hash fallback for files that regex might miss
DIRECT_BLOCKS = {
    "b3837a3613fb37dc34d30c8e7741f9e87d97de0f": "connectors/shopify_connector.py",
    "50b652dc113fbbb938cd1429b92351772b9016a9": "connectors/fitness_base.py",
    "6b4de7752b1b975e5917985ef2403a814a079bee": "api/auth.py",
}

def restore():
    inventory = {} # path -> (hash, size)
    files = glob.glob(f"{RECOVERY_DIR}/*.txt")
    
    print(f"Analyzing {len(files)} blobs...")
    
    for f in files:
        hash_val = os.path.basename(f).replace('.txt', '')
        size = os.path.getsize(f)
        
        target_path = None
        
        # 1. Try Direct Hash
        if hash_val in DIRECT_BLOCKS:
            target_path = DIRECT_BLOCKS[hash_val]
        else:
            # 2. Try Regex
            try:
                with open(f, 'r', encoding='utf8', errors='ignore') as infile:
                    content = infile.read(30000)
                    for pattern, path in PATTERNS:
                        if re.search(pattern, content, re.IGNORECASE):
                            target_path = path
                            break
            except Exception as e:
                print(f"Error reading {f}: {e}")
        
        if target_path:
            if target_path not in inventory or size > inventory[target_path][1]:
                inventory[target_path] = (hash_val, size)

    print(f"Identified {len(inventory)} unique files for restoration.")
    
    logs = []
    for path, (hash_val, size) in inventory.items():
        try:
            full_path = os.path.join(os.getcwd(), path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            blob_file = f"{RECOVERY_DIR}/{hash_val}.txt"
            with open(blob_file, 'r', encoding='utf8', errors='ignore') as src:
                with open(full_path, 'w', encoding='utf8') as dst:
                    dst.write(src.read())
            
            logs.append(f"RESTORED: {path} | Hash: {hash_val} | Size: {size}")
            print(f"Restored: {path}")
        except Exception as e:
            logs.append(f"FAILED: {path} | Hash: {hash_val} | Error: {e}")
            print(f"Failed to restore {path}: {e}")

    with open(MAPPING_LOG, 'w', encoding='utf8') as lfile:
        lfile.write("\n".join(logs))

if __name__ == "__main__":
    restore()
