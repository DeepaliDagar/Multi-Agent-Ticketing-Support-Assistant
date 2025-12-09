"""
MCP Server using FastMCP (following official MCP documentation)
Run with: python customer_mcp/server/mcp_server_fastmcp.py

This implementation uses FastMCP, the recommended way to build MCP servers.
Reference: https://modelcontextprotocol.io/docs/develop/build-server
"""
import json
import sys
import os
import logging
from pathlib import Path
from typing import Any, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Suppress harmless errors from MCP streamable HTTP cleanup
# These occur when sessions terminate and message routers try to read from closed streams
# They're expected behavior and don't affect functionality

# Custom filter to suppress known harmless errors
class MCPErrorFilter(logging.Filter):
    """Filter out known harmless MCP connection cleanup errors."""
    def filter(self, record):
        # Get the log message
        message = record.getMessage()
        
        # List of harmless error patterns
        harmless_patterns = [
            'ClosedResourceError',
            'Error in message router',
            'Terminating session',
            'receive_nowait',
            'WouldBlock',
            'async generator ignored',
            'CancelledError',
            'Cancelled via cancel scope',
            'Exception in thread',
            '_asyncio_thread_main',
        ]
        
        # Check if message contains any harmless pattern
        if any(pattern in message for pattern in harmless_patterns):
            return False  # Don't log this message
        
        # Also check exception type if available
        if hasattr(record, 'exc_info') and record.exc_info:
            exc_type = record.exc_info[0]
            if exc_type:
                exc_name = exc_type.__name__
                if any(pattern in exc_name for pattern in ['ClosedResourceError', 'CancelledError', 'WouldBlock']):
                    return False
        
        return True  # Log other messages

# Apply comprehensive logging suppression
mcp_loggers = [
    'mcp.server.streamable_http',
    'mcp.server.streamable_http_manager',
    'mcp.server',
    'mcp',
]

for logger_name in mcp_loggers:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.WARNING)  # Suppress INFO/ERROR, keep WARNING+
    logger.addFilter(MCPErrorFilter())  # Add custom filter

# Also suppress anyio and asyncio cleanup errors
logging.getLogger('anyio').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)

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
# Use stateless_http=True for optimal performance
# Note: Setting json_response=False to support SSE mode (required by Google ADK client)
# The client may try to establish SSE connections which require text/event-stream in Accept header
mcp = FastMCP(
    "customer-management-server",
    host=MCP_HTTP_HOST,
    port=MCP_HTTP_PORT,
    streamable_http_path="/mcp",  # Path for Google ADK compatibility
    stateless_http=True,  # Recommended for production
    json_response=False,  # Use SSE mode (required for Google ADK client compatibility)
    log_level="INFO",  # Set to INFO to see connection attempts (change back to WARNING later)
)

# Verify configuration (for debugging)
import sys
if hasattr(mcp, '_settings') and hasattr(mcp._settings, 'json_response'):
    if not mcp._settings.json_response:
        print("⚠️  Warning: json_response was not properly set to True!", file=sys.stderr)
        print("   Server may require text/event-stream in Accept header", file=sys.stderr)


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
    print(f" Starting FastMCP server on {MCP_HTTP_HOST}:{MCP_HTTP_PORT}")
    print(f" Server will be available at: http://{MCP_HTTP_HOST}:{MCP_HTTP_PORT}/mcp")
    print(f" Transport: streamable-http (stateless, SSE mode)")
    print(f"✅ Configuration: json_response=False, stateless_http=True")
    print(f" Note: Using SSE mode for Google ADK client compatibility")
    print(f"   Client must send Accept: application/json, text/event-stream headers")
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
