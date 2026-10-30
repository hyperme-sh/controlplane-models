from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from panopticon_models._config import model_config_contracts


class SharedTenant(BaseModel):
    """Cross-service tenant contract (not the SQLAlchemy ORM row)."""

    model_config = model_config_contracts

    id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(
        ...,
        min_length=1,
        max_length=128,
        pattern=r"^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$",
    )
    is_active: bool = True
