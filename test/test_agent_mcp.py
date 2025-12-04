"""
Test agents with direct tool imports
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from a2a.agent.customer_data_agent import create_customer_data_agent

def test_customer_data_agent():
    """Test customer data agent with direct tool imports"""
    print("=" * 60)
    print("  Testing Customer Data Agent (Direct Imports)")
    print("=" * 60)
    print()
    
    try:
        # Create agent
        print("Creating customer_data_agent...")
        agent = create_customer_data_agent()
        print(f"✅ Agent created: {agent.name}")
        print(f"   Model: {agent.model}")
        print()
        
        # Test agent processing
        print("Testing agent.process()...")
        query = "Get customer with ID 5"
        response = agent.process(query)
        print(f"Response: {response}")
        print()
        
        # Test with conversation history
        print("Testing with conversation history...")
        history = "User previously asked about customer 3"
        response2 = agent.process("What about customer 5?", conversation_history=history)
        print(f"Response: {response2}")
        print()
        
        # Test with A2A coordination
        print("Testing with A2A coordination...")
        other_agents = {"support": "support_agent", "sql": "sql_generator"}
        response3 = agent.process("List all active customers", other_agents=other_agents)
        print(f"Response: {response3}")
        print()
        
        print("✅ Customer Data Agent working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_customer_data_agent()
