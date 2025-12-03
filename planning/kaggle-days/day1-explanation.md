# Day 1: AI Agents - From Prompt to Action & Multi-Agent Architectures

## Core Concepts Overview

This document summarizes the key concepts from Day 1 of the AI Agents course, covering basic agent development and multi-agent system architectures.

---

## Part 1: From Prompt to Action

### 1. Understanding AI Agents

**Traditional LLM Interaction:**
```
Prompt → LLM → Text Response
```

**AI Agent Interaction:**
```
Prompt → Agent → Thought → Action → Observation → Final Answer
```

**Key Difference:** Agents don't just respond - they can **reason**, **take actions**, and **observe results** to provide better answers.

### 2. Agent Development Kit (ADK)

ADK is Google's open-source framework for building, deploying, and orchestrating AI agents. It brings software development best practices to AI agent creation.

**Key Features:**
- Model-agnostic design (works with various AI models)
- Optimized for Google's Gemini models
- Multi-agent architecture support
- Extensive tooling ecosystem
- Code-first approach
- Available in Python, Go, and Java

**Installation & Setup:**

```bash
# Install ADK
pip install google-adk

# Create a new agent project
adk create my-agent --model gemini-2.5-flash-lite
```

**Basic Setup Code:**

```python
import os
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

# Set API key
os.environ["GOOGLE_API_KEY"] = "your-api-key-here"

# Configure retry options
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)
```

### 3. Core Agent Components

An agent in ADK consists of five main properties:

```python
agent = Agent(
    name="helpful_assistant",           # Identifier for the agent
    description="...",                   # What the agent does
    model=Gemini(model="..."),          # The LLM powering the agent
    instruction="...",                   # The agent's behavior guide
    tools=[google_search]                # Capabilities the agent can use
)
```

**Components Explained:**
- **name**: A unique identifier for the agent
- **description**: Brief explanation of the agent's purpose
- **model**: The specific LLM (e.g., "gemini-2.5-flash-lite")
- **instruction**: The guiding prompt that defines the agent's goal and behavior
- **tools**: List of tools the agent can use (search, code execution, custom functions, etc.)

**Complete Example:**

```python
# Create a simple agent with search capability
simple_agent = Agent(
    name="research_assistant",
    description="A helpful agent that answers questions using web search",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""You are a helpful research assistant.
    Use Google Search for current information or when you're unsure.
    Provide concise, accurate answers with citations.""",
    tools=[google_search]
)

# Run the agent
runner = InMemoryRunner(agent=simple_agent)
response = await runner.run_debug("What are the latest AI developments in 2025?")
print(response)
```

### 4. The Runner - Orchestrating Agents

The `Runner` is the central component that manages conversations and handles agent responses.

```python
runner = InMemoryRunner(agent=root_agent)
response = await runner.run_debug("Your question here")
```

**InMemoryRunner** handles:
- Session creation and maintenance
- Message routing to agents
- Response handling
- State management

### 5. Tools - Extending Agent Capabilities

Tools augment agents with specific functionalities:

**Pre-built Tools:**
- `google_search` - Search for current information
- Code execution tools
- Database connectors

**Custom Tools:**
- Integration with LangChain libraries
- Integration with LlamaIndex
- Custom Python functions (covered in Part 2)

### 6. Retry Configuration

Handle transient errors (rate limits, temporary unavailability) with automatic retry logic:

```python
retry_config = types.HttpRetryOptions(
    attempts=5,                              # Maximum retry attempts
    exp_base=7,                              # Delay multiplier
    initial_delay=1,                         # Initial delay (seconds)
    http_status_codes=[429, 500, 503, 504]  # HTTP errors to retry
)
```

---

## Part 2: Multi-Agent Systems & Workflow Patterns

### 7. Why Multi-Agent Systems?

**The Problem with Monolithic Agents:**
- Long, confusing instruction prompts
- Difficult to debug (which part failed?)
- Hard to maintain
- Unreliable results for complex tasks

