from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    database_url: str = "postgresql://transafrik:transafrik_secret@localhost:5432/transafrik"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    cors_origins: str = "http://localhost:3000"
    cors_origin_regex: str = ""
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 10
    allowed_upload_extensions: str = ".pdf,.jpg,.jpeg,.png,.webp"
    seed_admin_email: str = "admin@transafrik.co.za"
    seed_admin_password: str = "Admin@TransAfrik2024!"
    seed_compliance_email: str = "compliance@transafrik.co.za"
    seed_compliance_password: str = "Compliance@TransAfrik2024!"
    seed_operations_email: str = "operations@transafrik.co.za"
    seed_operations_password: str = "Operations@TransAfrik2024!"
    seed_customer_email: str = "customer@demo.co.za"
    seed_customer_password: str = "Customer@TransAfrik2024!"
    seed_agent_email: str = "agent@transafrik.co.za"
    seed_agent_password: str = "Agent@TransAfrik2024!"
    seed_founder_email: str = "founder@transafrik.co.za"
    seed_founder_password: str = "Founder@TransAfrik2024!"
    seed_demo_data: bool = True
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
    twilio_verify_service_sid: str = ""
    otp_provider: str = "console"  # console | twilio_verify
    africas_talking_api_key: str = ""
    africas_talking_username: str = ""
    africas_talking_sender_id: str = "TransAfrik"
    webhook_replay_protection: bool = True
    webhook_idempotency_enabled: bool = True
    webhook_queue_enabled: bool = True
    whatsapp_provider: str = "console"
    otp_dev_expose_code: bool = True
    rate_limit_redis_enabled: bool = True
    # Phase 12 — production security
    admin_mfa_required: bool = True
    account_lockout_max_attempts: int = 5
    account_lockout_minutes: int = 30
    password_max_age_days: int = 90
    admin_ip_allowlist_enabled: bool = False
    flutterwave_public_key: str = ""
    flutterwave_secret_key: str = ""
    flutterwave_encryption_key: str = ""
    flutterwave_webhook_secret: str = ""
    flutterwave_redirect_url: str = "https://app.ipaygo.co.za/payment/complete"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        if self.is_production or self.environment.lower() == "staging":
            for origin in (
                "https://trans-afrik-remit.vercel.app",
                "https://app.ipaygo.co.za",
                "https://api.ipaygo.co.za",
            ):
                if origin not in origins:
                    origins.append(origin)
        return origins

    @property
    def effective_cors_origin_regex(self) -> str | None:
        if self.cors_origin_regex:
            return self.cors_origin_regex
        if self.is_production or self.environment.lower() == "staging":
            return r"https://.*\.vercel\.app"
        return None

    @property
    def allowed_extensions(self) -> set[str]:
        return {ext.strip().lower() for ext in self.allowed_upload_extensions.split(",") if ext.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
