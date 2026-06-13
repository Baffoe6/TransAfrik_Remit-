"""Pilot workflow tests."""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.models.enums import PilotCustomerStatus, PilotInviteStatus
from app.services.pilot_service import get_pilot_settings, validate_invite_for_registration


def test_pilot_customer_status_enum():
    assert PilotCustomerStatus.APPROVED.value == "approved"
    assert PilotInviteStatus.ACTIVE.value == "active"


def test_validate_invite_when_pilot_disabled(monkeypatch):
    db = MagicMock()
    settings = MagicMock()
    settings.pilot_mode_enabled = False
    settings.invite_only_registration = True
    monkeypatch.setattr("app.services.pilot_service.get_pilot_settings", lambda d: settings)
    assert validate_invite_for_registration(db, "test@example.com", "+27721234567", None) is None


def test_validate_invite_requires_code(monkeypatch):
    db = MagicMock()
    settings = MagicMock()
    settings.pilot_mode_enabled = True
    settings.invite_only_registration = True
    monkeypatch.setattr("app.services.pilot_service.get_pilot_settings", lambda d: settings)
    from fastapi import HTTPException
    with pytest.raises(HTTPException, match="invite"):
        validate_invite_for_registration(db, "test@example.com", "+27721234567", None)
