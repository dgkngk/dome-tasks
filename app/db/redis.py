import redis
from app.core.config import settings
from app.core.logger import dome_logger

class RedisConnectionError(Exception):
    """Raised when Redis connection fails"""

class RedisInterface:
    def __init__(self):
        self.client = None
        self.host = settings.REDIS_HOST
        self.port = settings.REDIS_PORT
        self.db = settings.REDIS_DB
        self.connect()

    def connect(self):
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=False,
                socket_connect_timeout=2
            )
            self.client.ping()
            dome_logger.info(f"Connected to Redis at {self.host}:{self.port}")
        except Exception as e:
            dome_logger.exception(f"Redis connection failed: {e}")
            raise RedisConnectionError("Could not connect to Redis") from e

    def setex(self, key, ttl, value):
        return self.client.setex(key, ttl, value)

    def get(self, key):
        return self.client.get(key)

    def exists(self, key):
        return self.client.exists(key) == 1

    def expire(self, key, ttl):
        return self.client.expire(key, ttl)

    def delete(self, key):
        return self.client.delete(key)

# Create a single Redis instance
redis_interface = RedisInterface()
