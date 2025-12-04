"""
Simplified MCP Client: Dynamic Tool Discovery Without Hardcoding
Discovers tools from MCP registry and calls them directly
This is like a wrapper for the MCP Server
"""
import sys
import os
from pathlib import Path
import importlib
from typing import List, Dict, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# MCP Tool Registry: Central source of truth
MCP_TOOLS_REGISTRY = {
    "get_customer": {
        "module": "customer_mcp.tools.get_customer",
        "function": "get_customer",
        "description": "Retrieves details for a specific customer by their ID",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "integer",
                    "description": "The ID of the customer"
                }
            },
            "required": ["customer_id"]
        }
    },
    "list_customers": {
        "module": "customer_mcp.tools.list_customers",
        "function": "list_customers",
        "description": "Lists customers, optionally filtered by status or limited by count",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["active", "disabled", "all"],
                    "description": "Filter by customer status"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of customers to return"
                }
            }
        }
    },
    "add_customer": {
        "module": "customer_mcp.tools.add_customer",
        "function": "add_customer",
        "description": "Adds a new customer to the database",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the new customer"},
                "email": {"type": "string", "description": "Email of the new customer"},
                "phone": {"type": "string", "description": "Phone number"},
                "status": {
                    "type": "string",
                    "enum": ["active", "disabled"],
                    "description": "Initial status"
                }
            },
            "required": ["name", "email"]
        }
    },
    "update_customer": {
        "module": "customer_mcp.tools.update_customer",
        "function": "update_customer",
        "description": "Updates existing customer information by ID",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "integer", "description": "Customer ID to update"},
                "name": {"type": "string", "description": "New name"},
                "email": {"type": "string", "description": "New email"},
                "phone": {"type": "string", "description": "New phone"},
                "status": {
                    "type": "string",
                    "enum": ["active", "disabled"],
                    "description": "New status"
                }
            },
            "required": ["customer_id"]
        }
    },
    "create_ticket": {
        "module": "customer_mcp.tools.create_ticket",
        "function": "create_ticket",
        "description": "Creates a new support ticket for a customer. Automatically determine priority based on issue severity.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "integer", "description": "Customer ID"},
                "issue": {"type": "string", "description": "Description of the issue"},
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Priority level based on issue severity. HIGH: login/access issues, account locked, payment failures, data loss. MEDIUM: bugs, performance issues, billing questions. LOW: feature requests, general questions, minor issues. If not specified, defaults to medium."
                }
            },
            "required": ["customer_id", "issue"]
        }
    },
    "get_customer_history": {
        "module": "customer_mcp.tools.get_customer_history",
        "function": "get_customer_history",
        "description": "Retrieves the support ticket history for a given customer",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "integer", "description": "Customer ID"}
            },
            "required": ["customer_id"]
        }
    },
    "fallback_sql": {
        "module": "customer_mcp.tools.fallback_sql",
        "function": "fallback_sql",
        "description": "Executes a generated SQL query (SELECT, INSERT, UPDATE) against the database",
        "parameters": {
            "type": "object",
            "properties": {
                "sql_query": {
                    "type": "string",
                    "description": "The SQL query to execute. Only SELECT, INSERT, UPDATE allowed."
                }
            },
            "required": ["sql_query"]
        }
    }
}


class MCPClient:
    """
    Simplified MCP Client: Dynamic Tool Discovery Without Hardcoding
    Discovers tools from MCP registry and calls them directly
    This is like a wrapper for the MCP Server
    
    Benefits:
    - No hardcoded tools in agents
    - Dynamic tool discovery from MCP registry
    - Direct Python function calls
    """
    
    def __init__(self):
        self._tool_cache = {}  # Cache imported functions for faster access     
        # for_agent is like a filter to only get tools for a specific agent
    def list_tools(self, for_agent: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all available tools from MCP registry.
        
        Args:
            for_agent: Optional agent name to filter tools
                      (e.g., 'customer_data' gets customer tools only)
        
        Returns:
            List of tool definitions in OpenAI function calling format
        """
        tools = []
        
        for tool_name, tool_info in MCP_TOOLS_REGISTRY.items():
            # Filter by agent if specified
            if for_agent:
                if for_agent == "customer_data" and tool_name not in [
                    "get_customer", "list_customers", "add_customer", "update_customer"
                ]:
                    continue
                elif for_agent == "support" and tool_name not in [
                    "create_ticket", "get_customer_history"
                ]:
                    continue
                elif for_agent == "sql" and tool_name != "fallback_sql":
                    continue
            
            # Convert to OpenAI function format
            tools.append({
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_info["description"],
                    "parameters": tool_info["parameters"]
                }
            })
        
        return tools
    
    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Call a tool by name with given arguments.
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Arguments to pass to the tool
        
        Returns:
            Tool execution result
        """
        if tool_name not in MCP_TOOLS_REGISTRY:
            return {"error": f"Unknown tool: {tool_name}"}
        
        # Get tool info
        tool_info = MCP_TOOLS_REGISTRY[tool_name]
        
        # Import function if not cached
        if tool_name not in self._tool_cache:
            try:
                module = importlib.import_module(tool_info["module"])
                function = getattr(module, tool_info["function"])
                self._tool_cache[tool_name] = function
            except Exception as e:
                return {"error": f"Failed to import tool {tool_name}: {str(e)}"}
        
        # Call the function
        try:
            func = self._tool_cache[tool_name]
            result = func(**kwargs)
            return result
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        return MCP_TOOLS_REGISTRY.get(tool_name)
    
    def get_all_tool_names(self) -> List[str]:
        """Get list of all available tool names."""
        return list(MCP_TOOLS_REGISTRY.keys())


# Global client instance
_global_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """Get or create the global MCP client instance."""
    global _global_client
    if _global_client is None:
        _global_client = MCPClient()
    return _global_client


# Convenience functions
def list_mcp_tools(for_agent: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all available MCP tools."""
    return get_mcp_client().list_tools(for_agent=for_agent)


def call_mcp_tool(tool_name: str, **kwargs) -> Any:
    """Call an MCP tool by name."""
    return get_mcp_client().call_tool(tool_name, **kwargs)


if __name__ == "__main__":
    # Test the MCP client
    print("=" * 70)
    print("  MCP Client Test")
    print("=" * 70)
    
    client = get_mcp_client()
    
    print("\n -> All Available Tools:")
    all_tools = client.get_all_tool_names()
    for tool in all_tools:
        print(f"  • {tool}")
    
    print("\n -> Customer Data Agent Tools:")
    customer_tools = client.list_tools(for_agent="customer_data")
    for tool in customer_tools:
        print(f"  • {tool['function']['name']}: {tool['function']['description']}")
    
    print("\n -> Support Agent Tools:")
    support_tools = client.list_tools(for_agent="support")
    for tool in support_tools:
        print(f"  • {tool['function']['name']}: {tool['function']['description']}")
    
    print("\n Testing Tool Call:")
    print("Calling: list_customers(limit=3)")
    result = client.call_tool("list_customers", limit=3)
    print(f"Result: {result}")
    
    print("\n✅ MCP Client working!")

