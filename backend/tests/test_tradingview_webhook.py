from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.core.config import settings
from app.db.session import Base
from app.db.session import get_db as original_get_db


@pytest.fixture(scope="module", autouse=True)
def override_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def init_models() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    import anyio

    anyio.run(init_models)

    async def get_db_override():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[original_get_db] = get_db_override
    yield
    app.dependency_overrides.pop(original_get_db, None)


client = TestClient(app)


@pytest.mark.asyncio
async def test_tradingview_webhook_rejects_bad_signature(monkeypatch):
    payload = {
        "strategy": "HullSuite",
        "symbol": "XAUUSD",
        "timeframe": "15m",
        "state": "green",
        "timenow": datetime.now(timezone.utc).isoformat(),
        "idempotency_key": "abc123",
    }
    body = json.dumps(payload).encode()
    headers = {
        "X-Signature": "bad",
        "X-Timestamp": datetime.now(timezone.utc).isoformat(),
        "X-Nonce": "nonce1",
    }
    response = client.post("/webhook/tradingview", json=payload, headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_tradingview_webhook_accepts_valid_signature(monkeypatch):
    payload = {
        "strategy": "HullSuite",
        "symbol": "XAUUSD",
        "timeframe": "15m",
        "state": "green",
        "timenow": datetime.now(timezone.utc).isoformat(),
        "idempotency_key": "abc124",
    }
    body = json.dumps(payload).encode()
    signature = hmac.new(settings.webhook_secret.encode(), body, hashlib.sha256).hexdigest()
    headers = {
        "X-Signature": signature,
        "X-Timestamp": datetime.now(timezone.utc).isoformat(),
        "X-Nonce": str(datetime.now().timestamp()),
    }
    response = client.post("/webhook/tradingview", json=payload, headers=headers)
    assert response.status_code in {200, 409}