**The Multi-Agent Solution:**
- Team of specialized agents
- Each agent has one clear job
- Easier to build, test, and maintain
- More powerful and reliable when collaborating

**Architecture Comparison:**
```
❌ Monolithic: One Agent Does Everything

✅ Multi-Agent: Root Coordinator → Specialist A
                                 → Specialist B
                                 → Specialist C
```

### 8. State Management with output_key

Agents share data through a session state using `output_key`:

```python
research_agent = Agent(
    name="ResearchAgent",
    instruction="Find information...",
    output_key="research_findings"  # Stores result in session state
)

summarizer_agent = Agent(
    name="SummarizerAgent",
    # Access previous agent's output using {research_findings}
    instruction="Summarize this: {research_findings}",
    output_key="final_summary"
)
```

**Complete Working Example:**

```python
# Agent 1: Research
research_agent = Agent(
    name="ResearchAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="Use google_search to find 2-3 key facts about the topic.",
    tools=[google_search],
    output_key="research_findings"  # Output stored here
)

# Agent 2: Summarize (uses Agent 1's output)
summarizer_agent = Agent(
    name="SummarizerAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""Read the research findings: {research_findings}
    Create a 3-bullet summary of the key points.""",
    output_key="final_summary"  # Final output stored here
)

# Coordinator that orchestrates both agents
coordinator = Agent(
    name="ResearchCoordinator",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""1. Call ResearchAgent to gather information
    2. Call SummarizerAgent to create summary
    3. Present the final summary to the user""",
    tools=[AgentTool(research_agent), AgentTool(summarizer_agent)]
)

# Run the system
runner = InMemoryRunner(agent=coordinator)
result = await runner.run_debug("What is quantum computing?")
```

### 9. AgentTool - Wrapping Agents as Tools

Make sub-agents callable by a root coordinator:

```python
root_agent = Agent(
    name="Coordinator",
    instruction="Call ResearchAgent first, then SummarizerAgent",
    tools=[
        AgentTool(research_agent),      # Wrap agents as tools
        AgentTool(summarizer_agent)
    ]
)
```

### 10. The Four Workflow Patterns

#### Pattern 1: LLM-Based Orchestration

**When to Use:** Need dynamic, intelligent routing between agents

**How it Works:** The root agent (an LLM) decides which tools/agents to call and in what order

```python
root_agent = Agent(
    name="Coordinator",
    instruction="Intelligently orchestrate the sub-agents",
    tools=[AgentTool(agent1), AgentTool(agent2)]
)
```

**Pros:** Flexible, adaptive
**Cons:** Unpredictable, may skip steps or change order

---

#### Pattern 2: Sequential Workflow

**When to Use:** Tasks must happen in a specific, guaranteed order

**How it Works:** Runs agents like an assembly line - one after another

```python
root_agent = SequentialAgent(
    name="Pipeline",
    sub_agents=[outline_agent, writer_agent, editor_agent]
)
```

**Example Use Case:** Blog post creation
1. Outline Agent creates structure
2. Writer Agent writes content
3. Editor Agent polishes the draft

**Pros:** Deterministic, predictable
**Cons:** Slower (sequential execution)

**Complete Code Example:**

```python
from google.adk.agents import Agent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner

# Step 1: Create outline
outline_agent = Agent(
    name="OutlineAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""Create a blog outline with:
    1. Catchy headline
    2. Introduction hook
    3. 3-5 main sections
    4. Conclusion""",
    output_key="blog_outline"
)

# Step 2: Write the blog
writer_agent = Agent(
    name="WriterAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""Following this outline: {blog_outline}
    Write a 200-300 word blog post with engaging tone.""",
    output_key="blog_draft"
)

# Step 3: Edit and polish
editor_agent = Agent(
    name="EditorAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""Edit this draft: {blog_draft}
    Fix grammar, improve flow, enhance clarity.""",
    output_key="final_blog"
)

# Create sequential pipeline
blog_pipeline = SequentialAgent(
    name="BlogPipeline",
    sub_agents=[outline_agent, writer_agent, editor_agent]
)

# Run the pipeline
runner = InMemoryRunner(agent=blog_pipeline)
result = await runner.run_debug("Write a blog about AI agents")

# Access the final output
print(result)  # The polished blog post
```

