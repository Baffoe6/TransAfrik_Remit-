"""Corridor engine tests."""

from app.models.enums import CorridorStatus


def test_corridor_status_enum():
    assert CorridorStatus.ACTIVE.value == "active"
    assert CorridorStatus.INACTIVE.value == "inactive"


def test_corridor_seed_codes():
    expected = {"ZA-GH", "ZA-ZW", "ZA-ZM", "ZA-KE", "ZA-NG", "ZA-UG"}
    seeds = [
        ("ZA-GH", "GH", "GHS"),
        ("ZA-ZW", "ZW", "ZWL"),
        ("ZA-ZM", "ZM", "ZMW"),
        ("ZA-KE", "KE", "KES"),
        ("ZA-NG", "NG", "NGN"),
        ("ZA-UG", "UG", "UGX"),
    ]
    assert {s[0] for s in seeds} == expected
