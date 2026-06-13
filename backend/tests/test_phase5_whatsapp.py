"""WhatsApp bot service tests."""

from unittest.mock import MagicMock, patch

from app.services.whatsapp_bot_service import MENU, _contact_support, handle_inbound_message
from app.whatsapp.base import WhatsAppInboundMessage


def test_menu_constant():
    assert "Track Transfer" in MENU
    assert "Contact Support" in MENU


def test_contact_support():
    response = _contact_support()
    assert "support" in response.lower()


@patch("app.services.whatsapp_bot_service.log_operations_action")
@patch("app.services.whatsapp_bot_service._log_conversation")
def test_menu_response(mock_log, mock_audit):
    db = MagicMock()
    response = handle_inbound_message(
        db,
        WhatsAppInboundMessage(from_number="+27821234567", body="menu"),
        transport_code="twilio",
    )
    assert "Track Transfer" in response
    mock_log.assert_called_once()


@patch("app.services.whatsapp_bot_service.log_operations_action")
@patch("app.services.whatsapp_bot_service._log_conversation")
def test_contact_support_option(mock_log, mock_audit):
    db = MagicMock()
    response = handle_inbound_message(
        db,
        WhatsAppInboundMessage(from_number="+27821234567", body="5"),
        transport_code="twilio",
    )
    assert "support" in response.lower()
