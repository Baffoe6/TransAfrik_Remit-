"""Seed corridor-specific FX rates and enable Flutterwave payment methods.

Revision ID: 015_corridor_fx
Revises: 014_open_registration
"""

from datetime import date
from decimal import Decimal
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "015_corridor_fx"
down_revision: Union[str, None] = "014_open_registration"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

RATE_PAIRS = [
    ("ZAR", "GHS", "0.72"),
    ("ZAR", "KES", "7.15"),
    ("ZAR", "NGN", "42.50"),
    ("ZAR", "UGX", "195.00"),
    ("ZAR", "ZMW", "1.35"),
    ("ZAR", "USD", "0.054"),
    ("ZAR", "ZWL", "18.50"),
    ("GBP", "GHS", "15.80"),
    ("USD", "GHS", "12.50"),
    ("EUR", "GHS", "13.60"),
]

MARKUP_PAIRS = [
    ("ZAR", "GHS", "2.0"),
    ("ZAR", "KES", "2.0"),
    ("ZAR", "NGN", "2.5"),
    ("ZAR", "UGX", "2.0"),
    ("ZAR", "ZMW", "2.0"),
    ("ZAR", "USD", "1.5"),
    ("ZAR", "ZWL", "2.0"),
    ("GBP", "GHS", "1.5"),
    ("USD", "GHS", "1.5"),
    ("EUR", "GHS", "1.5"),
]


def upgrade() -> None:
    today = date.today().isoformat()
    for src, dst, rate in RATE_PAIRS:
        op.execute(
            sa.text(
                """
                INSERT INTO exchange_rates (from_currency, to_currency, rate, effective_from, is_active, created_at, updated_at)
                SELECT :src, :dst, :rate, :today, true, NOW(), NOW()
                WHERE NOT EXISTS (
                    SELECT 1 FROM exchange_rates
                    WHERE from_currency = :src AND to_currency = :dst AND is_active = true
                )
                """
            ).bindparams(src=src, dst=dst, rate=Decimal(rate), today=today)
        )

    for src, dst, pct in MARKUP_PAIRS:
        op.execute(
            sa.text(
                """
                INSERT INTO fx_markup_rules (from_currency, to_currency, markup_type, markup_value, priority, is_active, created_at, updated_at)
                SELECT :src, :dst, 'percentage', :pct, 0, true, NOW(), NOW()
                WHERE NOT EXISTS (
                    SELECT 1 FROM fx_markup_rules
                    WHERE from_currency = :src AND to_currency = :dst AND is_active = true
                )
                """
            ).bindparams(src=src, dst=dst, pct=Decimal(pct))
        )

    op.execute(
        sa.text(
            """
            INSERT INTO payment_methods (name, code, provider, provider_class, description, requires_proof_upload, is_instant, is_active, created_at, updated_at)
            SELECT 'Flutterwave Checkout', 'flutterwave', 'flutterwave', 'flutterwave',
                   'Card, bank transfer, Capitec Pay, 1Voucher via Flutterwave', false, true, true, NOW(), NOW()
            WHERE NOT EXISTS (SELECT 1 FROM payment_methods WHERE code = 'flutterwave')
            """
        )
    )
    op.execute(
        sa.text(
            """
            INSERT INTO payment_methods (name, code, provider, provider_class, description, requires_proof_upload, is_instant, is_active, created_at, updated_at)
            SELECT 'Card Payment', 'card', 'flutterwave', 'card',
                   'Debit/credit card via Flutterwave', false, true, true, NOW(), NOW()
            WHERE NOT EXISTS (SELECT 1 FROM payment_methods WHERE code = 'card')
            """
        )
    )
    op.execute(sa.text("UPDATE payment_methods SET is_active = true WHERE code IN ('flutterwave', 'card')"))


def downgrade() -> None:
    op.execute(sa.text("UPDATE payment_methods SET is_active = false WHERE code IN ('flutterwave', 'card')"))
