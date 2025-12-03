🎯 Project Overview: Adaptive PDF Quiz Agent
Core Concept
An agentic system that ingests PDF documents and guides learners through a structured understanding journey: Big Picture → Deep Dive → Connections → Verification → Repeat until mastery is achieved.

🏗️ High-Level Architecture
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                              │
│              (Chat Interface / ADK Web UI)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ROOT COORDINATOR AGENT                        │
│         (Orchestrates learning flow & session management)        │
└─────────────────────────────────────────────────────────────────┘
           │              │              │              │
           ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Document   │ │   Concept    │ │    Quiz      │ │  Progress    │
│   Analyzer   │ │   Explorer   │ │  Generator   │ │   Tracker    │
│    Agent     │ │    Agent     │ │    Agent     │ │    Agent     │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
       │                                                   │
       ▼                                                   ▼
┌──────────────┐                                   ┌──────────────┐
│   PDF Tool   │                                   │   Session    │
│  (Extract)   │                                   │   Memory     │
└──────────────┘                                   └──────────────┘

🤖 Agent Definitions
1. Root Coordinator Agent (SequentialAgent + LLM Orchestration)
Purpose: Manages the overall learning flow and decides which phase to enter next.
pythonroot_agent = Agent(
    name="QuizCoordinator",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="""
    You orchestrate an adaptive learning experience.
    
    LEARNING PHASES:
    1. INGESTION: Process PDF and extract concepts
    2. BIG_PICTURE: Test understanding of main concepts
    3. DEEP_DIVE: Explore specific concept details
    4. CONNECTIONS: Test understanding of relationships
    5. SYNTHESIS: Verify holistic understanding
    
    Based on progress_tracker results, decide:
    - Move to next phase if mastery achieved
    - Repeat current phase with different questions if gaps exist
    - Switch to related concept if current is mastered
    """,
    tools=[AgentTool(document_analyzer), AgentTool(concept_explorer), 
           AgentTool(quiz_generator), AgentTool(progress_tracker)],
    output_key="session_state"
)
2. Document Analyzer Agent
Purpose: Extracts text, identifies concepts, builds knowledge graph.
pythondocument_analyzer = Agent(
    name="DocumentAnalyzer",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="""
    Analyze the PDF document and extract:
    1. MAIN CONCEPTS: Key topics (5-10 major concepts)
    2. SUB-CONCEPTS: Details under each main concept
    3. RELATIONSHIPS: How concepts connect to each other
    4. HIERARCHY: Parent-child relationships
    5. DEFINITIONS: Key terms and their meanings
    
    Output as structured JSON for the knowledge graph.
    """,
    tools=[FunctionTool(extract_pdf_text), FunctionTool(build_knowledge_graph)],
    output_key="knowledge_graph"
)
3. Concept Explorer Agent
Purpose: Navigates the knowledge graph and selects which concept to explore.
pythonconcept_explorer = Agent(
    name="ConceptExplorer",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="""
    Using the knowledge graph: {knowledge_graph}
    And current progress: {learner_progress}
    
    Select the next concept to explore based on:
    1. Mastery level (prioritize low-mastery concepts)
    2. Prerequisites (ensure foundational concepts first)
    3. Logical flow (related concepts together)
    4. Depth level (big picture before details)
    
    Return: concept_id, depth_level, related_concepts
    """,
    output_key="current_concept"
)
4. Quiz Generator Agent
Purpose: Creates adaptive questions based on current learning phase.
pythonquiz_generator = Agent(
    name="QuizGenerator",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="""
    Generate quiz questions for concept: {current_concept}
    At depth level: {depth_level}
    
    QUESTION TYPES BY DEPTH:
    - LEVEL 0 (Big Picture): "What is X?" "Why does X matter?"
    - LEVEL 1 (Understanding): "How does X work?" "Explain the process of X"
    - LEVEL 2 (Details): "What are the components of X?" "Compare X and Y"
    - LEVEL 3 (Connections): "How does X relate to Y?" "What happens if X changes?"
    - LEVEL 4 (Synthesis): "Design a solution using X and Y" "Predict outcomes"
    
    Include:
    - The question
    - Expected key points in answer
    - Follow-up probing questions
    - Hints if learner struggles
    """,
    output_key="current_question"
)
5. Progress Tracker Agent
Purpose: Evaluates answers and tracks mastery levels.
pythonprogress_tracker = Agent(
    name="ProgressTracker",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="""
    Evaluate the learner's response: {learner_response}
    Against expected: {expected_answer}
    
    Score on dimensions:
    1. Accuracy (0-100): Factually correct?
    2. Completeness (0-100): Covered all key points?
    3. Understanding (0-100): Shows deep comprehension?
    4. Connections (0-100): Mentions related concepts?
    
    Update mastery levels and recommend:
    - ADVANCE: Move to deeper level or next concept
    - REINFORCE: Ask different question on same concept
    - REMEDIATE: Go back to foundational concepts
    - CONNECT: Test relationship understanding
    """,
    tools=[FunctionTool(update_progress_state), FunctionTool(calculate_mastery)],
    output_key="progress_update"
)
```

---

## 🔄 User Flows

### Flow 1: Initial Document Ingestion
```
User uploads PDF
      │
      ▼
