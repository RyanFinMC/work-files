# Seed List App

This repository is moving from planning into implementation.

## Planning Status
✅ Planning is now complete through all Phase 1 parts and the coding kickoff plan below.

## Phase 1 (MVP Foundation)

### Phase 1 scope
- Seed account CRUD + secret references
- IMAP connector + worker queue
- Campaign registration + basic result table
- Simple dashboard summary + ESP table

### Progress tracker
- [ ] Part 1 — Seed Account CRUD + Secret References
- [ ] Part 2 — IMAP Connector + Worker Queue
- [ ] Part 3 — Campaign Registration + Basic Result Table
- [ ] Part 4 — Simple Dashboard Summary + ESP Table

---

## Part 1 — Seed Account CRUD + Secret References

### Objective
Implement the data model and API endpoints needed to create, update, list, and manage seed accounts without storing plaintext credentials.

### Deliverables
- [ ] `seed_accounts` schema finalized (UUID id, email, esp_name, auth_method, credential_ref, status, timestamps)
- [ ] Unique constraint on `email`
- [ ] `POST /seed-accounts` endpoint
- [ ] `GET /seed-accounts` endpoint
- [ ] `PATCH /seed-accounts/:id` endpoint
- [ ] Validation rules (email format, allowed auth methods/status values)
- [ ] Secret reference pattern documented (`credential_ref` only)

### Definition of done
- CRUD endpoints return consistent JSON payloads.
- Invalid payloads return clear validation errors.
- No plaintext mailbox passwords/tokens are persisted in the application database.

---

## Part 2 — IMAP Connector + Worker Queue

### Objective
Build an asynchronous check pipeline that polls IMAP seed inboxes for campaign messages and writes normalized placement outcomes.

### Deliverables
- [ ] Worker queue selected and configured (e.g., Redis + queue abstraction)
- [ ] Job payload contract defined (`campaign_id`, `seed_account_id`, `attempt`, `scheduled_at`)
- [ ] IMAP connector module with login + mailbox selection + search capability
- [ ] Poll schedule implemented (T+1, T+3, T+5, T+10 minutes)
- [ ] Placement classification for IMAP folders (`inbox`, `spam`, `missing`)
- [ ] Retry/backoff and final missing-state handling
- [ ] Basic deduplication (avoid duplicate writes for same campaign/seed)
- [ ] Structured worker logs (job id, seed id, provider, outcome, latency)
- [ ] Failure handling for auth/network errors with status updates

### Definition of done
- Given a queued campaign check, worker attempts mailbox polling at configured intervals.
- For each seed, a terminal state is produced within retry window (`inbox`, `spam`, or `missing`).
- Transient failures are retried; permanent failures are surfaced with actionable logs.
- Queue and worker can process multiple seed accounts concurrently without duplicate final writes.

---

## Part 3 — Campaign Registration + Basic Result Table

### Objective
Implement campaign creation and result persistence so every seed check has a traceable campaign context.

### Deliverables
- [ ] `campaigns` table schema (`id`, `name`, `subject_identifier`, `header_identifier`, `tracking_id`, `sent_at`, `created_at`)
- [ ] `delivery_results` table schema (`campaign_id`, `seed_account_id`, `placement`, `detected_at`, `latency_ms`, `source_provider`, auth fields)
- [ ] FK constraints from `delivery_results` to `campaigns` and `seed_accounts`
- [ ] `POST /campaigns` endpoint
- [ ] `GET /campaigns` endpoint with basic pagination/filter by date
- [ ] `POST /campaigns/:id/checks/run` endpoint to enqueue checks for selected/all seeds
- [ ] Idempotency rule for campaign check runs (to avoid duplicate enqueue storms)
- [ ] Basic query endpoint for results: `GET /campaigns/:id/results`

### Result model contract
- `placement`: `inbox | spam | promotions | missing`
- `source_provider`: `imap | gmail_api | ms_graph`
- `detected_at` and `latency_ms` nullable for terminal `missing`
- auth columns optional: `spf_result`, `dkim_result`, `dmarc_result`

### Definition of done
- A campaign can be created and listed.
- Triggering checks creates queue jobs against seed accounts.
- Worker writes normalized `delivery_results` records linked to a campaign and seed.
- Duplicate check-trigger requests are safely ignored or merged according to idempotency key.

---

## Part 4 — Simple Dashboard Summary + ESP Table

### Objective
Expose a minimal read model/UI surface for immediate campaign and ESP health visibility.

### Deliverables
- [ ] Summary query/service for global placement rates in a date range
- [ ] ESP breakdown query/service (inbox %, spam %, missing %, total seeds checked)
- [ ] `GET /dashboard/summary?from=&to=` endpoint
- [ ] `GET /dashboard/esp-breakdown?campaign_id=&from=&to=` endpoint
- [ ] Basic frontend view (or API-only placeholder if UI stack not initialized)
- [ ] Empty/error/loading states defined
- [ ] CSV export of current view (optional if time allows)

