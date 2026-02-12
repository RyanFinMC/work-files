"""create seed_accounts table

Revision ID: 0001_create_seed_accounts
Revises:
Create Date: 2026-02-12 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_create_seed_accounts"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
    op.create_table(
        "seed_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("esp_name", sa.String(length=100), nullable=False),
        sa.Column("auth_method", sa.Enum("oauth2", "imap_secret", name="auth_method"), nullable=False),
        sa.Column("credential_ref", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "paused", "auth_expired", "error", name="seed_status"),
            nullable=False,
            server_default="active",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_seed_accounts_email"),
    )
    op.create_index("ix_seed_accounts_email", "seed_accounts", ["email"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_seed_accounts_email", table_name="seed_accounts")
    op.drop_table("seed_accounts")
    op.execute("DROP TYPE IF EXISTS seed_status")
    op.execute("DROP TYPE IF EXISTS auth_method")
