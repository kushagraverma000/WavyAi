"""Rate limiting middleware."""
from typing import Callable, Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
from collections import defaultdict

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.redis_client import get_redis_client

settings = get_settings()
logger = get_logger(__name__)


class RateLimiter:
    """Rate limiter using Redis or in-memory storage."""

    def __init__(self):
        """Initialize rate limiter."""
        self.redis_client = get_redis_client()
        self.in_memory_storage: Dict[str, List[float]] = defaultdict(list)
        self.rate_limit_per_hour = settings.RATE_LIMIT_PER_HOUR
        self.window_seconds = 3600  # 1 hour

    def is_rate_limited(self, identifier: str) -> bool:
        """Check if identifier is rate limited."""
        current_time = time.time()
        
        # Try Redis first
        if self.redis_client and self.redis_client.client:
            try:
                key = f"rate_limit:{identifier}"
                count = self.redis_client.client.incr(key)
                
                if count == 1:
                    # Set expiration on first request
                    self.redis_client.client.expire(key, self.window_seconds)
                
                return count > self.rate_limit_per_hour
            except Exception as e:
                logger.warning("Rate limit Redis check failed, using in-memory", error=str(e))
                # Fall back to in-memory
        
        # In-memory fallback
        window_start = current_time - self.window_seconds
        if identifier not in self.in_memory_storage:
            self.in_memory_storage[identifier] = []
        
        requests = self.in_memory_storage[identifier]
        
        # Remove old requests
        requests[:] = [req_time for req_time in requests if req_time > window_start]
        
        # Check rate limit
        if len(requests) >= self.rate_limit_per_hour:
            return True
        
        # Add current request
        requests.append(current_time)
        return False

    def get_remaining_requests(self, identifier: str) -> int:
        """Get remaining requests for identifier."""
        current_time = time.time()
        
        # Try Redis first
        if self.redis_client and self.redis_client.client:
            try:
                key = f"rate_limit:{identifier}"
                count = int(self.redis_client.client.get(key) or 0)
                return max(0, self.rate_limit_per_hour - count)
            except Exception as e:
                logger.warning("Rate limit Redis check failed, using in-memory", error=str(e))
                # Fall back to in-memory
        
        # In-memory fallback
        window_start = current_time - self.window_seconds
        if identifier not in self.in_memory_storage:
            self.in_memory_storage[identifier] = []
        
        requests = self.in_memory_storage[identifier]
        requests[:] = [req_time for req_time in requests if req_time > window_start]
        
        return max(0, self.rate_limit_per_hour - len(requests))


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


async def rate_limit_middleware(request: Request, call_next: Callable):
    """Rate limiting middleware."""
    # Get identifier (IP address or user ID)
    identifier = request.client.host if request.client else "unknown"
    
    # Check rate limit
    rate_limiter = get_rate_limiter()
    if rate_limiter.is_rate_limited(identifier):
        remaining = rate_limiter.get_remaining_requests(identifier)
        logger.warning("Rate limit exceeded", identifier=identifier, remaining=remaining)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Limit: {settings.RATE_LIMIT_PER_HOUR} requests per hour.",
                "retry_after": 3600,
            },
            headers={
                "X-RateLimit-Limit": str(settings.RATE_LIMIT_PER_HOUR),
                "X-RateLimit-Remaining": str(remaining),
                "Retry-After": "3600",
            },
        )
    
    # Add rate limit headers
    response = await call_next(request)
    remaining = rate_limiter.get_remaining_requests(identifier)
    response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_PER_HOUR)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    return response

