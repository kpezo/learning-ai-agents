# Building an Adaptive Quiz Agent with Google ADK: Complete Implementation Guide

An adaptive quiz agent requires four integrated systems: a knowledge graph for content modeling, ADK-native evaluation infrastructure, pedagogical measurement frameworks, and multi-agent orchestration. This guide provides concrete schemas, code patterns, and benchmarks to implement each component using Google's Agent Development Kit.

## Knowledge graph architecture forms the foundation

Educational knowledge graphs require **three hierarchical levels** for optimal concept representation: domains/chapters at level 1, topics/sections at level 2, and concepts/keywords at level 3. Research on intelligent tutoring systems shows this granularity balances navigability with semantic precision.

The following JSON schema captures both hierarchical structure and the rich semantic relationships essential for adaptive learning:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "definitions": {
    "ConceptNode": {
      "type": "object",
      "required": ["id", "name", "node_type"],
      "properties": {
        "id": {"type": "string", "format": "uuid"},
        "name": {"type": "string"},
        "node_type": {
          "type": "string",
          "enum": ["domain", "course", "module", "topic", "concept", "skill", "resource", "assessment"]
        },
        "hierarchy_level": {"type": "integer", "minimum": 1, "maximum": 5},
        "description": {"type": "string"},
        "aliases": {"type": "array", "items": {"type": "string"}},
        "properties": {
          "type": "object",
          "properties": {
            "difficulty": {"type": "string", "enum": ["novice", "beginner", "intermediate", "advanced", "expert"]},
            "bloom_taxonomy_level": {"type": "string", "enum": ["remember", "understand", "apply", "analyze", "evaluate", "create"]},
            "estimated_learning_time_minutes": {"type": "integer"},
            "importance_weight": {"type": "number", "minimum": 0, "maximum": 1},
            "keywords": {"type": "array", "items": {"type": "string"}}
          }
        },
        "provenance": {
          "type": "object",
          "properties": {
            "source_document": {"type": "string"},
            "page_numbers": {"type": "array", "items": {"type": "integer"}},
            "extraction_method": {"type": "string", "enum": ["manual", "llm_extracted", "rule_based"]},
            "confidence_score": {"type": "number", "minimum": 0, "maximum": 1}
          }
        }
      }
    },
    "RelationshipEdge": {
      "type": "object",
      "required": ["id", "source_id", "target_id", "relationship_type"],
      "properties": {
        "id": {"type": "string"},
        "source_id": {"type": "string"},
        "target_id": {"type": "string"},
        "relationship_type": {
          "type": "string",
          "enum": ["prerequisite", "enables", "part_of", "contains", "similar_to", "related_to", "contradicts", "exemplifies", "applies_to", "extends", "teaches", "assesses"]
        },
        "is_directed": {"type": "boolean", "default": true},
        "properties": {
          "type": "object",
          "properties": {
            "strength": {"type": "number", "minimum": 0, "maximum": 1},
            "prerequisite_type": {"type": "string", "enum": ["hard", "soft", "recommended"]},
            "evidence_text": {"type": "string"},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1}
          }
        }
      }
    }
  }
}
```

**Relationship types serve distinct pedagogical functions**: Prerequisites (hard vs. soft) define learning dependencies, `enables` captures conceptual unlocking, `similar_to` identifies confusable concepts requiring differentiation instruction, and `exemplifies` connects abstract concepts to concrete instances.

### LLM-based knowledge graph construction

LlamaIndex provides the most direct path for automated construction from academic PDFs:

```python
from llama_index.core import SimpleDirectoryReader, KnowledgeGraphIndex
from llama_index.core.graph_stores import SimpleGraphStore
from llama_index.llms.openai import OpenAI
from llama_index.core import StorageContext, Settings

# Load course materials
documents = SimpleDirectoryReader("./course_materials/").load_data()

Settings.llm = OpenAI(temperature=0, model="gpt-4")
Settings.chunk_size = 512

graph_store = SimpleGraphStore()
storage_context = StorageContext.from_defaults(graph_store=graph_store)

# Extract knowledge graph with triplets per chunk
index = KnowledgeGraphIndex.from_documents(
    documents,
    max_triplets_per_chunk=5,
    storage_context=storage_context,
    include_embeddings=True
)

