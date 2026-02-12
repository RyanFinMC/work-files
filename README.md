# Seed List App

This repository is moving from planning into implementation.

## Current Implementation Status

### Completed in this kickoff
- FastAPI project scaffold
- Environment config loading via `pydantic-settings`
- SQLAlchemy DB session wiring
- Alembic migration framework setup
- `seed_accounts` model and initial migration
- Part 1 API endpoints:
  - `POST /seed-accounts`
  - `GET /seed-accounts`
  - `PATCH /seed-accounts/{id}`
- Validation via Pydantic (`EmailStr`, enum constraints)
- Secret reference-only credential field (`credential_ref`)

### Next planned slices
- Queue and worker baseline (Part 2)
- Campaign + delivery result tables and endpoints (Part 3)
- Dashboard aggregate endpoints (Part 4)

## Local Run

1. Install dependencies
2. Copy `.env.example` to `.env` and update `DATABASE_URL`
3. Run migrations
4. Start API

Example commands:

```bash
pip install -e .
alembic upgrade head
uvicorn app.main:app --reload
```

## Planning Status
Planning is complete through all Phase 1 parts and coding kickoff. See `seed-list-app-plan.md` for the full roadmap.
