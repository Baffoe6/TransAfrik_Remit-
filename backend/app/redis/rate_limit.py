"""Redis-backed rate limiting."""

from app.redis.client import get_redis

RL_PREFIX = "rl:"


def check_rate_limit(key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
    """Returns (allowed, current_count)."""
    r = get_redis()
    redis_key = f"{RL_PREFIX}{key}"
    count = r.incr(redis_key)
    if count == 1:
        r.expire(redis_key, window_seconds)
    return count <= limit, count