# Add educational relationships manually
index.upsert_triplet(("Calculus", "prerequisite_for", "Differential Equations"))
index.upsert_triplet(("Algebra", "enables", "Calculus"))
```

For more controlled extraction, use this structured prompt:

```python
EDUCATIONAL_EXTRACTION_PROMPT = """
Extract educational concepts and relationships from the following text.

For each concept identify:
1. Concept name and type (domain/topic/subtopic/concept/skill)
2. Difficulty level (beginner/intermediate/advanced)
3. Bloom's taxonomy level (remember/understand/apply/analyze/evaluate/create)

For relationships identify:
- prerequisite: A must be learned before B
- part_of: A is component of B  
- similar_to: Concepts are related but distinct
- exemplifies: A is an example of B

Output as JSON with "concepts" and "relationships" arrays.
TEXT: {text_chunk}
"""
```

---

## ADK evaluation requires structured evalset.json files

Google ADK's evaluation system uses two core files: `.evalset.json` for test cases and `test_config.json` for evaluation criteria. The evalset schema captures multi-turn conversations with expected tool trajectories:

```json
{
  "eval_set_id": "quiz_agent_comprehensive_eval",
  "name": "Adaptive Quiz Agent Evaluation Suite",
  "description": "Tests quiz generation, answer evaluation, and adaptive difficulty",
  "eval_cases": [
    {
      "eval_id": "basic_quiz_flow",
      "session_input": {
        "app_name": "quiz_agent",
        "user_id": "test_student",
        "state": {
          "difficulty": "medium",
          "topic": "algebra",
          "mastery_threshold": 0.8
        }
      },
      "conversation": [
        {
          "invocation_id": "turn_1_start_quiz",
          "user_content": {
            "role": "user",
            "parts": [{"text": "Start a quiz on linear equations"}]
          },
          "final_response": {
            "role": "model",
            "parts": [{"text": "Let's begin your linear equations quiz. Question 1: Solve for x: 2x + 5 = 13"}]
          },
          "intermediate_data": {
            "tool_uses": [
              {
                "name": "query_knowledge_graph",
                "args": {"concept": "linear_equations", "query_type": "prerequisites"}
              },
              {
                "name": "generate_adaptive_quiz",
                "args": {"concept": "linear_equations", "difficulty": "medium", "num_questions": 5}
              }
            ],
            "intermediate_responses": []
          }
        },
        {
          "invocation_id": "turn_2_correct_answer",
          "user_content": {
            "role": "user",
            "parts": [{"text": "x = 4"}]
          },
          "final_response": {
            "role": "model",
            "parts": [{"text": "Correct! You solved 2x + 5 = 13 by subtracting 5 from both sides to get 2x = 8, then dividing by 2. Score: 1/1. Ready for question 2?"}]
          },
          "intermediate_data": {
            "tool_uses": [
              {"name": "evaluate_answer", "args": {"question_id": "q1", "student_answer": "x = 4"}},
              {"name": "update_mastery_score", "args": {"concept": "linear_equations", "correct": true}}
            ],
            "intermediate_responses": []
          }
        },
        {
          "invocation_id": "turn_3_incorrect_answer",
          "user_content": {
            "role": "user",
            "parts": [{"text": "Yes, next question"}]
          },
          "final_response": {
            "role": "model",
            "parts": [{"text": "Question 2: If 3(x - 2) = 15, what is x?"}]
          },
          "intermediate_data": {
            "tool_uses": [
              {"name": "get_next_question", "args": {"quiz_id": "quiz_123", "adjust_difficulty": false}}
            ],
            "intermediate_responses": []
          }
        }
      ]
    },
    {
      "eval_id": "adaptive_difficulty_adjustment",
      "session_input": {
        "app_name": "quiz_agent",
        "user_id": "struggling_student",
        "state": {"consecutive_incorrect": 2}
      },
      "conversation": [
        {
          "invocation_id": "difficulty_decrease",
          "user_content": {
            "role": "user",
            "parts": [{"text": "I don't know, maybe 10?"}]
          },
          "final_response": {
            "role": "model",
            "parts": [{"text": "Not quite. Let me break this down with an easier example first. If x + 3 = 7, what is x?"}]
          },
          "intermediate_data": {
            "tool_uses": [
              {"name": "evaluate_answer", "args": {"question_id": "q5", "student_answer": "10"}},
              {"name": "adjust_difficulty", "args": {"direction": "decrease", "reason": "consecutive_failures"}},
              {"name": "generate_scaffolded_question", "args": {"concept": "linear_equations", "difficulty": "beginner"}}
            ],
            "intermediate_responses": []
          }
        }
      ]
    }
  ]
}
```

### Test configuration with thresholds

The `test_config.json` defines evaluation criteria and acceptable thresholds:

```json
{
  "criteria": {
    "tool_trajectory_avg_score": {
      "threshold": 0.8
    },
    "final_response_match_v2": {
      "threshold": 0.7,
      "judge_model_options": {
        "judge_model": "gemini-2.5-flash",
        "num_samples": 3
      }
    },
    "rubric_based_final_response_quality_v1": {
      "threshold": 0.8,
      "judge_model_options": {
        "judge_model": "gemini-2.5-flash",
        "num_samples": 5
      },
      "rubrics": [
        {
          "rubric_id": "pedagogical_accuracy",
          "rubric_content": {
            "text_property": "The agent provides educationally accurate explanations and correctly evaluates student answers."
          }
        },
        {
          "rubric_id": "adaptive_behavior",
          "rubric_content": {
            "text_property": "The agent appropriately adjusts difficulty based on student performance patterns."
          }
        },
        {
          "rubric_id": "constructive_feedback",
          "rubric_content": {
            "text_property": "The agent provides specific, actionable feedback that helps the student understand mistakes."
          }
        },
        {
          "rubric_id": "bloom_alignment",
          "rubric_content": {
            "text_property": "Questions progress appropriately through cognitive levels from recall to application."
          }
        }
      ]
    },
    "hallucinations_v1": {
      "threshold": 0.9,
      "judge_model_options": {
        "judge_model": "gemini-2.5-flash"
      },
      "evaluate_intermediate_nl_responses": true
    }
  }
}
```

**Recommended thresholds by use case**:

| Metric | Strict Validation | Standard Testing | Flexible Paths |
|--------|-------------------|------------------|----------------|
| `tool_trajectory_avg_score` | 1.0 | 0.8 | 0.6 |
| `response_match_score` | 0.8 | 0.6 | 0.5 |
| `hallucinations_v1` | 0.95 | 0.85 | 0.8 |

---

## Pedagogical evaluation requires measurable learning metrics

### Mastery thresholds validated by research

Meta-analyses of mastery learning show optimal thresholds vary by domain:

| Context | Accuracy Threshold | Consistency Requirement | Evidence |
|---------|-------------------|------------------------|----------|
| General K-12 | 80% | 2-3 consecutive correct | Bloom's mastery learning |
| STEM skills | 85% | 3 consecutive correct | Carnegie Learning research |
| Medical training | 90-95% | Across multiple sessions | Ebel standard-setting |
| Elementary math | 90% (9/10) | Within time limit | MasteryTrack validation |

For Bayesian Knowledge Tracing (BKT), the standard mastery threshold is **P(mastery) ≥ 0.95**:

```python
# BKT Parameters for educational domains
BKT_PARAMS = {
    "P_L0": 0.1,    # Initial probability of knowing skill
    "P_T": 0.3,     # Probability of learning per opportunity  
    "P_G": 0.2,     # Probability of guessing correctly
    "P_S": 0.1,     # Probability of slipping (error despite knowing)
    "mastery_threshold": 0.95
}

