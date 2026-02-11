"""File utility functions."""
import os
from pathlib import Path


def get_file_extension(file_path: str) -> str:
    return Path(file_path).suffix.lower().lstrip(".")


def get_file_size_mb(file_path: str) -> float:
    return os.path.getsize(file_path) / (1024 * 1024)


def ensure_directory(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)
