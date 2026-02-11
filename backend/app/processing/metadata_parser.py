"""Parse title/author from filename when metadata is missing."""
import re
from pathlib import Path


def parse_filename(file_path: str) -> dict:
    stem = Path(file_path).stem
    # Remove common patterns like (z-lib.org), [epub], etc.
    cleaned = re.sub(r"\([^)]*\)", "", stem)
    cleaned = re.sub(r"\[[^\]]*\]", "", cleaned)
    cleaned = cleaned.strip(" _-.")

    # Try "Author - Title" pattern
    if " - " in cleaned:
        parts = cleaned.split(" - ", 1)
        return {"author": parts[0].strip(), "title": parts[1].strip()}

    # Try "Title_Author" pattern
    if "_" in cleaned:
        parts = cleaned.rsplit("_", 1)
        if len(parts) == 2 and len(parts[1]) > 3:
            return {"title": parts[0].replace("_", " ").strip(), "author": parts[1].replace("_", " ").strip()}

    # Fall back to filename as title
    title = cleaned.replace("_", " ").replace("-", " ")
    title = re.sub(r"\s+", " ", title).strip()
    return {"title": title, "author": None}
