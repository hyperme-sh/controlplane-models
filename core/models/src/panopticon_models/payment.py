from __future__ import annotations

import uuid
from datetime import datetime
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


class StripeCheckoutSessionCreate(BaseModel):
    """POST /payments/stripe/checkout-sessions"""

    model_config = model_config_contracts

    mode: Literal["subscription", "payment"] = "payment"
    price_id: str = Field(..., min_length=1, max_length=255)
    success_url: str = Field(..., min_length=8, max_length=2048)
    cancel_url: str = Field(..., min_length=8, max_length=2048)


class StripeCheckoutSessionResponse(BaseModel):
    model_config = model_config_contracts

    stripe_session_id: str = Field(..., max_length=255)
    billing_record_id: uuid.UUID
    checkout_url: str | None = Field(
        default=None,
        max_length=4096,
        description="Stripe-hosted checkout URL (redirect the browser here).",
    )


class BillingRecordReadResponse(BaseModel):
    """GET /payments/billing-records and GET /payments/billing-records/{billing_record_id}"""

    model_config = model_config_contracts

    id: uuid.UUID
    status: str = Field(..., max_length=64)
    amount: int | None = Field(default=None, ge=0)
    currency: str = Field(default="usd", max_length=8)
    payment_type: str = Field(..., max_length=64)
    extra_metadata: dict = Field(default_factory=dict)
    stripe_session_id: str | None = Field(default=None, max_length=255)
    created_at: datetime | None = None


class CryptoBudgetCreateRequest(BaseModel):
    """Create an in-app Solana-style budget envelope (pubkeys only; no private keys stored)."""

    model_config = model_config_contracts

    ceiling_lamports: int = Field(..., ge=0, le=2**63 - 1)
    mint_pubkey: str = Field(..., min_length=32, max_length=64)
    label: str | None = Field(default=None, max_length=255)


class BudgetAllocateRequest(BaseModel):
    model_config = model_config_contracts

    delta_lamports: int = Field(..., ge=1)


class CryptoBudgetResponse(BaseModel):
    model_config = model_config_contracts

    id: uuid.UUID
    owner_pubkey: str
    mint_pubkey: str
    ceiling_lamports: int
    allocated_lamports: int
    label: str | None = None
