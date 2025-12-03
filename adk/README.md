# ADK Scaffold (Education Agents)

This folder provides a Google ADK-based version of the tutor/curriculum/assessor workflow.

## Setup
1) Install deps (separate from LangGraph stack if you want):
```bash
pip install -r adk/requirements.txt
```

2) Set credentials and paths:
```bash
export GOOGLE_API_KEY=...             # Gemini key
export PDF_PATH=/path/to/textbook.pdf # RAG source; defaults to education_textbook.pdf
export GEMINI_MODEL=gemini-2.5-flash-lite  # optional override
# Optional: OPENAI_API_KEY if your rag_setup uses OpenAI embeddings
```

## Run locally
```bash
python -m adk.run_dev
```
Streams intermediate and final responses; adjust the scenario in `adk/run_dev.py`.

## Agents & tools
- `tutor_agent`, `curriculum_planner_agent`, `assessor_agent`: specialists.
- `root_agent`: supervisor that delegates to specialists; also exposed via `app` with context compaction.
- Quiz flow tools (`prepare_quiz`, `get_quiz_step`, `advance_quiz`, `reveal_context`) track quiz state in session and surface context when the learner struggles.

## RAG + quiz tools
- `fetch_info_tool`: returns snippets from the PDF.
- `get_quiz_source_tool`: returns labeled snippets for quiz generation.
- Quiz tools manage stateful questioning; they keep the current question until the learner answers correctly, and `reveal_context` provides more detail after misses.

If the RAG retriever is not initialized, the tools return a structured error to keep runs from crashing.

## Next steps
- Add approvals for publish/grade actions using `ToolContext.request_confirmation` (Day2 pattern).
- Swap `InMemorySessionService`/`InMemoryMemoryService` in `adk/run_dev.py` for persistent services.
- Add eval sets (`adk/tests/*.evalset.json`) and a `test_config.json` to run `adk eval` in CI (Day4).
- For deployment, wrap `root_agent` with `adk api_server` (Cloud Run) or `adk deploy agent_engine` (Vertex AI Agent Engine); include `.agent_engine_config.json` as needed (Day5).