def update_mastery_probability(p_known: float, is_correct: bool, params: dict) -> float:
    """Update mastery probability using Bayesian Knowledge Tracing."""
    if is_correct:
        # P(known | correct) using Bayes' rule
        p_correct_given_known = 1 - params["P_S"]
        p_correct_given_unknown = params["P_G"]
        p_correct = p_known * p_correct_given_known + (1 - p_known) * p_correct_given_unknown
        p_known_given_correct = (p_known * p_correct_given_known) / p_correct
    else:
        # P(known | incorrect)
        p_incorrect_given_known = params["P_S"]
        p_incorrect_given_unknown = 1 - params["P_G"]
        p_incorrect = p_known * p_incorrect_given_known + (1 - p_known) * p_incorrect_given_unknown
        p_known_given_correct = (p_known * p_incorrect_given_known) / p_incorrect
    
    # Apply learning transition
    return p_known_given_correct + (1 - p_known_given_correct) * params["P_T"]
```

### Item Response Theory for question calibration

The **3-Parameter Logistic Model** provides rigorous item difficulty measurement:

```
P(correct|θ) = c + (1-c) × [1 / (1 + e^(-a(θ-b)))]

Where:
θ = student ability (scaled -3 to +3, mean=0, SD=1)
a = discrimination (0.5-2.5, higher = better)
b = difficulty (-3 to +3, higher = harder)
c = guessing parameter (0.25 for 4-option MCQ)
```

**IRT parameter quality benchmarks**:

| Parameter | Poor | Acceptable | Good | Excellent |
|-----------|------|------------|------|-----------|
| Discrimination (a) | < 0.5 | 0.5-1.0 | 1.0-1.5 | > 1.5 |
| Difficulty (b) | < -2.5 or > 2.5 | ±1.5-2.5 | ±0.5-1.5 | Near 0 |

### Zone of Proximal Development metrics

Optimal challenge occurs when students achieve **60-85% initial success** with scaffolding available. Track these indicators:

```python
ZPD_METRICS = {
    "optimal_success_range": (0.60, 0.85),
    "frustration_indicators": {
        "rapid_incorrect_attempts": 3,  # Within 10 seconds
        "help_requests_per_problem": 4,
        "abandonment_threshold": 0.3    # 30% of problems abandoned
    },
    "boredom_indicators": {
        "completion_time_ratio": 0.5,   # < 50% of expected time
        "consecutive_correct_easy": 5,
        "engagement_drop": 0.4          # 40% decrease in time-on-task
    }
}
```

### Bloom's Taxonomy question classification

Automated classification achieves **91% accuracy** using fine-tuned models. Map questions to cognitive levels:

| Level | Action Verbs | Question Patterns | Target Distribution |
|-------|--------------|-------------------|---------------------|
| Remember | define, list, identify | "What is..." "Name the..." | 15% |
| Understand | explain, describe, summarize | "Explain why..." "Describe..." | 25% |
| Apply | calculate, solve, demonstrate | "Calculate..." "Solve for..." | 30% |
| Analyze | compare, contrast, categorize | "Compare X and Y..." | 15% |
| Evaluate | critique, assess, justify | "Evaluate the..." | 10% |
| Create | design, construct, develop | "Design a solution..." | 5% |

---

## Multi-agent ADK architecture for educational systems

The complete educational system uses five specialist agents orchestrated by a coordinator:

```python
from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.tools.agent_tool import AgentTool

