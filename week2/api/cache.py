import os
import json
import redis

CACHE_TTL = 60
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
rd = redis.from_url(REDIS_URL, decode_responses=True)

def get_cache(key: str):
    data = rd.get(key)
    if data:
        print("cache hit!")
        return json.loads(data)
    return None

def set_cache(key: str, value, ttl: int = CACHE_TTL):
    rd.set(key, json.dumps(value, default=str), ex=ttl)

def delete_cache(key: str):
    rd.delete(key)
