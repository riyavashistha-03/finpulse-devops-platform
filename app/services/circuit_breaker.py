"""
SRE Resilience: Circuit Breaker Pattern for External Service Integrations
Prevents cascading microservice failures during upstream outages or latency spikes.
States:
  - CLOSED: Normal operation; requests pass through.
  - OPEN: Tripped due to repeated errors; requests fast-fail with deterministic fallback.
  - HALF_OPEN: Probing recovery; single trial request permitted to re-verify upstream health.
"""
import time
from typing import Callable, Any, Optional

class CircuitBreakerOpenException(Exception):
    """Raised when request is rejected because circuit breaker is currently OPEN."""
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 15.0, name: str = "MarketDataBreaker"):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name

        self.state = "CLOSED"
        self.failure_count = 0
        self.last_state_change = time.time()
        self.last_failure_time = 0.0
        self.success_count = 0

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute callable wrapped in circuit breaker protection."""
        now = time.time()

        if self.state == "OPEN":
            if now - self.last_state_change > self.recovery_timeout:
                self.state = "HALF_OPEN"
                self.last_state_change = now
            else:
                raise CircuitBreakerOpenException(f"Circuit breaker '{self.name}' is OPEN. Fast-failing request.")

        try:
            result = func(*args, **kwargs)
            self._handle_success()
            return result
        except Exception as e:
            self._handle_failure()
            raise e

    def _handle_success(self):
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.failure_count = 0
            self.last_state_change = time.time()
        self.success_count += 1

    def _handle_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.state in ["CLOSED", "HALF_OPEN"] and self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.last_state_change = time.time()

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "state": self.state,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout_seconds": self.recovery_timeout,
            "last_state_change_seconds_ago": round(time.time() - self.last_state_change, 1)
        }
