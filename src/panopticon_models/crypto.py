from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, model_validator

from panopticon_models._config import model_config_contracts


class CryptoBudget(BaseModel):
    """Solana-style budget envelope (lamports). Uses solders for pubkey validation."""

    model_config = model_config_contracts

    owner: str = Field(..., min_length=32, max_length=64, description="Base-58 public key")
    mint: str = Field(..., min_length=32, max_length=64, description="SPL mint public key")
    allocated_lamports: int = Field(..., ge=0)
    ceiling_lamports: int = Field(..., ge=0)

    @field_validator("owner", "mint")
    @classmethod
    def valid_solana_pubkey(cls, v: str) -> str:
        from solders.pubkey import Pubkey

        try:
            Pubkey.from_string(v)
        except Exception as e:
            raise ValueError(f"invalid Solana public key: {e}") from e
        return v

    @model_validator(mode="after")
    def allocated_within_ceiling(self) -> CryptoBudget:
        if self.allocated_lamports > self.ceiling_lamports:
            raise ValueError("allocated_lamports cannot exceed ceiling_lamports")
        return self
