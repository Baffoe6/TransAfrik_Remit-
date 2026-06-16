"""PIN-based customer authentication (mobile-first)

Revision ID: 013_pin_authentication
Revises: 012_production_security
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "013_pin_authentication"
down_revision: Union[str, None] = "012_production_security"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("pin_hash", sa.String(255), nullable=True))
    op.alter_column("users", "password_hash", existing_type=sa.String(255), nullable=True)
    # Legacy password-only customers: keep password_hash; PIN set on next login/reset


def downgrade() -> None:
    op.execute("UPDATE users SET password_hash = '' WHERE password_hash IS NULL")
    op.alter_column("users", "password_hash", existing_type=sa.String(255), nullable=False)
    op.drop_column("users", "pin_hash")
