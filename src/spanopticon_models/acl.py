from __future__ import annotations

import uuid
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from spanopticon_models._config import model_config_contracts


class PoliticalViewCategory(str, Enum):
    """Coarse, opt-in self-description for policy context (handle as sensitive data)."""

    UNSPECIFIED = "unspecified"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"
    OTHER = "other"


class SexualOrientationCategory(str, Enum):
    """Opt-in category; treat as special-category personal data under GDPR."""

    UNSPECIFIED = "unspecified"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"
    OTHER = "other"


class SociACLAttributes(BaseModel):
    """Optional SociACL dimensions attached to a policy. Highly sensitive — minimize collection."""

    model_config = model_config_contracts

    political_view: PoliticalViewCategory | None = None
    sexual_orientation: SexualOrientationCategory | None = None
    verification_level: int | None = Field(
        default=None,
        ge=0,
        le=4,
        description="0=none .. 4=strong identity assurance",
    )
    notes: str | None = Field(
        default=None,
        max_length=500,
        description="Internal policy notes; avoid PII.",
    )


class ACLPolicy(BaseModel):
    """Abstract ACL rule with optional SociACL predicates."""

    model_config = model_config_contracts

    id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255)
    effect: Literal["allow", "deny"]
    resource_pattern: str = Field(..., min_length=1, max_length=512)
    action: str = Field(..., min_length=1, max_length=128)
    sociacl: SociACLAttributes | None = None

    @field_validator("resource_pattern")
    @classmethod
    def resource_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("resource_pattern cannot be blank")
        return v
