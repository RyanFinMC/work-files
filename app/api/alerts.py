from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db_session
from app.models.alert_event import AlertEvent
from app.schemas.alert_event import AlertEventListResponse, AlertEventRead

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=AlertEventListResponse)
def list_alerts(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
) -> AlertEventListResponse:
    rows = db.execute(select(AlertEvent).order_by(AlertEvent.created_at.desc()).offset(offset).limit(limit)).scalars().all()
    return AlertEventListResponse(data=[AlertEventRead.model_validate(row) for row in rows], count=len(rows))
