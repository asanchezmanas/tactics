# Showcase & Demo Datasets

This guide explains how to use the built-in demo datasets to explore Tactics' analytic engines without connecting real data sources.

## Overview

Tactics includes 3 curated public datasets to demonstrate core features:

| Showcase | Source | Focus | Records |
|----------|--------|-------|---------|
| **E-commerce CPG** | UCI Online Retail | LTV, Segmentation | 10+ |
| **Omnichannel MMM** | Advertising Dataset | Budget Optimizer, ROAS | 9+ |
| **CRM Churn** | Telco Churn (IBM) | Risk Scoring, Retention | 5+ |

## Quick Start

### 1. Import Demo Data

```bash
# Import all showcases
python scripts/import_demo_showcases.py --all

# Import a specific showcase
python scripts/import_demo_showcases.py --showcase ecommerce

# Verify imported data
python scripts/import_demo_showcases.py --verify
```

### 2. Access the Showcase Gallery

Navigate to `/app/showcase` in your browser to see all available demos with descriptions and "Launch Demo" buttons.

### 3. Activate a Demo

Click "Launch Demo" or call the API directly:

```
GET /api/demo/activate/{case_id}
```

Where `case_id` is one of: `ecommerce`, `mmm`, `churn`.

This redirects to the dashboard with the demo company context loaded.

---

## Dataset Details

### E-commerce CPG (UCI Online Retail)

- **Company ID**: `demo_ecommerce`
- **Data Type**: Sales transactions (ventas)
- **Use Case**: Customer Lifetime Value and RFM Segmentation
- **Highlights**:
  - BG/NBD vs Pareto/NBD model comparison
  - RFM segments (Champions, Hibernating, etc.)
  - 12-month CLV projections

### Omnichannel MMM (Advertising)

- **Company ID**: `demo_mmm`
- **Data Type**: Marketing spend (gastos_marketing)
- **Use Case**: Marketing Mix Modeling and Budget Optimization
- **Highlights**:
  - Hill saturation curves per channel
  - Marginal ROAS calculations
  - Optimal spend reallocation

### CRM Churn (Telco)

- **Company ID**: `demo_churn`
- **Data Type**: Customer profiles with risk scores
- **Use Case**: Churn prediction and retention targeting
- **Highlights**:
  - At-risk customer identification
  - Cohort-based retention strategies
  - Predictive probability scoring

---

## Extending with Custom Showcases

Add new showcases by editing `scripts/import_demo_showcases.py`:

```python
SHOWCASES["my_new_demo"] = {
    "name": "My Custom Demo",
    "description": "Description of the use case",
    "company_id": "demo_my_new",
    "highlights": ["Feature 1", "Feature 2"],
    "engine_focus": ["LTV", "Churn"]
}
```

Then add the corresponding bundled data in `BUNDLED_*` dictionaries.

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/app/showcase` | GET | Showcase Gallery page |
| `/api/demo/activate/{case_id}` | GET | Activates demo and redirects to dashboard |

## Files

- `scripts/import_demo_showcases.py` - CLI importer
- `templates/app/showcase.html` - Gallery UI
- `api/main.py` - Route handlers
