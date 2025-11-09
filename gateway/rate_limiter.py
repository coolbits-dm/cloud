# Rate limiter with token bucket algorithm
import time
import threading
from typing import Dict, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class TokenBucket:
    """Token bucket rate limiter"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens, return True if successful"""
        with self.lock:
            now = time.time()
            # Refill tokens based on time elapsed
            time_passed = now - self.last_refill
            tokens_to_add = time_passed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now
            
            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def get_retry_after(self) -> float:
        """Get seconds until next token is available"""
        with self.lock:
            if self.tokens >= 1:
                return 0.0
            return 1.0 / self.refill_rate

class RateLimiter:
    """Rate limiter with per-IP token buckets"""
    
    def __init__(self):
        self.buckets = defaultdict(lambda: defaultdict(TokenBucket))
        self.lock = threading.Lock()
        
        # Rate limits per endpoint
        self.limits = {
            "/v1/nha/invoke": {"capacity": 30, "refill_rate": 30/60},  # 30/min
            "/v1/rag/query": {"capacity": 60, "refill_rate": 60/60},    # 60/min
            "/v1/flows": {"capacity": 10, "refill_rate": 10/60},       # 10/min
            "/v1/flows/": {"capacity": 10, "refill_rate": 10/60},      # 10/min (flows/{id})
        }
    
    def _get_client_ip(self, request) -> str:
        """Extract client IP from request"""
        # Try various headers for IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to request client
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    def _get_endpoint_pattern(self, path: str) -> Optional[str]:
        """Get endpoint pattern for rate limiting"""
        for pattern in self.limits.keys():
            if path.startswith(pattern):
                return pattern
        return None
    
    def is_allowed(self, request) -> tuple[bool, float]:
        """Check if request is allowed, return (allowed, retry_after)"""
        client_ip = self._get_client_ip(request)
        endpoint_pattern = self._get_endpoint_pattern(request.url.path)
        
        if not endpoint_pattern:
            return True, 0.0
        
        with self.lock:
            bucket = self.buckets[client_ip][endpoint_pattern]
            
            # Initialize bucket if needed
            if bucket.capacity == 0:
                limit_config = self.limits[endpoint_pattern]
                bucket.capacity = limit_config["capacity"]
                bucket.refill_rate = limit_config["refill_rate"]
            
            if bucket.consume():
                return True, 0.0
            else:
                retry_after = bucket.get_retry_after()
                logger.warning(f"Rate limit exceeded for {client_ip} on {endpoint_pattern}, retry after {retry_after}s")
                return False, retry_after
    
    def cleanup_old_buckets(self, max_age_seconds: int = 3600):
        """Clean up old unused buckets"""
        with self.lock:
            now = time.time()
            to_remove = []
            
            for client_ip, endpoint_buckets in self.buckets.items():
                for endpoint, bucket in endpoint_buckets.items():
                    if now - bucket.last_refill > max_age_seconds:
                        to_remove.append((client_ip, endpoint))
            
            for client_ip, endpoint in to_remove:
                del self.buckets[client_ip][endpoint]
                if not self.buckets[client_ip]:
                    del self.buckets[client_ip]

# Global rate limiter
rate_limiter = RateLimiter()

def check_rate_limit(request) -> tuple[bool, float]:
    """Check rate limit for request"""
    return rate_limiter.is_allowed(request)

def cleanup_rate_limits():
    """Clean up old rate limit buckets"""
    rate_limiter.cleanup_old_buckets()
