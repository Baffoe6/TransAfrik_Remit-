"""Phase 6.1: production integration infrastructure

Revision ID: 008
Revises: 007
Create Date: 2026-06-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("provider_secrets", sa.Column("credential_type", sa.String(50), server_default="api_key", nullable=False))
    op.add_column("provider_secrets", sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False))
    op.add_column("provider_secrets", sa.Column("last_validated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("provider_secrets", sa.Column("validation_status", sa.String(30), nullable=True))
    op.create_index(
        "ix_provider_secrets_provider_env_name",
        "provider_secrets",
        ["provider_code", "environment", "secret_name"],
        unique=True,
    )
    op.create_index(
        "ix_webhook_events_provider_external",
        "webhook_events",
        ["provider_code", "external_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_webhook_events_provider_external", table_name="webhook_events")
    op.drop_index("ix_provider_secrets_provider_env_name", table_name="provider_secrets")
    op.drop_column("provider_secrets", "validation_status")
    op.drop_column("provider_secrets", "last_validated_at")
    op.drop_column("provider_secrets", "is_active")
    op.drop_column("provider_secrets", "credential_type")
