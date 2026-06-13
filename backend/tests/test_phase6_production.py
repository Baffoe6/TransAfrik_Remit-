"""Production config tests."""

from app.services.production_readiness import migration_safety_check, validate_production_config


def test_production_readiness_returns_checks():
    result = validate_production_config()
    assert "checks" in result
    assert result["total"] >= 5


def test_migration_safety():
    result = migration_safety_check("007", head_revision="007")
    assert result["safe_to_deploy"] is True
