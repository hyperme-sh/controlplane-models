import importlib.metadata

def test_grpc_dependency_retains_immutable_protocol_reference():
    requirements = importlib.metadata.requires('panopticon-models')
    protocol = [r for r in requirements if r.lower().startswith('controlplane-proto')]
    assert len(protocol) == 1
    assert 'git+ssh://git@github.com/hyperme-sh/controlplane-proto.git@718c5f4dd552446204ac4a0af1c106ae0cbbb8f8' in protocol[0]
    assert 'grpc' in protocol[0]
