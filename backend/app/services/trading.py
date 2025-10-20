from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.entities import Alert, Strategy
from app.prediction.ensemble import EnsembleDecision, PredictionRequest, run_ensemble
from app.risk.engine import MonteCarloResult, RiskDecision, RiskDecisionType, evaluate_trade_risk


@dataclass(slots=True)
class TradePlan:
    decision: RiskDecisionType
    units: int
    atr_sl: float
    atr_tp: float
    breakeven_after: float
    trailing_atr_mult: float


async def resolve_strategy(session: AsyncSession, strategy_name: str) -> Strategy:
    stmt = select(Strategy).where(Strategy.name == strategy_name)
    result = await session.execute(stmt)
    strategy = result.scalar_one_or_none()
    if strategy is None:
        strategy = Strategy(name=strategy_name, code="hullsuite", params_json={})
        session.add(strategy)
        await session.flush()
    return strategy


async def record_alert(
    session: AsyncSession,
    strategy: Strategy,
    payload: dict,
    *,
    side: str,
    signature: str,
    idempotency_key: str,
    timestamp: datetime,
) -> Alert:
    alert = Alert(
        strategy_id=strategy.id,
        symbol=payload["symbol"],
        side=side,
        timeframe=payload["timeframe"],
        raw_payload_json=payload,
        sig_ts=timestamp,
        sig_hmac=signature,
        idempotency_key=idempotency_key,
    )
    session.add(alert)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise ValueError("Duplicate alert idempotency key") from exc
    return alert


async def plan_trade(alert: Alert, prediction: EnsembleDecision, risk: MonteCarloResult) -> TradePlan:
    decision = evaluate_trade_risk(prediction, risk)
    units = decision.units
    return TradePlan(
        decision=decision.decision,
        units=units,
        atr_sl=decision.stop_loss,
        atr_tp=decision.take_profit,
        breakeven_after=settings.risk_breakeven_after_r,
        trailing_atr_mult=settings.risk_tsl_atr_mult,
    )


async def run_trade_stack(alert: Alert) -> tuple[EnsembleDecision, MonteCarloResult]:
    prediction = await run_ensemble(
        PredictionRequest(symbol=alert.symbol, timeframe=alert.timeframe, lookback=500, horizons=[3, 6, 12])
    )
    risk = await MonteCarloResult.simulate(symbol=alert.symbol, horizon_minutes=15, n_paths=settings.mc_paths)
    return prediction, risk
