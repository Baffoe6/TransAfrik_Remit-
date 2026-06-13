"""SMTP email provider — logs in development, ready for SendGrid/SES integration."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx

from app.config import get_settings
from app.notifications.base import EmailProvider, SendResult

logger = logging.getLogger(__name__)


class SmtpEmailProvider(EmailProvider):
    @property
    def provider_code(self) -> str:
        return "smtp"

    def send_email(self, to: str, subject: str, body: str, *, html: bool = False) -> SendResult:
        settings = get_settings()
        if not settings.smtp_host:
            logger.info("EMAIL [stub] to=%s subject=%s", to, subject)
            return SendResult(
                success=True,
                provider_id=f"stub-email-{to[:8]}",
                message="Email logged (SMTP not configured)",
                raw_response={"mode": "stub", "to": to},
            )
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.smtp_from_email
            msg["To"] = to
            part = MIMEText(body, "html" if html else "plain")
            msg.attach(part)
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                if settings.smtp_use_tls:
                    server.starttls()
                if settings.smtp_username and settings.smtp_password:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.sendmail(settings.smtp_from_email, [to], msg.as_string())
            return SendResult(success=True, provider_id=f"smtp-{to[:8]}", message="Email sent via SMTP")
        except Exception as exc:
            logger.exception("SMTP send failed")
            return SendResult(success=False, message=str(exc))


class SendGridEmailProvider(EmailProvider):
    @property
    def provider_code(self) -> str:
        return "sendgrid"

    def send_email(self, to: str, subject: str, body: str, *, html: bool = False) -> SendResult:
        settings = get_settings()
        if not settings.sendgrid_api_key:
            return SmtpEmailProvider().send_email(to, subject, body, html=html)
        try:
            payload = {
                "personalizations": [{"to": [{"email": to}]}],
                "from": {"email": settings.smtp_from_email or "noreply@transafrik.co.za"},
                "subject": subject,
                "content": [{"type": "text/html" if html else "text/plain", "value": body}],
            }
            resp = httpx.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={"Authorization": f"Bearer {settings.sendgrid_api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=30,
            )
            if resp.status_code in (200, 202):
                return SendResult(success=True, provider_id=resp.headers.get("X-Message-Id"), message="Sent via SendGrid")
            return SendResult(success=False, message=f"SendGrid error {resp.status_code}", raw_response={"body": resp.text})
        except Exception as exc:
            return SendResult(success=False, message=str(exc))


class SesEmailProvider(EmailProvider):
    @property
    def provider_code(self) -> str:
        return "ses"

    def send_email(self, to: str, subject: str, body: str, *, html: bool = False) -> SendResult:
        settings = get_settings()
        if not settings.ses_region:
            return SmtpEmailProvider().send_email(to, subject, body, html=html)
        try:
            import boto3

            client = boto3.client(
                "ses",
                region_name=settings.ses_region,
                aws_access_key_id=settings.aws_access_key_id or None,
                aws_secret_access_key=settings.aws_secret_access_key or None,
            )
            resp = client.send_email(
                Source=settings.smtp_from_email or "noreply@transafrik.co.za",
                Destination={"ToAddresses": [to]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Html": {"Data": body}} if html else {"Text": {"Data": body}},
                },
            )
            return SendResult(success=True, provider_id=resp.get("MessageId"), message="Sent via AWS SES")
        except Exception as exc:
            return SendResult(success=False, message=str(exc))
