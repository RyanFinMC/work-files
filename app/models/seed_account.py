import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuthMethod(str, enum.Enum):
    oauth2 = "oauth2"
    imap_secret = "imap_secret"


class SeedStatus(str, enum.Enum):
    active = "active"
    paused = "paused"
    auth_expired = "auth_expired"
    error = "error"


class SeedAccount(Base):
    __tablename__ = "seed_accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    esp_name: Mapped[str] = mapped_column(String(100), nullable=False)
    auth_method: Mapped[AuthMethod] = mapped_column(Enum(AuthMethod, name="auth_method"), nullable=False)
    credential_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[SeedStatus] = mapped_column(
        Enum(SeedStatus, name="seed_status"),
        nullable=False,
        default=SeedStatus.active,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
