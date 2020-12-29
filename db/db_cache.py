from redis import Redis, ConnectionPool
from core import config


class Cache:
    _client = None

    @classmethod
    def client(cls):
        if cls._client:
            return cls._client
        else:
            pool = ConnectionPool(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
            cls._client = Redis(connection_pool=pool)
        return cls._client


cache = Cache().client()
