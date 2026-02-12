"""add campaigns, delivery_results, alert_events

Revision ID: 0002_campaigns_results_alerts
Revises: 0001_create_seed_accounts
Create Date: 2026-02-12 00:30:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0002_campaigns_results_alerts"
down_revision = "0001_create_seed_accounts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("subject_identifier", sa.String(length=255), nullable=False),
        sa.Column("header_identifier", sa.String(length=255), nullable=True),
        sa.Column("tracking_id", sa.String(length=255), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "delivery_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("seed_account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "placement",
            sa.Enum("inbox", "spam", "promotions", "missing", name="placement_enum"),
            nullable=False,
        ),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column(
            "source_provider",
            sa.Enum("imap", "gmail_api", "ms_graph", name="source_provider_enum"),
            nullable=False,
        ),
        sa.Column("folder_or_label", sa.String(length=255), nullable=True),
        sa.Column("spf_result", sa.String(length=32), nullable=True),
        sa.Column("dkim_result", sa.String(length=32), nullable=True),
        sa.Column("dmarc_result", sa.String(length=32), nullable=True),
        sa.Column("raw_headers", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["seed_account_id"], ["seed_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id", "seed_account_id", name="uq_delivery_results_campaign_seed"),
    )
    op.create_index("ix_delivery_results_campaign_id", "delivery_results", ["campaign_id"], unique=False)
    op.create_index("ix_delivery_results_seed_account_id", "delivery_results", ["seed_account_id"], unique=False)
    op.create_index(
        "ix_delivery_results_campaign_placement",
        "delivery_results",
        ["campaign_id", "placement"],
        unique=False,
    )
    op.create_index(
        "ix_delivery_results_seed_detected",
        "delivery_results",
        ["seed_account_id", "detected_at"],
        unique=False,
    )
    op.create_index("ix_delivery_results_detected", "delivery_results", ["detected_at"], unique=False)

    op.create_table(
        "alert_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("scope", sa.Enum("global", "esp", "campaign", name="alert_scope_enum"), nullable=False),
        sa.Column(
            "severity",
            sa.Enum("info", "warning", "critical", name="alert_severity_enum"),
            nullable=False,
        ),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("esp_name", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alert_events_campaign_id", "alert_events", ["campaign_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_alert_events_campaign_id", table_name="alert_events")
    op.drop_table("alert_events")
    op.execute("DROP TYPE IF EXISTS alert_severity_enum")
    op.execute("DROP TYPE IF EXISTS alert_scope_enum")

    op.drop_index("ix_delivery_results_detected", table_name="delivery_results")
    op.drop_index("ix_delivery_results_seed_detected", table_name="delivery_results")
    op.drop_index("ix_delivery_results_campaign_placement", table_name="delivery_results")
    op.drop_index("ix_delivery_results_seed_account_id", table_name="delivery_results")
    op.drop_index("ix_delivery_results_campaign_id", table_name="delivery_results")
    op.drop_table("delivery_results")
    op.execute("DROP TYPE IF EXISTS source_provider_enum")
    op.execute("DROP TYPE IF EXISTS placement_enum")

    op.drop_table("campaigns")
