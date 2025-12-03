# Day 5: Complete Guide to Agent-to-Agent Communication and Deployment

## Table of Contents

1. [Agent-to-Agent (A2A) Communication](#agent-to-agent-a2a-communication)
2. [Agent Deployment to Production](#agent-deployment-to-production)
3. [Memory Bank for Long-Term Memory](#memory-bank-for-long-term-memory)
4. [Best Practices and Decision Making](#best-practices-and-decision-making)

---

## Agent-to-Agent (A2A) Communication

### Overview: What is A2A?

**DECLARATIVE (What it is):**

The Agent2Agent (A2A) Protocol is a standardized communication protocol that enables AI agents to interact with each other over networks, regardless of their programming language, framework, or location. Think of it as a "universal translator" that allows different agents to understand each other and collaborate.

Key characteristics:
- **Standard Protocol**: Uses HTTP-based communication with JSON payloads
- **Agent Cards**: Each agent publishes a "business card" describing its capabilities
- **Framework-Agnostic**: Works across different programming languages and AI frameworks
- **Network-Based**: Agents can be on different machines, even across the internet
- **Tool-like Integration**: Remote agents can be used as if they were local tools

**CONDITIONAL (When to use it):**

Use A2A Protocol when:

| Scenario | Use A2A | Use Local Sub-Agents |
|----------|---------|---------------------|
| **Location** | Agents on different machines/servers | Agents in same codebase |
| **Ownership** | Different teams/organizations maintain agents | Your team owns all agents |
| **Language** | Cross-language integration needed (Python ↔ Java) | All agents use same language |
| **Framework** | Different AI frameworks (ADK, LangChain, etc.) | All use same framework |
| **Network** | Acceptable network latency | Need low-latency communication |
| **Contract** | Formal API contract required | Internal interface |
| **Example** | External vendor product catalog | Internal order processing steps |

**Specific use cases:**
1. **Cross-Organization Integration**: Your customer support agent needs to query a vendor's product catalog
2. **Microservices Architecture**: Different teams maintain specialized agents (payments, inventory, shipping)
3. **Third-Party Services**: Integrating with external AI services or vendors
4. **Cross-Language Systems**: Python agent needs to call a Java or Node.js agent
5. **Distributed Systems**: Agents need to run on different infrastructure

**PROCEDURAL (How to implement it):**

A2A implementation involves two roles: **exposing** agents (making them available) and **consuming** agents (using remote agents).

#### Part 1: Exposing an Agent via A2A

**Step 1: Create Your Agent**

First, build a standard ADK agent with tools:

```python
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

# Define a tool function
def get_product_info(product_name: str) -> str:
    """Get product information for a given product."""
    product_catalog = {
        "iphone 15 pro": "iPhone 15 Pro, $999, Low Stock (8 units)",
        "samsung galaxy s24": "Samsung Galaxy S24, $799, In Stock (31 units)"
    }

    product_lower = product_name.lower().strip()
    if product_lower in product_catalog:
        return f"Product: {product_catalog[product_lower]}"
    else:
        return f"Product not found: {product_name}"

# Create the agent
product_catalog_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite"),
    name="product_catalog_agent",
    description="External vendor's product catalog agent",
    instruction="You provide product information when asked. Use get_product_info tool.",
    tools=[get_product_info]
)
```

**Step 2: Convert to A2A-Compatible Service**

Use the `to_a2a()` function to wrap your agent:

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Convert agent to A2A-compatible FastAPI application
product_catalog_a2a_app = to_a2a(
    product_catalog_agent,
    port=8001  # Port where this agent will be served
)
```

What `to_a2a()` does automatically:
- Creates a FastAPI/Starlette web server
- Generates an agent card JSON describing capabilities
- Serves the agent card at `/.well-known/agent-card.json` (standard A2A path)
- Sets up A2A protocol endpoints (`/tasks` for communication)
- Handles request/response formatting per A2A specification

**Step 3: Deploy the Agent Server**

Save your agent code to a file (e.g., `product_catalog_server.py`):

```python
# product_catalog_server.py
import os
from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.google_llm import Gemini

# [Include your agent definition from Step 1]

# Create the A2A app - this is what uvicorn will serve
app = to_a2a(product_catalog_agent, port=8001)
```

Start the server using uvicorn:

```bash
# Run in background
uvicorn product_catalog_server:app --host localhost --port 8001
```

**Step 4: Verify the Agent Card**

Check that your agent is properly exposed:

```bash
curl http://localhost:8001/.well-known/agent-card.json
```

You should see a JSON response containing:
```json
{
  "name": "product_catalog_agent",
  "description": "External vendor's product catalog agent",
  "url": "http://localhost:8001",
  "skills": [...],  // Your tools become "skills"
  "version": "1.0.0"
}
```

#### Part 2: Consuming a Remote Agent via A2A

**Step 1: Create a Remote Agent Proxy**

Use `RemoteA2aAgent` to create a client-side proxy:

```python
from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH
)

# Create a proxy to the remote agent
remote_product_catalog_agent = RemoteA2aAgent(
    name="product_catalog_agent",
    description="Remote product catalog agent from external vendor",
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}"
)
```

What `RemoteA2aAgent` does:
- Reads the remote agent's card to understand capabilities
- Acts as a local proxy for the remote agent
- Translates sub-agent calls into A2A HTTP requests
- Handles all protocol details transparently

**Step 2: Use Remote Agent in Your Agent**

Add the remote agent as a sub-agent:

```python
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

# Create your main agent that uses the remote agent
customer_support_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite"),
    name="customer_support_agent",
    description="Customer support assistant",
    instruction="""
    You help customers with product inquiries.
    When asked about products, delegate to the product_catalog_agent sub-agent.
    Provide friendly, helpful responses.
    """,
    sub_agents=[remote_product_catalog_agent]  # Add remote agent as sub-agent
)
```

**Step 3: Run Your Agent**

Use the standard ADK Runner to execute:

```python
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import uuid

async def query_agent(user_query: str):
    # Setup session management
    session_service = InMemorySessionService()

    app_name = "support_app"
    user_id = "user_123"
    session_id = f"session_{uuid.uuid4().hex[:8]}"

    # Create session
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )

    # Create runner
    runner = Runner(
        agent=customer_support_agent,
        app_name=app_name,
        session_service=session_service
    )

    # Create message
    message = types.Content(parts=[types.Part(text=user_query)])

    # Run agent
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text"):
                    print(part.text)

