import importlib.metadata

def test_grpc_dependency_retains_immutable_protocol_reference():
    requirements = importlib.metadata.requires('spanopticon-models')
    protocol = [r for r in requirements if r.lower().startswith('controlplane-proto')]
    assert len(protocol) == 1
    assert 'git+https://github.com/hyperme-sh/controlplane-proto.git@438e7ad97168bf8bf12b93885ce6f7a889b46cd1' in protocol[0]
    assert 'grpc' in protocol[0]
