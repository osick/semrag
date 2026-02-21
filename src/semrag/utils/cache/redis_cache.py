import redis
import json
import hashlib
from typing import Optional, Any

class RedisCache:
    """
    Persistent Redis cache for SEMRAG embeddings and response context.
    """
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, expiration: int = 86400):
        self._redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self._expiration = expiration

    def _generate_key(self, prefix: str, data: str) -> str:
        """Generates a hashed key for the given data."""
        return f"{prefix}:{hashlib.sha256(data.encode()).hexdigest()}"

    def get(self, prefix: str, key_data: str) -> Optional[Any]:
        """Retrieves data from the cache."""
        key = self._generate_key(prefix, key_data)
        value = self._redis.get(key)
        if value:
            return json.loads(value)
        return None

    def set(self, prefix: str, key_data: str, value: Any) -> None:
        """Sets data in the cache with expiration."""
        key = self._generate_key(prefix, key_data)
        self._redis.setex(key, self._expiration, json.dumps(value))

    def clear(self) -> None:
        """Wipes the cache."""
        self._redis.flushdb()
