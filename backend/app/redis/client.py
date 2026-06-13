"""Redis client with in-memory fallback for dev/tests."""

import json
import time
from typing import Any

from app.config import get_settings

_redis_client = None
_memory_store: dict[str, tuple[str, float | None]] = {}


class _MemoryRedis:
    """Minimal Redis-compatible subset for offline dev."""

    def set(self, key: str, value: str, ex: int | None = None, nx: bool = False) -> bool | None:
        if nx and key in _memory_store:
            return None
        expiry = time.time() + ex if ex else None
        _memory_store[key] = (value, expiry)
        return True

    def get(self, key: str) -> str | None:
        entry = _memory_store.get(key)
        if not entry:
            return None
        value, expiry = entry
        if expiry and time.time() > expiry:
            del _memory_store[key]
            return None
        return value

    def delete(self, key: str) -> int:
        if key in _memory_store:
            del _memory_store[key]
            return 1
        return 0

    def exists(self, key: str) -> int:
        return 1 if self.get(key) is not None else 0

    def incr(self, key: str) -> int:
        current = int(self.get(key) or 0)
        current += 1
        self.set(key, str(current))
        return current

    def expire(self, key: str, seconds: int) -> bool:
        entry = _memory_store.get(key)
        if entry:
            _memory_store[key] = (entry[0], time.time() + seconds)
            return True
        return False

    def lpush(self, key: str, value: str) -> int:
        raw = self.get(key)
        items = json.loads(raw) if raw else []
        items.insert(0, value)
        self.set(key, json.dumps(items))
        return len(items)

    def lrange(self, key: str, start: int, end: int) -> list[str]:
        raw = self.get(key)
        items = json.loads(raw) if raw else []
        return items[start : end + 1 if end >= 0 else None]

    def ping(self) -> bool:
        return True


def get_redis():
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    settings = get_settings()
    if not settings.redis_url:
        _redis_client = _MemoryRedis()
        return _redis_client

    try:
        import redis

        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        _redis_client.ping()
    except Exception:
        _redis_client = _MemoryRedis()
    return _redis_client


def redis_health() -> dict[str, Any]:
    try:
        r = get_redis()
        r.ping()
        backend = "redis" if settings_redis_configured() else "memory"
        return {"status": "healthy", "backend": backend}
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc)}


def settings_redis_configured() -> bool:
    return bool(get_settings().redis_url)
