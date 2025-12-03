# Day 3: Memory Management in AI Agents

This document explains the core concepts from Google's Agent Development Kit (ADK) focused on building stateful AI agents with short-term and long-term memory capabilities.

## Table of Contents

1. [Overview](#overview)
2. [Sessions - Short-Term Memory](#sessions---short-term-memory)
3. [Memory - Long-Term Storage](#memory---long-term-storage)
4. [Context Engineering](#context-engineering)
5. [Practical Implementation Guide](#practical-implementation-guide)

---

## Overview

Large Language Models (LLMs) are inherently **stateless** - they only know what you tell them in a single API call. To build conversational agents that remember past interactions, we need two complementary systems:

| System | Purpose | Lifespan | Analogy |
|--------|---------|----------|---------|
| **Session** | Short-term conversation memory | Single conversation | Working memory |
| **Memory** | Long-term knowledge storage | Across all conversations | Long-term memory |

---

## Sessions - Short-Term Memory

### What is a Session?

A **Session** is a container for a single, continuous conversation between a user and an agent. It stores the chronological history of all interactions, including:

- User messages
- Agent responses
- Tool calls and their outputs
- Metadata about the conversation

### Key Components

#### 1. Session.Events

**Events** are the building blocks of a conversation. Each turn in the conversation creates events:

```
User Input Event → Agent Processing → Agent Response Event → Tool Call Event → Tool Output Event
```

**Example Event Types:**
- User message: "My favorite color is blue"
- Agent response: "I'll remember that!"
- Tool call: `save_user_preference(color="blue")`
- Tool output: `{"status": "saved"}`

#### 2. Session.State

**Session.State** is a key-value storage available to all agents and tools during a conversation. Think of it as a global scratchpad where the agent can store and retrieve dynamic information.

```python
# Writing to session state (in a tool)
def save_userinfo(tool_context: ToolContext, user_name: str, country: str):
    tool_context.state["user:name"] = user_name
    tool_context.state["user:country"] = country
    return {"status": "success"}

# Reading from session state
def retrieve_userinfo(tool_context: ToolContext):
    user_name = tool_context.state.get("user:name", "Username not found")
    country = tool_context.state.get("user:country", "Country not found")
    return {"user_name": user_name, "country": country}
```

**Best Practices for State Keys:**
- Use prefixes to organize data: `user:name`, `app:theme`, `temp:counter`
- State is session-specific (not shared across sessions by default)
- State is available to all tools and sub-agents

### Session Management Architecture

```
┌─────────────────────────────────────┐
│      Agentic Application            │
│  ┌──────────────────────────────┐  │
│  │          User                 │  │
│  │  ┌────────────────────────┐  │  │
│  │  │      Session           │  │  │
│  │  │  ┌──────────────────┐  │  │  │
│  │  │  │ Session.Events   │  │  │  │
│  │  │  └──────────────────┘  │  │  │
│  │  │  ┌──────────────────┐  │  │  │
│  │  │  │ Session.State    │  │  │  │
│  │  │  └──────────────────┘  │  │  │
│  │  └────────────────────────┘  │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

### SessionService Types

ADK provides different implementations for different needs:

#### InMemorySessionService
- **Storage:** RAM (temporary)
- **Persistence:** ❌ Lost on restart
- **Best for:** Development, testing, quick prototypes
- **Use case:** Learning and local experimentation

```python
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()
```

#### DatabaseSessionService
- **Storage:** SQL database (SQLite, PostgreSQL, etc.)
- **Persistence:** ✅ Survives restarts
- **Best for:** Small to medium production applications
- **Use case:** Self-managed deployments

```python
from google.adk.sessions import DatabaseSessionService

db_url = "sqlite:///my_agent_data.db"
session_service = DatabaseSessionService(db_url=db_url)
```

### The Runner: Session Orchestration

The **Runner** is the orchestration layer that manages information flow between users and agents. It automatically:

- Creates and retrieves sessions
- Maintains conversation history
- Manages context for the LLM
- Handles the execution flow

```python
from google.adk.runners import Runner

runner = Runner(
    agent=my_agent,
    app_name="MyApp",
    session_service=session_service
)

# Run a conversation
async for event in runner.run_async(
    user_id="user123",
    session_id="session456",
    new_message=user_query
):
    print(event.content)
```

### Session Workflow Example

```python
# Step 1: Create an agent
agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite"),
    name="chatbot",
    description="A helpful assistant"
)

# Step 2: Set up session management
session_service = InMemorySessionService()

# Step 3: Create a runner
runner = Runner(
    agent=agent,
    app_name="ChatApp",
    session_service=session_service
)

# Step 4: Have a conversation
session = await session_service.create_session(
    app_name="ChatApp",
    user_id="user123",
    session_id="session001"
)

# Multiple turns in the same session maintain context
async for event in runner.run_async(
    user_id="user123",
    session_id="session001",
    new_message="Hi, I'm Sam!"
):
    print(event.content)

# Agent remembers from previous turn
async for event in runner.run_async(
    user_id="user123",
    session_id="session001",
    new_message="What's my name?"
):
    print(event.content)  # "Your name is Sam!"
```

---

## Memory - Long-Term Storage

### What is Memory?

**Memory** is a searchable, long-term knowledge store that persists across multiple conversations. While Sessions handle individual conversation threads, Memory provides cross-session knowledge retention.

**Key Distinction:**
- **Session** = Application state (temporary, conversation-specific)
- **Memory** = Database (persistent, cross-conversation)

### Why Do We Need Memory?

| Capability | What It Means | Example |
|------------|---------------|---------|
| **Cross-Conversation Recall** | Access information from any past conversation | "What preferences has this user mentioned?" |
| **Intelligent Extraction** | LLM-powered consolidation extracts key facts | Stores "allergic to peanuts" instead of 50 raw messages |
| **Semantic Search** | Meaning-based retrieval, not just keyword matching | Query "preferred hue" matches "favorite color is blue" |
| **Persistent Storage** | Survives application restarts | Build knowledge that grows over time |

### Memory Workflow

There are three high-level steps to integrate Memory:

```
1. Initialize → Create MemoryService
2. Ingest → Transfer session data to memory
3. Retrieve → Search stored memories
```

### 1. Initialize MemoryService

```python
from google.adk.memory import InMemoryMemoryService

memory_service = InMemoryMemoryService()

# Provide to runner alongside session service
runner = Runner(
    agent=agent,
    app_name="MyApp",
    session_service=session_service,
    memory_service=memory_service  # Memory now available!
)
```

**Important:** Adding `memory_service` to the Runner makes memory *available*, but doesn't automatically use it. You must explicitly ingest data and enable retrieval.

### 2. Ingest Session Data into Memory

After a conversation, transfer it to long-term storage:

```python
# Have a conversation
await run_session(runner, "My favorite color is blue-green", "session-01")

# Get the session
session = await session_service.get_session(
    app_name="MyApp",
    user_id="user123",
    session_id="session-01"
)

# Transfer to memory
await memory_service.add_session_to_memory(session)
```

**What happens during transfer:**
- **InMemoryMemoryService:** Stores raw events without processing
- **VertexAiMemoryBankService:** Performs intelligent consolidation (extracts key facts)

### 3. Retrieve Memories

There are two ways to retrieve memories:

#### Manual Search (in code)

```python
search_response = await memory_service.search_memory(
    app_name="MyApp",
    user_id="user123",
    query="What is the user's favorite color?"
)

for memory in search_response.memories:
    print(memory.content.parts[0].text)
```

#### Agent-Based Retrieval (using tools)

ADK provides two built-in tools:

##### load_memory (Reactive)
- Agent decides when to search memory
- Only retrieves when the agent thinks it's needed
- More efficient (saves tokens)
- Risk: Agent might forget to search

```python
from google.adk.tools import load_memory

agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Use load_memory tool if you need past conversations.",
    tools=[load_memory]
)
```

##### preload_memory (Proactive)
- Automatically searches before every turn
- Memory always available to the agent
- Guaranteed context, but uses more tokens
- Searches even when not needed

```python
from google.adk.tools import preload_memory

agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Answer user questions.",
    tools=[preload_memory]
)
```

**Comparison:**

| Aspect | load_memory | preload_memory |
|--------|-------------|----------------|
| When | Agent decides | Every turn |
| Efficiency | Higher | Lower |
| Reliability | Depends on agent | Guaranteed |
| Best for | Cost-sensitive apps | Critical context apps |

### Automating Memory Storage with Callbacks

Instead of manually calling `add_session_to_memory()`, use callbacks to automate:

```python
# Define callback
async def auto_save_to_memory(callback_context):
    """Automatically save session to memory after each agent turn."""
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )

# Attach to agent
agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite"),
    name="AutoMemoryAgent",
    tools=[preload_memory],
    after_agent_callback=auto_save_to_memory  # Saves automatically!
)
```

**Available callback types:**
- `before_agent_callback` - Before agent starts processing
- `after_agent_callback` - After agent completes its turn
- `before_tool_callback` / `after_tool_callback` - Around tool calls
- `before_model_callback` / `after_model_callback` - Around LLM calls
- `on_model_error_callback` - When errors occur

### Memory Consolidation

**The Problem:** Storing raw conversation events doesn't scale.

**Before (Raw Storage):**
```
User: "My favorite color is BlueGreen. I also like purple.
       Actually, I prefer BlueGreen most of the time."
