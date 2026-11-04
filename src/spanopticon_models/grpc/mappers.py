"""Map domain ``spanopticon_models`` DTOs to/from gRPC wire messages."""

from __future__ import annotations

import json
import uuid
from decimal import Decimal
from typing import Any

from spanopticon_models.ai_metering import TokenUsage
from spanopticon_models.marketplace import Listing, ListingType, PriceType
from spanopticon_models.user import SharedUser
from spanopticon_models.grpc.wire import ListingWire, TokenUsageWire, UserWire


def user_to_wire(u: SharedUser) -> UserWire:
    return UserWire(
        id=str(u.id),
        email=str(u.email),
        display_name=u.display_name,
        tenant_id=str(u.tenant_id) if u.tenant_id is not None else None,
    )


def user_from_wire(w: UserWire) -> SharedUser:
    return SharedUser(
        id=uuid.UUID(w.id),
        email=w.email,  # type: ignore[arg-type]
        display_name=w.display_name,
        tenant_id=uuid.UUID(w.tenant_id) if w.tenant_id else None,
    )


def listing_to_wire(l: Listing) -> ListingWire:
    return ListingWire(
        id=str(l.id),
        tenant_id=str(l.tenant_id),
        seller_id=str(l.seller_id),
        title=l.title,
        description=l.description,
        listing_type=l.type.value,
        price_type=l.price_type.value,
        price_amount=l.price_amount,
        metadata_json=json.dumps(l.metadata, sort_keys=True),
        sku=l.sku,
    )


def listing_from_wire(w: ListingWire) -> Listing:
    meta: dict[str, Any] = {}
    if w.metadata_json:
        try:
            meta = json.loads(w.metadata_json)
            if not isinstance(meta, dict):
                meta = {}
        except json.JSONDecodeError:
            meta = {}
    return Listing(
        id=uuid.UUID(w.id),
        tenant_id=uuid.UUID(w.tenant_id),
        seller_id=uuid.UUID(w.seller_id),
        title=w.title,
        description=w.description or "",
        type=ListingType(w.listing_type),
        price_type=PriceType(w.price_type),
        price_amount=w.price_amount,
        metadata=meta,
        sku=w.sku,
    )


def token_usage_to_wire(t: TokenUsage) -> TokenUsageWire:
    return TokenUsageWire(
        user_id=str(t.user_id),
        tenant_id=str(t.tenant_id),
        model=t.model,
        input_tokens=t.input_tokens,
        output_tokens=t.output_tokens,
        cost_usd=format(t.cost, "f"),
        timestamp=t.timestamp,
    )


def token_usage_from_wire(w: TokenUsageWire) -> TokenUsage:
    return TokenUsage(
        user_id=uuid.UUID(w.user_id),
        tenant_id=uuid.UUID(w.tenant_id),
        model=w.model,
        input_tokens=w.input_tokens,
        output_tokens=w.output_tokens,
        cost=Decimal(w.cost_usd),
        timestamp=w.timestamp,
    )
