import enum


class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    COMPLIANCE_OFFICER = "compliance_officer"
    AGENT = "agent"
    FOUNDER = "founder"


class BeneficiaryType(str, enum.Enum):
    MOBILE_MONEY = "mobile_money"
    BANK_ACCOUNT = "bank_account"
    CASH_PICKUP = "cash_pickup"


class GhanaMobileProvider(str, enum.Enum):
    MTN_GHANA = "MTN Ghana"
    TELECEL_GHANA = "Telecel Ghana"
    AIRTELTIGO_GHANA = "AirtelTigo Ghana"


class FxRateSourceType(str, enum.Enum):
    MANUAL = "manual"
    API = "api"
    COMPOSITE = "composite"


class FxMarkupType(str, enum.Enum):
    PERCENTAGE = "percentage"
    FLAT = "flat"


class AgentCommissionStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"


class ReferralType(str, enum.Enum):
    CUSTOMER = "customer"
    TRANSFER = "transfer"


class KycStatus(str, enum.Enum):
    NOT_SUBMITTED = "not_submitted"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class KycDocumentType(str, enum.Enum):
    ID_PASSPORT = "id_passport"
    PROOF_OF_ADDRESS = "proof_of_address"
    SELFIE = "selfie"


class BeneficiaryStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class TransferStatus(str, enum.Enum):
    QUOTE_CREATED = "quote_created"
    DRAFT = "draft"
    AWAITING_PAYMENT = "awaiting_payment"
    PAYMENT_PENDING = "payment_pending"
    CHECKOUT_CREATED = "checkout_created"
    PAYMENT_PENDING_VERIFICATION = "payment_pending_verification"
    PAYMENT_VERIFIED = "payment_verified"
    COMPLIANCE_REVIEW = "compliance_review"
    READY_FOR_PROCESSING = "ready_for_processing"
    SUBMITTED_TO_MUKURU = "submitted_to_mukuru"
    PROCESSING = "processing"
    PAYOUT_PENDING = "payout_pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class CancellationReason(str, enum.Enum):
    CUSTOMER_CANCELLED = "customer_cancelled"
    EXPIRED_UNPAID_24H = "expired_unpaid_24h"
    ADMIN_CANCELLED = "admin_cancelled"
    LATE_PAYMENT_RECEIVED = "late_payment_received"


class PaymentReferenceStatus(str, enum.Enum):
    DRAFT = "draft"
    AWAITING_PAYMENT = "awaiting_payment"
    PAID = "paid"
    VERIFIED = "verified"
    SUBMITTED_TO_PROVIDER = "submitted_to_provider"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    LATE_PAYMENT_RECEIVED = "late_payment_received"
    REQUIRES_REVIEW = "requires_review"
    REJECTED = "rejected"


class PaymentProofStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class PaymentEventType(str, enum.Enum):
    REFERENCE_GENERATED = "reference_generated"
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_VERIFIED = "payment_verified"
    PAYMENT_REJECTED = "payment_rejected"
    PROOF_UPLOADED = "proof_uploaded"
    REFERENCE_EXPIRED = "reference_expired"
    WEBHOOK_RECEIVED = "webhook_received"


class SupportTicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AmlFlagType(str, enum.Enum):
    REPEATED_TRANSFERS = "repeated_transfers"
    HIGH_VALUE = "high_value"
    MULTIPLE_BENEFICIARIES = "multiple_beneficiaries"
    NAME_MISMATCH = "name_mismatch"
    SHARED_BENEFICIARY = "shared_beneficiary"
    SANCTIONS_HIT = "sanctions_hit"


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"


class NotificationDeliveryChannel(str, enum.Enum):
    IN_APP = "in_app"
    PUSH = "push"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    EMAIL = "email"


class InAppReadStatus(str, enum.Enum):
    UNREAD = "unread"
    READ = "read"


class NotificationDeliveryStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SKIPPED = "skipped"


class InAppNotificationType(str, enum.Enum):
    TRANSFER_STATUS = "transfer_status"


class MukuruBatchStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    RECONCILED = "reconciled"
    REJECTED = "rejected"
    FAILED = "failed"


class MukuruSettlementStatus(str, enum.Enum):
    PENDING = "pending"
    MATCHED = "matched"
    VARIANCE = "variance"
    RECONCILED = "reconciled"


