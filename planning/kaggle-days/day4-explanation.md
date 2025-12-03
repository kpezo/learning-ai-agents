# Day 4 Complete Guide: Agent Observability and Evaluation

**A Comprehensive Tutorial on Debugging, Monitoring, and Testing AI Agents**

---

## Table of Contents

1. [Part A: Agent Observability](#part-a-agent-observability)
   - [What is Observability?](#what-is-observability)
   - [The Three Pillars](#the-three-pillars-of-observability)
   - [Logging Configuration](#logging-configuration)
   - [Debugging with ADK Web UI](#debugging-with-adk-web-ui)
   - [Plugins and Callbacks](#plugins-and-callbacks)
   - [Production Logging](#production-logging)

2. [Part B: Agent Evaluation](#part-b-agent-evaluation)
   - [What is Evaluation?](#what-is-agent-evaluation)
   - [Interactive Evaluation](#interactive-evaluation-with-adk-web-ui)
   - [Evaluation Metrics](#understanding-evaluation-metrics)
   - [Systematic Evaluation](#systematic-evaluation)
   - [User Simulation](#user-simulation-advanced)

3. [Quick Reference Guide](#quick-reference-guide)

---

# Part A: Agent Observability

## What is Observability?

### Declarative: What It Does

**Agent Observability** provides complete visibility into your AI agent's decision-making process. It reveals:
- What prompts are sent to the LLM
- Which tools are available and used
- How the model responds
- Where failures occur
- Why specific decisions were made

Unlike traditional software that fails predictably with stack traces and error codes, AI agents can fail mysteriously. Observability transforms these mysterious failures into clear, debuggable problems.

### Conditional: When to Use It

Use observability when:
- **Debugging mysterious failures**: Agent responds with "I cannot help with that request" without explanation
- **Understanding agent behavior**: You need to see the complete chain of reasoning
- **Performance optimization**: Identifying which steps take the longest
- **Production monitoring**: Tracking agent health in deployed systems
- **Quality assurance**: Ensuring agents make optimal tool choices

### Procedural: How to Implement It

**Problem Example:**
```
User: "Find quantum computing papers"
Agent: "I cannot help with that request."
You: 😭 WHY?? Is it the prompt? Missing tools? API error?
```

**Solution with Observability:**
```
DEBUG Log: LLM Request shows "Functions: []" (no tools!)
You: 🎯 Aha! Missing google_search tool - easy fix!
```

---

## The Three Pillars of Observability

### 1. Logs

#### Declarative: What They Are

**Logs** are records of individual events that tell you **what** happened at a specific moment in time. Each log entry captures:
- A timestamp
- A log level (DEBUG, INFO, WARNING, ERROR)
- The component that generated it
- The event description
- Relevant data

#### Conditional: When to Use Logs

Use logs when you need to:
- **Track specific events**: "Did the agent call this tool?"
- **Debug step-by-step**: "What happened right before the failure?"
- **Audit agent actions**: "What decisions did the agent make?"
- **Troubleshoot issues**: "Where did the error occur?"

#### Procedural: How to Configure Logging

**Step 1: Set up basic logging**

```python
import logging
import os

# Clean up any previous logs
for log_file in ["logger.log", "web.log", "tunnel.log"]:
    if os.path.exists(log_file):
        os.remove(log_file)
        print(f"🧹 Cleaned up {log_file}")

# Configure logging with DEBUG log level
logging.basicConfig(
    filename="logger.log",
    level=logging.DEBUG,  # Shows ALL log levels
    format="%(filename)s:%(lineno)s %(levelname)s:%(message)s",
)
```

**Log Levels Explained:**

| Level | What It Shows | When to Use |
|-------|--------------|-------------|
| **DEBUG** | Everything - LLM requests, responses, internal state | Development, detailed debugging |
| **INFO** | General information about agent flow | Development, general monitoring |
| **WARNING** | Potential issues that don't stop execution | Production monitoring |
| **ERROR** | Failures and exceptions | Production error tracking |

**Step 2: Run agent with DEBUG logging**

```bash
adk web --log_level DEBUG
```

**What you'll see:**
```
DEBUG - google_adk.models.google_llm - LLM Request: {
  "system_instruction": "You are a helpful assistant...",
  "contents": [...],
  "tools": [...]
}
DEBUG - google_adk.models.google_llm - LLM Response: {
  "candidates": [...],
  "usage_metadata": {...}
}
```

### 2. Traces

#### Declarative: What They Are

**Traces** connect individual logs into a complete story, showing you **why** a final result occurred by revealing the entire sequence of steps. A trace shows:
- The full execution path from user input to final response
- How long each step took
- The relationships between different operations
- The complete context of what happened

#### Conditional: When to Use Traces

Use traces when you need to:
- **Understand complete workflows**: "What was the full path from question to answer?"
- **Debug complex failures**: "Which step in the chain broke?"
- **Optimize performance**: "Which operation is the bottleneck?"
- **Analyze decision chains**: "Why did the agent choose this path?"

#### Procedural: How to Use Traces in ADK Web UI

**Step 1: Run your agent**
```bash
adk web --log_level DEBUG
```

**Step 2: Navigate to the Events tab**
1. Open ADK Web UI
2. Interact with your agent (send a message)
3. Click the **"Events"** tab in the left sidebar

**Step 3: Analyze the trace**
1. You'll see a chronological list of all agent actions
2. Click on any event to expand its details
3. Click the **"Trace"** button to see timing information

**What you'll see in a trace:**

```
User Message Received
└─ call_llm (150ms)
   └─ execute_tool: google_search_agent (2.3s)
      └─ call_llm (180ms)
         └─ execute_tool: google_search (1.8s)
            └─ tool_result (50ms)
   └─ execute_tool: count_papers (10ms)
      └─ ERROR: TypeError: object of type 'str' has no len()
   └─ final_response (20ms)
```

**Reading a trace:**
- **Indentation** shows parent-child relationships
- **Timing** (in parentheses) shows how long each step took
- **Errors** are highlighted and easy to spot
- **Tool calls** show which functions were invoked

### 3. Metrics

#### Declarative: What They Are

**Metrics** are summary numbers that tell you **how** well the agent is performing overall. They aggregate data from many logs and traces to show trends and patterns:
- Average response time
- Success/failure rates
- Tool usage statistics
- Error counts by type
- Performance trends over time

#### Conditional: When to Use Metrics

Use metrics when you need to:
- **Monitor production health**: "Is the agent performing well?"
- **Track performance trends**: "Are response times increasing?"
- **Identify patterns**: "Which tools fail most often?"
- **Make data-driven decisions**: "Should we optimize this operation?"
- **Set SLA targets**: "Are we meeting our 2-second response time goal?"

#### Procedural: How to Calculate and Track Metrics

**Using the built-in LoggingPlugin** (covered in detail below), you automatically get:

```python
from google.adk.plugins.logging_plugin import LoggingPlugin

# LoggingPlugin captures metrics automatically
runner = InMemoryRunner(
    agent=my_agent,
    plugins=[LoggingPlugin()]
)
```

**Custom metrics with a Plugin:**

```python
class MetricsPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="metrics")
        self.agent_count = 0
        self.tool_count = 0
        self.total_time = 0
        self.errors = 0

    async def before_agent_callback(self, *, agent, callback_context):
        self.agent_count += 1

    async def after_tool_callback(self, *, callback_context, tool_result):
        self.tool_count += 1

    def get_summary(self):
        return {
            "total_agent_calls": self.agent_count,
            "total_tool_calls": self.tool_count,
            "average_tools_per_agent": self.tool_count / self.agent_count
        }
```

---

## Logging Configuration

### Declarative: What Logging Configuration Does

Logging configuration determines:
- **Where** logs are written (file, console, remote service)
- **What level** of detail is captured (DEBUG, INFO, ERROR)
- **How** logs are formatted (timestamp, component, message)
- **What** gets logged (specific modules, severity levels)

### Conditional: When to Configure Logging Differently

| Scenario | Log Level | Destination | Why |
|----------|-----------|-------------|-----|
| **Development** | DEBUG | Local file + console | Maximum detail for debugging |
| **Testing** | INFO | Local file | Enough detail to verify behavior |
| **Production** | WARNING | Remote logging service | Only important issues, centralized monitoring |
| **Troubleshooting** | DEBUG | Temporary file | Deep investigation of specific issues |

### Procedural: How to Configure for Different Scenarios

#### Development Configuration

```python
import logging

# Maximum verbosity for debugging
logging.basicConfig(
    filename="dev_agent.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

Run with:
```bash
adk web --log_level DEBUG
```

#### Production Configuration

```python
import logging

# Only warnings and errors
logging.basicConfig(
    filename="/var/log/agent/production.log",
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
```

#### Selective Logging (specific modules only)

```python
import logging

# Only debug ADK LLM calls, INFO for everything else
logging.basicConfig(level=logging.INFO)
logging.getLogger('google_adk.models.google_llm').setLevel(logging.DEBUG)
```

---

## Debugging with ADK Web UI

### Declarative: What ADK Web UI Provides

The ADK Web UI is an interactive debugging interface that provides:
- **Live chat interface** to test your agent
- **Events timeline** showing all agent actions
- **Detailed trace visualization** with timing information
- **LLM request/response inspection**
- **Tool call analysis**
- **Evaluation capabilities** (covered in Part B)

### Conditional: When to Use ADK Web UI

Use ADK Web UI when:
- **Developing new agents**: Interactive testing during development
- **Debugging specific issues**: Step-through analysis of failures
- **Understanding agent behavior**: Visual analysis of decision-making
- **Creating test cases**: Save conversations as evaluation cases
- **Not appropriate for**: Production environments, automated testing

### Procedural: Complete Debugging Workflow

#### Step 1: Create Your Agent

```python
# agent.py
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

def count_papers(papers: str):  # BUG: Should be List[str]
    """Counts papers in a list."""
    return len(papers)

root_agent = LlmAgent(
    name="research_agent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Find papers and count them.",
    tools=[count_papers]
)
```

#### Step 2: Launch ADK Web UI

```bash
# From your agent directory
adk web --log_level DEBUG
```

#### Step 3: Test and Observe

1. **Open the web UI** (shown in terminal output)
2. **Select your agent** from the dropdown
3. **Send a test message**: "Find quantum computing papers"
4. **Watch for unexpected behavior**: Count seems too high?

#### Step 4: Investigate with Events Tab

1. **Click "Events" tab** in left sidebar
2. **See chronological event list**:
   - User message received
   - call_llm
   - execute_tool: google_search_agent
   - execute_tool: count_papers
   - final_response

3. **Click "Trace" button** to see timing tree

#### Step 5: Inspect Tool Calls

1. **Find the `execute_tool count_papers` span**
2. **Click to expand details**
3. **Look at the function call**:
   ```json
   {
     "name": "count_papers",
     "args": {
       "papers": "Paper 1\nPaper 2\nPaper 3..."  // String, not list!
     }
   }
   ```

4. **Find the bug**: `papers` is a string, so `len()` returns character count!

#### Step 6: Find Root Cause in LLM Request

1. **Click the `call_llm` span** before the tool call
2. **Examine the function declaration** in the request
3. **Notice the parameter type**: `papers: str` instead of `List[str]`

#### Step 7: Fix and Verify

```python
# Fixed agent.py
from typing import List

def count_papers(papers: List[str]):  # FIXED: Now List[str]
    """Counts papers in a list."""
    return len(papers)
```

**Restart and test again** - now it works correctly!

### The Core Debugging Pattern

```
Symptom → Logs → Root Cause → Fix → Verify

Example:
Wrong count → Events tab → String vs List → Fix type → Test passes
```

---

## Plugins and Callbacks

### Declarative: What Plugins Are

**Plugins** are custom code modules that run automatically at various stages of your agent's lifecycle. They provide **hooks** (called callbacks) that let you:
- Monitor agent behavior
- Log custom data
- Modify requests/responses
- Add caching layers
- Implement security checks
- Track performance metrics

**Callbacks** are the individual Python functions inside a Plugin that run at specific lifecycle points.

### Conditional: When to Use Plugins

| Use Case | Why Use a Plugin | Alternative |
|----------|------------------|-------------|
| **Standard observability** | Use built-in `LoggingPlugin` | Manual logging in code |
| **Custom metrics** | Automatic, consistent tracking | Manual instrumentation |
| **Security auditing** | Centralized, can't be bypassed | Scattered checks |
| **Performance monitoring** | Automatic timing of all operations | Manual timing code |
| **Request modification** | Intercept before LLM call | Modify agent code |
| **Caching** | Transparent to agent logic | Change agent implementation |

### Procedural: How to Create and Use Plugins

#### Understanding the Plugin Lifecycle

```
User sends message
    ↓
before_agent_callback ← Plugin runs here
    ↓
Agent processes
    ↓
before_model_callback ← Plugin runs here
    ↓
LLM generates response
    ↓
after_model_callback ← Plugin runs here
    ↓
before_tool_callback ← Plugin runs here (if tool needed)
    ↓
Tool executes
    ↓
after_tool_callback ← Plugin runs here
    ↓
after_agent_callback ← Plugin runs here
    ↓
Response to user
```

#### Available Callback Types

```python
from google.adk.plugins.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    # Runs before agent starts
    async def before_agent_callback(self, *, agent, callback_context):
        pass

    # Runs after agent completes
    async def after_agent_callback(self, *, agent, callback_context):
        pass

    # Runs before LLM call
    async def before_model_callback(self, *, callback_context, llm_request):
        pass

    # Runs after LLM responds
    async def after_model_callback(self, *, callback_context, llm_response):
        pass

    # Runs before tool execution
    async def before_tool_callback(self, *, callback_context, tool_call):
        pass

    # Runs after tool completes
    async def after_tool_callback(self, *, callback_context, tool_result):
        pass

    # Runs on LLM errors
    async def on_model_error_callback(self, *, callback_context, error):
        pass
```

#### Example: Invocation Counter Plugin

**Declarative**: Counts how many times agents, tools, and LLMs are called.

**When to use**: Tracking usage patterns, billing, performance analysis.

**How to implement**:

```python
import logging
from google.adk.plugins.base_plugin import BasePlugin

class CountInvocationPlugin(BasePlugin):
    """Counts agent and tool invocations."""

    def __init__(self):
        super().__init__(name="count_invocation")
        self.agent_count = 0
        self.tool_count = 0
        self.llm_request_count = 0

    async def before_agent_callback(self, *, agent, callback_context):
        """Count agent runs."""
        self.agent_count += 1
        logging.info(f"[Plugin] Agent run count: {self.agent_count}")

    async def before_model_callback(self, *, callback_context, llm_request):
        """Count LLM requests."""
        self.llm_request_count += 1
        logging.info(f"[Plugin] LLM request count: {self.llm_request_count}")

    async def before_tool_callback(self, *, callback_context, tool_call):
        """Count tool calls."""
        self.tool_count += 1
        logging.info(f"[Plugin] Tool call count: {self.tool_count}")

    def get_summary(self):
        """Get usage statistics."""
        return {
            "agents": self.agent_count,
            "llm_calls": self.llm_request_count,
            "tools": self.tool_count
        }
```

**How to use it**:

```python
from google.adk.runners import InMemoryRunner

# Create plugin instance
counter_plugin = CountInvocationPlugin()

# Register with runner
runner = InMemoryRunner(
    agent=my_agent,
    plugins=[counter_plugin]  # Applied to ALL agents automatically
)

# Run agent
await runner.run_debug("Find papers on AI")

# Get statistics
stats = counter_plugin.get_summary()
print(f"Stats: {stats}")
# Output: Stats: {'agents': 2, 'llm_calls': 3, 'tools': 2}
```

#### Example: Performance Timing Plugin

**Declarative**: Measures how long each agent and tool takes to execute.

**When to use**: Performance optimization, SLA monitoring, bottleneck identification.

**How to implement**:

```python
import time
from google.adk.plugins.base_plugin import BasePlugin

class PerformancePlugin(BasePlugin):
    """Tracks execution time for agents and tools."""

    def __init__(self):
        super().__init__(name="performance")
        self.timings = {}
        self._start_times = {}

    async def before_agent_callback(self, *, agent, callback_context):
        """Record start time."""
        key = f"agent_{agent.name}"
        self._start_times[key] = time.time()

    async def after_agent_callback(self, *, agent, callback_context):
        """Calculate and store duration."""
        key = f"agent_{agent.name}"
        if key in self._start_times:
            duration = time.time() - self._start_times[key]
            self.timings[key] = duration
            logging.info(f"[Performance] {key} took {duration:.2f}s")

    async def before_tool_callback(self, *, callback_context, tool_call):
        """Record tool start time."""
        key = f"tool_{tool_call.name}"
        self._start_times[key] = time.time()

    async def after_tool_callback(self, *, callback_context, tool_result):
        """Calculate and store tool duration."""
        tool_name = callback_context.get("tool_name")
        key = f"tool_{tool_name}"
        if key in self._start_times:
            duration = time.time() - self._start_times[key]
            self.timings[key] = duration
            logging.info(f"[Performance] {key} took {duration:.2f}s")

    def get_slowest_operations(self, top_n=5):
        """Get the slowest operations."""
        sorted_timings = sorted(
            self.timings.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_timings[:top_n]
```

**How to use it**:

```python
perf_plugin = PerformancePlugin()

runner = InMemoryRunner(
    agent=my_agent,
    plugins=[perf_plugin]
)

await runner.run_debug("Complex query")

# Find bottlenecks
slowest = perf_plugin.get_slowest_operations(3)
print("Slowest operations:")
for name, duration in slowest:
    print(f"  {name}: {duration:.2f}s")
```

---

## Production Logging

### Declarative: What Production Logging Means

In production, you need observability that:
- **Doesn't require manual interaction** (no Web UI)
- **Runs automatically** for every agent execution
- **Captures standard metrics** without custom code
- **Integrates with existing monitoring** systems
- **Doesn't impact performance** significantly

### Conditional: When Different Approaches Apply

| Scenario | Solution | Why |
|----------|----------|-----|
| **Standard observability needs** | `LoggingPlugin` | Built-in, comprehensive, zero-config |
| **Custom business metrics** | Custom Plugin | Track domain-specific KPIs |
| **Third-party monitoring** | Integration Plugin | Send to Datadog, CloudWatch, etc. |
| **Compliance/audit requirements** | Custom callback | Capture specific regulated events |
| **Development debugging** | `adk web --log_level DEBUG` | Interactive, detailed |

### Procedural: How to Implement Production Logging

#### Option 1: Built-in LoggingPlugin (Recommended)

**What it captures automatically**:
- User messages and agent responses
- Timing data for performance analysis
- LLM requests and responses
- Tool calls and results
- Complete execution traces

**How to use it**:

```python
from google.adk.runners import InMemoryRunner
from google.adk.plugins.logging_plugin import LoggingPlugin

# Configure logging output
import logging
logging.basicConfig(
    filename="/var/log/agent/production.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Add LoggingPlugin to runner
runner = InMemoryRunner(
    agent=my_agent,
    plugins=[LoggingPlugin()]  # That's it!
)

# All agent executions now logged automatically
response = await runner.run_debug("User query")
```

**What gets logged**:

```
2025-01-15 10:23:45 - google_adk.agents - INFO - Agent 'research_agent' started
2025-01-15 10:23:45 - google_adk.models - INFO - LLM request sent
2025-01-15 10:23:47 - google_adk.tools - INFO - Tool 'google_search' executed
2025-01-15 10:23:48 - google_adk.agents - INFO - Agent completed (duration: 3.2s)
```

#### Option 2: Custom Plugin for Business Metrics

**When to use**: You need domain-specific tracking beyond standard observability.

```python
from google.adk.plugins.base_plugin import BasePlugin
import logging

class BusinessMetricsPlugin(BasePlugin):
    """Tracks business-specific KPIs."""

    def __init__(self, metrics_backend):
        super().__init__(name="business_metrics")
        self.backend = metrics_backend  # Your metrics system

    async def after_agent_callback(self, *, agent, callback_context):
        """Log business metrics after each agent run."""

        # Extract relevant data
        user_query = callback_context.get("user_message")
        response = callback_context.get("final_response")

        # Track custom metrics
        self.backend.increment("agent.requests.total")
        self.backend.increment(f"agent.requests.{agent.name}")

        # Track business-specific events
        if "purchase" in user_query.lower():
            self.backend.increment("business.purchase_intent")

        if response and len(response) > 0:
            self.backend.increment("agent.successful_responses")
        else:
            self.backend.increment("agent.empty_responses")

    async def on_model_error_callback(self, *, callback_context, error):
        """Track errors for alerting."""
        self.backend.increment("agent.errors.total")
        self.backend.increment(f"agent.errors.{type(error).__name__}")
        logging.error(f"Agent error: {error}")
```

#### Option 3: Integration with External Monitoring

**When to use**: You want centralized monitoring across all services.

```python
import datadog
from google.adk.plugins.base_plugin import BasePlugin

class DatadogPlugin(BasePlugin):
    """Sends agent metrics to Datadog."""

    def __init__(self):
        super().__init__(name="datadog")
        datadog.initialize()

    async def after_agent_callback(self, *, agent, callback_context):
        """Send metrics to Datadog."""
        duration = callback_context.get("duration", 0)

        # Send timing metric
        datadog.statsd.histogram(
            'agent.execution.duration',
            duration,
            tags=[f"agent:{agent.name}"]
        )

        # Send success/failure
        success = callback_context.get("success", False)
        datadog.statsd.increment(
            'agent.execution.count',
            tags=[
                f"agent:{agent.name}",
                f"status:{'success' if success else 'failure'}"
            ]
        )
```

### Complete Production Setup Example

```python
# production_agent.py
import logging
from google.adk.runners import InMemoryRunner
from google.adk.plugins.logging_plugin import LoggingPlugin
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

# Configure production logging
logging.basicConfig(
    filename="/var/log/agent/production.log",
    level=logging.WARNING,  # Only warnings and errors
    format="%(asctime)s - %(levelname)s - %(message)s",
    # Optionally add rotation
    # handlers=[RotatingFileHandler('agent.log', maxBytes=10MB, backupCount=5)]
)

# Define agent
my_agent = LlmAgent(
    name="production_agent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Help users with their queries.",
    tools=[...]
)

# Create runner with LoggingPlugin
runner = InMemoryRunner(
    agent=my_agent,
    plugins=[
        LoggingPlugin(),  # Standard observability
        # Add custom plugins as needed
    ]
)

# Use in your application
async def handle_user_request(user_query: str):
    """Process user request with full observability."""
    try:
        response = await runner.run_debug(user_query)
        return response
    except Exception as e:
        logging.error(f"Agent execution failed: {e}")
        raise
```

### Decision Tree: Which Logging Approach?

```
Are you in development?
├─ Yes → Use `adk web --log_level DEBUG`
│         Interactive debugging, maximum detail
│
└─ No → Are you in production?
    └─ Yes → Do you need custom metrics?
        ├─ No → Use LoggingPlugin()
        │         Standard observability, zero config
        │
        └─ Yes → Do you need third-party integration?
            ├─ No → Create custom Plugin with business logic
            │
            └─ Yes → Create integration Plugin (Datadog, etc.)
```

---

# Part B: Agent Evaluation

## What is Agent Evaluation?

### Declarative: What It Is

**Agent Evaluation** is the systematic process of testing and measuring how well an AI agent performs across different scenarios and quality dimensions. Unlike traditional testing, evaluation:
- Tests the **entire decision-making process**, not just outputs
- Measures **quality** of responses, not just correctness
- Tracks the **path taken** (trajectory), not just the destination
- Handles **non-deterministic** behavior
- Identifies **regressions** over time

### The Problem with Traditional Testing

**Traditional Software Testing**:
```python
def test_add():
    assert add(2, 3) == 5  # Deterministic, always same result
```

**AI Agent Reality**:
```python
User: "Turn on the lights"
Agent: "I've turned on the living room lights" ✓
      OR "Lights activated" ✓
      OR "Done! Your lights are on" ✓
      OR "I cannot control lights" ✗
```

Agents are **non-deterministic** - same input can produce different (but valid) outputs.

### Conditional: When to Use Evaluation vs Testing

| Scenario | Use Evaluation | Use Traditional Testing |
|----------|---------------|------------------------|
| **Non-deterministic LLM outputs** | ✓ | ✗ |
| **Quality assessment** (helpfulness, tone) | ✓ | ✗ |
| **Tool usage correctness** | ✓ | Limited |
| **Deterministic functions** | ✗ | ✓ |
| **Unit testing tools** | ✗ | ✓ |
| **Regression detection** | ✓ | ✗ |
| **Continuous integration** | ✓ | ✓ |

### Procedural: The Evaluation Process

**Four-step evaluation process**:

```
1. Create Evaluation Configuration
   ↓ (Define what "good" looks like)

2. Create Test Cases
   ↓ (Sample scenarios to test)

3. Run Agent with Test Queries
   ↓ (Execute tests)

4. Compare Results
   ↓ (Measure against expectations)

   Pass/Fail + Detailed Analysis
```

---

## Interactive Evaluation with ADK Web UI

### Declarative: What Interactive Evaluation Provides

Interactive evaluation in ADK Web UI allows you to:
- **Create test cases** from real conversations
- **Run evaluations** immediately
- **See detailed results** with side-by-side comparisons
- **Iterate quickly** on agent improvements
- **Build evaluation sets** incrementally

### Conditional: When to Use Interactive Evaluation

Use interactive evaluation when:
- **Developing new agents**: Create test cases as you build
- **Exploring edge cases**: Discover failure modes through conversation
- **Quick validation**: Test fixes immediately
- **Building test suites**: Incrementally add cases
- **Not for**: Automated CI/CD, batch testing, production monitoring

### Procedural: Complete Interactive Evaluation Workflow

#### Step 1: Create Your Agent

```python
# agent.py
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

def set_device_status(location: str, device_id: str, status: str) -> dict:
    """Sets the status of a smart home device."""
    return {
        "success": True,
        "message": f"Set {device_id} in {location} to {status}"
    }

root_agent = LlmAgent(
    name="home_automation_agent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Control smart devices in the home.",
    tools=[set_device_status]
)
```

#### Step 2: Launch ADK Web UI

```bash
adk create home_automation_agent --model gemini-2.5-flash-lite
# Edit agent.py with above code
adk web
```

#### Step 3: Have a "Perfect" Conversation

**In the Web UI**:

1. **Select your agent** from dropdown
2. **Type**: "Turn on the desk lamp in the office"
3. **Agent responds correctly**: "Set desk lamp in office to ON"

This is your **baseline** - the expected behavior.

#### Step 4: Save as Evaluation Case

**In the Eval tab (right panel)**:

1. Click **"Create Evaluation set"**
2. Name it: `home_automation_tests`
3. Click the ">" arrow next to the set name
4. Click **"Add current session"**
5. Name the case: `basic_device_control`

**What gets saved**:
```json
{
  "user_message": "Turn on the desk lamp in the office",
  "expected_response": "Set desk lamp in office to ON",
  "expected_tools": [
    {
      "name": "set_device_status",
      "args": {
        "location": "office",
        "device_id": "desk lamp",
        "status": "ON"
      }
    }
  ]
}
```

#### Step 5: Run Your First Evaluation

**In the Eval tab**:

1. **Check** your test case
2. Click **"Run Evaluation"**
3. In the dialog, leave defaults:
   - Response Match Score threshold: 0.8
   - Tool Trajectory Score threshold: 1.0
4. Click **"Start"**

**Result**: Green "Pass" ✓

**What happened**:
- Agent ran with same user message
- Response compared to expected response
- Tool calls compared to expected tools
- Both scores above thresholds = Pass

#### Step 6: Create a Challenging Test Case

**Start a new conversation**:

1. Type: "Turn off the lights in the garage"
2. **Agent might respond**: "Set lights in garage to OFF"

**Problem**: Your smart home doesn't have a garage!

**Save this as a test case**:
1. Add to `home_automation_tests`
2. Name: `invalid_location_test`

**Edit the expected response**:
1. Click **Edit** (pencil icon)
2. Change expected response to: "I don't have access to devices in the garage"
3. Save

**Run evaluation again**:
- Agent says: "Set lights in garage to OFF"
- Expected: "I don't have access to devices in the garage"
- Result: **Fail** ✗

#### Step 7: Analyze the Failure

**Hover over the "Fail" label**:

```
Actual Output:
"Set lights in garage to OFF"

Expected Output:
"I don't have access to devices in the garage"

Response Match Score: 0.12 / 0.80 (FAIL)
Tool Trajectory Score: 1.0 / 1.0 (PASS)
```

**Interpretation**:
- **Tool usage was correct** (it called the right function)
- **Response quality failed** (didn't acknowledge the limitation)
- **Root cause**: Agent instruction doesn't specify valid locations

#### Step 8: Fix and Re-evaluate

**Update agent instruction**:

```python
root_agent = LlmAgent(
    name="home_automation_agent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="""Control smart devices in the home.

    Valid locations: living room, bedroom, kitchen, office

    If asked about invalid locations, politely explain you don't
    have access to devices there.""",
    tools=[set_device_status]
)
```

**Restart `adk web` and run evaluation**:
- Now agent responds appropriately
- Result: **Pass** ✓

---

## Understanding Evaluation Metrics

### Declarative: What Evaluation Metrics Are

Evaluation metrics quantify how well your agent performs. ADK provides two primary metrics:

#### 1. Response Match Score

**What it measures**: How similar the agent's actual response is to the expected response.

**Range**: 0.0 (completely different) to 1.0 (perfect match)

**How it works**: Uses text similarity algorithms to compare content, not exact string matching.

#### 2. Tool Trajectory Score

**What it measures**: Whether the agent used the correct tools with correct parameters in the correct sequence.

**Range**: 0.0 (wrong tools/parameters) to 1.0 (perfect tool usage)

**How it works**: Compares the actual sequence of tool calls against expected behavior.

### Conditional: When Each Metric Matters

| Scenario | Response Match Important? | Tool Trajectory Important? |
|----------|--------------------------|---------------------------|
| **Conversational assistant** | High (user experience) | Medium |
| **Automation agent** | Medium | High (correctness) |
| **API agent** | Low | High (functional correctness) |
| **Customer support** | High (tone, clarity) | Medium |
| **Data processing** | Low | High (right operations) |

### Procedural: How to Set Appropriate Thresholds

#### Understanding Threshold Values

```
Score: 1.0 = Perfect match (very strict)
Score: 0.9 = Nearly identical (strict)
Score: 0.8 = Very similar (balanced)
Score: 0.7 = Similar (lenient)
Score: 0.6 = Somewhat similar (very lenient)
```

#### Setting Response Match Thresholds

**Strict (0.9-1.0)**: Use when response must be nearly identical
```
Expected: "The temperature is 72°F"
Actual:   "The temperature is 72 degrees Fahrenheit"
Score:    0.92 ✓ (Pass with 0.9 threshold)
```

**Balanced (0.7-0.8)**: Use when semantic similarity matters more than exact wording
```
Expected: "I've turned on the lights"
Actual:   "The lights are now on"
Score:    0.78 ✓ (Pass with 0.7 threshold)
```

**Lenient (0.5-0.6)**: Use when general topic match is sufficient
```
Expected: "The weather is sunny and warm"
Actual:   "It's a nice day with clear skies"
Score:    0.58 ✓ (Pass with 0.5 threshold)
```

#### Setting Tool Trajectory Thresholds

**Always 1.0 (strict)**: Tool calls must be exact
```json
Expected: {"name": "set_device", "args": {"device": "light", "status": "ON"}}
Actual:   {"name": "set_device", "args": {"device": "light", "status": "ON"}}
Score:    1.0 ✓
```

**Why strict?**: Wrong tool calls cause incorrect actions, not just poor communication.

#### Example Configuration

```json
{
  "criteria": {
    "response_match_score": 0.8,
    "tool_trajectory_avg_score": 1.0
  }
}
```

**Interpretation**:
- Responses can vary in wording (0.8 allows flexibility)
- Tool usage must be perfect (1.0 requires exactness)

---

## Systematic Evaluation

### Declarative: What Systematic Evaluation Is

Systematic evaluation is **automated, batch evaluation** using:
- **Predefined test suites** (`.evalset.json` files)
- **Configuration files** (`test_config.json`)
- **CLI commands** for automation
- **Regression detection** through repeated runs

Unlike interactive evaluation, systematic evaluation:
- Runs without human interaction
- Tests multiple cases at once
- Integrates with CI/CD pipelines
- Tracks performance over time

### Conditional: When to Use Systematic Evaluation

| Use Case | Interactive Eval | Systematic Eval |
|----------|-----------------|-----------------|
| **Development/debugging** | ✓ | ✗ |
| **CI/CD integration** | ✗ | ✓ |
| **Regression testing** | ✗ | ✓ |
| **Batch testing (100+ cases)** | ✗ | ✓ |
| **Automated quality gates** | ✗ | ✓ |
| **Quick iteration** | ✓ | ✗ |
| **Production monitoring** | ✗ | ✓ |

### Procedural: Complete Systematic Evaluation Setup

#### Step 1: Create Evaluation Configuration

**File**: `test_config.json`

**What it does**: Defines pass/fail thresholds for your evaluation.

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.8
  }
}
```

**How to create it**:

```python
import json

eval_config = {
    "criteria": {
        "tool_trajectory_avg_score": 1.0,  # Perfect tool usage required
        "response_match_score": 0.8,       # 80% text similarity
    }
}

with open("home_automation_agent/test_config.json", "w") as f:
    json.dump(eval_config, f, indent=2)
```

#### Step 2: Create Test Cases (Evaluation Set)

**File**: `integration.evalset.json`

**What it contains**: Multiple test cases with expected behaviors.

**Structure**:
```json
{
  "eval_set_id": "unique_identifier",
  "eval_cases": [
    {
      "eval_id": "test_case_name",
      "conversation": [
        {
          "user_content": {"parts": [{"text": "user message"}]},
          "final_response": {"parts": [{"text": "expected response"}]},
          "intermediate_data": {
            "tool_uses": [
              {"name": "tool_name", "args": {...}}
            ]
          }
        }
      ]
    }
  ]
}
```

**How to create it** (Method 1: Programmatically):

```python
test_cases = {
    "eval_set_id": "home_automation_integration_suite",
    "eval_cases": [
        # Test Case 1: Basic device control
        {
            "eval_id": "living_room_light_on",
            "conversation": [
                {
                    "user_content": {
                        "parts": [{"text": "Turn on the floor lamp in the living room"}]
                    },
                    "final_response": {
                        "parts": [{"text": "Set floor lamp in living room to on"}]
                    },
                    "intermediate_data": {
                        "tool_uses": [
                            {
                                "name": "set_device_status",
                                "args": {
                                    "location": "living room",
                                    "device_id": "floor lamp",
                                    "status": "ON"
                                }
                            }
                        ]
                    }
                }
            ]
        },

        # Test Case 2: Different location
        {
            "eval_id": "kitchen_light_control",
            "conversation": [
                {
                    "user_content": {
                        "parts": [{"text": "Switch on the main light in the kitchen"}]
                    },
                    "final_response": {
                        "parts": [{"text": "Set main light in kitchen to on"}]
                    },
                    "intermediate_data": {
                        "tool_uses": [
                            {
                                "name": "set_device_status",
                                "args": {
                                    "location": "kitchen",
                                    "device_id": "main light",
                                    "status": "ON"
                                }
                            }
                        ]
                    }
                }
            ]
        },

        # Test Case 3: Invalid location (should fail gracefully)
        {
            "eval_id": "invalid_location_garage",
            "conversation": [
                {
                    "user_content": {
                        "parts": [{"text": "Turn off the TV in the garage"}]
                    },
                    "final_response": {
                        "parts": [{
                            "text": "I don't have access to devices in the garage"
                        }]
                    },
                    "intermediate_data": {
                        "tool_uses": []  # Should NOT call any tools
                    }
                }
            ]
        }
    ]
}

# Write to file
with open("home_automation_agent/integration.evalset.json", "w") as f:
    json.dump(test_cases, f, indent=2)
```

**How to create it** (Method 2: From ADK Web UI):

1. Create conversations in Web UI
2. Add to evaluation set
3. The set is automatically saved to `<eval_set_name>.evalset.json`

#### Step 3: Run Evaluation via CLI

**Command**:
```bash
adk eval <agent_directory> <evalset_file> --config_file_path=<config_file> --print_detailed_results
```

**Example**:
```bash
adk eval home_automation_agent \
  home_automation_agent/integration.evalset.json \
  --config_file_path=home_automation_agent/test_config.json \
  --print_detailed_results
```

**What happens**:
1. ADK loads your agent
2. Runs each test case from the evalset
3. Compares results against expected values
4. Calculates scores
5. Prints summary and details

#### Step 4: Analyze Results

**Sample Output**:
```
Running evaluation set: home_automation_integration_suite

Test Case: living_room_light_on
  ✓ response_match_score: 0.95 / 0.80 (PASS)
  ✓ tool_trajectory_avg_score: 1.0 / 1.0 (PASS)
  Status: PASS

Test Case: kitchen_light_control
  ✓ response_match_score: 0.88 / 0.80 (PASS)
  ✓ tool_trajectory_avg_score: 1.0 / 1.0 (PASS)
  Status: PASS

Test Case: invalid_location_garage
  ✗ response_match_score: 0.45 / 0.80 (FAIL)
  ✓ tool_trajectory_avg_score: 1.0 / 1.0 (PASS)
  Status: FAIL

Summary:
  Total: 3
  Passed: 2
  Failed: 1
  Success Rate: 66.7%
```

**How to interpret**:

**Case 1: PASS** ✓
- Both scores above thresholds
- Agent behaved as expected
- No action needed

**Case 2: PASS** ✓
- Both scores above thresholds
- Slight variation in wording (0.88 vs 1.0) but acceptable
- No action needed

**Case 3: FAIL** ✗
- Response quality too low (0.45 < 0.80)
- Tool usage correct (didn't call tools as expected)
- **Action needed**: Agent's response communication needs improvement

**Detailed analysis with `--print_detailed_results`**:

```
Test Case: invalid_location_garage (FAIL)

Expected Response:
  "I don't have access to devices in the garage"

Actual Response:
  "I cannot help with that request"

Diff:
  - I don't have access to devices in the garage
  + I cannot help with that request

Analysis:
  • Tool usage: Correct (no tools called)
  • Communication: Too generic, lacks specificity
  • Fix: Update instruction to give location-specific errors
```

#### Step 5: Fix Issues and Re-run

**Update agent**:
```python
instruction="""Control smart devices in the home.

Valid locations: living room, bedroom, kitchen, office

If asked about invalid locations, respond with:
"I don't have access to devices in [location]"
"""
```

**Re-run evaluation**:
```bash
adk eval home_automation_agent \
  home_automation_agent/integration.evalset.json \
  --config_file_path=home_automation_agent/test_config.json
```

**New result**:
```
Summary:
  Total: 3
  Passed: 3
  Failed: 0
  Success Rate: 100%
```

#### Step 6: Integrate with CI/CD

**GitHub Actions Example**:

```yaml
# .github/workflows/agent-evaluation.yml
name: Agent Evaluation

on: [push, pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install google-adk

      - name: Run agent evaluation
        env:
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
        run: |
          adk eval home_automation_agent \
            home_automation_agent/integration.evalset.json \
            --config_file_path=home_automation_agent/test_config.json

      - name: Check results
        run: |
          if grep -q "Failed: 0" evaluation_results.txt; then
            echo "All tests passed!"
            exit 0
          else
            echo "Some tests failed!"
            exit 1
          fi
```

**What this does**:
- Runs evaluation on every commit
- Blocks merges if tests fail
- Ensures no regressions

---

## User Simulation (Advanced)

### Declarative: What User Simulation Is

**User Simulation** uses a generative AI model to **dynamically generate user prompts** during evaluation, instead of using fixed test cases.

**Key difference**:

**Traditional Evaluation**:
```
Fixed user message → Agent → Compare to fixed expected response
```

**User Simulation**:
```
Conversation goal → Simulated user (LLM) ↔ Agent → Evaluate goal achievement
```

The simulated user:
- Follows a conversation plan
- Adapts based on agent responses
- Generates realistic, varied prompts
- Tests agent's ability to handle unpredictability

### Conditional: When to Use User Simulation

| Scenario | Use User Simulation | Use Fixed Test Cases |
|----------|-------------------|---------------------|
| **Multi-turn conversations** | ✓ | Limited |
| **Natural dialogue flow** | ✓ | ✗ |
| **Edge case discovery** | ✓ | ✗ |
| **Regression testing** | ✗ | ✓ |
| **Exact reproduction** | ✗ | ✓ |
| **Goal-oriented evaluation** | ✓ | Limited |
| **Unpredictable user behavior** | ✓ | ✗ |

**Use user simulation when**:
- You want to test conversational robustness
- User goals are more important than exact phrasing
- You need to discover unexpected edge cases
- Testing multi-turn dialogue flows

**Use fixed test cases when**:
- You need reproducible tests for CI/CD
- Testing specific known failure modes
- Regression detection is critical
- You want consistent benchmarking

### Procedural: How to Implement User Simulation

#### Step 1: Define a Conversation Scenario

```python
from google.adk.evaluation.conversation_scenario import ConversationScenario

scenario = ConversationScenario(
    goal="Book a flight from San Francisco to New York",
    conversation_plan="""
    1. Ask about available flights
    2. If offered options, choose the cheapest
    3. Provide passenger details when asked
    4. Confirm the booking
    5. Ask for confirmation number
    """,
    user_persona="A budget-conscious traveler who is direct and efficient",
    max_turns=10
)
```

**What each parameter does**:

- **goal**: The overall objective the simulated user is trying to achieve
- **conversation_plan**: Step-by-step guide for the simulated user's strategy
- **user_persona**: Character traits that influence how the user communicates
- **max_turns**: Limit on conversation length to prevent infinite loops

#### Step 2: Create the User Simulation Evaluator

```python
from google.adk.evaluation.user_simulation import UserSimulationEvaluator
from google.adk.models.google_llm import Gemini

evaluator = UserSimulationEvaluator(
    agent=my_agent,
    scenario=scenario,
    user_simulator_model=Gemini(model="gemini-2.5-flash-lite"),
    evaluation_criteria={
        "goal_achieved": "Did the user successfully book the flight?",
        "efficiency": "Was the booking completed in minimal turns?",
        "user_satisfaction": "Was the experience smooth and helpful?"
    }
)
```

#### Step 3: Run the Simulation

```python
result = await evaluator.run()

print(f"Goal Achieved: {result.goal_achieved}")
print(f"Turns Used: {result.turns}")
print(f"Conversation:")
for turn in result.conversation:
    print(f"  User: {turn.user_message}")
    print(f"  Agent: {turn.agent_response}")
```

**Example output**:
```
Goal Achieved: True
Turns Used: 6

Conversation:
  User: What flights do you have from San Francisco to New York?
  Agent: I found 3 flights: $250 (United), $220 (Delta), $200 (Southwest)

  User: I'll take the Southwest flight for $200
  Agent: Great! I need your name and email to complete the booking.

  User: John Smith, john@example.com
  Agent: Booking confirmed! Your confirmation number is SW123456

  User: Perfect, thanks!
  Agent: You're welcome! Have a great flight.
```

#### Step 4: Analyze Simulation Results

```python
# Analyze how natural the conversation was
if result.turns <= 5:
    print("✓ Efficient conversation")
else:
    print("⚠ Conversation took longer than expected")

# Check if agent handled user's persona appropriately
if "cheapest" in result.conversation[1].agent_response.lower():
    print("✓ Agent understood budget-conscious preference")
```

#### Example: Complex User Simulation

```python
from google.adk.evaluation.conversation_scenario import ConversationScenario
from google.adk.evaluation.user_simulation import UserSimulationEvaluator

# Define a challenging scenario
scenario = ConversationScenario(
    goal="Get help with a technical issue without providing much detail initially",
    conversation_plan="""
    1. Start with vague complaint: "It's not working"
    2. Only provide details when specifically asked
    3. Get frustrated if asked too many questions
    4. Expect the agent to be helpful despite limited info
    5. Become satisfied once issue is understood
    """,
    user_persona="""
    Non-technical user who:
    - Doesn't know technical terms
    - Gets frustrated easily
    - Expects quick solutions
    - Appreciates patient explanation
    """,
    max_turns=15
)

# Run simulation
evaluator = UserSimulationEvaluator(
    agent=support_agent,
    scenario=scenario,
    user_simulator_model=Gemini(model="gemini-2.5-flash-lite"),
    evaluation_criteria={
        "problem_diagnosed": "Was the technical issue identified?",
        "user_not_frustrated": "Did the agent maintain user patience?",
        "solution_provided": "Was a clear solution offered?"
    }
)

result = await evaluator.run()

# Analyze results
print(f"\nEvaluation Results:")
print(f"  Problem Diagnosed: {result.criteria['problem_diagnosed']}")
print(f"  User Patience Maintained: {result.criteria['user_not_frustrated']}")
print(f"  Solution Provided: {result.criteria['solution_provided']}")
print(f"  Total Turns: {result.turns}")
```

**What this tests**:
- Agent's ability to handle ambiguity
- Patient information gathering
- Frustration management
- Non-technical communication

---

# Quick Reference Guide

## When to Use What?

### Observability Tools

| Your Need | Solution | Command/Code |
|-----------|----------|--------------|
| **Debug agent failure** | ADK Web UI with DEBUG | `adk web --log_level DEBUG` |
| **See full execution trace** | Events tab in Web UI | Click "Events" → "Trace" |
| **Production logging** | LoggingPlugin | `plugins=[LoggingPlugin()]` |
| **Custom metrics** | Custom Plugin | Create `BasePlugin` subclass |
| **Third-party monitoring** | Integration Plugin | Custom plugin with external API |

### Evaluation Tools

| Your Need | Solution | Command/Code |
|-----------|----------|--------------|
| **Quick test during development** | Interactive Web UI eval | Web UI → Eval tab |
| **Automated regression testing** | CLI evaluation | `adk eval agent/ test.evalset.json` |
| **CI/CD integration** | CLI in pipeline | Add `adk eval` to GitHub Actions |
| **Test natural conversations** | User Simulation | `UserSimulationEvaluator` |
| **Measure response quality** | Response Match Score | Set in `test_config.json` |
| **Verify tool usage** | Tool Trajectory Score | Set in `test_config.json` |

## Common Patterns

### Pattern 1: Development Debugging

```bash
# 1. Run with debug logging
adk web --log_level DEBUG

# 2. Test in UI
# 3. Check Events tab for issues
# 4. Fix code
# 5. Create test case from working conversation
```

### Pattern 2: Production Deployment

```python
# 1. Add LoggingPlugin
from google.adk.plugins.logging_plugin import LoggingPlugin

runner = InMemoryRunner(
    agent=my_agent,
    plugins=[LoggingPlugin()]
)

# 2. Configure production logging
logging.basicConfig(
    filename="/var/log/agent.log",
    level=logging.WARNING
)

# 3. Add monitoring/alerting
```

### Pattern 3: Regression Testing

```bash
# 1. Create evalset from good conversations
# saved as integration.evalset.json

# 2. Create test config
# test_config.json with thresholds

# 3. Run before changes
adk eval agent/ integration.evalset.json --config_file_path=test_config.json

# 4. Make changes to agent

# 5. Run after changes
adk eval agent/ integration.evalset.json --config_file_path=test_config.json

# 6. Compare results
```

### Pattern 4: CI/CD Integration

```yaml
# .github/workflows/test.yml
- name: Run evaluation
  run: adk eval agent/ tests/ --config_file_path=config.json
- name: Check results
  run: |
    if [ $? -eq 0 ]; then
      echo "Tests passed"
    else
      echo "Tests failed"
      exit 1
    fi
```

## Troubleshooting Guide

### "Agent gives wrong answers"

1. **Check logs**: `adk web --log_level DEBUG`
2. **Look at Events tab**: See what tools were called
3. **Inspect LLM request**: Check if instructions are clear
4. **Verify tool definitions**: Ensure parameter types are correct

### "Evaluation always fails"

1. **Check thresholds**: Are they too strict?
2. **Inspect actual vs expected**: Use `--print_detailed_results`
3. **Adjust response_match_score**: Lower if too strict (try 0.7 instead of 0.9)
4. **Verify expected values**: Are they realistic?

### "Agent is slow"

1. **Use Performance Plugin**: Track timing
2. **Check traces**: Identify bottleneck
3. **Optimize slowest operations**
4. **Consider caching**

### "Can't reproduce failure"

1. **Check logs for full context**
2. **Create evaluation case**: Save failing conversation
3. **Use DEBUG logging**: Maximum detail
4. **Check for non-determinism**: Run multiple times

## File Structure Reference

```
my-agent/
├── agent.py                        # Agent definition
├── test_config.json               # Evaluation thresholds
├── integration.evalset.json       # Test cases
├── regression.evalset.json        # Regression tests
└── plugins/
    ├── metrics_plugin.py          # Custom metrics
    └── monitoring_plugin.py       # Custom monitoring
```

## Configuration Templates

### test_config.json

```json
{
  "criteria": {
    "response_match_score": 0.8,
    "tool_trajectory_avg_score": 1.0
  }
}
```

### Basic evalset structure

```json
{
  "eval_set_id": "my_test_suite",
  "eval_cases": [
    {
      "eval_id": "test_case_1",
      "conversation": [
        {
          "user_content": {
            "parts": [{"text": "user message"}]
          },
          "final_response": {
            "parts": [{"text": "expected response"}]
          },
          "intermediate_data": {
            "tool_uses": [
              {
                "name": "tool_name",
                "args": {"param": "value"}
              }
            ]
          }
        }
      ]
    }
  ]
}
```

---

## Summary

### Agent Observability

**What**: Visibility into agent decision-making through logs, traces, and metrics

**When**: Always in development, selectively in production

**How**:
- Development: `adk web --log_level DEBUG`
- Production: `LoggingPlugin()` or custom plugins

### Agent Evaluation

**What**: Systematic testing of agent quality and behavior

**When**:
- Development: Interactive Web UI
- CI/CD: CLI evaluation
- Complex scenarios: User Simulation

**How**:
- Create test cases (`.evalset.json`)
- Define criteria (`test_config.json`)
- Run evaluation (`adk eval`)
- Analyze results and iterate

### Key Principles

1. **Observability is reactive**: Helps debug after problems occur
2. **Evaluation is proactive**: Catches problems before they reach users
3. **Use both**: Observability finds issues, evaluation prevents regressions
4. **Start simple**: Basic logging and test cases first
5. **Add complexity as needed**: Custom plugins and user simulation later

---

**Next Steps**:
- Set up basic logging in your agents
- Create your first evaluation test case
- Integrate evaluation into your development workflow
- Explore advanced features like user simulation as needed
