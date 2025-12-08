# A2A-MCP: Multi-Agent Customer Support System

A production-ready multi-agent customer support system featuring Google ADK, FastMCP server, intelligent agent routing, and an interactive chatbot interface.

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv genaienv
source genaienv/bin/activate  # On Windows: genaienv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Setup Database

```bash
python database/database_setup.py
```

### 3. Configure Environment

Create a `.env` file:

```bash
# API Keys
OPENAI_API_KEY=your_openai_api_key_here

# MCP Server Configuration (optional)
MCP_HTTP_HOST=localhost
MCP_HTTP_PORT=8001

# Model Configuration (optional)
ROUTER_MODEL=openai/gpt-4o-mini
CUSTOMER_DATA_MODEL=openai/gpt-4o-mini
SUPPORT_MODEL=openai/gpt-4o-mini
SQL_GENERATOR_MODEL=openai/gpt-3.5-turbo
```

### 4. Start MCP Server

```bash
python customer_mcp/server/mcp_server.py
```

The server will start on `http://localhost:8001/mcp`

### 5. Run Chatbot

In a new terminal:

```bash
python chatbot.py
```

## Architecture Overview

```
User Query → Orchestrator → Router Agent (Supervisor)
                              ↓
                         Routing Decision
                              ↓
                   Specialized Agents (Customer/Support/SQL)
                              ↓
                         MCP Tools
                              ↓
                        SQLite Database
```

### Key Components

- **A2A Orchestrator**: Coordinates multi-agent execution
- **Router Agent (Supervisor)**: Makes intelligent routing decisions
- **Specialized Agents**: Customer Data, Support, SQL Generator
- **FastMCP Server**: Exposes tools via MCP protocol
- **SQLite Database**: Customer and ticket data storage

## 🤖 Agents

- **Router Agent**: Supervisor that routes queries to appropriate agents
- **Customer Data Agent**: Customer information management (CRUD operations)
- **Support Agent**: Support ticket creation and management
- **SQL Generator Agent**: Handles complex SQL queries for advanced analytics

### Agent Architecture Notes

**LLM Backend**: All agents use LLM backends (GPT-4o-mini, GPT-3.5-turbo) for intelligent decision-making:
- Router Agent uses LLM to analyze queries and make routing decisions
- Customer Data, Support, and SQL Agents use LLMs to understand user intent and execute appropriate tools
- LLMs process natural language queries and generate structured responses

**MCP Server Integration**: Agents connect directly to the MCP server, not Python functions:
- All agents use `McpToolset` with `StreamableHTTPConnectionParams` to connect to FastMCP server
- Tools are discovered dynamically via MCP protocol (`tools/list`)
- Tool calls are made through MCP protocol (`tools/call`) over HTTP
- Agents do not import or call Python tool functions directly - all communication is via MCP

**A2A Support**: Agent-to-Agent (A2A) coordination is built into Google ADK:
- No custom A2A classes needed - Google ADK provides native A2A capabilities
- The orchestrator uses Google ADK's `Runner` and `InMemorySessionService` for agent coordination
- Agents can coordinate through ADK's built-in mechanisms and session management

## MCP Tools

7+ tools exposed via FastMCP server:

**Customer Management:**
- `get_customer` - Retrieve customer by ID
- `list_customers` - List customers with optional filtering
- `add_customer` - Create new customer
- `update_customer` - Update customer information

**Support Tickets:**
- `create_ticket` - Create support ticket with priority assignment
- `get_customer_history` - Get all tickets for a customer

**Database:**
- `fallback_sql` - Execute custom SQL queries (SELECT, INSERT, UPDATE only)

## Documentation

For comprehensive documentation including:
- File-by-file breakdown
- Complete execution flows
- Technical implementation details
- Design decisions and rationale

See **[PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)**

## MCP Inspector

Test the MCP server using the MCP Inspector:

```bash
# Start MCP server first
python customer_mcp/server/mcp_server.py

# In another terminal
npx @modelcontextprotocol/inspector
```

- Select transport: **HTTP**
- Enter server URL: `http://localhost:8001/mcp`
- Click "Connect"

## Usage Examples

### Chatbot Interface

```bash
python chatbot.py
```

