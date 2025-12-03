import os
from dataclasses import dataclass
from functools import lru_cache
from typing import List

import fitz  # PyMuPDF
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Document:
    page_content: str


class SimpleRetriever:
    def __init__(self, chunks: List[str]):
        self.chunks = chunks

    def get_relevant_documents(self, query: str, k: int = 5) -> List[Document]:
        q_terms = [t for t in query.lower().split() if t]
        scores = []
        for idx, chunk in enumerate(self.chunks):
            text = chunk.lower()
            score = sum(text.count(t) for t in q_terms)
            scores.append((score, idx))
        scores.sort(reverse=True)
        docs = []
        for score, idx in scores[:k]:
            docs.append(Document(page_content=self.chunks[idx]))
        return docs


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks


def build_retriever(pdf_path: str | None = None):
    """Create a simple keyword-based retriever from a PDF without external APIs."""
    path = pdf_path or os.getenv("PDF_PATH", "education_textbook.pdf")
    if not os.path.exists(path):
        raise FileNotFoundError(f"PDF_PATH does not exist: {path}")

    doc = fitz.open(path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()

    chunks = _chunk_text(text)
    return SimpleRetriever(chunks)


@lru_cache(maxsize=1)
def get_retriever():
    """Return a cached retriever so the PDF is only ingested once."""
    return build_retriever()