Agent: "Great! I'll remember that."
User: "Thanks!"
Agent: "You're welcome!"

→ Stores ALL 4 messages (redundant, verbose)
```

**After (Consolidation):**
```
Extracted Memory: "User's favorite color: BlueGreen"

→ Stores 1 concise fact
```

**How it works:**
1. Raw Session Events
2. LLM analyzes conversation
3. Extracts key facts
4. Stores concise memories
5. Merges with existing memories (deduplication)

**Memory Service Comparison:**

| Feature | InMemoryMemoryService | VertexAiMemoryBankService |
|---------|----------------------|---------------------------|
| Storage | In-memory (temporary) | Cloud (persistent) |
| Search | Keyword matching | Semantic search |
| Consolidation | ❌ Stores raw events | ✅ LLM-powered extraction |
| Best for | Learning, prototypes | Production applications |

---

## Context Engineering

### The Problem

As conversations grow, the context sent to the LLM becomes massive:

```
Session: 50 messages = 10,000 tokens
Cost: Higher API costs
Performance: Slower responses
Quality: Agent loses focus
```

### Context Compaction

**Context Compaction** automatically summarizes older parts of the conversation, reducing token usage while maintaining important information.

```python
from google.adk.apps.app import App, EventsCompactionConfig

# Create app with compaction
app = App(
    name="research_app",
    root_agent=agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3,  # Compact every 3 turns
        overlap_size=1  # Keep 1 previous turn for context
    )
)

