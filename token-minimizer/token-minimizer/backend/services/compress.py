"""Prompt template and post-processing for text compression."""

from services import ollama_client, tokenizer

SYSTEM_PROMPT = (
    "You are a text compression engine. You rewrite text to use fewer tokens "
    "while preserving 100% of the factual meaning, intent, and key details. "
    "Rules:\n"
    "1. Never drop facts, numbers, names, constraints, or instructions.\n"
    "2. Remove filler words, redundant phrasing, and unnecessary politeness.\n"
    "3. Prefer shorter synonyms and tighter grammar over dropping content.\n"
    "4. Keep the original language and tone register (formal stays formal).\n"
    "5. Output ONLY the compressed text. No preamble, no explanation, "
    "no quotation marks, no 'Here is the compressed text:'.\n"
    "6. If the input is already minimal, return it unchanged."
)


def _build_prompt(text: str) -> str:
    return f"Compress the following text:\n\n{text}"


def _clean_output(raw: str) -> str:
    """Strip common model wrapper artifacts (quotes, leading labels)."""
    cleaned = raw.strip()
    # Strip a single pair of wrapping quotes if the model added them.
    if len(cleaned) >= 2 and cleaned[0] in "\"'" and cleaned[-1] == cleaned[0]:
        cleaned = cleaned[1:-1].strip()
    # Strip a leading "Compressed text:" style label if present.
    for prefix in ("compressed text:", "compressed:", "output:"):
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
    return cleaned


async def compress_text(text: str, model: str) -> dict:
    original_tokens = tokenizer.count_tokens(text)

    raw = await ollama_client.generate(
        model=model, prompt=_build_prompt(text), system=SYSTEM_PROMPT
    )
    compressed = _clean_output(raw)

    # Safety net: if the model produced something empty or somehow longer
    # in a degenerate way, fall back to the original rather than losing content.
    if not compressed:
        compressed = text

    compressed_tokens = tokenizer.count_tokens(compressed)

    # Never report a "win" that isn't real, and never silently expand text.
    if compressed_tokens >= original_tokens:
        compressed = text
        compressed_tokens = original_tokens

    saved = original_tokens - compressed_tokens
    percent = round((saved / original_tokens) * 100, 1) if original_tokens else 0.0

    return {
        "original_text": text,
        "compressed_text": compressed,
        "original_tokens": original_tokens,
        "compressed_tokens": compressed_tokens,
        "tokens_saved": saved,
        "percent_saved": percent,
        "model_used": model,
    }
