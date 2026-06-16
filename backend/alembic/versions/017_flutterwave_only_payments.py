"""Restrict customer checkout to Flutterwave gateway only.

Revision ID: 017_flutterwave_only_payments
Revises: 016_beneficiary_auto_active
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "017_flutterwave_only"
down_revision: Union[str, None] = "016_beneficiary_auto_active"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sa.text("UPDATE payment_methods SET is_active = false WHERE code != 'flutterwave'"))
    op.execute(sa.text("UPDATE payment_methods SET is_active = true WHERE code = 'flutterwave'"))


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE payment_methods SET is_active = true
            WHERE code IN ('pay_at', 'easy_pay', 'eft', 'flutterwave', 'card')
            """
        )
    )