# Provide app to runner
runner = Runner(app=app, session_service=session_service)
```

**What happens:**
1. After 3 conversation turns, compaction triggers
2. LLM summarizes the older turns into a concise summary
3. Summary replaces the verbose original turns
4. Future turns use the summary instead of full history

**Benefits:**
- Reduced token usage → Lower costs
- Faster response times
- Agent stays focused on important information

### Additional Context Engineering Tools

#### Custom Compaction

You can provide your own summarization logic:

```python
from google.adk.context import SlidingWindowCompactor

custom_compactor = SlidingWindowCompactor(
    window_size=5,
    overlap=1,
    # Custom summarization prompt
)
```

#### Context Caching

Reduce token size of static instructions by caching request data. See [ADK Context Caching Documentation](https://google.github.io/adk-docs/context/caching/).

---

## Practical Implementation Guide

### Scenario 1: Simple Chatbot (Sessions Only)

**Use case:** Conversation within a single session, no need for cross-session memory.

```python
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Create agent
agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite"),
    name="chatbot",
    description="A helpful assistant"
)

# Set up session management
session_service = InMemorySessionService()
runner = Runner(agent=agent, app_name="ChatApp", session_service=session_service)

# Have a conversation
async for event in runner.run_async(
    user_id="user123",
    session_id="session001",
    new_message="Hi, I'm Sam!"
):
    print(event.content)
```

### Scenario 2: Persistent Chatbot (Database Sessions)

**Use case:** Conversations that survive application restarts.

```python
from google.adk.sessions import DatabaseSessionService

# Use database instead of in-memory
db_url = "sqlite:///chatbot_data.db"
session_service = DatabaseSessionService(db_url=db_url)

runner = Runner(agent=agent, app_name="ChatApp", session_service=session_service)

# Sessions now persist across restarts!
```

### Scenario 3: Agent with Long-Term Memory (Manual)

**Use case:** Agent needs to remember information across different conversations.

```python
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import load_memory

# Create memory service
memory_service = InMemoryMemoryService()

# Agent with memory tool
agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Use load_memory tool if you need past conversations.",
    tools=[load_memory]
)

# Runner with both services
runner = Runner(
    agent=agent,
    app_name="MemoryApp",
    session_service=session_service,
    memory_service=memory_service
)

# Have conversation
await run_session(runner, "My birthday is March 15th", "session-01")

# Manually save to memory
session = await session_service.get_session(
    app_name="MemoryApp",
    user_id="user123",
    session_id="session-01"
)
await memory_service.add_session_to_memory(session)

