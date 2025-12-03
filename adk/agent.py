"""ADK scaffold for education-focused hierarchical agents.

Defines three specialists (Tutor, Curriculum Planner, Assessor) and a
supervisor/root agent that can delegate. Uses Gemini via Google ADK.
"""

import os
from typing import List

from google.adk.agents import Agent, LlmAgent
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.models.google_llm import Gemini
from google.adk.tools import preload_memory

from adk.tools import fetch_info_tool, get_quiz_source_tool
from adk.quiz_tools import (
    advance_quiz_tool,
    get_quiz_step_tool,
    prepare_quiz_tool,
    reveal_context_tool,
    get_learning_stats_tool,
    get_weak_concepts_tool,
    get_quiz_history_tool,
    extract_topics_tool,
)
from adk.difficulty import (
    get_difficulty_level_tool,
    set_difficulty_level_tool,
    record_performance_tool,
)
from adk.scaffolding import get_scaffolding_tool


def _gemini_model() -> Gemini:
    # Uses Day1 retry guidance defaults; override via env if needed.
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    return Gemini(model=model_name)


def _base_instruction(role: str) -> str:
    base = (
        f"You are a {role} working with students."
        " Ground every response in the provided snippets or retrieved context."
        " Be concise and actionable."
        " For quizzes: call prepare_quiz(topic) once, then get_quiz_step to pull the"
        " current item, ask one question at a time, and only move on after"
        " advance_quiz(correct=True). If the learner is wrong, call"
        " advance_quiz(correct=False) and reveal_context to give more detail before"
        " retrying."
    )

    # Add difficulty guidance for Assessor
    if role == "Assessor":
        base += (
            "\n\nADAPTIVE DIFFICULTY SYSTEM:"
            " Before generating questions, call get_difficulty_level() to get the current"
            " difficulty (1-6) and allowed question types. Generate questions ONLY from the"
            " allowed types for that level:"
            "\n- Level 1 (Foundation): definition, recognition, true_false"
            "\n- Level 2 (Understanding): explanation, comparison, cause_effect"
            "\n- Level 3 (Application): scenario, case_study, problem_solving"
            "\n- Level 4 (Analysis): breakdown, pattern_recognition, critique"
            "\n- Level 5 (Synthesis): design, integration, hypothesis"
            "\n- Level 6 (Mastery): teach_back, edge_case, meta_cognition"
            "\n\nThe difficulty adjusts automatically based on performance (advance_quiz handles this)."
            " If scaffolding is active (indicated in get_difficulty_level), provide hints before questions."
        )

    return base


def _make_specialist(role: str, extra_tools: List = None) -> LlmAgent:
    tools = [
        fetch_info_tool,
        get_quiz_source_tool,
        prepare_quiz_tool,
        get_quiz_step_tool,
        advance_quiz_tool,
        reveal_context_tool,
        get_learning_stats_tool,
        get_weak_concepts_tool,
        get_quiz_history_tool,
        extract_topics_tool,
        preload_memory,
    ]
    if extra_tools:
        tools.extend(extra_tools)

    return LlmAgent(
        name=role.lower().replace(" ", "_"),
        description=f"{role} agent for education tasks.",
        model=_gemini_model(),
        instruction=_base_instruction(role),
        tools=tools,
    )


# Specialists
tutor_agent = _make_specialist("Tutor")
curriculum_planner_agent = _make_specialist("Curriculum Planner")
assessor_agent = _make_specialist(
    "Assessor",
    extra_tools=[
        get_difficulty_level_tool,
        set_difficulty_level_tool,
        record_performance_tool,
        get_scaffolding_tool,
    ]
)


# Root supervisor agent that can delegate to specialists via sub_agents.
root_agent = Agent(
    name="education_supervisor",
    model=_gemini_model(),
    description=(
        "Supervisor that decides whether the Tutor, Curriculum Planner, or Assessor"
        " should act next. Use sub-agents for focused work; include rationale in outputs."
    ),
    instruction=(
        "Route tasks to the right specialist."
        " Keep responses short and cite which agent contributed."
        " Ask clarifying questions if requirements are ambiguous."
    ),
    tools=[
        fetch_info_tool,
        get_quiz_source_tool,
        prepare_quiz_tool,
        get_quiz_step_tool,
        advance_quiz_tool,
        reveal_context_tool,
        get_learning_stats_tool,
        get_weak_concepts_tool,
        get_quiz_history_tool,
        extract_topics_tool,
        preload_memory,
    ],
    sub_agents=[tutor_agent, curriculum_planner_agent, assessor_agent],
)


# Optional App wrapper with compaction; runner can choose to use agent or app.
app = App(
    name="education_app",
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=6,
        overlap_size=2,
    ),
)

__all__ = [
    "root_agent",
    "app",
    "tutor_agent",
    "curriculum_planner_agent",
    "assessor_agent",
]
