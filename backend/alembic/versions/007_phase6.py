"""Phase 6: pilot launch readiness

Revision ID: 007
Revises: 006
Create Date: 2026-06-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pilot_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pilot_mode_enabled", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("invite_only_registration", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("require_admin_approval", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("default_max_transfer_zar", sa.Numeric(precision=14, scale=2), server_default="5000", nullable=False),
        sa.Column("default_daily_transfer_limit", sa.Integer(), server_default="3", nullable=False),
        sa.Column("default_monthly_volume_zar", sa.Numeric(precision=14, scale=2), server_default="15000", nullable=False),
        sa.Column("default_allowed_corridors", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("demo_mode_enabled", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "pilot_invites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("invite_code", sa.String(length=32), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("max_uses", sa.Integer(), server_default="1", nullable=False),
        sa.Column("uses_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invite_code"),
    )
    op.create_index(op.f("ix_pilot_invites_id"), "pilot_invites", ["id"])
    op.create_index(op.f("ix_pilot_invites_invite_code"), "pilot_invites", ["invite_code"])

    op.create_table(
        "pilot_customers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("invite_code_used", sa.String(length=32), nullable=True),
        sa.Column("max_transfer_zar", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("daily_transfer_limit", sa.Integer(), nullable=True),
        sa.Column("monthly_volume_zar", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("allowed_corridors", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("approved_by", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_pilot_customers_user_id"), "pilot_customers", ["user_id"])

    op.add_column("support_tickets", sa.Column("priority", sa.String(length=20), server_default="normal", nullable=False))
    op.add_column("support_tickets", sa.Column("transfer_id", sa.Integer(), nullable=True))
    op.add_column("support_tickets", sa.Column("sla_due_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("support_tickets", sa.Column("escalated", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("support_tickets", sa.Column("whatsapp_handoff", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("support_tickets", sa.Column("sla_hours", sa.Integer(), server_default="24", nullable=False))
    op.create_foreign_key("fk_support_tickets_transfer_id", "support_tickets", "transfers", ["transfer_id"], ["id"], ondelete="SET NULL")

    op.create_table(
        "support_ticket_notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=True),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("is_internal", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["ticket_id"], ["support_tickets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_support_ticket_notes_ticket_id"), "support_ticket_notes", ["ticket_id"])


def downgrade() -> None:
    op.drop_table("support_ticket_notes")
    op.drop_constraint("fk_support_tickets_transfer_id", "support_tickets", type_="foreignkey")
    op.drop_column("support_tickets", "sla_hours")
    op.drop_column("support_tickets", "whatsapp_handoff")
    op.drop_column("support_tickets", "escalated")
    op.drop_column("support_tickets", "sla_due_at")
    op.drop_column("support_tickets", "transfer_id")
    op.drop_column("support_tickets", "priority")
    op.drop_table("pilot_customers")
    op.drop_table("pilot_invites")
    op.drop_table("pilot_settings")
