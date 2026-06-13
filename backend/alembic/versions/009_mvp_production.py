"""MVP production: waitlist, KYC notes

Revision ID: 009
Revises: 008
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "waitlist_leads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("mobile", sa.String(30), nullable=True),
        sa.Column("country_from", sa.String(2), server_default="ZA", nullable=False),
        sa.Column("country_to", sa.String(2), nullable=False),
        sa.Column("estimated_monthly_volume", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_waitlist_leads_email", "waitlist_leads", ["email"])
    op.create_index("ix_waitlist_leads_country_to", "waitlist_leads", ["country_to"])
    op.create_index("ix_waitlist_leads_created_at", "waitlist_leads", ["created_at"])

    op.add_column("customer_profiles", sa.Column("kyc_review_notes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("customer_profiles", "kyc_review_notes")
    op.drop_index("ix_waitlist_leads_created_at", table_name="waitlist_leads")
    op.drop_index("ix_waitlist_leads_country_to", table_name="waitlist_leads")
    op.drop_index("ix_waitlist_leads_email", table_name="waitlist_leads")
    op.drop_table("waitlist_leads")
