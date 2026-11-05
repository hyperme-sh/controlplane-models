# Releasing

This repository's package version is `0.2.0`, declared in `pyproject.toml` and
recorded in `release-policy.json` (line `0.2`). GitHub release
[v0.24.0](https://github.com/hyperme-sh/controlplane-models/releases/tag/v0.24.0)
remains the immutable stable distribution of `spanopticon_models-0.24.0`.
Historical tags stay in place. Development builds use the exact source pins in
this tree and artifacts rebuilt from that source.

How a candidate is admitted against the shared compatibility line is in
[Release compatibility](release-policy.md). This page is the channel behavior:
what CI stores, what becomes a prerelease, and what becomes a stable release.

## Main validation

[`.github/workflows/check.yml`](../.github/workflows/check.yml) (`Component checks`)
runs on pull requests, on pushes to `main`, and on manual dispatch. It checks
out the repository read-only, installs uv 0.11.26 and Python 3.13, and runs
`bash scripts/check.sh --grpc-fixture`.

A push to `main` uploads the wheel and sdist from that run as the `tested-dist`
Actions artifact (retention 90 days, uncompressed). The same run uploads JUnit
results as `package-test-results`. Those artifacts are the qualification
record. Tags and GitHub releases come from the workflows below.

Pull requests run the same checks. Publication waits for a `main` push or a
version tag.

## Test snapshots

Two prerelease forms exist:

- `test-<commit>` GitHub prereleases are development snapshots. The version
  string embedded in the wheel does not reserve a stable version. Evidence for
  those snapshots is kept under `releases/qualification`, with an explicit
  non-stable classification. The current tree's qualification manifest is
  `releases/qualification/current/release.json` (package `0.2.0`,
  `stable_release: false`).
- After a successful `Component checks` run on a `main` push,
  [`.github/workflows/test-bundles.yml`](../.github/workflows/test-bundles.yml)
  publishes that run's `tested-dist` files as an immutable `0.24.0-test.N`
  prerelease. The channel is
  [`.github/test-channel.json`](../.github/test-channel.json) (`next` is
  `0.24.0`, workflow `.github/workflows/check.yml`). The publisher checks the
  workflow run, source revision, channel configuration, and the original
  Actions artifact digest from GitHub metadata. Dependency credentials stay
  off that job.

`releases/accepted` and the repository variable
`SPANOPTICON_RELEASE_BASELINE_SHA` refer to an immutable stable GitHub release.
Stable acceptance is a `v*` tag published through the path below and recorded
under `releases/accepted`. Snapshots remain under `releases/qualification`.

Consumers assembling a coordinated Hypermesh test bundle pin this component by
commit and artifact digest. The `0.24.0-test.N` counter is local to this
repository's test channel.

## Stable publication

A stable release is a `vMAJOR.MINOR.PATCH` tag.
[`.github/workflows/release.yml`](../.github/workflows/release.yml) runs
release admission, then publishes the exact `tested-dist` artifact from the
successful main validation of that commit. The publisher checks the run, the
source revision, and the artifact digest from GitHub metadata.

The accepted record for `v0.24.0` is in `releases/accepted/`:

| Field | Value |
| --- | --- |
| GitHub release | [v0.24.0](https://github.com/hyperme-sh/controlplane-models/releases/tag/v0.24.0) (release id `434678548`) |
| Source revision | `30eeeffbb840cc512300045f98c9c3b0c19f1cc4` |
| Wheel | `spanopticon_models-0.24.0-py3-none-any.whl` |
| Wheel SHA-256 | `7373dc89d95cccdb67e50e8e83965a6a0417547fe129118fd67194dc3b42e936` |
| Sdist SHA-256 | `1745d8266425e54c7320571fb9e786334dbea9eb4d017a74e7e8ca78864cd871` |

That record is in `releases/accepted/provenance.json`. The `v0.24.0` wheel's
`grpc` extra pins `controlplane-proto` at
`51e61210f272eabdc2a3a8d471a50b26257d866a`. This tree pins
`db0c3b6b2359ec5a3a3792e0a2ec00d4c9c38db9`. Package qualification, the choice
of a coordinated consumer set, and deploying a running control plane are
separate steps from publishing the GitHub release.

## Protocol fixture

`bash scripts/check.sh --grpc-fixture` checks the protocol wheel under
`tests_artifacts/protocol` against the SHA-256, package name, Git revision, and
lockfile recorded in `tests_artifacts/protocol/manifest.json`. The manifest
revision and the wheel's build revision are the same commit
(`db0c3b6b2359ec5a3a3792e0a2ec00d4c9c38db9`). The fixture is test-only and is
not installed into the `spanopticon-models` distribution.

Registry dependencies still come from `uv.lock`. The Git dependency is left
out of that hashed install, and the verified fixture wheel is installed with
`--no-deps`. gRPC consumer tests then run from source, from a fresh wheel, and
from a wheel rebuilt from the sdist. A pin change needs a matching fixture; a
missing or altered fixture fails the lane.

`bash scripts/check.sh --grpc` builds `controlplane-proto` from the commit in
`pyproject.toml` when that repository is reachable. Neither lane deploys a
live service.
