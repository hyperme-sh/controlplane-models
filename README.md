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

## Release channels

Successful main-push validation retains the validated Python wheel and source distribution and publishes
an immutable `test-<commit>` GitHub prerelease. Push a `vMAJOR.MINOR.PATCH`
tag at that tested commit to promote the exact files to a stable release,
without rebuilding. Repository visibility applies to all package assets.
Package metadata versions are preserved; these are GitHub distribution snapshots,
not automatic PyPI publication or service deployment.

Promotion requires the original Actions artifact (90-day requested retention;
organization policy may shorten it). Expired evidence fails closed: validate a
new main revision. The publisher verifies the run, source, workflow and artifact
digest independently of release metadata. Repository immutable releases must be
enabled. See the [shared release contract](https://github.com/hyperme-sh/.github/blob/7749591fccd30d46ba9b0adabe82114001c9d0de/actions/release-channel/README.md).
