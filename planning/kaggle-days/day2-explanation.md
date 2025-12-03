# Day 2: Agent Tools - Complete Guide

## Overview

These notebooks teach you how to extend AI agents beyond simple chat responses into powerful systems that can interact with external tools, pause for approvals, and connect to standardized services. You'll learn to build production-ready agents that can perform real-world tasks safely and reliably.

---

## Part 1: Agent Tools Fundamentals

### What Are Agent Tools?

**Agent tools** transform isolated language models into capable agents that can take actions in the real world. Without tools, an agent's knowledge is frozen in time and it cannot:
- Access current information (news, weather, stock prices)
- Perform calculations reliably
- Interact with databases or APIs
- Execute code or commands
- Connect to external systems

Tools bridge this gap by giving agents specific capabilities they can invoke when needed.

---

## Core Concepts

### 1. Custom Function Tools

**What it is:** Any Python function can become an agent tool by following simple conventions.

**How it works:**
- Write a regular Python function with your business logic
- Add clear docstrings (the LLM uses these to understand when to call the tool)
- Use type hints for parameters
- Return structured dictionaries with status indicators
- Add the function to the agent's `tools=[]` list

**Example:**
```python
def get_exchange_rate(base_currency: str, target_currency: str) -> dict:
    """Looks up and returns the exchange rate between two currencies.

    Args:
        base_currency: The ISO 4217 currency code (e.g., "USD")
        target_currency: The ISO 4217 currency code (e.g., "EUR")

    Returns:
        Dictionary with status and rate information.
        Success: {"status": "success", "rate": 0.93}
        Error: {"status": "error", "error_message": "..."}
    """
    rate_database = {
        "usd": {"eur": 0.93, "jpy": 157.50, "inr": 83.58}
    }

    base = base_currency.lower()
    target = target_currency.lower()

    rate = rate_database.get(base, {}).get(target)
    if rate is not None:
        return {"status": "success", "rate": rate}
    else:
        return {
            "status": "error",
            "error_message": f"Unsupported currency pair"
        }
```

**Best Practices:**
1. **Dictionary Returns** - Always return `{"status": "success/error", ...}`
2. **Clear Docstrings** - LLMs read these to decide when to use the tool
3. **Type Hints** - Enable ADK to generate proper schemas
4. **Error Handling** - Return structured errors, not exceptions

**How to use:**
```python
currency_agent = LlmAgent(
    name="currency_agent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="You convert currencies. Use get_exchange_rate() to get rates.",
    tools=[get_exchange_rate]  # Just add your function here!
)
```

---

### 2. Code Execution Tools

**What it is:** A built-in tool that lets agents write and execute Python code in a sandbox.

**Why it matters:** LLMs are unreliable at math. Instead of having the agent calculate "500 * 0.93 - (500 * 0.02)", let it generate Python code and execute it for precise results.

**How it works:**
```python
calculation_agent = LlmAgent(
    name="CalculationAgent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="""Generate Python code to calculate the result.
    Output ONLY the code block. The code must print the final result.""",
    code_executor=BuiltInCodeExecutor()  # Adds code execution capability
)
```

**Workflow:**
1. Agent receives: "Calculate 500 USD to EUR with 2% fee, rate 0.93"
2. Agent generates Python code:
   ```python
   amount = 500
   fee = amount * 0.02
   after_fee = amount - fee
   result = after_fee * 0.93
   print(f"Result: {result}")
   ```
3. Code executor runs it in sandbox
4. Agent receives precise output: "Result: 455.7"

---

### 3. Agent Tools (Using Agents as Tools)

**What it is:** You can use one agent as a tool for another agent, creating specialist delegation.

**Key Difference from Sub-Agents:**
- **Agent Tools:** Agent A calls Agent B, gets result, continues working
- **Sub-Agents:** Agent A transfers control completely to Agent B

**How it works:**
```python
# Create specialist agent
calculation_agent = LlmAgent(
    name="CalculationAgent",
    instruction="Generate Python code for calculations",
    code_executor=BuiltInCodeExecutor()
)

# Use it as a tool in another agent
currency_agent = LlmAgent(
    name="currency_agent",
    instruction="Use calculation_agent to compute final amounts",
    tools=[
        get_fee_for_payment_method,
        get_exchange_rate,
        AgentTool(agent=calculation_agent)  # Specialist as tool!
    ]
)
```

