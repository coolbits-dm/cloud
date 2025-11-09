# Circuit breaker for M19.4
import time
import logging
from typing import Dict, Optional
from enum import Enum
import threading

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, failing fast
    HALF_OPEN = "half_open"  # Testing if service is back

class CircuitBreaker:
    """Circuit breaker for individual agents/services"""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 success_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.lock = threading.Lock()
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise CircuitBreakerOpenException("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit"""
        if self.state != CircuitState.OPEN:
            return False
        
        if self.last_failure_time is None:
            return True
        
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info("Circuit breaker reset to CLOSED")
        else:
            # Reset failure count on success
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker opened from HALF_OPEN")
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def get_state(self) -> CircuitState:
        """Get current circuit state"""
        with self.lock:
            return self.state
    
    def get_stats(self) -> Dict:
        """Get circuit breaker statistics"""
        with self.lock:
            return {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "last_failure_time": self.last_failure_time
            }

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass

class CircuitBreakerManager:
    """Manager for multiple circuit breakers"""
    
    def __init__(self):
        self.breakers = {}
        self.lock = threading.Lock()
    
    def get_breaker(self, service_name: str) -> CircuitBreaker:
        """Get circuit breaker for service"""
        with self.lock:
            if service_name not in self.breakers:
                self.breakers[service_name] = CircuitBreaker()
            return self.breakers[service_name]
    
    def call_with_breaker(self, service_name: str, func, *args, **kwargs):
        """Call function with circuit breaker protection"""
        breaker = self.get_breaker(service_name)
        return breaker.call(func, *args, **kwargs)
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """Get statistics for all circuit breakers"""
        with self.lock:
            return {name: breaker.get_stats() for name, breaker in self.breakers.items()}
    
    def is_open(self, service_name: str) -> bool:
        """Check if circuit breaker is open for service"""
        breaker = self.get_breaker(service_name)
        return breaker.get_state() == CircuitState.OPEN

# Global circuit breaker manager
circuit_breaker_manager = CircuitBreakerManager()

def call_with_breaker(service_name: str, func, *args, **kwargs):
    """Call function with circuit breaker protection"""
    return circuit_breaker_manager.call_with_breaker(service_name, func, *args, **kwargs)

def is_circuit_open(service_name: str) -> bool:
    """Check if circuit breaker is open for service"""
    return circuit_breaker_manager.is_open(service_name)

def get_circuit_stats() -> Dict[str, Dict]:
    """Get circuit breaker statistics"""
    return circuit_breaker_manager.get_all_stats()
