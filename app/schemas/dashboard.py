from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SummaryCounts(BaseModel):
    inbox: int = 0
    spam: int = 0
    promotions: int = 0
    missing: int = 0
    total: int = 0


class SummaryRates(BaseModel):
    inbox_pct: float = 0.0
    spam_pct: float = 0.0
    promotions_pct: float = 0.0
    missing_pct: float = 0.0


class DashboardSummaryRead(BaseModel):
    from_ts: datetime
    to_ts: datetime
    counts: SummaryCounts
    rates: SummaryRates


class DashboardSummaryResponse(BaseModel):
    data: DashboardSummaryRead


class EspBreakdownRow(BaseModel):
    esp_name: str
    campaign_id: UUID | None
    counts: SummaryCounts
    rates: SummaryRates


class DashboardEspBreakdownRead(BaseModel):
    rows: list[EspBreakdownRow]
    count: int


class DashboardEspBreakdownResponse(BaseModel):
    data: DashboardEspBreakdownRead
