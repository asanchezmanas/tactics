# Algorithm Maintenance System

> **"First, do no harm."** — Sistema conservador de mantenimiento de modelos ML.

---

## Vista General

El sistema de mantenimiento automatiza la gestión del ciclo de vida de los algoritmos de ML en producción, con un enfoque **conservador** que prioriza la estabilidad sobre la optimización.

```
┌─────────────────────────────────────────────────────────────┐
│                    MAINTENANCE FLOW                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   [CRON Trigger] ──► [Drift Check] ──► Drift?              │
│                           │              │                  │
│                           │          No  │  Yes             │
│                           ▼              │                  │
│                     [Exit/Log]           ▼                  │
│                                    [Retrain Candidate]      │
│                                          │                  │
│                                          ▼                  │
│                                    [Validate] ──► Pass?     │
│                                          │          │       │
│                                      No  │      Yes │       │
│                                          ▼          ▼       │
│                                    [Keep Old]  [Promote]    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Componentes

### 1. Model Registry (`core/model_registry.py`)

Almacenamiento versionado e inmutable para estados de modelos.

```python
from core.model_registry import ModelRegistry

registry = ModelRegistry()

# Guardar snapshot
version = registry.save_snapshot(
    model_name="thompson_priors",
    state={"offer_A": {"alpha": 5, "beta": 2}},
    metrics={"ctr": 0.71},
    reason="manual_update"
)

# Cargar versión actual
current = registry.load_current("thompson_priors")

# Ver historial
history = registry.list_versions("thompson_priors", limit=5)

# Rollback a versión anterior
registry.rollback("thompson_priors", "v_20260101_120000")
```

**Estructura de archivos:**
```
data/models/
├── thompson_priors/
│   ├── current.txt           # Puntero a versión activa
│   ├── v_20260208_135853.json
│   └── v_20260201_100000.json
├── eclat/
│   └── ...
└── ltv_churn/
    └── ...
```

---

### 2. Drift Detector (`core/drift_detector.py`)

Detecta cuándo un modelo necesita re-entrenamiento.

```python
from core.drift_detector import DriftDetector, calculate_thompson_decay

detector = DriftDetector()

# Check ECLAT drift
result = detector.check_eclat_drift(
    current_basket_size=3.2,
    historical_basket_size=2.5,
    current_top_bundle_support=0.15,
    historical_top_bundle_support=0.18
)
# → {"drift_detected": True, "recommendation": "retrain"}

# Check Thompson staleness
result = detector.check_thompson_staleness(arm_priors)
# → {"drift_detected": False, "recommendation": "continue"}

# Apply decay to stale priors
decayed = calculate_thompson_decay(arm_priors, decay_factor=0.9)
```

**Umbrales (conservadores):**

| Modelo | Señal | Umbral | Acción |
|--------|-------|--------|--------|
| ECLAT | Cambio en tamaño de cesta | >25% | Re-entrenar |
| ECLAT | Caída en soporte de bundles | >40% | Re-entrenar |
| Thompson | Varianza de medias baja | <0.01 | Decay |
| LTV/Churn | Cambio en recency | >30% | Re-entrenar |
| LTV/Churn | Cambio en frequency | >25% | Re-entrenar |

---

### 3. Orchestrator (`scripts/model_maintenance.py`)

Script principal de mantenimiento.

**Uso:**
```bash
# Modo seguro (ver qué pasaría sin cambiar nada)
python scripts/model_maintenance.py --dry-run

# Ejecutar mantenimiento
python scripts/model_maintenance.py --live
```

**Logs:**
```
data/maintenance_logs/
├── maintenance_20260208_135831.log
└── maintenance_20260208_135853.log
```

---

## Thompson Sampling Decay

Cuando los priors de Thompson Sampling convergen (varianza < 0.01), se aplica decay para evitar que datos antiguos dominen.

```
Antes: α=50, β=20 (mean=0.71)
Decay (×0.9): α=45, β=18 (mean=0.71)

Si α + β < 2: Revertir a uniforme (1, 1)
```

---

## Salvaguardas

| Mecanismo | Propósito |
|-----------|-----------|
| **Modo dry-run** | Ver cambios antes de ejecutar |
| **Cooldown 7 días** | Evitar re-entrenamiento excesivo |
| **Snapshots inmutables** | Nunca sobrescribir, siempre versionar |
| **Umbrales conservadores** | Solo actuar ante drift significativo |
| **Logs completos** | Auditoría en `data/maintenance_logs/` |

---

## Automatización

### Windows Task Scheduler

1. Abrir **Task Scheduler**
2. Crear tarea básica:
   - **Trigger:** Diario, 4:00 AM
   - **Action:** Start a program
   - **Program:** `C:\Users\Artur\tactics\venv\Scripts\python.exe`
   - **Arguments:** `scripts/model_maintenance.py --live`
   - **Start in:** `C:\Users\Artur\tactics`

### Linux Cron

```bash
# Editar crontab
crontab -e

# Añadir línea (4:00 AM diario)
0 4 * * * cd /path/to/tactics && ./venv/bin/python scripts/model_maintenance.py --live
```

---

## Próximos Pasos

- [ ] Conectar ECLAT maintenance con datos reales de Supabase
- [ ] Conectar LTV/Churn maintenance con datos de clientes
- [ ] Añadir alertas (Slack/Email) cuando se detecte drift crítico