Document Analyzer extracts text
      │
      ▼
Build knowledge graph (concepts, relationships, hierarchy)
      │
      ▼
Present overview to user: "I found X main concepts..."
      │
      ▼
Ask: "Ready to start learning?"
```

### Flow 2: Big Picture Phase
```
Concept Explorer selects first main concept
      │
      ▼
Quiz Generator creates Level 0 question
"What is [Concept X] and why is it important?"
      │
      ▼
User responds
      │
      ▼
Progress Tracker evaluates response
      │
      ├── Good understanding ──▶ Move to next main concept
      │
      └── Gaps detected ──▶ Provide explanation, retry with different question
```

### Flow 3: Deep Dive Phase
```
After Big Picture mastery achieved
      │
      ▼
Concept Explorer selects first concept for deep dive
      │
      ▼
Quiz Generator creates Level 2 questions
"What are the components of X?"
"Walk me through the process of X step by step"
      │
      ▼
User responds
      │
      ▼
Progress Tracker evaluates
      │
      ├── Mastered ──▶ Go deeper (Level 3) or move to next sub-concept
      │
      └── Struggling ──▶ Break down further, provide hints, retry
```

### Flow 4: Connections Phase
```
After concepts understood individually
      │
      ▼
Concept Explorer identifies concept pairs
      │
      ▼
Quiz Generator creates relationship questions
"How does X influence Y?"
"What would happen to Y if X changes?"
      │
      ▼
User responds
      │
      ▼
Progress Tracker evaluates relationship understanding
      │
      ├── Connections clear ──▶ Move to synthesis
      │
      └── Missing links ──▶ Explain relationship, retry
```

### Flow 5: Synthesis & Mastery Verification
```
All concepts and connections explored
      │
      ▼
Quiz Generator creates synthesis questions
"Design a solution combining X, Y, and Z"
"Explain the overall system from start to finish"
      │
      ▼
User responds
      │
      ▼
Progress Tracker evaluates holistic understanding
      │
      ├── MASTERY ACHIEVED ──▶ Congratulations! Summary provided
      │
      └── Gaps remain ──▶ Identify weak areas, return to relevant phase

🛠️ Custom Tools
Tool 1: PDF Text Extractor
pythondef extract_pdf_text(pdf_path: str) -> dict:
    """
    Extracts text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary with extracted text and metadata
    """
    # Use PyPDF2 or pdfplumber
    return {
        "status": "success",
        "text": extracted_text,
        "page_count": num_pages,
        "word_count": word_count
    }
Tool 2: Knowledge Graph Builder
pythondef build_knowledge_graph(concepts_json: str) -> dict:
    """
    Builds a structured knowledge graph from extracted concepts.
    
    Args:
        concepts_json: JSON string with concepts and relationships
        
    Returns:
        Knowledge graph structure
    """
    return {
        "nodes": [...],  # Concepts
        "edges": [...],  # Relationships
        "hierarchy": {...},  # Parent-child structure
        "levels": {...}  # Depth assignments
    }
