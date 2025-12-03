"""Knowledge Graph Service API Contract.

This module defines the service layer interface for the knowledge graph.
Implementation will be in adk/graph.py.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol


# ============================================================
# Enums
# ============================================================


class NodeType(str, Enum):
    """Types of nodes in the knowledge graph."""

    DOMAIN = "domain"
    COURSE = "course"
    MODULE = "module"
    TOPIC = "topic"
    CONCEPT = "concept"
    SKILL = "skill"
    RESOURCE = "resource"
    ASSESSMENT = "assessment"


class RelationshipType(str, Enum):
    """Types of relationships between nodes."""

    PREREQUISITE = "prerequisite"
    ENABLES = "enables"
    PART_OF = "part_of"
    CONTAINS = "contains"
    SIMILAR_TO = "similar_to"
    RELATED_TO = "related_to"
    CONTRADICTS = "contradicts"
    EXEMPLIFIES = "exemplifies"
    APPLIES_TO = "applies_to"
    EXTENDS = "extends"
    TEACHES = "teaches"
    ASSESSES = "assesses"


class Difficulty(str, Enum):
    """Difficulty levels for concepts."""

    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class BloomLevel(str, Enum):
    """Bloom's Taxonomy cognitive levels."""

    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"


class PrerequisiteStrength(str, Enum):
    """Strength of prerequisite relationships."""

    HARD = "hard"
    SOFT = "soft"
    RECOMMENDED = "recommended"


class ExtractionMethod(str, Enum):
    """Method used to extract data."""

    MANUAL = "manual"
    LLM_EXTRACTED = "llm_extracted"
    RULE_BASED = "rule_based"


# ============================================================
# Data Classes
# ============================================================


@dataclass
class Provenance:
    """Tracks origin of extracted data."""

    source_document: str
    page_numbers: List[int] = field(default_factory=list)
    extraction_method: ExtractionMethod = ExtractionMethod.MANUAL
    confidence_score: float = 1.0
    extracted_by: Optional[str] = None
    extracted_at: Optional[datetime] = None


@dataclass
class ConceptNode:
    """A node in the knowledge graph."""

    id: Optional[int] = None
    name: str = ""
    node_type: NodeType = NodeType.CONCEPT
    hierarchy_level: int = 5
    parent_id: Optional[int] = None
    description: str = ""
    aliases: List[str] = field(default_factory=list)
    difficulty: Optional[Difficulty] = None
    bloom_level: Optional[BloomLevel] = None
    estimated_time_minutes: Optional[int] = None
    importance_weight: Optional[float] = None
    provenance: Optional[Provenance] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class RelationshipEdge:
    """A connection between two nodes."""

    id: Optional[int] = None
    source_id: int = 0
    target_id: int = 0
    relationship_type: RelationshipType = RelationshipType.RELATED_TO
    is_directed: bool = True
    strength: Optional[PrerequisiteStrength] = None
    evidence_text: str = ""
    confidence: float = 1.0
    provenance: Optional[Provenance] = None
    created_at: Optional[datetime] = None


@dataclass
class NodeWithChildren:
    """Node with its immediate children."""

    node: ConceptNode
    children: List[ConceptNode] = field(default_factory=list)


@dataclass
class LearningPath:
    """Ordered sequence of concepts for learning."""

    nodes: List[ConceptNode] = field(default_factory=list)
    total_time_minutes: int = 0
    difficulty_progression: List[Difficulty] = field(default_factory=list)


# ============================================================
# Service Protocol (Interface)
# ============================================================


