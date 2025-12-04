"""
MCP Server: Exposes customer management tools via Model Context Protocol
Run with inspector: npx @modelcontextprotocol/inspector python customer_mcp/server/mcp_server.py
"""
import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import MCP SDK (from site-packages)
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Import our tools
from customer_mcp.tools.get_customer import get_customer
from customer_mcp.tools.get_customer_history import get_customer_history  
from customer_mcp.tools.list_customers import list_customers
from customer_mcp.tools.add_customer import add_customer
from customer_mcp.tools.update_customer import update_customer
from customer_mcp.tools.create_ticket import create_ticket
from customer_mcp.tools.fallback_sql import fallback_sql

# Create server instance
server = Server("customer-support-mcp")

# Define tools
TOOLS = [
    Tool(
        name="get_customer",
        description="Retrieve complete customer details by ID including name, email, phone, status, and timestamps",
        inputSchema={
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "integer",
                    "description": "The unique ID of the customer"
                }
            },
            "required": ["customer_id"]
        }
    ),
    Tool(
        name="get_customer_history",
        description="Get all support tickets associated with a customer by their ID",
        inputSchema={
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "integer",
                    "description": "The unique ID of the customer"
                }
            },
            "required": ["customer_id"]
        }
    ),
    Tool(
        name="list_customers",
        description="List customers with optional filtering by status and limit on number of results",
        inputSchema={
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["active", "disabled"],
                    "description": "Filter by customer status (optional)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of customers to return (optional)"
                }
            }
        }
    ),
    Tool(
        name="add_customer",
        description="Create a new customer with name (required) and optional email, phone, and status",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Customer name (required)"
                },
                "email": {
                    "type": "string",
                    "description": "Customer email address (optional)"
                },
                "phone": {
                    "type": "string",
                    "description": "Customer phone number (optional)"
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "disabled"],
                    "description": "Customer status (optional, defaults to 'active')"
                }
            },
            "required": ["name"]
        }
    ),
    Tool(
        name="update_customer",
        description="Update customer information (name, email, phone, or status) by customer ID",
        inputSchema={
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "integer",
                    "description": "The unique ID of the customer to update"
                },
                "name": {
                    "type": "string",
                    "description": "New customer name (optional)"
                },
                "email": {
                    "type": "string",
                    "description": "New email address (optional)"
                },
                "phone": {
                    "type": "string",
                    "description": "New phone number (optional)"
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "disabled"],
                    "description": "New status (optional)"
                }
            },
            "required": ["customer_id"]
        }
    ),
    Tool(
        #Tool for creating a new ticket for a customer
        name="create_ticket",
        description="Create a new ticket for a customer by their ID",
        inputSchema={
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "integer",
                    "description": "The unique ID of the customer"
                },
                "issue": {
                    "type": "string",
                    "description": "The issue of the ticket"
                },
                "priority": {
                    "type": "string",
                    "description": "The priority of the ticket"
                }
            },
            "required": ["customer_id", "issue", "priority"]
        }
    ),
    Tool(
        name="fallback_sql",
        description="Execute a SQL query. Supports SELECT, INSERT, and UPDATE operations only",
        inputSchema={
            "type": "object",
            "properties": {
                "sql_query": {
                    "type": "string",
                    "description": "SQL query to execute (SELECT, INSERT, or UPDATE only)"
                }
            },
            "required": ["sql_query"]
        }
    ),
]

# Register list_tools handler
@server.list_tools()
async def handle_list_tools():
    """List available tools."""
    return TOOLS

# Register call_tool handler
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """Handle tool execution."""
    
    if name == "get_customer":
        result = get_customer(arguments["customer_id"])
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_customer_history":
        result = get_customer_history(arguments["customer_id"])
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "list_customers":
        result = list_customers(
            status=arguments.get("status"),
            limit=arguments.get("limit")
        )
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "add_customer":
        result = add_customer(
            name=arguments["name"],
            email=arguments.get("email"),
            phone=arguments.get("phone"),
            status=arguments.get("status")
        )
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "update_customer":
        result = update_customer(
            customer_id=arguments["customer_id"],
            name=arguments.get("name"),
            email=arguments.get("email"),
            phone=arguments.get("phone"),
            status=arguments.get("status")
        )
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "create_ticket":
        result = create_ticket(
            customer_id=arguments["customer_id"],
            issue=arguments["issue"],
            priority=arguments["priority"]
        )
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "fallback_sql":
        result = fallback_sql(arguments["sql_query"])
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

# Main entry point
async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
