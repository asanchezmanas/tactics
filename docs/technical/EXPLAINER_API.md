# Explainer Engine API

Sistema de explicaciones en lenguaje plano para todas las métricas de los algoritmos de Tactics.

## Principios

1. **Honestidad** - Nunca sonar a certeza cuando hay incertidumbre
2. **Claridad** - Lenguaje accesible para usuarios no técnicos
3. **Contexto** - Explicar qué significa Y cómo se calcula
4. **Limitaciones** - Siempre mencionar márgenes de error y supuestos

## API Endpoints

### Listar Categorías

```
GET /api/explain/categories
```

**Response:**
```json
{
  "categories": ["ltv", "mmm", "eclat", "thompson", "linucb", "profit"],
  "count": 6
}
```

### Listar Métricas de una Categoría

```
GET /api/explain/{category}/metrics
```

**Ejemplo:** `/api/explain/ltv/metrics`

**Response:**
```json
{
  "category": "ltv",
  "metrics": [
    {"id": "clv", "name": "Valor de Vida del Cliente", "unit": "currency", "direction": "higher_better"},
    {"id": "p_alive", "name": "Probabilidad Activo", "unit": "percentage", "direction": "higher_better"},
    {"id": "churn_probability", "name": "Probabilidad de Churn", "unit": "percentage", "direction": "lower_better"}
  ],
  "count": 6
}
```

### Explicar una Métrica (POST)

```
POST /api/explain/{category}/{metric_id}
Content-Type: application/json

{
  "value": 487.32,
  "context": {
    "confidence_interval": [412, 562],
    "sample_size": 1247
  },
  "locale": "es"
}
```

**Response:**
```json
{
  "metric_id": "clv",
  "metric_name": "Valor de Vida del Cliente",
  "category": "ltv",
  "value": 487.32,
  "formatted_value": "€487",
  "confidence_interval": [412, 562],
  "confidence_level": 0.95,
  "what_it_means": "Es la cantidad total de dinero que estimamos que este cliente gastará en tu negocio...",
  "how_calculated": "Analizamos su historial de compras (frecuencia, recencia, valor)...",
  "caveats": [
    "Esta es una estimación estadística basada en datos históricos.",
    "El valor real puede variar si el cliente cambia su comportamiento.",
    "La proyección asume que las condiciones del mercado se mantienen similares."
  ],
  "color_hint": "green",
  "data_quality": "Alta"
}
```

### Explicación Rápida (GET)

```
GET /api/explain/{category}/{metric_id}/quick?value=487.32&locale=es
```

Para uso rápido sin contexto adicional.

## Categorías Disponibles

| Categoría | Descripción | Métricas |
|-----------|-------------|----------|
| `ltv` | Valor de Vida y Churn | clv, p_alive, churn_probability, expected_purchases, recency, segment |
| `mmm` | Media Mix Modeling | roas, saturation, contribution, optimal_budget, adstock |
| `eclat` | Reglas de Asociación | support, confidence, lift |
| `thompson` | Thompson Sampling | conversion_rate, samples, prob_best |
| `linucb` | LinUCB Contextual | ucb_score, exploitation, exploration |
| `profit` | Unit Economics | net_margin, gross_margin, cogs, gross_margin_pct, net_margin_pct |

## Uso en Frontend (Alpine.js)

Para integrar las explicaciones en el dashboard, utilizamos el componente `metric-explainer.js` y el partial `explainer_modal.html`.

### 1. Inicialización
En el `x-data` del dashboard:
```html
<div x-data="{ explainerModal: metricExplainer() }">
```

### 2. Disparar Explicación
```html
<button @click="explainerModal.explain('ltv', 'clv_12m', 487.32)">
    Explicar LTV
</button>
```

### 3. Componente Logic (`static/js/components/metric-explainer.js`)
El componente gestiona el estado de carga (`loading`), los datos de la explicación (`content`) y la visibilidad del modal (`open`).

## Localización

## Localización

El sistema soporta múltiples idiomas:
- `es` - Español (default)
- `en` - English

Pasa el parámetro `locale` en las peticiones para cambiar el idioma.

## Extensibilidad

Para añadir un nuevo algoritmo:

1. Crear `core/explainers/my_explainer.py` extendiendo `ExplainerBase`
2. Añadir templates en `core/explainers/templates.py`
3. Registrar en `api/main.py`:
   ```python
   ExplainerRegistry.register("my_algo", MyExplainer())
   ```