Example queries:
- "Get customer 1"
- "Show me all active customers"
- "Create a ticket for customer 5 with issue 'Cannot login'"
- "Get customer 3 and their tickets"
- "Show customers who created accounts last month"

### Using Orchestrator Directly

```python
from a2a.orchestrator import process
import asyncio

async def main():
    response = await process("Get customer 1", thread_id="my_session")
    print(response)

asyncio.run(main())
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `MCP_HTTP_HOST` | MCP server host | `localhost` |
| `MCP_HTTP_PORT` | MCP server port | `8001` |
| `ROUTER_MODEL` | Model for router agent | `openai/gpt-4o-mini` |
| `CUSTOMER_DATA_MODEL` | Model for customer agent | `openai/gpt-4o-mini` |
| `SUPPORT_MODEL` | Model for support agent | `openai/gpt-4o-mini` |
| `SQL_GENERATOR_MODEL` | Model for SQL agent | `openai/gpt-3.5-turbo` |

### Model Configuration

The system uses LiteLLM for multi-provider LLM support:

- **OpenAI models**: `openai/gpt-4o-mini`, `openai/gpt-4o`, `openai/gpt-3.5-turbo`
- **Gemini models**: `gemini-1.5-flash`, `gemini-1.5-pro`
- **Other providers**: `anthropic/claude-3-5-sonnet`, etc.

## How It Works

### Supervisor Agent Architecture

The system implements a **Supervisor Agent Architecture**:

1. **User Query** → Orchestrator receives query
2. **Router Decision** → Router Agent (Supervisor) analyzes and routes to appropriate agent
3. **Agent Execution** → Selected agent processes query using MCP tools
4. **Evaluation** → Router evaluates if query is complete or needs another agent
5. **Iteration** → Steps 2-4 repeat until query is fully answered
6. **Response** → Orchestrator combines results and returns to user

### Example Flow

```
User: "Get customer 1 and create a ticket"

1. Router → Routes to customer_data agent
2. Customer Agent → Gets customer 1 details
3. Router → Evaluates: Need to create ticket
4. Router → Routes to support agent  
5. Support Agent → Creates ticket for customer 1
6. Router → Evaluates: Query complete
7. Response → Combined result returned
```

For detailed execution flows and technical deep dives, see [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md).

## Troubleshooting

### MCP Server Issues

**Port already in use:**
```bash
lsof -ti :8001 | xargs kill -9
```

**Connection errors:**
- Ensure server is running: `python customer_mcp/server/mcp_server.py`
- Check port configuration in `.env`
- Verify `MCP_HTTP_BASE_URL` matches server address

### Agent/Orchestrator Issues

**"Model not found" errors:**
- Ensure API key is set in `.env`
- Check model name format: `openai/gpt-4o-mini` (with prefix)
- Verify LiteLLM is installed: `pip install litellm`

**Database errors:**
- Run database setup: `python database/database_setup.py`
- Check database file permissions

### API Key Issues

- Verify `OPENAI_API_KEY` is set in `.env`
- Check API key is valid
- Ensure LiteLLM is configured correctly

## Project Structure

```
googleadk/
├── a2a/                          # Agent system
│   ├── agent/                    # Individual agents
│   │   ├── router_agent.py      # Router/supervisor agent
│   │   ├── customer_data_agent.py
│   │   ├── support_agent.py
│   │   └── fallback_sql_generator_agent.py
│   ├── orchestrator.py          # Supervisor orchestrator
│   └── utils.py                 # Configuration & utilities
├── customer_mcp/                # MCP server
│   ├── server/
│   │   └── mcp_server.py       # FastMCP server
│   └── tools/                   # MCP tool implementations
├── database/                    # Database setup
│   └── database_setup.py
├── chatbot.py                   # Interactive chatbot interface
├── requirements.txt             # Python dependencies
├── README.md                    # This file (high-level overview)
└── PROJECT_DOCUMENTATION.md     # Comprehensive documentation
```

## References

- [MCP Documentation](https://modelcontextprotocol.io/docs/develop/build-server)
- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [FastMCP Guide](https://modelcontextprotocol.io/docs/develop/build-server)


---

**Built with**: Google ADK, FastMCP, LiteLLM, SQLite, Python

**For detailed technical documentation**, see [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)
