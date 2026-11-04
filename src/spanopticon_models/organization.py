from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from spanopticon_models._config import model_config_contracts


class SharedOrganization(BaseModel):
    """Legal / billing organization linked to a tenant."""

    model_config = model_config_contracts

    id: uuid.UUID
    legal_name: str = Field(..., min_length=1, max_length=512)
    tenant_id: uuid.UUID