Tool 3: Progress State Manager
pythondef update_progress_state(
    tool_context: ToolContext,
    concept_id: str,
    score: float,
    dimension: str
) -> dict:
    """
    Updates learner progress in session state.
    """
    key = f"progress:{concept_id}:{dimension}"
    current = tool_context.state.get(key, 0)
    new_score = (current + score) / 2  # Running average
    tool_context.state[key] = new_score
    
    return {"status": "updated", "new_score": new_score}
Tool 4: Mastery Calculator
pythondef calculate_mastery(tool_context: ToolContext, concept_id: str) -> dict:
    """
    Calculates overall mastery level for a concept.
    """
    dimensions = ["accuracy", "completeness", "understanding", "connections"]
    scores = []
    
    for dim in dimensions:
        key = f"progress:{concept_id}:{dim}"
        scores.append(tool_context.state.get(key, 0))
    
    mastery = sum(scores) / len(scores)
    
    return {
        "concept_id": concept_id,
        "mastery": mastery,
        "status": "mastered" if mastery >= 80 else "learning"
    }

📊 Workflow Pattern Selection
Based on the Day 1 patterns, here's how they apply:
PhasePatternReasonDocument ProcessingSequentialMust complete extraction before analysisConcept SelectionLLM OrchestrationDynamic decision based on progressQuiz GenerationSequentialFollows structured question creationAnswer EvaluationParallel (potential)Could evaluate multiple dimensions simultaneouslyOverall LearningLoopIterate until mastery achieved
Combined Architecture
python# Phase 1: Document Processing (Sequential)
document_pipeline = SequentialAgent(
    name="DocumentPipeline",
    sub_agents=[pdf_extractor_agent, concept_identifier_agent, graph_builder_agent]
)

# Phase 2: Learning Loop
learning_loop = LoopAgent(
    name="LearningLoop",
    sub_agents=[concept_selector, quiz_generator, answer_evaluator],
    max_iterations=50  # Prevent infinite loops
)

# Exit condition tool
def check_mastery_complete(tool_context: ToolContext) -> dict:
    """Exit loop when all concepts mastered."""
    all_concepts = tool_context.state.get("all_concepts", [])
    mastered = tool_context.state.get("mastered_concepts", [])
    
    if set(all_concepts) == set(mastered):
        return {"complete": True, "message": "All concepts mastered!"}
    return {"complete": False, "remaining": len(all_concepts) - len(mastered)}

📋 Capstone Project Points Mapping
Based on the capstone requirements, here's how this project addresses each:
1. Multi-Agent Architecture ✅

5 specialized agents with clear responsibilities
Root coordinator for orchestration
Agent-to-Agent communication via AgentTool

2. Custom Tools ✅

extract_pdf_text: Document processing
build_knowledge_graph: Structure creation
update_progress_state: State management
calculate_mastery: Progress tracking

3. Session/Memory Management ✅

Session state for learner progress
Knowledge graph persistence
Cross-session memory for learning continuity

4. Workflow Patterns ✅

Sequential: Document processing
Loop: Learning iteration
LLM Orchestration: Dynamic decisions

5. Observability ✅

LoggingPlugin for debugging
Custom ProgressPlugin to track learning metrics
Events/Traces for quiz flow analysis

6. Evaluation ✅

Test cases for different PDF types
Quiz quality evaluation
Learning outcome metrics

7. Bonus: Video Demonstration

Walkthrough of the learning flow
Demo with sample PDF


🚀 Implementation Roadmap
Phase 1: Foundation (Days 1-2)

 Set up ADK project structure
 Implement PDF extraction tool
 Create basic Document Analyzer agent
 Test with sample PDF

Phase 2: Core Agents (Days 3-4)

 Build Concept Explorer agent
 Build Quiz Generator agent
 Implement Progress Tracker agent
 Create knowledge graph tool

Phase 3: Integration (Days 5-6)

 Connect agents via Root Coordinator
 Implement session state management
 Add memory for cross-session learning
 Create learning loop

Phase 4: Polish (Days 7-8)

 Add observability (LoggingPlugin)
 Create evaluation test cases
 Handle edge cases (short PDFs, unclear content)
 User experience improvements

Phase 5: Submission (Day 9)

 Write project documentation
 Create demo video (bonus)
 Submit writeup

