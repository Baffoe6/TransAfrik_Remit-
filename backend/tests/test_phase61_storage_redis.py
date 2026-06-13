"""Phase 6.1: storage and Redis layer tests."""

import io

from app.redis.otp_store import store_otp, verify_otp
from app.redis.rate_limit import check_rate_limit
from app.redis.session_blacklist import blacklist_token, is_token_blacklisted
from app.storage import get_storage


def test_local_storage_roundtrip():
    storage = get_storage()
    key = "test/sample.txt"
    content = b"TransAfrik storage test"
    storage.save(key, content)
    assert storage.exists(key)
    assert storage.read(key) == content
    storage.delete(key)
    assert not storage.exists(key)


def test_storage_save_file():
    storage = get_storage()
    key = "test/upload.bin"
    data = io.BytesIO(b"binary upload test")
    storage.save_file(key, data)
    assert storage.read(key) == b"binary upload test"


def test_otp_store_and_verify():
    store_otp("test", "user+27123456789", "123456", ttl=60)
    assert verify_otp("test", "user+27123456789", "123456") is True
    assert verify_otp("test", "user+27123456789", "123456") is False


def test_session_blacklist():
    blacklist_token("jti-test-abc", ttl_seconds=60)
    assert is_token_blacklisted("jti-test-abc") is True
    assert is_token_blacklisted("jti-other") is False


def test_rate_limit():
    allowed1, c1 = check_rate_limit("test-key", 2, 60)
    allowed2, c2 = check_rate_limit("test-key", 2, 60)
    allowed3, c3 = check_rate_limit("test-key", 2, 60)
    assert allowed1 and allowed2
    assert not allowed3
    assert c3 == 3
