# Assumptions

- The local development environment uses SQLite for unit testing while production uses MariaDB/MySQL as defined in `.env`.
- Prediction and risk engines return deterministic placeholder outputs until real models are integrated. Interfaces were designed to allow drop-in replacement.
- Webhook nonce storage uses an in-memory cache for the prototype; production should persist to a fast datastore (e.g., Redis) to guarantee uniqueness across instances.
- UI authentication flow assumes JWT-based login; token storage and refresh will be completed during hardening.
- OANDA client is mocked for local-first mode to avoid live order placement. Real API integration will enforce retries, circuit breaking, and idempotency keys.
