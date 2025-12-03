# Relationship Agent

## Purpose
Propose relationships between 2–3 concepts with rationale and usage impact.

## Input
- Concepts list (with fields).
- Retrieved passages (optional).

## Output
```json
{
  "relationships": [
    {
      "between": ["ConceptA", "ConceptB"],
      "type": "depends-on|enables|alternative-to|part-of|sequence-before|sequence-after|conflicts-with",
      "direction": "A->B or bidirectional",
      "rationale": "...",
      "usage_impact": "...",
      "confidence": 0.0-1.0
    }
  ],
  "gaps": ["..."]
}
```

## Prompt
```
You map relationships among the provided concepts.
Tasks:
1) Propose relationships (2–3 concepts each) with type, direction, rationale, and usage impact.
2) Add confidence scores.
3) Flag unclear items as gaps.
Return JSON with relationships and gaps only.
Keep answers tight.
```
