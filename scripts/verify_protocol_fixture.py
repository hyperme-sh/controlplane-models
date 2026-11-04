"""Verify the real protocol fixture against the immutable dependency and lockfile."""
import email.parser
import hashlib
import json
from pathlib import Path
import sys
import tomllib
import zipfile


def verify(root):
    root = Path(root)
    directory = root / 'tests_artifacts/protocol'
    record = json.loads((directory / 'manifest.json').read_text())
    project = tomllib.loads((root / 'pyproject.toml').read_text())
    lock = tomllib.loads((root / 'uv.lock').read_text())
    expected = 'controlplane-proto @ git+https://github.com/hyperme-sh/controlplane-proto.git@' + record['dependency_revision']
    if project['project']['optional-dependencies']['grpc'].count(expected) != 1:
        raise ValueError('Protocol fixture does not match declared dependency revision')
    entries = [p for p in lock['package'] if p['name'] == 'controlplane-proto']
    git = 'https://github.com/hyperme-sh/controlplane-proto.git?rev=' + record['dependency_revision'] + '#' + record['dependency_revision']
    if len(entries) != 1 or entries[0]['version'] != record['version'] or entries[0]['source'] != {'git': git}:
        raise ValueError('Protocol fixture does not match locked dependency')
    name = record['wheel']
    if Path(name).name != name or not name.endswith('.whl'):
        raise ValueError('Fixture must be a wheel in the fixture directory')
    wheel = directory / name
    if hashlib.sha256(wheel.read_bytes()).hexdigest() != record['sha256']:
        raise ValueError('Protocol fixture digest mismatch')
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        metadata = [n for n in names if n.endswith('.dist-info/METADATA')]
        if len(names) != len(set(names)) or len(metadata) != 1:
            raise ValueError('Ambiguous protocol wheel contents')
        info = email.parser.BytesParser().parsebytes(archive.read(metadata[0]))
        if info.get_all('Name') != ['controlplane-proto'] or info.get_all('Version') != [record['version']]:
            raise ValueError('Protocol wheel metadata differs from fixture')
    return wheel.resolve()


if __name__ == '__main__':
    print(verify(sys.argv[1]))
