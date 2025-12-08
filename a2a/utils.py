"""
Utilities and Configuration for A2A-MCP System
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import customer_mcp.server.mcp_server
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

# Configure LiteLLM for OpenAI models (if OpenAI API key is present)
if OPENAI_API_KEY:
    try:
        import litellm
        # Set OpenAI API key for LiteLLM
        os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
        # Enable LiteLLM to work with OpenAI models
        litellm.set_verbose = False  # Set to True for debugging
    except ImportError:
        pass  # LiteLLM not installed

# Model Configuration
# Google ADK supports multiple LLM providers via LiteLLM:
# - Gemini models: gemini-1.5-flash, gemini-1.5-pro, gemini-1.5-flash-002
# - OpenAI models via LiteLLM: Use "openai/gpt-4o-mini" format
# - Other providers: anthropic/claude-3-5-sonnet, etc.
ROUTER_MODEL = os.getenv('ROUTER_MODEL', 'openai/gpt-4o-mini')
CUSTOMER_DATA_MODEL = os.getenv('CUSTOMER_DATA_MODEL', 'openai/gpt-4o-mini')
SUPPORT_MODEL = os.getenv('SUPPORT_MODEL', 'openai/gpt-4o-mini')
SQL_GENERATOR_MODEL = os.getenv('SQL_GENERATOR_MODEL', 'openai/gpt-3.5-turbo')

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
    if not OPENAI_API_KEY:
        print("  ⚠️  You need at least one API key:")
        print("     - OPENAI_API_KEY for OpenAI models (https://platform.openai.com/api-keys)")
    print()
    
    try:
        validate_config()
        print("Configuration is valid!")
    except ValueError as e:
        print(f"Configuration errors:")
        print(e)
