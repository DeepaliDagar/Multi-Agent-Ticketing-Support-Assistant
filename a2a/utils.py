"""
Utilities and Configuration for A2A-MCP System
"""
import os
from dotenv import load_dotenv

# Try to load .env, but don't fail if it doesn't exist or has permission issues
try:
    load_dotenv()
except (FileNotFoundError, PermissionError) as e:
    print(f"⚠️  Warning: Could not load .env file ({e}). Using environment variables.")

# MCP Server Configuration

# Note: MCP Server is kept ONLY for testing with MCP Inspector
# Agents call tools directly as Python functions (no network calls)

# MCP Server for testing with MCP Inspector and agent to know which tools are available
MCP_SERVER_HOST = os.getenv('MCP_SERVER_HOST', 'localhost')
MCP_SERVER_PORT = os.getenv('MCP_SERVER_PORT', '8000')


# API Keys

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


# Model Configuration

# Router Model (fast classification)
ROUTER_MODEL = os.getenv('ROUTER_MODEL', 'gpt-4o-mini')

# Agent Models
CUSTOMER_DATA_MODEL = os.getenv('CUSTOMER_DATA_MODEL', 'gpt-4o-mini')
SUPPORT_MODEL = os.getenv('SUPPORT_MODEL', 'gpt-4o-mini')
SQL_GENERATOR_MODEL = os.getenv('SQL_GENERATOR_MODEL', 'gpt-4o') # good for complex queries


# Database Configuration

from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / 'Database' / 'support.db'


# MCP Tools Configuration

# Available MCP tools
MCP_TOOLS = [
    'get_customer',
    'list_customers',
    'add_customer',
    'update_customer',
    'create_ticket',
    'get_customer_history',
    'fallback_sql',
]


# Validation

def validate_config():
    """Validate that all required configuration is present."""
    errors = []
    
    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY not set in .env")
    
    if not DATABASE_PATH.exists():
        errors.append(f"Database not found at {DATABASE_PATH}")
    
    if errors:
        raise ValueError(
            "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
        )
    
    return True


# Helper Functions

def get_config_summary() -> dict:
    """Get a summary of current configuration."""
    return {
        "architecture": "Direct tool imports (no HTTP)",
        "mcp_server_for_testing": f"{MCP_SERVER_HOST}:{MCP_SERVER_PORT}",
        "database": str(DATABASE_PATH),
        "models": {
            "router": ROUTER_MODEL,
            "customer_data": CUSTOMER_DATA_MODEL,
            "support": SUPPORT_MODEL,
            "sql_generator": SQL_GENERATOR_MODEL,
        },
        "tools_available": len(MCP_TOOLS),
    }


# Auto-validate on import

if __name__ != "__main__":
    # Only validate when imported, not when run directly
    try:
        validate_config()
    except ValueError as e:
        print(f"⚠️  Configuration Warning: {e}")


# CLI for testing

if __name__ == "__main__":
    print("=" * 60)
    print("  A2A-MCP Configuration")
    print("=" * 60)
    print()
    
    config = get_config_summary()
    
    print("Architecture:")
    print(f"  {config['architecture']}")
    print()
    
    print("MCP Server (Testing Only):")
    print(f"  Endpoint: {config['mcp_server_for_testing']}")
    print(f"  Purpose: MCP Inspector testing")
    print()
    
    print("Database:")
    print(f"  Path: {config['database']}")
    print(f"  Exists: {DATABASE_PATH.exists()}")
    print()
    
    print("Models:")
    for agent, model in config['models'].items():
        print(f"  {agent}: {model}")
    print()
    
    print("MCP Tools:")
    print(f"  Available: {config['tools_available']} tools")
    for tool in MCP_TOOLS:
        print(f"    - {tool}")
    print()
    
    print("Environment:")
    print(f"  OPENAI_API_KEY: {'✅ Set' if OPENAI_API_KEY else '❌ Not set'}")
    print()
    
    # Validate
    try:
        validate_config()
        print("✅ Configuration is valid!")
    except ValueError as e:
        print(f"❌ Configuration errors:")
        print(e)

