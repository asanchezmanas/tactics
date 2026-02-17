# V2 Architecture Overview

> **Design Goals**: Maintainability, Flexibility, Safety
> **Status**: Consolidated V2 Documentation

This document provides a high-level map of the new consolidated Tactics architecture (V2).

## 1. System Anatomy

The system is built on a "Unified Core" that handles different business requirements via pluggable strategies.

### A. The Intelligence Layer (`core/engine_v2.py`)
Uses the **Strategy Pattern** to switch between statistical models (Standard) and deep learning models (Enterprise).
- **Entry Point**: `TacticalEngineV2`

### B. The Optimization Layer (`core/optimizer_v2.py`)
Consolidates budget allocation logic with decoupled solver backends for Scipy and PyMC.
- **Entry Point**: `MarketingOptimizerV2`

### C. The Integrity Layer (`core/integrity_v2.py`)
A centralized hub for all validation and data quality gating, utilized by both API and Resilience modules.
- **Entry Point**: `UnifiedIntegrityGuardV2`

## 2. Data Connectivity Hub (`connectors/sync_v2.py`)

A unified sync router that manages multiple providers (Shopify, Stripe, GA4, Fitness APIs) through a standardized interface, ensuring consistent data ingestion.

## 3. Resilience & Security (`core/resilience.py`, `api/database.py`)

- **Vault Integration**: All sensitive credentials are encrypted via SecureVault.
- **Retry Logic**: Automated resilience for failed API calls and database transactions.
- **Tiered Progress**: The pipeline unlocks advanced V2 features as data integrity milestones are met.

---

## 4. Why V2?

1. **SSoT**: Changes to core logic (e.g., LTV calculation) now happen in one place.
2. **Standardization**: Both SaaS and Hardware scenarios share the same engine logic.
3. **Safety**: V1 files remain for reference and zero-downtime rollback.
