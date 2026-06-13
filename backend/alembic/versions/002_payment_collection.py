"""Payment collection module and transfer status update

Revision ID: 002
Revises: 001
Create Date: 2026-06-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

STATUS_MAP = {
    "pending_kyc": "draft",
    "pending_payment": "awaiting_payment",
    "under_review": "payment_pending_verification",
    "submitted_to_provider": "submitted_to_mukuru",
    "rejected": "failed",
    "refunded": "refunded",
    "completed": "completed",
}


def upgrade() -> None:
    op.create_table(
        "payment_methods",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("provider_class", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("requires_proof_upload", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_instant", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_payment_methods_id"), "payment_methods", ["id"], unique=False)

    op.add_column("beneficiaries", sa.Column("account_name", sa.String(length=200), nullable=True))

    op.add_column("transfers", sa.Column("payment_method_id", sa.Integer(), nullable=True))
    op.add_column("transfers", sa.Column("risk_score", sa.Integer(), server_default="0", nullable=False))
    op.add_column("transfers", sa.Column("compliance_approved", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("transfers", sa.Column("compliance_approved_by", sa.Integer(), nullable=True))
    op.add_column("transfers", sa.Column("compliance_approved_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key("fk_transfers_payment_method", "transfers", "payment_methods", ["payment_method_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_transfers_compliance_approved_by", "transfers", "users", ["compliance_approved_by"], ["id"], ondelete="SET NULL")

    for old, new in STATUS_MAP.items():
        op.execute(sa.text(f"UPDATE transfers SET status = '{new}' WHERE status = '{old}'"))
        op.execute(sa.text(f"UPDATE transfer_status_history SET from_status = '{new}' WHERE from_status = '{old}'"))
        op.execute(sa.text(f"UPDATE transfer_status_history SET to_status = '{new}' WHERE to_status = '{old}'"))

    op.create_table(
        "payment_references",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transfer_id", sa.Integer(), nullable=False),
        sa.Column("payment_method_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("reference_number", sa.String(length=50), nullable=False),
        sa.Column("voucher_number", sa.String(length=50), nullable=True),
        sa.Column("barcode_data", sa.String(length=500), nullable=True),
        sa.Column("qr_data", sa.String(length=1000), nullable=True),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("banking_instructions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("provider_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["payment_method_id"], ["payment_methods.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_number"),
    )
    op.create_index(op.f("ix_payment_references_id"), "payment_references", ["id"], unique=False)
    op.create_index(op.f("ix_payment_references_transfer_id"), "payment_references", ["transfer_id"], unique=False)
    op.create_index(op.f("ix_payment_references_status"), "payment_references", ["status"], unique=False)

    op.create_table(
        "payment_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transfer_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("event_timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("provider_reference", sa.String(length=100), nullable=True),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payment_events_id"), "payment_events", ["id"], unique=False)
    op.create_index(op.f("ix_payment_events_transfer_id"), "payment_events", ["transfer_id"], unique=False)
    op.create_index(op.f("ix_payment_events_event_type"), "payment_events", ["event_type"], unique=False)

    op.create_table(
        "payment_verifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transfer_id", sa.Integer(), nullable=False),
        sa.Column("verified_by", sa.Integer(), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["verified_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payment_verifications_id"), "payment_verifications", ["id"], unique=False)
    op.create_index(op.f("ix_payment_verifications_transfer_id"), "payment_verifications", ["transfer_id"], unique=False)


def downgrade() -> None:
    op.drop_table("payment_verifications")
    op.drop_table("payment_events")
    op.drop_table("payment_references")
    op.drop_constraint("fk_transfers_compliance_approved_by", "transfers", type_="foreignkey")
    op.drop_constraint("fk_transfers_payment_method", "transfers", type_="foreignkey")
    op.drop_column("transfers", "compliance_approved_at")
    op.drop_column("transfers", "compliance_approved_by")
    op.drop_column("transfers", "compliance_approved")
    op.drop_column("transfers", "risk_score")
    op.drop_column("transfers", "payment_method_id")
    op.drop_column("beneficiaries", "account_name")
    op.drop_table("payment_methods")
