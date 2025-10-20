from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TradingViewAlert(BaseModel):
    strategy: str
    symbol: str
    timeframe: str
    state: str
    timenow: datetime = Field(alias="timenow")
    idempotency_key: str

    model_config = {
        "populate_by_name": True,
        "str_strip_whitespace": True,
    }


class WebhookResponse(BaseModel):
    status: str
    decision: str
    order_units: int | None = None
