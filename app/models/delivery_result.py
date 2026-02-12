import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Placement(str, enum.Enum):
    inbox = "inbox"
    spam = "spam"
    promotions = "promotions"
    missing = "missing"


class SourceProvider(str, enum.Enum):
    imap = "imap"
    gmail_api = "gmail_api"
    ms_graph = "ms_graph"


class DeliveryResult(Base):
    __tablename__ = "delivery_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    seed_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("seed_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    placement: Mapped[Placement] = mapped_column(Enum(Placement, name="placement_enum"), nullable=False)
    detected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_provider: Mapped[SourceProvider] = mapped_column(
        Enum(SourceProvider, name="source_provider_enum"),
        nullable=False,
    )
    folder_or_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    spf_result: Mapped[str | None] = mapped_column(String(32), nullable=True)
    dkim_result: Mapped[str | None] = mapped_column(String(32), nullable=True)
    dmarc_result: Mapped[str | None] = mapped_column(String(32), nullable=True)
    raw_headers: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
