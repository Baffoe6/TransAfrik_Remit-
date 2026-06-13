"""Webhook processing queue in Redis."""

import json
from datetime import UTC, datetime

from app.redis.client import get_redis

QUEUE_KEY = "webhook:queue"
MAX_QUEUE_SIZE = 10000


def enqueue_webhook(provider_code: str, event_id: int, payload: dict) -> bool:
    r = get_redis()
    item = json.dumps({
        "provider_code": provider_code,
        "event_id": event_id,
        "payload": payload,
        "enqueued_at": datetime.now(UTC).isoformat(),
    })
    length = r.lpush(QUEUE_KEY, item)
    return length <= MAX_QUEUE_SIZE


def peek_queue(limit: int = 20) -> list[dict]:
    r = get_redis()
    items = r.lrange(QUEUE_KEY, 0, limit - 1)
    return [json.loads(i) for i in items]


def queue_depth() -> int:
    items = get_redis().lrange(QUEUE_KEY, 0, -1)
    return len(items)
