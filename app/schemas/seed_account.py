from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.seed_account import AuthMethod, SeedStatus


class SeedAccountBase(BaseModel):
    email: EmailStr
    esp_name: str = Field(min_length=1, max_length=100)
    auth_method: AuthMethod
    credential_ref: str = Field(min_length=1, max_length=255)
    status: SeedStatus = SeedStatus.active


class SeedAccountCreate(SeedAccountBase):
    pass


class SeedAccountUpdate(BaseModel):
    email: EmailStr | None = None
    esp_name: str | None = Field(default=None, min_length=1, max_length=100)
    auth_method: AuthMethod | None = None
    credential_ref: str | None = Field(default=None, min_length=1, max_length=255)
    status: SeedStatus | None = None


class SeedAccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    esp_name: str
    auth_method: AuthMethod
    credential_ref: str
    status: SeedStatus
    created_at: datetime
    updated_at: datetime


class SeedAccountListResponse(BaseModel):
    data: list[SeedAccountRead]
    count: int


class SeedAccountResponse(BaseModel):
    data: SeedAccountRead
