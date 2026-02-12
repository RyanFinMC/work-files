from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.delivery_result import Placement, SourceProvider


class DeliveryResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    campaign_id: UUID
    seed_account_id: UUID
    placement: Placement
    detected_at: datetime | None
    latency_ms: int | None
    source_provider: SourceProvider
    folder_or_label: str | None
    spf_result: str | None
    dkim_result: str | None
    dmarc_result: str | None
    raw_headers: dict | None
    created_at: datetime


class CampaignResultsRead(BaseModel):
    campaign_id: UUID
    placement_counts: dict[str, int]
    total: int
    results: list[DeliveryResultRead]
    count: int


class CampaignResultsResponse(BaseModel):
    data: CampaignResultsRead