---

#### Pattern 3: Parallel Workflow

**When to Use:** Tasks are independent and can run simultaneously

**How it Works:** Executes all sub-agents concurrently, then aggregates results

```python
parallel_team = ParallelAgent(
    name="ResearchTeam",
    sub_agents=[tech_researcher, health_researcher, finance_researcher]
)

# Often combined with Sequential for aggregation
root_agent = SequentialAgent(
    name="System",
    sub_agents=[parallel_team, aggregator_agent]
)
```

**Example Use Case:** Multi-topic research
- Run 3 researchers simultaneously
- Aggregate findings into single report

**Pros:** Fast, efficient
**Cons:** Only for independent tasks

**Complete Code Example:**

```python
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search

# Parallel researchers (run simultaneously)
tech_researcher = Agent(
    name="TechResearcher",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="Research latest AI/ML trends. Keep report to 100 words.",
    tools=[google_search],
    output_key="tech_research"
)

health_researcher = Agent(
    name="HealthResearcher",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="Research medical breakthroughs. Keep report to 100 words.",
    tools=[google_search],
    output_key="health_research"
)

finance_researcher = Agent(
    name="FinanceResearcher",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="Research fintech trends. Keep report to 100 words.",
    tools=[google_search],
    output_key="finance_research"
)

# Aggregator (runs after parallel research)
aggregator = Agent(
    name="Aggregator",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""Combine these findings into executive summary:

    Tech: {tech_research}
    Health: {health_research}
    Finance: {finance_research}

    Highlight common themes and key takeaways (200 words).""",
    output_key="executive_summary"
)

# Combine patterns: Parallel → Sequential
parallel_team = ParallelAgent(
    name="ResearchTeam",
    sub_agents=[tech_researcher, health_researcher, finance_researcher]
)

research_system = SequentialAgent(
    name="ResearchSystem",
    sub_agents=[parallel_team, aggregator]  # Parallel first, then aggregate
)

# Run the system
runner = InMemoryRunner(agent=research_system)
result = await runner.run_debug("Daily briefing on Tech, Health, Finance")
```

---

#### Pattern 4: Loop Workflow

**When to Use:** Need iterative refinement and quality control

**How it Works:** Repeatedly runs sub-agents until condition met or max iterations reached

```python
# Exit function for loop termination
def exit_loop():
    return {"status": "approved"}

refiner_agent = Agent(
    name="Refiner",
    instruction="If critique is APPROVED, call exit_loop. Otherwise, improve the story.",
    tools=[FunctionTool(exit_loop)]
)

loop = LoopAgent(
    name="RefinementLoop",
    sub_agents=[critic_agent, refiner_agent],
    max_iterations=5
)
```

**Example Use Case:** Story refinement
1. Critic reviews story
2. Refiner improves based on feedback
3. Loop continues until approved or max iterations

**Pros:** Iterative improvement, quality control
**Cons:** Slower, needs exit conditions

**Complete Code Example:**

```python
from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import FunctionTool

# Step 1: Create initial draft (runs once)
initial_writer = Agent(
    name="InitialWriter",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="Write a first draft (100-150 words) of a short story.",
    output_key="current_story"
)

# Step 2: Critic (runs in loop)
critic = Agent(
    name="Critic",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""Review this story: {current_story}

    If well-written and complete, respond EXACTLY: "APPROVED"
    Otherwise, give 2-3 specific suggestions for improvement.""",
    output_key="critique"
)

# Exit function
def exit_loop():
    """Call when story is approved to exit the refinement loop"""
    return {"status": "approved", "message": "Story approved!"}

# Step 3: Refiner (runs in loop)
refiner = Agent(
    name="Refiner",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""Story: {current_story}
    Critique: {critique}

    If critique is EXACTLY "APPROVED", call exit_loop function.
    Otherwise, rewrite the story incorporating the feedback.""",
    output_key="current_story",  # Overwrites the story
    tools=[FunctionTool(exit_loop)]
)

# Create the loop
refinement_loop = LoopAgent(
    name="RefinementLoop",
    sub_agents=[critic, refiner],
    max_iterations=3  # Prevent infinite loops
)

# Combine: Initial write → Refinement loop
story_pipeline = SequentialAgent(
    name="StoryPipeline",
    sub_agents=[initial_writer, refinement_loop]
)

# Run the system
runner = InMemoryRunner(agent=story_pipeline)
result = await runner.run_debug(
    "Write a short story about a lighthouse keeper who finds a glowing map"
)
```

