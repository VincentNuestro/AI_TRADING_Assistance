# Runbook

## Local Development

1. Copy `.env.example` to `.env` and adjust secrets.
2. Start services:
   ```bash
   docker-compose up --build
   ```
3. Apply migrations:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```
4. Seed demo data (placeholder script to be implemented) or register via `/auth/register`.
5. Access API docs at `http://localhost:8000/docs` and the UI at `http://localhost:5173`.

## Health Checks
- `GET /healthz` for application liveness.
- `GET /metrics` for Prometheus scraping.

## Alert Handling Flow
1. TradingView sends HullSuite alert to `/webhook/tradingview` with signed headers.
2. API validates HMAC, timestamp, and nonce.
3. Alert is persisted with idempotency guard.
4. Prediction ensemble and Monte Carlo modules provide gating decisions.
5. Risk engine returns PASS/DOWNSIZE/BLOCK with ATR-based SL/TP.
6. OANDA client executes close-then-open order when decision is PASS or DOWNSIZE.
7. All actions are logged via structured JSON logs and stored in `tr_audit_logs`.

## Troubleshooting
- **Invalid signature**: Verify `WEBHOOK_SECRET` matches TradingView configuration.
- **Database connectivity**: Ensure MariaDB container is running and credentials match `.env`.
- **Model unavailability**: System defaults to BLOCK decision when prediction service errors; review logs for stack trace.
- **Rate limiting**: Login and webhook endpoints are protected; repeated errors may indicate brute-force attempts.
