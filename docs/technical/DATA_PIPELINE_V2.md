# Unified Data Pipeline v2.0

> **Architecture**: Resilient Orchestration
> **Status**: Consolidated V2 Documentation

This document describes the end-to-end data pipeline from external source ingestion to normalized analytical storage.

## 1. Data Acquisition (`connectors/sync_v2.py`)

The **Unified Sync Hub** centralizes all external integrations into a provider-based registry.

### A. Ingestion Sources
- **E-commerce**: Shopify (Orders, Products, Customers).
- **Payments**: Stripe (Charges, Subscriptions).
- **Marketing**: GA4, GSC, Meta Ads.
- **Fitness Industry**: Glofox, Mindbody.

### B. Normalization
All incoming payloads are standardized into the internal Tactics schema before being handed to the validation layer.

---

## 2. Integrity & Resilience (`core/integrity_v2.py`)

The V2 Integrity Guard provides a centralized gate for data quality.

### A. Validation Layers
1. **Schema Validation**: Ensures all mandatory fields are present and correctly typed.
2. **Logical Duplicates**: Detects overlapping data across sources.
3. **Temporal Gaps**: Identifies missing days in time-series data.
4. **Outlier Detection**: Flags statistically significant anomalies in revenue or spend.

### B. Resilience Interaction
The `DataGuard` in the resilience layer acts as a proxy for the `UnifiedIntegrityGuardV2`, ensuring that only healthy data enters the processing pipeline.

---

## 3. Storage & Orchestration (`api/database.py`, `api/pipeline.py`)

- **Database Layer**: A resilient repository for both raw and processed analytical data.
- **Pipeline Tier**: Progression logic that unlocks higher-tier algorithms (V2 Intelligence/Optimizer) as data quality milestones are met.
