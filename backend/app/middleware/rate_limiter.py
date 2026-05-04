from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, List, Tuple
import time
import redis
from app.core.config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""
    
    def __init__(self, app, default_limit: int = 100, default_window: int = 60):
        super().__init__(app)
        self.default_limit = default_limit
        self.default_window = default_window
        
        # Initialize Redis client
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL)
            self.redis_client.ping()  # Test connection
        except Exception:
            self.redis_client = None
            print("Warning: Redis not available, using in-memory rate limiting")
        
        # In-memory fallback
        self.in_memory_store: Dict[str, List[float]] = {}
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Get rate limit rules for this endpoint
        limit, window = self._get_rate_limit_rules(request)
        
        # Check rate limit
        if not self._is_allowed(client_ip, limit, window):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "limit": limit,
                    "window": window,
                    "retry_after": self._get_retry_after(client_ip, window)
                }
            )
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(self._get_remaining_requests(client_ip, limit, window))
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + window))
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        return request.client.host
    
    def _get_rate_limit_rules(self, request: Request) -> Tuple[int, int]:
        """Get rate limit rules based on endpoint"""
        path = request.url.path
        method = request.method
        
        # Define rate limit rules
        rate_rules = {
            # API endpoints
            ("/api/v1/devices/", "GET"): (1000, 3600),  # 1000 requests per hour
            ("/api/v1/devices/", "PUT"): (200, 3600),    # 200 requests per hour
            ("/api/v1/devices/", "DELETE"): (50, 3600),  # 50 requests per hour
            
            # Analytics endpoints
            ("/api/v1/analytics/", "GET"): (500, 3600),   # 500 requests per hour
            ("/api/v1/analytics/", "POST"): (100, 3600),  # 100 requests per hour
            
            # AI endpoints (lower limits due to resource usage)
            ("/api/v1/ai/", "GET"): (200, 3600),         # 200 requests per hour
            ("/api/v1/ai/", "POST"): (50, 3600),         # 50 requests per hour
            
            # Alert endpoints
            ("/api/v1/alerts/", "GET"): (1000, 3600),    # 1000 requests per hour
            ("/api/v1/alerts/", "POST"): (200, 3600),    # 200 requests per hour
            
            # Health endpoints (no rate limiting)
            ("/api/v1/health/", "GET"): (10000, 60),     # 10000 requests per minute
            
            # WebSocket endpoints (no rate limiting)
            ("/ws/", "GET"): (10000, 60),
        }
        
        # Find matching rule
        for (pattern, rule_method), (limit, window) in rate_rules.items():
            if path.startswith(pattern) and method == rule_method:
                return limit, window
        
        # Default limits
        return self.default_limit, self.default_window
    
    def _is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        if self.redis_client:
            return self._is_allowed_redis(key, limit, window, now)
        else:
            return self._is_allowed_memory(key, limit, window, now)
    
    def _is_allowed_redis(self, key: str, limit: int, window: int, now: float) -> bool:
        """Check rate limit using Redis"""
        try:
            # Use Redis sliding window algorithm
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, now - window)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(now): now})
            
            # Set expiration
            pipe.expire(key, window)
            
            results = pipe.execute()
            current_requests = results[1]
            
            return current_requests < limit
        except Exception:
            # Fallback to in-memory if Redis fails
            return self._is_allowed_memory(key, limit, window, now)
    
    def _is_allowed_memory(self, key: str, limit: int, window: int, now: float) -> bool:
        """Check rate limit using in-memory storage"""
        if key not in self.in_memory_store:
            self.in_memory_store[key] = []
        
        # Remove old requests
        self.in_memory_store[key] = [
            req_time for req_time in self.in_memory_store[key]
            if now - req_time < window
        ]
        
        # Check if under limit
        if len(self.in_memory_store[key]) < limit:
            self.in_memory_store[key].append(now)
            return True
        
        return False
    
    def _get_retry_after(self, key: str, window: int) -> int:
        """Get retry after time in seconds"""
        if self.redis_client:
            try:
                # Get oldest request time
                oldest = self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest:
                    oldest_time = oldest[0][1]
                    retry_after = int(oldest_time + window - time.time())
                    return max(1, retry_after)
            except Exception:
                pass
        
        # Fallback for in-memory storage
        if key in self.in_memory_store and self.in_memory_store[key]:
            oldest_time = min(self.in_memory_store[key])
            retry_after = int(oldest_time + window - time.time())
            return max(1, retry_after)
        
        return window
    
    def _get_remaining_requests(self, key: str, limit: int, window: int) -> int:
        """Get remaining requests for the current window"""
        if self.redis_client:
            try:
                current = self.redis_client.zcard(key)
                return max(0, limit - current)
            except Exception:
                pass
        
        # Fallback for in-memory storage
        if key in self.in_memory_store:
            now = time.time()
            current = len([
                req_time for req_time in self.in_memory_store[key]
                if now - req_time < window
            ])
            return max(0, limit - current)
        
        return limit

class AdvancedRateLimiter:
    """Advanced rate limiter with multiple strategies"""
    
    def __init__(self):
        self.strategies = {
            "sliding_window": SlidingWindowRateLimiter(),
            "fixed_window": FixedWindowRateLimiter(),
            "token_bucket": TokenBucketRateLimiter(),
        }
    
    def is_allowed(self, key: str, strategy: str = "sliding_window", **kwargs) -> bool:
        """Check if request is allowed using specified strategy"""
        if strategy not in self.strategies:
            strategy = "sliding_window"
        
        return self.strategies[strategy].is_allowed(key, **kwargs)

class SlidingWindowRateLimiter:
    """Sliding window rate limiter"""
    
    def __init__(self):
        self.windows = {}
    
    def is_allowed(self, key: str, limit: int = 100, window: int = 60) -> bool:
        now = time.time()
        
        if key not in self.windows:
            self.windows[key] = []
        
        # Remove old requests
        self.windows[key] = [
            req_time for req_time in self.windows[key]
            if now - req_time < window
        ]
        
        # Check if under limit
        if len(self.windows[key]) < limit:
            self.windows[key].append(now)
            return True
        
        return False

class FixedWindowRateLimiter:
    """Fixed window rate limiter"""
    
    def __init__(self):
        self.counters = {}
        self.windows = {}
    
    def is_allowed(self, key: str, limit: int = 100, window: int = 60) -> bool:
        now = time.time()
        current_window = int(now // window) * window
        
        if key not in self.windows or self.windows[key] != current_window:
            self.windows[key] = current_window
            self.counters[key] = 0
        
        if self.counters[key] < limit:
            self.counters[key] += 1
            return True
        
        return False

class TokenBucketRateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self):
        self.buckets = {}
    
    def is_allowed(self, key: str, capacity: int = 100, refill_rate: float = 1.0) -> bool:
        now = time.time()
        
        if key not in self.buckets:
            self.buckets[key] = {
                "tokens": capacity,
                "last_refill": now
            }
        
        bucket = self.buckets[key]
        
        # Refill tokens
        time_passed = now - bucket["last_refill"]
        tokens_to_add = time_passed * refill_rate
        bucket["tokens"] = min(capacity, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now
        
        # Check if token available
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True
        
        return False