# Test recall in new session
await run_session(runner, "When is my birthday?", "session-02")
# Agent uses load_memory tool and responds: "March 15th"
```

### Scenario 4: Fully Automated Memory Agent

**Use case:** Production-ready agent with automatic memory management.

```python
from google.adk.tools import preload_memory

# Callback for automatic memory saving
async def auto_save_to_memory(callback_context):
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )

# Agent with automatic memory
agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Answer user questions.",
    tools=[preload_memory],  # Automatically loads memory
    after_agent_callback=auto_save_to_memory  # Automatically saves memory
)

runner = Runner(
    agent=agent,
    app_name="AutoMemoryApp",
    session_service=session_service,
    memory_service=memory_service
)

# Everything happens automatically!
# - Memory is loaded before each turn
# - Memory is saved after each turn
```

### Scenario 5: Long Conversation with Context Compaction

**Use case:** Agent handles long conversations efficiently.

```python
from google.adk.apps.app import App, EventsCompactionConfig

# Create app with compaction
app = App(
    name="research_app",
    root_agent=agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=5,  # Compact every 5 turns
        overlap_size=2  # Keep 2 previous turns
    )
)

runner = Runner(app=app, session_service=session_service)

# Long conversations automatically get compacted
# to maintain performance and reduce costs
```

### Scenario 6: Session State for User Preferences

**Use case:** Track structured information during a conversation.

```python
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any

# Define tools that use session state
def save_user_preferences(
    tool_context: ToolContext,
    theme: str,
    language: str
) -> Dict[str, Any]:
    """Save user preferences to session state."""
    tool_context.state["user:theme"] = theme
    tool_context.state["user:language"] = language
    return {"status": "saved"}

def get_user_preferences(tool_context: ToolContext) -> Dict[str, Any]:
    """Retrieve user preferences from session state."""
    return {
        "theme": tool_context.state.get("user:theme", "default"),
        "language": tool_context.state.get("user:language", "en")
    }

# Agent with state management tools
agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite"),
    tools=[save_user_preferences, get_user_preferences],
    description="""
    Use save_user_preferences when user mentions preferences.
    Use get_user_preferences when you need to know user preferences.
    """
)
```

---

## Best Practices

### Session Management
1. **Use descriptive session IDs** that map to real user conversations
2. **Choose the right SessionService** for your deployment:
   - Development: `InMemorySessionService`
   - Production: `DatabaseSessionService` or managed cloud service
3. **Organize state keys** with prefixes: `user:`, `app:`, `temp:`
4. **Implement context compaction** for long conversations

### Memory Management
1. **Decide on retrieval strategy:**
   - Use `load_memory` for cost-sensitive applications
   - Use `preload_memory` when context is critical
2. **Automate memory storage** with callbacks instead of manual calls
3. **Use managed services** (Vertex AI Memory Bank) for production:
   - Automatic consolidation
   - Semantic search
   - Persistent cloud storage
4. **Save to memory strategically:**
   - After every turn (real-time, higher cost)
   - End of conversation (batch, lower cost)
   - Periodic intervals (long conversations)

### Context Engineering
1. **Enable compaction** for conversations with >5 turns
2. **Balance overlap** - too little loses context, too much wastes tokens
3. **Monitor token usage** to optimize compaction settings
4. **Consider context caching** for frequently used static instructions

---

## Summary

### Session (Short-Term Memory)
- **What:** Container for single conversation
- **Components:** Events (conversation turns) + State (key-value storage)
- **When to use:** All agents need sessions for context
- **Storage:** InMemorySessionService (dev) or DatabaseSessionService (prod)

### Memory (Long-Term Storage)
- **What:** Searchable knowledge store across conversations
- **How:** Add sessions to memory → Search when needed
- **Tools:** `load_memory` (reactive) or `preload_memory` (proactive)
- **Automation:** Use callbacks for automatic saving
- **Storage:** InMemoryMemoryService (dev) or VertexAiMemoryBankService (prod)

### Context Engineering
- **Compaction:** Automatically summarize old conversation turns
- **Caching:** Reduce costs for static instructions
- **Goal:** Maintain quality while reducing token usage

### The Complete Stack

```
┌─────────────────────────────────────────────┐
│          Agent (LLM + Tools)                │
│  - Processes queries                        │
│  - Uses memory tools (load/preload)         │
│  - Callbacks for automation                 │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│            Runner (Orchestrator)            │
│  - Manages execution flow                   │
│  - Handles sessions and memory              │
│  - Applies context compaction               │
└─────────────────────────────────────────────┘
         ↓                        ↓