### Required calculations
- `inbox_rate = inbox_count / total_checked`
- `spam_rate = spam_count / total_checked`
- `missing_rate = missing_count / total_checked`
- `total_checked` excludes seeds not yet in terminal state for active runs

### Definition of done
- Dashboard endpoints return accurate aggregated values for a known fixture dataset.
- At least one campaign and one date-range summary can be inspected end to end.
- Results are grouped by ESP consistently using canonical ESP values.

---

## Cross-Cutting Decisions (Locked for Phase 1)

### Canonical enums
- `placement`: `inbox | spam | promotions | missing`
- `seed_status`: `active | paused | auth_expired | error`
- `auth_method`: `oauth2 | imap_secret`
- `source_provider`: `imap | gmail_api | ms_graph`

### Retry policy
- Scheduled checks at minute offsets: `+1, +3, +5, +10` from `sent_at`
- Transition to `missing` only after final attempt
- Exponential backoff with jitter for network/provider errors

### Data integrity
- Unique `seed_accounts.email`
- One terminal result per (`campaign_id`, `seed_account_id`) per run
- All writes include `created_at` and source metadata for traceability

### Security rules
- Never store plaintext mailbox credentials in DB
- Store only `credential_ref`
- Log redaction required for secrets and tokens

---

## Coding Kickoff Plan (Start Immediately)

### Sprint 0 (first coding PRs)
1. **PR A — Project skeleton + config**
   - API service scaffold
   - DB migration framework setup
   - Environment config loading + validation
2. **PR B — Part 1 core**
   - `seed_accounts` migration + CRUD endpoints + validators
3. **PR C — Part 2 queue/worker baseline**
   - Queue bootstrap + worker process + job contract
4. **PR D — Part 3 campaign/results baseline**
   - `campaigns` + `delivery_results` migrations + enqueue endpoint + results endpoint
5. **PR E — Part 4 dashboard API**
   - Summary and ESP breakdown endpoints

### Initial acceptance gates before moving to Phase 2
- [ ] End-to-end flow: create campaign → enqueue checks → write terminal results → query dashboard summaries
- [ ] Basic reliability: retries verified in test/staging
- [ ] Security baseline: credential references only, secrets redacted in logs

---

## What we code next
We start coding with **PR A (project skeleton + config)** and then proceed through PR B–E in order.

---

## Local Development Setup (Recommended)

If you want to start implementation immediately, use this local stack:

- **Frontend:** Next.js
- **API:** FastAPI (Python)
- **Database:** PostgreSQL
- **Queue/Cache:** Redis
- **Worker:** Celery (or RQ) worker process

This aligns with the architecture in `seed-list-app-plan.md` and keeps the API + worker split clear from day one.

### 1) Prerequisites

Install locally:

- Docker + Docker Compose (recommended for DB/Redis)
- Python 3.11+
- Node.js 20+
- pnpm or npm

### 2) Suggested project structure

```text
seed-list-app/
  apps/
    web/                 # Next.js UI
    api/                 # FastAPI service
    worker/              # Celery worker + polling jobs
  infra/
    docker-compose.yml   # Postgres + Redis
  .env.example
```

### 3) `docker-compose.yml` (Postgres + Redis)

Create `infra/docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: seed
      POSTGRES_PASSWORD: seed
      POSTGRES_DB: seedlist
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

Run:

```bash
docker compose -f infra/docker-compose.yml up -d
```

### 4) Environment variables (`.env.example`)

```dotenv
# Shared
DATABASE_URL=postgresql://seed:seed@localhost:5432/seedlist
REDIS_URL=redis://localhost:6379/0

# API
API_PORT=8000
SECRET_BACKEND=local

# Worker polling cadence (minutes)
POLL_SCHEDULE_MINUTES=1,3,5,10

# Optional provider credentials
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
MS_GRAPH_CLIENT_ID=
MS_GRAPH_CLIENT_SECRET=
```

### 5) API service bootstrap (FastAPI)

Inside `apps/api`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn sqlalchemy psycopg[binary] alembic pydantic-settings redis
```

Start API:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6) Worker bootstrap (Celery)

Inside `apps/worker`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install celery redis imapclient
```

Start worker:

```bash
celery -A worker.app worker --loglevel=INFO
```

### 7) Frontend bootstrap (Next.js)

Inside `apps/web`:

```bash
npx create-next-app@latest . --ts --eslint --app --src-dir
pnpm dev
```

Set API base URL in the web app env:

```dotenv
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 8) Minimum startup checklist

- [ ] `docker compose ... up -d` (Postgres + Redis running)
- [ ] API responds on `GET /health`
- [ ] Worker connected to Redis and accepting jobs
- [ ] Frontend loads and can call API base URL

### 9) Alternate Node-only stack (also valid)

If your team prefers Node end-to-end, you can substitute:

- **API:** Express/NestJS
- **Worker/Queue:** BullMQ + Redis
- **ORM/Migrations:** Prisma or Drizzle

Keep Postgres + Redis and the same service boundaries.
