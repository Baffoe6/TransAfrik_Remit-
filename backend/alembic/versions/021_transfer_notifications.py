"""In-app notifications and per-channel delivery tracking.

Revision ID: 021_transfer_notifications
Revises: 020_transfer_cancellation
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "021_transfer_notifications"
down_revision: Union[str, None] = "020_transfer_cancellation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("transfer_id", sa.Integer(), nullable=True),
        sa.Column("notification_type", sa.String(length=30), server_default="transfer_status", nullable=False),
        sa.Column("event_code", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("transfer_reference", sa.String(length=20), nullable=True),
        sa.Column("read_status", sa.String(length=10), server_default="unread", nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_id"), "notifications", ["id"], unique=False)
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)
    op.create_index(op.f("ix_notifications_transfer_id"), "notifications", ["transfer_id"], unique=False)
    op.create_index(op.f("ix_notifications_read_status"), "notifications", ["read_status"], unique=False)
    op.create_index(op.f("ix_notifications_created_at"), "notifications", ["created_at"], unique=False)

    op.create_table(
        "notification_deliveries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("notification_id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("recipient", sa.String(length=255), nullable=True),
        sa.Column("provider_response", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["notification_id"], ["notifications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notification_deliveries_id"), "notification_deliveries", ["id"], unique=False)
    op.create_index(op.f("ix_notification_deliveries_notification_id"), "notification_deliveries", ["notification_id"], unique=False)
    op.create_index(op.f("ix_notification_deliveries_channel"), "notification_deliveries", ["channel"], unique=False)
    op.create_index(op.f("ix_notification_deliveries_status"), "notification_deliveries", ["status"], unique=False)

    op.add_column("users", sa.Column("push_token", sa.String(length=512), nullable=True))
    op.add_column(
        "users",
        sa.Column("push_notifications_enabled", sa.Boolean(), server_default="true", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("users", "push_notifications_enabled")
    op.drop_column("users", "push_token")
    op.drop_table("notification_deliveries")
    op.drop_table("notifications")