┌──────────────────────┐  ┌──────────────────┐
│  SessionService      │  │  MemoryService   │
│  (Short-term)        │  │  (Long-term)     │
│  - Conversation      │  │  - Knowledge     │
│  - Events + State    │  │  - Searchable    │
│  - Single session    │  │  - Cross-session │
└──────────────────────┘  └──────────────────┘
```

---

## Commands, Tricks & Patterns Reference

### Essential Imports

```python
# Core ADK imports
from google.adk.agents import Agent, LlmAgent
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, DatabaseSessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import load_memory, preload_memory
from google.adk.tools.tool_context import ToolContext
from google.adk.context import SlidingWindowCompactor
from google.genai import types

# Typing support
from typing import Any, Dict
```

### Configuration Patterns

#### Retry Configuration for API Calls

```python
# Configure retry behavior for LLM API calls
retry_config = types.HttpRetryOptions(
    attempts=5,                           # Maximum retry attempts
    exp_base=7,                           # Delay multiplier for exponential backoff
    initial_delay=1,                      # Initial delay in seconds
    http_status_codes=[429, 500, 503, 504]  # HTTP errors to retry
)

# Use in agent creation
agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config)
)
```

#### Environment Setup for Kaggle

```python
import os
from kaggle_secrets import UserSecretsClient

try:
    GOOGLE_API_KEY = UserSecretsClient().get_secret("GOOGLE_API_KEY")
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    print("✅ Gemini API key setup complete.")
except Exception as e:
    print(f"🔑 Authentication Error: {e}")
```

### Helper Function Patterns

#### Universal Session Runner

```python
async def run_session(
    runner_instance: Runner,
    user_queries: list[str] | str = None,
    session_name: str = "default",
):
    """
    Comprehensive helper for running sessions with automatic creation/retrieval.
    Handles both single queries and multiple queries in sequence.
    """
    print(f"\n ### Session: {session_name}")

    app_name = runner_instance.app_name

    # Try-except pattern for create-or-get session
    try:
        session = await session_service.create_session(
            app_name=app_name, user_id=USER_ID, session_id=session_name
        )
    except:
        session = await session_service.get_session(
            app_name=app_name, user_id=USER_ID, session_id=session_name
        )

    # Handle both single query and list of queries
    if user_queries:
        if type(user_queries) == str:
            user_queries = [user_queries]

        # Process each query sequentially
        for query in user_queries:
            print(f"\nUser > {query}")

            # Convert string to ADK Content format
            query = types.Content(role="user", parts=[types.Part(text=query)])

            # Stream responses
            async for event in runner_instance.run_async(
                user_id=USER_ID, session_id=session.id, new_message=query
            ):
                # Filter out empty/None responses
                if event.content and event.content.parts:
                    if (event.content.parts[0].text != "None"
                        and event.content.parts[0].text):
                        print(f"Model > ", event.content.parts[0].text)
```

#### Alternative Streaming Pattern

```python
async def run_session_final_only(
    runner_instance: Runner,
    user_queries: list[str] | str,
    session_id: str = "default"
):
    """Only show final responses, not intermediate events."""

    # Create/get session (same as above)
    try:
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )
    except:
        session = await session_service.get_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )

    # Convert single query to list
    if isinstance(user_queries, str):
        user_queries = [user_queries]

    for query in user_queries:
        print(f"\nUser > {query}")
        query_content = types.Content(role="user", parts=[types.Part(text=query)])

        # Only show final response
        async for event in runner_instance.run_async(
            user_id=USER_ID, session_id=session.id, new_message=query_content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                text = event.content.parts[0].text
                if text and text != "None":
                    print(f"Model: > {text}")
```

### Session Management Patterns

#### Create or Retrieve Session Pattern

```python
# Pattern 1: Try-except
try:
    session = await session_service.create_session(
        app_name="MyApp",
        user_id="user123",
        session_id="session001"
    )
except:
    session = await session_service.get_session(
        app_name="MyApp",
        user_id="user123",
        session_id="session001"
    )

# Pattern 2: Direct retrieval (when you know it exists)
session = await session_service.get_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id="my-session"
)
```

#### Inspecting Session Contents

```python
# Get session
session = await session_service.get_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id="session-id"
)

# Iterate through events
print("📝 Session contains:")
for event in session.events:
    # Extract text from event (with safety checks)
    text = (
        event.content.parts[0].text[:60]  # Truncate to 60 chars
        if event.content and event.content.parts
        else "(empty)"
    )
    print(f"  {event.content.role}: {text}...")

