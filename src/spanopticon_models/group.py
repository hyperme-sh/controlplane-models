from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from spanopticon_models._config import model_config_contracts


class SharedGroup(BaseModel):
    """Logical group within a tenant."""

    model_config = model_config_contracts

    id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255)
    tenant_id: uuid.UUID
    description: str | None = Field(default=None, max_length=2000)
