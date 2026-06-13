from app.providers.partners.base import PartnerProvider
from app.providers.partners.mocks import FlutterwaveProvider, MukuruProvider, OnafriqProvider, VeenguProvider

_REGISTRY: dict[str, type[PartnerProvider]] = {
    "flutterwave": FlutterwaveProvider,
    "mukuru": MukuruProvider,
    "mock_mukuru": MukuruProvider,
    "mukuru_api": MukuruProvider,
    "onafriq": OnafriqProvider,
    "veengu": VeenguProvider,
}


def get_partner_provider(code: str) -> PartnerProvider:
    cls = _REGISTRY.get(code, MukuruProvider)
    return cls()


def list_partner_providers() -> list[str]:
    return list(_REGISTRY.keys())
