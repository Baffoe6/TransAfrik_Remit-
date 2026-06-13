"""Phase 5: multi-corridor, orchestration, referrals, documents, tenant, API security

Revision ID: 006
Revises: 005
Create Date: 2026-06-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=50), nullable=False),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column("domain", sa.String(length=255), nullable=True),
        sa.Column("primary_color", sa.String(length=7), server_default="#1B5E3B", nullable=False),
        sa.Column("secondary_color", sa.String(length=7), server_default="#C9A227", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
        sa.UniqueConstraint("domain"),
    )
    op.create_index(op.f("ix_tenants_id"), "tenants", ["id"], unique=False)

    op.create_table(
        "corridors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("source_country", sa.String(length=2), server_default="ZA", nullable=False),
        sa.Column("destination_country", sa.String(length=2), nullable=False),
        sa.Column("destination_currency", sa.String(length=3), nullable=False),
        sa.Column("provider_code", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("fee_rule_id", sa.Integer(), nullable=True),
        sa.Column("fx_markup_rule_id", sa.Integer(), nullable=True),
        sa.Column("priority", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["fee_rule_id"], ["fee_rules.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["fx_markup_rule_id"], ["fx_markup_rules.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_corridors_id"), "corridors", ["id"], unique=False)

    op.create_table(
        "corridor_provider_routes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("corridor_id", sa.Integer(), nullable=False),
        sa.Column("provider_code", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.Integer(), server_default="0", nullable=False),
        sa.Column("cost_score", sa.Integer(), server_default="100", nullable=False),
        sa.Column("is_available", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["corridor_id"], ["corridors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_corridor_provider_routes_corridor_id"), "corridor_provider_routes", ["corridor_id"])

    op.create_table(
        "referral_programs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("points_per_referral", sa.Integer(), server_default="100", nullable=False),
        sa.Column("points_per_completed_transfer", sa.Integer(), server_default="50", nullable=False),
        sa.Column("voucher_threshold_points", sa.Integer(), server_default="500", nullable=False),
        sa.Column("voucher_discount_zar", sa.Numeric(precision=10, scale=2), server_default="25.00", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "customer_referrals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("program_id", sa.Integer(), nullable=False),
        sa.Column("referrer_user_id", sa.Integer(), nullable=False),
        sa.Column("referred_user_id", sa.Integer(), nullable=True),
        sa.Column("referral_code", sa.String(length=20), nullable=False),
        sa.Column("converted", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("converted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["program_id"], ["referral_programs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["referrer_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["referred_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_customer_referrals_referrer_user_id"), "customer_referrals", ["referrer_user_id"])
    op.create_index(op.f("ix_customer_referrals_referral_code"), "customer_referrals", ["referral_code"])

    op.create_table(
        "referral_rewards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("reward_type", sa.String(length=30), nullable=False),
        sa.Column("points", sa.Integer(), server_default="0", nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("referral_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["referral_id"], ["customer_referrals.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_referral_rewards_user_id"), "referral_rewards", ["user_id"])

    op.create_table(
        "discount_vouchers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("discount_zar", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("redeemed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_discount_vouchers_user_id"), "discount_vouchers", ["user_id"])

    op.create_table(
        "document_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("parent_document_id", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("uploaded_by", sa.Integer(), nullable=True),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["parent_document_id"], ["document_records.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_document_records_category"), "document_records", ["category"])

    op.create_table(
        "document_audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["document_records.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_document_audit_logs_document_id"), "document_audit_logs", ["document_id"])

    op.create_table(
        "api_keys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("key_prefix", sa.String(length=12), nullable=False),
        sa.Column("key_hash", sa.String(length=128), nullable=False),
        sa.Column("environment", sa.String(length=20), server_default="development", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("scopes", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_api_keys_key_prefix"), "api_keys", ["key_prefix"])

    op.create_table(
        "provider_secrets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider_code", sa.String(length=50), nullable=False),
        sa.Column("secret_name", sa.String(length=100), nullable=False),
        sa.Column("encrypted_value", sa.Text(), nullable=False),
        sa.Column("environment", sa.String(length=20), server_default="development", nullable=False),
        sa.Column("rotated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_provider_secrets_provider_code"), "provider_secrets", ["provider_code"])

    op.create_table(
        "security_monitor_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("source_ip", sa.String(length=45), nullable=True),
        sa.Column("path", sa.String(length=255), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_security_monitor_events_event_type"), "security_monitor_events", ["event_type"])

    op.create_table(
        "fx_rate_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_code", sa.String(length=50), nullable=False),
        sa.Column("from_currency", sa.String(length=3), nullable=False),
        sa.Column("to_currency", sa.String(length=3), nullable=False),
        sa.Column("base_rate", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("effective_rate", sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column("margin_applied", sa.String(length=50), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_fx_rate_snapshots_source_code"), "fx_rate_snapshots", ["source_code"])
    op.create_index(op.f("ix_fx_rate_snapshots_synced_at"), "fx_rate_snapshots", ["synced_at"])

    op.create_table(
        "fx_sync_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_code", sa.String(length=50), nullable=False),
        sa.Column("success", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("pairs_synced", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_fx_sync_runs_source_code"), "fx_sync_runs", ["source_code"])

    op.create_table(
        "whatsapp_conversation_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider_code", sa.String(length=50), nullable=False),
        sa.Column("phone_number", sa.String(length=30), nullable=False),
        sa.Column("direction", sa.String(length=10), server_default="inbound", nullable=False),
        sa.Column("menu_option", sa.String(length=50), nullable=True),
        sa.Column("message_body", sa.Text(), nullable=True),
        sa.Column("response_body", sa.Text(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("transfer_id", sa.Integer(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_whatsapp_conversation_logs_phone_number"), "whatsapp_conversation_logs", ["phone_number"])

    op.create_table(
        "provider_health_checks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider_code", sa.String(length=50), nullable=False),
        sa.Column("is_healthy", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("checked_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_provider_health_checks_provider_code"), "provider_health_checks", ["provider_code"])

    op.create_table(
        "operations_queue_status",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("queue_name", sa.String(length=100), nullable=False),
        sa.Column("pending_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("failed_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_operations_queue_status_queue_name"), "operations_queue_status", ["queue_name"])


def downgrade() -> None:
    op.drop_table("operations_queue_status")
    op.drop_table("provider_health_checks")
    op.drop_table("whatsapp_conversation_logs")
    op.drop_table("fx_sync_runs")
    op.drop_table("fx_rate_snapshots")
    op.drop_table("security_monitor_events")
    op.drop_table("provider_secrets")
    op.drop_table("api_keys")
    op.drop_table("document_audit_logs")
    op.drop_table("document_records")
    op.drop_table("discount_vouchers")
    op.drop_table("referral_rewards")
    op.drop_table("customer_referrals")
    op.drop_table("referral_programs")
    op.drop_table("corridor_provider_routes")
    op.drop_table("corridors")
    op.drop_table("tenants")
