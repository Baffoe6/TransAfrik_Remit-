"""Seed initial data: staff, demo customer, providers, payment methods, rates, fees."""

from datetime import date
from decimal import Decimal

from app.config import get_settings
from app.database import SessionLocal
from app.models.beneficiary import Beneficiary
from app.models.customer_profile import CustomerProfile
from app.models.agent import AgentProfile
from app.models.enums import BeneficiaryStatus, BeneficiaryType, FxMarkupType, FxRateSourceType, KycStatus, NotificationChannel, UserRole
from app.models.fx import FxMarkupRule, FxRateSource
from app.models.exchange_rate import ExchangeRate
from app.models.fee_rule import FeeRule
from app.models.notification import NotificationTemplate
from app.models.payment_method import PaymentMethod
from app.models.provider import Provider
from app.models.user import User
from app.models.webhook import ProviderConfig
from app.models.tenant import Tenant
from app.models.corridor import Corridor, CorridorProviderRoute
from app.models.referral_program import ReferralProgram
from app.models.enums import CorridorStatus, PilotCustomerStatus
from app.models.pilot import PilotCustomer, PilotInvite, PilotSettings
from app.notifications.templates import DEFAULT_TEMPLATES
from app.utils.security import hash_password, hash_pin

settings = get_settings()

PAYMENT_METHODS = [
    {
        "name": "Pay@ Voucher",
        "code": "pay_at",
        "provider": "pay_at",
        "provider_class": "pay_at",
        "description": "Pay cash at Shoprite, Checkers, Pick n Pay, Boxer, Usave and other Pay@ merchants",
        "requires_proof_upload": False,
        "is_instant": False,
    },
    {
        "name": "EasyPay Voucher",
        "code": "easy_pay",
        "provider": "easy_pay",
        "provider_class": "easy_pay",
        "description": "Pay cash at EasyPay partner outlets across South Africa",
        "requires_proof_upload": False,
        "is_instant": False,
    },
    {
        "name": "EFT Bank Transfer",
        "code": "eft",
        "provider": "eft",
        "provider_class": "eft",
        "description": "Pay via EFT or cash deposit — upload proof of payment",
        "requires_proof_upload": True,
        "is_instant": False,
    },
    {
        "name": "Instant EFT (Stitch)",
        "code": "stitch",
        "provider": "stitch",
        "provider_class": "stitch",
        "description": "Instant EFT via Stitch — coming soon",
        "requires_proof_upload": False,
        "is_instant": True,
    },
    {
        "name": "Instant EFT (Ozow)",
        "code": "ozow",
        "provider": "ozow",
        "provider_class": "ozow",
        "description": "Instant EFT via Ozow — coming soon",
        "requires_proof_upload": False,
        "is_instant": True,
    },
    {
        "name": "Card (Peach Payments)",
        "code": "peach_payments",
        "provider": "peach_payments",
        "provider_class": "peach_payments",
        "description": "Card payments via Peach Payments — coming soon",
        "requires_proof_upload": False,
        "is_instant": True,
    },
    {
        "name": "Card (PayFast)",
        "code": "payfast",
        "provider": "payfast",
        "provider_class": "payfast",
        "description": "Card payments via PayFast — coming soon",
        "requires_proof_upload": False,
        "is_instant": True,
    },
    {"name": "Kazang Voucher", "code": "kazang", "provider": "kazang", "provider_class": "kazang", "description": "Pay at Kazang agent network", "requires_proof_upload": False, "is_instant": False},
    {"name": "Flash Voucher", "code": "flash", "provider": "flash", "provider_class": "flash", "description": "Pay at Flash agent outlets", "requires_proof_upload": False, "is_instant": False},
    {"name": "Shoprite Voucher", "code": "shoprite", "provider": "shoprite", "provider_class": "shoprite", "description": "Pay at Shoprite / Checkers", "requires_proof_upload": False, "is_instant": False},
    {"name": "Pick n Pay Voucher", "code": "pick_n_pay", "provider": "pick_n_pay", "provider_class": "pick_n_pay", "description": "Pay at Pick n Pay / Boxer", "requires_proof_upload": False, "is_instant": False},
    {
        "name": "Flutterwave Checkout",
        "code": "flutterwave",
        "provider": "flutterwave",
        "provider_class": "flutterwave",
        "description": "Card, bank transfer, Capitec Pay, 1Voucher and more via Flutterwave",
        "requires_proof_upload": False,
        "is_instant": True,
    },
    {
        "name": "Card Payment",
        "code": "card",
        "provider": "flutterwave",
        "provider_class": "card",
        "description": "Debit/credit card via Flutterwave Checkout",
        "requires_proof_upload": False,
        "is_instant": True,
    },
]


