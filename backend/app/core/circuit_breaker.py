import time
import logging
from typing import Callable, Any, Dict, Optional

logger = logging.getLogger(__name__)


class CircuitBreakerOpenException(Exception):
    """Raised when an external service circuit is tripped."""
    pass


class CircuitBreaker:
    """
    Lightweight in-memory Circuit Breaker to prevent cascading failures
    when third-party APIs (Groq, Meta, Google Calendar, Gemini) degrade or timeout.
    """
    def __init__(self, name: str, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def is_available(self) -> bool:
        if self.state == "CLOSED":
            return True
        now = time.time()
        if self.state == "OPEN":
            if now - self.last_failure_time >= self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info(f"[CircuitBreaker:{self.name}] Transitioned to HALF_OPEN probe.")
                return True
            return False
        return True  # HALF_OPEN allows a probe

    def record_success(self):
        if self.state != "CLOSED":
            logger.info(f"[CircuitBreaker:{self.name}] Service recovered. Transitioned to CLOSED.")
        self.state = "CLOSED"
        self.failure_count = 0

    def record_failure(self, err: Optional[Exception] = None):
        self.failure_count += 1
        self.last_failure_time = time.time()
        logger.warning(f"[CircuitBreaker:{self.name}] Failure #{self.failure_count}: {err}")
        if self.failure_count >= self.failure_threshold or self.state == "HALF_OPEN":
            self.state = "OPEN"
            logger.error(f"[CircuitBreaker:{self.name}] Failure threshold reached. Circuit is now OPEN (fail fast for {self.recovery_timeout}s).")

    def call(self, func: Callable, *args, **kwargs) -> Any:
        if not self.is_available():
            raise CircuitBreakerOpenException(f"Circuit breaker for '{self.name}' is OPEN.")
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure(e)
            raise e


# Registry of circuit breakers for external integrations
_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str, failure_threshold: int = 3, recovery_timeout: float = 30.0) -> CircuitBreaker:
    if name not in _breakers:
        _breakers[name] = CircuitBreaker(name, failure_threshold, recovery_timeout)
    return _breakers[name]
