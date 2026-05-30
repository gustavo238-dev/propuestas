import redis
import os

class CacheService:
    def __init__(self):
        self.client = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))

    def get(self, key: str):
        return self.client.get(key)

    def set(self, key: str, value: str, expire: int = 3600):
        self.client.setex(key, expire, value)