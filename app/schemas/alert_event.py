from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.alert_event import AlertScope, AlertSeverity


class AlertEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    campaign_id: UUID | None
    scope: AlertScope
    severity: AlertSeverity
    message: str
    esp_name: str | None
    created_at: datetime


class AlertEventListResponse(BaseModel):
    data: list[AlertEventRead]
    count: int
