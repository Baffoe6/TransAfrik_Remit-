"""OTP storage, rate limiting, and step-up session state in Redis."""

import json

from app.redis.client import get_redis

OTP_PREFIX = "otp:"
OTP_TTL_SECONDS = 600
OTP_RATE_PREFIX = "otp_rate:"
OTP_RATE_LIMIT = 5
OTP_RATE_WINDOW = 3600
STEPUP_PREFIX = "stepup:"
STEPUP_TTL = 600


def _otp_key(purpose: str, mobile: str) -> str:
    return f"{OTP_PREFIX}{purpose}:{mobile}"


def store_otp(purpose: str, mobile: str, code: str, *, metadata: dict | None = None, ttl: int = OTP_TTL_SECONDS) -> None:
    payload = {"code": code, "metadata": metadata or {}}
    get_redis().set(_otp_key(purpose, mobile), json.dumps(payload), ex=ttl)


def verify_otp(purpose: str, mobile: str, code: str, *, consume: bool = True) -> bool:
    key = _otp_key(purpose, mobile)
    r = get_redis()
    raw = r.get(key)
    if not raw:
        return False
    try:
        payload = json.loads(raw)
        stored = payload.get("code", raw)
    except (json.JSONDecodeError, TypeError):
        stored = raw
    if stored != code:
        return False
    if consume:
        r.delete(key)
    return True


def delete_otp(purpose: str, mobile: str) -> None:
    get_redis().delete(_otp_key(purpose, mobile))


def check_otp_rate_limit(mobile: str) -> bool:
    """Return True if under rate limit, False if exceeded."""
    key = f"{OTP_RATE_PREFIX}{mobile}"
    r = get_redis()
    count = r.incr(key)
    if count == 1:
        r.expire(key, OTP_RATE_WINDOW)
    return count <= OTP_RATE_LIMIT


def store_stepup(mobile: str, user_id: int, risk_score: int) -> None:
    get_redis().set(
        f"{STEPUP_PREFIX}{mobile}",
        json.dumps({"user_id": user_id, "risk_score": risk_score}),
        ex=STEPUP_TTL,
    )


def get_stepup(mobile: str) -> dict | None:
    raw = get_redis().get(f"{STEPUP_PREFIX}{mobile}")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def clear_stepup(mobile: str) -> None:
    get_redis().delete(f"{STEPUP_PREFIX}{mobile}")
