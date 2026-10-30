# controlplane-models

Component packaging from Panopticon source `2d92d13f38d491c298631b9b9296979c1fbadd19`.

`src/` is relocated from `core/models/src`; runtime and wire/schema bytes
are preserved unless an explicit change is recorded in `SOURCE-MANIFEST.json`.
`EXTRACTION.json` and the Git parents retain the original selected-path history.

Run `bash scripts/check.sh`. It uses the frozen dependency lock, runs the
component contracts, builds wheel/sdist, then installs the wheel and locked
dependencies into a fresh environment and repeats tests outside this checkout.
No sibling repository or monorepo environment is used for base package checks.

Private CI has read-only repository permissions and disposable GitHub-hosted runners.
No App credential, deployment environment, package publication or runtime cutover
is introduced. Package metadata versions retain their imported values; they do
not reset or stand in for public-contract versions.

## Optional protocol integration

`uv sync --frozen --extra grpc` installs the explicit protocol dependency pinned
to `controlplane-proto` commit `718c5f4dd552446204ac4a0af1c106ae0cbbb8f8`.
The mapper imports the installed generated module rather than walking parent
folders for a monorepo `proto/` directory. All conversion/wire bytes outside that
loader remain unchanged; the one runtime packaging change is recorded separately.

Base CI needs no cross-repository credential and tests the default model package.
The grpc extra also runs the original user/listing/token protobuf roundtrips.
Local integration can use the developer's existing private Git read access;
automated cross-repository grpc checks still need destination-specific read-only
access. Do not reuse Panopticon's deployment credential. No tag or consumer
cutover is implied by the reviewed-branch commit pin.

## Isolated component CI

Checks run on disposable GitHub-hosted Ubuntu workers for PRs, main and manual
runs. This repository has no access to the organization self-hosted runner groups,
so PR changes cannot select the shared private fleet. The contents token is
read-only; checkout credentials are not persisted, and no environment/deployment
secrets are provided. The external action allowlist contains only the two full-SHA checkout/uv setup
actions. GitHub also permits local and organization-owned actions. No VM, runner or App is created.

This is the user-authorized isolation correction for new component repositories.
Existing private deployment and payment jobs retain their runner access. An
isolated package check does not authorize publication or runtime cutover.
