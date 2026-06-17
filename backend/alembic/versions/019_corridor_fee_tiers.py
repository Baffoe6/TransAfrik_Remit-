"""Corridor fee tiers and transfer profitability columns.

Revision ID: 019_corridor_fee_tiers
Revises: 018_flutterwave_split
"""

from decimal import Decimal
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "019_corridor_fee_tiers"
down_revision: Union[str, None] = "018_flutterwave_split"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ZA_GH_TIERS: list[tuple[Decimal, Decimal | None, Decimal, str]] = [
    (Decimal("0"), Decimal("500"), Decimal("20"), "R0 – R500"),
    (Decimal("501"), Decimal("1000"), Decimal("30"), "R501 – R1,000"),
    (Decimal("1001"), Decimal("2500"), Decimal("45"), "R1,001 – R2,500"),
    (Decimal("2501"), Decimal("5000"), Decimal("70"), "R2,501 – R5,000"),
    (Decimal("5001"), Decimal("10000"), Decimal("100"), "R5,001 – R10,000"),
    (Decimal("10001"), Decimal("20000"), Decimal("150"), "R10,001 – R20,000"),
    (Decimal("20001"), Decimal("50000"), Decimal("250"), "R20,001 – R50,000"),
]


def upgrade() -> None:
    op.create_table(
        "corridor_fee_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("corridor_code", sa.String(length=20), nullable=False),
        sa.Column("source_country", sa.String(length=2), server_default="ZA", nullable=False),
        sa.Column("destination_country", sa.String(length=2), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("provider_cost_pct", sa.Numeric(precision=8, scale=4), server_default="1.5", nullable=False),
        sa.Column("provider_cost_flat_zar", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("priority", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_corridor_fee_rules_id"), "corridor_fee_rules", ["id"], unique=False)
    op.create_index(op.f("ix_corridor_fee_rules_corridor_code"), "corridor_fee_rules", ["corridor_code"], unique=False)
    op.create_index(op.f("ix_corridor_fee_rules_destination_country"), "corridor_fee_rules", ["destination_country"], unique=False)

    op.create_table(
        "corridor_fee_tiers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rule_id", sa.Integer(), nullable=False),
        sa.Column("min_amount_zar", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("max_amount_zar", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("fee_zar", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("label", sa.String(length=50), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["rule_id"], ["corridor_fee_rules.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_corridor_fee_tiers_id"), "corridor_fee_tiers", ["id"], unique=False)
    op.create_index(op.f("ix_corridor_fee_tiers_rule_id"), "corridor_fee_tiers", ["rule_id"], unique=False)

    op.add_column("transfers", sa.Column("provider_cost_zar", sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column("transfers", sa.Column("fx_margin_zar", sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column("transfers", sa.Column("net_revenue_zar", sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column("transfers", sa.Column("corridor_fee_tier_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_transfers_corridor_fee_tier",
        "transfers",
        "corridor_fee_tiers",
        ["corridor_fee_tier_id"],
        ["id"],
        ondelete="SET NULL",
    )

    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            """
            INSERT INTO corridor_fee_rules (corridor_code, source_country, destination_country, name, provider_cost_pct, is_active, priority)
            VALUES ('ZA-GH', 'ZA', 'GH', 'South Africa → Ghana', 1.5, true, 100)
            RETURNING id
            """
        )
    )
    rule_id = result.scalar_one()
    for idx, (min_amt, max_amt, fee, label) in enumerate(ZA_GH_TIERS):
        conn.execute(
            sa.text(
                """
                INSERT INTO corridor_fee_tiers (rule_id, min_amount_zar, max_amount_zar, fee_zar, label, sort_order, is_active)
                VALUES (:rule_id, :min_amt, :max_amt, :fee, :label, :sort_order, true)
                """
            ),
            {
                "rule_id": rule_id,
                "min_amt": min_amt,
                "max_amt": max_amt,
                "fee": fee,
                "label": label,
                "sort_order": idx,
            },
        )


def downgrade() -> None:
    op.drop_constraint("fk_transfers_corridor_fee_tier", "transfers", type_="foreignkey")
    op.drop_column("transfers", "corridor_fee_tier_id")
    op.drop_column("transfers", "net_revenue_zar")
    op.drop_column("transfers", "fx_margin_zar")
    op.drop_column("transfers", "provider_cost_zar")
    op.drop_table("corridor_fee_tiers")
    op.drop_table("corridor_fee_rules")
