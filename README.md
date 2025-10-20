# AI Trading Assistance Platform

This repository provides a local-first scaffold for an automated OANDA trading system driven by TradingView HullSuite alerts, predictive modeling, and Monte Carlo risk management.

## Features

- **FastAPI backend** with JWT auth, webhook security (HMAC + timestamp + nonce), and modular routers.
- **MariaDB/MySQL schema** with Alembic migrations covering users, strategies, alerts, orders, predictions, Monte Carlo runs, and audit trails.
- **Prediction and risk services** exposing extensible interfaces for PyTorch ensembles and GBM Monte Carlo simulation.
- **React + Tailwind UI** delivering an enterprise-style dashboard, risk views, and account management pages in responsive dark mode.
- **Docker Compose** stack for local development with MariaDB, backend API, and UI.
- **Structured JSON logging**, health/metrics endpoints, and unit tests for security-critical paths.

## Getting Started

1. Copy `.env.example` to `.env` and customize secrets.
2. Launch the stack:
   ```bash
   docker-compose up --build
   ```
3. Run database migrations inside the backend container:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```
4. (Optional) Seed demo data:
   ```bash
   docker-compose exec backend python -m app.db.seed
   ```
5. Access the API docs at `http://localhost:8000/docs` and the UI at `http://localhost:5173`.

## Testing

Run unit tests locally with:

```bash
cd backend
pytest
```

## Documentation

- [`docs/runbook.md`](docs/runbook.md) – operational guide.
- [`docs/erd.md`](docs/erd.md) – data model overview.
- [`docs/sequence_tradingview.md`](docs/sequence_tradingview.md) – webhook processing sequence.
- [`docs/assumptions.md`](docs/assumptions.md) – explicit design assumptions.