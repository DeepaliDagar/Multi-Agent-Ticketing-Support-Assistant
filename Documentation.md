# Complete End-to-End Project Documentation

## Multi-Agent Customer Support System using Google ADK and MCP Protocol

A production-ready multi-agent customer support system featuring Google ADK, FastMCP server, intelligent agent routing, and an interactive chatbot interface.
---

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [File-by-File Breakdown](#file-by-file-breakdown)
5. [Data Flow & Communication](#data-flow--communication)
6. [How Everything Works Together](#how-everything-works-together)
7. [Complete Execution Flow](#complete-execution-flow)
8. [Database Schema](#database-schema)
9. [MCP Protocol Implementation](#mcp-protocol-implementation)
10. [Agent Coordination Logic](#agent-coordination-logic)

---

## Project Overview

This project implements a **production-ready multi-agent AI customer support system** that demonstrates:

- **Supervisor Agent Architecture**: A router agent (supervisor) intelligently routes queries to specialized agents
- **Agent-to-Agent (A2A) Coordination**: Multiple agents collaborate to handle complex multi-step queries
- **Model Context Protocol (MCP)**: Tools exposed via MCP protocol for dynamic tool discovery
- **Multi-Provider LLM Support**: Using LiteLLM to support OpenAI, Gemini, and other providers
- **Interactive Chatbot Interface**: Real-time visualization of agent handoffs and routing decisions

### Key Features

- 3 specialized agents: Customer Data, Support, SQL Generator
- 7+ MCP tools for customer and ticket management
- SQLite database with WAL mode for concurrent access
- Stateless HTTP MCP server using FastMCP
- Per-agent session management using Google ADK

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│                  (chatbot.py)                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ User Query
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 A2A Orchestrator                         │
│         (a2a/orchestrator.py)                            │
│  - Coordinates execution                                 │
│  - Manages agent lifecycle                               │
│  - Collects and aggregates results                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Query + Previous Results
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Router Agent (Supervisor)                   │
│         (a2a/agent/router_agent.py)                      │
│  - Makes routing decisions                               │
│  - Evaluates query completeness                          │
│  - Returns JSON decision                                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Decision: {"next_agent": "...", "done": false}
                     ▼
         ┌───────────────────────────────────┐
         │    A2A Orchestrator               │
         │    (Executes selected agent)      │
         └────┬──────────┬──────────┬────────┘
              │          │          │
              ▼          ▼          ▼
      ┌──────────┐ ┌──────────┐ ┌──────────────┐
      │ Customer │ │ Support  │ │ SQL Generator│
      │  Agent   │ │  Agent   │ │    Agent     │
      └────┬─────┘ └────┬─────┘ └──────┬───────┘
           │            │               │
           │            │               │
           └────────────┴───────────────┘
                         │
                         │ Tool Calls via MCP Protocol
                         │ HTTP POST to /mcp endpoint
                         ▼
              ┌──────────────────┐
              │  FastMCP Server  │
              │ (mcp_server.py)  │
              │  JSON-RPC 2.0    │
              └────────┬─────────┘
                       │
                       │ Tool Function Calls
                       ▼
              ┌──────────────────┐
              │   Tool Layer     │
              │ (customer_mcp/   │
              │   tools/*.py)    │
              └────────┬─────────┘
                       │
                       │ SQL Queries
                       ▼
              ┌──────────────────┐
              │   SQLite DB      │
              │  (support.db)    │
              │  WAL Mode        │
              └──────────────────┘
```

---

## Technology Stack

### Core Frameworks
- **Google ADK (Agent Development Kit)**: Framework for building LLM agents
- **FastMCP**: Recommended way to build MCP servers
- **LiteLLM**: Universal LLM adapter for multi-provider support
- **SQLite**: Embedded database with WAL mode

### Python Libraries
- `google.adk`: Agent creation and orchestration
- `mcp.server.fastmcp`: MCP server implementation
- `litellm`: LLM provider abstraction
- `sqlite3`: Database operations
- `termcolor`: Colored terminal output
- `python-dotenv`: Environment configuration

### Protocols & Standards
- **MCP (Model Context Protocol)**: Tool discovery and execution protocol
- **JSON-RPC 2.0**: Communication protocol over HTTP
- **HTTP/1.1**: Transport layer for MCP

---

## File-by-File Breakdown

### Root Level Files

#### `chatbot.py`
**Purpose**: Interactive command-line chatbot interface for end users

**What it does**:
- Provides a conversational UI with colored output
- Handles user input and displays responses
- Shows real-time agent handoff visualization
- Manages special commands (exit, clear, help)

**Why it's needed**:
- User-facing interface for the multi-agent system
- Demonstrates transparent AI decision-making
- Provides visual feedback on agent coordination
- Makes the system accessible to non-technical users

**Key Components**:
- `handoff_display_callback`: Visualizes agent transitions
- `chatbot_session()`: Main chat loop
- Terminal formatting with `termcolor`

**Dependencies**: `a2a.orchestrator`, `termcolor`

---

### Configuration & Utilities

#### `a2a/utils.py`
**Purpose**: Central configuration and utility functions

**What it does**:
- Loads environment variables from `.env` file
- Configures LiteLLM for OpenAI models
- Defines MCP server URL and port
- Sets model names for each agent
- Validates configuration

**Why it's needed**:
- Single source of truth for configuration
- Enables easy environment-based configuration
- Centralizes API key management
- Allows configuration validation before runtime

**Key Variables**:
- `MCP_HTTP_BASE_URL`: MCP server endpoint
- `ROUTER_MODEL`, `CUSTOMER_DATA_MODEL`, etc.: LLM model names
- `OPENAI_API_KEY`: API key for OpenAI models via LiteLLM

**Dependencies**: `python-dotenv`, `litellm`

---

### Core Orchestration

#### `a2a/orchestrator.py`
**Purpose**: Central coordinator for multi-agent execution (572 lines)

**What it does**:
- Implements Supervisor Agent Architecture
- Routes queries to appropriate agents via router
- Manages agent lifecycle and session creation
- Collects and aggregates agent results
- Handles iterative multi-agent workflows
- Implements handoff callbacks for external notifications

**Why it's needed**:
- Core orchestration logic - without this, agents can't coordinate
- Implements the supervisor pattern for intelligent routing
- Manages complex multi-step workflows
- Handles error recovery and iteration limits

**Key Classes**:
- `A2AOrchestrator`: Main orchestrator class
- `AsyncCleanupFilter`: Filters harmless async cleanup errors

**Key Methods**:
- `process_query()`: Main entry point for query processing
- `_supervisor_decide()`: Calls router agent for routing decisions
- `_execute_agent()`: Executes a specific agent with session management
- `_get_session_id()`: Generates per-agent session IDs

**Dependencies**: `google.adk`, `google.adk.sessions`, all agent modules

**Design Decisions**:
- Uses Google ADK's `InMemorySessionService` for session management
- Implements maximum iteration limit (default: 5) to prevent infinite loops
- Async/await pattern for non-blocking execution
- Error suppression for harmless MCP connection cleanup warnings

---

### Agent Implementations

#### `a2a/agent/router_agent.py`
**Purpose**: Supervisor agent that makes routing decisions

**What it does**:
- Analyzes user queries to determine which agent should handle them
- Evaluates intermediate results to decide if more agents are needed
- Returns JSON decisions: `{"next_agent": "...", "done": true/false, "reason": "..."}`
- Acts as the central decision-maker in Supervisor Architecture

**Why it's needed**:
- Intelligent routing - without this, you'd need hardcoded routing rules
- Enables dynamic, context-aware routing
- Makes the system extensible (easy to add new agents)
- Evaluates query completeness for multi-step workflows

**Key Components**:
- `LlmAgent` with GPT-4o-mini model
- Detailed instruction prompt explaining routing logic
- MCP tool access for all tools (can use tools if needed)

**Model**: `openai/gpt-4o-mini` (configurable via `ROUTER_MODEL`)

**Output Format**: JSON with `next_agent`, `done`, and `reason` fields

---

#### `a2a/agent/customer_data_agent.py`
**Purpose**: Handles customer information operations

**What it does**:
- Retrieves customer details by ID
- Lists and filters customers
- Adds new customers
- Updates customer information
- Uses MCP tools: `get_customer`, `list_customers`, `add_customer`, `update_customer`

**Why it's needed**:
- Specialized domain expertise for customer data operations
- Separates concerns from support and SQL agents
- Enables focused prompts and tool access

**Model**: `openai/gpt-4o-mini` (configurable via `CUSTOMER_DATA_MODEL`)

**Available Tools**: Customer CRUD operations via MCP

---

#### `a2a/agent/support_agent.py`
**Purpose**: Handles support ticket operations

**What it does**:
- Creates support tickets with intelligent priority assignment
- Retrieves ticket history for customers
- Analyzes issues to determine priority (high/medium/low)
- Uses MCP tools: `create_ticket`, `get_customer_history`

**Why it's needed**:
- Specialized for support ticket workflows
- Implements business logic for priority assignment
- Separates ticket operations from customer data operations

**Model**: `openai/gpt-4o-mini` (configurable via `SUPPORT_MODEL`)

**Priority Logic**:
- **High**: Login issues, account locks, payment failures, data loss, security
- **Medium**: Bugs, performance issues, billing questions
- **Low**: Feature requests, general questions, minor issues

---

#### `a2a/agent/fallback_sql_generator_agent.py`
**Purpose**: Handles complex SQL queries that standard tools can't handle

**What it does**:
- Generates SQL queries from natural language
- Executes complex queries (pattern matching, aggregations, joins)
- Used only for queries beyond standard REST API capabilities
- Uses MCP tool: `fallback_sql`

**Why it's needed**:
- Handles queries that require complex SQL (e.g., "customers who logged in last month")
- Provides flexibility for ad-hoc analytics
- Complements standard CRUD tools with SQL capabilities

**Model**: `openai/gpt-3.5-turbo` (optimized for SQL generation, configurable via `SQL_GENERATOR_MODEL`)

**Use Cases**:
- Pattern matching: `name LIKE '%pattern%'`
- Date range filtering: `created_at >= date('now','-30 days')`
- Aggregations: `COUNT`, `SUM`, `AVG`
- Complex JOINs and WHERE conditions

---

### MCP Server

#### `customer_mcp/server/mcp_server.py`
**Purpose**: FastMCP server exposing tools via MCP protocol

**What it does**:
- Implements MCP server using FastMCP framework
- Exposes 7 tools via `@mcp.tool()` decorators
- Handles JSON-RPC 2.0 requests over HTTP
- Uses stateless HTTP transport for production scalability
- Runs on configurable host/port (default: localhost:8001)

**Why it's needed**:
- Provides tool discovery and execution via MCP protocol
- Enables agents to dynamically discover and call tools
- Separates tool layer from agent layer
- Follows MCP standard for compatibility

**Configuration**:
- `streamable-http` transport (recommended for HTTP)
- `stateless_http=True`: Each request is independent
- `json_response=True`: Faster than SSE streaming
- Path: `/mcp` for Google ADK compatibility

**Tools Exposed**:
- `get_customer_tool`, `list_customers_tool`, `add_customer_tool`, `update_customer_tool`
- `create_ticket_tool`, `get_customer_history_tool`, `fallback_sql_tool`

**Dependencies**: `mcp.server.fastmcp`, all tool modules

---

### Tool Implementations

#### `customer_mcp/tools/db_utils.py`
**Purpose**: Database connection utilities

**What it does**:
- Provides `get_db_connection()`: Creates SQLite connections
- Initializes WAL (Write-Ahead Logging) mode for concurrent access
- Converts SQLite rows to dictionaries via `row_to_dict()`
- Manages connection lifecycle

**Why it's needed**:
- Centralized database connection management
- WAL mode enables multiple concurrent reads/writes
- Consistent connection configuration across all tools
- Prevents connection leaks with proper cleanup

**Key Features**:
- WAL mode initialization (runs once per process)
- `timeout=5.0`: Prevents indefinite blocking
- `check_same_thread=False`: Allows multi-threaded access
- `row_factory=sqlite3.Row`: Dict-like row access

**WAL Mode Benefits**:
- Multiple readers and one writer can access database simultaneously
- Better performance than default journal mode
- Reduced locking conflicts

---

#### `customer_mcp/tools/get_customer.py`
**Purpose**: Retrieve customer by ID

**What it does**:
- Executes `SELECT * FROM customers WHERE id = ?`
- Returns customer data as dictionary or error message
- Uses parameterized queries to prevent SQL injection

**Why it's needed**:
- Core customer retrieval functionality
- Used by Customer Data Agent
- Demonstrates safe SQL practices with parameterized queries

**Return Format**:
```python
{
    'success': True,
    'customer': {...}  # Customer data dictionary
}
# OR
{
    'success': False,
    'error': 'Customer with ID X not found'
}
```

---

#### `customer_mcp/tools/list_customers.py`
**Purpose**: List customers with optional filtering

**What it does**:
- Lists all customers or filters by status
- Supports optional limit on results
- Returns list of customer dictionaries

**Why it's needed**:
- Enables listing/filtering operations
- Supports pagination via limit parameter
- Demonstrates flexible query building

**Parameters**:
- `status` (optional): Filter by 'active' or 'disabled'
- `limit` (optional): Maximum number of results

---

#### `customer_mcp/tools/add_customer.py`
**Purpose**: Create new customer

**What it does**:
- Inserts new customer into database
- Validates required fields (name)
- Sets defaults for optional fields (status='active')
- Returns created customer data

**Why it's needed**:
- Customer creation functionality
- Validates input data
- Demonstrates INSERT operations

---

#### `customer_mcp/tools/update_customer.py`
**Purpose**: Update existing customer information

**What it does**:
- Updates customer fields (name, email, phone, status)
- Only updates provided fields (partial updates)
- Validates customer exists before update

**Why it's needed**:
- Customer modification functionality
- Supports partial updates
- Demonstrates UPDATE operations with validation

---

#### `customer_mcp/tools/create_ticket.py`
**Purpose**: Create support ticket for customer

**What it does**:
- Validates customer exists
- Creates ticket with issue and priority
- Implements retry logic for database locks
- Returns created ticket data

**Why it's needed**:
- Core ticket creation functionality
- Demonstrates retry logic for concurrent access
- Validates foreign key relationships (customer must exist)

**Key Features**:
- Retry mechanism (max 2 retries, 0.1s delay) for database locks
- Priority validation (low/medium/high)
- Foreign key validation (customer must exist)

---

#### `customer_mcp/tools/get_customer_history.py`
**Purpose**: Get all tickets for a customer

**What it does**:
- Retrieves all tickets associated with customer ID
- Joins with customers table if needed
- Returns list of ticket dictionaries

**Why it's needed**:
- Enables viewing customer ticket history
- Used in multi-step workflows (get customer → get tickets)
- Demonstrates relationship queries

---

#### `customer_mcp/tools/fallback_sql.py`
**Purpose**: Execute custom SQL queries

**What it does**:
- Executes user-provided SQL queries
- Blocks dangerous operations (DROP, DELETE, ALTER, etc.)
- Supports SELECT, INSERT, UPDATE operations
- Returns query results or error messages

**Why it's needed**:
- Handles complex queries beyond standard tools
- Enables ad-hoc analytics and reporting
- Provides flexibility for SQL Generator Agent

**Safety Features**:
- Blocks: `DROP TABLE`, `DELETE FROM`, `TRUNCATE`, `ALTER TABLE`, etc.
- Only allows: SELECT, INSERT, UPDATE
- Input validation and error handling

---

### Database Setup

#### `database/database_setup.py`
**Purpose**: Initialize SQLite database with schema and sample data

**What it does**:
- Creates `customers` and `tickets` tables
- Sets up indexes for performance
- Creates triggers for automatic timestamp updates
- Optionally inserts sample data (15 customers, 25 tickets)
- Runs sample queries for verification

**Why it's needed**:
- One-time database initialization
- Ensures proper schema with constraints
- Provides sample data for testing
- Validates database setup

**Database Schema**:
- `customers`: id, name, email, phone, status, created_at, updated_at
- `tickets`: id, customer_id (FK), issue, status, priority, created_at
- Indexes on email, customer_id, status
- Foreign key constraints with CASCADE delete

**Key Features**:
- Foreign key constraints enabled
- Check constraints for status/priority values
- Automatic timestamp triggers
- Sample data with realistic scenarios

---

## Data Flow & Communication

### 1. User Query Flow

```
User → chatbot.py
     ↓
A2AOrchestrator.process_query()
     ↓
Router Agent (Supervisor) → Returns JSON decision
     ↓
A2AOrchestrator._execute_agent() → Selected Agent
     ↓
Agent → Google ADK Runner → MCP Client
     ↓
HTTP POST to FastMCP Server (/mcp endpoint)
     ↓
FastMCP → Tool Function (e.g., get_customer)
     ↓
Tool → SQLite Database
     ↓
Database → Tool → FastMCP → JSON Response
     ↓
MCP Client → Agent → Runner → Orchestrator
     ↓
Orchestrator → Router Agent (evaluation)
     ↓
If done: Return to user
If not: Repeat with next agent
```

### 2. MCP Protocol Communication

**Request Format (JSON-RPC 2.0)**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_customer",
    "arguments": {
      "customer_id": 1
    }
  }
}
```

**Response Format**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\": true, \"customer\": {...}}"
      }
    ]
  }
}
```

### 3. Agent Coordination Flow

```
Query: "Get customer 5 and create a ticket"

Step 1: Router → {"next_agent": "customer_data", "done": false}
Step 2: Customer Data Agent → Executes get_customer tool → Returns customer data
Step 3: Router → {"next_agent": "support", "done": false, "reason": "Need to create ticket"}
Step 4: Support Agent → Executes create_ticket tool → Returns ticket data
Step 5: Router → {"next_agent": null, "done": true, "reason": "Query complete"}
Step 6: Orchestrator → Aggregates results → Returns to user
```

---

## How Everything Works Together

### Initialization Sequence

1. **Database Setup** (`database_setup.py`):
   - Creates schema, indexes, triggers
   - Optionally loads sample data

2. **Configuration Loading** (`a2a/utils.py`):
   - Loads `.env` file
   - Configures LiteLLM
   - Sets model names and MCP server URL

3. **MCP Server Start** (`customer_mcp/server/mcp_server.py`):
   - FastMCP server starts on port 8001
   - Registers all 7 tools via decorators
   - Ready to accept HTTP requests

4. **Agent Creation** (`a2a/agent/*.py`):
   - Each agent file creates `LlmAgent` instance
   - Agents connect to MCP server via `McpToolset`
   - Agents are imported by orchestrator

5. **Orchestrator Initialization** (`a2a/orchestrator.py`):
   - Creates `A2AOrchestrator` instance
   - Initializes `InMemorySessionService`
   - Maps agent names to agent instances

6. **Chatbot Start** (`chatbot.py`):
   - Creates orchestrator instance
   - Enters chat loop
   - Ready for user queries

### Execution Sequence (Single Query)

1. User types query in chatbot
2. Chatbot calls `orchestrator.process_query()`
3. Orchestrator calls router agent (supervisor)
4. Router analyzes query and returns JSON decision
5. Orchestrator executes selected agent
6. Agent calls MCP tool via Google ADK
7. MCP client sends HTTP POST to FastMCP server
8. FastMCP calls tool function
9. Tool function queries SQLite database
10. Response flows back: Database → Tool → FastMCP → MCP Client → Agent → Orchestrator
11. Orchestrator collects result and asks router again
12. Router evaluates: done or need another agent?
13. If not done, repeat from step 5 with next agent
14. If done, orchestrator aggregates results and returns to chatbot
15. Chatbot displays response to user

---

## Complete Execution Flow

### Example: "Get customer 5 and create a ticket with issue 'Cannot login'"

**Step 1: User Input**
```
User: "Get customer 5 and create a ticket with issue 'Cannot login'"
```

**Step 2: Orchestrator → Router**
```python
# orchestrator.py: _supervisor_decide()
Query sent to router agent:
"Get customer 5 and create a ticket with issue 'Cannot login'"
```

**Step 3: Router Decision**
```json
{
  "next_agent": "customer_data",
  "done": false,
  "reason": "Need customer info first, then create ticket"
}
```

**Step 4: Orchestrator → Customer Data Agent**
```python
# orchestrator.py: _execute_agent()
Agent: customer_data_agent
Session: chat_session_customer_data
Query: "Get customer 5 and create a ticket..."
```

**Step 5: Customer Data Agent → MCP Tool**
```python
# Agent uses get_customer tool
Tool call: get_customer(customer_id=5)
```

**Step 6: MCP Client → FastMCP Server**
```
HTTP POST http://localhost:8001/mcp
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_customer",
    "arguments": {"customer_id": 5}
  }
}
```

**Step 7: FastMCP → Tool Function**
```python
# mcp_server.py: get_customer_tool()
# customer_mcp/tools/get_customer.py: get_customer()
SQL: SELECT * FROM customers WHERE id = 5
```

**Step 8: Database → Response**
```python
# get_customer.py returns:
{
  'success': True,
  'customer': {
    'id': 5,
    'name': 'Charlie Brown',
    'email': 'charlie.brown@email.com',
    ...
  }
}
```

**Step 9: Response → Agent → Orchestrator**
```
FastMCP → MCP Client → Agent → Runner → Orchestrator
Agent response: "Customer 5 is Charlie Brown (charlie.brown@email.com)..."
```

**Step 10: Orchestrator → Router (Evaluation)**
```python
# orchestrator.py: _supervisor_decide()
Previous results sent to router:
"Customer 5: Charlie Brown... Now need to create ticket"
```

**Step 11: Router Decision**
```json
{
  "next_agent": "support",
  "done": false,
  "reason": "Customer retrieved, now create ticket"
}
```

**Step 12: Orchestrator → Support Agent**
```python
# orchestrator.py: _execute_agent()
Agent: support_agent
Session: chat_session_support
Context: Previous customer data included
Query: "Create ticket for customer 5 with issue 'Cannot login'"
```

**Step 13: Support Agent → MCP Tool**
```python
# Agent uses create_ticket tool
Tool call: create_ticket(customer_id=5, issue="Cannot login", priority="high")
# Priority determined by agent based on issue severity
```

**Step 14: MCP Client → FastMCP → Tool**
```python
# customer_mcp/tools/create_ticket.py
SQL: INSERT INTO tickets (customer_id, issue, priority) VALUES (5, 'Cannot login', 'high')
```

**Step 15: Response → Agent → Orchestrator**
```python
{
  'success': True,
  'message': 'Ticket created successfully with ID 26',
  'ticket': {...}
}
```

**Step 16: Orchestrator → Router (Final Evaluation)**
```json
{
  "next_agent": null,
  "done": true,
  "reason": "Customer retrieved and ticket created"
}
```

**Step 17: Orchestrator → User**
```python
# Aggregated response:
"**Customer Data Agent:**
Customer 5: Charlie Brown (charlie.brown@email.com)

**Support Agent:**
Ticket #26 created successfully for customer 5 with issue 'Cannot login' (Priority: high)"
```

**Step 18: Chatbot Display**
```
🤖 Assistant:
   Customer Data Agent:
   Customer 5: Charlie Brown (charlie.brown@email.com)

   Support Agent:
   Ticket #26 created successfully for customer 5 with issue 'Cannot login' (Priority: high)
```

---

## Database Schema

### Customers Table
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'disabled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Tickets Table
```sql
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    issue TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'in_progress', 'resolved')),
    priority TEXT NOT NULL DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
)
```

### Indexes
- `idx_customers_email`: Fast email lookups
- `idx_tickets_customer_id`: Fast customer ticket retrieval
- `idx_tickets_status`: Fast status filtering

### Triggers
- `update_customer_timestamp`: Auto-updates `updated_at` on customer updates

---

## MCP Protocol Implementation

### FastMCP Server Configuration

**Transport**: `streamable-http`
- HTTP POST requests with JSON-RPC 2.0
- Stateless (each request independent)
- JSON responses (not SSE streaming)

**Tool Registration**:
- Uses `@mcp.tool()` decorator
- FastMCP automatically generates tool schemas from function signatures
- Docstrings become tool descriptions

**Protocol Endpoints**:
- `/mcp`: Main endpoint for all MCP requests
- Handles `initialize`, `tools/list`, `tools/call`

### Tool Discovery Flow

1. Agent connects to MCP server
2. MCP client sends `tools/list` request
3. FastMCP returns all registered tools with schemas
4. Agent stores available tools
5. Agent can call tools by name with arguments

---

## Agent Coordination Logic

### Supervisor Architecture Rules

1. **Router Agent (Supervisor)**:
   - Makes ALL routing decisions
   - Evaluates query completeness
   - Returns structured JSON decisions

2. **Orchestrator (Coordinator)**:
   - Calls router for decisions
   - Executes selected agents
   - Collects and passes results
   - Manages session lifecycle

3. **Specialized Agents**:
   - Focus on domain-specific tasks
   - Use MCP tools to perform operations
   - Return results to orchestrator

### Routing Logic Examples

**Simple Query**: "Get customer 1"
- Router → `{"next_agent": "customer_data", "done": false}`
- Customer Data Agent → Executes → Returns customer
- Router → `{"next_agent": null, "done": true}`
- **Result**: Single agent, one iteration

**Multi-Step Query**: "Get customer 5 and their tickets"
- Router → `{"next_agent": "customer_data", "done": false}`
- Customer Data Agent → Returns customer
- Router → `{"next_agent": "support", "done": false, "reason": "Need ticket history"}`
- Support Agent → Returns tickets
- Router → `{"next_agent": null, "done": true}`
- **Result**: Two agents, two iterations

**Complex Query**: "Show customers who created accounts last month"
- Router → `{"next_agent": "sql", "done": false, "reason": "Complex date filtering requires SQL"}`
- SQL Agent → Generates and executes SQL query
- Router → `{"next_agent": null, "done": true}`
- **Result**: SQL agent, one iteration

### Error Handling

- **Agent Errors**: Caught by orchestrator, passed to router for re-evaluation
- **Tool Errors**: Returned as error responses, agent can retry or report
- **Database Errors**: Retry logic in `create_ticket.py` for locks
- **Iteration Limits**: Maximum 5 iterations prevents infinite loops

---

## Key Design Decisions & Rationale

### 1. Why Supervisor Architecture?
- **Flexibility**: Easy to add new agents without changing routing logic
- **Intelligence**: LLM-based routing adapts to query complexity
- **Extensibility**: New agents automatically discovered by router

### 2. Why MCP Protocol?
- **Standard**: Follows official MCP specification
- **Tool Discovery**: Agents dynamically discover available tools
- **Interoperability**: Works with any MCP-compatible client

### 3. Why FastMCP?
- **Recommended**: Official recommended way to build MCP servers
- **Simplified**: Decorator-based tool registration
- **Production-Ready**: Stateless HTTP transport, JSON responses

### 4. Why LiteLLM?
- **Multi-Provider**: Support OpenAI, Gemini, Anthropic, etc.
- **Unified API**: Same interface across providers
- **Flexibility**: Easy model switching without code changes

### 5. Why SQLite with WAL?
- **Embedded**: No separate database server needed
- **Concurrent**: WAL mode enables multiple readers/writers
- **Simple**: Perfect for demo/prototype, easy to migrate to PostgreSQL later

### 6. Why Per-Agent Sessions?
- **Isolation**: Each agent maintains its own conversation context
- **Context Preservation**: Agents remember previous interactions in their domain
- **Google ADK**: Uses Google ADK's built-in session management

---

## Extension Points

### Adding a New Agent

1. Create `a2a/agent/new_agent.py`:
   ```python
   from google.adk.agents import LlmAgent
   from google.adk.tools.mcp_tool import McpToolset
   from a2a.utils import MCP_HTTP_BASE_URL, NEW_AGENT_MODEL
   
   new_agent = LlmAgent(
       model=NEW_AGENT_MODEL,
       name="new_agent",
       tools=[McpToolset(connection_params=...)]
   )
   ```

2. Add to `a2a/orchestrator.py`:
   ```python
   self.agents = {
       ...
       'new_agent': new_agent,
   }
   ```

3. Update router agent instructions in `router_agent.py` to include new agent

### Adding a New Tool

1. Create `customer_mcp/tools/new_tool.py`:
   ```python
   def new_tool(param: str) -> Dict[str, Any]:
       # Implementation
       return {'success': True, ...}
   ```

2. Add to `mcp_server.py`:
   ```python
   @mcp.tool()
   def new_tool_tool(param: str) -> str:
       result = new_tool(param)
       return format_response(result)
   ```

3. Tool automatically discovered by all agents via MCP

---

## Testing & Validation

### Database Testing
```bash
python database/database_setup.py
# Creates schema, optionally loads sample data, runs sample queries
```

### MCP Server Testing
```bash
python customer_mcp/server/mcp_server.py
# Server starts, can test with MCP Inspector
npx @modelcontextprotocol/inspector
# Connect to http://localhost:8001/mcp
```

### End-to-End Testing
```bash
python chatbot.py
# Interactive testing of full system
```

### Configuration Validation
```bash
python a2a/utils.py
# Validates configuration, shows current settings
```

---

## Troubleshooting Guide

### MCP Server Not Starting
- Check port 8001 is available: `lsof -ti :8001`
- Verify `MCP_HTTP_PORT` in `.env`

### Agents Can't Connect to MCP
- Ensure MCP server is running first
- Verify `MCP_HTTP_BASE_URL` matches server URL
- Check network connectivity

### Database Errors
- Run `database_setup.py` to initialize schema
- Check database file permissions
- Verify SQLite is installed

### Model Errors
- Verify API keys in `.env`
- Check model name format (e.g., `openai/gpt-4o-mini`)
- Ensure LiteLLM is installed: `pip install litellm`

---

## Performance Considerations

### Database
- **WAL Mode**: Enables concurrent access
- **Indexes**: Fast lookups on email, customer_id, status
- **Connection Pooling**: Not implemented (SQLite limitation)
- **Retry Logic**: Handles temporary database locks

### MCP Communication
- **Stateless HTTP**: No connection overhead
- **JSON Responses**: Faster than SSE streaming
- **Single Endpoint**: Simplified routing

### Agent Execution
- **Async/Await**: Non-blocking execution
- **Session Reuse**: Google ADK manages session lifecycle
- **Iteration Limits**: Prevents infinite loops

---

## Security Considerations

### SQL Injection Prevention
- **Parameterized Queries**: All tools use `?` placeholders
- **Input Validation**: Tool functions validate required parameters
- **SQL Restrictions**: `fallback_sql` blocks dangerous operations

### API Key Management
- **Environment Variables**: Keys stored in `.env` (not in code)
- **LiteLLM**: Handles API key passing to providers
- **Validation**: Configuration validation before runtime

### Database Access
- **Foreign Keys**: Enforced relationships
- **Check Constraints**: Validates status/priority values
- **WAL Mode**: Prevents data corruption from concurrent access

---

## Conclusion

This project demonstrates a production-ready multi-agent AI system with:

- **Intelligent Routing**: Supervisor pattern with LLM-based decisions
- **Tool Abstraction**: MCP protocol for tool discovery and execution
- **Multi-Provider Support**: LiteLLM enables flexibility
- **Production Features**: Error handling, retry logic, session management
- **Extensibility**: Easy to add agents and tools
- **Documentation**: Comprehensive code and architecture documentation

The architecture separates concerns cleanly:
- **Agents**: Domain logic and tool usage
- **Orchestrator**: Coordination and lifecycle management
- **MCP Server**: Tool abstraction layer
- **Tools**: Database operations and business logic
- **Database**: Data persistence

This design enables the system to handle complex, multi-step queries by coordinating specialized agents, each focusing on their domain expertise.

