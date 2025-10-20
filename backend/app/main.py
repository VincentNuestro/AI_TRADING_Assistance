from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.logging.json_logger import configure_logging
from app.middleware.request_context import register_middlewares
from app.routers import accounts, auth, health, metrics, tradingview

configure_logging()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_middlewares(app)

app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
app.include_router(tradingview.router, prefix="/webhook", tags=["webhook"])


@app.get("/info", tags=["info"])
async def info() -> dict[str, str]:
    return {"app": settings.app_name, "env": settings.app_env}
