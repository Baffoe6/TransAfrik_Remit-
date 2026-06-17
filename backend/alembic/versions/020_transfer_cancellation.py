"""Transfer cancellation fields and unpaid expiry support.

Revision ID: 020_transfer_cancellation
Revises: 019_corridor_fee_tiers
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "020_transfer_cancellation"
down_revision: Union[str, None] = "019_corridor_fee_tiers"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("transfers", sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("transfers", sa.Column("cancellation_reason", sa.String(length=50), nullable=True))
    op.create_index(op.f("ix_transfers_cancellation_reason"), "transfers", ["cancellation_reason"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_transfers_cancellation_reason"), table_name="transfers")
    op.drop_column("transfers", "cancellation_reason")
    op.drop_column("transfers", "cancelled_at")
