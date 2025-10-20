from __future__ import annotations

import pytest

from app.prediction.ensemble import EnsembleDecision
from app.risk.engine import MonteCarloResult, evaluate_trade_risk


@pytest.mark.asyncio
async def test_monte_carlo_simulation_deterministic():
    result = await MonteCarloResult.simulate(symbol="XAUUSD", horizon_minutes=15, n_paths=1000)
    assert result.mean > 0
    assert result.prob_hit_tp > result.prob_hit_sl


def test_evaluate_trade_risk_block_on_large_loss(monkeypatch):
    prediction = EnsembleDecision(
        model_version="v0",
        pred_direction="LONG",
        prob_long=0.6,
        prob_short=0.4,
        exp_return_bps=10,
        uncertainty=0.2,
        decision="PASS",
        top_features=["atr_pct"],
    )
    mc = MonteCarloResult(mean=1, std=1, var95=-1000, es95=-1000, prob_hit_tp=0.1, prob_hit_sl=0.9)
    decision = evaluate_trade_risk(prediction, mc)
    assert decision.decision == "BLOCK"


def test_evaluate_trade_risk_pass_default():
    prediction = EnsembleDecision(
        model_version="v0",
        pred_direction="LONG",
        prob_long=0.7,
        prob_short=0.3,
        exp_return_bps=10,
        uncertainty=0.2,
        decision="PASS",
        top_features=["atr_pct"],
    )
    mc = MonteCarloResult(mean=10, std=5, var95=-5, es95=-5, prob_hit_tp=0.6, prob_hit_sl=0.2)
    decision = evaluate_trade_risk(prediction, mc)
    assert decision.decision in {"PASS", "DOWNSIZE"}
