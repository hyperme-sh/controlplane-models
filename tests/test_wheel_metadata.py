import importlib.metadata

def test_grpc_dependency_retains_immutable_protocol_reference():
    requirements = importlib.metadata.requires('spanopticon-models')
    protocol = [r for r in requirements if r.lower().startswith('controlplane-proto')]
    assert len(protocol) == 1
    assert 'git+https://github.com/hyperme-sh/controlplane-proto.git@db0c3b6b2359ec5a3a3792e0a2ec00d4c9c38db9' in protocol[0]
    assert 'grpc' in protocol[0]
