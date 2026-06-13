"""Phase 2: notifications, exchange rate history, compliance, security, webhooks

Revision ID: 003
Revises: 002
Create Date: 2026-06-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "exchange_rates",
        sa.Column("effective_from", sa.Date(), server_default=sa.text("CURRENT_DATE"), nullable=False),
    )
    op.add_column("exchange_rates", sa.Column("effective_to", sa.Date(), nullable=True))

    op.add_column("fee_rules", sa.Column("destination_country", sa.String(length=2), nullable=True))
    op.add_column("fee_rules", sa.Column("payment_method_id", sa.Integer(), nullable=True))
    op.add_column("fee_rules", sa.Column("provider_id", sa.Integer(), nullable=True))
    op.add_column("fee_rules", sa.Column("priority", sa.Integer(), server_default="0", nullable=False))
    op.create_index(op.f("ix_fee_rules_destination_country"), "fee_rules", ["destination_country"], unique=False)
    op.create_foreign_key(
        "fk_fee_rules_payment_method", "fee_rules", "payment_methods", ["payment_method_id"], ["id"], ondelete="SET NULL"
    )
    op.create_foreign_key(
        "fk_fee_rules_provider", "fee_rules", "providers", ["provider_id"], ["id"], ondelete="SET NULL"
    )

    op.create_table(
        "exchange_rate_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("exchange_rate_id", sa.Integer(), nullable=False),
        sa.Column("from_currency", sa.String(length=3), nullable=False),
        sa.Column("to_currency", sa.String(length=3), nullable=False),
        sa.Column("rate", sa.Numeric(precision=12, scale=6), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("change_reason", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["exchange_rate_id"], ["exchange_rates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_exchange_rate_history_id"), "exchange_rate_history", ["id"], unique=False)
    op.create_index(op.f("ix_exchange_rate_history_exchange_rate_id"), "exchange_rate_history", ["exchange_rate_id"], unique=False)

    op.create_table(
        "notification_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("subject", sa.String(length=200), nullable=True),
        sa.Column("body_template", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", "channel", name="uq_notification_template_code_channel"),
    )
    op.create_index(op.f("ix_notification_templates_id"), "notification_templates", ["id"], unique=False)

    op.create_table(
        "notification_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("transfer_id", sa.Integer(), nullable=True),
        sa.Column("template_code", sa.String(length=50), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("recipient", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=200), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("provider_response", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notification_logs_id"), "notification_logs", ["id"], unique=False)
    op.create_index(op.f("ix_notification_logs_user_id"), "notification_logs", ["user_id"], unique=False)
    op.create_index(op.f("ix_notification_logs_transfer_id"), "notification_logs", ["transfer_id"], unique=False)
    op.create_index(op.f("ix_notification_logs_template_code"), "notification_logs", ["template_code"], unique=False)
    op.create_index(op.f("ix_notification_logs_created_at"), "notification_logs", ["created_at"], unique=False)

    op.create_table(
        "customer_risk_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("risk_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("risk_level", sa.String(length=20), server_default="low", nullable=False),
        sa.Column("aml_flag_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_transfer_volume_zar", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("transfer_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_reviewed_by", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["last_reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_customer_risk_profiles_id"), "customer_risk_profiles", ["id"], unique=False)
    op.create_index(op.f("ix_customer_risk_profiles_user_id"), "customer_risk_profiles", ["user_id"], unique=True)

    op.create_table(
        "sanctions_screenings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("transfer_id", sa.Integer(), nullable=True),
        sa.Column("screened_name", sa.String(length=200), nullable=False),
        sa.Column("result", sa.String(length=30), server_default="clear", nullable=False),
        sa.Column("match_details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("provider", sa.String(length=50), server_default="internal_placeholder", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sanctions_screenings_id"), "sanctions_screenings", ["id"], unique=False)
    op.create_index(op.f("ix_sanctions_screenings_user_id"), "sanctions_screenings", ["user_id"], unique=False)
    op.create_index(op.f("ix_sanctions_screenings_transfer_id"), "sanctions_screenings", ["transfer_id"], unique=False)
    op.create_index(op.f("ix_sanctions_screenings_created_at"), "sanctions_screenings", ["created_at"], unique=False)

    op.create_table(
        "enhanced_due_diligence_cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("transfer_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="open", nullable=False),
        sa.Column("risk_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("aml_flags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("assigned_to", sa.Integer(), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["assigned_to"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_enhanced_due_diligence_cases_id"), "enhanced_due_diligence_cases", ["id"], unique=False)
    op.create_index(op.f("ix_enhanced_due_diligence_cases_user_id"), "enhanced_due_diligence_cases", ["user_id"], unique=False)
    op.create_index(op.f("ix_enhanced_due_diligence_cases_transfer_id"), "enhanced_due_diligence_cases", ["transfer_id"], unique=False)
    op.create_index(op.f("ix_enhanced_due_diligence_cases_status"), "enhanced_due_diligence_cases", ["status"], unique=False)

    op.create_table(
        "user_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("refresh_token_hash", sa.String(length=64), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("is_revoked", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("refresh_token_hash"),
    )
    op.create_index(op.f("ix_user_sessions_id"), "user_sessions", ["id"], unique=False)
    op.create_index(op.f("ix_user_sessions_user_id"), "user_sessions", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_sessions_refresh_token_hash"), "user_sessions", ["refresh_token_hash"], unique=True)

    op.create_table(
        "user_mfa",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("totp_secret", sa.String(length=64), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("backup_codes_hash", sa.Text(), nullable=True),
        sa.Column("enabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_mfa_id"), "user_mfa", ["id"], unique=False)

    op.create_table(
        "security_audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_security_audit_logs_id"), "security_audit_logs", ["id"], unique=False)
    op.create_index(op.f("ix_security_audit_logs_user_id"), "security_audit_logs", ["user_id"], unique=False)
    op.create_index(op.f("ix_security_audit_logs_event_type"), "security_audit_logs", ["event_type"], unique=False)
    op.create_index(op.f("ix_security_audit_logs_created_at"), "security_audit_logs", ["created_at"], unique=False)

    op.create_table(
        "provider_configs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider_code", sa.String(length=50), nullable=False),
        sa.Column("provider_type", sa.String(length=30), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_sandbox", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("api_base_url", sa.String(length=500), nullable=True),
        sa.Column("webhook_secret", sa.String(length=255), nullable=True),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider_code"),
    )
    op.create_index(op.f("ix_provider_configs_id"), "provider_configs", ["id"], unique=False)
    op.create_index(op.f("ix_provider_configs_provider_code"), "provider_configs", ["provider_code"], unique=True)

    op.create_table(
        "webhook_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider_code", sa.String(length=50), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("external_id", sa.String(length=100), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="received", nullable=False),
        sa.Column("processing_notes", sa.Text(), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_webhook_events_id"), "webhook_events", ["id"], unique=False)
    op.create_index(op.f("ix_webhook_events_provider_code"), "webhook_events", ["provider_code"], unique=False)
    op.create_index(op.f("ix_webhook_events_event_type"), "webhook_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_webhook_events_external_id"), "webhook_events", ["external_id"], unique=False)
    op.create_index(op.f("ix_webhook_events_status"), "webhook_events", ["status"], unique=False)
    op.create_index(op.f("ix_webhook_events_received_at"), "webhook_events", ["received_at"], unique=False)


def downgrade() -> None:
    op.drop_table("webhook_events")
    op.drop_table("provider_configs")
    op.drop_table("security_audit_logs")
    op.drop_table("user_mfa")
    op.drop_table("user_sessions")
    op.drop_table("enhanced_due_diligence_cases")
    op.drop_table("sanctions_screenings")
    op.drop_table("customer_risk_profiles")
    op.drop_table("notification_logs")
    op.drop_table("notification_templates")
    op.drop_table("exchange_rate_history")
    op.drop_constraint("fk_fee_rules_provider", "fee_rules", type_="foreignkey")
    op.drop_constraint("fk_fee_rules_payment_method", "fee_rules", type_="foreignkey")
    op.drop_index(op.f("ix_fee_rules_destination_country"), table_name="fee_rules")
    op.drop_column("fee_rules", "priority")
    op.drop_column("fee_rules", "provider_id")
    op.drop_column("fee_rules", "payment_method_id")
    op.drop_column("fee_rules", "destination_country")
    op.drop_column("exchange_rates", "effective_to")
    op.drop_column("exchange_rates", "effective_from")
