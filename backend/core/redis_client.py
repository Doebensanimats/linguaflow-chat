import redis
from config import REDIS_URL

r = redis.from_url(REDIS_URL)