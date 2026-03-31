from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from panopticon_models._config import model_config_contracts

PaymentIntentStatus = Literal[
    "requires_payment_method",
    "processing",
    "succeeded",
    "canceled",
]


class PaymentIntent(BaseModel):
    """Stripe-aligned payment intent contract for events and APIs."""

    model_config = model_config_contracts

    id: uuid.UUID
    amount_cents: int = Field(..., gt=0, le=999_999_999_999)
    currency: str = Field(..., min_length=3, max_length=3, pattern=r"^[a-z]{3}$")
    status: PaymentIntentStatus
    stripe_payment_intent_id: str | None = Field(default=None, max_length=255)
    tenant_id: uuid.UUID | None = None

    @field_validator("currency", mode="before")
    @classmethod
    def currency_lowercase(cls, v: object) -> object:
        if isinstance(v, str):
            return v.lower()
        return v
