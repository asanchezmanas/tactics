import os
import shutil

# Mappings of identified blobs to their original paths
RESTORE_MAP = {
    "12a71cac3d5b7410f017edbfd81704e7765a21db": "api/main.py",
    "90a9b31c56f4ed39e4b434a866a9402945a630aa": "api/database_resilient.py",
    "9ebc1b4ecf0d0a14ed5ed64d8816fa90221ffbbb": "api/pipeline.py",
    "0831f4605fc718173e351a338610cae72ae09647": "scripts/model_maintenance.py",
    "8c8d69eda266be2df61c59405719508ecca90da7": "core/algorithm_tiers.py",
    "42e905b203d48f54d5a66dc8b7bccec46f932955": "core/data_quality.py",
    "c0e24fd2335439254efd66052e75951e2ece1431": "templates/app/creative_vault.html",
    "b76115b6d1b2ac1f29e6894c6c0d9c223c51a622": "templates/app/strategy_kanban.html",
    "131516e908f71dfe3f18e84e54b2acc54acc9702": "templates/app/ltv_predict.html",
    "0e3d1a5f61b4cd5cef96d1fcb199c2e20d486403": "templates/app/alert_inbox.html",
    "bc660b3ef29f92bad5b98b2863d8ed17a3e125e7": "templates/app/marketing_calendar.html",
}

RECOVERY_DIR = "recovery_temp"
BASE_DIR = os.getcwd()

def restore_identified():
    print("Starting restoration of identified enterprise files...")
    restored_count = 0
    
    for blob_hash, target_path in RESTORE_MAP.items():
        source = os.path.join(RECOVERY_DIR, f"{blob_hash}.txt")
        destination = os.path.join(BASE_DIR, target_path)
        
        if not os.path.exists(source):
            print(f"FAILED: Source blob {blob_hash} not found in {RECOVERY_DIR}")
            continue
            
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        try:
            shutil.copy2(source, destination)
            print(f"RESTORED: {target_path} (from {blob_hash})")
            restored_count += 1
        except Exception as e:
            print(f"ERROR: Failed to restore {target_path}: {e}")
            
    print(f"\nRestoration complete. {restored_count} files restored.")

if __name__ == "__main__":
    restore_identified()