**Workflow:**
1. User asks currency agent to convert money
2. Currency agent calls `get_exchange_rate()` → gets rate
3. Currency agent calls `get_fee_for_payment_method()` → gets fee
4. Currency agent calls `calculation_agent` with: "Calculate 500 - (500*0.02) then multiply by 0.93"
5. Calculation agent generates and runs Python code
6. Currency agent receives result and continues conversation

**Use case:** Delegation for specific tasks while maintaining control

---

### 4. Complete Tool Ecosystem

#### Custom Tools (You Build Them)

| Tool Type | Purpose | Example |
|-----------|---------|---------|
| **Function Tools** | Turn Python functions into tools | `get_exchange_rate`, `query_database` |
| **Long Running Function Tools** | Operations that take time | File processing, human approvals |
| **Agent Tools** | Use specialist agents | Calculation agent, validation agent |
| **MCP Tools** | Connect to MCP servers | Filesystem, databases, APIs |
| **OpenAPI Tools** | Auto-generate from API specs | REST endpoints become tools |

#### Built-in Tools (Ready to Use)

| Tool Type | Purpose | Example |
|-----------|---------|---------|
| **Gemini Tools** | Leverage Gemini capabilities | `google_search`, `BuiltInCodeExecutor` |
| **Google Cloud Tools** | Enterprise integration | `BigQueryToolset`, `SpannerToolset` |
| **Third-party Tools** | Existing ecosystems | Hugging Face, GitHub, Firecrawl |

---

## Part 2: Advanced Tool Patterns

### 5. Model Context Protocol (MCP)

**What it is:** An open standard that lets agents connect to external services without writing custom integration code.

**The Problem:** Every API is different. Connecting to GitHub requires GitHub-specific code, databases need database-specific code, etc.

**The Solution:** MCP provides a standardized interface. All MCP servers work the same way, regardless of what service they connect to.

**Architecture:**
```
Your Agent (MCP Client)
        ↓
   MCP Protocol
        ↓
   ┌────┴────┬────────┬────────┐
   ↓         ↓        ↓        ↓
GitHub    Slack    Maps    Database
Server    Server   Server  Server
```

**How it works:**

