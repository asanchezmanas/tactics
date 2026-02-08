from .config import ALGORITHM_CONFIG

def segment_customers(rfm_pred, config=None):
    """
    Classifies customers using configurable thresholds.
    """
    if config is None:
        config = ALGORITHM_CONFIG["segmentation"]

    def categorize(row):
        prob = row['prob_alive']
        clv = row['clv_12m']
        
        # 1. VIPs at risk
        v = config["vip_at_risk"]
        if prob < v["prob_alive_threshold"] and clv > v["clv_threshold"]:
            return v["label"]
            
        # 2. Customers already lost
        l = config["lost_customer"]
        if prob < l["prob_alive_threshold"]:
            return l["label"]
            
        # 3. Loyal and active customers
        ly = config["loyal_customer"]
        if prob > ly["prob_alive_threshold"] and row['expected_purchases_90d'] > ly["expected_purchases_threshold"]:
            return ly["label"]
            
        # 4. Potencial Ballena
        w = config["whale_potential"]
        if clv > w["clv_threshold"]:
            return w["label"]
            
        return config["default_label"]

    rfm_pred['segmento'] = rfm_pred.apply(categorize, axis=1)
    return rfm_pred
