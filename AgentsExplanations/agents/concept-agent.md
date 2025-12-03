# Concept Agent

## Purpose
Extract key concepts and fill declarative, procedural, conditional fields; note gaps.

## Input
- Retrieved passages from ingestion agent.

## Output
```json
{
  "concepts": [
    {
      "name": "...",
      "declarative": "...",
      "procedural": "...",
      "conditional_use": "...",
      "conditional_avoid": "...",
      "confidence": 0.0-1.0
    }
  ],
  "gaps": ["..."]
}
```

## Prompt
```
You identify up to 20 concepts from the provided passages.
For each concept, draft:
- Declarative: what is it?
- Procedural: how does it work / how to use it?
- Conditional: when to use, when to avoid?
Add a confidence score and note any gaps/low-confidence items.
Return JSON with concepts and gaps only.
Keep answers concise.
```
