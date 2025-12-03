"""Quiz flow tools using ADK ToolContext for session state.

Flow (aligned with Day2/Day3 patterns):
- prepare_quiz(topic): fetch RAG snippets, cache in session state.
- get_quiz_step(): return current snippet hint and progress.
- advance_quiz(correct): update progress; on incorrect, stay on the same item.
- reveal_context(): return the full snippet for extra help when the learner
  struggles.
"""

from typing import Any, Dict, List

from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

try:
    from rag_setup import get_retriever  # type: ignore

    _retriever = get_retriever()
except Exception:
    _retriever = None


QUIZ_SNIPPETS_KEY = "quiz:snippets"
QUIZ_TOPIC_KEY = "quiz:topic"
QUIZ_INDEX_KEY = "quiz:index"
QUIZ_MISTAKES_KEY = "quiz:mistakes"


def _prepare_quiz(topic: str, max_chunks: int = 3, tool_context: ToolContext = None) -> Dict[str, Any]:
    """Initialize quiz state from RAG snippets for a topic.

    Stores snippets and progress counters in session state.
    """

    if _retriever is None:
        return {
            "status": "error",
            "error_message": "Retriever not initialized. Set PDF_PATH and dependencies.",
        }

    docs = _retriever.get_relevant_documents(topic)
    snippets: List[str] = []
    for doc in docs[:max_chunks]:
        text = (doc.page_content or "").strip()
        if text:
            snippets.append(text)

    if not snippets:
        return {"status": "error", "error_message": "No snippets found for topic."}

    if tool_context:
        tool_context.state[QUIZ_SNIPPETS_KEY] = snippets
        tool_context.state[QUIZ_TOPIC_KEY] = topic
        tool_context.state[QUIZ_INDEX_KEY] = 0
        tool_context.state[QUIZ_MISTAKES_KEY] = 0

    return {
        "status": "success",
        "topic": topic,
        "total_questions": len(snippets),
        "current_index": 0,
    }


def _get_quiz_step(tool_context: ToolContext = None) -> Dict[str, Any]:
    """Return the current quiz step with a hint snippet."""

    snippets = tool_context.state.get(QUIZ_SNIPPETS_KEY, []) if tool_context else []
    if not snippets:
        return {"status": "error", "error_message": "Quiz not prepared. Call prepare_quiz first."}

    idx = int(tool_context.state.get(QUIZ_INDEX_KEY, 0)) if tool_context else 0
    idx = max(0, min(idx, len(snippets) - 1))
    topic = tool_context.state.get(QUIZ_TOPIC_KEY, "") if tool_context else ""
    mistakes = int(tool_context.state.get(QUIZ_MISTAKES_KEY, 0)) if tool_context else 0

    snippet = snippets[idx]
    hint = snippet[:400]

    return {
        "status": "success",
        "topic": topic,
        "question_number": idx + 1,
        "total_questions": len(snippets),
        "hint_snippet": hint,
        "mistakes_on_question": mistakes,
    }


def _advance_quiz(correct: bool, tool_context: ToolContext = None) -> Dict[str, Any]:
    """Update quiz progress. If correct, move to next; if not, stay and track mistakes."""

    snippets = tool_context.state.get(QUIZ_SNIPPETS_KEY, []) if tool_context else []
    if not snippets:
        return {"status": "error", "error_message": "Quiz not prepared."}

    idx = int(tool_context.state.get(QUIZ_INDEX_KEY, 0)) if tool_context else 0
    mistakes = int(tool_context.state.get(QUIZ_MISTAKES_KEY, 0)) if tool_context else 0

    if correct:
        idx += 1
        mistakes = 0
    else:
        mistakes += 1

    if tool_context:
        tool_context.state[QUIZ_INDEX_KEY] = idx
        tool_context.state[QUIZ_MISTAKES_KEY] = mistakes

    done = idx >= len(snippets)

    return {
        "status": "success",
        "done": done,
        "next_question_number": min(idx + 1, len(snippets)),
        "total_questions": len(snippets),
        "mistakes_on_current": mistakes,
    }


def _reveal_context(tool_context: ToolContext = None) -> Dict[str, Any]:
    """Return full context for the current quiz item to help the learner."""

    snippets = tool_context.state.get(QUIZ_SNIPPETS_KEY, []) if tool_context else []
    if not snippets:
        return {"status": "error", "error_message": "Quiz not prepared."}

    idx = int(tool_context.state.get(QUIZ_INDEX_KEY, 0)) if tool_context else 0
    idx = max(0, min(idx, len(snippets) - 1))

    return {
        "status": "success",
        "context": snippets[idx],
        "question_number": idx + 1,
        "total_questions": len(snippets),
    }


# FunctionTool wrappers
prepare_quiz_tool = FunctionTool(func=_prepare_quiz)
get_quiz_step_tool = FunctionTool(func=_get_quiz_step)
advance_quiz_tool = FunctionTool(func=_advance_quiz)
reveal_context_tool = FunctionTool(func=_reveal_context)

__all__ = [
    "prepare_quiz_tool",
    "get_quiz_step_tool",
    "advance_quiz_tool",
    "reveal_context_tool",
]
