"""Quiz flow tools using ADK ToolContext for session state.

Flow (aligned with Day2/Day3 patterns):
- prepare_quiz(topic): fetch RAG snippets, cache in session state, persist to storage.
- get_quiz_step(): return current snippet hint and progress.
- advance_quiz(correct): update progress; on incorrect, stay on the same item.
- reveal_context(): return the full snippet for extra help when the learner struggles.

Storage integration:
- Quiz starts are recorded with start_quiz()
- Progress updates are persisted after each advance_quiz()
- Concept mastery is updated based on correct/incorrect answers
"""

from typing import Any, Dict, List

from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

try:
    from adk.rag_setup import get_retriever

    _retriever = get_retriever()
except Exception:
    _retriever = None

try:
    from adk.storage import get_storage
except Exception:
    get_storage = None


QUIZ_SNIPPETS_KEY = "quiz:snippets"
QUIZ_TOPIC_KEY = "quiz:topic"
QUIZ_INDEX_KEY = "quiz:index"
QUIZ_MISTAKES_KEY = "quiz:mistakes"
QUIZ_TOTAL_MISTAKES_KEY = "quiz:total_mistakes"
QUIZ_CORRECT_KEY = "quiz:correct"
QUIZ_ID_KEY = "quiz:db_id"
QUIZ_QUESTION_DETAILS_KEY = "quiz:question_details"


def _get_user_id(tool_context: ToolContext) -> str:
    """Extract user_id from tool context, default to 'default_user'."""
    if tool_context and hasattr(tool_context, "user_id"):
        return tool_context.user_id or "default_user"
    return "default_user"


def _get_session_id(tool_context: ToolContext) -> str:
    """Extract session_id from tool context."""
    if tool_context and hasattr(tool_context, "session_id"):
        return tool_context.session_id or "default_session"
    return "default_session"


