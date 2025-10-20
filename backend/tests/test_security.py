from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.utils.security import validate_timestamp, verify_hmac_signature
from app.core.config import settings


def test_validate_timestamp_within_window(monkeypatch):
    now = datetime.now(timezone.utc)
    assert validate_timestamp(now.isoformat())


def test_validate_timestamp_outside_window(monkeypatch):
    past = datetime.now(timezone.utc) - timedelta(minutes=10)
    assert not validate_timestamp(past.isoformat())


def test_verify_hmac_signature():
    body = b"{\"foo\": \"bar\"}"
    import hashlib
    import hmac

    expected = hmac.new(settings.webhook_secret.encode(), body, hashlib.sha256).hexdigest()
    assert verify_hmac_signature(body, expected)
