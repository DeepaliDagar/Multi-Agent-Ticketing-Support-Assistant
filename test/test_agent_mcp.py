"""
Test agents with HTTP-based MCP server
"""
import sys
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from a2a.agent.customer_data_agent import customer_data_agent

MCP_SERVER_URL = "http://localhost:8001"

def check_mcp_server():
    """Check if MCP server is running."""
    try:
        response = requests.get(f"{MCP_SERVER_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def test_customer_data_agent():
    """Test customer data agent with HTTP MCP server"""
    print("=" * 60)
    print("  Testing Customer Data Agent (HTTP MCP Server)")
    print("=" * 60)
    print()
    
    if not check_mcp_server():
        print("Error: MCP server is not running!")
        print(f"   Start it with: python customer_mcp/server/mcp_server.py")
        print(f"   Expected URL: {MCP_SERVER_URL}")
        return
    
    print("MCP Server is running")
    print()
    
    try:
        print("Creating customer_data_agent...")
        agent = customer_data_agent()
        print(f"Agent created: {agent.name}")
        print(f"   Model: {agent.model}")
        print()
        
        print("Testing agent.process()...")
        query = "Get customer with ID 5"
        response = agent.process(query)
        print(f"Response: {response[:200]}...")
        print()
        
        print("Testing with conversation history...")
        history = "User previously asked about customer 3"
        response2 = agent.process("What about customer 5?", conversation_history=history)
        print(f"Response: {response2[:200]}...")
        print()
        
        print("Testing with A2A coordination...")
        other_agents = {"support": "support_agent", "sql": "sql_generator"}
        response3 = agent.process("List all active customers", other_agents=other_agents)
        print(f"Response: {response3[:200]}...")
        print()
        
        print("Customer Data Agent working!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_customer_data_agent()