**Step 1: Choose an MCP Server**
Find servers at [modelcontextprotocol.io/examples](https://modelcontextprotocol.io/examples)

**Step 2: Create the Toolset**
```python
mcp_image_server = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",  # Run MCP server via npx
            args=["-y", "@modelcontextprotocol/server-everything"],
            tool_filter=["getTinyImage"]  # Only use specific tools
        ),
        timeout=30
    )
)
```

**Step 3: Add to Agent**
```python
image_agent = LlmAgent(
    name="image_agent",
    instruction="Use the MCP Tool to generate images",
    tools=[mcp_image_server]  # Just add it like any other tool
)
```

**Behind the Scenes:**
1. ADK launches the MCP server: `npx -y @modelcontextprotocol/server-everything`
2. Server announces: "I provide getTinyImage functionality"
3. Agent can now call `getTinyImage()` as if it were a local function
4. ADK handles all communication automatically

**Real-World Examples:**

**Kaggle MCP Server:**
```python
McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=['-y', 'mcp-remote', 'https://www.kaggle.com/mcp']
        )
    )
)
# Provides: Dataset search/download, notebook access, competition queries
```

**GitHub MCP Server:**
```python
McpToolset(
    connection_params=StreamableHTTPServerParams(
        url="https://api.githubcopilot.com/mcp/",
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "X-MCP-Toolsets": "all"
        }
    )
)
# Provides: PR/issue analysis, repository queries
```

---

### 6. Long-Running Operations (LRO)

**What it is:** Tools that need to pause execution to wait for external input, typically human approval.

**The Problem:** Most tools execute immediately:
```
User asks → Agent calls tool → Tool returns → Agent responds
```

But what if you need approval before completing an action?
```
User asks → Agent calls tool → Tool PAUSES → Human approves → Tool completes → Agent responds
```

**When to Use:**
- 💰 Financial transactions requiring approval
- 🗑️ Bulk operations (delete 1000 records)
- 📋 Compliance checkpoints
- 💸 High-cost actions (spin up 50 servers)
- ⚠️ Irreversible operations (delete account)

**How it works:**

#### The Tool with Three Scenarios

```python
LARGE_ORDER_THRESHOLD = 5

def place_shipping_order(
    num_containers: int,
    destination: str,
    tool_context: ToolContext  # ADK provides this automatically
) -> dict:
    """Places a shipping order. Requires approval if >5 containers."""

    # SCENARIO 1: Small orders auto-approve
    if num_containers <= LARGE_ORDER_THRESHOLD:
        return {
            "status": "approved",
            "order_id": f"ORD-{num_containers}-AUTO",
            "message": "Order auto-approved"
        }

    # SCENARIO 2: First call for large order - REQUEST PAUSE
    if not tool_context.tool_confirmation:
        tool_context.request_confirmation(
            hint=f"⚠️ Large order: {num_containers} containers to {destination}",
            payload={"num_containers": num_containers, "destination": destination}
        )
        return {
            "status": "pending",
            "message": "Order requires approval"
        }

    # SCENARIO 3: Resumed after approval - HANDLE DECISION
    if tool_context.tool_confirmation.confirmed:
        return {
            "status": "approved",
            "order_id": f"ORD-{num_containers}-HUMAN",
            "message": "Order approved"
        }
    else:
        return {
            "status": "rejected",
            "message": "Order rejected"
        }
```

#### Making it Resumable

**Create Resumable App:**
```python
# Regular agent won't remember state between calls
shipping_agent = LlmAgent(
    name="shipping_agent",
    instruction="Process shipping orders using place_shipping_order tool",
    tools=[FunctionTool(func=place_shipping_order)]
)

# Wrap in App with resumability - THIS IS KEY!
shipping_app = App(
    name="shipping_coordinator",
    root_agent=shipping_agent,
    resumability_config=ResumabilityConfig(is_resumable=True)
)

# Create runner with the app
shipping_runner = Runner(
    app=shipping_app,  # Pass app, not agent
    session_service=InMemorySessionService()
)
```

**What Gets Saved When Paused:**
- All conversation messages
- Which tool was called (`place_shipping_order`)
- Tool parameters (10 containers, Rotterdam)
- Exact pause point (waiting for approval)

#### The Workflow Pattern

**Key Technical Concepts:**

- **Events:** ADK creates events as the agent executes (tool calls, responses, etc.)
- **`adk_request_confirmation` event:** Special event created when a tool calls `request_confirmation()`
- **`invocation_id`:** Unique ID for each execution - used to resume the correct paused execution

**Complete Workflow:**
```python
async def run_shipping_workflow(query: str, auto_approve: bool = True):
    # STEP 1: Send initial request
    events = []
    async for event in shipping_runner.run_async(
        user_id="test_user",
        session_id=session_id,
        new_message=query_content
    ):
        events.append(event)

    # STEP 2: Check if agent paused for approval
    approval_info = check_for_approval(events)  # Looks for adk_request_confirmation

    # STEP 3: Handle approval if needed
    if approval_info:
        # Tool paused - get human decision
        human_decision = True  # or False

        # Resume with approval decision
        async for event in shipping_runner.run_async(
            user_id="test_user",
            session_id=session_id,
            new_message=create_approval_response(approval_info, human_decision),
            invocation_id=approval_info["invocation_id"]  # CRITICAL: Resume same execution
        ):
            print_response(event)
    else:
        # No approval needed - already completed
        print_agent_response(events)
```

**Helper Functions:**

```python
def check_for_approval(events):
    """Detect if agent paused for approval."""
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if (part.function_call and
                    part.function_call.name == "adk_request_confirmation"):
                    return {
                        "approval_id": part.function_call.id,
                        "invocation_id": event.invocation_id
                    }
    return None

def create_approval_response(approval_info, approved):
    """Format human decision for ADK."""
    confirmation_response = types.FunctionResponse(
        id=approval_info["approval_id"],
        name="adk_request_confirmation",
        response={"confirmed": approved}
    )
    return types.Content(
        role="user",
        parts=[types.Part(function_response=confirmation_response)]
    )
```

#### Complete Execution Timeline

```
TIME 1: User: "Ship 10 containers to Rotterdam"
TIME 2: Workflow calls shipping_runner.run_async(...)
        ADK assigns invocation_id = "abc123"
TIME 3: Agent decides to use place_shipping_order
TIME 4: ADK calls place_shipping_order(10, "Rotterdam", tool_context)
TIME 5: Tool checks: 10 > 5, calls request_confirmation()
TIME 6: Tool returns {'status': 'pending'}
TIME 7: ADK creates adk_request_confirmation event with invocation_id="abc123"
TIME 8: Workflow detects event, saves invocation_id="abc123"
TIME 9: Workflow gets human decision → True
TIME 10: Workflow calls run_async(..., invocation_id="abc123")
TIME 11: ADK sees "abc123" → RESUMES (not restart)
TIME 12: ADK calls place_shipping_order again
         Now tool_context.tool_confirmation.confirmed = True
TIME 13: Tool returns {'status': 'approved', 'order_id': 'ORD-10-HUMAN'}
TIME 14: Agent responds to user with approval confirmation
```

**Key Point:** The `invocation_id` tells ADK to resume the paused execution instead of starting a new one.

---

## Practical Usage Guide

### Getting Started with Function Tools

1. **Write your function** with clear docstrings and type hints
2. **Return structured dictionaries** with status indicators
3. **Add to agent's tools list**
4. **Test with simple queries**

### Adding Code Execution

1. **Create specialist agent** with `BuiltInCodeExecutor()`
2. **Use as AgentTool** in your main agent
3. **Instruct agent when to delegate** calculations

### Connecting to MCP Servers

1. **Find an MCP server** at modelcontextprotocol.io
2. **Create McpToolset** with connection parameters
3. **Add to agent's tools** like any other tool
4. **Test the integration**

### Implementing Approvals

1. **Identify operations** that need human oversight
2. **Add `tool_context: ToolContext`** parameter to function
3. **Call `request_confirmation()`** when approval needed
4. **Wrap agent in resumable App**
5. **Build workflow** to detect pauses and resume
6. **Test both approval** and rejection paths

---

## Common Patterns

### Multi-Tool Agent
```python
agent = LlmAgent(
    name="smart_agent",
    tools=[
        function_tool_1,           # Custom function
        function_tool_2,           # Another custom function
        AgentTool(specialist),     # Specialist agent
        mcp_toolset,               # MCP integration
    ]
)
```

### Calculation Delegation
```python
main_agent = LlmAgent(
    instruction="""
    1. Gather data using tools
    2. Use calculation_agent to compute results
    3. Present findings
    """,
    tools=[data_tool_1, data_tool_2, AgentTool(calculation_agent)]
)
```

### Approval Workflow
```python
# 1. Create tool with approval logic
# 2. Wrap in resumable app
app = App(
    root_agent=agent,
    resumability_config=ResumabilityConfig(is_resumable=True)
)
# 3. Build workflow to detect/handle pauses
# 4. Resume with same invocation_id
```

---

## Key Takeaways

### Production-Ready Patterns

| Pattern | When to Use | Key Components |
|---------|-------------|----------------|
| **Function Tools** | Custom business logic | Python functions, type hints, docstrings |
| **Code Execution** | Reliable calculations | `BuiltInCodeExecutor`, specialist agents |
| **Agent Tools** | Specialist delegation | `AgentTool`, clear instructions |
| **MCP Integration** | External services | `McpToolset`, standardized protocols |
| **Long-Running Ops** | Human approvals | `ToolContext`, `App`, resumability |

### Best Practices

1. **Start Simple:** Begin with function tools, add complexity as needed
2. **Clear Instructions:** Tell agents exactly when to use each tool
3. **Error Handling:** Always return structured errors
4. **Test Thoroughly:** Test both success and failure paths
5. **State Management:** Use resumable apps for workflows that pause

### Progression Path

1. **Basic:** Custom function tools with simple logic
2. **Intermediate:** Add code execution for reliability
3. **Advanced:** Integrate MCP servers for external data
4. **Production:** Implement approval workflows for critical operations

---

## Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [ADK Tools Documentation](https://google.github.io/adk-docs/tools/)
- [MCP Tools Guide](https://google.github.io/adk-docs/tools/mcp-tools/)
- [Function Tools Guide](https://google.github.io/adk-docs/tools/function-tools/)
- [Model Context Protocol Spec](https://spec.modelcontextprotocol.io/)
- [MCP Server Examples](https://modelcontextprotocol.io/examples)

---

## Next Steps

Continue to **Day 3** to learn about **State and Memory Management** for building agents that remember context across sessions and conversations.