# Check session state
print("Session State:")
print(session.state)
```

#### Finding Compaction Events

```python
# Search for compaction summary in session history
final_session = await session_service.get_session(
    app_name=runner.app_name,
    user_id=USER_ID,
    session_id="session-id"
)

print("--- Searching for Compaction Summary Event ---")
found_summary = False
for event in final_session.events:
    # Compaction events have a 'compaction' attribute
    if event.actions and event.actions.compaction:
        print("\n✅ SUCCESS! Found the Compaction Event:")
        print(f"  Author: {event.author}")
        print(f"\n Compacted information: {event}")
        found_summary = True
        break

if not found_summary:
    print("\n❌ No compaction event found.")
```

### Database Operations

#### SQLite Session Inspection

```python
import sqlite3

def check_data_in_db():
    """Inspect session data stored in SQLite database."""
    with sqlite3.connect("my_agent_data.db") as connection:
        cursor = connection.cursor()

        # Query all events
        result = cursor.execute(
            "select app_name, session_id, author, content from events"
        )

        # Print column headers
        print([_[0] for _ in result.description])

        # Print all rows
        for each in result.fetchall():
            print(each)

check_data_in_db()
```

#### Database Cleanup

```python
import os

# Clean up database file
if os.path.exists("my_agent_data.db"):
    os.remove("my_agent_data.db")
print("✅ Cleaned up old database files")
```

### Memory Operations

#### Manual Memory Search with Result Inspection

```python
# Search for specific information
search_response = await memory_service.search_memory(
    app_name=APP_NAME,
    user_id=USER_ID,
    query="What is the user's favorite color?"
)

# Inspect results
print("🔍 Search Results:")
print(f"  Found {len(search_response.memories)} relevant memories")
print()

for memory in search_response.memories:
    if memory.content and memory.content.parts:
        # Truncate text for display
        text = memory.content.parts[0].text[:80]
        print(f"  [{memory.author}]: {text}...")
```

#### Memory Transfer Pattern

```python
# Pattern 1: After conversation - manual
await run_session(runner, "My favorite color is blue", "session-01")

session = await session_service.get_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id="session-01"
)

await memory_service.add_session_to_memory(session)

# Pattern 2: Automatic with callback (defined in agent)
async def auto_save_to_memory(callback_context):
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )
```

### Agent Creation Patterns

#### Basic Agent

```python
# Pattern 1: Using Agent class
root_agent = Agent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="text_chat_bot",
    description="A text chatbot"
)

# Pattern 2: Using LlmAgent class (more common)
agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="chatbot",
    description="A helpful assistant"
)
```

#### Agent with Tools

```python
agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="text_chat_bot",
    description="""A text chatbot.
    Tools for managing user context:
    * To record username and country when provided use `save_userinfo` tool.
    * To fetch username and country when required use `retrieve_userinfo` tool.
    """,
    tools=[save_userinfo, retrieve_userinfo]  # Custom tools
)
```

#### Agent with Memory Tools

```python
# Reactive memory
agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Use load_memory tool if you need past conversations.",
    tools=[load_memory]
)

# Proactive memory
agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Answer user questions.",
    tools=[preload_memory]
)
```

#### Agent with Callbacks

```python
agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite"),
    name="AutoMemoryAgent",
    instruction="Answer user questions.",
    tools=[preload_memory],
    after_agent_callback=auto_save_to_memory  # Callback function
)
```

### Tool Definition Patterns

#### Session State Tools

```python
# Write to session state
def save_userinfo(
    tool_context: ToolContext,
    user_name: str,
    country: str
) -> Dict[str, Any]:
    """
    Tool to record and save user name and country in session state.

    Args:
        user_name: The username to store in session state
        country: The name of the user's country
    """
    # Write to session state with prefix
    tool_context.state["user:name"] = user_name
    tool_context.state["user:country"] = country

    return {"status": "success"}

