"""Phase 3: Mukuru operations, settlements, operations audit

Revision ID: 004
Revises: 003
Create Date: 2026-06-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "mukuru_batches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), server_default="draft", nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=True),
        sa.Column("file_format", sa.String(length=10), server_default="csv", nullable=False),
        sa.Column("transfer_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_amount_zar", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("total_amount_ghs", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("approved_by", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reconciled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("export_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("batch_id"),
    )
    op.create_index(op.f("ix_mukuru_batches_id"), "mukuru_batches", ["id"], unique=False)
    op.create_index(op.f("ix_mukuru_batches_batch_id"), "mukuru_batches", ["batch_id"], unique=True)
    op.create_index(op.f("ix_mukuru_batches_status"), "mukuru_batches", ["status"], unique=False)
    op.create_index(op.f("ix_mukuru_batches_created_at"), "mukuru_batches", ["created_at"], unique=False)

    op.create_table(
        "mukuru_batch_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.Integer(), nullable=False),
        sa.Column("transfer_id", sa.Integer(), nullable=False),
        sa.Column("amount_zar", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("amount_ghs", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("provider_reference", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=30), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["mukuru_batches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mukuru_batch_items_id"), "mukuru_batch_items", ["id"], unique=False)
    op.create_index(op.f("ix_mukuru_batch_items_batch_id"), "mukuru_batch_items", ["batch_id"], unique=False)
    op.create_index(op.f("ix_mukuru_batch_items_transfer_id"), "mukuru_batch_items", ["transfer_id"], unique=False)

    op.create_table(
        "mukuru_settlements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.Integer(), nullable=True),
        sa.Column("settlement_reference", sa.String(length=100), nullable=False),
        sa.Column("settlement_date", sa.Date(), nullable=False),
        sa.Column("amount_zar", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("amount_ghs", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("transfer_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("status", sa.String(length=30), server_default="pending", nullable=False),
        sa.Column("variance_zar", sa.Numeric(precision=12, scale=2), server_default="0", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("recorded_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["mukuru_batches.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["recorded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("settlement_reference"),
    )
    op.create_index(op.f("ix_mukuru_settlements_id"), "mukuru_settlements", ["id"], unique=False)
    op.create_index(op.f("ix_mukuru_settlements_batch_id"), "mukuru_settlements", ["batch_id"], unique=False)
    op.create_index(op.f("ix_mukuru_settlements_settlement_reference"), "mukuru_settlements", ["settlement_reference"], unique=True)
    op.create_index(op.f("ix_mukuru_settlements_settlement_date"), "mukuru_settlements", ["settlement_date"], unique=False)
    op.create_index(op.f("ix_mukuru_settlements_status"), "mukuru_settlements", ["status"], unique=False)

    op.create_table(
        "payment_settlements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("settlement_date", sa.Date(), nullable=False),
        sa.Column("expected_amount_zar", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("collected_amount_zar", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("variance_zar", sa.Numeric(precision=12, scale=2), server_default="0", nullable=False),
        sa.Column("transaction_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("status", sa.String(length=30), server_default="pending", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("recorded_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["recorded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payment_settlements_id"), "payment_settlements", ["id"], unique=False)
    op.create_index(op.f("ix_payment_settlements_provider"), "payment_settlements", ["provider"], unique=False)
    op.create_index(op.f("ix_payment_settlements_settlement_date"), "payment_settlements", ["settlement_date"], unique=False)
    op.create_index(op.f("ix_payment_settlements_status"), "payment_settlements", ["status"], unique=False)

    op.create_table(
        "operations_audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_operations_audit_logs_id"), "operations_audit_logs", ["id"], unique=False)
    op.create_index(op.f("ix_operations_audit_logs_user_id"), "operations_audit_logs", ["user_id"], unique=False)
    op.create_index(op.f("ix_operations_audit_logs_category"), "operations_audit_logs", ["category"], unique=False)
    op.create_index(op.f("ix_operations_audit_logs_action"), "operations_audit_logs", ["action"], unique=False)
    op.create_index(op.f("ix_operations_audit_logs_created_at"), "operations_audit_logs", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_table("operations_audit_logs")
    op.drop_table("payment_settlements")
    op.drop_table("mukuru_settlements")
    op.drop_table("mukuru_batch_items")
    op.drop_table("mukuru_batches")
