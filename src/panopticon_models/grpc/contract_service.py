"""Minimal service class for pydantic-rpc CLI ``generate`` (echo unary RPCs for contract messages)."""

from panopticon_models.grpc.wire import ListingWire, TokenUsageWire, UserWire


class ContractEcho:
    """Unused at runtime except for protobuf generation; methods return requests unchanged."""

    def echo_user(self, request: UserWire) -> UserWire:
        return request

    def echo_listing(self, request: ListingWire) -> ListingWire:
        return request

    def echo_token_usage(self, request: TokenUsageWire) -> TokenUsageWire:
        return request
