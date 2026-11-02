"""Map domain models to/from generated ``contractecho_pb2`` messages (binary protobuf)."""

from __future__ import annotations

import json
import importlib

from google.protobuf.timestamp_pb2 import Timestamp

from panopticon_models.ai_metering import TokenUsage
from panopticon_models.marketplace import Listing
from panopticon_models.user import SharedUser


def _pb2_mod():
    """Load the explicitly installed protocol component, without filesystem search."""
    return importlib.import_module("contractecho_pb2")


def shared_user_to_pb2(u: SharedUser):
    m = _pb2_mod()
    msg = m.UserWire()
    msg.id = str(u.id)
    msg.email = str(u.email)
    msg.display_name = u.display_name
    if u.tenant_id is not None:
        msg.tenant_id = str(u.tenant_id)
    return msg


def shared_user_from_pb2(msg) -> SharedUser:
    import uuid

    tid: str | None = msg.tenant_id if msg.HasField("tenant_id") else None
    return SharedUser(
        id=uuid.UUID(msg.id),
        email=msg.email,
        display_name=msg.display_name,
        tenant_id=uuid.UUID(tid) if tid else None,
    )


def listing_to_pb2(l: Listing):
    m = _pb2_mod()
    msg = m.ListingWire()
    msg.id = str(l.id)
    msg.tenant_id = str(l.tenant_id)
    msg.seller_id = str(l.seller_id)
    msg.title = l.title
    msg.description = l.description
    msg.listing_type = l.type.value
    msg.price_type = l.price_type.value
    if l.price_amount is not None:
        msg.price_amount = int(l.price_amount)
    msg.metadata_json = json.dumps(l.metadata, sort_keys=True)
    if l.sku is not None:
        msg.sku = l.sku
    return msg


def listing_from_pb2(msg) -> Listing:
    import uuid

    from panopticon_models.marketplace import Listing, ListingType, PriceType

    meta: dict = {}
    if msg.metadata_json:
        try:
            meta = json.loads(msg.metadata_json)
            if not isinstance(meta, dict):
                meta = {}
        except json.JSONDecodeError:
            meta = {}
    pa = msg.price_amount if msg.HasField("price_amount") else None
    sku = msg.sku if msg.HasField("sku") else None
    return Listing(
        id=uuid.UUID(msg.id),
        tenant_id=uuid.UUID(msg.tenant_id),
        seller_id=uuid.UUID(msg.seller_id),
        title=msg.title,
        description=msg.description,
        type=ListingType(msg.listing_type),
        price_type=PriceType(msg.price_type),
        price_amount=pa,
        metadata=meta,
        sku=sku,
    )


def token_usage_to_pb2(t: TokenUsage):
    m = _pb2_mod()
    msg = m.TokenUsageWire()
    msg.user_id = str(t.user_id)
    msg.tenant_id = str(t.tenant_id)
    msg.model = t.model
    msg.input_tokens = int(t.input_tokens)
    msg.output_tokens = int(t.output_tokens)
    msg.cost_usd = format(t.cost, "f")
    ts = Timestamp()
    ts.FromDatetime(t.timestamp)
    msg.timestamp.CopyFrom(ts)
    return msg


def token_usage_from_pb2(msg) -> TokenUsage:
    import uuid
    from datetime import timezone
    from decimal import Decimal

    from panopticon_models.ai_metering import TokenUsage

    ts = msg.timestamp.ToDatetime()
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return TokenUsage(
        user_id=uuid.UUID(msg.user_id),
        tenant_id=uuid.UUID(msg.tenant_id),
        model=msg.model,
        input_tokens=int(msg.input_tokens),
        output_tokens=int(msg.output_tokens),
        cost=Decimal(msg.cost_usd),
        timestamp=ts,
    )
