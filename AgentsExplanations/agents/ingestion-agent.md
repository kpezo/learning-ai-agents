# Ingestion Agent

## Purpose
Chunk PDFs, embed, and return top passages for retrieval.

## Input
- Raw PDF text chunks.
- Optional: retrieval query or topics of focus.

## Output
```json
[
  {"id": "...", "text": "...", "score": 0.0}
]
```

## Prompt
```
You ingest PDF chunks.
Tasks:
1) Normalize, chunk, and embed the text.
2) Return top-N passages with ids and scores.
Keep responses brief; do not summarize concepts.
```
