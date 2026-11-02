"""gRPC-oriented Pydantic ``Message`` types (protobuf-friendly: string IDs, JSON blobs)."""

from datetime import datetime

from pydantic_rpc import Message


class UserWire(Message):
    """Wire shape for :class:`panopticon_models.user.SharedUser`."""

    id: str
    email: str
    display_name: str
    tenant_id: str | None = None


class ListingWire(Message):
    """Wire shape for :class:`panopticon_models.marketplace.Listing` (metadata as JSON text)."""

    id: str
    tenant_id: str
    seller_id: str
    title: str
    description: str = ""
    listing_type: str
    price_type: str
    price_amount: int | None = None
    metadata_json: str = "{}"
    sku: str | None = None


class TokenUsageWire(Message):
    """Wire shape for :class:`panopticon_models.ai_metering.TokenUsage` (cost as decimal string)."""

    user_id: str
    tenant_id: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: str = "0"
    timestamp: datetime
