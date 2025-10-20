from __future__ import annotations

from datetime import datetime, date, timezone

from sqlalchemy import Boolean, CheckConstraint, Column, Date, DateTime, Enum, ForeignKey, Index, Integer, JSON, LargeBinary, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


role_enum = Enum("admin", "trader", "viewer", name="role_enum", native_enum=False, validate_strings=True)
side_enum = Enum("BUY", "SELL", name="side_enum", native_enum=False, validate_strings=True)
order_type_enum = Enum("market", "limit", name="order_type_enum", native_enum=False, validate_strings=True)
account_env_enum = Enum("practice", "live", name="account_env_enum", native_enum=False, validate_strings=True)
status_enum = Enum("pending", "processed", "error", name="status_enum", native_enum=False, validate_strings=True)
model_type_enum = Enum("ffnn", "lstm", "gru", name="model_type_enum", native_enum=False, validate_strings=True)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )


class User(Base, TimestampMixin):
    __tablename__ = "tr_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(role_enum, nullable=False, default="viewer")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    twofa_secret: Mapped[str | None] = mapped_column(String(32))

    sessions: Mapped[list["Session"]] = relationship(back_populates="user")
    api_keys: Mapped[list["ApiKey"]] = relationship(back_populates="user")


class Session(Base):
    __tablename__ = "tr_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("tr_users.id", ondelete="CASCADE"), nullable=False)
    jti: Mapped[str] = mapped_column(String(255), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ip_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    ua_hash: Mapped[str] = mapped_column(String(128), nullable=False)

    user: Mapped[User] = relationship(back_populates="sessions")


class ApiKey(Base):
    __tablename__ = "tr_api_keys"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("tr_users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_secret: Mapped[str] = mapped_column(String(255), nullable=False)
    scope: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="api_keys")


class Account(Base, TimestampMixin):
    __tablename__ = "tr_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("tr_users.id"), nullable=False)
    oanda_account_id: Mapped[str] = mapped_column(String(64), nullable=False)
    env: Mapped[str] = mapped_column(account_env_enum, nullable=False)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_health_ts: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    orders: Mapped[list["Order"]] = relationship(back_populates="account")
    positions: Mapped[list["Position"]] = relationship(back_populates="account")


class Strategy(Base):
    __tablename__ = "tr_strategies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    params_json: Mapped[dict | None] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "tr_alerts"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_alert_idem"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    strategy_id: Mapped[int] = mapped_column(ForeignKey("tr_strategies.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    side: Mapped[str] = mapped_column(side_enum, nullable=False)
    timeframe: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    raw_payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    sig_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sig_hmac: Mapped[str] = mapped_column(String(128), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)


class Order(Base):
    __tablename__ = "tr_orders"
    __table_args__ = (
        UniqueConstraint("client_order_id", name="uq_order_client"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("tr_accounts.id"), nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    side: Mapped[str] = mapped_column(side_enum, nullable=False)
    units: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(order_type_enum, nullable=False)
    sl: Mapped[float | None] = mapped_column()
    tp: Mapped[float | None] = mapped_column()
    client_order_id: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    oanda_order_id: Mapped[str | None] = mapped_column(String(128), index=True)
    placed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    filled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    meta_json: Mapped[dict | None] = mapped_column(JSON)

    account: Mapped[Account] = relationship(back_populates="orders")
    executions: Mapped[list["Execution"]] = relationship(back_populates="order")


class Position(Base):
    __tablename__ = "tr_positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("tr_accounts.id"), nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    net_units: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_price: Mapped[float] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_json: Mapped[dict | None] = mapped_column(JSON)

    account: Mapped[Account] = relationship(back_populates="positions")


class Execution(Base):
    __tablename__ = "tr_executions"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("tr_orders.id", ondelete="CASCADE"), nullable=False)
    fill_price: Mapped[float] = mapped_column()
    fill_units: Mapped[int] = mapped_column(Integer, nullable=False)
    fees: Mapped[float] = mapped_column(default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    order: Mapped[Order] = relationship(back_populates="executions")


class DailyPnL(Base):
    __tablename__ = "tr_pnl_daily"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("tr_accounts.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    realized_pnl: Mapped[float] = mapped_column(default=0.0)
    unrealized_pnl: Mapped[float] = mapped_column(default=0.0)
    equity: Mapped[float] = mapped_column(default=0.0)
    drawdown: Mapped[float] = mapped_column(default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "tr_predictions"
    __table_args__ = (
        Index("ix_predictions_symbol_tf", "symbol", "timeframe", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    strategy_id: Mapped[int] = mapped_column(ForeignKey("tr_strategies.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(16), nullable=False)
    features_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    pred_direction: Mapped[str] = mapped_column(String(16), nullable=False)
    prob_long: Mapped[float] = mapped_column()
    prob_short: Mapped[float] = mapped_column()
    exp_return_bps: Mapped[float] = mapped_column()
    uncertainty: Mapped[float] = mapped_column()
    decision: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)


class Model(Base):
    __tablename__ = "tr_models"
    __table_args__ = (
        UniqueConstraint("model_version", name="uq_model_version"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    type: Mapped[str] = mapped_column(model_type_enum, nullable=False)
    params_json: Mapped[dict | None] = mapped_column(JSON)
    metrics_json: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(32), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Backtest(Base):
    __tablename__ = "tr_backtests"

    id: Mapped[int] = mapped_column(primary_key=True)
    strategy_id: Mapped[int] = mapped_column(ForeignKey("tr_strategies.id"), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    period_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metrics_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class MonteCarloRun(Base):
    __tablename__ = "tr_mc_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    strategy_id: Mapped[int] = mapped_column(ForeignKey("tr_strategies.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    horizon_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    n_paths: Mapped[int] = mapped_column(Integer, nullable=False)
    drift: Mapped[float] = mapped_column()
    vol: Mapped[float] = mapped_column()
    pnl_metrics_json: Mapped[dict | None] = mapped_column(JSON)
    distribution_blob: Mapped[bytes | None] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "tr_audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor: Mapped[str] = mapped_column(String(128), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    entity: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_id: Mapped[int | None] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    context_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)


class Report(Base):
    __tablename__ = "tr_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("tr_users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    params_json: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    file_path: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class ReportJob(Base):
    __tablename__ = "tr_report_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("tr_reports.id", ondelete="CASCADE"), nullable=False)
    requested_by: Mapped[int] = mapped_column(ForeignKey("tr_users.id"), nullable=False)
    schedule_cron: Mapped[str | None] = mapped_column(String(64))
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class RiskEvent(Base):
    __tablename__ = "tr_risk_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("tr_orders.id"))
    position_id: Mapped[int | None] = mapped_column(ForeignKey("tr_positions.id"))
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    before_sl: Mapped[float | None] = mapped_column()
    after_sl: Mapped[float | None] = mapped_column()
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    context_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


__all__ = [
    "User",
    "Session",
    "ApiKey",
    "Account",
    "Strategy",
    "Alert",
    "Order",
    "Position",
    "Execution",
    "DailyPnL",
    "Prediction",
    "Model",
    "Backtest",
    "MonteCarloRun",
    "AuditLog",
    "Report",
    "ReportJob",
    "RiskEvent",
]
