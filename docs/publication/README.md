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
offline. No third-party source archives are fetched or bundled. Publication
activation remains a separate step; no registry credentials are used here.

History review inventories reachable origin branches, tags and HEAD, including
bounded archived wheel members, without executing historical code. Findings
remain a review queue rather than publication clearance. Unreachable/deleted
refs, remote LFS data and external archives are outside this scan.

TEST publication will use a moving channel. Integration/e2e remains nightly.
No Actions uploads, visibility changes or history rewrites are introduced.
