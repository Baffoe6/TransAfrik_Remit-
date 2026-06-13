"""Phase 4: wallet, agents, FX engine, tracking, expanded beneficiaries

Revision ID: 005
Revises: 004
Create Date: 2026-06-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("beneficiaries", sa.Column("beneficiary_type", sa.String(length=30), server_default="mobile_money", nullable=False))
    op.add_column("beneficiaries", sa.Column("bank_name", sa.String(length=100), nullable=True))
    op.add_column("beneficiaries", sa.Column("bank_account_number", sa.String(length=50), nullable=True))
    op.add_column("beneficiaries", sa.Column("bank_branch", sa.String(length=100), nullable=True))
    op.add_column("beneficiaries", sa.Column("pickup_location", sa.String(length=200), nullable=True))
    op.add_column("beneficiaries", sa.Column("pickup_city", sa.String(length=100), nullable=True))
    op.alter_column("beneficiaries", "mobile_money_provider", existing_type=sa.String(length=100), nullable=True)
    op.alter_column("beneficiaries", "mobile_wallet_number", existing_type=sa.String(length=30), nullable=True)

    op.create_table(
        "agent_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("agent_code", sa.String(length=20), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("region", sa.String(length=100), nullable=True),
        sa.Column("commission_rate", sa.Numeric(precision=5, scale=2), server_default="1.50", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
        sa.UniqueConstraint("agent_code"),
    )
    op.create_index(op.f("ix_agent_profiles_id"), "agent_profiles", ["id"], unique=False)
    op.create_index(op.f("ix_agent_profiles_agent_code"), "agent_profiles", ["agent_code"], unique=True)

    op.create_table(
        "customer_wallet_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("total_sent_zar", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("total_fees_zar", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("transfer_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("completed_transfer_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("preferred_corridor", sa.String(length=10), server_default="ZAR-GHS", nullable=False),
        sa.Column("referral_code", sa.String(length=20), nullable=True),
        sa.Column("referred_by_agent_id", sa.Integer(), nullable=True),
        sa.Column("last_transfer_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["referred_by_agent_id"], ["agent_profiles.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
        sa.UniqueConstraint("referral_code"),
    )
    op.create_index(op.f("ix_customer_wallet_profiles_id"), "customer_wallet_profiles", ["id"], unique=False)

    op.create_table(
        "agent_referrals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("customer_user_id", sa.Integer(), nullable=True),
        sa.Column("transfer_id", sa.Integer(), nullable=True),
        sa.Column("referral_type", sa.String(length=20), nullable=False),
        sa.Column("referral_code_used", sa.String(length=20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agent_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["customer_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_referrals_id"), "agent_referrals", ["id"], unique=False)

    op.create_table(
        "agent_commissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("transfer_id", sa.Integer(), nullable=False),
        sa.Column("transfer_amount_zar", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("commission_rate", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("commission_amount_zar", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agent_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_commissions_id"), "agent_commissions", ["id"], unique=False)

    op.create_table(
        "fx_rate_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("source_type", sa.String(length=30), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("priority", sa.Integer(), server_default="0", nullable=False),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_fx_rate_sources_id"), "fx_rate_sources", ["id"], unique=False)

    op.create_table(
        "fx_markup_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("from_currency", sa.String(length=3), server_default="ZAR", nullable=False),
        sa.Column("to_currency", sa.String(length=3), server_default="GHS", nullable=False),
        sa.Column("markup_type", sa.String(length=20), server_default="percentage", nullable=False),
        sa.Column("markup_value", sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("priority", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_fx_markup_rules_id"), "fx_markup_rules", ["id"], unique=False)

    op.create_table(
        "transfer_tracking_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transfer_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("label", sa.String(length=150), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("event_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_transfer_tracking_events_id"), "transfer_tracking_events", ["id"], unique=False)
    op.create_index(op.f("ix_transfer_tracking_events_transfer_id"), "transfer_tracking_events", ["transfer_id"], unique=False)


def downgrade() -> None:
    op.drop_table("transfer_tracking_events")
    op.drop_table("fx_markup_rules")
    op.drop_table("fx_rate_sources")
    op.drop_table("agent_commissions")
    op.drop_table("agent_referrals")
    op.drop_table("customer_wallet_profiles")
    op.drop_table("agent_profiles")
    op.drop_column("beneficiaries", "pickup_city")
    op.drop_column("beneficiaries", "pickup_location")
    op.drop_column("beneficiaries", "bank_branch")
    op.drop_column("beneficiaries", "bank_account_number")
    op.drop_column("beneficiaries", "bank_name")
    op.drop_column("beneficiaries", "beneficiary_type")
