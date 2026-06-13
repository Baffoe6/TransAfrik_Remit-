"""CORS configuration tests."""

from app.config import Settings


def test_vercel_regex_enabled_in_production():
    s = Settings(environment="production", cors_origins="http://localhost:3000")
    assert s.effective_cors_origin_regex == r"https://.*\.vercel\.app"


def test_vercel_regex_disabled_in_development():
    s = Settings(environment="development")
    assert s.effective_cors_origin_regex is None


def test_custom_regex_override():
    s = Settings(environment="production", cors_origin_regex=r"https://example\.com")
    assert s.effective_cors_origin_regex == r"https://example\.com"
