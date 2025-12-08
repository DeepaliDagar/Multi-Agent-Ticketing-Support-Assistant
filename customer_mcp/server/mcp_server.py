"""
MCP Server using FastMCP (following official MCP documentation)
Run with: python customer_mcp/server/mcp_server_fastmcp.py

This implementation uses FastMCP, the recommended way to build MCP servers.
Reference: https://modelcontextprotocol.io/docs/develop/build-server
"""
import json
import sys
import os
from pathlib import Path
from typing import Any, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import FastMCP
from mcp.server.fastmcp import FastMCP

# Import tool functions
from customer_mcp.tools.add_customer import add_customer
from customer_mcp.tools.create_ticket import create_ticket
from customer_mcp.tools.fallback_sql import fallback_sql
from customer_mcp.tools.get_customer import get_customer
from customer_mcp.tools.get_customer_history import get_customer_history
from customer_mcp.tools.list_customers import list_customers
from customer_mcp.tools.update_customer import update_customer

# Get configuration from environment
MCP_HTTP_HOST = os.getenv('MCP_HTTP_HOST', 'localhost')
MCP_HTTP_PORT = int(os.getenv('MCP_HTTP_PORT', '8001'))

# Initialize FastMCP server
# Use stateless_http=True and json_response=True for optimal performance
mcp = FastMCP(
    "customer-management-server",
    host=MCP_HTTP_HOST,
    port=MCP_HTTP_PORT,
    streamable_http_path="/mcp",  # Path for Google ADK compatibility
    stateless_http=True,  # Recommended for production
    json_response=True,  # Use JSON responses (faster than SSE streaming)
)


# Helper function to format tool responses as JSON strings
def format_response(result: dict[str, Any]) -> str:
    """Format tool result dictionary as JSON string for FastMCP."""
    return json.dumps(result, indent=2)


# Define tools using @mcp.tool() decorator
# FastMCP automatically generates tool definitions from function signatures and docstrings

@mcp.tool()
def get_customer_tool(customer_id: int) -> str:
    """Retrieve complete customer details by ID including name, email, phone, status, and timestamps.
    
    Args:
        customer_id: The unique ID of the customer
    """
    result = get_customer(customer_id)
    return format_response(result)


@mcp.tool()
def get_customer_history_tool(customer_id: int) -> str:
    """Get all support tickets associated with a customer by their ID.
    
    Args:
        customer_id: The unique ID of the customer
    """
    result = get_customer_history(customer_id)
    return format_response(result)


@mcp.tool()
def list_customers_tool(status: Optional[str] = None, limit: Optional[int] = None) -> str:
    """List customers with optional filtering by status and limit on number of results.
    
    Args:
        status: Filter by customer status (optional) - 'active' or 'disabled'
        limit: Maximum number of customers to return (optional)
    """
    result = list_customers(status=status, limit=limit)
    return format_response(result)


@mcp.tool()
def add_customer_tool(name: str, email: Optional[str] = None, phone: Optional[str] = None, 
                     status: Optional[str] = None) -> str:
    """Create a new customer with name (required) and optional email, phone, and status.
    
    Args:
        name: Customer name (required)
        email: Customer email address (optional)
        phone: Customer phone number (optional)
        status: Customer status - 'active' or 'disabled' (optional, defaults to 'active')
    """
    result = add_customer(name=name, email=email, phone=phone, status=status)
    return format_response(result)


@mcp.tool()
def update_customer_tool(customer_id: int, name: Optional[str] = None, email: Optional[str] = None,
                        phone: Optional[str] = None, status: Optional[str] = None) -> str:
    """Update customer information (name, email, phone, or status) by customer ID.
    
    Args:
        customer_id: The unique ID of the customer to update (required)
        name: New customer name (optional)
        email: New email address (optional)
        phone: New phone number (optional)
        status: New status - 'active' or 'disabled' (optional)
    """
    result = update_customer(customer_id=customer_id, name=name, email=email, phone=phone, status=status)
    return format_response(result)


@mcp.tool()
def create_ticket_tool(customer_id: int, issue: str, priority: str = 'medium') -> str:
    """Create a new ticket for a customer by their ID.
    
    Args:
        customer_id: The unique ID of the customer (required)
        issue: The issue description (required)
        priority: The priority level - 'low', 'medium', or 'high' (optional, defaults to 'medium')
                 LLM should determine based on issue severity:
                 - high: login/access issues, account locked, payment failures, data loss
                 - medium: bugs, performance issues, billing questions
                 - low: feature requests, general questions, minor issues
    """
    result = create_ticket(customer_id=customer_id, issue=issue, priority=priority)
    return format_response(result)


@mcp.tool()
def fallback_sql_tool(sql_query: str) -> str:
    """Execute a SQL query. Supports SELECT, INSERT, and UPDATE operations only.
    
    Args:
        sql_query: SQL query to execute (SELECT, INSERT, or UPDATE only)
    """
    result = fallback_sql(sql_query)
    return format_response(result)


def main():
    """Entry point for the FastMCP server."""
    # Run server with streamable-http transport (recommended for HTTP)
    print(f"🚀 Starting FastMCP server on {MCP_HTTP_HOST}:{MCP_HTTP_PORT}")
    print(f"📡 Server will be available at: http://{MCP_HTTP_HOST}:{MCP_HTTP_PORT}/mcp")
    print(f"🔧 Transport: streamable-http (stateless, JSON responses)")
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