# Read from session state
def retrieve_userinfo(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Tool to retrieve user name and country from session state.
    """
    # Read with default fallback
    user_name = tool_context.state.get("user:name", "Username not found")
    country = tool_context.state.get("user:country", "Country not found")

    return {
        "status": "success",
        "user_name": user_name,
        "country": country
    }
```

#### State Key Naming Convention

```python
# Best practices for state key prefixes
USER_NAME_SCOPE_LEVELS = ("temp", "user", "app")

# Examples:
tool_context.state["user:name"] = "Sam"           # User-specific
tool_context.state["user:preferences"] = {...}    # User preferences
tool_context.state["app:theme"] = "dark"          # App-level
tool_context.state["temp:counter"] = 5            # Temporary data
```

### App Configuration Patterns

#### App with Context Compaction

```python
# Create app wrapper for advanced features
app = App(
    name="research_app_compacting",
    root_agent=chatbot_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3,  # Trigger compaction every 3 invocations
        overlap_size=1          # Keep 1 previous turn for context
    )
)

# Use app instead of agent in runner
runner = Runner(app=app, session_service=session_service)
```

#### Custom Compaction (Advanced)

```python
from google.adk.context import SlidingWindowCompactor

custom_compactor = SlidingWindowCompactor(
    window_size=5,
    overlap=1
)

app = App(
    name="my_app",
    root_agent=agent,
    compactor=custom_compactor  # Use custom compactor
)
```

### Runner Patterns

#### Basic Runner Setup

```python
# Pattern 1: Agent only
runner = Runner(
    agent=agent,
    app_name="MyApp",
    session_service=session_service
)

# Pattern 2: App (with advanced features)
runner = Runner(
    app=app,
    session_service=session_service
)

# Pattern 3: With memory
runner = Runner(
    agent=agent,
    app_name="MyApp",
    session_service=session_service,
    memory_service=memory_service
)
```

#### Running Queries

```python
# Pattern 1: Direct async iteration
async for event in runner.run_async(
    user_id="user123",
    session_id="session001",
    new_message=query_content
):
    if event.content and event.content.parts:
        print(event.content.parts[0].text)

# Pattern 2: Final response only
async for event in runner.run_async(
    user_id=USER_ID,
    session_id=session.id,
    new_message=query_content
):
    if event.is_final_response():
        if event.content and event.content.parts:
            print(event.content.parts[0].text)
```

### Message Format Conversion

```python
# Convert string to ADK Content format
user_message = "Hello, how are you?"

# Method 1: Using types.Content
query_content = types.Content(
    role="user",
    parts=[types.Part(text=user_message)]
)

# Use in runner
async for event in runner.run_async(
    user_id=USER_ID,
    session_id=session_id,
    new_message=query_content
):
    pass
```

### Error Handling Patterns

#### Safe Event Content Access

```python
# Always check for None before accessing
if event.content and event.content.parts:
    text = event.content.parts[0].text
    if text and text != "None":  # Filter out "None" strings
        print(text)

# Truncate with safety
text = (
    event.content.parts[0].text[:60]
    if event.content and event.content.parts
    else "(empty)"
)
```

#### Session Creation Error Handling

```python
# Graceful fallback pattern
try:
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
except Exception as e:
    # Session might already exist, try to get it
    session = await session_service.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
```

### Callback Patterns

#### Basic Callback Structure

```python
# Callbacks receive callback_context automatically
async def my_callback(callback_context):
    """
    Callback function structure.
    callback_context provides access to:
    - _invocation_context.memory_service
    - _invocation_context.session
    - _invocation_context.session_service
    """
    # Access services
    memory_service = callback_context._invocation_context.memory_service
    session = callback_context._invocation_context.session

    # Perform actions
    await memory_service.add_session_to_memory(session)
```

#### All Callback Types

```python
# Before agent processes request
async def before_agent_callback(callback_context):
    print("Agent is about to start processing")

# After agent completes turn
async def after_agent_callback(callback_context):
    print("Agent finished processing")
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )

# Around tool calls
async def before_tool_callback(callback_context):
    print("About to call a tool")

async def after_tool_callback(callback_context):
    print("Tool execution completed")

# Around model calls
async def before_model_callback(callback_context):
    print("About to call LLM")

async def after_model_callback(callback_context):
    print("LLM call completed")

# On errors
async def on_model_error_callback(callback_context):
    print("Error occurred during model call")

# Attach to agent
agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite"),
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
    on_model_error_callback=on_model_error_callback
)
```

### Testing Patterns

#### Multi-Turn Conversation Test

```python
# Test pattern: Multiple queries in same session
await run_session(
    runner,
    [
        "Hi, I am Sam! What is the capital of United States?",
        "Hello! What is my name?",  # Agent should remember
    ],
    "stateful-agentic-session"
)
```

#### Cross-Session Memory Test

```python
# Step 1: Store information in session-01
await run_session(runner, "My birthday is March 15th.", "session-01")

# Step 2: Manually save to memory
session = await session_service.get_session(
    app_name=APP_NAME, user_id=USER_ID, session_id="session-01"
)
await memory_service.add_session_to_memory(session)

# Step 3: Test recall in new session-02
await run_session(runner, "When is my birthday?", "session-02")
# Should retrieve from memory and answer correctly
```

#### Automated Memory Test

```python
# Agent with automatic save and load
auto_memory_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite"),
    tools=[preload_memory],  # Auto-load
    after_agent_callback=auto_save_to_memory  # Auto-save
)

runner = Runner(
    agent=auto_memory_agent,
    app_name=APP_NAME,
    session_service=session_service,
    memory_service=memory_service
)

# Test 1: Store information
await run_session(
    runner,
    "I gifted a new toy to my nephew on his 1st birthday!",
    "auto-save-test"
)  # Automatically saved to memory

# Test 2: Recall in new session
await run_session(
    runner,
    "What did I gift my nephew?",
    "auto-save-test-2"  # Different session - memory automatically loaded
)
```

### Common Tricks

#### 1. List to Single Query Auto-Conversion

```python
# Handle both single query and list
if type(user_queries) == str:
    user_queries = [user_queries]

# Now can always iterate
for query in user_queries:
    # Process
    pass
```

#### 2. Text Truncation for Display

```python
# Truncate long text
text = event.content.parts[0].text[:60]  # First 60 chars

# With ellipsis
text = f"{text[:60]}..." if len(text) > 60 else text
```

#### 3. Null-Safe Chaining

```python
# Safe access pattern
text = (
    event.content.parts[0].text
    if event.content and event.content.parts
    else "(empty)"
)
```

#### 4. Session State Default Values

```python
# Get with fallback
value = tool_context.state.get("user:name", "default_value")

# Multiple defaults
theme = tool_context.state.get("user:theme", "light")
language = tool_context.state.get("user:language", "en")
```

#### 5. Conditional Printing

```python
# Filter out None and "None" strings
if text and text != "None":
    print(text)
```

#### 6. Using isinstance() for Type Checking

```python
# More pythonic than type()
if isinstance(user_queries, str):
    user_queries = [user_queries]
```

### Performance Optimization Tricks

#### 1. Compaction Configuration

```python
# For short conversations (5-10 turns)
EventsCompactionConfig(
    compaction_interval=5,
    overlap_size=1
)

# For long conversations (20+ turns)
EventsCompactionConfig(
    compaction_interval=10,
    overlap_size=2
)

# For very long conversations (50+ turns)
EventsCompactionConfig(
    compaction_interval=15,
    overlap_size=3
)
```

#### 2. Memory Search Optimization

```python
# Use specific queries instead of broad ones
# Good: "What is user's favorite color?"
# Bad: "Tell me everything about the user"

search_response = await memory_service.search_memory(
    app_name=APP_NAME,
    user_id=USER_ID,
    query="What is user's favorite color?"  # Specific
)
```

#### 3. Batch Memory Saves

```python
# Instead of saving after every turn, batch at conversation end
async def save_on_conversation_end(callback_context):
    """Only save when conversation ends (custom logic needed)"""
    # Your logic to determine conversation end
    if is_conversation_ended():
        await callback_context._invocation_context.memory_service.add_session_to_memory(
            callback_context._invocation_context.session
        )
```

### Debugging Patterns

#### 1. Print Session Events

```python
session = await session_service.get_session(app_name, user_id, session_id)

for i, event in enumerate(session.events):
    print(f"Event {i}:")
    print(f"  Role: {event.content.role if event.content else 'N/A'}")
    print(f"  Author: {event.author}")
    if event.content and event.content.parts:
        print(f"  Text: {event.content.parts[0].text[:100]}")
    print()
```

#### 2. Inspect Memory Search Results

```python
search_response = await memory_service.search_memory(
    app_name=APP_NAME,
    user_id=USER_ID,
    query="search query"
)

print(f"Found {len(search_response.memories)} memories")
for i, memory in enumerate(search_response.memories):
    print(f"\nMemory {i}:")
    print(f"  Author: {memory.author}")
    if memory.content and memory.content.parts:
        print(f"  Content: {memory.content.parts[0].text}")
```

#### 3. Check Event Properties

```python
for event in session.events:
    print(f"Event attributes:")
    print(f"  - has content: {event.content is not None}")
    print(f"  - has actions: {event.actions is not None}")
    if event.actions:
        print(f"  - has compaction: {event.actions.compaction is not None}")
```

---

## Additional Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [ADK Sessions Guide](https://google.github.io/adk-docs/sessions/overview/)
- [ADK Memory Guide](https://google.github.io/adk-docs/sessions/memory/)
- [ADK Context Compaction](https://google.github.io/adk-docs/context/compaction/)
- [ADK Callbacks](https://google.github.io/adk-docs/agents/callbacks/)
- [Vertex AI Memory Bank](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview)
