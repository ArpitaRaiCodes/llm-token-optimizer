"""Pydantic schemas shared across the API."""

from typing import Optional
from pydantic import BaseModel, Field

ALLOWED_MODELS = {
    "qwen2.5:0.5b": {"label": "Qwen2.5 0.5B", "min_ram_gb": 2},
    "qwen2.5:1.5b": {"label": "Qwen2.5 1.5B", "min_ram_gb": 4},
    "qwen2.5:3b": {"label": "Qwen2.5 3B", "min_ram_gb": 6},
}

MAX_INPUT_CHARS = 20_000  # guard against pathologically large pastes


class TokenCountRequest(BaseModel):
    text: str = Field(..., max_length=MAX_INPUT_CHARS)


class TokenCountResponse(BaseModel):
    tokens: int
    characters: int


class CompressRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_INPUT_CHARS)
    model: str = Field(default="qwen2.5:0.5b")


class CompressResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    original_text: str
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    tokens_saved: int
    percent_saved: float
    model_used: str


class ModelInfo(BaseModel):
    id: str
    label: str
    min_ram_gb: int
    available: bool


class ModelsResponse(BaseModel):
    models: list[ModelInfo]
    ollama_reachable: bool
