from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CampaignBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    subject_identifier: str = Field(min_length=1, max_length=255)
    header_identifier: str | None = Field(default=None, max_length=255)
    tracking_id: str | None = Field(default=None, max_length=255)


class CampaignCreate(CampaignBase):
    sent_at: datetime


class CampaignRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    subject_identifier: str
    header_identifier: str | None
    tracking_id: str | None
    sent_at: datetime
    created_at: datetime


class CampaignResponse(BaseModel):
    data: CampaignRead


class CampaignListResponse(BaseModel):
    data: list[CampaignRead]
    count: int


class CampaignCheckRunRead(BaseModel):
    campaign_id: UUID
    created_count: int
    skipped_count: int
    total_active_seeds: int
    alerts_created: int


class CampaignCheckRunResponse(BaseModel):
    data: CampaignCheckRunRead
