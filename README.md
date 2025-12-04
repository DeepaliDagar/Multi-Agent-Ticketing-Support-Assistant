# A2A-MCP: Agent-to-Agent with Model Context Protocol

A multi-agent customer support system with React UI, Flask backend, LangGraph orchestration, and dynamic MCP tool discovery.

---

## Quick Start

### 1. Setup Environment

```bash
# Activate virtual environment
source xyz/bin/activate  #xyz -> virtual env name

# Install Python dependencies
pip install -r requirements.txt

# Install React dependencies #only needed for UI
cd react 
npm install
cd ..
```

### 2. Configure Environment

Create a `.env` file in the root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Start the System

**Backend (Terminal 1):**
```bash
source xyz/bin/activate
export OPENAI_API_KEY='your-key-here'
python backend_api.py
```
Runs on: http://localhost:8000

**Frontend (Terminal 2):**
```bash
cd react
npm start
```
Opens at: http://localhost:3000

---

## Project Structure

```
A2A-MCP/
├── backend_api.py                    # Flask REST API server
├── requirements.txt                  # Python dependencies
├── .env                              # API keys (gitignored)
│
├── react/                            # React Frontend
│   ├── src/
│   │   ├── App.js                    # Main component
│   │   ├── components/               # UI components
│   │   └── services/api.js           # Backend API calls
│   └── package.json                  # React dependencies
│
├── a2a/                              # Agent System
│   ├── mcp_client.py                 # MCP client (dynamic tool discovery)
│   ├── langgraph_orchestrator.py    # Main orchestrator
│   ├── a2a_logger.py                 # A2A communication logger
│   ├── agent_card.py                 # Agent registry
│   ├── utils.py                      # Configuration
│   └── agent/
│       ├── router_agent.py           # Routes queries
│       ├── customer_data_agent.py    # Customer operations
│       ├── support_agent.py          # Support/tickets
│       └── fallback_sql_generator_agent.py  # SQL generation
│
├── customer_mcp/                     # MCP Tools & Server
│   ├── server/
│   │   └── mcp_server.py             # MCP server (for testing)
│   ├── tools/
│   │   ├── db_utils.py               # Database utilities
│   │   ├── get_customer.py           # Get customer by ID
│   │   ├── list_customers.py         # List/filter customers
│   │   ├── add_customer.py           # Add new customer
│   │   ├── update_customer.py        # Update customer
│   │   ├── create_ticket.py          # Create ticket
│   │   ├── get_customer_history.py   # Get history
│   │   └── fallback_sql.py           # Custom SQL
│   └── data/
│       └── customers.db              # SQLite database
│
└── local testing files/              # Tests & documentation (gitignored)
```

---

## Features

### Flask Backend API
- REST API endpoints
- CORS enabled
- Integrates with orchestrator
- A2A logging

### LangGraph Orchestration
- Smart routing
- A2A coordination
- Conversation memory
- Multi-turn support and negotiation

### Three Specialized Agents
The idea is to use customer data agent (Retrieves customer information
Updates customer records, Handles data validation) or Support Agent (Handles general customer support queries, Can escalate complex issues, Requests customer context from Data Agent, Provides solutions and recommendations)
If both are not capable of giving any solution, fallback is a sql generating agent. This agent doesnt allow delete, remove or dangerous queries.

1. **Customer Data Agent** (`customer_data`)
   - Get/list/add/update customers
   - Uses MCP client for dynamic tool discovery

2. **Support Agent** (`support`)
   - Create tickets
   - Get customer history
   - Uses MCP client for dynamic tool discovery

3. **SQL Generator Agent** (`sql`)
   - Complex queries
   - Pattern matching
   - Date filtering
   - Uses MCP client for dynamic tool discovery

### Dynamic MCP Tool Discovery
- Agents use MCP client (wrapper for MCP Server) to discover tools

---

## Architecture

```
User Browser (port 3000)
    ↓ HTTP POST /chat
React UI
    ↓ axios
Flask Backend (port 8000)
    ↓ Python
LangGraph Orchestrator
    ↓ Routes query
Agents (customer_data, support, sql)
    ↓ Uses MCP Client
MCP Server (dynamic tool discovery)
    ↓ Executes tools
SQLite Database (customers.db)
```

---

## Usage Examples

### Using the React UI

1. Start backend and frontend (see Quick Start)
2. Open http://localhost:3000
3. Try example queries:
   - "Get customer 3"
   - "Show me open tickets"
   - "Customer 5 with complete ticket history" (A2A coordination!)

### Programmatic Usage

```python
from a2a.langgraph_orchestrator import LangGraphOrchestrator

# Create orchestrator
orch = LangGraphOrchestrator()

# Process queries with memory
result = orch.process(
    "Show me all active customers",
    thread_id="user123"
)
print(result['response'])

# Follow-up with context
result = orch.process(
    "Create a ticket for customer 5",
    thread_id="user123"
)
print(result['response'])
```

---

## Testing

Tests are in `local testing files/test/` directory.

### Test with MCP Inspector

```bash
# Optional: Test tools with MCP Inspector (Good way to visualize and make sure tools are working)
npx @modelcontextprotocol/inspector python customer_mcp/server/mcp_server.py
```

---

## Configuration

### Backend Port
Default: 8000 (change in `backend_api.py`)

### Frontend Port
Default: 3000 (change with `PORT=3001 npm start`)

### Agent Models
Configure in `a2a/utils.py`:
```python
ROUTER_MODEL = "gpt-4o-mini"
CUSTOMER_DATA_MODEL = "gpt-4o-mini"
SUPPORT_MODEL = "gpt-4o-mini"
SQL_GENERATOR_MODEL = "gpt-4o" #good for generating sql queries
```

### Thread Management
Each conversation has a unique thread ID for memory:
```python
# Different users
orch.process("Query", thread_id="user_alice")
orch.process("Query", thread_id="user_bob")
```

---

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is available
lsof -ti:8000 | xargs kill -9

# Verify API key is set
echo $OPENAI_API_KEY
```

### Database 
Database is at: `customer_mcp/data/customers.db`

---

## Key Concepts

### **MCP (Model Context Protocol)**
- Agents discover tools dynamically from MCP server
- No hardcoded tool definitions
- Clean separation between tools and agents

### **A2A (Agent-to-Agent)**
- Agents can request help from other agents
- Example: customer_data agent asks support agent for ticket history
- Logged in real-time for debugging

### **LangGraph**
- Orchestrates agent execution
- Manages conversation memory
- Enables multi-turn conversations

---

## Resources

- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **OpenAI API**: https://platform.openai.com/docs/

---

## What's Included

- React chatbot UI
- Flask REST API backend
- LangGraph orchestrator
- 3 specialized agents with A2A coordination
- Dynamic MCP tool discovery
- 7 MCP tools (customer + ticket operations)
- SQLite database
- Conversation memory
- A2A logging and visualization

---

## Next Steps

1. Start the backend: `python backend_api.py`
2. Start the frontend: `cd react && npm start`
3. Open browser: http://localhost:3000
4. Try queries and watch A2A coordination!

---
