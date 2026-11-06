from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from spanopticon_models._config import model_config_contracts

MIN_STABLECOIN_CHARGE_CENTS = 50
MAX_STABLECOIN_CHARGE_CENTS = 1_000_000

PaymentIntentStatus = Literal[
    "requires_payment_method",
    "processing",
    "succeeded",
    "canceled",
]


class PaymentIntent(BaseModel):
    """Provider-neutral payment intent contract for events and APIs."""

    model_config = model_config_contracts

    id: uuid.UUID
    amount_cents: int = Field(..., gt=0, le=999_999_999_999)
    currency: str = Field(..., min_length=3, max_length=3, pattern=r"^[a-z]{3}$")
    status: PaymentIntentStatus
    processor_reference: str | None = Field(default=None, max_length=255)
    tenant_id: uuid.UUID | None = None

    @field_validator("currency", mode="before")
    @classmethod
    def currency_lowercase(cls, v: object) -> object:
        if isinstance(v, str):
            return v.lower()
        return v


class UsdcLeasePaymentCreate(BaseModel):
    """POST /payments/usdc/lease-payments

    Opens a pending USDC payment for one lease. The price clears 1:1 from
    USD cents into USDC atoms. No card is involved.
    """

    model_config = model_config_contracts

    amount_cents: int = Field(
        ...,
        ge=MIN_STABLECOIN_CHARGE_CENTS,
        le=MAX_STABLECOIN_CHARGE_CENTS,
        description="Total USD cents: $0.50–$10,000.00 inclusive",
    )

    @field_validator("amount_cents", mode="before")
    @classmethod
    def validate_charge_range(cls, value):
        if isinstance(value, int) and not isinstance(value, bool):
            if value < MIN_STABLECOIN_CHARGE_CENTS:
                raise ValueError(
                    "Lease total is below the $0.50 minimum; allowed range is $0.50–$10,000.00 USD"
                )
            if value > MAX_STABLECOIN_CHARGE_CENTS:
                raise ValueError(
                    "Lease total exceeds the $10,000.00 maximum; allowed range is $0.50–$10,000.00 USD"
                )
        return value

    listing_id: uuid.UUID | None = Field(
        default=None,
        description=(
            "Marketplace listing this payment buys. The server writes it to "
            "billing extra_metadata.listing_id, which marketplace purchase "
            "checks. A listing_id key in metadata is ignored."
        ),
    )
    metadata: dict[str, str] | None = Field(
        default=None,
        description=(
            "Optional string map copied onto billing extra_metadata. "
            "Platform keys tenant_id and payment_rail win. lease_id and "
            "listing_id from a browser client are ignored. Do not send secrets."
        ),
    )

    @field_validator("metadata")
    @classmethod
    def metadata_is_safe(cls, value: dict[str, str] | None) -> dict[str, str] | None:
        if value is None:
            return None
        if len(value) > 16:
            raise ValueError("metadata has at most 16 keys")
        blocked = ("secret", "token", "password", "api_key", "private")
        cleaned: dict[str, str] = {}
        for key, item in value.items():
            if len(key) > 40 or len(item) > 500:
                raise ValueError("metadata key or value is too long")
            folded = key.lower()
            if any(part in folded for part in blocked):
                raise ValueError("metadata must not include secrets")
            cleaned[key] = item
        return cleaned


UsdcLeasePaymentStatus = Literal["pending", "succeeded", "refunded", "failed"]


class UsdcLeasePaymentResponse(BaseModel):
    """A USDC lease payment. ``amount_atoms`` has 6 decimals."""

    model_config = model_config_contracts

    billing_record_id: uuid.UUID
    status: str = Field(..., max_length=64)
    amount_cents: int = Field(..., ge=0)
    amount_atoms: int = Field(
        ...,
        ge=0,
        description="USDC atoms (6 decimals). 64-bit: large payments exceed 32 bits.",
        json_schema_extra={"format": "int64"},
    )
    chain_id: int | None = Field(
        default=None,
        description="Base chain id from deployment config, when set.",
    )
    test_credit_available: bool = Field(
        default=False,
        description=(
            "True only where PAYMENTS_USDC_TEST_CREDIT_ENABLED is set and the "
            "configured processor and network are in test mode. The renter may "
            "then settle this payment from a test-network credit."
        ),
    )








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
