import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.compress import _clean_output


def test_clean_output_strips_quotes():
    assert _clean_output('"Hello there"') == "Hello there"


def test_clean_output_strips_label():
    assert _clean_output("Compressed text: Hello there") == "Hello there"


def test_clean_output_passthrough():
    assert _clean_output("Already clean.") == "Already clean."


def test_clean_output_handles_whitespace():
    assert _clean_output("   padded text   ") == "padded text"
