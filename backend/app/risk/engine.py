from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.core.config import settings
from app.prediction.ensemble import EnsembleDecision

RiskDecisionType = Literal["PASS", "DOWNSIZE", "BLOCK"]


@dataclass(slots=True)
class MonteCarloResult:
    mean: float
    std: float
    var95: float
    es95: float
    prob_hit_tp: float
    prob_hit_sl: float

    @staticmethod
    async def simulate(symbol: str, horizon_minutes: int, n_paths: int) -> "MonteCarloResult":
        # Placeholder deterministic simulation
        base = 10.0 if symbol.upper().endswith("USD") else 5.0
        return MonteCarloResult(
            mean=base,
            std=base * 0.8,
            var95=-base * 1.2,
            es95=-base * 1.5,
            prob_hit_tp=0.55,
            prob_hit_sl=0.25,
        )


@dataclass(slots=True)
class RiskDecision:
    decision: RiskDecisionType
    units: int
    stop_loss: float
    take_profit: float


def evaluate_trade_risk(prediction: EnsembleDecision, mc: MonteCarloResult) -> RiskDecision:
    if mc.es95 < -settings.risk_max_pct_per_trade * 100:
        return RiskDecision(decision="BLOCK", units=0, stop_loss=0.0, take_profit=0.0)
    if prediction.decision == "DOWNSIZE" or mc.prob_hit_tp < 0.5:
        units = 1000
        decision = "DOWNSIZE"
    else:
        units = 2000
        decision = "PASS"
    stop_loss = settings.risk_atr_mult_sl * 10
    take_profit = stop_loss * (settings.risk_r_mult_tp if settings.risk_use_r_mult_tp else settings.risk_atr_mult_tp)
    return RiskDecision(decision=decision, units=units, stop_loss=stop_loss, take_profit=take_profit)
