#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"
unset PYTHONPATH UV_NO_SYNC
extras=()
export_options=()
sync_options=()
run_options=()
fixture_wheel=
case "${1:-}" in
  '') ;;
  --grpc) extras=(--extra grpc); export_options=(--no-emit-package controlplane-proto) ;;
  --grpc-fixture) extras=(--extra grpc); export_options=(--no-emit-package controlplane-proto); sync_options=(--no-install-package controlplane-proto); run_options=(--no-sync) ;;
  *) echo 'Usage: bash scripts/check.sh [--grpc|--grpc-fixture]' >&2; exit 2 ;;
esac
if (( $# > 1 )); then echo 'Unexpected arguments' >&2; exit 2; fi
uv sync --frozen "${extras[@]}" "${sync_options[@]}"
if [[ "${1:-}" == --grpc-fixture ]]; then
  fixture_wheel=$(uv run --no-sync python scripts/verify_protocol_fixture.py "$root")
  uv pip install --python "$root/.venv/bin/python" --no-deps --reinstall "$fixture_wheel"
fi
if (( ${#extras[@]} )); then
  # Unlike the base test lane, the integration lane may not skip a missing proto.
  uv run --frozen "${extras[@]}" "${run_options[@]}" python -c 'import contractecho_pb2; assert contractecho_pb2.DESCRIPTOR.package == "spanopticon.v1"'
fi
uv run --frozen "${extras[@]}" "${run_options[@]}" pytest -q
uv run --frozen "${extras[@]}" "${run_options[@]}" pytest -q tests_tools
check_tmp=$(mktemp -d)
trap 'rm -rf "$check_tmp"' EXIT
uv build --no-sources --out-dir "$check_tmp/dist"
uv run --frozen "${extras[@]}" "${run_options[@]}" python scripts/verify_wheel.py "$check_tmp/dist"
uv run --frozen "${extras[@]}" "${run_options[@]}" python scripts/export_release_contract.py "$check_tmp"/dist/*.whl --output "$check_tmp/contract"
for qualified_manifest in releases/qualification/current/release.json releases/candidate/release.json; do
if [[ -f "$qualified_manifest" ]]; then
  uv run --frozen "${extras[@]}" "${run_options[@]}" python scripts/verify_release_candidate.py "$qualified_manifest" "$check_tmp/contract/contract.json" "$check_tmp/contract/evidence.json" controlplane-models
fi
done
uv venv "$check_tmp/venv" --python 3.13
uv export --frozen "${extras[@]}" "${export_options[@]}" --no-emit-project --format requirements-txt --output-file "$check_tmp/requirements.txt" >/dev/null
uv pip sync --python "$check_tmp/venv/bin/python" --require-hashes "$check_tmp/requirements.txt"
if (( ${#extras[@]} )); then
  if [[ -n "$fixture_wheel" ]]; then
    uv pip install --python "$check_tmp/venv/bin/python" --no-deps "$fixture_wheel"
  else
  # VCS requirements cannot be hash-verified like registry archives. Build the
  # reviewed exact commit separately, then install its wheel without resolution.
  protocol_ref=$(uv run --frozen "${extras[@]}" "${run_options[@]}" python - <<'PYTHON'
import re, tomllib
with open('pyproject.toml', 'rb') as stream:
    dependencies = tomllib.load(stream)['project']['optional-dependencies']['grpc']
prefix = 'controlplane-proto @ git+https://github.com/hyperme-sh/controlplane-proto.git@'
refs = [d.removeprefix(prefix) for d in dependencies if d.startswith(prefix)]
if len(refs) != 1 or not re.fullmatch('[0-9a-f]{40}', refs[0]):
    raise ValueError('Expected one immutable protocol dependency')
print(refs[0])
PYTHON
)
  git init -q "$check_tmp/protocol"
  git -C "$check_tmp/protocol" fetch --depth=1 https://github.com/hyperme-sh/controlplane-proto.git "$protocol_ref"
  git -C "$check_tmp/protocol" checkout -q --detach FETCH_HEAD
  test "$(git -C "$check_tmp/protocol" rev-parse HEAD)" = "$protocol_ref"
  uv build --wheel "$check_tmp/protocol" --no-sources --out-dir "$check_tmp/protocol-dist"
  uv pip install --python "$check_tmp/venv/bin/python" --no-deps "$check_tmp"/protocol-dist/*.whl
  fi
  "$check_tmp/venv/bin/python" -I -c 'import contractecho_pb2; assert contractecho_pb2.DESCRIPTOR.package == "spanopticon.v1"'
fi
uv pip install --python "$check_tmp/venv/bin/python" --no-deps "$check_tmp"/dist/*.whl
cp -R tests "$check_tmp/tests"
(cd "$check_tmp" && "$check_tmp/venv/bin/python" -I -m pytest -c /dev/null tests -q)
uv run --frozen "${extras[@]}" "${run_options[@]}" python - "$check_tmp" <<'PYTHON'
import pathlib, sys, tarfile
root = pathlib.Path(sys.argv[1])
with tarfile.open(next((root / 'dist').glob('*.tar.gz'))) as archive:
    archive.extractall(root / 'sdist', filter='data')
PYTHON
uv build --wheel "$check_tmp"/sdist/* --no-sources --out-dir "$check_tmp/rebuilt"
uv run --frozen "${extras[@]}" "${run_options[@]}" python scripts/verify_wheel.py "$check_tmp/rebuilt"
uv run --frozen "${extras[@]}" "${run_options[@]}" python scripts/export_release_contract.py "$check_tmp"/rebuilt/*.whl --output "$check_tmp/rebuilt-contract"
cmp "$check_tmp/contract/contract.json" "$check_tmp/rebuilt-contract/contract.json"
uv pip install --python "$check_tmp/venv/bin/python" --no-deps --reinstall "$check_tmp"/rebuilt/*.whl
(cd "$check_tmp" && "$check_tmp/venv/bin/python" -I -m pytest -c /dev/null tests -q)

# Retain the exact validated bytes for the release channel; never rebuild them.
if [[ -n "${RELEASE_ARTIFACT_DIR:-}" ]]; then
  mkdir -p "$RELEASE_ARTIFACT_DIR"
  cp "$check_tmp/dist"/* "$RELEASE_ARTIFACT_DIR/"
fi
