"""LLM / agent usage and budget contracts (distinct from on-chain CryptoBudget)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator

from spanopticon_models._config import model_config_contracts


class AIModel(BaseModel):
    """Reference pricing for a provider model (for metering / quotes)."""

    model_config = model_config_contracts

    provider: str = Field(..., min_length=1, max_length=64)
    model_name: str = Field(..., min_length=1, max_length=256)
    cost_per_1k_input: Decimal = Field(..., ge=0, description="USD per 1k input tokens")
    cost_per_1k_output: Decimal = Field(..., ge=0, description="USD per 1k output tokens")

    @field_validator("cost_per_1k_input", "cost_per_1k_output", mode="before")
    @classmethod
    def decimal_coerce(cls, v: object) -> object:
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        return v


class TokenUsage(BaseModel):
    """One inference call usage record."""

    model_config = model_config_contracts

    user_id: uuid.UUID
    tenant_id: uuid.UUID
    model: str = Field(..., min_length=1, max_length=256)
    input_tokens: int = Field(..., ge=0)
    output_tokens: int = Field(..., ge=0)
    cost: Decimal = Field(..., ge=0, description="Charged amount in USD")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("cost", mode="before")
    @classmethod
    def cost_decimal(cls, v: object) -> object:
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        return v

    @field_validator("timestamp")
    @classmethod
    def timestamp_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return v


class AgentBudget(BaseModel):
    """Spend cap for LLM/agent usage (fiat minor units), not Solana lamports — see CryptoBudget."""

    model_config = model_config_contracts

    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID | None = Field(
        default=None,
        description="None = tenant-wide pool; set for per-user caps",
    )
    label: str | None = Field(default=None, max_length=255)
    currency: str = Field(default="usd", min_length=3, max_length=3, pattern=r"^[a-z]{3}$")
    ceiling_cents: int = Field(..., ge=0, description="Max spend in minor units")
    spent_cents: int = Field(..., ge=0)

    @field_validator("currency", mode="before")
    @classmethod
    def currency_lower(cls, v: object) -> object:
        if isinstance(v, str):
            return v.lower()
        return v

    @model_validator(mode="after")
    def spent_within_ceiling(self) -> AgentBudget:
        if self.spent_cents > self.ceiling_cents:
            raise ValueError("spent_cents cannot exceed ceiling_cents")
        return self
