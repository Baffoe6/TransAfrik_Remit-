"""OTP storage in Redis."""

from app.redis.client import get_redis

OTP_PREFIX = "otp:"
OTP_TTL_SECONDS = 600


def store_otp(identifier: str, code: str, ttl: int = OTP_TTL_SECONDS) -> None:
    get_redis().set(f"{OTP_PREFIX}{identifier}", code, ex=ttl)


def verify_otp(identifier: str, code: str, *, consume: bool = True) -> bool:
    key = f"{OTP_PREFIX}{identifier}"
    r = get_redis()
    stored = r.get(key)
    if not stored or stored != code:
        return False
    if consume:
        r.delete(key)
    return True


def delete_otp(identifier: str) -> None:
    get_redis().delete(f"{OTP_PREFIX}{identifier}")
