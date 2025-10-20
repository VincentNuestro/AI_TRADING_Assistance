from __future__ import annotations

import secrets
from functools import lru_cache
from typing import List, Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Trading Automation Platform"
    app_env: str = Field(default="local", alias="APP_ENV")
    debug: bool = Field(default=False, alias="APP_DEBUG")
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), alias="JWT_SECRET")
    access_token_expire_minutes: int = 30

    database_url: str = Field(default="sqlite+aiosqlite:///./local.db", alias="DB_URL")
    webhook_secret: str = Field(default="change_me", alias="WEBHOOK_SECRET")

    cors_origins: List[AnyHttpUrl] | List[str] = Field(default_factory=lambda: ["http://localhost:5173"], alias="CORS_ORIGINS")

    oanda_env: str = Field(default="practice", alias="OANDA_ENV")
    oanda_token: str = Field(default="", alias="OANDA_TOKEN")
    oanda_account_id: str = Field(default="", alias="OANDA_ACCOUNT_ID")

    prediction_gate_enabled: bool = Field(default=True, alias="PREDICTION_GATE_ENABLED")
    mc_paths: int = Field(default=20000, alias="MC_PATHS")
    use_torch_models: bool = Field(default=True, alias="USE_TORCH_MODELS")

    # Risk configuration
    risk_max_pct_per_trade: float = Field(default=0.5, alias="RISK_MAX_PCT_PER_TRADE")
    risk_min_sl_pips: float = Field(default=8, alias="RISK_MIN_SL_PIPS")
    risk_max_sl_pips: float = Field(default=250, alias="RISK_MAX_SL_PIPS")
    risk_atr_period: int = Field(default=14, alias="RISK_ATR_PERIOD")
    risk_atr_mult_sl: float = Field(default=1.5, alias="RISK_ATR_MULT_SL")
    risk_atr_mult_tp: float = Field(default=3.0, alias="RISK_ATR_MULT_TP")
    risk_use_r_mult_tp: bool = Field(default=True, alias="RISK_USE_R_MULT_TP")
    risk_r_mult_tp: float = Field(default=2.0, alias="RISK_R_MULT_TP")
    risk_tsl_enable: bool = Field(default=True, alias="RISK_TSL_ENABLE")
    risk_tsl_atr_mult: float = Field(default=1.2, alias="RISK_TSL_ATR_MULT")
    risk_breakeven_enable: bool = Field(default=True, alias="RISK_BREAKEVEN_ENABLE")
    risk_breakeven_after_r: float = Field(default=1.0, alias="RISK_BREAKEVEN_AFTER_R")
    risk_time_stop_enable: bool = Field(default=True, alias="RISK_TIME_STOP_ENABLE")
    risk_time_stop_min: int = Field(default=120, alias="RISK_TIME_STOP_MIN")
    risk_max_dd_day_pct: float = Field(default=3.0, alias="RISK_MAX_DD_DAY_PCT")
    risk_max_open_trades: int = Field(default=5, alias="RISK_MAX_OPEN_TRADES")
    risk_trading_windows: str = Field(default="09:00-23:00", alias="RISK_TRADING_WINDOWS")
    risk_news_block_enable: bool = Field(default=False, alias="RISK_NEWS_BLOCK_ENABLE")
    risk_spread_max_pips: float = Field(default=35, alias="RISK_SPREAD_MAX_PIPS")
    risk_slippage_max_pips: float = Field(default=20, alias="RISK_SLIPPAGE_MAX_PIPS")
    risk_failsafe_mode: str = Field(default="block", alias="RISK_FAILSAFE_MODE")

    metrics_enabled: bool = Field(default=True, alias="METRICS_ENABLED")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
