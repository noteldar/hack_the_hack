import redis.asyncio as redis
from .config import settings

# Redis connection for general caching
redis_client = redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True
)

# Redis connection for Celery (separate database)
celery_redis_client = redis.from_url(
    settings.REDIS_CELERY_URL,
    encoding="utf-8",
    decode_responses=True
)