"""Activate pending beneficiaries for customer sends.

Revision ID: 016_beneficiary_auto_active
Revises: 015_corridor_fx
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "016_beneficiary_auto_active"
down_revision: Union[str, None] = "015_corridor_fx"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE beneficiaries
            SET status = 'approved'
            WHERE status = 'pending' AND is_active = true
            """
        )
    )


def downgrade() -> None:
    pass