# === Tool Definitions ===

def query_knowledge_graph(concept: str, query_type: str = "prerequisites") -> dict:
    """Queries the educational knowledge graph for concept relationships.
    
    Args:
        concept: The concept to query
        query_type: One of 'prerequisites', 'related', 'successors', 'part_of'
    Returns:
        dict with status and related concepts
    """
    return {
        "status": "success",
        "concept": concept,
        "prerequisites": ["algebra", "arithmetic"],
        "difficulty_level": 3,
        "bloom_level": "apply"
    }

def generate_adaptive_quiz(
    concept: str,
    difficulty: str,
    student_mastery: float,
    num_questions: int = 5
) -> dict:
    """Generates quiz questions adapted to student's current mastery level.
    
    Args:
        concept: Topic to assess
        difficulty: 'beginner', 'intermediate', 'advanced'
        student_mastery: Current mastery score 0.0-1.0
        num_questions: Number of questions to generate
    """
    return {
        "status": "success",
        "quiz_id": "quiz_" + concept,
        "questions": [...],
        "target_mastery": max(0.8, student_mastery + 0.1)
    }

def evaluate_answer(question_id: str, student_answer: str, expected: str) -> dict:
    """Evaluates student answer and provides detailed feedback."""
    return {
        "status": "success",
        "correct": student_answer.lower() == expected.lower(),
        "feedback": "Correct approach..." if correct else "Consider...",
        "partial_credit": 0.8 if partially_correct else 0.0
    }

def update_mastery_score(student_id: str, concept: str, score_delta: float) -> dict:
    """Updates student's mastery score for a concept in the knowledge state."""
    return {"status": "success", "new_mastery": 0.75, "concept": concept}


