from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr, Field

from panopticon_models._config import model_config_contracts


class SharedUser(BaseModel):
    """Cross-service user contract (not the SQLAlchemy ORM row)."""

    model_config = model_config_contracts

    id: uuid.UUID
    email: EmailStr
    display_name: str = Field(..., min_length=1, max_length=255)
    tenant_id: uuid.UUID | None = None
