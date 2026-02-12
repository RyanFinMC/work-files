from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db_session
from app.models.seed_account import SeedAccount
from app.schemas.seed_account import (
    SeedAccountCreate,
    SeedAccountListResponse,
    SeedAccountRead,
    SeedAccountResponse,
    SeedAccountUpdate,
)

router = APIRouter(prefix="/seed-accounts", tags=["seed-accounts"])


@router.post("", response_model=SeedAccountResponse, status_code=status.HTTP_201_CREATED)
def create_seed_account(
    payload: SeedAccountCreate,
    db: Session = Depends(get_db_session),
) -> SeedAccountResponse:
    seed_account = SeedAccount(**payload.model_dump())
    db.add(seed_account)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Seed account email already exists")

    db.refresh(seed_account)
    return SeedAccountResponse(data=SeedAccountRead.model_validate(seed_account))


@router.get("", response_model=SeedAccountListResponse)
def list_seed_accounts(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
) -> SeedAccountListResponse:
    rows = db.execute(select(SeedAccount).order_by(SeedAccount.created_at.desc()).offset(offset).limit(limit)).scalars().all()
    return SeedAccountListResponse(
        data=[SeedAccountRead.model_validate(row) for row in rows],
        count=len(rows),
    )


@router.patch("/{seed_account_id}", response_model=SeedAccountResponse)
def update_seed_account(
    seed_account_id: UUID,
    payload: SeedAccountUpdate,
    db: Session = Depends(get_db_session),
) -> SeedAccountResponse:
    seed_account = db.get(SeedAccount, seed_account_id)
    if not seed_account:
        raise HTTPException(status_code=404, detail="Seed account not found")

    updates = payload.model_dump(exclude_none=True)
    for field, value in updates.items():
        setattr(seed_account, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Seed account email already exists")

    db.refresh(seed_account)
    return SeedAccountResponse(data=SeedAccountRead.model_validate(seed_account))
