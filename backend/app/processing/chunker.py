"""Recursive text chunking with paragraph awareness."""
import re
from dataclasses import dataclass


@dataclass
class TextChunk:
    text: str
    chunk_index: int
    page_number: int | None = None
    chapter: str | None = None
    token_count: int = 0


class TextChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def estimate_tokens(self, text: str) -> int:
        return len(text.split())

    def chunk_text(
        self,
        text: str,
        page_number: int | None = None,
        chapter: str | None = None,
        start_index: int = 0,
    ) -> list[TextChunk]:
        if not text.strip():
            return []

        paragraphs = re.split(r"\n\s*\n", text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_idx = start_index

        for para in paragraphs:
            para_tokens = self.estimate_tokens(para)

            if current_tokens + para_tokens > self.chunk_size and current_chunk:
                chunk_text = "\n\n".join(current_chunk)
                chunks.append(TextChunk(
                    text=chunk_text,
                    chunk_index=chunk_idx,
                    page_number=page_number,
                    chapter=chapter,
                    token_count=current_tokens,
                ))
                chunk_idx += 1

                # Keep overlap
                overlap_text = []
                overlap_tokens = 0
                for p in reversed(current_chunk):
                    t = self.estimate_tokens(p)
                    if overlap_tokens + t > self.chunk_overlap:
                        break
                    overlap_text.insert(0, p)
                    overlap_tokens += t

                current_chunk = overlap_text
                current_tokens = overlap_tokens

            current_chunk.append(para)
            current_tokens += para_tokens

        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunks.append(TextChunk(
                text=chunk_text,
                chunk_index=chunk_idx,
                page_number=page_number,
                chapter=chapter,
                token_count=self.estimate_tokens(chunk_text),
            ))

        return chunks

    def chunk_pages(self, pages: list[dict]) -> list[TextChunk]:
        """Chunk a list of pages [{text, page_number, chapter}]."""
        all_chunks = []
        idx = 0
        for page in pages:
            page_chunks = self.chunk_text(
                text=page["text"],
                page_number=page.get("page_number"),
                chapter=page.get("chapter"),
                start_index=idx,
            )
            all_chunks.extend(page_chunks)
            idx += len(page_chunks)
        return all_chunks
