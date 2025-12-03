"""ADK-ready tools for the education agents.

These wrap the existing RAG retriever for grounded responses and provide
quiz-building snippets. Each tool follows Day2 guidance: clear docstrings,
type hints, and structured dict returns.
"""

from typing import Any, Dict

from google.adk.tools import FunctionTool

try:
    # Reuse the retriever defined in the adk package.
    from adk.rag_setup import get_retriever

    _retriever = get_retriever()
except Exception:
    # Fallback stub retriever to keep the scaffold import-safe if LangChain
    # deps or the PDF are not set up yet.
    _retriever = None


def _fetch_info(query: str) -> Dict[str, Any]:
    """Retrieve relevant chunks from the domain PDF (RAG-backed).

    Args:
        query: The question or topic to search for.

    Returns:
        Dict with status and a list of text snippets.
    """

    if _retriever is None:
        return {
            "status": "error",
            "error_message": "Retriever not initialized. Set PDF_PATH and dependencies.",
        }

    docs = _retriever.get_relevant_documents(query)
    snippets = [(doc.page_content or "").strip() for doc in docs]
    return {"status": "success", "snippets": snippets}


def _get_quiz_source(topic: str, max_chunks: int = 3) -> Dict[str, Any]:
    """Return a few concise snippets to ground quiz generation.

    Args:
        topic: Topic to pull reference material for.
        max_chunks: Maximum number of chunks to return.

    Returns:
        Dict with status and labeled snippet strings.
    """

    if _retriever is None:
        return {
            "status": "error",
            "error_message": "Retriever not initialized. Set PDF_PATH and dependencies.",
        }

    docs = _retriever.get_relevant_documents(topic)
    snippets = []
    for idx, doc in enumerate(docs[:max_chunks], start=1):
        text = (doc.page_content or "").strip()
        snippets.append(f"Snippet {idx}: {text[:600]}")

    return {"status": "success", "snippets": snippets}


# ADK FunctionTool wrappers
fetch_info_tool = FunctionTool(func=_fetch_info)
get_quiz_source_tool = FunctionTool(func=_get_quiz_source)

__all__ = ["fetch_info_tool", "get_quiz_source_tool"]
