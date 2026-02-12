---
name: local-deploy-seed-list-app
description: Set up and run the Seed List App API on a local machine with a reproducible workflow for Python environment setup, environment variables, PostgreSQL readiness, Alembic migrations, and starting Uvicorn. Use when users ask to deploy this app locally, run it on localhost, bootstrap a new dev machine, or troubleshoot local startup failures.
---

# Local Deploy Seed List App

## Overview

Use this skill to bring the current FastAPI project online locally with minimal manual steps and consistent checks.

## Workflow

1. Verify prerequisites: Python 3.11+, `pip`, and optionally Docker.
2. Bootstrap Python environment and dependencies with `scripts/bootstrap_local.ps1`.
3. Ensure PostgreSQL is reachable:
- Use existing local PostgreSQL from `.env`.
- Or start an ephemeral Docker PostgreSQL with `scripts/start_postgres_docker.ps1`.
4. Run migrations.
5. Start API with `scripts/start_api.ps1`.
6. Confirm health endpoint.

## Commands

### 1. Bootstrap environment

```powershell
powershell -ExecutionPolicy Bypass -File skills/local-deploy-seed-list-app/scripts/bootstrap_local.ps1
```

### 2. Start PostgreSQL with Docker (optional)

```powershell
powershell -ExecutionPolicy Bypass -File skills/local-deploy-seed-list-app/scripts/start_postgres_docker.ps1
```

### 3. Start API server

```powershell
powershell -ExecutionPolicy Bypass -File skills/local-deploy-seed-list-app/scripts/start_api.ps1
```

## Operational Guidance

- Prefer `.venv` in repository root.
- Keep `.env` as source of truth for `DATABASE_URL`, `APP_HOST`, and `APP_PORT`.
- Run `alembic upgrade head` before first start and after schema changes.
- If database connection fails, verify database is reachable and matches `.env`.
- Use `references/local-deploy-checklist.md` for troubleshooting and smoke tests.
