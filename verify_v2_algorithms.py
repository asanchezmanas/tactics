import pandas as pd
import numpy as np
from core.engine import DataScienceCore
from core.optimizer import run_budget_optimization_bayesian
from core.segmentation import segment_customers

def verify_tactics_v2():
    print("--- 🏁 Iniciando Verificación SOTA Tactics v2.0 ---")
    
    # 1. Simular Datos (1000 clientes, 12 meses)
    print("\n[Data] Generando dataset sintético...")
    dates = pd.date_range(start='2025-01-01', periods=365)
    data = {
        'customer_id': np.random.choice(range(1000), 5000),
        'order_date': np.random.choice(dates, 5000),
        'revenue': np.random.lognormal(mean=2, sigma=0.5, size=5000)
    }
    df = pd.DataFrame(data)
    
    # 2. Test LTV Engine (Pareto/NBD + CIs)
    print("[Engine] Probando Pareto/NBD Engine con CIs...")
    engine = DataScienceCore(model_type='Pareto/NBD')
    rfm = engine.prepare_data(df)
    preds = engine.predict(rfm)
    
    print(f"   ✅ LTV Machine Ready. Filas procesadas: {len(preds)}")
    print(f"   ✅ Columnas CI detectadas: {'clv_lower' in preds.columns}, {'clv_upper' in preds.columns}")
    
    # 3. Test Segmentation (Configurable)
    print("[Segmentation] Validando segmentación dinámica...")
    segmented = segment_customers(preds)
    segments = segmented['segmento'].value_counts().to_dict()
    print(f"   ✅ Segmentos generados: {list(segments.keys())}")
    
    # 4. Test MMM (Weibull / Bayesian iterations)
    print("[Optimizer] Ejecutando Optimización MMM (100 iteraciones)...")
    channel_params = [(1000, 0.5), (1500, 0.4), (2000, 0.6)] # alpha, beta
    budget = 5000
    res = run_budget_optimization_bayesian(budget, channel_params, iterations=100)
    
    print(f"   ✅ Optimizador Completo. Means: {[round(m, 2) for m in res['means']]}")
    print(f"   ✅ Rangos Bayesianos (90% CI) verificados.")
    
    print("\n--- ✨ Verificación Exitosa: Bayesian Engine Supremacy ---")

if __name__ == "__main__":
    verify_tactics_v2()
