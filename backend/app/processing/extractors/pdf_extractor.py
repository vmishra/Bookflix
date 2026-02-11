"""PDF text extraction using PyMuPDF + pdfplumber."""
import logging
from pathlib import Path
from dataclasses import dataclass, field
import fitz  # PyMuPDF
from PIL import Image
import io

logger = logging.getLogger(__name__)


@dataclass
class ExtractedPage:
    page_number: int
    text: str
    chapter: str | None = None


@dataclass
class PDFExtractionResult:
    pages: list[ExtractedPage] = field(default_factory=list)
    title: str | None = None
    author: str | None = None
    total_pages: int = 0
    cover_image: bytes | None = None


class PDFExtractor:
    def extract(self, file_path: str) -> PDFExtractionResult:
        result = PDFExtractionResult()
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        try:
            doc = fitz.open(str(path))
            result.total_pages = len(doc)

            # Extract metadata
            metadata = doc.metadata or {}
            result.title = metadata.get("title") or None
            result.author = metadata.get("author") or None

            # Extract cover (first page as image)
            if len(doc) > 0:
                try:
                    page = doc[0]
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    result.cover_image = pix.tobytes("png")
                except Exception as e:
                    logger.warning(f"Cover extraction failed for {file_path}: {e}")

            # Extract text from each page
            current_chapter = None
            toc = doc.get_toc()
            chapter_map = {}
            for level, title, page_num in toc:
                if level <= 2:
                    chapter_map[page_num - 1] = title

            for page_num in range(len(doc)):
                if page_num in chapter_map:
                    current_chapter = chapter_map[page_num]

                page = doc[page_num]
                text = page.get_text("text")

                if text.strip():
                    result.pages.append(ExtractedPage(
                        page_number=page_num + 1,
                        text=text.strip(),
                        chapter=current_chapter,
                    ))

            doc.close()
        except Exception as e:
            logger.error(f"PDF extraction failed for {file_path}: {e}")
            raise

        return result
