"""Knowledge Graph ADK Tools Contract.

This module defines the ADK FunctionTool interfaces for graph operations.
Implementation will be in adk/graph_tools.py.
"""

from typing import Any, Dict, List, Optional


# ============================================================
# ADK Tool Function Signatures
# ============================================================


def get_concept(name: str) -> Dict[str, Any]:
    """Look up a concept by name or alias.

    Args:
        name: The concept name or alias to search for

    Returns:
        Dictionary with concept details:
        {
            "status": "found" | "not_found",
            "concept": {
                "id": int,
                "name": str,
                "node_type": str,
                "hierarchy_level": int,
                "description": str,
                "difficulty": str,
                "bloom_level": str,
                "estimated_time_minutes": int
            } | None,
            "alternatives": [str]  # Similar names if not exact match
        }
    """
    ...


def get_prerequisites(
    concept_id: int,
    strength: Optional[str] = None,
    transitive: bool = True,
) -> Dict[str, Any]:
    """Get all prerequisites for a concept.

    Args:
        concept_id: The concept to find prerequisites for
        strength: Filter by 'hard', 'soft', or 'recommended' (optional)
        transitive: If True, get transitive closure of prerequisites

    Returns:
        Dictionary with prerequisites:
        {
            "status": "success" | "not_found",
            "concept_name": str,
            "prerequisites": [
                {
                    "id": int,
                    "name": str,
                    "strength": str,
                    "is_direct": bool
                }
            ],
            "total_count": int
        }
    """
    ...


def get_descendants(
    concept_id: int,
    max_depth: Optional[int] = None,
) -> Dict[str, Any]:
    """Get all descendants of a concept in the hierarchy.

    Args:
        concept_id: The ancestor concept ID
        max_depth: Maximum hierarchy depth to traverse (optional)

    Returns:
        Dictionary with descendants:
        {
            "status": "success" | "not_found",
            "concept_name": str,
            "descendants": [
                {
                    "id": int,
                    "name": str,
                    "node_type": str,
                    "hierarchy_level": int,
                    "depth_from_root": int
                }
            ],
            "total_count": int
        }
    """
    ...


def get_ancestors(concept_id: int) -> Dict[str, Any]:
    """Get all ancestors of a concept (path to root).

    Args:
        concept_id: The descendant concept ID

    Returns:
        Dictionary with ancestors (ordered root-first):
        {
            "status": "success" | "not_found",
            "concept_name": str,
            "ancestors": [
                {
                    "id": int,
                    "name": str,
                    "node_type": str,
                    "hierarchy_level": int
                }
            ],
            "path": str  # "Domain > Course > Module > Topic > Concept"
        }
    """
    ...


def get_related_concepts(
    concept_id: int,
    relationship_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Get concepts related to a given concept.

    Args:
        concept_id: The concept to find relations for
        relationship_type: Filter by type (optional):
            'prerequisite', 'enables', 'part_of', 'contains',
            'similar_to', 'related_to', 'contradicts', 'exemplifies',
            'applies_to', 'extends', 'teaches', 'assesses'

    Returns:
        Dictionary with related concepts:
        {
            "status": "success" | "not_found",
            "concept_name": str,
            "related": [
                {
                    "id": int,
                    "name": str,
                    "relationship_type": str,
                    "direction": "outgoing" | "incoming",
                    "confidence": float
                }
            ],
            "by_type": {
                "prerequisite": [names],
                "similar_to": [names],
                ...
            }
        }
    """
    ...


def find_learning_path(
    start_concept_id: int,
    target_concept_id: int,
) -> Dict[str, Any]:
    """Find an optimal learning path between two concepts.

    Args:
        start_concept_id: Where the learner currently is
        target_concept_id: The goal concept to learn

    Returns:
        Dictionary with learning path:
        {
            "status": "found" | "no_path" | "error",
            "start": str,
            "target": str,
            "path": [
                {
                    "order": int,
                    "id": int,
                    "name": str,
                    "estimated_time_minutes": int,
                    "difficulty": str
                }
            ],
            "total_concepts": int,
            "total_time_minutes": int
        }
    """
    ...


def search_concepts(
    query: str,
    node_type: Optional[str] = None,
    bloom_level: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """Search for concepts by text query.

    Args:
        query: Search text (matches name, description, aliases)
        node_type: Filter by type (optional)
        bloom_level: Filter by Bloom's level (optional)
        difficulty: Filter by difficulty (optional)
        limit: Maximum results to return

    Returns:
        Dictionary with search results:
        {
            "status": "success",
            "query": str,
            "results": [
                {
                    "id": int,
                    "name": str,
                    "node_type": str,
                    "description": str,
                    "match_type": "name" | "alias" | "description"
                }
            ],
            "total_found": int
        }
    """
    ...


def get_concept_details(concept_id: int) -> Dict[str, Any]:
    """Get full details of a concept including relationships.

    Args:
        concept_id: The concept ID to get details for

    Returns:
        Dictionary with full concept details:
        {
            "status": "success" | "not_found",
            "concept": {
                "id": int,
                "name": str,
                "node_type": str,
                "hierarchy_level": int,
                "description": str,
                "aliases": [str],
                "difficulty": str,
                "bloom_level": str,
                "estimated_time_minutes": int,
                "importance_weight": float,
                "provenance": {
                    "source_document": str,
                    "page_numbers": [int],
                    "extraction_method": str,
                    "confidence_score": float
                }
            },
            "parent": {"id": int, "name": str} | None,
            "children_count": int,
            "prerequisites_count": int,
            "related_count": int
        }
    """
    ...


def get_graph_overview() -> Dict[str, Any]:
    """Get statistics about the knowledge graph.

    Returns:
        Dictionary with graph statistics:
        {
            "status": "success",
            "nodes": {
                "total": int,
                "by_type": {
                    "domain": int,
                    "course": int,
                    ...
                },
                "by_level": {
                    "1": int,
                    "2": int,
                    ...
                }
            },
            "relationships": {
                "total": int,
                "by_type": {
                    "prerequisite": int,
                    "similar_to": int,
                    ...
                }
            },
            "coverage": {
                "with_bloom_level": float,  # 0.0-1.0
                "with_difficulty": float,
                "with_time_estimate": float
            }
        }
    """
    ...


# ============================================================
# Tool Definitions for ADK Agent
# ============================================================

# These tools will be instantiated in adk/graph_tools.py:
#
# from google.adk.tools import FunctionTool
#
# get_concept_tool = FunctionTool(func=get_concept)
# get_prerequisites_tool = FunctionTool(func=get_prerequisites)
# get_descendants_tool = FunctionTool(func=get_descendants)
# get_ancestors_tool = FunctionTool(func=get_ancestors)
# get_related_concepts_tool = FunctionTool(func=get_related_concepts)
# find_learning_path_tool = FunctionTool(func=find_learning_path)
# search_concepts_tool = FunctionTool(func=search_concepts)
# get_concept_details_tool = FunctionTool(func=get_concept_details)
# get_graph_overview_tool = FunctionTool(func=get_graph_overview)
#
# GRAPH_TOOLS = [
#     get_concept_tool,
#     get_prerequisites_tool,
#     get_descendants_tool,
#     get_ancestors_tool,
#     get_related_concepts_tool,
#     find_learning_path_tool,
#     search_concepts_tool,
#     get_concept_details_tool,
#     get_graph_overview_tool,
# ]
