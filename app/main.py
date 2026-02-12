from fastapi import FastAPI

from app.api.alerts import router as alerts_router
from app.api.campaigns import router as campaigns_router
from app.api.dashboard import router as dashboard_router
from app.api.health import router as health_router
from app.api.seed_accounts import router as seed_accounts_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)
app.include_router(health_router)
app.include_router(seed_accounts_router)
app.include_router(campaigns_router)
app.include_router(dashboard_router)
app.include_router(alerts_router)
