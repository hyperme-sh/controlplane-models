"""Original wire roundtrips, enabled when the explicit grpc extra is installed."""
import uuid
from datetime import UTC,datetime
from decimal import Decimal
import pytest
pytest.importorskip('contractecho_pb2', reason='Install the grpc extra for protocol integration checks')

def test_shared_user_pb2_roundtrip() -> None:
    from spanopticon_models.grpc.pb2_convert import shared_user_from_pb2, shared_user_to_pb2
    from spanopticon_models.user import SharedUser

    u = SharedUser(
        id=uuid.uuid4(),
        email="a@b.com",
        display_name="Test",
        tenant_id=None,
    )
    pb = shared_user_to_pb2(u)
    raw = pb.SerializeToString()
    u2 = shared_user_from_pb2(type(pb).FromString(raw))
    assert u2.id == u.id
    assert u2.email == u.email
    assert u2.display_name == u.display_name
    assert u2.tenant_id is None

def test_listing_pb2_roundtrip() -> None:
    from spanopticon_models.grpc.pb2_convert import listing_from_pb2, listing_to_pb2
    from spanopticon_models.marketplace import Listing, ListingType, PriceType

    lid = uuid.uuid4()
    tid = uuid.uuid4()
    sid = uuid.uuid4()
    l = Listing(
        id=lid,
        tenant_id=tid,
        seller_id=sid,
        title="Item",
        description="Desc",
        type=ListingType.PLUGIN,
        price_type=PriceType.ONE_TIME,
        price_amount=1234,
        sku="SKU-1",
        metadata={"k": "v"},
    )
    pb = listing_to_pb2(l)
    l2 = listing_from_pb2(type(pb).FromString(pb.SerializeToString()))
    assert l2.id == l.id
    assert l2.title == l.title
    assert l2.price_amount == l.price_amount
    assert l2.sku == l.sku
    assert l2.metadata == l.metadata
    assert l2.tenant_id == l.tenant_id

def test_token_usage_pb2_roundtrip() -> None:
    from spanopticon_models.ai_metering import TokenUsage
    from spanopticon_models.grpc.pb2_convert import token_usage_from_pb2, token_usage_to_pb2

    uid = uuid.uuid4()
    tenant_id = uuid.uuid4()
    t = TokenUsage(
        user_id=uid,
        tenant_id=tenant_id,
        model="gpt-4",
        input_tokens=10,
        output_tokens=20,
        cost=Decimal("0.001"),
        timestamp=datetime(2025, 1, 2, 3, 4, 5, tzinfo=UTC),
    )
    pb = token_usage_to_pb2(t)
    t2 = token_usage_from_pb2(type(pb).FromString(pb.SerializeToString()))
    assert t2.user_id == t.user_id
    assert t2.tenant_id == t.tenant_id
    assert t2.cost == t.cost
    assert t2.timestamp == t.timestamp

def test_converter_does_not_search_an_ancestor_checkout(monkeypatch):
    from spanopticon_models.grpc import pb2_convert
    assert not hasattr(pb2_convert, '_proto_stubs_dir')
    assert pb2_convert._pb2_mod().__name__ == 'contractecho_pb2'


@pytest.mark.parametrize('tenant_id', [None, uuid.UUID('ba18a632-39e1-44f7-9f45-09739a55bcb2')])
def test_installed_client_server_and_model_roundtrip(tenant_id):
    """Exercise generated service routing and model presence over real loopback RPC."""
    from concurrent.futures import ThreadPoolExecutor
    import grpc
    import contractecho_pb2 as pb
    import contractecho_pb2_grpc as rpc
    from spanopticon_models.grpc.pb2_convert import shared_user_from_pb2, shared_user_to_pb2
    from spanopticon_models.user import SharedUser

    assert pb.DESCRIPTOR.package == 'spanopticon.v1'

    class Echo(rpc.ContractEchoServicer):
        def EchoUser(self, request, context):
            return request

    with ThreadPoolExecutor(max_workers=1) as workers:
        server = grpc.server(workers)
        rpc.add_ContractEchoServicer_to_server(Echo(), server)
        port = server.add_insecure_port('127.0.0.1:0')
        assert port != 0
        server.start()
        try:
            with grpc.insecure_channel(f'127.0.0.1:{port}') as channel:
                user = SharedUser(id=uuid.uuid4(), email='rpc@example.com', display_name='RPC', tenant_id=tenant_id)
                reply = rpc.ContractEchoStub(channel).EchoUser(shared_user_to_pb2(user), timeout=5)
                assert reply.HasField('tenant_id') is (tenant_id is not None)
                assert shared_user_from_pb2(reply) == user
        finally:
            assert server.stop(grace=0).wait(timeout=5)
