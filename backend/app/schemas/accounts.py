from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AccountBase(BaseModel):
    user_id: int
    oanda_account_id: str
    env: str
    label: str
    is_default: bool = False


class AccountCreate(AccountBase):
    pass


class AccountPublic(AccountBase):
    id: int
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_health_ts: datetime | None = None

    model_config = {
        "from_attributes": True,
    }
