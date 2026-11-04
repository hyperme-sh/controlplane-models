# controlplane-models

Shared Pydantic domain contracts distributed as `spanopticon-models`. Import them
from `spanopticon_models`; optional gRPC adapters convert the supported models to
and from ContractEcho protobuf messages.

## Development

Requires Python 3.13+ and uv 0.11.26:

```sh
bash scripts/check.sh
```

The script runs source tests with locked dependencies, builds wheel/sdist artifacts,
checks their runtime contents, and repeats tests outside the checkout against a
fresh installed wheel and an sdist-rebuilt wheel. Base checks need no private Git
credential; optional gRPC tests are skipped when the extra is absent.

## Optional gRPC integration

```sh
uv sync --frozen --extra grpc
uv run --frozen --extra grpc pytest -q
```

This needs SSH read access to `hyperme-sh/controlplane-proto`. The distribution
metadata pins commit `4ce51c3492d1f7d7c85fb8322f7eefda059209f2`, so ordinary
wheel installers use the same immutable dependency. The adapters import installed
protocol modules and do not search parent source directories.

CI runs base checks on isolated GitHub-hosted Ubuntu workers with read-only access
and pinned actions. Automated private gRPC integration needs separately configured
read-only repository access; deployment credentials must not be used for it.
