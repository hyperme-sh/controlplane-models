import importlib.util
import json
from pathlib import Path
import shutil

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('protocol_fixture', ROOT/'scripts/verify_protocol_fixture.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


@pytest.fixture
def root(tmp_path):
    shutil.copytree(ROOT/'tests_artifacts',tmp_path/'tests_artifacts')
    for name in ['pyproject.toml','uv.lock']:shutil.copyfile(ROOT/name,tmp_path/name)
    return tmp_path


def test_real_fixture_matches_dependency_and_lock(root):
    assert module.verify(root).name == 'controlplane_proto-0.2.0-py3-none-any.whl'


def test_modified_artifact_fails(root):
    wheel = module.verify(root); wheel.write_bytes(wheel.read_bytes()+b'tampered')
    with pytest.raises(ValueError,match='digest'):module.verify(root)


@pytest.mark.parametrize('name',['pyproject.toml','uv.lock'])
def test_dependency_revision_change_requires_new_fixture(root,name):
    manifest=json.loads((root/'tests_artifacts/protocol/manifest.json').read_text())
    p=root/name;p.write_text(p.read_text().replace(manifest['dependency_revision'],'a'*40))
    with pytest.raises(ValueError,match='dependency'):module.verify(root)


def test_missing_fixture_fails(root):
    module.verify(root).unlink()
    with pytest.raises(FileNotFoundError):module.verify(root)


def test_fixture_cannot_escape_directory(root):
    p=root/'tests_artifacts/protocol/manifest.json';record=json.loads(p.read_text());record['wheel']='../outside.whl';p.write_text(json.dumps(record))
    with pytest.raises(ValueError,match='directory'):module.verify(root)
