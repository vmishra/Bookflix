"""Book processing pipeline orchestrator."""
import logging
import hashlib
from pathlib import Path
from app.config import settings

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".epub"}


def compute_file_hash(file_path: str) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def scan_directory(directory: str) -> list[dict]:
    """Walk directory and find all supported book files."""
    results = []
    root = Path(directory)
    if not root.exists():
        logger.error(f"Directory not found: {directory}")
        return results

    for path in sorted(root.rglob("*")):
        if path.suffix.lower() in SUPPORTED_EXTENSIONS and path.is_file():
            results.append({
                "file_path": str(path),
                "file_type": path.suffix.lower().lstrip("."),
                "file_size": path.stat().st_size,
                "file_name": path.name,
            })

    logger.info(f"Found {len(results)} books in {directory}")
    return results


def save_cover_image(book_id: int, image_data: bytes) -> str:
    """Save cover image and return relative path."""
    covers_dir = Path(settings.covers_path)
    covers_dir.mkdir(parents=True, exist_ok=True)
    cover_path = covers_dir / f"{book_id}.png"
    cover_path.write_bytes(image_data)
    return f"{book_id}.png"
