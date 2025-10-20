from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.core.config import settings


@dataclass(slots=True)
class OandaOrderResult:
    order_id: str
    status: str


class OandaClient:
    def __init__(self) -> None:
        self._base_url = "https://api-fxpractice.oanda.com/v3" if settings.oanda_env == "practice" else "https://api-fxtrade.oanda.com/v3"
        self._client = httpx.AsyncClient(base_url=self._base_url, headers={
            "Authorization": f"Bearer {settings.oanda_token}",
            "Content-Type": "application/json",
        }, timeout=10.0)

    async def close_positions(self, account_id: str, symbol: str) -> None:
        # Placeholder no-op for local testing
        return None

    async def place_market_order(
        self,
        account_id: str,
        symbol: str,
        side: str,
        units: int,
        *,
        stop_loss: float,
        take_profit: float,
        client_order_id: str,
    ) -> OandaOrderResult:
        # Placeholder - would call OANDA API
        return OandaOrderResult(order_id=f"demo-{client_order_id}", status="filled")

    async def aclose(self) -> None:
        await self._client.aclose()


async def get_client() -> OandaClient:
    return OandaClient()
