"""
Test the Router Agent
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from a2a.agent.router_agent import router_agent 

def test_router():
    """Test router classification"""
    print("=" * 60)
    print("  TESTING ROUTER AGENT")
    print("=" * 60)
    print()
    
    router = router_agent()
    
    # Test cases
    test_queries = [
        ("Show me all active customers", "customer_data"),
        ("Get details for customer ID 5", "customer_data"),
        ("Add a new customer John Doe", "customer_data"),
        ("Update customer email", "customer_data"),
        ("I have a billing problem", "support"),
        ("Create a ticket for login issue", "support"),
        ("My order hasn't arrived", "support"),
        ("Find all customers whose ticket was created in the last 30 days and are active", "fallback_sql"),
    ]
    
    correct = 0
    total = len(test_queries)
    
    for query, expected_route in test_queries:
        print(f"Query: '{query}'")
        result = router.route(query)
        status = "✅" if result == expected_route else "❌"
        print(f"{status} Routed to: {result} (expected: {expected_route})")
        
        if result == expected_route:
            correct += 1
        
        print()
        
    print("=" * 60)
    print(f"  RESULTS: {correct}/{total} correct ({(correct/total)*100:.1f}%)")
    print("=" * 60)

if __name__ == "__main__":
    test_router()

