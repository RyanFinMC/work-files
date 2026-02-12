import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AlertScope(str, enum.Enum):
    global_scope = "global"
    esp = "esp"
    campaign = "campaign"


class AlertSeverity(str, enum.Enum):
    info = "info"
    warning = "warning"
    critical = "critical"


class AlertEvent(Base):
    __tablename__ = "alert_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    scope: Mapped[AlertScope] = mapped_column(Enum(AlertScope, name="alert_scope_enum"), nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity, name="alert_severity_enum"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    esp_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
