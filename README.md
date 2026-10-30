# controlplane-models

Component packaging from Panopticon source `2d92d13f38d491c298631b9b9296979c1fbadd19`.

`src/` is relocated from `core/models/src`; runtime and wire/schema bytes
are preserved unless an explicit change is recorded in `SOURCE-MANIFEST.json`.
`EXTRACTION.json` and the Git parents retain the original selected-path history.

Run `bash scripts/check.sh`. It uses the frozen dependency lock, runs the
component contracts, builds wheel/sdist, then installs the wheel and locked
dependencies into a fresh environment and repeats tests outside this checkout.
No sibling repository or monorepo environment is used for base package checks.

Private CI has read-only repository permissions and self-hosted Linux/x64 runners.
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

## Automated execution hold

Repository Actions are disabled. The staged workflow accepts only the main ref
on push/manual dispatch; it does not execute unmerged PR code on the shared
self-hosted runner pool. Before enabling it, verify reviewed/default-branch write
controls and the destination's execution isolation. Automated PR checks need an
isolated runner path; a same-repository condition and read-only workflow token
do not sandbox collaborator-controlled code. Until then, use the local frozen
wheel command above and require review before merge. No runner is provisioned.

The current repository action policy also refuses third-party actions. The staged
main workflow therefore remains inactive pending an explicit least-privilege
action policy and isolated execution review; this work does not broaden that
policy. Local wheel checks do not depend on GitHub action availability.
