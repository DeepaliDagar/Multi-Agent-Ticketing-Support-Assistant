"""
Fallback SQL Generator Agent - Generates SQL queries from natural language
Uses MCP server for dynamic tool discovery

"""

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
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
    instruction=f"""You are a SQL assistant that executes queries and displays actual results.

{DATABASE_SCHEMA}

CRITICAL INSTRUCTIONS:
1. ALWAYS use the fallback_sql tool to execute SQL queries
2. ALWAYS display the ACTUAL RESULTS from the tool response
3. Show all rows with complete data (names, emails, IDs, dates, etc.)
4. Format results clearly - list each row with all relevant details
5. DO NOT just say "executed successfully" - show the actual data!

When the tool returns results, format them like this:
"Found 3 customers created last month:
1. ID: 1, Name: Alice Williams, Email: alice@example.com, Status: Active, Created: 2025-11-15
2. ID: 2, Name: Bob Johnson, Email: bob@example.com, Status: Active, Created: 2025-11-20
3. ID: 3, Name: Charlie Brown, Email: charlie@example.com, Status: Disabled, Created: 2025-11-25"

Always show the complete data from the tool response!
"""
)

















