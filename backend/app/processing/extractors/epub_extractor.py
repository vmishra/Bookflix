"""EPUB text extraction using ebooklib + BeautifulSoup."""
import logging
from dataclasses import dataclass, field
from pathlib import Path
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class ExtractedChapter:
    index: int
    title: str | None
    text: str


@dataclass
class EPUBExtractionResult:
    chapters: list[ExtractedChapter] = field(default_factory=list)
    title: str | None = None
    author: str | None = None
    cover_image: bytes | None = None
    total_chapters: int = 0


class EPUBExtractor:
    def extract(self, file_path: str) -> EPUBExtractionResult:
        result = EPUBExtractionResult()
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"EPUB not found: {file_path}")

        try:
            book = epub.read_epub(str(path), options={"ignore_ncx": True})

            # Metadata
            title_meta = book.get_metadata("DC", "title")
            result.title = title_meta[0][0] if title_meta else None

            author_meta = book.get_metadata("DC", "creator")
            result.author = author_meta[0][0] if author_meta else None

            # Cover image
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_COVER:
                    result.cover_image = item.get_content()
                    break
            if not result.cover_image:
                for item in book.get_items_of_type(ebooklib.ITEM_IMAGE):
                    name = item.get_name().lower()
                    if "cover" in name:
                        result.cover_image = item.get_content()
                        break

            # Extract text from HTML documents
            chapter_idx = 0
            for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                soup = BeautifulSoup(item.get_content(), "html.parser")
                text = soup.get_text(separator="\n", strip=True)

                if len(text.strip()) < 50:
                    continue

                title = None
                heading = soup.find(["h1", "h2", "h3"])
                if heading:
                    title = heading.get_text(strip=True)

                result.chapters.append(ExtractedChapter(
                    index=chapter_idx,
                    title=title,
                    text=text.strip(),
                ))
                chapter_idx += 1

            result.total_chapters = len(result.chapters)
        except Exception as e:
            logger.error(f"EPUB extraction failed for {file_path}: {e}")
            raise

        return result