class PaymentSettlementStatus(str, enum.Enum):
    PENDING = "pending"
    MATCHED = "matched"
    VARIANCE = "variance"
    RECONCILED = "reconciled"


class OperationsAuditCategory(str, enum.Enum):
    BATCH = "batch"
    SETTLEMENT = "settlement"
    TREASURY = "treasury"
    PROVIDER = "provider"
    WALLET = "wallet"
    AGENT = "agent"
    FX = "fx"
    TRACKING = "tracking"
    CORRIDOR = "corridor"
    REFERRAL = "referral"
    DOCUMENT = "document"
    WHATSAPP = "whatsapp"
    API_SECURITY = "api_security"
    OPERATIONS = "operations"
    PILOT = "pilot"
    LAUNCH = "launch"
    COMPLIANCE_PACK = "compliance_pack"


class CorridorStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class DocumentCategory(str, enum.Enum):
    FICA = "fica"
    KYC = "kyc"
    CIPC = "cipc_documents"
    TAX = "tax_documents"
    BANK_CONFIRMATION = "bank_confirmation"
    PARTNER_AGREEMENT = "partner_agreements"
    MUKURU = "mukuru_documents"
    FLUTTERWAVE = "flutterwave_documents"


class ReferralRewardType(str, enum.Enum):
    REFERRAL_SIGNUP = "referral_signup"
    REFERRAL_TRANSFER = "referral_transfer"
    VOUCHER_REDEMPTION = "voucher_redemption"
    MANUAL_ADJUSTMENT = "manual_adjustment"


class VoucherStatus(str, enum.Enum):
    ACTIVE = "active"
    REDEEMED = "redeemed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApiEnvironment(str, enum.Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ApiKeyStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class WhatsAppBotProvider(str, enum.Enum):
    TWILIO = "twilio"
    META_CLOUD = "meta_cloud"
    INFOBIP = "infobip"
    CONSOLE = "console"


class FxFeedProvider(str, enum.Enum):
    EXCHANGE_RATE_API = "exchange_rate_api"
    CURRENCY_LAYER = "currencylayer"
    OPEN_EXCHANGE_RATES = "openexchangerates"
    MANUAL = "manual"


class PilotCustomerStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class PilotInviteStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class SupportPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class CompliancePackType(str, enum.Enum):
    KYC_SUMMARY = "kyc_summary"
    TRANSFER_AUDIT = "transfer_audit"
    PAYMENT_PROOF = "payment_proof"
    AML_REVIEW = "aml_review"
    MUKURU_BATCH = "mukuru_batch"
    PARTNER_ONBOARDING = "partner_onboarding"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class EddStatus(str, enum.Enum):
    OPEN = "open"
    IN_REVIEW = "in_review"
    CLEARED = "cleared"
    ESCALATED = "escalated"
    REJECTED = "rejected"


class SanctionsResult(str, enum.Enum):
    CLEAR = "clear"
    POTENTIAL_MATCH = "potential_match"
    CONFIRMED_MATCH = "confirmed_match"
    ERROR = "error"


class WebhookStatus(str, enum.Enum):
    RECEIVED = "received"
    PROCESSED = "processed"
    FAILED = "failed"
    IGNORED = "ignored"


class SecurityEventType(str, enum.Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    MFA_ENABLED = "mfa_enabled"
    MFA_VERIFIED = "mfa_verified"
    MFA_FAILED = "mfa_failed"
    TOKEN_REFRESH = "token_refresh"
    TOKEN_REVOKED = "token_revoked"
    PASSWORD_CHANGED = "password_changed"
    RATE_LIMITED = "rate_limited"
    OTP_SENT = "otp_sent"
    OTP_VERIFIED = "otp_verified"
    OTP_FAILED = "otp_failed"
    STEP_UP_REQUIRED = "step_up_required"
    DEVICE_TRUSTED = "device_trusted"
    ACCOUNT_LOCKED = "account_locked"
    LOGIN_ANOMALY = "login_anomaly"
    IP_BLOCKED = "ip_blocked"
    PASSWORD_EXPIRED = "password_expired"
    SESSION_REVOKED = "session_revoked"
