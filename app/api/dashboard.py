from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.db import get_db_session
from app.models.delivery_result import DeliveryResult, Placement
from app.models.seed_account import SeedAccount
from app.schemas.dashboard import (
    DashboardEspBreakdownRead,
    DashboardEspBreakdownResponse,
    DashboardSummaryRead,
    DashboardSummaryResponse,
    EspBreakdownRow,
    SummaryCounts,
    SummaryRates,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _compute_rates(counts: SummaryCounts) -> SummaryRates:
    if counts.total == 0:
        return SummaryRates()
    return SummaryRates(
        inbox_pct=round((counts.inbox / counts.total) * 100, 2),
        spam_pct=round((counts.spam / counts.total) * 100, 2),
        promotions_pct=round((counts.promotions / counts.total) * 100, 2),
        missing_pct=round((counts.missing / counts.total) * 100, 2),
    )


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    from_ts: datetime | None = Query(default=None),
    to_ts: datetime | None = Query(default=None),
    db: Session = Depends(get_db_session),
) -> DashboardSummaryResponse:
    now = datetime.now(timezone.utc)
    from_dt = from_ts or (now - timedelta(days=7))
    to_dt = to_ts or now

    rows = db.execute(
        select(DeliveryResult.placement, func.count(DeliveryResult.id))
        .where(and_(DeliveryResult.created_at >= from_dt, DeliveryResult.created_at <= to_dt))
        .group_by(DeliveryResult.placement)
    ).all()

    counts = SummaryCounts()
    for placement, count in rows:
        if placement == Placement.inbox:
            counts.inbox = count
        elif placement == Placement.spam:
            counts.spam = count
        elif placement == Placement.promotions:
            counts.promotions = count
        elif placement == Placement.missing:
            counts.missing = count
    counts.total = counts.inbox + counts.spam + counts.promotions + counts.missing

    payload = DashboardSummaryRead(from_ts=from_dt, to_ts=to_dt, counts=counts, rates=_compute_rates(counts))
    return DashboardSummaryResponse(data=payload)


@router.get("/esp-breakdown", response_model=DashboardEspBreakdownResponse)
def get_esp_breakdown(
    campaign_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db_session),
) -> DashboardEspBreakdownResponse:
    stmt = (
        select(SeedAccount.esp_name, DeliveryResult.campaign_id, DeliveryResult.placement, func.count(DeliveryResult.id))
        .join(SeedAccount, SeedAccount.id == DeliveryResult.seed_account_id)
        .group_by(SeedAccount.esp_name, DeliveryResult.campaign_id, DeliveryResult.placement)
        .order_by(SeedAccount.esp_name.asc())
    )
    if campaign_id:
        stmt = stmt.where(DeliveryResult.campaign_id == campaign_id)

    rows = db.execute(stmt).all()
    grouped: dict[tuple[str, UUID | None], SummaryCounts] = {}
    for esp_name, row_campaign_id, placement, count in rows:
        key = (esp_name, row_campaign_id)
        if key not in grouped:
            grouped[key] = SummaryCounts()
        bucket = grouped[key]
        if placement == Placement.inbox:
            bucket.inbox += count
        elif placement == Placement.spam:
            bucket.spam += count
        elif placement == Placement.promotions:
            bucket.promotions += count
        elif placement == Placement.missing:
            bucket.missing += count
        bucket.total = bucket.inbox + bucket.spam + bucket.promotions + bucket.missing

    result_rows = [
        EspBreakdownRow(
            esp_name=esp_name,
            campaign_id=row_campaign_id,
            counts=counts,
            rates=_compute_rates(counts),
        )
        for (esp_name, row_campaign_id), counts in grouped.items()
    ]
    return DashboardEspBreakdownResponse(data=DashboardEspBreakdownRead(rows=result_rows, count=len(result_rows)))
