"""
Utilities and Configuration for A2A-MCP System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

try:
    load_dotenv()
except (FileNotFoundError, PermissionError) as e:
    print(f"Warning: Could not load .env file ({e}). Using environment variables.")

# MCP Server HTTP Configuration
MCP_HTTP_HOST = os.getenv('MCP_HTTP_HOST', 'localhost')
MCP_HTTP_PORT = int(os.getenv('MCP_HTTP_PORT', '8001'))
MCP_HTTP_BASE_URL = f"http://{MCP_HTTP_HOST}:{MCP_HTTP_PORT}"

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Model Configuration
ROUTER_MODEL = os.getenv('ROUTER_MODEL', 'gpt-4o-mini')
CUSTOMER_DATA_MODEL = os.getenv('CUSTOMER_DATA_MODEL', 'gpt-4o-mini')
SUPPORT_MODEL = os.getenv('SUPPORT_MODEL', 'gpt-4o-mini')
SQL_GENERATOR_MODEL = os.getenv('SQL_GENERATOR_MODEL', 'gpt-3.5-turbo')

# Database Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / 'Database' / 'support.db'

# MCP Tools
MCP_TOOLS = [
    'get_customer',
    'list_customers',
    'add_customer',
    'update_customer',
    'create_ticket',
    'get_customer_history',
    'fallback_sql',
]

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

def get_config_summary() -> dict:
    """Get a summary of current configuration."""
    return {
        "architecture": "HTTP-based MCP server",
        "mcp_server_url": MCP_HTTP_BASE_URL,
        "database": str(DATABASE_PATH),
        "models": {
            "router": ROUTER_MODEL,
            "customer_data": CUSTOMER_DATA_MODEL,
            "support": SUPPORT_MODEL,
            "sql_generator": SQL_GENERATOR_MODEL,
        },
        "tools_available": len(MCP_TOOLS),
    }

if __name__ != "__main__":
    try:
        validate_config()
    except ValueError as e:
        print(f"Configuration Warning: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("  A2A-MCP Configuration")
    print("=" * 60)
    print()
    
    config = get_config_summary()
    
    print("Architecture:")
    print(f"  {config['architecture']}")
    print()
    
    print("MCP Server:")
    print(f"  URL: {config['mcp_server_url']}")
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
    print(f"  OPENAI_API_KEY: {'Set' if OPENAI_API_KEY else 'Not set'}")
    print()
    
    try:
        validate_config()
        print("Configuration is valid!")
    except ValueError as e:
        print(f"Configuration errors:")
        print(e)
