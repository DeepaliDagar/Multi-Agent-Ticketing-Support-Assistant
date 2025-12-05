"""
MCP Server (HTTP): Exposes customer management tools via HTTP REST API
Run with: python customer_mcp/server/mcp_server.py

This is the main MCP server. Orchestrator and agents call it directly via HTTP.
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import MCP SDK
from mcp.server import Server
from mcp.types import Tool, TextContent
#from mcp.server.streamable_http import StreamableHTTPServerTransport

# Import FastAPI for HTTP server
try:
    from fastapi import FastAPI, Request, Response
    from fastapi.responses import StreamingResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

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

# Define tools (same as STDIO version)
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

# Tool registry mapping tool names to functions
TOOL_REGISTRY = {
    "get_customer": get_customer,
    "get_customer_history": get_customer_history,
    "list_customers": list_customers,
    "add_customer": add_customer,
    "update_customer": update_customer,
    "create_ticket": create_ticket,
    "fallback_sql": fallback_sql,
}

# Register call_tool handler
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """Handle tool execution - dynamically calls tool functions."""
    if name not in TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {name}")
    
    tool_func = TOOL_REGISTRY[name]
    result = tool_func(**arguments)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

# Create FastAPI app
if FASTAPI_AVAILABLE:
    app = FastAPI(title="MCP Server (HTTP)")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "ok", "server": "mcp-http"}
    
    @app.get("/tools")
    async def list_tools_endpoint():
        """List all available tools."""
        tools_list = await handle_list_tools()
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in tools_list
            ]
        }
    
    @app.post("/tools/{tool_name}")
    async def call_tool_endpoint(tool_name: str, request: Request):
        """Call a tool by name with arguments."""
        try:
            body = await request.json()
            arguments = body.get("arguments", {})
            
            # Call the tool handler
            result = await handle_call_tool(tool_name, arguments)
            
            # Extract text content from result
            if result and len(result) > 0:
                text_content = result[0].text if hasattr(result[0], 'text') else str(result[0])
                # Try to parse as JSON, fallback to string
                try:
                    return json.loads(text_content)
                except:
                    return {"result": text_content}
            else:
                return {"result": None}
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

def main():
    """Run the HTTP MCP server."""
    if not FASTAPI_AVAILABLE:
        print("FastAPI and uvicorn are required for HTTP server")
        print("Install with: pip install fastapi uvicorn")
        sys.exit(1)
    
    import os
    port = int(os.getenv("MCP_HTTP_PORT", "8001"))
    host = os.getenv("MCP_HTTP_HOST", "localhost")
    
    print(f" Starting MCP HTTP Server on http://{host}:{port}")
    print(f"   Health: http://{host}:{port}/health")
    print(f"   Tools: http://{host}:{port}/tools")
    print(f"   MCP Endpoint: http://{host}:{port}/mcp")
    
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()