def _ensure_user(db, email: str, password: str, role: UserRole) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            password_hash=hash_password(password),
            role=role,
            email_verified=True,
            phone_verified=True,
            is_active=True,
            status="active",
        )
        db.add(user)
        db.flush()
        print(f"Created user: {email} ({role.value})")
    return user


def seed():
    db = SessionLocal()
    try:
        _ensure_user(db, settings.seed_admin_email, settings.seed_admin_password, UserRole.ADMIN)
        _ensure_user(db, settings.seed_compliance_email, settings.seed_compliance_password, UserRole.COMPLIANCE_OFFICER)
        _ensure_user(db, settings.seed_founder_email, settings.seed_founder_password, UserRole.FOUNDER)
        _ensure_user(db, settings.seed_operations_email, settings.seed_operations_password, UserRole.ADMIN)

        seed_demo = settings.seed_demo_data and not settings.is_production

        if seed_demo:
            agent_user = _ensure_user(db, settings.seed_agent_email, settings.seed_agent_password, UserRole.AGENT)
            if not db.query(AgentProfile).filter(AgentProfile.user_id == agent_user.id).first():
                db.add(AgentProfile(user_id=agent_user.id, agent_code="AGDEMO01", display_name="Demo Agent", region="Gauteng", commission_rate=Decimal("1.50")))
                print(f"Created demo agent: {settings.seed_agent_email}")

            customer = _ensure_user(db, settings.seed_customer_email, settings.seed_customer_password, UserRole.CUSTOMER)
            customer.mobile_number = "+27821234567"
            customer.first_name = "Thabo"
            customer.last_name = "Molefe"
            customer.phone_verified = True
            customer.pin_hash = hash_pin("1234")

            profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == customer.id).first()
            if not profile:
                profile = CustomerProfile(
                    user_id=customer.id,
                    first_name="Thabo",
                    last_name="Molefe",
                    id_number="8001015800088",
                    address_line1="12 Main Road",
                    city="Johannesburg",
                    province="Gauteng",
                    postal_code="2001",
                    kyc_status=KycStatus.APPROVED,
                )
                db.add(profile)
                print(f"Created demo customer profile: {settings.seed_customer_email}")

            beneficiary = (
                db.query(Beneficiary)
                .filter(Beneficiary.user_id == customer.id, Beneficiary.mobile_wallet_number == "+233241234567")
                .first()
            )
            if not beneficiary:
                beneficiary = Beneficiary(
                    user_id=customer.id,
                    beneficiary_type=BeneficiaryType.MOBILE_MONEY,
                    full_name="Ama Osei",
                    account_name="Ama Osei",
                    country="GH",
                    mobile_money_provider="MTN Ghana",
                    mobile_wallet_number="+233241234567",
                    relationship_to_sender="Sister",
                    status=BeneficiaryStatus.APPROVED,
                )
                db.add(beneficiary)
                print("Created demo beneficiary: Ama Osei (MTN Ghana)")

        if not db.query(Provider).filter(Provider.code == "manual_mukuru").first():
            db.add(Provider(
                name="Mukuru Enterprise (Manual)",
                code="manual_mukuru",
                provider_class="manual_mukuru",
                is_active=True,
                is_manual=True,
                description="Manual batch processing via Mukuru Enterprise portal",
            ))

        for pm in PAYMENT_METHODS:
            if not db.query(PaymentMethod).filter(PaymentMethod.code == pm["code"]).first():
                inactive_codes = ("stitch", "ozow", "peach_payments")
                db.add(PaymentMethod(
                    **pm,
                    is_active=pm["code"] not in inactive_codes,
                ))
            else:
                existing_pm = db.query(PaymentMethod).filter(PaymentMethod.code == pm["code"]).first()
                if existing_pm and pm["code"] in ("flutterwave", "card"):
                    existing_pm.is_active = True
                    existing_pm.provider_class = pm["provider_class"]

        if not db.query(FxRateSource).filter(FxRateSource.code == "manual").first():
            db.add(FxRateSource(code="manual", name="Admin Manual Rates", source_type=FxRateSourceType.MANUAL, priority=10, is_active=True))

        if not db.query(FxMarkupRule).first():
            markup_pairs = [
                ("ZAR", "GHS", Decimal("2.0")),
                ("ZAR", "KES", Decimal("2.0")),
                ("ZAR", "NGN", Decimal("2.5")),
                ("ZAR", "UGX", Decimal("2.0")),
                ("ZAR", "ZMW", Decimal("2.0")),
                ("ZAR", "USD", Decimal("1.5")),
                ("ZAR", "ZWL", Decimal("2.0")),
                ("GBP", "GHS", Decimal("1.5")),
                ("USD", "GHS", Decimal("1.5")),
                ("EUR", "GHS", Decimal("1.5")),
            ]
            for src, dst, pct in markup_pairs:
                db.add(FxMarkupRule(
                    from_currency=src, to_currency=dst,
                    markup_type=FxMarkupType.PERCENTAGE, markup_value=pct,
                    priority=0, is_active=True,
                ))

        rate_pairs = [
            ("ZAR", "GHS", Decimal("0.72")),
            ("ZAR", "KES", Decimal("7.15")),
            ("ZAR", "NGN", Decimal("42.50")),
            ("ZAR", "UGX", Decimal("195.00")),
            ("ZAR", "ZMW", Decimal("1.35")),
            ("ZAR", "USD", Decimal("0.054")),
            ("ZAR", "ZWL", Decimal("18.50")),
            ("GBP", "GHS", Decimal("15.80")),
            ("USD", "GHS", Decimal("12.50")),
            ("EUR", "GHS", Decimal("13.60")),
        ]
        for src, dst, rate in rate_pairs:
            if not db.query(ExchangeRate).filter(
                ExchangeRate.from_currency == src,
                ExchangeRate.to_currency == dst,
                ExchangeRate.is_active.is_(True),
            ).first():
                db.add(ExchangeRate(
                    from_currency=src,
                    to_currency=dst,
                    rate=rate,
                    effective_from=date.today(),
                    is_active=True,
                ))

        if not db.query(FeeRule).first():
            db.add_all([
                FeeRule(name="Standard flat fee", min_amount_zar=Decimal("0"), max_amount_zar=Decimal("4999.99"), fee_type="flat", fee_value=Decimal("49.00"), is_active=True, priority=0),
                FeeRule(name="Mid-tier fee", min_amount_zar=Decimal("5000"), max_amount_zar=Decimal("9999.99"), fee_type="flat", fee_value=Decimal("79.00"), is_active=True, priority=0),
                FeeRule(name="High-value fee", min_amount_zar=Decimal("10000"), max_amount_zar=None, fee_type="percentage", fee_value=Decimal("1.5"), is_active=True, priority=0),
                FeeRule(name="Ghana premium", min_amount_zar=Decimal("0"), destination_country="GH", fee_type="flat", fee_value=Decimal("55.00"), is_active=True, priority=10),
            ])

        for tmpl in DEFAULT_TEMPLATES:
            exists = (
                db.query(NotificationTemplate)
                .filter(
                    NotificationTemplate.code == tmpl["code"],
                    NotificationTemplate.channel == NotificationChannel(tmpl["channel"]),
                )
                .first()
            )
            if not exists:
                db.add(NotificationTemplate(
                    code=tmpl["code"],
                    name=tmpl["name"],
                    channel=NotificationChannel(tmpl["channel"]),
                    subject=tmpl.get("subject"),
                    body_template=tmpl["body_template"],
                    is_active=True,
                ))

        provider_configs = [
            ("pay_at", "payment", "Pay@ Voucher", True),
            ("easy_pay", "payment", "EasyPay Voucher", True),
            ("eft", "payment", "EFT Bank Transfer", True),
            ("mukuru_api", "remittance", "Mukuru API", False),
            ("manual_mukuru", "remittance", "Mukuru Manual Batch", True),
            ("kazang", "payment", "Kazang", True),
            ("flash", "payment", "Flash", True),
            ("shoprite", "payment", "Shoprite", True),
            ("pick_n_pay", "payment", "Pick n Pay", True),
            ("flutterwave", "payment", "Flutterwave Checkout", True),
            ("mock_mukuru", "remittance", "Mock Mukuru", True),
            ("live_mukuru", "remittance", "Live Mukuru API", False),
            ("flutterwave", "remittance", "Flutterwave", False),
            ("veengu", "remittance", "Veengu", False),
            ("onafriq", "remittance", "Onafriq", False),
        ]
        if not db.query(Tenant).filter(Tenant.slug == "transafrik").first():
            db.add(Tenant(
                name="TransAfrik Remit",
                slug="transafrik",
                domain="transafrik.co.za",
                primary_color="#1B5E3B",
                secondary_color="#C9A227",
            ))
            print("Created default tenant: TransAfrik")

        corridor_seeds = [
            ("ZA-GH", "GH", "GHS", "mock_mukuru", 100),
            ("ZA-ZW", "ZW", "ZWL", "mukuru_api", 90),
            ("ZA-ZM", "ZM", "ZMW", "flutterwave", 80),
            ("ZA-KE", "KE", "KES", "onafriq", 70),
            ("ZA-NG", "NG", "NGN", "flutterwave", 60),
            ("ZA-UG", "UG", "UGX", "veengu", 50),
        ]
        for code, dest, currency, provider, priority in corridor_seeds:
            if not db.query(Corridor).filter(Corridor.code == code).first():
                c = Corridor(
                    code=code,
                    source_country="ZA",
                    destination_country=dest,
                    destination_currency=currency,
                    provider_code=provider,
                    status=CorridorStatus.ACTIVE,
                    priority=priority,
                )
                db.add(c)
                db.flush()
                db.add(CorridorProviderRoute(
                    corridor_id=c.id,
                    provider_code=provider,
                    priority=priority,
                    cost_score=100 - priority // 2,
                ))
        print("Seeded 6 corridors (ZA → GH/ZW/ZM/KE/NG/UG)")

        if not db.query(ReferralProgram).first():
            db.add(ReferralProgram(name="TransAfrik Customer Referrals"))
            print("Created customer referral program")

        fx_feed_sources = [
            ("exchange_rate_api", "ExchangeRate-API", {"feed_provider": "exchange_rate_api"}),
            ("currencylayer", "CurrencyLayer", {"feed_provider": "currencylayer"}),
            ("openexchangerates", "Open Exchange Rates", {"feed_provider": "openexchangerates"}),
        ]
        for code, name, config in fx_feed_sources:
            if not db.query(FxRateSource).filter(FxRateSource.code == code).first():
                db.add(FxRateSource(
                    code=code,
                    name=name,
                    source_type=FxRateSourceType.API,
                    priority=10,
                    config=config,
                    is_active=True,
                ))

        if not db.query(PilotSettings).first():
            db.add(PilotSettings(
                pilot_mode_enabled=False,
                invite_only_registration=False,
                require_admin_approval=False,
                default_allowed_corridors=["ZA-GH", "ZA-ZW", "ZA-ZM", "ZA-KE", "ZA-NG", "ZA-UG"],
                demo_mode_enabled=False,
            ))
            if seed_demo:
                db.add(PilotInvite(invite_code="PILOTDEMO2026", email=settings.seed_customer_email, max_uses=10))
                print("Created demo invite PILOTDEMO2026 (local demo only)")
            else:
                print("Created open registration pilot settings")

        for code, ptype, name, enabled in provider_configs:
            if not db.query(ProviderConfig).filter(ProviderConfig.provider_code == code).first():
                db.add(ProviderConfig(
                    provider_code=code,
                    provider_type=ptype,
                    display_name=name,
                    is_enabled=enabled,
                    is_sandbox=True,
                ))

        if seed_demo:
            demo_user = db.query(User).filter(User.email == settings.seed_customer_email).first()
            if demo_user and not db.query(PilotCustomer).filter(PilotCustomer.user_id == demo_user.id).first():
                db.add(PilotCustomer(
                    user_id=demo_user.id,
                    status=PilotCustomerStatus.APPROVED,
                    invite_code_used="PILOTDEMO2026",
                    allowed_corridors=["ZA-GH"],
                ))

        db.commit()
        print("Seed completed successfully")
        if seed_demo:
            print(f"  Demo customer: {settings.seed_customer_email} / PIN 1234 (legacy password: {settings.seed_customer_password})")
            print(f"  Demo agent: {settings.seed_agent_email} / {settings.seed_agent_password}")
        print(f"  Admin: {settings.seed_admin_email}")
        print(f"  Founder: {settings.seed_founder_email}")
        print(f"  Compliance: {settings.seed_compliance_email}")
        print(f"  Operations: {settings.seed_operations_email}")
    except Exception as e:
        db.rollback()
        print(f"Seed error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
