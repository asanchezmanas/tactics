# Catálogo de Algoritmos - Tactics

> Documentación técnica de todos los algoritmos implementados en la plataforma.

---

## Índice

1. [Engine A: LTV/Churn (Pareto/NBD)](#engine-a-ltvchurn)
2. [Engine B: Budget Optimizer (MMM)](#engine-b-budget-optimizer)
3. [Segmentación de Clientes](#segmentación-de-clientes)
4. [Profit Matrix](#profit-matrix)
   - ECLAT (Market Basket)
   - Thompson Sampling
   - LinUCB (Contextual Bandit)
5. [Engine Enterprise (LSTM + PyMC)](#engine-enterprise)
6. [Capa de Interpretabilidad (Explainer Engine)](#explainer-engine)

---

## Engine A: LTV/Churn

**Archivo:** `core/engine.py`
**Clase:** `DataScienceCore`

### Descripción
Predice el **Customer Lifetime Value (LTV)** y la **probabilidad de churn** usando el modelo Pareto/NBD.

### Inputs
```python
# DataFrame con columnas:
# - customer_id: str
# - order_date: datetime
# - revenue: float
```

### Outputs
| Métrica | Descripción |
|---------|-------------|
| `clv_12m` | Valor esperado del cliente en 12 meses |
| `prob_alive` | Probabilidad de que el cliente siga activo (0-1) |
| `expected_purchases_90d` | Compras esperadas en 90 días |

### Uso
```python
from core.engine import DataScienceCore

engine = DataScienceCore()
rfm = engine.prepare_data(transactions_df)
predictions = engine.run_predictions(rfm)
```

### Parámetros Configurables
```python
# core/config.py → ALGORITHM_CONFIG["ltv"]
{
    "model_type": "pareto_nbd",  # o "bg_nbd"
    "prediction_horizon_months": 12,
    "confidence_level": 0.90
}
```

---

## Engine B: Budget Optimizer

**Archivo:** `core/optimizer.py`
**Funciones:** `run_budget_optimization`, `run_budget_optimization_bayesian`

### Descripción
Optimiza la distribución de presupuesto entre canales de marketing usando **Marketing Mix Modeling (MMM)** con funciones de saturación.

### Funciones de Saturación

**Hill (default):**
```
y = α × (x^γ / (x^γ + 1))
```

**Michaelis-Menten:**
```
y = α × x / (Km + x)
```

### Adstock (Memoria publicitaria)

**Geometric:**
```python
adstock[t] = spending[t] + decay × adstock[t-1]
```

**Weibull (SOTA):**
```python
weights = exp(-((t/scale)^shape))
adstock = convolve(spending, weights)
```

### Uso
```python
from core.optimizer import run_budget_optimization_bayesian

# Parámetros por canal: (alpha, gamma)
channel_params = [
    (1000, 0.8),  # Meta Ads
    (2000, 0.5),  # Google Ads
    (500, 0.3)    # TikTok
]

result = run_budget_optimization_bayesian(
    total_budget=10000,
    channel_params=channel_params,
    iterations=100
)
# → {"means": [...], "lowers": [...], "uppers": [...]}
```

### Outputs
| Campo | Descripción |
|-------|-------------|
| `means` | Presupuesto óptimo medio por canal |
| `lowers` | Límite inferior del intervalo de confianza (10%) |
| `uppers` | Límite superior del intervalo de confianza (90%) |

---

## Segmentación de Clientes

**Archivo:** `core/segmentation.py`
**Función:** `segment_customers`

### Descripción
Clasifica clientes en segmentos accionables basándose en sus predicciones de LTV/Churn.

### Segmentos

| Segmento | Criterio |
|----------|----------|
| `CLIENTE LEAL` | prob_alive > 0.7 AND high engagement |
| `ALTO RIESGO - VIP` | prob_alive < 0.4 AND high CLV |
| `NUEVO POTENCIAL` | Recent signup, low data |
| `CLIENTE PERDIDO` | prob_alive < 0.2 AND no recent activity |

### Uso
```python
from core.segmentation import segment_customers

segmented = segment_customers(predictions_df)
# → DataFrame with 'segmento' column
```

---

## Profit Matrix

**Archivo:** `core/profit.py`
**Clase:** `ProfitMatrixEngine`

### 4.1 ECLAT (Market Basket Analysis)

Encuentra productos que se compran juntos frecuentemente.

```python
from core.profit import ProfitMatrixEngine

engine = ProfitMatrixEngine()

# transactions: DataFrame con [order_id, product_id]
result = engine.calculate_basket_rules(transactions, min_support=0.05)

# Output:
# {
#   "top_bundles": [
#     {"items": ["A", "B"], "support": 0.12, "lift": 2.5},
#     ...
#   ],
#   "frequent_itemsets": [[["A", "B"], 0.12], ...]
# }
```

**Métricas:**
- **Support:** Frecuencia de la combinación
- **Lift:** Cuántas veces más probable es comprar juntos vs independiente

---

### 4.2 Thompson Sampling (A/B Testing)

Testing bayesiano de ofertas sin necesidad de contexto.

```python
engine = ProfitMatrixEngine()

offers = [
    {"id": "10_pct_off", "name": "10% Off"},
    {"id": "free_ship", "name": "Free Shipping"}
]

# Seleccionar oferta
result = engine.thompson_sampling_select(offers)
# → {"selected_offer": {...}, "winning_sample": 0.72}

# Actualizar después de conversión
engine.thompson_sampling_update("10_pct_off", success=True)
engine.thompson_sampling_update("free_ship", success=False)

# Ver estado
state = engine.get_thompson_state()
# → {"10_pct_off": {"alpha": 5, "beta": 2, "mean": 0.71}, ...}
```

---

### 4.3 LinUCB (Contextual Bandit)

Selección de ofertas basada en contexto del usuario.

```python
import numpy as np

# Vector de contexto (edad normalizada, segment_id, device_id, etc.)
context = np.array([0.35, 1.0, 0.0, 0.8])

offers = [
    {"id": "premium", "name": "Premium Offer"},
    {"id": "basic", "name": "Basic Offer"}
]

result = engine.linucb_select_offer(context, offers, alpha=1.0)
# → {"selected_offer": {...}, "ucb_score": 1.23}
```

**Parámetros:**
- `alpha`: Exploración vs explotación (mayor = más exploración)

---

## Engine Enterprise

**Archivos:** `core/engine_enterprise.py`, `core/optimizer_enterprise.py`

### 5.1 LSTM para LTV (engine_enterprise.py)

Red neuronal para predicción de LTV en clientes con alta complejidad.

```python
from core.engine_enterprise import EnterpriseEngine

engine = EnterpriseEngine()

# Detectar drift en cohortes
drift = engine.detect_cohort_drift(
    historical_recency=[10, 20, 15],
    current_recency=[25, 40, 30]
)
# → {"kl_divergence": 0.23, "significant_drift": True}
```

### 5.2 PyMC para MMM (optimizer_enterprise.py)

Optimización bayesiana completa con matrices de sinergia entre canales.

```python
from core.optimizer_enterprise import EnterpriseOptimizer

optimizer = EnterpriseOptimizer()

# Matriz de sinergia (off-diagonal = interacción entre canales)
synergy = optimizer.calculate_channel_synergy(spending_history)
# → {"synergy_matrix": [[1.0, 0.3], [0.3, 1.0]], "interpretation": "..."}
```

---

## Configuración Global

Todos los parámetros están centralizados en `core/config.py`:

```python
ALGORITHM_CONFIG = {
    "ltv": {
        "model_type": "pareto_nbd",
        "prediction_horizon_months": 12,
        "confidence_level": 0.90
    },
    "mmm": {
        "saturation_type": "hill",
        "adstock_type": "weibull",
        "monte_carlo_iterations": 100
    },
    "profit": {
        "min_support": 0.05,
        "thompson_decay_factor": 0.9
    },
    "tier": "core"  # "core" | "enterprise"
}
```

---

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                              │
│  (Supabase + SQLite Cache + Resilient Writes)                  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                        CORE ENGINES                               │
├─────────────────┬─────────────────┬─────────────────┬────────────┤
│  engine.py      │  optimizer.py   │  segmentation.py│ profit.py  │
│  (LTV/Churn)    │  (MMM Budget)   │  (Customer Seg) │ (Profit)   │
│  Pareto/NBD     │  Hill/Weibull   │  Rule-based     │ ECLAT      │
│                 │  Monte Carlo    │                 │ Thompson   │
│                 │                 │                 │ LinUCB     │
└─────────────────┴─────────────────┴─────────────────┴────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                      ENTERPRISE TIER                              │
├─────────────────────────┬─────────────────────────────────────────┤
│  engine_enterprise.py   │  optimizer_enterprise.py                │
│  LSTM + Drift Detection │  PyMC + Channel Synergy                 │
└─────────────────────────┴─────────────────────────────────────────┘
```

---

## Mantenimiento de Algoritmos

**Archivos:** `core/model_registry.py`, `core/drift_detector.py`, `scripts/model_maintenance.py`

### Filosofía
> **"First, do no harm."** — Conservador por defecto, inmutable, auditable.

### Cobertura Completa

| Algoritmo | Estado | Mantenimiento |
|-----------|--------|---------------|
| Thompson Sampling | ✅ Completo | Staleness check → Decay (×0.9) |
| LinUCB | ✅ Completo | Condition check → Reset matrices |
| ECLAT | ✅ Completo | Age check → Refresh flag |
| LTV/Churn | ✅ Completo | CLV drift → Retrain flag |
| MMM | ✅ Completo | Calibration age → Recalibrate flag |

### Cuándo se Re-entrena

| Algoritmo | Señal de Drift | Umbral |
|-----------|----------------|--------|
| Thompson | Convergencia (varianza baja) | <0.01 |
| LinUCB | Matriz A mal condicionada | cond > 1e6 |
| ECLAT | Edad del cache | >7 días |
| LTV/Churn | Cambio en CLV promedio | >30% |
| MMM | Edad de calibración | >30 días |

### Estado Persistido

```
data/models/
├── thompson_priors/
│   ├── current.txt
│   └── v_20260208_135853.json
├── linucb_state/
│   ├── current.txt
│   └── v_20260208_140531.json
├── eclat_rules/
├── ltv_predictions/
└── mmm_params/
    ├── current.txt
    └── v_20260208_140531.json
```

### Uso

```bash
# Ver qué pasaría (seguro)
python scripts/model_maintenance.py --dry-run

# Ejecutar mantenimiento
python scripts/model_maintenance.py --live
```

### Salvaguardas

- ✅ Snapshots inmutables (nunca sobrescribe)
- ✅ Cooldown de 7 días entre re-entrenamientos
- ✅ Logs completos en `data/maintenance_logs/`
- ✅ Modo dry-run por defecto

---

## Explainer Engine

**Archivo:** `core/explainers/base.py`, `core/explainers/registry.py`
**Middleware Humano:** El puente entre los modelos matemáticos y la toma de decisiones.

### Arquitectura de Explicación
Cada algoritmo tiene un "Explainer" dedicado que traduce sus métricas crudas a narrativas.

1. **BaseExplainer**: Define el esquema de la métrica (`MetricSchema`) y el resultado esperado (`ExplainedResult`).
2. **Templates**: Diccionarios de traducción (ES/EN) con placeholders para los valores calculados.
3. **Interpretación Contextual**:
   - **LTV**: Traduce valores de churn en impacto financiero tangible.
   - **MMM**: Traduce coeficientes de saturación en "reventar el canal" o "curva de aprendizaje".
   - **Profit**: Traduce márgenes en salud de inventario.

### Uso
```python
from core.explainers.registry import ExplainerRegistry

explainer = ExplainerRegistry.get("ltv")
result = explainer.explain("clv_12m", value=450.0)

print(result.what_it_means)
# "Este cliente es un activo de alto impacto. Basado en su recencia..."
```

---

📄 **Documentación completa:** [ALGORITHM_MAINTENANCE.md](./ALGORITHM_MAINTENANCE.md)