**How the Loop Works:**
1. `initial_writer` creates first draft → stored in `current_story`
2. Loop begins:
   - `critic` reviews `current_story` → creates `critique`
   - `refiner` reads critique:
     - If "APPROVED" → calls `exit_loop()` → loop exits
     - Otherwise → rewrites story → updates `current_story`
   - Loop repeats (max 3 times)
3. Final refined story returned

---

### 11. FunctionTool - Custom Python Functions

Wrap Python functions to make them callable by agents:

```python
def exit_loop():
    """Exit the refinement loop when quality is sufficient"""
    return {"status": "approved", "message": "Loop exiting"}

agent = Agent(
    name="MyAgent",
    tools=[FunctionTool(exit_loop)]
)
```

**More Advanced Example:**

```python
from google.adk.tools import FunctionTool

# Custom function for calculations
def calculate_discount(price: float, discount_percent: float) -> dict:
    """Calculate discounted price"""
    discount_amount = price * (discount_percent / 100)
    final_price = price - discount_amount
    return {
        "original_price": price,
        "discount_percent": discount_percent,
        "discount_amount": discount_amount,
        "final_price": final_price
    }

# Custom function for data validation
def validate_email(email: str) -> dict:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = bool(re.match(pattern, email))
    return {
        "email": email,
        "is_valid": is_valid,
        "message": "Valid email" if is_valid else "Invalid email format"
    }

# Create agent with custom tools
shopping_agent = Agent(
    name="ShoppingAssistant",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""Help users with shopping queries.
    Use calculate_discount to compute sale prices.
    Use validate_email to check customer emails.""",
    tools=[
        FunctionTool(calculate_discount),
        FunctionTool(validate_email)
    ]
)

# Run the agent
runner = InMemoryRunner(agent=shopping_agent)
result = await runner.run_debug(
    "What's the final price of a $100 item with 20% discount?"
)
```

**Key Points:**
- Functions should have clear docstrings (agents use these to understand the tool)
- Use type hints for parameters
- Return structured data (dict, list, etc.)
- Keep functions focused on one task

---

## Decision Framework: Choosing the Right Pattern

**Use LLM-Based Orchestration when:**
- Need dynamic, intelligent routing
- Workflow depends on content/context
- Example: Research assistant that decides what to investigate

**Use Sequential when:**
- Order matters
- Need deterministic execution
- Each step builds on the previous
- Example: Document pipeline (outline → write → edit)

**Use Parallel when:**
- Tasks are independent
- Speed is critical
- Can execute concurrently
- Example: Multi-topic research, batch processing

**Use Loop when:**
- Iterative improvement needed
- Quality refinement required
- Need review/feedback cycles
- Example: Creative writing, code review

---

## Quick Reference Table

| Pattern | Execution | Use Case | Key Benefit |
|---------|-----------|----------|-------------|
| **LLM-Based** | Dynamic | Adaptive workflows | Intelligent routing |
| **Sequential** | One-by-one | Linear pipelines | Deterministic order |
| **Parallel** | Simultaneous | Independent tasks | Speed & efficiency |
| **Loop** | Iterative | Quality refinement | Continuous improvement |

---

## Key Takeaways