# === Specialist Agents ===

diagnostic_agent = LlmAgent(
    name="DiagnosticAgent",
    model="gemini-2.0-flash",
    description="Assesses student's current knowledge state and identifies gaps",
    instruction="""Analyze the student's knowledge state from session.
    1. Query knowledge graph for topic prerequisites
    2. Check student's mastery of each prerequisite
    3. Identify gaps that need remediation
    4. Output diagnostic assessment to state.""",
    tools=[query_knowledge_graph, get_student_progress],
    output_key="diagnostic_result"
)

tutor_agent = LlmAgent(
    name="TutorAgent", 
    model="gemini-2.0-flash",
    description="Delivers personalized instruction matching student's level",
    instruction="""Based on {diagnostic_result}:
    - Explain concepts at the appropriate Bloom's level
    - Use scaffolding for concepts in the student's ZPD
    - Check understanding with concept-check questions
    - Adapt explanations based on student responses""",
    tools=[query_knowledge_graph],
    output_key="lesson_delivered"
)

quiz_agent = LlmAgent(
    name="QuizAgent",
    model="gemini-2.0-flash", 
    description="Generates adaptive assessments and evaluates responses",
    instruction="""Generate and evaluate quiz questions:
    1. Create questions matching student's current mastery level
    2. Include variety of question types (MCQ, short answer, problem-solving)
    3. Evaluate answers with partial credit where appropriate
    4. Adjust difficulty based on consecutive success/failure patterns""",
    tools=[generate_adaptive_quiz, evaluate_answer],
    output_key="quiz_result"
)

feedback_agent = LlmAgent(
    name="FeedbackAgent",
    model="gemini-2.0-flash",
    description="Provides constructive feedback and updates learning progress",
    instruction="""Analyze quiz performance from {quiz_result}:
    - Provide specific, actionable feedback for incorrect answers
    - Celebrate successes with reinforcement
    - Identify patterns in errors (conceptual vs. procedural)
    - Update mastery scores based on performance""",
    tools=[update_mastery_score, query_knowledge_graph],
    output_key="feedback_provided"
)

path_planner_agent = LlmAgent(
    name="PathPlannerAgent",
    model="gemini-2.0-flash",
    description="Plans and adjusts the learning path based on progress",
    instruction="""Based on {feedback_provided} and learning goals:
    - Determine if concept is mastered (threshold: 0.8)
    - Plan next concepts using prerequisite graph
    - Adjust pacing based on learning rate
    - Schedule review for spaced repetition""",
    tools=[query_knowledge_graph, generate_learning_path],
    output_key="updated_path"
)

# === Orchestration ===

learning_cycle = SequentialAgent(
    name="LearningCycle",
    sub_agents=[tutor_agent, quiz_agent, feedback_agent]
)

mastery_loop = LoopAgent(
    name="MasteryLoop",
    max_iterations=5,
    sub_agents=[learning_cycle]
)

# Root coordinator with LLM-driven routing
root_agent = LlmAgent(
    name="AdaptiveQuizCoordinator",
    model="gemini-2.0-flash",
    instruction="""You coordinate the adaptive learning experience.
    
    For new topics: Start with DiagnosticAgent, then learning cycle
    For practice requests: Route directly to QuizAgent
    For concept questions: Route to TutorAgent
    For progress checks: Route to PathPlannerAgent
    
    Always maintain an encouraging, growth-mindset tone.
    Track session state for continuity across interactions.""",
    sub_agents=[diagnostic_agent, tutor_agent, quiz_agent, feedback_agent, path_planner_agent]
)
```

### State management for learning progress

ADK provides three state scopes critical for educational tracking:

```python
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()

# Initialize session with learning state
session = await session_service.create_session(
    app_name="adaptive_quiz",
    user_id="student_123",
    state={
        # Session-scoped: current learning session
        "current_concept": "linear_equations",
        "session_score": 0,
        "questions_attempted": 0,
        
        # User-scoped (prefix "user:"): persistent across sessions
        "user:mastery_scores": {
            "algebra_basics": 0.9,
            "linear_equations": 0.6,
            "quadratic_equations": 0.2
        },
        "user:total_study_hours": 15.5,
        "user:learning_style": "visual",
        "user:completed_modules": ["intro_algebra", "basic_operations"],
        
        # App-scoped (prefix "app:"): shared across all users
        "app:available_courses": ["algebra", "geometry", "calculus"]
    }
)
```

---

## Phase-based implementation roadmap

### Phase 1: MVP Foundation (Weeks 1-2)
**Goal**: Basic tutoring agent with simple Q&A

```python
# Minimal viable agent
from google.adk.agents import Agent

