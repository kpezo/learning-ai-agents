# Quickstart: Knowledge Graph Schema Enhancement

**Branch**: `006-knowledge-graph-schema`
**Estimated Setup Time**: 5 minutes

## Prerequisites

- Python 3.11+
- Existing ADK environment configured
- `GOOGLE_API_KEY` environment variable set

## Quick Setup

```bash
# 1. Install dependencies (if not already done)
pip install -r adk/requirements.txt

# 2. Verify environment
python -c "from google.adk.agents import Agent; print('ADK ready')"
```

## Basic Usage

### Create the Graph Service

```python
from adk.graph import GraphService
from adk.storage import DATA_DIR

# Initialize graph service (creates tables if needed)
graph = GraphService(user_id="dev_user", db_path=DATA_DIR / "dev_user.db")
```

### Add Concepts

```python
from adk.graph import ConceptNode, NodeType, BloomLevel, Difficulty

# Create a domain (level 1)
domain = ConceptNode(
    name="Machine Learning",
    node_type=NodeType.DOMAIN,
    hierarchy_level=1,
    description="The study of algorithms that improve through experience"
)
domain_id = graph.create_node(domain)

# Create a topic under the domain (level 3)
topic = ConceptNode(
    name="Supervised Learning",
    node_type=NodeType.TOPIC,
    hierarchy_level=3,
    parent_id=domain_id,
    difficulty=Difficulty.INTERMEDIATE,
    bloom_level=BloomLevel.UNDERSTAND
)
topic_id = graph.create_node(topic)

# Create a concept under the topic (level 4)
concept = ConceptNode(
    name="Linear Regression",
    node_type=NodeType.CONCEPT,
    hierarchy_level=4,
    parent_id=topic_id,
    difficulty=Difficulty.BEGINNER,
    bloom_level=BloomLevel.APPLY,
    estimated_time_minutes=30
)
concept_id = graph.create_node(concept)
```

### Add Relationships

```python
from adk.graph import RelationshipEdge, RelationshipType, PrerequisiteStrength

# Linear Algebra is a prerequisite for Linear Regression
prerequisite = RelationshipEdge(
    source_id=algebra_id,  # Linear Algebra concept
    target_id=concept_id,   # Linear Regression
    relationship_type=RelationshipType.PREREQUISITE,
    strength=PrerequisiteStrength.HARD,
    confidence=0.95
)
graph.create_relationship(prerequisite)
```

### Query the Graph

```python
# Get all prerequisites for a concept
prereqs = graph.get_prerequisites(concept_id, transitive=True)
print(f"Prerequisites: {[p.name for p in prereqs]}")

# Get hierarchy path
ancestors = graph.get_ancestors(concept_id)
print(f"Path: {' > '.join(a.name for a in ancestors)}")
# Output: "Machine Learning > Supervised Learning > Linear Regression"

# Find learning path
path = graph.find_learning_path(start_id=basics_id, end_id=concept_id)
print(f"Learning path: {path.total_time_minutes} minutes")
```

### Extract from PDF

```python
from adk.extraction import ExtractionService

extractor = ExtractionService()

# Extract concepts from PDF
concepts = extractor.extract_concepts_from_pdf("Intro.pdf")
print(f"Extracted {len(concepts)} concepts")

# Extract relationships
relationships = extractor.extract_relationships(concepts, context_text)

# Persist to graph
for c in concepts:
    graph.create_node(c)
for r in relationships:
    graph.create_relationship(r)
```

## Using ADK Tools

The graph functionality is exposed via ADK tools for agent use:

```python
from adk.agent import root_agent
from adk.graph_tools import GRAPH_TOOLS

# Add graph tools to your agent
tutor_with_graph = LlmAgent(
    name="tutor",
    model=gemini_model,
    instruction="Help learners understand concepts...",
    tools=[*existing_tools, *GRAPH_TOOLS]
)
```

### Tool Examples

```python
# Agent can call these tools:

# Look up a concept
result = get_concept("Linear Regression")
# Returns: {"status": "found", "concept": {...}}

# Get prerequisites
result = get_prerequisites(concept_id=42, transitive=True)
# Returns: {"prerequisites": [{"name": "Algebra", "strength": "hard"}]}

# Find learning path
result = find_learning_path(start_id=1, target_id=42)
# Returns: {"path": [...], "total_time_minutes": 120}
```

## Running Tests

```bash
# Unit tests
pytest tests/unit/test_graph.py -v

# Integration tests
pytest tests/integration/test_graph_storage.py -v

# All graph tests
pytest tests/ -k "graph" -v
```

## Common Tasks

### Import Existing Concepts

If you have concepts in the old `extracted_concepts` table:

```python
from adk.storage import get_storage
from adk.graph import GraphService, migrate_concepts

storage = get_storage("user123")
graph = GraphService("user123")

# Migrate old concepts to new graph schema
migrated = migrate_concepts(storage, graph)
print(f"Migrated {migrated} concepts")
```

### Validate Graph Integrity

```python
# Check for issues
issues = graph.validate()
if issues:
    print("Graph issues found:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("Graph is valid")
```

### Export Graph Statistics

```python
stats = graph.get_graph_stats()
print(f"Nodes: {stats['total_nodes']}")
print(f"Relationships: {stats['total_relationships']}")
print(f"Bloom coverage: {stats['bloom_coverage']:.1%}")
```

## Troubleshooting

### "Hierarchy level mismatch" Error

Ensure child nodes have `hierarchy_level = parent.hierarchy_level + 1`:

```python
# Wrong
parent = ConceptNode(hierarchy_level=1, ...)
child = ConceptNode(hierarchy_level=3, parent_id=parent_id, ...)  # Error!

# Correct
child = ConceptNode(hierarchy_level=2, parent_id=parent_id, ...)  # OK
```

### "Circular prerequisite detected" Error

Hard prerequisites cannot form cycles:

```python
# This will fail if A -> B -> C -> A exists
graph.create_relationship(RelationshipEdge(
    source_id=c_id,
    target_id=a_id,
    relationship_type=RelationshipType.PREREQUISITE,
    strength=PrerequisiteStrength.HARD  # Will raise ValueError
))

# Soft prerequisites can form cycles
graph.create_relationship(RelationshipEdge(
    strength=PrerequisiteStrength.SOFT  # OK
))
```

### Low Extraction Confidence

Concepts with confidence < 0.7 may need review:

```python
low_confidence = graph.search_nodes(
    query="",
    min_confidence=0.0,
    max_confidence=0.7
)
print(f"{len(low_confidence)} concepts need review")
```

## Next Steps

1. Read the full [spec.md](spec.md) for requirements
2. Review [data-model.md](data-model.md) for schema details
3. Check [contracts/](contracts/) for API definitions
4. Run `pytest tests/` to verify your setup
