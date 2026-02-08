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
        "core": {
            "engines": ["engine_a_core", "engine_b_core", "engine_c_core"],
            "max_customers": 50000,
            "plans": ["starter", "growth", "agency"]
        },
        "enterprise": {
            "engines": ["engine_a_enterprise", "engine_b_enterprise", "engine_c_enterprise"],
            "max_customers": None,  # Unlimited
            "plans": ["pro_ai", "strategic", "enterprise"],
            "features": ["lstm", "pymc", "channel_synergy", "cohort_drift", "linucb"]
        }
    },
    "enterprise_ltv": {
        "model_type": "LSTM",
        "sequence_length": 12,
        "drift_threshold": 0.15
    },
    "enterprise_mmm": {
        "inference_type": "pymc",
        "n_samples": 2000,
        "nevergrad_budget": 100
    }
}
