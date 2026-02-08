"""
Tactics Resilience Module
Provides patterns for fault tolerance: Circuit Breakers, Retries, and Rate Limiters.
"""

import time
import functools
import logging
import threading
from datetime import datetime, timedelta
from typing import Callable, Any, Dict, Optional, List

logger = logging.getLogger("tactics.resilience")

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    """
    Prevents cascading failures by stopping calls to a failing service.
    State: CLOSED (Normal) -> OPEN (Failing) -> HALF-OPEN (Testing)
    
    Thread-safe implementation using Lock for concurrent worker access.
    """
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, name: str = "CircuitBreaker"):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        
        self.failures = 0
        self.state = "CLOSED"
        self.last_failure_time: Optional[datetime] = None
        self._lock = threading.Lock()  # Thread safety

    def __call__(self, func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self._lock:
                if self.state == "OPEN":
                    if (datetime.now() - self.last_failure_time).total_seconds() > self.recovery_timeout:
                        self.state = "HALF-OPEN"
                        logger.info(f"[{self.name}] Circuit HALF-OPEN: Testing service...")
                    else:
                        logger.warning(f"[{self.name}] Circuit OPEN: Call blocked.")
                        raise CircuitBreakerOpenException(f"Circuit {self.name} is OPEN")
                current_state = self.state

            try:
                result = func(*args, **kwargs)
                
                with self._lock:
                    if current_state == "HALF-OPEN":
                        self.state = "CLOSED"
                        self.failures = 0
                        logger.info(f"[{self.name}] Circuit CLOSED: Service recovered.")
                    elif self.state == "CLOSED":
                        self.failures = 0
                    
                return result
                
            except Exception as e:
                with self._lock:
                    self.failures += 1
                    self.last_failure_time = datetime.now()
                    logger.error(f"[{self.name}] Call failed ({self.failures}/{self.failure_threshold}): {e}")
                    
                    if self.failures >= self.failure_threshold:
                        self.state = "OPEN"
                        logger.error(f"[{self.name}] Circuit OPENED due to failures.")
                
                raise e
        return wrapper

def retry_with_backoff(max_retries: int = 3, initial_delay: float = 1.0, backoff_factor: float = 2.0):
    """
    Decorator for exponential backoff retries.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                    
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= backoff_factor
            
            raise last_exception
        return wrapper
    return decorator

# Shared instances for specific services
# These should be imported where needed
_all_breakers = []

def register_breaker(breaker):
    _all_breakers.append(breaker)
    return breaker

shopify_breaker = register_breaker(CircuitBreaker(name="ShopifyAPI", failure_threshold=5, recovery_timeout=120))
meta_breaker = register_breaker(CircuitBreaker(name="MetaAPI", failure_threshold=5, recovery_timeout=300))
google_breaker = register_breaker(CircuitBreaker(name="GoogleAPI", failure_threshold=5, recovery_timeout=300))
klaviyo_breaker = register_breaker(CircuitBreaker(name="KlaviyoAPI", failure_threshold=5, recovery_timeout=120))
stripe_breaker = register_breaker(CircuitBreaker(name="StripeAPI", failure_threshold=5, recovery_timeout=60))
ga4_breaker = register_breaker(CircuitBreaker(name="GoogleAnalytics4", failure_threshold=5, recovery_timeout=300))
gsc_breaker = register_breaker(CircuitBreaker(name="GoogleSearchConsole", failure_threshold=5, recovery_timeout=300))

def get_circuit_breaker_status() -> List[Dict]:
    """Returns the status of all registered circuit breakers."""
    return [
        {
            "name": b.name,
            "state": b.state,
            "failures": b.failures,
            # "last_failure": b.last_failure_time.isoformat() if b.last_failure_time else None
        }
        for b in _all_breakers
    ]

class DataGuard:
    """
    Enforces data quality standards before processing.
    """
    @staticmethod
    def validate_sales_data(df) -> List[str]:
        errors = []
        if df.empty:
            return ["Dataset is empty"]
            
        required_cols = ['customer_id', 'order_date', 'revenue']
        for col in required_cols:
            if col not in df.columns:
                errors.append(f"Missing column: {col}")
                
        if 'revenue' in df.columns:
            if (df['revenue'] < 0).any():
                errors.append("Found negative revenue values")
                
        return errors

    @staticmethod
    def validate_marketing_data(df) -> List[str]:
        errors = []
        if df.empty:
            return ["Dataset is empty"]
            
        required_cols = ['fecha', 'canal', 'inversion']
        for col in required_cols:
            if col not in df.columns:
                errors.append(f"Missing column: {col}")
        
        return errors
