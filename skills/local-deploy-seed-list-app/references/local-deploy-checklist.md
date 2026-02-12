# Local Deploy Checklist

## Prerequisites

- Python 3.11 or newer
- PowerShell
- PostgreSQL reachable from `DATABASE_URL` in `.env`
- Optional: Docker (for `start_postgres_docker.ps1`)

## Recommended Run Order

1. `scripts/bootstrap_local.ps1`
2. `scripts/start_postgres_docker.ps1` (only if not using an existing PostgreSQL)
3. `scripts/start_api.ps1`
4. Open `http://localhost:8000/docs`
5. Health check: `GET http://localhost:8000/health`

## Troubleshooting

- Alembic fails with connection error:
  - Confirm PostgreSQL is running.
  - Confirm `.env` `DATABASE_URL` matches host/port/credentials/database.
- `uvicorn` command not found:
  - Ensure virtualenv is active.
  - Re-run bootstrap to install dependencies.
- Port 8000 already in use:
  - Stop conflicting process or run uvicorn with a different `--port`.
- Import errors during startup:
  - Re-run `pip install -e .` in the active virtualenv.
