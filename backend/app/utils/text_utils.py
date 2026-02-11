"""Text processing utilities."""
import re
import unicodedata


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\S\n]+", " ", text)
    return text.strip()


def truncate_text(text: str, max_length: int = 500) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."


def estimate_reading_time(text: str, wpm: int = 250) -> int:
    words = len(text.split())
    return max(1, words // wpm)
