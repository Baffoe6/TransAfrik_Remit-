"""OTP auth and trusted devices

Revision ID: 011
Revises: 010
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "trusted_devices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("device_fingerprint_hash", sa.String(64), nullable=False),
        sa.Column("device_label", sa.String(100), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("risk_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_trusted", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("login_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("trusted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trusted_devices_user_id", "trusted_devices", ["user_id"])
    op.create_index("ix_trusted_devices_fingerprint", "trusted_devices", ["device_fingerprint_hash"])


def downgrade() -> None:
    op.drop_index("ix_trusted_devices_fingerprint", table_name="trusted_devices")
    op.drop_index("ix_trusted_devices_user_id", table_name="trusted_devices")
    op.drop_table("trusted_devices")
