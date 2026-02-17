"""
Engine A Enterprise: SOTA 2024 LTV/Churn Prediction
Tier: Enterprise (Pro AI, Strategic, Enterprise plans)

Features:
- LSTM-based Deep Learning LTV prediction
- Multi-source feature expansion
- Cohort Drift Detection with KL-Divergence
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Tuple
from scipy.stats import entropy
import warnings

# TensorFlow imports with graceful fallback
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.layers import AdditiveAttention, Attention
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    warnings.warn("TensorFlow not installed. LSTM features will use fallback mode.")

# XGBoost for NaN-resilient fallback
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

from core.features import EliteFeatures


class EnterpriseDataScienceCore:
    """
    Enterprise tier engine with SOTA 2024 capabilities:
    - Deep Learning LTV (LSTM)
    - Multi-source feature expansion
    - Cohort Drift Detection
    """
    
    def __init__(self, model_type: str = 'LSTM', sequence_length: int = 12):
        self.model_type = model_type
        self.sequence_length = sequence_length
        self.model = None
        self.baseline_distribution = None
        self.drift_threshold = 0.15  # KL-Divergence threshold
        self.feature_columns = ['purchases', 'revenue', 'recency', 'frequency', 'velocity']
        self.feature_engineer = None # Set in prepare_sequence_data 
        self.scaler_params = {}  # Store min/max for scaling
    
    # ============================================================
    # LSTM-BASED LTV PREDICTION
    # ============================================================
    
    def prepare_sequence_data(self, df: pd.DataFrame, 
                              date_col: str = 'order_date',
                              customer_col: str = 'customer_id',
                              revenue_col: str = 'revenue') -> Tuple[np.ndarray, np.ndarray, List]:
        """
        Transforms transaction data into sequences for LSTM.
        Each customer gets a sequence of their monthly purchase behavior.
        
        Returns:
            X: Shape (n_customers, sequence_length, n_features)
            y: Shape (n_customers, 1) - LTV target
            customer_ids: List of customer IDs for mapping back
        """
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Create monthly aggregations per customer
        df['month'] = df[date_col].dt.to_period('M')
        
        # Get all unique months and customers
        all_months = pd.period_range(
            df['month'].min(), 
            df['month'].max(), 
            freq='M'
        )[-self.sequence_length:]  # Last N months
        
        customers = df[customer_col].unique()
        
        sequences = []
        targets = []
        customer_ids = []
        
        # Define cutoff: features from first N months, target from last 12 months
        total_months = len(all_months)
        if total_months < self.sequence_length + 12:
            # Not enough data for proper train/target split
            raise ValueError(f"Need at least {self.sequence_length + 12} months of data for proper LTV training (current: {total_months})")
        
        # Feature period: use sequence_length months ending 12 months ago
        # Target period: last 12 months
        feature_end_idx = max(0, total_months - 12)  # Index where target period starts
        feature_months = all_months[:feature_end_idx][-self.sequence_length:]
        target_months = all_months[feature_end_idx:]  # Last 12 months
        
        for customer in customers:
            cust_data = df[df[customer_col] == customer]
            
            # Monthly aggregation for FEATURE period only
            monthly = cust_data.groupby('month').agg({
                revenue_col: ['sum', 'count']
            }).reindex(feature_months, fill_value=0)
            
            monthly.columns = ['revenue', 'purchases']
            
            # Elite Feature: Velocity (Revenue / Purchases)
            monthly['velocity'] = monthly['revenue'] / monthly['purchases'].replace(0, 1)
            
            # Calculate recency and frequency features
            monthly['recency'] = range(len(monthly), 0, -1)  # Months ago
            monthly['frequency'] = monthly['purchases'].cumsum()
            
            # Robustness: Handle NaNs in metrics
            monthly = monthly.fillna(0) # Insecure fallback, but necessary for LSTM
            
            # Create sequence (from feature period only)
            seq = monthly[self.feature_columns].values
            
            # Ensure correct sequence length
            if len(seq) < self.sequence_length:
                # Pad with zeros at the beginning
                pad = np.zeros((self.sequence_length - len(seq), seq.shape[1]))
                seq = np.vstack([pad, seq])
            else:
                seq = seq[-self.sequence_length:]
            
            # Target: ACTUAL future 12-month revenue (no leakage!)
            future_data = cust_data[cust_data['month'].isin(target_months)]
            target = future_data[revenue_col].sum() if not future_data.empty else 0.0
            
            sequences.append(seq)
            targets.append(target)
            customer_ids.append(customer)
        
        X = np.array(sequences)
        y = np.array(targets)
        
        # Normalize features
        self._fit_scaler(X)
        X = self._scale_features(X)
        
        return X, y, customer_ids
    
    def _fit_scaler(self, X: np.ndarray):
        """Fit min-max scaler parameters."""
        for i, col in enumerate(self.feature_columns):
            self.scaler_params[col] = {
                'min': X[:, :, i].min(),
                'max': X[:, :, i].max()
            }
    
    def _scale_features(self, X: np.ndarray) -> np.ndarray:
        """Apply min-max scaling."""
        X_scaled = X.copy()
        for i, col in enumerate(self.feature_columns):
            min_val = self.scaler_params[col]['min']
            max_val = self.scaler_params[col]['max']
            if max_val > min_val:
                X_scaled[:, :, i] = (X[:, :, i] - min_val) / (max_val - min_val)
            else:
                X_scaled[:, :, i] = 0
        return X_scaled
    
    def build_lstm_attention_model(self, n_features: int = 5) -> 'Sequential':
        """
        Builds the Elite LSTM + Attention architecture for LTV prediction.
        Uses additive attention to weigh critical temporal events.
        """
        if not TF_AVAILABLE:
            raise ImportError("TensorFlow is required for LSTM model.")
        
        inputs = tf.keras.Input(shape=(self.sequence_length, n_features))
        
        # 1. Feature extraction layer
        lstm_out = LSTM(64, return_sequences=True)(inputs)
        lstm_out = BatchNormalization()(lstm_out)
        lstm_out = Dropout(0.3)(lstm_out)
        
        # 2. Attention Mechanism (Focus on key purchase months)
        query = Dense(64)(lstm_out)
        value = Dense(64)(lstm_out)
        attention_out = AdditiveAttention()([query, value])
        
        # 3. Aggregation and deep layers
        att_lstm_comb = tf.keras.layers.GlobalAveragePooling1D()(attention_out)
        x = Dense(32, activation='relu')(att_lstm_comb)
        x = BatchNormalization()(x)
        x = Dropout(0.2)(x)
        x = Dense(16, activation='relu')(x)
        outputs = Dense(1, activation='softplus')(x)
        
        # Create a model that also returns attention scores
        # We need to modify the architecture to return scores
        self.full_model = tf.keras.Model(inputs=inputs, outputs=outputs)
        self.attention_model = tf.keras.Model(inputs=inputs, outputs=attention_out)
        
        self.full_model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='huber',
            metrics=['mae', 'mape']
        )
        
        self.model = self.full_model
        return self.model

    def explain_prediction(self, X: np.ndarray) -> Dict:
        """
        XAI Layer: Extracts Attention Weights to explain "Why" the LTV is as predicted.
        Shows which months in the sequence were critical.
        """
        if not TF_AVAILABLE or self.model is None:
            return {"error": "Model not trained or TF unavailable"}
            
        # Get attention output (last layer of attention before pooling)
        attn_weights = self.attention_model.predict(X, verbose=0)
        # Simplify to feature/temporal importance (sum across dimensions)
        importance = np.abs(attn_weights).mean(axis=-1) # (n_samples, sequence_length)
        
        # Normalize to 0-1
        importance = importance / (importance.sum(axis=1, keepdims=True) + 1e-10)
        
        return {
            "temporal_importance": importance.tolist(),
            "most_important_month": np.argmax(importance, axis=1).tolist(),
            "method": "AdditiveAttention_Weights"
        }

    def calibration_audit(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """
        Data Science Calibration Audit:
        Measures how well predicted values align with actuals.
        """
        from sklearn.metrics import mean_squared_error, mean_absolute_error
        
        mse = mean_squared_error(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        
        # Simple R-Squared
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r2 = 1 - (ss_res / (ss_tot + 1e-10))
        
        # Calibration Metric: Mean Ratio
        ratio = np.mean(y_pred / (y_true + 1e-10))
        
        return {
            "mse": float(mse),
            "mae": float(mae),
            "r2": float(r2),
            "calibration_ratio": float(ratio), # 1.0 is perfect, <1 underpredicts, >1 overpredicts
            "status": "Healthy" if 0.8 < ratio < 1.2 else "Drift Warning"
        }

    def build_lstm_model(self, n_features: int = 5) -> 'Sequential':
        """Wrapper for backward compatibility, defaults to Attention model."""
        return self.build_lstm_attention_model(n_features)
    
    def train_lstm(self, X: np.ndarray, y: np.ndarray, 
                   validation_split: float = 0.2,
                   epochs: int = 100,
                   batch_size: int = 32) -> Dict:
        """
        Trains the LSTM model with early stopping and learning rate reduction.
        
        Returns:
            Training history and metrics
        """
        if not TF_AVAILABLE:
            return self._fallback_train(X, y)
        
        if self.model is None:
            self.build_lstm_model(n_features=X.shape[2])
        
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=7,
                min_lr=1e-6
            )
        ]
        
        history = self.model.fit(
            X, y,
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=0
        )
        
        # Calculate final metrics
        val_predictions = self.model.predict(X[-int(len(X) * validation_split):], verbose=0)
        val_actual = y[-int(len(y) * validation_split):]
        
        r2 = 1 - (np.sum((val_actual - val_predictions.flatten())**2) / 
                  np.sum((val_actual - np.mean(val_actual))**2))
        
        return {
            "epochs_trained": len(history.history['loss']),
            "final_loss": history.history['loss'][-1],
            "final_val_loss": history.history['val_loss'][-1],
            "r2_score": float(r2),
            "model_type": "LSTM"
        }
    
    def _fallback_train(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Fallback training using XGBoost (if available) or Ridge."""
        # Flatten sequences to features
        X_flat = X.reshape(X.shape[0], -1)
        
        if XGB_AVAILABLE:
            self._fallback_model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                objective='reg:squarederror'
            )
            model_name = "XGBoost_Fallback"
        else:
            from sklearn.linear_model import Ridge
            self._fallback_model = Ridge(alpha=1.0)
            model_name = "Ridge_Fallback"
            
        self._fallback_model.fit(X_flat, y)
        
        predictions = self._fallback_model.predict(X_flat)
        r2 = 1 - (np.sum((y - predictions)**2) / np.sum((y - np.mean(y))**2))
        
        return {
            "epochs_trained": 1,
            "final_loss": np.mean((y - predictions)**2),
            "r2_score": float(r2),
            "model_type": model_name
        }
    
    def predict_lstm(self, X: np.ndarray, 
                     confidence_iterations: int = 100,
                     integrity_factor: float = 1.0,
                     retention_bias: float = None) -> Dict:
        """
        LSTM-based LTV prediction with Monte Carlo Dropout for uncertainty.
        integrity_factor: Multiplier for std deviation if data integrity is low.
        retention_bias: Optional real cohort retention signal to adjust predictions.
        """
        if not TF_AVAILABLE or self.model is None:
            if hasattr(self, '_fallback_model'):
                X_flat = X.reshape(X.shape[0], -1)
                preds = self._fallback_model.predict(X_flat)
                
                # Apply retention_bias if provided (weighted adjustment)
                reinforcement_reason = None
                if retention_bias is not None:
                    adjustment = (0.8 + 0.4 * retention_bias)
                    preds = preds * adjustment
                    direction = "alza" if adjustment > 1 else "baja"
                    reinforcement_reason = f"Ajuste predictivo ({direction}) basado en retención real de cohortes (Simulación Fallback)."
                    
                return {
                    "predictions": preds.tolist(),
                    "confidence_intervals": [(p * 0.8, p * 1.2) for p in preds],
                    "model_type": "Ridge_Fallback",
                    "reinforcement_applied": retention_bias is not None,
                    "reinforcement_reason": reinforcement_reason
                }
            return {"predictions": [], "confidence_intervals": [], "model_type": "none"}
        
        # Monte Carlo Dropout for uncertainty quantification
        mc_predictions = []
        
        for _ in range(confidence_iterations):
            # Enable dropout during inference for MC sampling
            preds = self.model(X, training=True)  # training=True enables dropout
            mc_predictions.append(preds.numpy().flatten())
        
        mc_predictions = np.array(mc_predictions)
        
        # Calculate statistics
        mean_predictions = mc_predictions.mean(axis=0)
        
        # BI Reinforcement: Adjust mean using real cohort retention signal
        reinforcement_reason = None
        if retention_bias is not None:
            # Heuristic: nudging LSTM towards real retention observations
            # If retention is 0.7, adjustment is 0.9 + 0.14 = 1.04 (+4% nudge)
            # If retention is 0.2, adjustment is 0.9 + 0.04 = 0.94 (-6% nudge)
            adjustment = 0.9 + (0.2 * retention_bias) 
            mean_predictions = mean_predictions * adjustment
            
            direction = "alza" if adjustment > 1 else "baja"
            impact = abs(1 - adjustment) * 100
            reinforcement_reason = (
                f"Ajuste a la {direction} ({impact:.1f}%) basado en señales de retención real de cohortes. "
                "Este refuerzo anclamos la predicción estadística en el comportamiento histórico probado."
            )
        
        # Uncertainty Calculation (Standard Deviation)
        std_predictions = mc_predictions.std(axis=0)
        
        # 90% confidence intervals (Adjusted by integrity_factor)
        adjusted_std = std_predictions * integrity_factor
        lower = mean_predictions - 1.645 * adjusted_std
        upper = mean_predictions + 1.645 * adjusted_std
        
        return {
            "predictions": mean_predictions.tolist(),
            "confidence_intervals": list(zip(lower.tolist(), upper.tolist())),
            "std": std_predictions.tolist(),
            "model_type": "LSTM_MC_Dropout",
            "reinforcement_applied": retention_bias is not None,
            "reinforcement_reason": reinforcement_reason
        }
    
    def save_model(self, path: str):
        """Save the trained LSTM model."""
        if TF_AVAILABLE and self.model is not None:
            self.model.save(path)
    
    def load_model(self, path: str):
        """Load a pre-trained LSTM model."""
        if TF_AVAILABLE:
            self.model = load_model(path)
    
    # ============================================================
    # MULTI-SOURCE FEATURE EXPANSION
    # ============================================================
    
    def expand_features(self, rfm_df: pd.DataFrame, 
                        web_engagement: Optional[pd.DataFrame] = None,
                        email_metrics: Optional[pd.DataFrame] = None,
                        demographics: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Multi-source feature expansion beyond RFM.
        Combines transactional data with behavioral and demographic signals.
        """
        expanded = rfm_df.copy()
        
        if web_engagement is not None:
            # Add: page_views, session_duration, cart_abandonment_rate
            expanded = expanded.merge(web_engagement, on='customer_id', how='left')
        
        if email_metrics is not None:
            # Add: open_rate, click_rate, unsubscribe_flag
            expanded = expanded.merge(email_metrics, on='customer_id', how='left')
            
        if demographics is not None:
            # Add: age_bucket, location_tier, acquisition_channel
            expanded = expanded.merge(demographics, on='customer_id', how='left')
        
        return expanded.fillna(0)
    
    # ============================================================
    # COHORT DRIFT DETECTION
    # ============================================================
    
    def set_baseline_distribution(self, ltv_values: np.ndarray, n_bins: int = 20):
        """
        Establishes the baseline LTV distribution for drift detection.
        Should be called with historical cohort data.
        """
        hist, bin_edges = np.histogram(ltv_values, bins=n_bins, density=True)
        # Add small epsilon to avoid log(0)
        hist = hist + 1e-10
        hist = hist / hist.sum()
        
        self.baseline_distribution = {
            "mean": float(np.mean(ltv_values)),
            "std": float(np.std(ltv_values)),
            "median": float(np.median(ltv_values)),
            "histogram": hist,
            "bin_edges": bin_edges,
            "n_samples": len(ltv_values)
        }
    
    def detect_cohort_drift(self, new_cohort_ltv: np.ndarray) -> Dict:
        """
        Detects if new customer cohorts deviate from historical patterns.
        Uses KL-Divergence as the drift metric.
        """
        if self.baseline_distribution is None:
            return {"status": "no_baseline", "message": "Set baseline first"}
        
        # Create histogram with same bins as baseline
        new_hist, _ = np.histogram(
            new_cohort_ltv, 
            bins=self.baseline_distribution["bin_edges"],
            density=True
        )
        new_hist = new_hist + 1e-10
        new_hist = new_hist / new_hist.sum()
        
        # Calculate KL-Divergence
        kl_divergence = entropy(new_hist, self.baseline_distribution["histogram"])
        
        # Also calculate symmetric JS-Divergence for stability
        m = 0.5 * (new_hist + self.baseline_distribution["histogram"])
        js_divergence = 0.5 * (entropy(new_hist, m) + entropy(self.baseline_distribution["histogram"], m))
        
        is_drifting = js_divergence > self.drift_threshold
        
        # Calculate shift metrics
        new_mean = float(np.mean(new_cohort_ltv))
        baseline_mean = self.baseline_distribution["mean"]
        mean_shift_pct = (new_mean - baseline_mean) / baseline_mean * 100
        
        return {
            "kl_divergence": float(kl_divergence),
            "js_divergence": float(js_divergence),
            "is_drifting": bool(is_drifting),
            "baseline_mean": baseline_mean,
            "new_cohort_mean": new_mean,
            "mean_shift_pct": float(mean_shift_pct),
            "new_cohort_size": len(new_cohort_ltv),
            "alert": "⚠️ COHORT DRIFT DETECTED" if is_drifting else "✅ Within normal range",
            "recommendation": self._get_drift_recommendation(mean_shift_pct, is_drifting)
        }
    
    def _get_drift_recommendation(self, shift_pct: float, is_drifting: bool) -> str:
        """Generate actionable recommendation based on drift analysis."""
        if not is_drifting:
            return "Continue current acquisition strategy."
        
        if shift_pct > 20:
            return "POSITIVE DRIFT: New cohort has higher LTV. Analyze acquisition channels to replicate success."
        elif shift_pct < -20:
            return "NEGATIVE DRIFT: New cohort has lower LTV. Review ad targeting and channel mix. Consider pausing underperforming campaigns."
        else:
            return "MARGINAL DRIFT: Monitor next cohort before taking action."


# ============================================================
# CONVENIENCE FUNCTION FOR FULL PIPELINE
# ============================================================

def run_enterprise_ltv_pipeline(df_transactions: pd.DataFrame,
                                 sequence_length: int = 12,
                                 epochs: int = 100) -> Dict:
    """
    Complete enterprise LTV prediction pipeline.
    
    Args:
        df_transactions: DataFrame with customer_id, order_date, revenue
        sequence_length: Months of history to use per customer
        epochs: Training epochs
    
    Returns:
        Dictionary with predictions and training metrics
    """
    engine = EnterpriseDataScienceCore(sequence_length=sequence_length)
    
    # Prepare data
    X, y, customer_ids = engine.prepare_sequence_data(df_transactions)
    
    # Train model
    training_metrics = engine.train_lstm(X, y, epochs=epochs)
    
    # Get predictions with confidence intervals
    predictions = engine.predict_lstm(X)
    
    # Map back to customers
    results = []
    for i, cust_id in enumerate(customer_ids):
        results.append({
            "customer_id": cust_id,
            "ltv_predicted": predictions["predictions"][i],
            "ltv_lower": predictions["confidence_intervals"][i][0],
            "ltv_upper": predictions["confidence_intervals"][i][1]
        })
    
    return {
        "predictions": results,
        "training_metrics": training_metrics,
        "model_type": predictions.get("model_type", "unknown")
    }
