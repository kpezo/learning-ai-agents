# Questioning Agent System – Requirements and Prompt Templates

## 1) Recap of the Requested Behavior
- Input: One or more PDFs.
- Task: Extract main concepts, their relationships, and classify knowledge as Declarative (what), Procedural (how/usage), and Conditional (when/when-not).
- Output: A list of concepts and relationships with fields: what it is, how it works, how to use it, when to use, when not to use.
- Questioning: Ask atomic clarifying questions (cover big-picture and details). Each question should involve at most 2–3 connected concepts. Track user answers, judge sufficiency, and ask follow-ups if answers are weak.
- Goal: Improve understanding of concepts/relationships via iterative Q&A until information is satisfactory.

## 2) Concept & Relationship Schema
- Concept:
  - Name
  - Declarative: What is it?
  - Procedural: How does it work? How do I use it?
  - Conditional: When should I use it? When should I avoid it?
- Relationship (between 2–3 concepts):
  - Type (e.g., depends-on, enables, alternative-to, part-of, sequence-before/after)
  - Directionality (if applicable)
  - Rationale (why the relationship exists)
  - Usage impact (how it changes “how/when to use”)

## 3) High-Level Agentic Workflow (suggested)
1) Ingest PDFs → chunk text → embed for retrieval.
2) Extract candidate concepts and relationships (summaries + scores).
3) Normalize concepts (merge duplicates, disambiguate).
4) Fill Declarative/Procedural/Conditional fields from source text; mark gaps/low-confidence items.
5) Generate atomic clarifying questions to close gaps:
   - Big-picture first (scope, goals, primary flows).
   - Then details (edge cases, constraints, examples).
   - Each question references ≤2–3 concepts.
6) Present questions, capture answers, assess sufficiency:
   - If vague/partial/conflicting → ask follow-up.
   - If complete → update concept/relationship fields and confidence.
7) Iterate until all concepts/relationships meet quality thresholds.
8) Deliver final map: concepts, relationships, Q&A history, open gaps (if any).

## 4) Multi-Agent Split (use smaller prompts per role)
- Ingestion Agent: Chunk PDFs, store embeddings, surface top passages.
- Concept Agent: Extract concepts with declarative/procedural/conditional drafts.
- Relationship Agent: Map 2–3-concept relations with type/direction/rationale/usage impact.
- Question Planner: Turn gaps into ordered questions (big-picture → detail).
- Follow-up Judge: Score user answers; ask targeted follow-ups; update map.
- Orchestrator: Routes calls, merges updates, tracks confidence/gaps.

## 5) Question Design Rules
- Atomic: single focused ask; avoid multi-part.
- Scope: big-picture → then detailed; avoid jumping to minutiae first.
- Concepts per question: ≤2–3.
- Coverage: ensure declarative + procedural + conditional are all covered.
- Follow-ups: trigger when answers lack clarity, examples, constraints, or conflict prior info.
- Examples required: when asking “how to use,” request a concrete example.

## 6) Prompt Snippets by Agent

### Ingestion Agent (short)
```
Input: PDF chunks.
Task: Chunk and embed; return top-N passages with IDs for retrieval.
Output: [{id, text, score}]
```

### Concept Agent (short)
```
Input: retrieved passages.
Task: Extract ≤20 concepts. For each: declarative (what), procedural (how/usage), conditional (when/when-not), confidence. Note gaps.
Output: concepts list + gaps.
```

### Relationship Agent (short)
```
Input: concepts, passages.
Task: Propose relationships (2–3 concepts): type, direction, rationale, usage impact, confidence. Flag unclear items.
Output: relationships list + gaps.
```

### Question Planner (short)
```
Input: current concepts/relationships + gaps.
Task: Emit 3–6 ordered questions (big-picture first, then detail). Atomic; ≤3 concepts referenced. Cover declarative/procedural/conditional gaps.
Output: [{stage: big-picture|detail, text}]
```

### Follow-up Judge (short)
```
Input: question, user answer, target fields.
Task: Rate sufficiency; if weak/contradictory/missing examples → ask ONE follow-up. If sufficient, update fields/confidence and mark gap closed.
Output: status (sufficient|followup-needed), updated fields, next_question (optional).
```

### Orchestrator (short)
```
Input: user PDF + Q/A history + component outputs.
Task: Route calls, merge updates, track confidence/gaps, decide when to stop, deliver final map + Q&A history.
Output: updated state.
```

### 6.1 Example “Big Picture” Questions
- “What is the primary goal of <Concept A> and how does it fit with <Concept B>?”
- “Which 1–2 main problems does <Concept A> solve, and when would you choose it over <Concept B>?”
- “How do the major steps of <Concept A> flow from start to finish?”

### 6.2 Example “Detail” Questions
- Declarative: “What is the precise definition of <Concept A>, and how does it differ from <Concept B>?”
- Procedural: “List the key steps to use <Concept A> in practice; include a concrete example.”
- Conditional: “When should <Concept A> be preferred over <Concept B>, and when should it be avoided?”
- Relationship: “How does <Concept A> depend on <Concept B>? What breaks if <Concept B> is missing?”

### 6.3 Satisfaction Checks
```
After each answer:
- If vague (no specifics/examples) → follow-up: “Can you give a concrete example of <X>?”
- If conflicting → follow-up: “You mentioned <claim1> and <claim2>; which is correct, and why?”
- If complete → acknowledge and mark gap closed.
```

## 7) Output Format (suggested)
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
  "relationships": [
    {
      "between": ["ConceptA", "ConceptB"],
      "type": "...",
      "direction": "...",
      "rationale": "...",
      "usage_impact": "...",
      "confidence": 0.0-1.0
    }
  ],
  "questions_pending": [
    {"stage": "big-picture|detail", "text": "..."}
  ],
  "answered_history": [
    {"question": "...", "answer": "...", "status": "sufficient|followup-needed"}
  ],
  "gaps": ["..."]
}
```

## 8) Minimal Runbook
1) Ingest PDFs and extract concepts/relationships (use 5.1, 5.2).
2) Identify gaps; generate big-picture questions first (5.3).
3) Ask user; evaluate answers (5.4, 5.7); update map.
4) Move to detailed questions; iterate until gaps resolved.
5) Deliver final concept/relationship map + answered Q&A + remaining gaps.
