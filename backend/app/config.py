from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils.database_url import normalize_database_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    database_url: str = "postgresql://transafrik:transafrik_secret@localhost:5432/transafrik"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    cors_origins: str = "http://localhost:3000"
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 10
    allowed_upload_extensions: str = ".pdf,.jpg,.jpeg,.png,.webp"
    seed_admin_email: str = "admin@ipaygo.co.za"
    seed_admin_password: str = "Admin@TransAfrik2024!"
    seed_compliance_email: str = "compliance@ipaygo.co.za"
    seed_compliance_password: str = "Compliance@TransAfrik2024!"
    seed_customer_email: str = "customer@demo.co.za"
    seed_customer_password: str = "Customer@TransAfrik2024!"
    seed_agent_email: str = "agent@transafrik.co.za"
    seed_agent_password: str = "Agent@TransAfrik2024!"
    seed_founder_email: str = "founder@ipaygo.co.za"
    seed_founder_password: str = "Founder@TransAfrik2024!"
    enable_dev_endpoints: bool = True
    docs_enabled: bool = True
    whatsapp_bot_provider: str = "twilio"
    fx_sync_interval_hours: int = 1
    api_signing_secret: str = ""
    partner_api_rate_limit: str = "120/minute"
    require_https: bool = False
    secure_cookies: bool = False
    pilot_mode_enabled: bool = False
    redis_url: str = ""
    storage_backend: str = "local"
    s3_bucket: str = ""
    s3_region: str = "af-south-1"
    s3_endpoint_url: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    email_provider: str = "smtp"
    sms_provider: str = "console"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_use_tls: bool = True
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@transafrik.co.za"
    sendgrid_api_key: str = ""
    ses_region: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_sms_from: str = ""
    twilio_whatsapp_from: str = ""
    africas_talking_api_key: str = ""
    africas_talking_username: str = ""
    africas_talking_sender_id: str = "TransAfrik"
    webhook_replay_protection: bool = True
    webhook_idempotency_enabled: bool = True
    webhook_queue_enabled: bool = True
    rate_limit_redis_enabled: bool = True

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        return normalize_database_url(value)

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def allowed_extensions(self) -> set[str]:
        return {ext.strip().lower() for ext in self.allowed_upload_extensions.split(",") if ext.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
