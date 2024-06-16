import json

import redis
from config.app_logger import logger
from .aws import secrets

MINUTE = 60
MONTHLY_TTL = 30 * 86400
WEEKLY_TTL = 7 * 86400
DAILY_TTL = 86400

host = secrets['REDIS_HOST']
username = ""
password = ""
port = secrets['REDIS_PORT']
db_index = 0
redis_ssl = False
redis_url = secrets['REDIS_URL']



class RedisCache:
    def __init__(self, url: str = None):
        self.log = logger
        if url:
            self.redis_client = redis.from_url(url, decode_responses=True)
        else:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                username=username,
                password=password,
                decode_responses=True,
                db=db_index,
                ssl=redis_ssl
            )
        self.log.info(self.redis_client.ping())

    def set(self, key: str, value: any, duration: int = MONTHLY_TTL) -> bool:
        if isinstance(value, (list, dict)):
            value = json.dumps(value, default=str)
        return self.redis_client.set(key, value, ex=duration)

    def get(self, key: str) -> any:
        value = self.redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

    def delete(self, key: str) -> int:
        return self.redis_client.delete(key)


redis_db = RedisCache(url=redis_url)
