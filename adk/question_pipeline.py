"""Questioning pipeline wired with ADK agents.

Pipeline:
1) Ingestion agent: load PDF passages (function tool).
2) Concept agent: extract concepts (declarative/procedural/conditional).
3) Relationship agent: map relationships.
4) Question planner: propose clarifying questions.

Run via `python -m adk.run_dev` (uses this pipeline by default).
"""

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from google.adk.agents import Agent, LlmAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool, AgentTool

from rag_setup import build_retriever

PROMPTS_DIR = Path("AgentsExplanations/agents")


def _load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text()


def ingest_pdf(pdf_path: str | None = None, top_n: int = 20) -> Dict[str, Any]:
    """Return top passages from the PDF."""
    path = pdf_path or os.getenv("PDF_PATH", "Intro.pdf")
    retriever = build_retriever(path)
    passages = []
    for idx, chunk in enumerate(retriever.chunks[:top_n]):
        passages.append({"id": str(idx), "text": chunk, "score": 1.0})
    return {"passages": passages}


# Tool wrapper for ingestion
ingest_pdf_tool = FunctionTool(
    func=ingest_pdf,
)


@lru_cache(maxsize=1)
def _model() -> Gemini:
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    return Gemini(model=model_name)


# Instantiate agents with their prompts.
ingestion_agent = LlmAgent(
    name="ingestion",
    model=_model(),
    instruction=_load_prompt("ingestion-agent.md"),
    description="Ingest PDF and surface passages.",
    tools=[ingest_pdf_tool],
    output_key="passages",
)

concept_agent = LlmAgent(
    name="concept",
    model=_model(),
    instruction=_load_prompt("concept-agent.md")
    + "\n\nContext passages:\n{passages}",
    description="Extract concepts with declarative/procedural/conditional fields.",
    output_key="concepts",
)

relationship_agent = LlmAgent(
    name="relationship",
    model=_model(),
    instruction=_load_prompt("relationship-agent.md")
    + "\n\nConcepts:\n{concepts}\n\nPassages:\n{passages}",
    description="Map relationships among concepts.",
    output_key="relationships",
)

question_planner_agent = LlmAgent(
    name="question_planner",
    model=_model(),
    instruction=_load_prompt("question-planner.md")
    + "\n\nConcepts:\n{concepts}\n\nRelationships:\n{relationships}",
    description="Generate clarifying questions.",
    output_key="questions",
)


# Sequential pipeline for predictable ordering.
question_pipeline = SequentialAgent(
    name="question_pipeline",
    sub_agents=[
        ingestion_agent,
        concept_agent,
        relationship_agent,
        question_planner_agent,
    ],
)


# Root agent wraps pipeline as a sub-agent for clean routing.
root_agent = Agent(
    name="question_orchestrator",
    model=_model(),
    description="Orchestrates PDF understanding and questioning.",
    instruction=(
        "Run the questioning pipeline: ingest the PDF, extract concepts, map relationships, "
        "and generate clarifying questions. Return a concise status and include the JSON outputs."
    ),
    tools=[AgentTool(question_pipeline)],
)

__all__ = [
    "root_agent",
    "question_pipeline",
    "ingestion_agent",
    "concept_agent",
    "relationship_agent",
    "question_planner_agent",
]
