from app.notifications.base import EmailProvider, SmsProvider
from app.notifications.sms import AfricasTalkingSmsProvider, ConsoleSmsProvider, TwilioSmsProvider
from app.notifications.smtp_email import SendGridEmailProvider, SesEmailProvider, SmtpEmailProvider
from app.notifications.whatsapp import ConsoleWhatsAppProvider, TwilioWhatsAppProvider

_EMAIL: dict[str, type[EmailProvider]] = {
    "smtp": SmtpEmailProvider,
    "sendgrid": SendGridEmailProvider,
    "ses": SesEmailProvider,
}

_SMS: dict[str, type[SmsProvider]] = {
    "console": ConsoleSmsProvider,
    "africas_talking": AfricasTalkingSmsProvider,
    "twilio": TwilioSmsProvider,
}


def get_email_provider(provider_class: str = "smtp") -> EmailProvider:
    cls = _EMAIL.get(provider_class, SmtpEmailProvider)
    return cls()


def get_sms_provider(provider_class: str = "console") -> SmsProvider:
    cls = _SMS.get(provider_class, ConsoleSmsProvider)
    return cls()


_WHATSAPP: dict[str, type] = {
    "console": ConsoleWhatsAppProvider,
    "twilio": TwilioWhatsAppProvider,
}


def get_whatsapp_provider(provider_class: str = "console"):
    cls = _WHATSAPP.get(provider_class, ConsoleWhatsAppProvider)
    return cls()
