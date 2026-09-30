"""Thin async wrapper around a local Ollama instance."""

import os
import httpx

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
REQUEST_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "120"))


class OllamaError(Exception):
    """Raised when Ollama is unreachable or returns an error."""


async def is_reachable() -> bool:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{OLLAMA_HOST}/api/tags")
            return r.status_code == 200
    except httpx.HTTPError:
        return False


async def list_local_models() -> set[str]:
    """Returns the set of model tags Ollama already has pulled locally."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{OLLAMA_HOST}/api/tags")
            r.raise_for_status()
            data = r.json()
            return {m["name"] for m in data.get("models", [])}
    except httpx.HTTPError:
        return set()


async def generate(model: str, prompt: str, system: str | None = None) -> str:
    """Calls Ollama's /api/generate with streaming disabled and returns the
    full response text. Raises OllamaError on failure."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2},
    }
    if system:
        payload["system"] = system

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            r = await client.post(f"{OLLAMA_HOST}/api/generate", json=payload)
            r.raise_for_status()
            data = r.json()
            return data.get("response", "").strip()
    except httpx.ConnectError as e:
        raise OllamaError(
            f"Could not reach Ollama at {OLLAMA_HOST}. Is it running? "
            f"(`ollama serve`)"
        ) from e
    except httpx.HTTPStatusError as e:
        detail = e.response.text
        if "model" in detail.lower() and "not found" in detail.lower():
            raise OllamaError(
                f"Model '{model}' isn't pulled yet. Run: ollama pull {model}"
            ) from e
        raise OllamaError(f"Ollama returned an error: {detail}") from e
    except httpx.HTTPError as e:
        raise OllamaError(f"Ollama request failed: {e}") from e