def _prepare_quiz(
    topic: str, max_chunks: int = 3, tool_context: ToolContext = None
) -> Dict[str, Any]:
    """Initialize quiz state from RAG snippets for a topic.

    Stores snippets and progress counters in session state.
    Records quiz start in persistent storage.
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

    quiz_id = None
    if tool_context:
        tool_context.state[QUIZ_SNIPPETS_KEY] = snippets
        tool_context.state[QUIZ_TOPIC_KEY] = topic
        tool_context.state[QUIZ_INDEX_KEY] = 0
        tool_context.state[QUIZ_MISTAKES_KEY] = 0
        tool_context.state[QUIZ_TOTAL_MISTAKES_KEY] = 0
        tool_context.state[QUIZ_CORRECT_KEY] = 0
        tool_context.state[QUIZ_QUESTION_DETAILS_KEY] = []

        # Persist to storage
        if get_storage:
            try:
                user_id = _get_user_id(tool_context)
                session_id = _get_session_id(tool_context)
                storage = get_storage(user_id)
                quiz_id = storage.start_quiz(session_id, topic, len(snippets))
                tool_context.state[QUIZ_ID_KEY] = quiz_id
            except Exception:
                pass  # Storage errors shouldn't break quiz flow

    return {
        "status": "success",
        "topic": topic,
        "total_questions": len(snippets),
        "current_index": 0,
        "quiz_id": quiz_id,
    }


def _get_quiz_step(tool_context: ToolContext = None) -> Dict[str, Any]:
    """Return the current quiz step with a hint snippet."""

    snippets = tool_context.state.get(QUIZ_SNIPPETS_KEY, []) if tool_context else []
    if not snippets:
        return {
            "status": "error",
            "error_message": "Quiz not prepared. Call prepare_quiz first.",
        }

    idx = int(tool_context.state.get(QUIZ_INDEX_KEY, 0)) if tool_context else 0
    idx = max(0, min(idx, len(snippets) - 1))
    topic = tool_context.state.get(QUIZ_TOPIC_KEY, "") if tool_context else ""
    mistakes = (
        int(tool_context.state.get(QUIZ_MISTAKES_KEY, 0)) if tool_context else 0
    )

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


def _advance_quiz(
    correct: bool, concept_name: str = "", tool_context: ToolContext = None
) -> Dict[str, Any]:
    """Update quiz progress. If correct, move to next; if not, stay and track mistakes.

    Args:
        correct: Whether the answer was correct.
        concept_name: Optional concept being tested (for mastery tracking).
        tool_context: ADK tool context for session state.
    """

    snippets = tool_context.state.get(QUIZ_SNIPPETS_KEY, []) if tool_context else []
    if not snippets:
        return {"status": "error", "error_message": "Quiz not prepared."}

    idx = int(tool_context.state.get(QUIZ_INDEX_KEY, 0)) if tool_context else 0
    mistakes = (
        int(tool_context.state.get(QUIZ_MISTAKES_KEY, 0)) if tool_context else 0
    )
    total_mistakes = (
        int(tool_context.state.get(QUIZ_TOTAL_MISTAKES_KEY, 0)) if tool_context else 0
    )
    total_correct = (
        int(tool_context.state.get(QUIZ_CORRECT_KEY, 0)) if tool_context else 0
    )
    question_details = (
        tool_context.state.get(QUIZ_QUESTION_DETAILS_KEY, []) if tool_context else []
    )
    topic = tool_context.state.get(QUIZ_TOPIC_KEY, "") if tool_context else ""

    if correct:
        # Record question result before advancing
        question_details.append(
            {
                "question_number": idx + 1,
                "correct": True,
                "attempts": mistakes + 1,
                "concept": concept_name or topic,
            }
        )
        idx += 1
        total_correct += 1
        mistakes = 0
    else:
        mistakes += 1
        total_mistakes += 1

    if tool_context:
        tool_context.state[QUIZ_INDEX_KEY] = idx
        tool_context.state[QUIZ_MISTAKES_KEY] = mistakes
        tool_context.state[QUIZ_TOTAL_MISTAKES_KEY] = total_mistakes
        tool_context.state[QUIZ_CORRECT_KEY] = total_correct
        tool_context.state[QUIZ_QUESTION_DETAILS_KEY] = question_details

        # Persist progress to storage
        if get_storage:
            try:
                user_id = _get_user_id(tool_context)
                storage = get_storage(user_id)
                quiz_id = tool_context.state.get(QUIZ_ID_KEY)

                # Update quiz progress
                if quiz_id:
                    storage.update_quiz_progress(
                        quiz_id, total_correct, total_mistakes, question_details
                    )

                # Update concept mastery if concept provided
                if concept_name:
                    storage.update_mastery(concept_name, correct)
            except Exception:
                pass

    done = idx >= len(snippets)

    # Mark quiz complete in storage
    if done and tool_context and get_storage:
        try:
            user_id = _get_user_id(tool_context)
            storage = get_storage(user_id)
            quiz_id = tool_context.state.get(QUIZ_ID_KEY)
            if quiz_id:
                storage.complete_quiz(quiz_id)
        except Exception:
            pass

    return {
        "status": "success",
        "done": done,
        "next_question_number": min(idx + 1, len(snippets)),
        "total_questions": len(snippets),
        "mistakes_on_current": mistakes,
        "total_correct": total_correct,
        "total_mistakes": total_mistakes,
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


def _get_learning_stats(tool_context: ToolContext = None) -> Dict[str, Any]:
    """Get user's learning statistics from persistent storage."""

    if not get_storage:
        return {"status": "error", "error_message": "Storage not available."}

    try:
        user_id = _get_user_id(tool_context) if tool_context else "default_user"
        storage = get_storage(user_id)
        stats = storage.get_user_stats()
        return {"status": "success", **stats}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def _get_weak_concepts(
    threshold: float = 0.5, tool_context: ToolContext = None
) -> Dict[str, Any]:
    """Get concepts the user is struggling with.

    Args:
        threshold: Mastery threshold below which concepts are considered weak.
    """

    if not get_storage:
        return {"status": "error", "error_message": "Storage not available."}

    try:
        user_id = _get_user_id(tool_context) if tool_context else "default_user"
        storage = get_storage(user_id)
        weak = storage.get_weak_concepts(threshold)
        return {
            "status": "success",
            "weak_concepts": [
                {
                    "name": c.concept_name,
                    "mastery": c.mastery_level,
                    "times_seen": c.times_seen,
                    "times_correct": c.times_correct,
                }
                for c in weak
            ],
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def _get_quiz_history(
    topic: str = "", limit: int = 10, tool_context: ToolContext = None
) -> Dict[str, Any]:
    """Get user's quiz history, optionally filtered by topic."""

    if not get_storage:
        return {"status": "error", "error_message": "Storage not available."}

    try:
        user_id = _get_user_id(tool_context) if tool_context else "default_user"
        storage = get_storage(user_id)
        history = storage.get_quiz_history(topic=topic if topic else None, limit=limit)
        return {
            "status": "success",
            "history": [
                {
                    "id": q.id,
                    "topic": q.topic,
                    "total_questions": q.total_questions,
                    "correct_answers": q.correct_answers,
                    "total_mistakes": q.total_mistakes,
                    "started_at": q.started_at,
                    "completed_at": q.completed_at,
                }
                for q in history
            ],
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


# FunctionTool wrappers
prepare_quiz_tool = FunctionTool(func=_prepare_quiz)
get_quiz_step_tool = FunctionTool(func=_get_quiz_step)
advance_quiz_tool = FunctionTool(func=_advance_quiz)
reveal_context_tool = FunctionTool(func=_reveal_context)
get_learning_stats_tool = FunctionTool(func=_get_learning_stats)
get_weak_concepts_tool = FunctionTool(func=_get_weak_concepts)
get_quiz_history_tool = FunctionTool(func=_get_quiz_history)

__all__ = [
    "prepare_quiz_tool",
    "get_quiz_step_tool",
    "advance_quiz_tool",
    "reveal_context_tool",
    "get_learning_stats_tool",
    "get_weak_concepts_tool",
    "get_quiz_history_tool",
]
