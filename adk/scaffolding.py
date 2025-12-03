"""
Scaffolding support system for struggling learners.

Provides structured hints, learning strategies, and question simplification
based on detected struggle areas (definition, process, relationship, application).
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ScaffoldingSupport:
    """
    Structured hints and strategies for a specific struggle area.

    Attributes:
        struggle_area: Type of struggle (definition/process/relationship/application)
        hint_templates: Generic hint text templates
        strategies: Learning strategies to suggest
        question_simplification: How to simplify questions
        example_prompts: Example easier questions
    """
    struggle_area: str
    hint_templates: List[str]
    strategies: List[str]
    question_simplification: str
    example_prompts: List[str]


# Static scaffolding strategy configuration
SCAFFOLDING_STRATEGIES = {
    "definition": ScaffoldingSupport(
        struggle_area="definition",
        hint_templates=[
            "Let's start with the basic definition of {concept}.",
            "The key word here is {keyword}.",
            "Think about what {concept} means in simple terms."
        ],
        strategies=[
            "Focus on the core meaning first",
            "Look for keywords that define the concept",
            "Connect to something you already know"
        ],
        question_simplification="Ask for recognition instead of recall",
        example_prompts=[
            "Which of these best describes {concept}?",
            "True or false: {simple_statement}"
        ]
    ),
    "process": ScaffoldingSupport(
        struggle_area="process",
        hint_templates=[
            "Let's break this down step by step.",
            "The first step is to {step1}.",
            "What needs to happen before {step}?"
        ],
        strategies=[
            "Identify the sequence of steps",
            "Focus on one step at a time",
            "Think about the order things happen"
        ],
        question_simplification="Ask about individual steps",
        example_prompts=[
            "What is the first step in {process}?",
            "What comes after {step}?"
        ]
    ),
    "relationship": ScaffoldingSupport(
        struggle_area="relationship",
        hint_templates=[
            "Think about how {concept1} and {concept2} are connected.",
            "What do these concepts have in common?",
            "How does {concept1} affect {concept2}?"
        ],
        strategies=[
            "Look for cause and effect",
            "Identify similarities and differences",
            "Map out how concepts connect"
        ],
        question_simplification="Focus on single relationships",
        example_prompts=[
            "How are {concept1} and {concept2} similar?",
            "Does {concept1} depend on {concept2}?"
        ]
    ),
    "application": ScaffoldingSupport(
        struggle_area="application",
        hint_templates=[
            "Think about a simpler example first.",
            "What concept from the lesson applies here?",
            "Have you seen a similar situation before?"
        ],
        strategies=[
            "Start with a simpler version of the problem",
            "Identify which concept to apply",
            "Think about real-world examples"
        ],
        question_simplification="Provide more context",
        example_prompts=[
            "In this simple case, what would you do?",
            "Which approach would work for {scenario}?"
        ]
    )
}


# =============================================================================
# Core Logic Functions
# =============================================================================

def detect_struggle_area(recent_errors: List[Dict[str, Any]]) -> str:
    """
    Detect struggle area from recent error patterns.

    Args:
        recent_errors: List of recent error records with question_type and score

    Returns:
        Struggle area: definition, process, relationship, or application
    """
    if not recent_errors:
        return "definition"  # Default to foundational support

    # Map question types to struggle areas
    question_type_mapping = {
        # Definition struggles
        "definition": "definition",
        "recognition": "definition",
        "true_false": "definition",

        # Process struggles
        "problem_solving": "process",
        "breakdown": "process",

        # Relationship struggles
        "comparison": "relationship",
        "cause_effect": "relationship",
        "pattern_recognition": "relationship",

        # Application struggles
        "scenario": "application",
        "case_study": "application",
        "design": "application",
        "integration": "application",
    }

    # Count struggle areas from error patterns
    struggle_counts: Dict[str, int] = {
        "definition": 0,
        "process": 0,
        "relationship": 0,
        "application": 0,
    }

    for error in recent_errors:
        question_type = error.get("question_type", "")
        detected_area = question_type_mapping.get(question_type)

        if detected_area:
            struggle_counts[detected_area] += 1
        else:
            # Unknown question types default to definition
            struggle_counts["definition"] += 1

    # Return the most common struggle area
    max_area = max(struggle_counts, key=struggle_counts.get)

    # If no clear winner, default to definition
    if struggle_counts[max_area] == 0:
        return "definition"

    return max_area


def get_scaffolding_hints(
    struggle_area: str,
    concept: str = "",
) -> Dict[str, Any]:
    """
    Get scaffolding hints for a specific struggle area.

    Args:
        struggle_area: The detected struggle area
        concept: Optional concept name for hint substitution

    Returns:
        Dict with hint_templates, strategies, simplification, example_prompts
    """
    # Get strategy for struggle area, default to definition if invalid
    strategy = SCAFFOLDING_STRATEGIES.get(struggle_area, SCAFFOLDING_STRATEGIES["definition"])

    return {
        "hint_templates": strategy.hint_templates,
        "strategies": strategy.strategies,
        "simplification": strategy.question_simplification,
        "example_prompts": strategy.example_prompts,
    }


# =============================================================================
# ADK Tool Functions
# =============================================================================

def _get_scaffolding(tool_context=None) -> Dict[str, Any]:
    """
    Get scaffolding hints when scaffolding is active.

    Args:
        tool_context: ADK ToolContext with session state

    Returns:
        Dict with status, scaffolding_active, struggle_area, hints
    """
    if tool_context is None:
        return {"status": "error", "error_message": "No tool context provided"}

    scaffolding_active = tool_context.state.get("difficulty:scaffolding_active", False)

    if not scaffolding_active:
        return {
            "status": "success",
            "scaffolding_active": False,
            "message": "Scaffolding is not currently active",
        }

    # Get recent errors from history
    history = tool_context.state.get("difficulty:history", [])
    recent_errors = [
        {
            "question_type": record.get("question_type", ""),
            "score": record.get("score", 0.0),
            "concept": record.get("concept_tested", ""),
        }
        for record in history[:3]  # Look at last 3 records
        if record.get("score", 1.0) < 0.60  # Only errors
    ]

    # Detect struggle area
    struggle_area = detect_struggle_area(recent_errors)

    # Get scaffolding hints
    hints = get_scaffolding_hints(struggle_area)

    return {
        "status": "success",
        "scaffolding_active": True,
        "struggle_area": struggle_area,
        "hints": hints,
    }


# =============================================================================
# ADK FunctionTool Wrappers
# =============================================================================

try:
    from google.adk.tools import FunctionTool

    get_scaffolding_tool = FunctionTool(func=_get_scaffolding)

except ImportError:
    # ADK not installed, tool will be None
    get_scaffolding_tool = None
