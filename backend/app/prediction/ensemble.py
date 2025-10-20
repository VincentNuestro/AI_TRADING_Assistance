from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(slots=True)
class PredictionRequest:
    symbol: str
    timeframe: str
    lookback: int
    horizons: Sequence[int]


@dataclass(slots=True)
class EnsembleDecision:
    model_version: str
    pred_direction: str
    prob_long: float
    prob_short: float
    exp_return_bps: float
    uncertainty: float
    decision: str
    top_features: list[str]


async def run_ensemble(request: PredictionRequest) -> EnsembleDecision:
    # Placeholder: in production load torch models.
    # Decision: PASS with dummy probabilities.
    prob_long = 0.62 if request.symbol.upper().endswith("USD") else 0.5
    prob_short = 1 - prob_long
    return EnsembleDecision(
        model_version="v0.1.0",
        pred_direction="LONG" if prob_long >= prob_short else "SHORT",
        prob_long=prob_long,
        prob_short=prob_short,
        exp_return_bps=12.5,
        uncertainty=0.18,
        decision="PASS" if prob_long > 0.55 else "DOWNSIZE",
        top_features=["atr_pct", "rsi", "macd_hist"],
    )
