# controlplane-models

`controlplane-models` is the source repository for the Python package
`spanopticon-models` (version `0.2.0` in this tree). It is the shared set of
[Pydantic](https://docs.pydantic.dev/) v2 domain contracts that Hypermesh
control-plane services exchange: users and tenants, marketplace listings,
lease payments, inference metering, and access-control payloads. An optional
`grpc` extra converts `SharedUser`, `Listing`, and `TokenUsage` to and from
`spanopticon.v1` ContractEcho protobuf messages published by
[`controlplane-proto`](https://github.com/hyperme-sh/controlplane-proto).

## Why

A renter paying for host time, a host recording a payout address, and an
inference call being metered all cross several control-plane services. Each
service owns its database and HTTP handlers, and each one still has to accept
the same JSON the others send. Repeating those shapes by hand is how a listing,
a user, or a USDC lease payment drifts between callers. This package is the
schema they import as `spanopticon_models`, with the same fields and the same
validation on every side of the call.

## How it works

Callers import the models. This repository has no daemon and no configuration
file. Every domain model uses one config: strings are stripped, unknown fields
are rejected, and assignment is validated (`spanopticon_models._config`).

| Module | What it carries |
| --- | --- |
| `user`, `tenant`, `organization`, `group` | Cross-service identity DTOs (`SharedUser`, `SharedTenant`, `SharedOrganization`, `SharedGroup`). SQLAlchemy rows live in [`controlplane-db`](https://github.com/hyperme-sh/controlplane-db). |
| `marketplace` | `Listing` (`plugin`, `agent`, `config`, `hardware`), `Purchase`, and `Review`. Prices are integer minor units. |
| `payment` | Stripe-shaped `PaymentIntent`, USDC lease payment bodies, billing-record reads, and usage records. |
| `ai_metering` | `AIModel` reference prices, one `TokenUsage` inference record, and an `AgentBudget` fiat spend cap. |
| `crypto` | `CryptoBudget`, a Solana lamport envelope checked with `solders`. Separate from `AgentBudget`. |
| `acl`, `sociacl` | `ACLPolicy` plus SociACL share-link and evaluation payloads. |
| `http_common` | `ApiErrorBody` and offset `Page` for REST responses. |
| `grpc` | Optional. Wire messages, mappers, and protobuf converters. |

The root package re-exports the types most callers need. Lease-payment and
billing models stay in `spanopticon_models.payment`.

The `grpc` extra depends on `controlplane-proto` at the commit pinned in
`pyproject.toml` (`db0c3b6b2359ec5a3a3792e0a2ec00d4c9c38db9`), plus `grpcio`,
`protobuf`, and `pydantic-rpc`. Converters import the installed
`contractecho_pb2` module (`spanopticon.v1`). `ContractEcho` is the echo
service class used to generate those messages (`echo_user`, `echo_listing`,
`echo_token_usage`). Generation lives with the protocol package; this
repository ships the mappers.

## Practical use

Requires Python 3.13 or newer. Development and CI use
[uv](https://docs.astral.sh/uv/) 0.11.26. Runtime dependencies are
`pydantic[email]>=2.12.0` and `solana>=0.36.0`.

Install this tree:

```sh
git clone https://github.com/hyperme-sh/controlplane-models.git
cd controlplane-models
uv python install 3.13
uv sync
```

The published GitHub release
[`v0.24.0`](https://github.com/hyperme-sh/controlplane-models/releases/tag/v0.24.0)
is a separate artifact (`spanopticon_models-0.24.0-py3-none-any.whl`). Its
`grpc` extra pins `controlplane-proto` at
`51e61210f272eabdc2a3a8d471a50b26257d866a`. The snippet below matches the
models in this tree (`0.2.0`).

```sh
uv pip install \
  'https://github.com/hyperme-sh/controlplane-models/releases/download/v0.24.0/spanopticon_models-0.24.0-py3-none-any.whl'
```

Build a hardware listing and the USDC lease-payment body a renter posts.
`price_amount` and `amount_cents` are USD cents. A non-free listing requires a
non-negative price. A lease payment accepts `$0.50`–`$10,000.00`
(`50`–`1000000` cents).

```python
import uuid

from spanopticon_models import Listing, ListingType, PriceType, SharedUser
from spanopticon_models.payment import UsdcLeasePaymentCreate

tenant_id = uuid.uuid4()
user = SharedUser(
    id=uuid.uuid4(),
    email="renter@example.com",
    display_name="Ada",
    tenant_id=tenant_id,
)
listing = Listing(
    id=uuid.uuid4(),
    tenant_id=tenant_id,
    seller_id=uuid.uuid4(),
    title="AGX Orin",
    type=ListingType.HARDWARE,
    price_type=PriceType.USAGE,
    price_amount=150,
)
payment = UsdcLeasePaymentCreate(
    amount_cents=listing.price_amount,
    listing_id=listing.id,
)
print(user.model_dump(mode="json"))
print(payment.model_dump(mode="json"))
```

`POST /payments/usdc/lease-payments` takes `UsdcLeasePaymentCreate`. The
response model is `UsdcLeasePaymentResponse` (`amount_atoms` is USDC with 6
decimals, cents mapped 1:1). `GET /payments/billing-records` returns
`BillingRecordReadResponse`, including `host_pubkey` for the host payout
address. `POST /payments/usage-records` takes `UsageRecordCreate`.

Install the protobuf adapters from this tree:

```sh
uv sync --extra grpc
```

```python
import contractecho_pb2
from spanopticon_models.grpc.pb2_convert import (
    listing_from_pb2,
    listing_to_pb2,
    shared_user_from_pb2,
    shared_user_to_pb2,
)

user_bytes = shared_user_to_pb2(user).SerializeToString()
listing_bytes = listing_to_pb2(listing).SerializeToString()
user_again = shared_user_from_pb2(contractecho_pb2.UserWire.FromString(user_bytes))
listing_again = listing_from_pb2(contractecho_pb2.ListingWire.FromString(listing_bytes))
```

`shared_user_from_pb2` and `listing_from_pb2` take the generated message
objects. `FromString` turns the serialized bytes into those messages.
`token_usage_to_pb2` and `token_usage_from_pb2` round-trip `TokenUsage` the
same way, through `contractecho_pb2.TokenUsageWire.FromString`.
String-id mappers in `spanopticon_models.grpc` (`user_to_wire`,
`listing_to_wire`, `token_usage_to_wire`, and the matching `*_from_wire`
functions) work with the `pydantic-rpc` wire types alone.

## How Hypermesh uses it

Hypermesh rents AI inference on host machines. A host enrolls with the control
plane and runs certification, model downloads, and inference leases. A renter
pays for that time and sends work through the gateway. Control-plane services
validate the records on that path with these models. Host enrollment and the
job agent live in
[`hypermesh-host`](https://github.com/hyperme-sh/hypermesh-host). Price
clearing lives in
[`hypermesh-pricing`](https://github.com/hyperme-sh/hypermesh-pricing).
Lease-ticket signing (`hm1`) for gateway authorization lives in
[`hypermesh-ticket`](https://github.com/hyperme-sh/hypermesh-ticket). Event
envelopes and the topic registry live in
[`controlplane-events`](https://github.com/hyperme-sh/controlplane-events).

Callers and the traffic they put through this package:

- **Accounts.** [`user-service`](https://github.com/hyperme-sh/user-service),
  [`auth-service`](https://github.com/hyperme-sh/auth-service), and
  [`controlplane-identity`](https://github.com/hyperme-sh/controlplane-identity)
  own live accounts. The JSON they hand to other services is `SharedUser`,
  `SharedTenant`, `SharedOrganization`, and `SharedGroup`.
  [`controlplane-tenancy`](https://github.com/hyperme-sh/controlplane-tenancy)
  owns tenant membership and the marketplace tenant; these models are the
  detached copies of that directory.
- **Host capacity for sale.** A `Listing` with `ListingType.HARDWARE` is the
  sellable host offer (plugin, agent, and config listings use the same model).
  `Purchase` is the buyer acquiring that listing. Marketplace HTTP and events
  carry these types. The price in cents is what a renter locks when
  [`hypermesh-pricing`](https://github.com/hyperme-sh/hypermesh-pricing)
  clears a lease.
- **Lease payment.** The renter client sends `UsdcLeasePaymentCreate` to
  `POST /payments/usdc/lease-payments`. The control plane answers with
  `UsdcLeasePaymentResponse`: pending USDC, atoms equal to the cent amount at
  6 decimals, and the chain id when the deployment has one. Billing reads
  (`BillingRecordReadResponse`) carry `host_pubkey`, the host USDC address
  used for payout, plus any stored Stripe ids for card or invoice rails.
  `PaymentIntent` is that Stripe-shaped contract. Later metered quantity on a
  commitment is `UsageRecordCreate` on `POST /payments/usage-records`.
- **Inference on the lease.** `TokenUsage` is one call: user, tenant, model,
  input and output tokens, and USD cost. `AgentBudget` is the fiat ceiling for
  that spend. `CryptoBudget` is the on-chain lamport envelope and is a
  different object. [`hypermesh-conductor`](https://github.com/hyperme-sh/hypermesh-conductor)
  is the budgeted task runtime that consumes those limits.
- **Who may see the resource.** [`acl-service`](https://github.com/hyperme-sh/acl-service)
  evaluates `ACLPolicy` and SociACL share links (`SociACLEvaluateRequest`,
  `SociACLDecision`). `SociACLShareLinkOwnerView` exposes a token prefix. The
  raw token stays off that payload.
- **Edge protobuf.** [`controlplane-edge`](https://github.com/hyperme-sh/controlplane-edge)
  can serve ContractEcho gRPC from the pinned
  [`controlplane-proto`](https://github.com/hyperme-sh/controlplane-proto)
  package. The bytes on that RPC are `spanopticon.v1` `UserWire`,
  `ListingWire`, and `TokenUsageWire`. This package is the conversion to and
  from the Pydantic models.

## Develop and test

From a checkout, with Python 3.13 and uv 0.11.26:

```sh
bash scripts/check.sh
```

That runs the test suite from source with the locked dependencies, builds a
wheel and a source distribution, checks their contents, and repeats the tests
against a fresh install of the wheel and a wheel rebuilt from the sdist.
Protocol tests run only with the flags below.

```sh
bash scripts/check.sh --grpc
bash scripts/check.sh --grpc-fixture
```

`--grpc` fetches `controlplane-proto` at
`db0c3b6b2359ec5a3a3792e0a2ec00d4c9c38db9`, builds that commit as a wheel, and
requires `contractecho_pb2` to import before tests. `--grpc-fixture` uses the
wheel and checksums recorded in
[`tests_artifacts/protocol/manifest.json`](tests_artifacts/protocol/manifest.json)
instead of cloning the protocol repository. The fixture stays under
`tests_artifacts/` and is omitted from the `spanopticon-models` wheel. CI runs
the fixture lane.

Release tags, test bundles, and the stable GitHub release are described in
[Releasing](docs/releasing.md).

## Release and versioning

The version declared in this repository is `0.2.0` (`pyproject.toml`).
Published bytes are GitHub release assets. Tag
[`v0.24.0`](https://github.com/hyperme-sh/controlplane-models/releases/tag/v0.24.0)
is the immutable stable release of `spanopticon_models-0.24.0`. Tags named
`test-<commit>` and prereleases named `0.24.0-test.N` are development
snapshots. Channel rules, artifact retention, and the accepted-release record
are in [Releasing](docs/releasing.md). Compatibility admission for the shared
line is in [Release compatibility](docs/release-policy.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).
