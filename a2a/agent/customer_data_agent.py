"""
Customer Data Agent - Handles customer information retrieval and management
Uses MCP server for dynamic tool discovery
"""
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from a2a.utils import MCP_HTTP_BASE_URL, CUSTOMER_DATA_MODEL

customer_data_agent = LlmAgent(
    model=CUSTOMER_DATA_MODEL, # this is the model of the agent
    name="customer_data_agent", # this is the name of the agent
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(url=f"{MCP_HTTP_BASE_URL}/mcp")
        )
    ],
    instruction="""You are a helpful customer management assistant.

YOUR TOOLS:
- get_customer: Get customer details by ID
- list_customers: List/filter customers
- add_customer: Add new customer
- update_customer: Update customer info
- ask_agent: Request help from other agents (A2A coordination)

AGENT-TO-AGENT (A2A) COORDINATION:
When you need ticket information or complex SQL queries, check agent cards to see who can help.
"""
)