class GraphService(Protocol):
    """Protocol defining the knowledge graph service interface."""

    # --------------------------------------------------------
    # Node Operations
    # --------------------------------------------------------

    def create_node(self, node: ConceptNode) -> int:
        """Create a new concept node.

        Args:
            node: The node to create (id will be assigned)

        Returns:
            The ID of the created node

        Raises:
            ValueError: If hierarchy_level inconsistent with parent
            ValueError: If required fields missing
        """
        ...

    def get_node(self, node_id: int) -> Optional[ConceptNode]:
        """Get a node by ID.

        Args:
            node_id: The node ID to retrieve

        Returns:
            The node if found, None otherwise
        """
        ...

    def get_node_by_name(self, name: str) -> Optional[ConceptNode]:
        """Get a node by name.

        Args:
            name: The node name or alias to search

        Returns:
            The first matching node, or None
        """
        ...

    def update_node(self, node: ConceptNode) -> bool:
        """Update an existing node.

        Args:
            node: The node with updated fields (id required)

        Returns:
            True if update succeeded, False if node not found

        Raises:
            ValueError: If hierarchy_level change violates constraints
        """
        ...

    def delete_node(self, node_id: int) -> bool:
        """Delete a node and its relationships.

        Args:
            node_id: The node ID to delete

        Returns:
            True if deleted, False if not found
        """
        ...

    # --------------------------------------------------------
    # Hierarchy Operations
    # --------------------------------------------------------

    def get_children(self, node_id: int) -> List[ConceptNode]:
        """Get immediate children of a node.

        Args:
            node_id: The parent node ID

        Returns:
            List of child nodes (empty if none)
        """
        ...

    def get_descendants(self, node_id: int) -> List[ConceptNode]:
        """Get all descendants of a node (children, grandchildren, etc.).

        Args:
            node_id: The ancestor node ID

        Returns:
            List of all descendant nodes
        """
        ...

    def get_ancestors(self, node_id: int) -> List[ConceptNode]:
        """Get all ancestors of a node (parents, grandparents, etc.).

        Args:
            node_id: The descendant node ID

        Returns:
            List of all ancestor nodes (root first)
        """
        ...

    def get_node_with_children(self, node_id: int) -> Optional[NodeWithChildren]:
        """Get a node with its immediate children.

        Args:
            node_id: The node ID

        Returns:
            NodeWithChildren if found, None otherwise
        """
        ...

    # --------------------------------------------------------
    # Relationship Operations
    # --------------------------------------------------------

    def create_relationship(self, edge: RelationshipEdge) -> int:
        """Create a new relationship between nodes.

        Args:
            edge: The relationship to create

        Returns:
            The ID of the created relationship

        Raises:
            ValueError: If would create circular hard prerequisite
            ValueError: If source or target node doesn't exist
        """
        ...

    def get_relationships(
        self,
        node_id: int,
        relationship_type: Optional[RelationshipType] = None,
        direction: str = "both",
    ) -> List[RelationshipEdge]:
        """Get relationships for a node.

        Args:
            node_id: The node ID
            relationship_type: Filter by type (optional)
            direction: 'outgoing', 'incoming', or 'both'

        Returns:
            List of matching relationships
        """
        ...

    def delete_relationship(self, edge_id: int) -> bool:
        """Delete a relationship.

        Args:
            edge_id: The relationship ID to delete

        Returns:
            True if deleted, False if not found
        """
        ...

    # --------------------------------------------------------
    # Prerequisite Operations
    # --------------------------------------------------------

    def get_prerequisites(
        self,
        node_id: int,
        strength: Optional[PrerequisiteStrength] = None,
        transitive: bool = True,
    ) -> List[ConceptNode]:
        """Get prerequisite nodes for a concept.

        Args:
            node_id: The concept node ID
            strength: Filter by strength (optional)
            transitive: If True, get all transitive prerequisites

        Returns:
            List of prerequisite nodes
        """
        ...

    def would_create_cycle(
        self, source_id: int, target_id: int, strength: PrerequisiteStrength
    ) -> bool:
        """Check if adding a prerequisite would create a cycle.

        Only applies to hard prerequisites.

        Args:
            source_id: The prerequisite node
            target_id: The dependent node
            strength: The prerequisite strength

        Returns:
            True if would create cycle, False otherwise
        """
        ...

    # --------------------------------------------------------
    # Query Operations
    # --------------------------------------------------------

    def search_nodes(
        self,
        query: str,
        node_type: Optional[NodeType] = None,
        bloom_level: Optional[BloomLevel] = None,
        difficulty: Optional[Difficulty] = None,
        limit: int = 20,
    ) -> List[ConceptNode]:
        """Search nodes by name, description, or aliases.

        Args:
            query: Search text
            node_type: Filter by type
            bloom_level: Filter by Bloom's level
            difficulty: Filter by difficulty
            limit: Maximum results

        Returns:
            Matching nodes
        """
        ...

    def find_learning_path(
        self, start_id: int, end_id: int
    ) -> Optional[LearningPath]:
        """Find a learning path between two concepts.

        Traverses prerequisites in reverse to build path.

        Args:
            start_id: Starting concept (learner's current position)
            end_id: Target concept

        Returns:
            Learning path if exists, None otherwise
        """
        ...

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph.

        Returns:
            Dictionary with counts, coverage, etc.
        """
        ...


# ============================================================
# Extraction Service Protocol
# ============================================================


class ExtractionService(Protocol):
    """Protocol for LLM-based concept extraction."""

    def extract_concepts_from_pdf(
        self, pdf_path: str, top_n_chunks: int = 20
    ) -> List[ConceptNode]:
        """Extract concepts from a PDF document.

        Args:
            pdf_path: Path to PDF file
            top_n_chunks: Number of chunks to process

        Returns:
            List of extracted concept nodes (not yet persisted)
        """
        ...

    def extract_relationships(
        self, concepts: List[ConceptNode], context_text: str
    ) -> List[RelationshipEdge]:
        """Extract relationships between concepts.

        Args:
            concepts: Previously extracted concepts
            context_text: Source text for evidence

        Returns:
            List of extracted relationships (not yet persisted)
        """
        ...

    def infer_hierarchy(self, concepts: List[ConceptNode]) -> List[ConceptNode]:
        """Infer hierarchy levels for concepts.

        Args:
            concepts: Concepts without hierarchy info

        Returns:
            Same concepts with hierarchy_level and parent_id set
        """
        ...

    def classify_bloom_level(self, concept: ConceptNode) -> BloomLevel:
        """Classify a concept's Bloom's taxonomy level.

        Args:
            concept: The concept to classify

        Returns:
            The inferred Bloom's level
        """
        ...
