"""Redis client configuration."""
from typing import Optional, Any
import json
import redis
from redis.exceptions import RedisError

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class RedisClient:
    """Redis client for caching."""

    def __init__(self):
        """Initialize Redis client."""
        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            self.client.ping()
            logger.info("Redis client initialized successfully")
        except RedisError as e:
            logger.error("Failed to initialize Redis client", error=str(e))
            self.client = None

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except (RedisError, json.JSONDecodeError) as e:
            logger.error("Failed to get from cache", error=str(e), key=key)
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600,
    ) -> bool:
        """Set value in cache."""
        if not self.client:
            return False
        
        try:
            self.client.setex(
                key,
                ttl,
                json.dumps(value, default=str),
            )
            return True
        except (RedisError, TypeError) as e:
            logger.error("Failed to set cache", error=str(e), key=key)
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.client:
            return False
        
        try:
            self.client.delete(key)
            return True
        except RedisError as e:
            logger.error("Failed to delete from cache", error=str(e), key=key)
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.client:
            return False
        
        try:
            return bool(self.client.exists(key))
        except RedisError as e:
            logger.error("Failed to check cache existence", error=str(e), key=key)
            return False


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    """Get Redis client instance."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client

