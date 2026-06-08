from dotenv import load_dotenv
import os
import redis

load_dotenv()

class ConnectionDBRedis:
    
    def __init__(self):
        self.host = os.getenv("REDIS_HOST")
        self.port = os.getenv("REDIS_PORT", 6379)
        self.db = os.getenv("REDIS_DB", 0)
        self.password = os.getenv("REDIS_PASSWORD", None)
        self._connection = None
        
    def get_connection(self):
        if self._connection is None:
            self.connection = redis.Redis(
                self.host,
                self.port,
                self.db,
                self.password,
                decode_responses=True
            )
        return self.connection
    
    def ping(self):
        try:
            return self.get_connection().ping()
        except redis.ConnectionError:
            return False
        
    def set_cache(self, key, value, ttl=300):
        try:
            self.get_connection().setex(key, ttl, value)
        except redis.ConnectionError:
            ...
    
    def get_cache(self, key):
        try:
            return self.get_connection().get(key)
        except redis.ConnectionError:
            return None
    
    def delete_cache(self, key):
        try:
            return self.get_connection().delete(key)
        except redis.ConnectionError:
            ...
    
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc, tb):
        self.get_connection().close()
        self._connection = None