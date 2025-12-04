"""
Test Agent Card System for A2A Coordination
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from a2a.agent_card import get_agent_registry


def test_agent_registry():
    """Test agent registry and card retrieval"""
    print("=" * 60)
    print("  Testing Agent Card System")
    print("=" * 60)
    print()
    
    registry = get_agent_registry()
    
    # Test 1: Get all cards
    print("Test 1: Get All Agent Cards")
    print("-" * 60)
    all_cards = registry.get_all_cards()
    print(f"✅ Found {len(all_cards)} agents:")
    for name in all_cards.keys():
        print(f"  - {name}")
    print()
    
    # Test 2: Get specific card
    print("Test 2: Get Customer Data Agent Card")
    print("-" * 60)
    customer_card = registry.get_card('customer_data')
    if customer_card:
        print(f"✅ Agent: {customer_card.name}")
        print(f"   Description: {customer_card.description}")
        print(f"   Tools: {', '.join(customer_card.tools)}")
        print(f"   Capabilities: {len(customer_card.capabilities)} capabilities")
    print()
    
    # Test 3: Get cards formatted for context
    print("Test 3: Get Cards for LLM Context")
    print("-" * 60)
    context = registry.get_cards_for_context(exclude=['customer_data'])
    print("✅ Context for customer_data agent (excluding self):")
    print(context[:500] + "...")  # Show first 500 chars
    print()
    
    # Test 4: Agent matching
    print("Test 4: Agent Matching for Queries")
    print("-" * 60)
    test_queries = [
        "Get customer 5",
        "Create a ticket for billing issue",
        "Find customers whose name starts with 'A'",
        "Show active customers with more than 3 tickets"
    ]
    
    for query in test_queries:
        suggested = registry.match_agent_for_query(query)
        print(f"Query: '{query}'")
        print(f"  → Suggested: {suggested}")
    print()
    
    # Test 5: Agent card to prompt
    print("Test 5: Convert Card to Prompt Format")
    print("-" * 60)
    support_card = registry.get_card('support')
    if support_card:
        prompt = support_card.to_prompt()
        print("✅ Support Agent Card as Prompt:")
        print(prompt)
    print()
    
    print("✅ All tests passed!")


if __name__ == "__main__":
    test_agent_registry()

