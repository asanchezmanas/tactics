# System Architecture Overview (Tactics)

**Last Updated:** February 2026
**Version:** 2.3 (Resilience & Intelligence Update)

## 1. High-Level Design

Tactics is a **Marketing Intelligence SaaS** built on a "Lean AI" philosophy. It avoids heavy infrastructure (like Kubernetes/Kafka) in favor of a robust, monolithic-first architecture that scales vertically.

### Core Stack
- **Frontend**: HTML5 + Utility CSS + Alpine.js (No Build Step).
- **Backend**: FastAPI (Python 3.10+) + AsyncIO.
- **Database**: Supabase (PostgreSQL + JSONB).
- **AI Core**: NumPy/Pandas (Data), PyMC (Bayesian), Scikit-Learn (Predictive).

---

## 2. Resilience Layer ("Guaranteed Delivery")

We prioritize data integrity over speed. The system is designed to "fail gracefully" and recover automatically.

- **Circuit Breakers**: Protect external APIs (Meta, Google, Shopify). See `core/resilience.py`.
- **Dead Letter Queue (DLQ)**: Failed writes are saved to local SQLite and retried. See `api/database_resilient.py`.
- **DataGuard**: Validates data quality before it enters the AI Engine. See `api/pipeline.py`.

---

## 3. The "Brain" (AI Engines)

The platform is powered by three specialized engines:

### Engine A: Customer Value (LTV)
- **Goal**: Predict future value of cohorts.
- **Tech**: BG/NBD Model (Pareto Distribution).
- **Output**: `clv_12m`, `p_alive` (Churn Probability).

### Engine B: Marketing Mix (MMM)
- **Goal**: Optimize budget allocation.
- **Tech**: Bayesian Media Mix Modeling (PyMC).
- **Features**: Adstock (Weibull), Saturation (Hill Function).

### Engine C: Profit Matrix (Economics)
- **Goal**: Determine true profitability.
- **Data**: Net Revenue (Stripe) - COGS - Ad Spend.
- **Features**: Unit Economics, Contribution Margin.

---

## 4. Frontend Philosophy

We use **Server-Side Rendering (Jinja2)** for the initial paint, enriched with **Alpine.js** for interactivity.

- **Fast & SEO Friendly**: Zero-JS initial load.
- **Reactive**: Dashboards update instantly via Alpine stores.
- **Modular**: Components are separated into `templates/partials` and `static/js/components`.

---

## 5. Deployment & Security

- **Environment**: Docker-ready (files prepared).
- **Secrets**: Managed via `.env`.
- **Auth**: Supabase Auth (JWT).
- **RLS**: Row-Level Security enabled on critical tables.
