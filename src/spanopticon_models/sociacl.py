"""SociACL sharing, predicates, and recovery contracts (APIs + events)."""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from spanopticon_models._config import model_config_contracts
from spanopticon_models.acl import PoliticalViewCategory, SociACLAttributes


class SociACLShareMode(str, Enum):
    notify_only = "notify_only"
    negotiate = "negotiate"
    release_if_match = "release_if_match"


class SociACLResourceKind(str, Enum):
    user = "user"
    group = "group"
    attribute_bundle = "attribute_bundle"


class SociACLDistanceSource(str, Enum):
    client = "client"
    ip_coarse = "ip_coarse"
    beacon = "beacon"


class SociACLPredicate(BaseModel):
    """JSON-serializable rules stored on share links; evaluated server-side."""

    model_config = model_config_contracts

    min_verification_level: int | None = Field(default=None, ge=0, le=4)
    min_vouch_count: int | None = Field(default=None, ge=0)
    max_distance_km: float | None = Field(default=None, ge=0)
    required_political_tolerance: PoliticalViewCategory | None = None
    member_of_group_id: uuid.UUID | None = None
    cross_network_handle_allowlist: list[str] | None = Field(
        default=None,
        description="If set, requester handle must match one entry (exact).",
    )
    cross_network_handle_blocklist: list[str] | None = None


class SociACLRequestContext(BaseModel):
    """Requester-supplied context for evaluation (trust labels are advisory)."""

    model_config = model_config_contracts

    sub: str | None = Field(default=None, max_length=512)
    political_view: PoliticalViewCategory | None = None
    verification_level: int | None = Field(default=None, ge=0, le=4)
    vouch_count: int | None = Field(default=None, ge=0)
    vouch_source: str | None = Field(default=None, max_length=64)
    cross_network_handle: str | None = Field(default=None, max_length=256)
    distance_km: float | None = Field(default=None, ge=0)
    distance_source: SociACLDistanceSource | None = None


class SociACLDecisionKind(str, Enum):
    allow = "allow"
    deny = "deny"
    challenge = "challenge"
    notify_owner = "notify_owner"


class SociACLDecision(BaseModel):
    model_config = model_config_contracts

    decision: SociACLDecisionKind
    reason_code: str = Field(..., max_length=64)
    matched_predicates: list[str] = Field(default_factory=list)


class SociACLShareLinkCreate(BaseModel):
    resource_kind: SociACLResourceKind
    owner_user_id: uuid.UUID | None = None
    group_id: uuid.UUID | None = None
    resource_descriptor: dict = Field(default_factory=dict)
    predicate: SociACLPredicate
    mode: SociACLShareMode
    expires_at: str | None = Field(
        default=None,
        description="ISO8601; omit for no expiry",
    )
    max_uses: int | None = Field(default=None, ge=1)


class SociACLShareLinkPublic(BaseModel):
    """Non-sensitive resolve payload for anonymous callers."""

    share_id: uuid.UUID
    mode: SociACLShareMode
    active: bool
    resource_kind: SociACLResourceKind
    expires_at: str | None = None
    uses_remaining: int | None = None


class SociACLShareLinkOwnerView(BaseModel):
    """Tenant-scoped share metadata. Never includes raw token or token_hash."""

    model_config = model_config_contracts

    share_id: uuid.UUID
    token_prefix: str = Field(..., max_length=16)
    mode: SociACLShareMode
    active: bool
    resource_kind: SociACLResourceKind
    resource_descriptor: dict = Field(default_factory=dict)
    predicate: SociACLPredicate
    expires_at: str | None = None
    uses_remaining: int | None = None
    owner_user_id: uuid.UUID | None = None
    group_id: uuid.UUID | None = None
    created_by: str | None = None
    created_at: str | None = None


class SociACLEvaluateRequest(BaseModel):
    token: str = Field(..., min_length=8, max_length=512)
    context: SociACLRequestContext
    owner_attributes: SociACLAttributes | None = Field(
        default=None,
        description="MVP/tests: owner SociACL dimensions; production should load from user-service.",
    )


class RecoverySessionCreate(BaseModel):
    idempotency_key: str = Field(..., min_length=8, max_length=128)
    metadata: dict | None = None


class RecoverySessionResponse(BaseModel):
    session_id: uuid.UUID
    state: Literal["pending", "awaiting_proof", "completed", "failed"]
    expires_at: str


class RecoveryProofRequest(BaseModel):
    proof_type: Literal["mfa", "oidc", "split_key_stub"] = "split_key_stub"
    payload: dict | None = None
