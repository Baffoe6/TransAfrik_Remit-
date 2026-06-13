"""Phase 4 unit tests."""

from decimal import Decimal

from app.retail_network.registry import get_retail_network, list_retail_networks
from app.payment_providers.base import PaymentReferenceRequest
from app.providers.mukuru.mock_mukuru import MockMukuruProvider
from app.providers.mukuru.live_mukuru import LiveMukuruProvider
from app.providers.base import TransferRequest


def test_retail_networks_listed():
    networks = list_retail_networks()
    for code in ("pay_at", "easy_pay", "kazang", "flash", "shoprite", "pick_n_pay"):
        assert code in networks


def test_kazang_voucher_generation():
    network = get_retail_network("kazang")
    result = network.generate_voucher(
        PaymentReferenceRequest(
            transfer_reference="TA123456",
            amount=Decimal("500.00"),
            currency="ZAR",
            customer_name="Test User",
            customer_email="test@example.com",
        )
    )
    assert result.success
    assert result.reference_number
    assert result.barcode_data


def test_mock_mukuru_provider():
    provider = MockMukuruProvider()
    assert provider.validate_credentials()
    req = TransferRequest(
        transfer_id=1,
        reference="TA000001",
        sender_name="Sender",
        sender_phone=None,
        sender_id_number=None,
        beneficiary_name="Receiver",
        beneficiary_country="GH",
        mobile_money_provider="MTN Ghana",
        mobile_wallet_number="233241234567",
        send_amount_zar=Decimal("1000"),
        receive_amount_ghs=Decimal("720"),
        exchange_rate=Decimal("0.72"),
        fee_zar=Decimal("49"),
    )
    result = provider.create_transfer(req)
    assert result.success
    assert result.provider_reference


def test_live_mukuru_not_configured():
    provider = LiveMukuruProvider({})
    assert not provider.validate_credentials()
    status = provider.get_api_status()
    assert status["mode"] == "not_configured"
