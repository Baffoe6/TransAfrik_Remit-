"""JWT/session token blacklist in Redis."""

from app.config import get_settings
from app.redis.client import get_redis

BLACKLIST_PREFIX = "bl:jti:"


def blacklist_token(jti: str, ttl_seconds: int | None = None) -> None:
    settings = get_settings()
    ttl = ttl_seconds or settings.access_token_expire_minutes * 60
    get_redis().set(f"{BLACKLIST_PREFIX}{jti}", "1", ex=ttl)


def is_token_blacklisted(jti: str) -> bool:
    return bool(get_redis().exists(f"{BLACKLIST_PREFIX}{jti}"))