1. **Agents vs LLMs**: Agents can reason and take actions, not just respond
2. **Specialization**: Multiple focused agents > one "do-it-all" agent
3. **State Management**: Use `output_key` to pass data between agents
4. **Tool Ecosystem**: AgentTool, FunctionTool extend agent capabilities
5. **Workflow Patterns**: Choose the right pattern for your use case
6. **Composition**: Combine patterns (e.g., Parallel inside Sequential)
7. **ADK**: Code-first, model-agnostic framework for agent development

---

## Architecture Best Practices

1. **Keep agents focused** - One clear responsibility per agent
2. **Use explicit workflows** - Prefer Sequential/Parallel over LLM orchestration for predictability
3. **Combine patterns** - Nest agents for complex workflows
4. **Manage state properly** - Use clear `output_key` names
5. **Add exit conditions** - Always set `max_iterations` for LoopAgents
6. **Test in isolation** - Validate individual agents before composition

---

## Practical Examples

### Example 1: Simple Single Agent

```python
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search

# Create a simple Q&A agent
qa_agent = Agent(
    name="QAAgent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Answer questions concisely using search when needed.",
    tools=[google_search]
)

# Run it
runner = InMemoryRunner(agent=qa_agent)
response = await runner.run_debug("What is the capital of France?")
```

### Example 2: Two-Agent System with State Sharing

```python
# Agent 1: Data gatherer
data_agent = Agent(
    name="DataGatherer",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Collect data about the topic",
    tools=[google_search],
    output_key="raw_data"
)

# Agent 2: Data analyzer (uses Agent 1's output)
analysis_agent = Agent(
    name="DataAnalyzer",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Analyze this data: {raw_data} and provide insights",
    output_key="analysis"
)

# Coordinator
coordinator = Agent(
    name="Coordinator",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Call DataGatherer first, then DataAnalyzer",
    tools=[AgentTool(data_agent), AgentTool(analysis_agent)]
)

runner = InMemoryRunner(agent=coordinator)
result = await runner.run_debug("Analyze AI market trends")
```

### Example 3: Complete Multi-Agent System

```python
from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search, FunctionTool

# Custom function
def format_article(content: str, format: str = "markdown") -> str:
    """Format article content"""
    if format == "markdown":
        return f"# Article\n\n{content}\n\n---\n*Generated by AI*"
    return content

# Specialized agents
researcher = Agent(
    name="Researcher",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Research the topic thoroughly",
    tools=[google_search],
    output_key="findings"
)

writer = Agent(
    name="Writer",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Write article based on: {findings}",
    output_key="draft"
)

editor = Agent(
    name="Editor",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Edit and improve: {draft}",
    output_key="edited_content"
)

formatter = Agent(
    name="Formatter",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Format this article: {edited_content}",
    tools=[FunctionTool(format_article)],
    output_key="final"
)

# Composed workflow
pipeline = SequentialAgent(
    name="ContentPipeline",
    sub_agents=[researcher, writer, editor, formatter]
)

# Execute
runner = InMemoryRunner(agent=pipeline)
result = await runner.run_debug("Create an article about AI agents")
print(result)
```

### Example 4: Advanced Pattern Combination

```python
# Parallel research on multiple aspects
tech_researcher = Agent(
    name="TechResearcher",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Research technical aspects",
    tools=[google_search],
    output_key="tech_findings"
)

business_researcher = Agent(
    name="BusinessResearcher",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Research business implications",
    tools=[google_search],
    output_key="business_findings"
)

# Parallel research phase
parallel_research = ParallelAgent(
    name="ResearchPhase",
    sub_agents=[tech_researcher, business_researcher]
)

# Synthesis agent
synthesizer = Agent(
    name="Synthesizer",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="""Combine findings:
    Technical: {tech_findings}
    Business: {business_findings}
    Create comprehensive report.""",
    output_key="synthesis"
)

# Editor with quality check
editor = Agent(
    name="QualityEditor",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Polish and fact-check: {synthesis}",
    output_key="final_report"
)

# Complete pipeline: Parallel research → Synthesize → Edit
complete_system = SequentialAgent(
    name="ResearchReportSystem",
    sub_agents=[parallel_research, synthesizer, editor]
)

# Run
runner = InMemoryRunner(agent=complete_system)
result = await runner.run_debug("Create report on AI in healthcare")
```

