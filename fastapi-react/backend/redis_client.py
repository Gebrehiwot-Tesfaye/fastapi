import redis
import json
import logging
from typing import Optional, Any
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._connect()
    
    def _connect(self):
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Successfully connected to Redis!")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def is_connected(self) -> bool:
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def get(self, key: str) -> Optional[Any]:
        if not self.is_connected():
            logger.warning("Redis not connected - returning None (cache miss)")
            return None
        try:
            data = self.redis_client.get(key)
            if data:
                logger.info(f"🎯 Cache HIT for key: {key}")
                return json.loads(data)
            logger.info(f"❌ Cache MISS for key: {key}")
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        if not self.is_connected():
            logger.warning("Redis not connected - cache not set")
            return False
        try:
            serialized = json.dumps(value, default=str)
            result = self.redis_client.setex(key, expire, serialized)
            logger.info(f"💾 Cache SET for key: {key} (expire: {expire}s)")
            return result
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        if not self.is_connected():
            return False
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        if not self.is_connected():
            return 0
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis delete pattern error: {e}")
            return 0

# Global Redis client instance
redis_client = RedisClient()
