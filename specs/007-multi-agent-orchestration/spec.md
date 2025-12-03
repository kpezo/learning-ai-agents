# Feature Specification: Multi-Agent Orchestration Expansion

**Feature Branch**: `007-multi-agent-orchestration`
**Created**: 2025-12-03
**Status**: Draft
**Input**: User description: "Expand multi-agent architecture with 5 specialist agents (Diagnostic, Tutor, Quiz, Feedback, PathPlanner), sequential and loop orchestration patterns, and LLM-driven routing"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Intelligent Task Routing (Priority: P1)

A learner sends a message to the system, and the coordinator agent automatically routes it to the appropriate specialist agent based on content. Questions go to Tutor, quiz requests go to Quiz, progress inquiries go to PathPlanner. The learner experiences a seamless conversation without knowing multiple agents are involved.

**Why this priority**: This is the core value proposition - without intelligent routing, the multi-agent system cannot function. It enables separation of concerns while maintaining a unified user experience.

**Independent Test**: Can be fully tested by sending different types of messages and verifying they are routed to the correct specialist agent.

**Acceptance Scenarios**:

1. **Given** a learner asks "Can you explain how derivatives work?", **When** the coordinator receives this, **Then** it routes to the Tutor agent which provides an explanation.

2. **Given** a learner says "Quiz me on calculus," **When** the coordinator receives this, **Then** it routes to the Quiz agent which starts a quiz session.

3. **Given** a learner asks "What should I learn next?", **When** the coordinator receives this, **Then** it routes to the PathPlanner agent which recommends next topics.

---

### User Story 2 - Diagnostic Assessment for New Topics (Priority: P1)

When a learner starts a new topic, the Diagnostic agent first assesses their existing knowledge by checking prerequisites and identifying gaps. This assessment informs how the subsequent tutoring and quizzing is tailored.

**Why this priority**: Equally critical - without diagnosis, the system cannot personalize the learning experience. This is what makes the system "adaptive."

**Independent Test**: Can be tested by starting a new topic and verifying the system first checks prerequisites before teaching.

**Acceptance Scenarios**:

1. **Given** a learner requests to learn "calculus" for the first time, **When** the session starts, **Then** the Diagnostic agent checks mastery of algebra and trigonometry prerequisites.

2. **Given** the Diagnostic agent identifies a gap in "fractions," **When** diagnosis completes, **Then** it recommends remediation before proceeding to calculus.

3. **Given** all prerequisites are met, **When** diagnosis completes, **Then** the system proceeds directly to tutoring on calculus.

---

### User Story 3 - Constructive Feedback After Quizzes (Priority: P2)

After a learner completes quiz questions, the Feedback agent provides specific, actionable feedback on their performance. It identifies patterns in errors (conceptual vs. procedural), celebrates successes, and updates mastery scores.

**Why this priority**: Feedback transforms assessment from testing into learning. Important but the basic quiz can function without dedicated feedback processing.

**Independent Test**: Can be tested by completing a quiz and verifying detailed feedback is provided that goes beyond simple correct/incorrect.

**Acceptance Scenarios**:

1. **Given** a learner answers a question incorrectly, **When** feedback is generated, **Then** it explains why the answer was wrong and provides a hint for the correct approach.

2. **Given** a learner has 3 incorrect answers with the same mistake pattern, **When** the Feedback agent analyzes this, **Then** it identifies the conceptual gap (e.g., "You seem to be confusing X with Y").

3. **Given** a learner answers correctly after previous struggles, **When** feedback is generated, **Then** it reinforces the improvement with encouraging language.

---

### User Story 4 - Learning Cycle Orchestration (Priority: P2)

The system orchestrates a complete learning cycle: Tutor explains → Quiz assesses → Feedback analyzes. This sequence runs automatically within a topic until mastery is achieved, with the loop repeating as needed.

**Why this priority**: This pattern enables self-paced mastery learning but requires the individual agents to exist first.

**Independent Test**: Can be tested by starting a learning session and verifying the system cycles through teach-quiz-feedback phases automatically.

**Acceptance Scenarios**:

1. **Given** a learner begins a topic session, **When** the learning cycle starts, **Then** Tutor explains first, then Quiz assesses understanding.

2. **Given** a learner scores below mastery threshold, **When** the learning cycle completes, **Then** it loops back for another round of teaching and assessment.

3. **Given** a learner achieves mastery (85%+ score), **When** the learning cycle completes, **Then** the system moves to the next concept or ends the session.

---

### User Story 5 - Adaptive Learning Path Updates (Priority: P3)

The PathPlanner agent monitors overall progress and adjusts the learning path. It considers mastery levels, time spent, learner goals, and prerequisite relationships to recommend optimal next steps.

