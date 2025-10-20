from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "20240201_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    role_enum = sa.Enum("admin", "trader", "viewer", name="role_enum")
    side_enum = sa.Enum("BUY", "SELL", name="side_enum")
    order_type_enum = sa.Enum("market", "limit", name="order_type_enum")
    env_enum = sa.Enum("practice", "live", name="account_env_enum")
    model_type_enum = sa.Enum("ffnn", "lstm", "gru", name="model_type_enum")

    op.create_table(
        "tr_users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", role_enum, nullable=False, server_default="viewer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("twofa_secret", sa.String(length=32)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "tr_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("tr_users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("jti", sa.String(length=255), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip_hash", sa.String(length=128), nullable=False),
        sa.Column("ua_hash", sa.String(length=128), nullable=False),
    )

    op.create_table(
        "tr_api_keys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("tr_users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("hashed_secret", sa.String(length=255), nullable=False),
        sa.Column("scope", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "tr_accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("tr_users.id"), nullable=False),
        sa.Column("oanda_account_id", sa.String(length=64), nullable=False),
        sa.Column("env", env_enum, nullable=False),
        sa.Column("label", sa.String(length=128), nullable=False),
        sa.Column("is_default", sa.Boolean(), server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("last_health_ts", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "tr_strategies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("params_json", sa.JSON()),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "tr_alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("strategy_id", sa.Integer(), sa.ForeignKey("tr_strategies.id"), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("side", side_enum, nullable=False),
        sa.Column("timeframe", sa.String(length=16), nullable=False),
        sa.Column("raw_payload_json", sa.JSON(), nullable=False),
        sa.Column("sig_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sig_hmac", sa.String(length=128), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("idempotency_key", name="uq_alert_idem"),
    )
    op.create_index("ix_alert_symbol_tf", "tr_alerts", ["symbol", "timeframe", "created_at"])

    op.create_table(
        "tr_orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("tr_accounts.id"), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("side", side_enum, nullable=False),
        sa.Column("units", sa.Integer(), nullable=False),
        sa.Column("type", order_type_enum, nullable=False),
        sa.Column("sl", sa.Float()),
        sa.Column("tp", sa.Float()),
        sa.Column("client_order_id", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("oanda_order_id", sa.String(length=128)),
        sa.Column("placed_at", sa.DateTime(timezone=True)),
        sa.Column("filled_at", sa.DateTime(timezone=True)),
        sa.Column("meta_json", sa.JSON()),
        sa.UniqueConstraint("client_order_id", name="uq_order_client"),
    )
    op.create_index("ix_orders_symbol", "tr_orders", ["symbol"])
    op.create_index("ix_orders_oanda_id", "tr_orders", ["oanda_order_id"])

    op.create_table(
        "tr_positions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("tr_accounts.id"), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("net_units", sa.Integer(), nullable=False),
        sa.Column("avg_price", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("meta_json", sa.JSON()),
    )
    op.create_index("ix_positions_symbol", "tr_positions", ["symbol"])

    op.create_table(
        "tr_executions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("tr_orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fill_price", sa.Float(), nullable=False),
        sa.Column("fill_units", sa.Integer(), nullable=False),
        sa.Column("fees", sa.Float(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "tr_pnl_daily",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("tr_accounts.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("realized_pnl", sa.Float(), server_default="0"),
        sa.Column("unrealized_pnl", sa.Float(), server_default="0"),
        sa.Column("equity", sa.Float(), server_default="0"),
        sa.Column("drawdown", sa.Float(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "tr_predictions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("strategy_id", sa.Integer(), sa.ForeignKey("tr_strategies.id"), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("timeframe", sa.String(length=16), nullable=False),
        sa.Column("features_hash", sa.String(length=64), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("pred_direction", sa.String(length=16), nullable=False),
        sa.Column("prob_long", sa.Float(), nullable=False),
        sa.Column("prob_short", sa.Float(), nullable=False),
        sa.Column("exp_return_bps", sa.Float(), nullable=False),
        sa.Column("uncertainty", sa.Float(), nullable=False),
        sa.Column("decision", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_predictions_symbol_tf", "tr_predictions", ["symbol", "timeframe", "created_at"])

    op.create_table(
        "tr_models",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("type", model_type_enum, nullable=False),
        sa.Column("params_json", sa.JSON()),
        sa.Column("metrics_json", sa.JSON()),
        sa.Column("status", sa.String(length=32), server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("model_version", name="uq_model_version"),
    )

    op.create_table(
        "tr_backtests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("strategy_id", sa.Integer(), sa.ForeignKey("tr_strategies.id"), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("period_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_to", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metrics_json", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "tr_mc_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("strategy_id", sa.Integer(), sa.ForeignKey("tr_strategies.id"), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("horizon_minutes", sa.Integer(), nullable=False),
        sa.Column("n_paths", sa.Integer(), nullable=False),
        sa.Column("drift", sa.Float(), nullable=False),
        sa.Column("vol", sa.Float(), nullable=False),
        sa.Column("pnl_metrics_json", sa.JSON()),
        sa.Column("distribution_blob", sa.LargeBinary()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "tr_audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor", sa.String(length=128), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("entity", sa.String(length=128), nullable=False),
        sa.Column("entity_id", sa.Integer()),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("context_json", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_created", "tr_audit_logs", ["created_at"])

    op.create_table(
        "tr_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("tr_users.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("params_json", sa.JSON()),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True)),
        sa.Column("file_path", sa.String(length=255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "tr_report_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("report_id", sa.Integer(), sa.ForeignKey("tr_reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("requested_by", sa.Integer(), sa.ForeignKey("tr_users.id"), nullable=False),
        sa.Column("schedule_cron", sa.String(length=64)),
        sa.Column("last_run_at", sa.DateTime(timezone=True)),
        sa.Column("next_run_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "tr_risk_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("tr_orders.id")),
        sa.Column("position_id", sa.Integer(), sa.ForeignKey("tr_positions.id")),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("before_sl", sa.Float()),
        sa.Column("after_sl", sa.Float()),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column("context_json", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("tr_risk_events")
    op.drop_table("tr_report_jobs")
    op.drop_table("tr_reports")
    op.drop_index("ix_audit_created", table_name="tr_audit_logs")
    op.drop_table("tr_audit_logs")
    op.drop_table("tr_mc_runs")
    op.drop_table("tr_backtests")
    op.drop_table("tr_models")
    op.drop_index("ix_predictions_symbol_tf", table_name="tr_predictions")
    op.drop_table("tr_predictions")
    op.drop_table("tr_pnl_daily")
    op.drop_table("tr_executions")
    op.drop_index("ix_positions_symbol", table_name="tr_positions")
    op.drop_table("tr_positions")
    op.drop_index("ix_orders_oanda_id", table_name="tr_orders")
    op.drop_index("ix_orders_symbol", table_name="tr_orders")
    op.drop_table("tr_orders")
    op.drop_index("ix_alert_symbol_tf", table_name="tr_alerts")
    op.drop_table("tr_alerts")
    op.drop_table("tr_strategies")
    op.drop_table("tr_accounts")
    op.drop_table("tr_api_keys")
    op.drop_table("tr_sessions")
    op.drop_table("tr_users")
    sa.Enum(name="role_enum").drop(op.get_bind(), checkfirst=False)
    sa.Enum(name="side_enum").drop(op.get_bind(), checkfirst=False)
    sa.Enum(name="order_type_enum").drop(op.get_bind(), checkfirst=False)
    sa.Enum(name="account_env_enum").drop(op.get_bind(), checkfirst=False)
    sa.Enum(name="model_type_enum").drop(op.get_bind(), checkfirst=False)
