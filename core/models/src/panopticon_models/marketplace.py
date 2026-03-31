"""Marketplace listing, purchase, and review contracts (shared across services)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from panopticon_models._config import model_config_contracts


class ListingType(StrEnum):
    PLUGIN = "plugin"
    AGENT = "agent"
    CONFIG = "config"
    HARDWARE = "hardware"


class PriceType(StrEnum):
    FREE = "free"
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"
    USAGE = "usage"


class PurchaseStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Listing(BaseModel):
    """Sellable item in the control-plane marketplace."""

    model_config = model_config_contracts

    id: uuid.UUID
    tenant_id: uuid.UUID
    seller_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=512)
    description: str = Field(default="", max_length=32_768)
    type: ListingType
    price_type: PriceType
    price_amount: int | None = Field(
        default=None,
        description="Minor units (e.g. cents) when priced; null for free",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def price_consistent_with_type(self) -> Listing:
        if self.price_type == PriceType.FREE:
            if self.price_amount is not None and self.price_amount != 0:
                raise ValueError("price_amount must be null or 0 when price_type is free")
        else:
            if self.price_amount is None or self.price_amount < 0:
                raise ValueError("price_amount required and non-negative when not free")
        return self


class Purchase(BaseModel):
    """A buyer acquiring a listing (license issuance)."""

    model_config = model_config_contracts

    id: uuid.UUID
    listing_id: uuid.UUID
    buyer_id: uuid.UUID
    tenant_id: uuid.UUID
    status: PurchaseStatus
    license_key: str | None = Field(default=None, max_length=512)


class Review(BaseModel):
    """Buyer/seller feedback on a listing."""

    model_config = model_config_contracts

    id: uuid.UUID
    tenant_id: uuid.UUID
    listing_id: uuid.UUID
    reviewer_id: uuid.UUID
    rating: int = Field(..., ge=1, le=5)
    text: str = Field(default="", max_length=16_384)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("created_at")
    @classmethod
    def created_at_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
        return v
