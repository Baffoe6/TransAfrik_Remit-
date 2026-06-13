from app.providers.base import RemittanceProvider
from app.providers.manual_mukuru import ManualMukuruProvider
from app.providers.mukuru.live_mukuru import LiveMukuruProvider
from app.providers.mukuru.mock_mukuru import MockMukuruProvider
from app.providers.mukuru_api import MukuruApiProvider
from app.providers.stubs import (
    FlutterwaveProvider,
    MukuruProvider,
    OnafriqProvider,
    StitchRemittanceProvider,
    VeenguProvider,
)

_PROVIDERS: dict[str, type[RemittanceProvider]] = {
    "manual_mukuru": ManualMukuruProvider,
    "mukuru_api": MukuruApiProvider,
    "mock_mukuru": MockMukuruProvider,
    "live_mukuru": LiveMukuruProvider,
    "veengu": VeenguProvider,
    "onafriq": OnafriqProvider,
    "flutterwave": FlutterwaveProvider,
    "stitch_remit": StitchRemittanceProvider,
}


def get_provider(provider_class: str) -> RemittanceProvider:
    provider_cls = _PROVIDERS.get(provider_class)
    if not provider_cls:
        raise ValueError(f"Unknown provider class: {provider_class}")
    return provider_cls()