mvp_tutor = Agent(
    model="gemini-2.0-flash",
    name="simple_tutor",
    instruction="You are a helpful tutor. Answer questions clearly.",
    tools=[get_topic_content]
)
```

**Test coverage**: Basic response quality, single-turn conversations

### Phase 2: Knowledge Graph Integration (Weeks 3-4)  
**Goal**: Add prerequisite checking and concept relationships

**New components**: Knowledge graph tools, prerequisite validation, concept navigation

**Test coverage**: Knowledge graph queries, prerequisite detection accuracy

### Phase 3: Assessment System (Weeks 5-6)
**Goal**: Quiz generation with answer evaluation

**New components**: Quiz generation, answer evaluation, difficulty levels, partial credit

**Test coverage**: Question quality metrics, answer evaluation accuracy, IRT calibration

### Phase 4: Adaptive Logic (Weeks 7-8)
**Goal**: Dynamic difficulty adjustment and ZPD maintenance

**New components**: BKT mastery tracking, difficulty adjustment, scaffolding system

**Test coverage**: Adaptation accuracy (>80% correct difficulty targeting)

### Phase 5: Multi-Agent Orchestration (Weeks 9-10)
**Goal**: Full specialist agent system with coordinator

**New components**: All five specialist agents, SequentialAgent workflows, LoopAgent for mastery

**Test coverage**: Agent routing accuracy, multi-turn conversation flows

### Phase 6: Production Deployment (Weeks 11-12)
**Goal**: Deploy to Vertex AI Agent Engine

```bash
# Deploy to Vertex AI
adk deploy --project=your-project --region=us-central1
```

---

## Evaluation test suite structure

Organize evaluation files by agent and scenario type:

```
educational_ai_system/
├── agent.py                    # Root agent
├── agents/
│   ├── diagnostic_agent.py
│   ├── tutor_agent.py
│   ├── quiz_agent.py
│   ├── feedback_agent.py
│   └── path_planner_agent.py
├── tools/
│   ├── knowledge_graph_tools.py
│   ├── assessment_tools.py
│   └── progress_tools.py
├── eval/
│   ├── test_eval.py
│   └── data/
│       ├── basic_tutoring.evalset.json
│       ├── quiz_flows.evalset.json
│       ├── adaptive_difficulty.evalset.json
│       ├── edge_cases.evalset.json
│       └── test_config.json
└── tests/
    ├── test_tools.py
    └── test_agents.py
```

Run evaluations with:

```bash
# Full evaluation suite
adk eval educational_ai_system eval/data/ --config_file_path eval/data/test_config.json

# Specific scenario testing  
adk eval educational_ai_system eval/data/adaptive_difficulty.evalset.json --print_detailed_results

# Pytest integration
pytest eval/test_eval.py -v
```

## Conclusion

Building an effective adaptive quiz agent requires tight integration between four systems. The knowledge graph provides the semantic backbone for prerequisite relationships and learning paths, using a hierarchical node structure with **12 distinct relationship types** covering dependencies, similarities, and pedagogical connections. ADK's evaluation framework enables rigorous testing through `.evalset.json` files with multi-turn conversations and tool trajectory validation—aim for **0.8 tool trajectory scores** and **0.7+ semantic response match** thresholds.

Pedagogical effectiveness depends on calibrated metrics: **80-95% mastery thresholds** depending on domain, **60-85% success rates** for optimal challenge, and BKT with **0.95 probability thresholds** for progression decisions. The multi-agent architecture separates concerns across diagnostic, tutoring, assessment, feedback, and planning agents, orchestrated through ADK's SequentialAgent and LoopAgent patterns with shared state for learning progress.

The phased implementation approach builds complexity incrementally—from a basic tutoring MVP through knowledge graph integration, assessment systems, adaptive logic, and finally multi-agent orchestration—with specific test coverage requirements at each phase ensuring production readiness.