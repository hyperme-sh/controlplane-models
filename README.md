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
bash scripts/check.sh --grpc
```

This needs Git read access to `hyperme-sh/controlplane-proto` through HTTPS
credentials or an existing SSH URL rewrite. The distribution
metadata pins commit `51e61210f272eabdc2a3a8d471a50b26257d866a`, so ordinary
wheel installers use the same immutable dependency. The adapters import installed
protocol modules and do not search parent source directories.

The explicit gRPC mode runs the complete test suite in source, fresh-wheel and
sdist-rebuilt-wheel environments. It requires the `spanopticon.v1` protocol to
import successfully before tests; a missing private dependency fails this lane.
Registry dependencies retain lockfile hashes. The protocol is fetched at the
metadata's full commit SHA, checked out detached, built as a wheel and installed
without dependency resolution in the isolated wheel-test environment. The base
mode still needs no private dependency access and may skip optional gRPC tests.

Local direct-Git qualification does not establish hosted private-dependency access
or release acceptance. The hosted fixture lane below verifies the published
protocol artifact without adding secrets or enabling a privileged runner.

CI runs fixture-backed gRPC checks on isolated GitHub-hosted Ubuntu workers with
read-only access and pinned actions. Direct-Git integration requires existing
read-only repository access; the hosted fixture lane requires no private credential.

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

## Hosted protocol consumer qualification

CI runs `bash scripts/check.sh --grpc-fixture`. This checks the real published
protocol wheel under `tests_artifacts/protocol` against its recorded SHA-256,
package identity, declared Git revision and lockfile. The manifest records the
immutable release and successful Actions artifact provenance; the dependency
revision and publication revision were verified to have identical Git trees.
The fixture is test-only and is not included in model distributions.

Registry dependencies still come from the frozen lockfile. The private Git
package is omitted from that installation, then the exact verified wheel is
installed without dependency resolution. All gRPC consumer tests run in source,
fresh-wheel and sdist-rebuilt-wheel contexts. A dependency pin change requires
a matching qualified fixture; a missing or altered fixture fails. No private
credentials, environments, approval gates or runner-policy changes are needed.
The existing `--grpc` mode still tests directly from the pinned Git dependency
when read access is available. Neither mode qualifies live provider deployments.

## Test qualification and stable acceptance

GitHub `test-<commit>` prereleases are development snapshots. Their embedded
package version does not reserve a stable version. Artifact and consumer evidence
lives under `releases/qualification`; the current wheel binding is still checked
by package CI, alongside any future explicit stable candidate. Earlier test
snapshot receipts are preserved there with an explicit non-stable classification.

`releases/accepted` and `SPANOPTICON_RELEASE_BASELINE_SHA` are reserved for an
actual immutable stable GitHub release. The pinned shared guard verifies the live
release channel, stable tag source and asset digests; a test snapshot cannot
become accepted through a provenance label. No stable baseline is recorded until
that release exists. Stable publication remains closed without a valid baseline;
first stable bootstrap and coordinated release qualification remain separate.
No stable version, approval prerequisite or deployment is introduced here.


### Published stable distribution

The accepted record binds the existing immutable `v0.24.0` release to its actual
GitHub release ID, source revision and published asset digests. Test snapshots
remain under `releases/qualification` and do not establish stable acceptance.
Runtime deployment and coordinated consumer acceptance remain separate.
