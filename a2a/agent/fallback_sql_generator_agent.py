"""
Fallback SQL Generator Agent - Generates SQL queries from natural language
Uses MCP server for dynamic tool discovery

"""

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from termcolor import colored
from a2a.utils import MCP_HTTP_BASE_URL, SQL_GENERATOR_MODEL

DATABASE_SCHEMA = """
DATABASE SCHEMA:
- customers (id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT, status TEXT, created_at TIMESTAMP, updated_at TIMESTAMP)
- tickets (id INTEGER PRIMARY KEY, customer_id INTEGER, issue TEXT, status TEXT, priority TEXT, created_at DATETIME)
- Foreign key: tickets.customer_id -> customers.id
"""

# Create the agent
fallback_sql_generator_agent = LlmAgent(
    model=SQL_GENERATOR_MODEL,
    name="fallback_sql_generator_agent",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=f"{MCP_HTTP_BASE_URL}/mcp"
            )
        )
    ],
    instruction=f"""You are a FALLBACK SQL generator assistant.

{DATABASE_SCHEMA}

 IMPORTANT: You should ONLY be used for complex queries that cannot be handled by other agents!

Your task:
1. Convert complex natural language queries into SQL
2. Only give me the SQL query, no other text or explanation
3. Only generate SELECT, INSERT, or UPDATE queries (no DELETE, DROP, CREATE TABLE, etc.)
4. Use proper SQL syntax for SQLite
5. Prefer SIMPLE queries - let other agents handle relationships via A2A coordination
6. AVOID JOINS when possible - customer_data and support agents can coordinate

WHEN TO USE SQL:
Name pattern matching (LIKE 'A%')
Date range filtering (created_at > date(...))
Aggregations (COUNT, SUM, AVG)
Complex WHERE conditions and joins

WHEN NOT TO USE SQL (other agents handle these):
Get customer by ID → customer_data agent
Customer + tickets → customer_data + support agents via A2A

Examples of what YOU should handle:
- "Find customers whose name starts with 'A'" → SELECT * FROM customers WHERE name LIKE 'A%'
- "Get customers created in last 30 days" → SELECT * FROM customers WHERE created_at >= date('now','-30 days')
- "Count tickets by priority" → SELECT priority, COUNT(*) FROM tickets GROUP BY priority
"""
)

print(colored("✅ Agent created successfully!", "green", attrs=["bold"]))
print()
print(colored("Agent Details:", "cyan"))
print(f"   Name: {fallback_sql_generator_agent.name}")
print(f"   Model: {SQL_GENERATOR_MODEL}")
print(f"   Tools: MCPToolSet connected to {MCP_HTTP_BASE_URL}/mcp")
print()
print(colored("💡 The agent can now use all SQL generator tools!", "yellow"))
















