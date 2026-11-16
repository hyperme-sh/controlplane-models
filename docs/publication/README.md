# Models publication preparation

Models remains Apache-2.0, version 0.2.0. Original and rebuilt wheels verify
owner LICENSE and NOTICE bytes. Contracts and wire bytes remain unchanged.

CI prepares `ghcr.io/hyperme-sh/controlplane-models/runtime` as a non-root
consumer image containing the qualified Models wheel and locked base runtime
dependencies. Models is a library, so the image has no service endpoint; its
default command identifies the package and consumers supply their command.
The optional grpc extra is qualified separately in package CI and is not
installed in this base consumer image.

The image preserves indexed installed dependency license texts and owner legal
texts. Missing legal texts fail preparation. CI scans every layer for secrets,
hosted-only code and source-bundle paths, and checks installed package bytes
offline. No third-party source archives are fetched or bundled. Main builds publish the qualified image to the moving GHCR `:test` channel.
Only the publication step receives write credentials, after qualification;
stale main builds skip publication. No version or production channel is enabled.

History review inventories reachable origin branches, tags and HEAD, including
bounded archived wheel members, without executing historical code. Findings
remain a review queue rather than publication clearance. Unreachable/deleted
refs, remote LFS data and external archives are outside this scan.

TEST publication will use a moving channel. Integration/e2e remains nightly.
No Actions uploads, visibility changes or history rewrites are introduced.

## Historical content and retained images

One historical payment DTO file retains provider-specific fields and descriptions.
Its exact Git object and content hashes are recorded under
`.github/workflows/historical-content-review.json`. CI refuses changed findings
or dispositions. The file remains in history without clearance for republication.

Retained-image CI inventories tagged and untagged GHCR versions and inspects
Linux amd64 layers without executing old images. It records hosted content,
legal paths, inherited configuration names and source-bundle presence, then
scans secrets. Deleted versions, other platforms and other registries are outside
this review. Inaccessible inventory is reported as unavailable, never as empty.
After TEST publication, inventory and retained-image inspection must succeed.
No source archives or registry settings changes are introduced.
