from app.whatsapp.base import WhatsAppBotTransport
from app.whatsapp.infobip_bot import InfobipWhatsAppTransport
from app.whatsapp.meta_cloud import MetaCloudWhatsAppTransport
from app.whatsapp.twilio_bot import TwilioWhatsAppBotTransport

_TRANSPORTS: dict[str, type] = {
    "twilio": TwilioWhatsAppBotTransport,
    "meta_cloud": MetaCloudWhatsAppTransport,
    "infobip": InfobipWhatsAppTransport,
}


def get_whatsapp_bot_transport(code: str, config: dict | None = None) -> WhatsAppBotTransport:
    config = config or {}
    factory = _TRANSPORTS.get(code)
    if not factory:
        raise ValueError(f"Unknown WhatsApp bot transport: {code}")
    if code == "twilio":
        return factory(
            account_sid=config.get("account_sid"),
            auth_token=config.get("auth_token"),
            from_number=config.get("from_number"),
        )
    if code == "meta_cloud":
        return factory(access_token=config.get("access_token"), phone_number_id=config.get("phone_number_id"))
    if code == "infobip":
        return factory(api_key=config.get("api_key"), base_url=config.get("base_url"))
    return factory()