---

## Common Patterns & Best Practices

### Pattern: Research → Process → Present

```python
# Step 1: Gather information
gather = Agent(name="Gatherer", tools=[google_search], output_key="data")

# Step 2: Process the information
process = Agent(name="Processor", instruction="Analyze: {data}", output_key="analysis")

# Step 3: Create presentation
present = Agent(name="Presenter", instruction="Summarize: {analysis}", output_key="result")

# Sequential execution
pipeline = SequentialAgent(
    name="Pipeline",
    sub_agents=[gather, process, present]
)
```

### Pattern: Parallel Processing → Aggregation

```python
# Multiple parallel workers
workers = [
    Agent(name=f"Worker{i}", instruction="Process task", output_key=f"result{i}")
    for i in range(3)
]

parallel_work = ParallelAgent(name="Workers", sub_agents=workers)

# Aggregate results
aggregator = Agent(
    name="Aggregator",
    instruction="Combine: {result0}, {result1}, {result2}",
    output_key="final"
)

# Combine: Parallel → Sequential
system = SequentialAgent(
    name="System",
    sub_agents=[parallel_work, aggregator]
)
```

### Pattern: Iterative Refinement

```python
# Reviewer
reviewer = Agent(
    name="Reviewer",
    instruction="Review {content}. Say 'APPROVED' if good, else suggest improvements",
    output_key="review"
)

# Improver
def exit_function():
    return {"status": "done"}

improver = Agent(
    name="Improver",
    instruction="If {review} is 'APPROVED', call exit_function. Else improve {content}",
    tools=[FunctionTool(exit_function)],
    output_key="content"
)

# Loop until approved
refinement = LoopAgent(
    name="Refinement",
    sub_agents=[reviewer, improver],
    max_iterations=5
)
```

---

## Troubleshooting & Tips

### Debugging Multi-Agent Systems

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use descriptive output_key names
agent = Agent(
    name="MyAgent",
    instruction="...",
    output_key="descriptive_name_for_output"  # Not just "output"
)

# Test agents individually first
runner = InMemoryRunner(agent=single_agent)
test_result = await runner.run_debug("test input")
print(f"Agent output: {test_result}")
```

### Common Mistakes to Avoid

```python
# ❌ BAD: Circular references
agent1 = Agent(instruction="Use {agent2_output}")
agent2 = Agent(instruction="Use {agent1_output}")  # Will fail!

# ✅ GOOD: Linear data flow
agent1 = Agent(output_key="step1")
agent2 = Agent(instruction="Use {step1}", output_key="step2")

# ❌ BAD: Missing output_key in pipeline
agent = Agent(instruction="Do work")  # No output_key!
next_agent = Agent(instruction="Use {???}")  # Can't access previous output

# ✅ GOOD: Always use output_key
agent = Agent(instruction="Do work", output_key="work_result")
next_agent = Agent(instruction="Use {work_result}")

# ❌ BAD: No max_iterations on LoopAgent
loop = LoopAgent(sub_agents=[...])  # Could loop forever!

# ✅ GOOD: Always set max_iterations
loop = LoopAgent(sub_agents=[...], max_iterations=5)
```

### Performance Tips

```python
# Use parallel when possible
# ❌ SLOW: Sequential independent tasks
seq = SequentialAgent(sub_agents=[task1, task2, task3])  # Takes 3x time

# ✅ FAST: Parallel independent tasks
par = ParallelAgent(sub_agents=[task1, task2, task3])  # Takes 1x time

# Use lighter models for simple tasks
heavy_agent = Agent(model=Gemini(model="gemini-2.0-pro"))  # Expensive
light_agent = Agent(model=Gemini(model="gemini-2.5-flash-lite"))  # Fast & cheap
```

This architecture ensures:
- Clear separation of concerns
- Predictable execution order
- Easy debugging (can test each agent independently)
- Maintainable code (modify one agent without affecting others)