**Why this priority**: Path planning is a higher-level concern that benefits from having the other agents functioning. Learners can manually choose topics initially.

**Independent Test**: Can be tested by completing several topics and verifying the next recommendation is contextually appropriate.

**Acceptance Scenarios**:

1. **Given** a learner has mastered "algebra basics," **When** they ask for next steps, **Then** the PathPlanner recommends topics that have algebra as a prerequisite.

2. **Given** a learner expresses a goal of "learning machine learning," **When** path planning runs, **Then** recommendations prioritize concepts on the path to that goal.

3. **Given** a learner has been struggling with a topic for extended time, **When** path planning runs, **Then** it suggests an alternative approach or simpler prerequisite.

---

### Edge Cases

- What happens when the coordinator cannot determine which agent to route to? Falls back to Tutor agent and asks clarifying questions.
- How does the system handle mid-conversation agent switches (e.g., user asks a question during a quiz)? Pauses quiz state, routes to appropriate agent, then offers to resume quiz.
- What happens if an agent fails to respond? Coordinator handles timeout gracefully and routes to fallback behavior.
- How does state transfer between agents work? Session state is shared via ADK session service; agents read and write to common state keys.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST include a Coordinator agent that routes messages to appropriate specialist agents.

- **FR-002**: System MUST include a Diagnostic agent that assesses learner's current knowledge and identifies gaps.

- **FR-003**: System MUST include a Tutor agent that delivers personalized instruction and explanations.

- **FR-004**: System MUST include a Quiz agent that generates assessments and evaluates answers.

- **FR-005**: System MUST include a Feedback agent that provides constructive analysis of quiz performance.

- **FR-006**: System MUST include a PathPlanner agent that recommends learning paths based on progress.

- **FR-007**: System MUST support sequential agent orchestration (run agents in defined order).

- **FR-008**: System MUST support loop-based orchestration (repeat agent sequence until condition met).

- **FR-009**: System MUST route messages using LLM-driven intent classification.

- **FR-010**: System MUST share session state across all agents using a common state service.

- **FR-011**: System MUST allow mid-conversation agent switching without losing context.

- **FR-012**: System MUST pass diagnostic results to subsequent agents for personalization.

- **FR-013**: System MUST track which agent handled each message for debugging and analytics.

- **FR-014**: System MUST define configurable mastery thresholds for learning cycle completion.

- **FR-015**: System MUST provide fallback routing when intent is unclear.

- **FR-016**: System MUST maintain conversation continuity across agent switches (learner sees one coherent conversation).

### Key Entities

- **CoordinatorAgent**: The root agent that receives all user messages, classifies intent, and routes to specialist agents.

- **DiagnosticAgent**: Specialist that assesses prerequisites, identifies knowledge gaps, and outputs diagnostic results to session state.

- **TutorAgent**: Specialist that explains concepts, answers questions, and adapts explanations based on diagnostic results.

- **QuizAgent**: Specialist that generates questions, evaluates answers, and manages quiz sessions.

- **FeedbackAgent**: Specialist that analyzes quiz performance, identifies error patterns, and provides constructive feedback.

- **PathPlannerAgent**: Specialist that generates and adjusts learning paths based on goals, progress, and prerequisites.

- **LearningCycle**: An orchestration pattern that sequences Tutor → Quiz → Feedback in a loop until mastery.

- **AgentTransition**: A record of routing from one agent to another, including reason and timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Coordinator routes messages to the correct specialist agent 90% of the time (validated by human review of sample conversations).

- **SC-002**: Learning cycles complete with learner achieving mastery in 80% of sessions.

- **SC-003**: Diagnostic assessments correctly identify prerequisite gaps in 85% of cases (validated against learner's actual quiz performance).

- **SC-004**: Feedback agent identifies correct error patterns in 75% of multi-error sequences.

- **SC-005**: Learners rate the conversation as coherent (not disjointed) in 90% of sessions spanning multiple agents.

- **SC-006**: Agent transitions occur within 2 seconds (no perceptible delay to learner).

- **SC-007**: PathPlanner recommendations lead to successful learning (mastery achieved) in 70% of followed recommendations.

## Assumptions

- All agents use the same Gemini model configured in the system.
- ADK's sub_agents parameter handles agent delegation at the framework level.
- Session state is managed via ADK's InMemorySessionService (or persistent service if storage enhancements are implemented).
- Agents can read state written by other agents using shared state key conventions.
- The current 3-agent system (Tutor, Curriculum Planner, Assessor) will be refactored into the new 5-agent architecture.
- Learning cycle and mastery loop patterns use ADK's SequentialAgent and LoopAgent constructs.
