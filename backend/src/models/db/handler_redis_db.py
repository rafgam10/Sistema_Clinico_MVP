from dotenv import load_dotenv
import os

try:
    import redis
except ImportError:
    redis = None

load_dotenv()

class ConnectionDBRedis:
    
    def __init__(self):
        self.host = os.getenv("REDIS_HOST")
        self.port = int(os.getenv("REDIS_PORT", 6379))
        self.db = int(os.getenv("REDIS_DB", 0))
        self.password = os.getenv("REDIS_PASSWORD", None)
        self._connection = None
        
    def get_connection(self):
        if redis is None:
            return None

        if self._connection is None:
            self._connection = redis.Redis(
                self.host,
                self.port,
                self.db,
                self.password,
                decode_responses=True
            )
        return self._connection
    
    def ping(self):
        if redis is None:
            return False

        try:
            return self.get_connection().ping()
        except redis.ConnectionError:
            return False
        
    def set_cache(self, key, value, ttl=300):
        if redis is None:
            return None

        try:
            self.get_connection().setex(key, ttl, value)
        except redis.ConnectionError:
            return None
    
    def get_cache(self, key):
        if redis is None:
            return None

        try:
            return self.get_connection().get(key)
        except redis.ConnectionError:
            return None
    
    def delete_cache(self, key):
        if redis is None:
            return None

        try:
            return self.get_connection().delete(key)
        except redis.ConnectionError:
            return None
    
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc, tb):
        connection = self.get_connection()
        if connection is not None:
            connection.close()
        self._connection = None