# Test it
await query_agent("What's the price of the iPhone 15 Pro?")
```

**Communication Flow:**

```
User Question
    ↓
Customer Support Agent (local)
    ↓ (decides to query product info)
RemoteA2aAgent proxy
    ↓ (HTTP POST to http://localhost:8001/tasks)
Product Catalog Agent (remote server)
    ↓ (calls get_product_info tool)
    ↓ (returns product data via A2A response)
RemoteA2aAgent proxy
    ↓ (receives response)
Customer Support Agent
    ↓ (formulates final answer)
User receives answer
```

---

### Understanding Agent Cards

**DECLARATIVE (What it is):**

An Agent Card is a JSON document that serves as the "business card" or "contract" for an A2A-compatible agent. It's a standardized way for agents to describe themselves to potential consumers.

**Structure of an Agent Card:**

```json
{
  "name": "product_catalog_agent",
  "description": "External vendor's product catalog agent",
  "url": "http://localhost:8001",
  "version": "1.0.0",
  "skills": [
    {
      "name": "get_product_info",
      "description": "Get product information for a given product",
      "parameters": {
        "type": "object",
        "properties": {
          "product_name": {
            "type": "string",
            "description": "Name of the product"
          }
        }
      }
    }
  ],
  "input_modes": ["text"],
  "output_modes": ["text"]
}
```

**Components:**
- **name**: Unique identifier for the agent
- **description**: What the agent does
- **url**: Base URL where the agent is hosted
- **skills**: List of capabilities (tools/functions) the agent provides
- **parameters**: JSON Schema describing input format for each skill
- **input_modes/output_modes**: Supported data types (text, images, etc.)

**CONDITIONAL (When to use agent cards):**

Agent cards are automatically generated by `to_a2a()`, but you should understand them for:
1. **Debugging**: Verify your agent is exposing the correct capabilities
2. **Documentation**: Share the agent card with consumers to show what's available
3. **Integration**: Consumers read agent cards to understand how to interact with your agent
4. **Versioning**: Track changes to agent capabilities over time

**PROCEDURAL (How to access/use agent cards):**

```python
import requests
import json

# Fetch an agent card
response = requests.get("http://localhost:8001/.well-known/agent-card.json")
agent_card = response.json()

# Examine the agent's capabilities
print(f"Agent Name: {agent_card['name']}")
print(f"Description: {agent_card['description']}")
print(f"Available Skills: {len(agent_card['skills'])}")

for skill in agent_card['skills']:
    print(f"  - {skill['name']}: {skill['description']}")
```

---

## Agent Deployment to Production

### Overview: Why Deploy Agents?

**DECLARATIVE (What deployment is):**

Agent deployment is the process of taking your AI agent from a development environment (like a Jupyter notebook) and making it available as a production service that can:
- Run continuously without your intervention
- Handle requests from multiple users simultaneously
- Scale automatically based on demand
- Be accessed over the internet
- Provide enterprise-grade reliability and monitoring

**The Problem:**
- Your agent only works when your notebook is running
- It's not accessible to other users or systems
- It can't handle concurrent requests
- There's no reliability, monitoring, or scaling

**The Solution:**
Deploy your agent to a production platform like:
- **Vertex AI Agent Engine** (managed AI agent hosting)
- **Cloud Run** (serverless containers)
- **Google Kubernetes Engine (GKE)** (full container orchestration)

**CONDITIONAL (When to deploy):**

| Scenario | Deploy | Keep Local |
|----------|---------|-----------|
| **Production users** | Need external users to access | Only you use it |
| **Availability** | Must run 24/7 | Occasional testing |
| **Scale** | Handle multiple concurrent users | Single user at a time |
| **Integration** | Other systems need to call it | Standalone notebook |
| **Reliability** | Need monitoring, logging, auto-restart | Development/testing only |
| **Security** | Production data, authentication needed | Sandbox/demo data |

**When to choose each platform:**

**Vertex AI Agent Engine:**
- **Use when**: Building conversational AI agents with sessions and memory
- **Benefits**: Built-in session management, memory bank integration, agent-specific features
- **Cost**: Free tier available, scales based on usage
- **Best for**: Customer support bots, virtual assistants, multi-turn conversations

**Cloud Run:**
- **Use when**: General serverless deployment needs
- **Benefits**: Easy deployment, automatic scaling, pay-per-use pricing
- **Cost**: Very cost-effective for low/variable traffic
- **Best for**: API endpoints, lightweight agents, demos

**GKE (Kubernetes):**
- **Use when**: Complex multi-agent systems, need full control
- **Benefits**: Maximum flexibility, advanced networking, custom configurations
- **Cost**: More expensive, requires Kubernetes expertise
- **Best for**: Enterprise systems, microservices architectures

**PROCEDURAL (How to deploy to Vertex AI Agent Engine):**

#### Step-by-Step Deployment Guide

**Phase 1: Prepare Your Agent**

**Step 1: Create Project Structure**

Organize your agent in a dedicated directory:

```bash
mkdir weather_agent
cd weather_agent
```

Your final structure will be:
```
weather_agent/
├── agent.py                     # Agent code
├── requirements.txt             # Python dependencies
├── .env                         # Environment configuration
└── .agent_engine_config.json   # Deployment settings
```

**Step 2: Write the Agent Code**

Create `agent.py`:

```python
from google.adk.agents import Agent
import vertexai
import os

# Initialize Vertex AI
vertexai.init(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.environ["GOOGLE_CLOUD_LOCATION"],
)

# Define tool function
def get_weather(city: str) -> dict:
    """Returns weather information for a given city."""
    weather_data = {
        "tokyo": {
            "status": "success",
            "report": "Tokyo is clear with temperature of 70°F (21°C)."
        },
        "new york": {
            "status": "success",
            "report": "New York is cloudy with temperature of 65°F (18°C)."
        }
    }

    city_lower = city.lower()
    if city_lower in weather_data:
        return weather_data[city_lower]
    else:
        available = ", ".join([c.title() for c in weather_data.keys()])
        return {
            "status": "error",
            "error_message": f"City not available. Try: {available}"
        }

# Create the agent - MUST be named 'root_agent'
root_agent = Agent(
    name="weather_assistant",
    model="gemini-2.5-flash-lite",
    description="A weather assistant that provides weather information",
    instruction="""
    You are a friendly weather assistant. When users ask about weather:
    1. Identify the city name from their question
    2. Use the get_weather tool to fetch information
    3. Respond in a friendly, conversational tone
    Be helpful and concise.
    """,
    tools=[get_weather]
)
```

**Critical requirements:**
- Agent MUST be named `root_agent` (Agent Engine looks for this variable)
- Must call `vertexai.init()` with project and location from environment
- Tools must be properly defined with type hints and docstrings

**Step 3: Define Dependencies**

Create `requirements.txt`:

```txt
google-adk
opentelemetry-instrumentation-google-genai
```

**Why these packages:**
- `google-adk`: The Agent Development Kit framework
- `opentelemetry-instrumentation-google-genai`: Enables tracing and monitoring

**Step 4: Configure Environment**

Create `.env`:

```env
# Use global endpoint for Gemini
GOOGLE_CLOUD_LOCATION="global"

# Use Vertex AI backend (not Google AI Studio)
GOOGLE_GENAI_USE_VERTEXAI=1
```

**Configuration explained:**
- `GOOGLE_CLOUD_LOCATION="global"`: Uses Vertex AI's global endpoint for Gemini API
- `GOOGLE_GENAI_USE_VERTEXAI=1`: Tells ADK to use Vertex AI instead of AI Studio

**Step 5: Configure Deployment Settings**

Create `.agent_engine_config.json`:

```json
{
    "min_instances": 0,
    "max_instances": 1,
    "resource_limits": {
        "cpu": "1",
        "memory": "1Gi"
    }
}
```

**Settings explained:**

- `"min_instances": 0`: Scale down to zero when idle (saves costs)
  - When a request comes in, Agent Engine automatically starts an instance
  - Cold start takes ~30-60 seconds for first request after idle period
  - Set to 1 if you need instant response (but costs more)

- `"max_instances": 1`: Maximum concurrent instances
  - Limits scaling to prevent runaway costs
  - For production, increase based on expected traffic (e.g., 10, 50, 100)

- `"cpu": "1"`: Number of CPU cores per instance
  - "1" = 1 vCPU (suitable for most agents)
  - Increase for CPU-intensive operations

- `"memory": "1Gi"`: RAM per instance
  - "1Gi" = 1 gigabyte (suitable for lightweight agents)
  - Increase for memory-intensive operations or large models

**Phase 2: Prerequisites Setup**

**Step 6: Set Up Google Cloud Account**

1. **Create GCP Account**: Visit https://cloud.google.com/free
   - New users get $300 free credits (90 days)
   - Credit card required for verification (no charges during free trial)

2. **Create a Project**: In Google Cloud Console
   - Go to https://console.cloud.google.com
   - Click "Select a project" → "New Project"
   - Name your project (e.g., "ai-agents-demo")
   - Note your Project ID (you'll need this)

3. **Enable Required APIs**:
   ```bash
   # Or use this link to enable all at once:
   # https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com,storage.googleapis.com,logging.googleapis.com
   ```

   Required APIs:
   - Vertex AI API
   - Cloud Storage API
   - Cloud Logging API
   - Cloud Monitoring API
   - Cloud Trace API
   - Telemetry API

4. **Enable Billing**:
   - Go to Billing section in Cloud Console
   - Link a payment method
   - Agent Engine has a free tier, but billing must be enabled

**Step 7: Authenticate Locally**

If deploying from your local machine (not Kaggle):

```bash
# Install Google Cloud SDK
# Visit: https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Set application default credentials
gcloud auth application-default login
```

**Phase 3: Deploy the Agent**

**Step 8: Deploy Using ADK CLI**

```bash
# Set your project ID
export PROJECT_ID="your-project-id"

# Choose a region (Agent Engine is available in specific regions)
export REGION="us-west1"  # or "europe-west1", "us-east4", etc.

# Deploy the agent
adk deploy agent_engine \
    --project=$PROJECT_ID \
    --region=$REGION \
    weather_agent \
    --agent_engine_config_file=weather_agent/.agent_engine_config.json
```

**Available regions for Agent Engine:**
- `us-west1` (Oregon)
- `us-east4` (Virginia)
- `europe-west1` (Belgium)
- `europe-west4` (Netherlands)

**What happens during deployment:**

1. **Packaging**: ADK bundles your agent code and dependencies
2. **Upload**: Code is uploaded to Cloud Storage
3. **Build**: Agent Engine creates a container image
4. **Deploy**: Container is deployed to the specified region
5. **Output**: You receive a resource name like:
   ```
   projects/123456789/locations/us-west1/reasoningEngines/987654321
   ```

**Deployment typically takes 2-5 minutes.**

**Common deployment errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| "root_agent not found" | Agent variable not named correctly | Name your agent `root_agent` in agent.py |
| "Invalid region" | Region doesn't support Agent Engine | Use supported region (see list above) |
| "Permission denied" | APIs not enabled | Enable required APIs in Cloud Console |
| "Billing not enabled" | No billing account linked | Enable billing in Cloud Console |

**Phase 4: Test the Deployed Agent**

**Step 9: Retrieve the Deployed Agent**

```python
import vertexai
from vertexai import agent_engines

# Initialize Vertex AI
PROJECT_ID = "your-project-id"
REGION = "us-west1"
vertexai.init(project=PROJECT_ID, location=REGION)

# List all deployed agents
agents_list = list(agent_engines.list())

# Get the most recent agent
if agents_list:
    remote_agent = agents_list[0]
    print(f"Connected to: {remote_agent.resource_name}")
else:
    print("No agents found")
```

**Step 10: Query the Agent**

```python
# Simple query
async for item in remote_agent.async_stream_query(
    message="What is the weather in Tokyo?",
    user_id="user_123"
):
    print(item)
```

**Understanding the response:**

You'll see multiple items in the stream:
1. **Function call**: Agent decides to use `get_weather` tool
   ```python
   FunctionCall(name='get_weather', args={'city': 'Tokyo'})
   ```

2. **Function response**: Result from the tool
   ```python
   FunctionResponse(name='get_weather', response={'status': 'success', ...})
   ```

3. **Final response**: Agent's natural language answer
   ```python
   "The weather in Tokyo is clear with a temperature of 70°F (21°C)."
   ```

**Step 11: Advanced Testing with Sessions**

For conversation history and context:

```python
import uuid

# Create a session ID for maintaining conversation context
session_id = str(uuid.uuid4())
user_id = "user_123"

# First query
async for item in remote_agent.async_stream_query(
    message="What's the weather in Tokyo?",
    user_id=user_id,
    session_id=session_id
):
    if hasattr(item, 'text'):
        print(item.text)

# Follow-up query (uses same session)
async for item in remote_agent.async_stream_query(
    message="How about New York?",
    user_id=user_id,
    session_id=session_id  # Same session maintains context
):
    if hasattr(item, 'text'):
        print(item.text)
```

**Phase 5: Monitor and Manage**

**Step 12: View in Cloud Console**

Visit the Agent Engine Console:
```
https://console.cloud.google.com/vertex-ai/agents/agent-engines
```

You can:
- View all deployed agents
- See deployment status and health
- Monitor request metrics
- View logs and traces
- Delete agents

**Step 13: Access Logs**

```python
# View logs for debugging
from google.cloud import logging

logging_client = logging.Client(project=PROJECT_ID)
logger = logging_client.logger("vertex-ai-agent-engine")

for entry in logger.list_entries(max_results=10):
    print(f"{entry.timestamp}: {entry.payload}")
```

**Phase 6: Cleanup**

**Step 14: Delete the Agent**

**CRITICAL: Always delete test agents to avoid charges!**

```python
# Delete the deployed agent
agent_engines.delete(
    resource_name=remote_agent.resource_name,
    force=True  # Force deletion even if running
)

print("Agent deleted successfully")
```

**Why cleanup matters:**
- Agent Engine charges for running instances
- Even with `min_instances=0`, there may be storage costs
- Free tier is limited - deleting prevents unexpected charges

**Cost monitoring:**

Check your costs:
```
https://console.cloud.google.com/billing
```

Set up budget alerts:
```
https://console.cloud.google.com/billing/budgets
```

---

### Alternative Deployment: Cloud Run

**PROCEDURAL (How to deploy to Cloud Run):**

Cloud Run is another deployment option that's simpler for basic use cases.

**Step 1: Create Dockerfile**

Create `Dockerfile` in your agent directory:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agent.py .
COPY .env .

# Expose port
ENV PORT=8080

# Run the agent server
CMD adk api_server agent:root_agent --host 0.0.0.0 --port $PORT
```

**Step 2: Deploy to Cloud Run**

```bash
# Build and deploy in one command
gcloud run deploy weather-agent \
    --source . \
    --region us-central1 \
    --allow-unauthenticated
```

**Step 3: Get the URL**

Cloud Run provides a URL like:
```
https://weather-agent-abc123-uc.a.run.app
```

You can now send HTTP requests to this URL.

---

## Memory Bank for Long-Term Memory

### Overview: What is Memory Bank?

**DECLARATIVE (What it is):**

Memory Bank is a Vertex AI service that provides long-term, persistent memory for your agents across sessions. It allows agents to remember facts, preferences, and context from previous conversations, even after the session ends.

**Types of Memory:**

| Memory Type | Scope | Persistence | Example |
|-------------|-------|-------------|---------|
| **Session Memory** | Single conversation | Until session ends | "You just asked about Tokyo" |
| **Memory Bank** | All conversations | Permanent (until deleted) | "User prefers Celsius" |

**How Memory Bank works:**

1. **During conversation**: Agent can search Memory Bank for relevant past information
2. **After conversation**: Agent Engine automatically extracts key facts and stores them
3. **Future conversations**: Agent automatically recalls relevant memories

**CONDITIONAL (When to use Memory Bank):**

Use Memory Bank when:

**Personalization needs:**
- User preferences should persist (temperature units, language, notification preferences)
- Agent should remember user's role, goals, or context
- User shouldn't have to repeat information every conversation

**Knowledge accumulation:**
- Agent needs to build up knowledge over time
- Learning from past interactions improves future responses
- Complex projects require continuity across sessions

**Examples:**
- **Customer Support**: "User reported bug #123 last week, don't ask again"
- **Personal Assistant**: "User prefers morning meetings, no calls after 5pm"
- **Education**: "User has completed modules 1-3, currently on module 4"
- **Sales**: "User interested in enterprise plan, follow up in 2 weeks"

**Don't use Memory Bank when:**
- Agent is stateless (each request is independent)
- No personalization needed
- Privacy concerns (user data should not persist)
- Short-term projects only

**PROCEDURAL (How to implement Memory Bank):**

**Step 1: Add Memory Tools to Your Agent**

```python
from google.adk.agents import Agent
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

# Create memory tool
memory_tool = PreloadMemoryTool(
    memory_bank_resource_name="projects/YOUR_PROJECT/locations/REGION/memoryBanks/MEMORY_BANK_ID"
)

# Create agent with memory
root_agent = Agent(
    name="weather_assistant",
    model="gemini-2.5-flash-lite",
    description="Weather assistant with memory",
    instruction="""
    You are a weather assistant that remembers user preferences.

    When a user mentions preferences (temperature units, favorite cities, etc.):
    1. Remember these preferences
    2. Apply them in future conversations

    Before responding, search your memory for relevant information about the user.
    """,
    tools=[get_weather, memory_tool],  # Add memory tool
    enable_memory=True  # Enable memory extraction
)
```

**Step 2: Create Memory Bank Resource**

```python
from vertexai import memory_bank

# Create a memory bank
memory_bank_resource = memory_bank.create(
    display_name="weather_preferences",
    project=PROJECT_ID,
    location=REGION
)

print(f"Memory Bank created: {memory_bank_resource.resource_name}")
```

**Step 3: Deploy with Memory Enabled**

Deploy as normal - Memory Bank is now integrated:

```bash
adk deploy agent_engine \
    --project=$PROJECT_ID \
    --region=$REGION \
    weather_agent \
    --agent_engine_config_file=weather_agent/.agent_engine_config.json
```

**Step 4: Test Memory Persistence**

```python
# Session 1: User sets preference
session_1 = str(uuid.uuid4())

async for item in remote_agent.async_stream_query(
    message="I prefer Celsius temperatures",
    user_id="user_123",
    session_id=session_1
):
    print(item)

# Session 2: Different session, preference is remembered
session_2 = str(uuid.uuid4())

async for item in remote_agent.async_stream_query(
    message="What's the weather in Tokyo?",
    user_id="user_123",  # Same user
    session_id=session_2  # Different session
):
    print(item)

# Agent should respond in Celsius because it remembered the preference!
```

**How it works behind the scenes:**

```
Session 1:
User: "I prefer Celsius"
  ↓
Agent processes request
  ↓
After session ends:
Agent Engine extracts fact: "user_123 prefers Celsius"
  ↓
Stores in Memory Bank

Session 2:
User: "What's the weather in Tokyo?"
  ↓
Agent queries Memory Bank
  ↓
Finds: "user_123 prefers Celsius"
  ↓
Agent uses get_weather tool
  ↓
Converts Fahrenheit to Celsius in response
```

---

## Best Practices and Decision Making

### Deployment Decision Matrix

**DECLARATIVE (What to consider):**

Choose the right deployment platform based on your requirements:

| Requirement | Agent Engine | Cloud Run | GKE |
|------------|--------------|-----------|-----|
| **Conversational agents** | ⭐⭐⭐ Best | ⭐⭐ Good | ⭐ Possible |
| **Session management** | ⭐⭐⭐ Built-in | ⭐ Manual | ⭐ Manual |
| **Memory Bank integration** | ⭐⭐⭐ Native | ❌ Not available | ❌ Not available |
| **Simple deployment** | ⭐⭐⭐ Easiest | ⭐⭐ Easy | ⭐ Complex |
| **Cost for low traffic** | ⭐⭐⭐ Free tier | ⭐⭐⭐ Pay-per-use | ⭐ Higher baseline |
| **Custom infrastructure** | ⭐ Limited | ⭐⭐ Moderate | ⭐⭐⭐ Full control |
| **Auto-scaling** | ⭐⭐⭐ Automatic | ⭐⭐⭐ Automatic | ⭐⭐ Manual config |

### Cost Optimization Strategies

**CONDITIONAL (When to use each strategy):**

**1. Scale to Zero**
- **When**: Agent has sporadic usage (not 24/7)
- **How**: Set `"min_instances": 0`
- **Savings**: Only pay for active time
- **Trade-off**: 30-60s cold start for first request after idle

**2. Instance Limits**
- **When**: Testing or predictable low traffic
- **How**: Set `"max_instances": 1` or low number
- **Savings**: Prevents runaway scaling costs
- **Trade-off**: Requests may queue if limit reached

**3. Right-Size Resources**
- **When**: Agent doesn't need much CPU/memory
- **How**: Start with `"cpu": "1", "memory": "1Gi"`, monitor, adjust
- **Savings**: Pay only for resources you need
- **Trade-off**: Under-provisioning causes slowness

**4. Region Selection**
- **When**: Users are geographically concentrated
- **How**: Deploy in region closest to users
- **Savings**: Lower latency = faster responses = lower compute time
- **Trade-off**: Multi-region costs more but provides redundancy

**5. Model Selection**
- **When**: Task doesn't require most capable model
- **How**: Use `gemini-2.5-flash-lite` instead of `gemini-pro` for simple tasks
- **Savings**: Lite models are significantly cheaper
- **Trade-off**: May have lower quality for complex tasks

### Security Best Practices

**PROCEDURAL (How to secure your agents):**

**1. Authentication**

```python
# Don't allow unauthenticated access in production
# Cloud Run example:
gcloud run deploy weather-agent \
    --source . \
    --region us-central1 \
    --no-allow-unauthenticated  # Require authentication
```

**2. Environment Variables for Secrets**

```python
# Never hardcode API keys
# Bad:
API_KEY = "sk-1234567890abcdef"

# Good:
import os
API_KEY = os.environ.get("API_KEY")
```

Store secrets in Secret Manager:
```bash
# Create secret
gcloud secrets create api-key --data-file=-

# Grant access to Agent Engine service account
gcloud secrets add-iam-policy-binding api-key \
    --member="serviceAccount:SERVICE_ACCOUNT@PROJECT.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

**3. Input Validation**

```python
def get_weather(city: str) -> dict:
    """Get weather for a city."""
    # Validate input
    if not city or len(city) > 100:
        return {"status": "error", "error_message": "Invalid city name"}

    # Sanitize input
    city = city.strip().lower()

    # Check against allowed list
    allowed_cities = ["tokyo", "new york", "london", "paris"]
    if city not in allowed_cities:
        return {"status": "error", "error_message": f"City not supported"}

    # Proceed with query
    return fetch_weather_data(city)
```

**4. Rate Limiting**

```python
from google.adk.agents import Agent

root_agent = Agent(
    name="weather_assistant",
    model="gemini-2.5-flash-lite",
    # ... other config ...

    # Add rate limiting
    max_requests_per_minute=60,  # Limit to 60 requests/minute per user
)
```

**5. Logging and Monitoring**

```python
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_weather(city: str) -> dict:
    logger.info(f"Weather request for city: {city}")

    try:
        result = fetch_weather_data(city)
        logger.info(f"Weather data retrieved successfully for {city}")
        return result
    except Exception as e:
        logger.error(f"Error fetching weather for {city}: {e}")
        raise
```

### Monitoring and Debugging

**PROCEDURAL (How to monitor deployed agents):**

**1. View Logs in Cloud Console**

```
https://console.cloud.google.com/logs/query
```

Filter logs:
```
resource.type="vertex_ai_endpoint"
resource.labels.agent_id="YOUR_AGENT_ID"
severity>="WARNING"
```

**2. Enable Tracing**

```python
from google.adk.agents import Agent

root_agent = Agent(
    name="weather_assistant",
    model="gemini-2.5-flash-lite",
    # ... other config ...

    enable_tracing=True  # Enable distributed tracing
)
```

View traces:
```
https://console.cloud.google.com/traces/list
```

**3. Set Up Alerts**

Create alert for high error rate:
```bash
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="Agent Errors" \
    --condition-display-name="High Error Rate" \
    --condition-threshold-value=10 \
    --condition-threshold-duration=300s
```

**4. Monitor Costs**

Create budget alert:
```
https://console.cloud.google.com/billing/budgets
```

Set budget (e.g., $50/month) with alerts at 50%, 90%, 100%

### Testing Strategies

**CONDITIONAL (When to use each testing approach):**

**1. Local Testing**
- **When**: Development and initial debugging
- **How**: Run agent in notebook or local Python script
- **Benefits**: Fast iteration, no deployment needed
- **Limitations**: Doesn't test deployment config or scaling

**2. Staging Deployment**
- **When**: Before production release
- **How**: Deploy to separate project or with different name
- **Benefits**: Tests real deployment, isolated from production
- **Example**:
  ```bash
  adk deploy agent_engine \
      --project=$STAGING_PROJECT \
      --region=$REGION \
      weather_agent_staging
  ```

**3. Integration Testing**
- **When**: Testing A2A communication or tool integrations
- **How**: Deploy all components and test end-to-end
- **Example**:
  ```python
  # Test A2A integration
  async def test_a2a_flow():
      # Deploy consumer agent
      # Deploy provider agent
      # Send test queries
      # Verify responses
      assert response.contains("expected data")
  ```

**4. Load Testing**
- **When**: Before production launch with high traffic
- **How**: Use tools like Locust or Apache JMeter
- **Example**:
  ```python
  # locustfile.py
  from locust import HttpUser, task

  class AgentUser(HttpUser):
      @task
      def query_agent(self):
          self.client.post("/query", json={
              "message": "What's the weather in Tokyo?",
              "user_id": "test_user"
          })
  ```

---

## Complete Example: E-Commerce Customer Support System

**DECLARATIVE (What we're building):**

A production-ready customer support system that:
- Uses A2A to integrate with external product catalog
- Deploys to Agent Engine with Memory Bank
- Remembers customer preferences
- Scales automatically

**PROCEDURAL (Complete implementation):**

### System Architecture

```
┌─────────────────────────────────────────┐
│  Customer                               │
│  ↓                                      │
│  Customer Support Agent (deployed)     │
│  ├─ Memory Bank (remembers customers)  │
│  └─ A2A call ──────────────────────┐   │
│                                     ↓   │
│  Product Catalog Agent (external)      │
│  └─ Database (product info)            │
└─────────────────────────────────────────┘
```

### Step 1: Create Product Catalog Agent (External Service)

```bash
mkdir product_catalog_agent
cd product_catalog_agent
```

**product_catalog_agent/agent.py:**

```python
from google.adk.agents import Agent
import vertexai
import os

vertexai.init(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.environ["GOOGLE_CLOUD_LOCATION"],
)

def get_product_info(product_name: str) -> dict:
    """Get detailed product information."""
    products = {
        "laptop pro": {
            "name": "Laptop Pro 15",
            "price": "$1299",
            "stock": "In Stock (23 units)",
            "specs": "Intel i7, 16GB RAM, 512GB SSD"
        },
        "wireless mouse": {
            "name": "Wireless Mouse X1",
            "price": "$49",
            "stock": "In Stock (156 units)",
            "specs": "2.4GHz wireless, 6-month battery"
        }
    }

    product_key = product_name.lower().strip()
    if product_key in products:
        return {"status": "success", "product": products[product_key]}
    else:
        return {
            "status": "error",
            "message": f"Product '{product_name}' not found",
            "available": list(products.keys())
        }

root_agent = Agent(
    name="product_catalog_agent",
    model="gemini-2.5-flash-lite",
    description="Product catalog service providing product information",
    instruction="""
    You provide product information from the catalog.
    Use get_product_info to fetch details.
    Always include price, availability, and specs.
    """,
    tools=[get_product_info]
)
```

**product_catalog_agent/requirements.txt:**
```txt
google-adk[a2a]
opentelemetry-instrumentation-google-genai
```

**product_catalog_agent/.env:**
```env
GOOGLE_CLOUD_LOCATION="global"
GOOGLE_GENAI_USE_VERTEXAI=1
```

**product_catalog_agent/.agent_engine_config.json:**
```json
{
    "min_instances": 0,
    "max_instances": 3,
    "resource_limits": {"cpu": "1", "memory": "1Gi"}
}
```

**Deploy Product Catalog Agent:**

```bash
adk deploy agent_engine \
    --project=$PROJECT_ID \
    --region=$REGION \
    product_catalog_agent \
    --agent_engine_config_file=product_catalog_agent/.agent_engine_config.json
```

**Expose via A2A:**

After deployment, convert to A2A service:

```python
# product_catalog_a2a_server.py
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from agent import root_agent

app = to_a2a(root_agent, port=8001)
```

Deploy A2A server (separate from Agent Engine):
```bash
# Deploy to Cloud Run for A2A endpoint
gcloud run deploy product-catalog-a2a \
    --source product_catalog_agent \
    --region $REGION \
    --allow-unauthenticated
```

Note the URL (e.g., `https://product-catalog-a2a-xyz.run.app`)

### Step 2: Create Customer Support Agent with Memory

```bash
mkdir customer_support_agent
cd customer_support_agent
```

**customer_support_agent/agent.py:**

```python
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
import vertexai
import os

vertexai.init(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.environ["GOOGLE_CLOUD_LOCATION"],
)

# Connect to remote Product Catalog Agent via A2A
PRODUCT_CATALOG_URL = "https://product-catalog-a2a-xyz.run.app"  # Your deployed URL

remote_product_catalog = RemoteA2aAgent(
    name="product_catalog_agent",
    description="External product catalog service",
    agent_card=f"{PRODUCT_CATALOG_URL}{AGENT_CARD_WELL_KNOWN_PATH}"
)

# Set up Memory Bank
MEMORY_BANK_ID = os.environ.get("MEMORY_BANK_ID")
memory_tool = PreloadMemoryTool(
    memory_bank_resource_name=f"projects/{os.environ['GOOGLE_CLOUD_PROJECT']}/locations/{os.environ['GOOGLE_CLOUD_LOCATION']}/memoryBanks/{MEMORY_BANK_ID}"
)

# Create customer support agent
root_agent = Agent(
    name="customer_support_agent",
    model="gemini-2.5-flash-lite",
    description="Customer support assistant with product catalog integration",
    instruction="""
    You are a helpful customer support agent for an e-commerce company.

    Capabilities:
    1. Answer product questions using product_catalog_agent
    2. Remember customer preferences and history using memory
    3. Provide personalized assistance

    Workflow:
    1. Check memory for customer preferences and history
    2. Use product_catalog_agent for product information
    3. Provide friendly, personalized responses
    4. Remember important details for future interactions

    Be professional, helpful, and remember customer context.
    """,
    tools=[memory_tool],
    sub_agents=[remote_product_catalog],
    enable_memory=True
)
```

**customer_support_agent/.env:**
```env
GOOGLE_CLOUD_LOCATION="global"
GOOGLE_GENAI_USE_VERTEXAI=1
MEMORY_BANK_ID="your-memory-bank-id"
```

**customer_support_agent/.agent_engine_config.json:**
```json
{
    "min_instances": 1,
    "max_instances": 10,
    "resource_limits": {"cpu": "2", "memory": "2Gi"}
}
```

**Deploy Customer Support Agent:**

```bash
# Create Memory Bank first
python -c "
from vertexai import memory_bank
import os

mb = memory_bank.create(
    display_name='customer_support_memory',
    project=os.environ['PROJECT_ID'],
    location=os.environ['REGION']
)
print(f'Memory Bank ID: {mb.resource_name.split(\"/\")[-1]}')
"

# Add MEMORY_BANK_ID to .env file

# Deploy
adk deploy agent_engine \
    --project=$PROJECT_ID \
    --region=$REGION \
    customer_support_agent \
    --agent_engine_config_file=customer_support_agent/.agent_engine_config.json
```

### Step 3: Test the Complete System

```python
import vertexai
from vertexai import agent_engines
import uuid

# Initialize
PROJECT_ID = "your-project-id"
REGION = "us-west1"
vertexai.init(project=PROJECT_ID, location=REGION)

# Get deployed agent
agents = list(agent_engines.list())
support_agent = agents[0]  # Customer support agent

# Test 1: First interaction - Customer asks about product
session_1 = str(uuid.uuid4())
user_id = "customer_alice"

print("=== Test 1: Product Inquiry ===")
async for item in support_agent.async_stream_query(
    message="I'm interested in the Laptop Pro. Can you tell me about it?",
    user_id=user_id,
    session_id=session_1
):
    if hasattr(item, 'text'):
        print(item.text)

# Test 2: Customer sets preference
print("\n=== Test 2: Set Preference ===")
async for item in support_agent.async_stream_query(
    message="I prefer to see prices in euros, not dollars.",
    user_id=user_id,
    session_id=session_1
):
    if hasattr(item, 'text'):
        print(item.text)

# Test 3: New session - Preference should be remembered
session_2 = str(uuid.uuid4())

print("\n=== Test 3: New Session (Days Later) ===")
async for item in support_agent.async_stream_query(
    message="What's the price of the Wireless Mouse?",
    user_id=user_id,  # Same user
    session_id=session_2  # Different session
):
    if hasattr(item, 'text'):
        print(item.text)

# Expected: Agent remembers euro preference and converts price!
```

**Expected Flow:**

```
Test 1:
Customer asks about Laptop Pro
  ↓
Support Agent checks Memory Bank (no prior history)
  ↓
Support Agent calls Product Catalog Agent via A2A
  ↓
Product Catalog returns: {"price": "$1299", ...}
  ↓
Support Agent responds: "Laptop Pro costs $1299..."
  ↓
After session: Memory stores "customer_alice interested in Laptop Pro"

Test 2:
Customer sets euro preference
  ↓
Support Agent acknowledges
  ↓
After session: Memory stores "customer_alice prefers euros"

Test 3 (Different day/session):
Customer asks about Wireless Mouse
  ↓
Support Agent checks Memory Bank
  ↓
Finds: "customer_alice prefers euros"
  ↓
Support Agent calls Product Catalog Agent via A2A
  ↓
Product Catalog returns: {"price": "$49", ...}
  ↓
Support Agent converts: $49 → €45 (approximate)
  ↓
Support Agent responds: "Wireless Mouse costs €45..." ✨
```

---

## Summary and Quick Reference

### A2A Communication Quick Reference

**When to use:**
- Cross-organization integrations
- Different programming languages/frameworks
- Microservices architectures
- Third-party agent services

**How to expose an agent:**
```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a
app = to_a2a(your_agent, port=8001)
# Run with: uvicorn server:app --port 8001
```

**How to consume a remote agent:**
```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH

remote_agent = RemoteA2aAgent(
    name="remote_agent",
    description="Description",
    agent_card=f"http://remote-url{AGENT_CARD_WELL_KNOWN_PATH}"
)

# Use as sub-agent
my_agent = Agent(..., sub_agents=[remote_agent])
```

### Deployment Quick Reference

**Agent Engine deployment:**
```bash
adk deploy agent_engine \
    --project=PROJECT_ID \
    --region=REGION \
    agent_directory \
    --agent_engine_config_file=agent_directory/.agent_engine_config.json
```

**Required files:**
- `agent.py` (must define `root_agent`)
- `requirements.txt`
- `.env`
- `.agent_engine_config.json`

**Testing deployed agent:**
```python
import vertexai
from vertexai import agent_engines

vertexai.init(project=PROJECT_ID, location=REGION)
agents = list(agent_engines.list())
remote_agent = agents[0]

async for item in remote_agent.async_stream_query(
    message="Your query",
    user_id="user_id"
):
    print(item)
```

**Cleanup:**
```python
agent_engines.delete(resource_name=remote_agent.resource_name, force=True)
```

### Memory Bank Quick Reference

**Enable memory:**
```python
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

memory_tool = PreloadMemoryTool(
    memory_bank_resource_name="projects/PROJECT/locations/REGION/memoryBanks/ID"
)

root_agent = Agent(
    ...,
    tools=[memory_tool],
    enable_memory=True
)
```

**Create Memory Bank:**
```python
from vertexai import memory_bank

mb = memory_bank.create(
    display_name="memory_name",
    project=PROJECT_ID,
    location=REGION
)
```

### Decision Matrices

**A2A vs Local Sub-Agents:**
- Same codebase? → Local sub-agents
- Different organizations? → A2A
- Need formal contract? → A2A
- Performance critical? → Local sub-agents

**Deployment Platform:**
- Conversational AI with sessions? → Agent Engine
- Simple API endpoint? → Cloud Run
- Complex multi-service system? → GKE
- Need Memory Bank? → Agent Engine (only option)

**Cost Optimization:**
- Sporadic usage? → `min_instances: 0`
- Predictable low traffic? → `max_instances: 1-3`
- Always-on requirement? → `min_instances: 1+`
- Simple tasks? → Use `gemini-2.5-flash-lite`

---

## Troubleshooting Guide

### Common A2A Issues

**Issue: "Connection refused" when accessing remote agent**
- **Cause**: Remote agent server not running or wrong URL
- **Solution**:
  ```bash
  # Verify server is running
  curl http://localhost:8001/.well-known/agent-card.json
  # Should return JSON agent card
  ```

**Issue: "Agent card not found"**
- **Cause**: Agent not properly exposed via `to_a2a()`
- **Solution**: Ensure you called `to_a2a()` and server is running on correct port

**Issue: "Remote agent not responding"**
- **Cause**: Network issue, authentication, or server error
- **Solution**: Check server logs, verify no firewall blocking, test with curl

### Common Deployment Issues

**Issue: "root_agent not found"**
- **Cause**: Agent variable not named `root_agent` in agent.py
- **Solution**: Rename your agent variable to exactly `root_agent`

**Issue: "Region not supported"**
- **Cause**: Selected region doesn't support Agent Engine
- **Solution**: Use supported region: us-west1, us-east4, europe-west1, europe-west4

**Issue: "Permission denied" errors**
- **Cause**: Required APIs not enabled or insufficient permissions
- **Solution**:
  ```bash
  # Enable APIs
  gcloud services enable aiplatform.googleapis.com
  ```

**Issue: "Out of memory" errors**
- **Cause**: Insufficient memory allocation
- **Solution**: Increase memory in `.agent_engine_config.json`:
  ```json
  {"resource_limits": {"cpu": "2", "memory": "4Gi"}}
  ```

### Common Memory Bank Issues

**Issue: "Memory not persisting across sessions"**
- **Cause**: `enable_memory=True` not set or Memory Bank not configured
- **Solution**: Verify both `enable_memory=True` in agent and `PreloadMemoryTool` is added

**Issue: "Cannot find Memory Bank"**
- **Cause**: Incorrect resource name or Memory Bank not created
- **Solution**:
  ```python
  # List memory banks
  from vertexai import memory_bank
  banks = list(memory_bank.list(project=PROJECT_ID, location=REGION))
  print([b.resource_name for b in banks])
  ```

---

This guide covers the complete lifecycle of building multi-agent systems with A2A communication and deploying them to production with persistent memory. Each section provides declarative explanations (what it is), conditional guidance (when to use it), and procedural instructions (how to do it) for comprehensive understanding.
