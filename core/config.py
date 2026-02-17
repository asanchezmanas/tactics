ALGORITHM_CONFIG = {
    "segmentation": {
        "vip_at_risk": {
            "prob_alive_threshold": 0.3,
            "clv_threshold": 200,
            "label": "ALTO RIESGO - VIP"
        },
        "lost_customer": {
            "prob_alive_threshold": 0.2,
            "label": "CLIENTE PERDIDO"
        },
        "loyal_customer": {
            "prob_alive_threshold": 0.8,
            "expected_purchases_threshold": 0.5,
            "label": "CLIENTE LEAL"
        },
        "whale_potential": {
            "clv_threshold": 500,
            "label": "POTENCIAL BALLENA"
        },
        "default_label": "ESTÁNDAR"
    },
    "mmm": {
        "default_saturation": "hill",
        "mc_iterations": 100,
        "adstock_type": "geometric"
    },
    "ltv": {
        "default_model": "BG/NBD",
        "confidence_iterations": 30,
        "discount_rate": 0.01
    },
    "profit": {
        "min_support": 0.05,
        "min_lift": 1.5,
        "linucb_alpha": 1.0
    },
    "tiers": {
        "INTELLIGENCE": {
            "engines": ["engine_a_core", "engine_b_core", "engine_c_core"],
            "max_customers": 25000,
            "plans": ["intelligence_monthly", "intelligence_annual"]
        },
        "OPTIMISATION": {
            "engines": ["engine_a_core", "engine_b_core", "engine_c_core"],
            "max_customers": 100000,
            "plans": ["optimisation_monthly", "optimisation_annual"],
            "features": ["mmm_slsqp", "poas", "basket_eclat"]
        },
        "PRECISION": {
            "engines": ["engine_a_enterprise", "engine_b_enterprise", "engine_c_enterprise"],
            "max_customers": None,  # Unlimited
            "plans": ["precision_monthly", "precision_annual"],
            "features": ["lstm_neural", "pymc_bayesian", "channel_synergy", "ltv_weighted_roas"]
        }
    },
    "precision_ltv": {
        "model_type": "LSTM",
        "sequence_length": 12,
        "drift_threshold": 0.15
    },
    "precision_mmm": {
        "inference_type": "pymc",
        "n_samples": 2000,
        "nevergrad_budget": 100
    },
    "default_tier": "INTELLIGENCE",
    "tier_hierarchy": ["INTELLIGENCE", "OPTIMISATION", "PRECISION"],
    "supabase": {
        "url": "https://your-project-id.supabase.co",
        "key": "your-anon-key",
        "tables": {
            "ingestion_raw": "raw_payloads",
            "customers": "customers",
            "transactions": "transactions",
            "marketing_spend": "marketing_spend",
            "sentiment_signals": "sentiment_signals",
            "ingestion_receipts": "ingestion_receipts"
        }
    }
}
