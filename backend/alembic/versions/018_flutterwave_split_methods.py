"""Seed split Flutterwave checkout payment methods.

Revision ID: 018_flutterwave_split_methods
Revises: 017_flutterwave_only
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "018_flutterwave_split"
down_revision: Union[str, None] = "017_flutterwave_only"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

METHODS = [
    ("fw_card", "Card payment", "Debit or credit card via Flutterwave"),
    ("fw_eft", "Bank transfer (EFT)", "Pay by EFT from your South African bank account"),
    ("fw_capitec", "Capitec Pay", "Pay instantly with Capitec Pay"),
    ("fw_1voucher", "1Voucher", "Pay with a 1Voucher PIN"),
    ("fw_ussd", "USSD", "Pay via mobile USSD banking"),
    ("fw_account", "Bank account", "Pay directly from your linked bank account"),
]


def upgrade() -> None:
    op.execute(sa.text("UPDATE payment_methods SET is_active = false WHERE code = 'flutterwave'"))
    for code, name, description in METHODS:
        op.execute(
            sa.text(
                """
                INSERT INTO payment_methods (name, code, provider, provider_class, description, requires_proof_upload, is_instant, is_active)
                SELECT :name, :code, 'flutterwave', 'flutterwave', :description, false, true, true
                WHERE NOT EXISTS (SELECT 1 FROM payment_methods WHERE code = :code)
                """
            ).bindparams(name=name, code=code, description=description)
        )
        op.execute(
            sa.text("UPDATE payment_methods SET is_active = true, name = :name, description = :description WHERE code = :code").bindparams(
                name=name, code=code, description=description
            )
        )


def downgrade() -> None:
    for code, _, _ in METHODS:
        op.execute(sa.text("UPDATE payment_methods SET is_active = false WHERE code = :code").bindparams(code=code))
    op.execute(sa.text("UPDATE payment_methods SET is_active = true WHERE code = 'flutterwave'"))
