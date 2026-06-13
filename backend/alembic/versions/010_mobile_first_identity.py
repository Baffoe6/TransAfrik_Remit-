"""Mobile-first customer identity: mobile_number primary, email optional

Revision ID: 010
Revises: 009
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("users", "phone", new_column_name="mobile_number", existing_type=sa.String(20))
    op.alter_column("users", "mobile_number", type_=sa.String(30), existing_nullable=True)
    op.alter_column("users", "email", existing_type=sa.String(255), nullable=True)

    op.add_column("users", sa.Column("first_name", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(100), nullable=True))
    op.add_column(
        "users",
        sa.Column("status", sa.String(20), server_default="active", nullable=False),
    )

    op.execute(
        """
        UPDATE users u
        SET first_name = cp.first_name, last_name = cp.last_name
        FROM customer_profiles cp
        WHERE cp.user_id = u.id AND u.first_name IS NULL
        """
    )
    op.execute("UPDATE users SET status = 'inactive' WHERE is_active = false")
    op.execute("UPDATE users SET status = 'active' WHERE is_active = true AND status IS NULL")

    op.execute("UPDATE waitlist_leads SET mobile = '+27000000000' WHERE mobile IS NULL OR mobile = ''")
    op.alter_column("waitlist_leads", "email", existing_type=sa.String(255), nullable=True)
    op.alter_column("waitlist_leads", "mobile", existing_type=sa.String(30), nullable=False)


def downgrade() -> None:
    op.alter_column("waitlist_leads", "mobile", existing_type=sa.String(30), nullable=True)
    op.alter_column("waitlist_leads", "email", existing_type=sa.String(255), nullable=False)

    op.drop_column("users", "status")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
    op.alter_column("users", "email", existing_type=sa.String(255), nullable=False)
    op.alter_column("users", "mobile_number", type_=sa.String(20), existing_nullable=True)
    op.alter_column("users", "mobile_number", new_column_name="phone", existing_type=sa.String(20))
