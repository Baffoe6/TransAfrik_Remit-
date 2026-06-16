"""Open customer registration — disable pilot invite-only gates

Revision ID: 014_open_registration
Revises: 013_pin_authentication
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "014_open_registration"
down_revision: Union[str, None] = "013_pin_authentication"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE pilot_settings SET
                pilot_mode_enabled = false,
                invite_only_registration = false,
                require_admin_approval = false
            """
        )
    )
    op.alter_column(
        "pilot_settings",
        "invite_only_registration",
        server_default=sa.text("false"),
        existing_type=sa.Boolean(),
    )
    op.alter_column(
        "pilot_settings",
        "require_admin_approval",
        server_default=sa.text("false"),
        existing_type=sa.Boolean(),
    )


def downgrade() -> None:
    op.alter_column(
        "pilot_settings",
        "invite_only_registration",
        server_default=sa.text("true"),
        existing_type=sa.Boolean(),
    )
    op.alter_column(
        "pilot_settings",
        "require_admin_approval",
        server_default=sa.text("true"),
        existing_type=sa.Boolean(),
    )
