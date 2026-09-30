"""Token counting.

We count tokens with tiktoken's cl100k_base encoding rather than Qwen's own
tokenizer. Reasoning: the point of this tool is to shrink text *before* it
gets sent to a paid, remote LLM (GPT-4-class models, Claude, etc.), so the
number a user sees should approximate what they'll be billed for downstream,
not what the local compressor model happens to use internally. cl100k_base
is a close, dependency-light stand-in across most modern BPE tokenizers.
"""

import tiktoken

_ENCODING = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    if not text:
        return 0
    return len(_ENCODING.encode(text))


def count_characters(text: str) -> int:
    return len(text)
