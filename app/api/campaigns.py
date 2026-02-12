from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db_session
from app.models.campaign import Campaign
from app.models.delivery_result import DeliveryResult, Placement
from app.schemas.campaign import (
    CampaignCheckRunRead,
    CampaignCheckRunResponse,
    CampaignCreate,
    CampaignListResponse,
    CampaignRead,
    CampaignResponse,
)
from app.schemas.delivery_result import CampaignResultsRead, CampaignResultsResponse, DeliveryResultRead
from app.services.check_runner import run_campaign_checks

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db_session)) -> CampaignResponse:
    campaign = Campaign(**payload.model_dump())
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return CampaignResponse(data=CampaignRead.model_validate(campaign))


@router.get("", response_model=CampaignListResponse)
def list_campaigns(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
) -> CampaignListResponse:
    rows = db.execute(select(Campaign).order_by(Campaign.sent_at.desc()).offset(offset).limit(limit)).scalars().all()
    return CampaignListResponse(data=[CampaignRead.model_validate(row) for row in rows], count=len(rows))


@router.post("/{campaign_id}/checks/run", response_model=CampaignCheckRunResponse)
def run_checks_for_campaign(campaign_id: UUID, db: Session = Depends(get_db_session)) -> CampaignCheckRunResponse:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    run_stats = run_campaign_checks(db=db, campaign=campaign)
    return CampaignCheckRunResponse(data=CampaignCheckRunRead(campaign_id=campaign.id, **run_stats))


@router.get("/{campaign_id}/results", response_model=CampaignResultsResponse)
def get_campaign_results(
    campaign_id: UUID,
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
) -> CampaignResultsResponse:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    rows = (
        db.execute(
            select(DeliveryResult)
            .where(DeliveryResult.campaign_id == campaign_id)
            .order_by(DeliveryResult.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        .scalars()
        .all()
    )

    grouped_rows = db.execute(
        select(DeliveryResult.placement, func.count(DeliveryResult.id))
        .where(DeliveryResult.campaign_id == campaign_id)
        .group_by(DeliveryResult.placement)
    ).all()
    counts = {placement.value: count for placement, count in grouped_rows}
    for placement in Placement:
        counts.setdefault(placement.value, 0)
    total = sum(counts.values())

    payload = CampaignResultsRead(
        campaign_id=campaign_id,
        placement_counts=counts,
        total=total,
        results=[DeliveryResultRead.model_validate(row) for row in rows],
        count=len(rows),
    )
    return CampaignResultsResponse(data=payload)
