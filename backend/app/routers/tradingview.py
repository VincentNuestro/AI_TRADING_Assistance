from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.tradingview import TradingViewAlert, WebhookResponse
from app.services.trading import plan_trade, record_alert, resolve_strategy, run_trade_stack
from app.utils.security import validate_nonce, validate_timestamp, verify_hmac_signature

router = APIRouter()
NONCE_CACHE: set[str] = set()


@router.post("/tradingview", response_model=WebhookResponse)
async def handle_tradingview_alert(
    request: Request,
    payload: TradingViewAlert,
    *,
    x_signature: str = Header(alias="X-Signature"),
    x_timestamp: str = Header(alias="X-Timestamp"),
    x_nonce: str = Header(alias="X-Nonce"),
    db: AsyncSession = Depends(get_db),
) -> WebhookResponse:
    raw_body = await request.body()

    if not verify_hmac_signature(raw_body, x_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")
    if not validate_timestamp(x_timestamp):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Timestamp skew too large")
    if not validate_nonce(x_nonce, NONCE_CACHE):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nonce already used")

    side = "BUY" if payload.state.lower() == "green" else "SELL"
    strategy = await resolve_strategy(db, payload.strategy)
    try:
        alert = await record_alert(
            db,
            strategy,
            payload.model_dump(mode="json"),
            side=side,
            signature=x_signature,
            idempotency_key=payload.idempotency_key,
            timestamp=payload.timenow,
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate alert")

    prediction, risk = await run_trade_stack(alert)
    plan = await plan_trade(alert, prediction, risk)

    await db.commit()

    return WebhookResponse(status="received", decision=plan.decision, order_units=plan.units)
