from core.redis_client import r

def get_cache(key):
    return r.get(key)

def set_cache(key, value):
    r.setex(key, 3600, value)