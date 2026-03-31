"""Shared HTTP-facing contracts (errors, pagination) for REST APIs."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from panopticon_models._config import model_config_contracts

T = TypeVar("T")


class ApiErrorBody(BaseModel):
    """RFC7807-style problem detail (subset) for documented error responses."""

    model_config = model_config_contracts

    detail: str = Field(..., description="Human-readable error message")
    code: str | None = Field(default=None, description="Stable machine-readable code when available")


class Page(BaseModel, Generic[T]):
    """Offset-based page of items."""

    model_config = model_config_contracts

    items: list[T] = Field(default_factory=list)
    total: int = Field(..., ge=0, description="Total rows matching the query (before limit/offset)")
    limit: int = Field(..., ge=1, le=500)
    offset: int = Field(..., ge=0)
