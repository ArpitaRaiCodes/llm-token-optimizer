import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services import tokenizer


def test_count_tokens_empty():
    assert tokenizer.count_tokens("") == 0


def test_count_tokens_basic():
    n = tokenizer.count_tokens("Hello world")
    assert n > 0
    assert n < 5  # sanity bound, cl100k_base tokenizes this as 2 tokens


def test_count_characters():
    assert tokenizer.count_characters("hello") == 5
    assert tokenizer.count_characters("") == 0


def test_longer_text_has_more_tokens():
    short = tokenizer.count_tokens("Hi.")
    long = tokenizer.count_tokens("Hi. " * 50)
    assert long > short
