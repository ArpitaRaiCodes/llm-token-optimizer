"""FastAPI app: token counting + Qwen-powered compression via Ollama."""

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request

from models.schemas import (
    ALLOWED_MODELS,
    CompressRequest,
    CompressResponse,
    ModelInfo,
    ModelsResponse,
    TokenCountRequest,
    TokenCountResponse,
)
from services import compress, ollama_client, tokenizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("token-minimizer")

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Token Minimizer API",
    description="Count and compress text tokens locally using Qwen models via Ollama.",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your deployed frontend origin in production
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    ollama_ok = await ollama_client.is_reachable()
    return {"status": "ok", "ollama_reachable": ollama_ok}


@app.get("/api/models", response_model=ModelsResponse)
async def get_models():
    ollama_ok = await ollama_client.is_reachable()
    local_models = await ollama_client.list_local_models() if ollama_ok else set()

    models = [
        ModelInfo(
            id=model_id,
            label=meta["label"],
            min_ram_gb=meta["min_ram_gb"],
            available=model_id in local_models,
        )
        for model_id, meta in ALLOWED_MODELS.items()
    ]
    return ModelsResponse(models=models, ollama_reachable=ollama_ok)


@app.post("/api/count", response_model=TokenCountResponse)
@limiter.limit("60/minute")
async def count_tokens(request: Request, body: TokenCountRequest):
    return TokenCountResponse(
        tokens=tokenizer.count_tokens(body.text),
        characters=tokenizer.count_characters(body.text),
    )


@app.post("/api/compress", response_model=CompressResponse)
@limiter.limit("15/minute")
async def compress_text(request: Request, body: CompressRequest):
    if body.model not in ALLOWED_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model '{body.model}'. Allowed: {list(ALLOWED_MODELS)}",
        )

    try:
        result = await compress.compress_text(body.text, body.model)
    except ollama_client.OllamaError as e:
        logger.warning("Compression failed: %s", e)
        raise HTTPException(status_code=503, detail=str(e)) from e

    return CompressResponse(**result)
