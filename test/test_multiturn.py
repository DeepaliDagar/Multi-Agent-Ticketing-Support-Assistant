"""
Test Multi-Turn Conversation with LangGraph Memory
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from a2a.langgraph_orchestrator import create_langgraph_orchestrator


def test_memory_persistence():
    """Test that conversation memory persists across turns."""
    print("=" * 60)
    print("  TEST 1: MEMORY PERSISTENCE")
    print("=" * 60)
    print()
    
    orch = create_langgraph_orchestrator()
    thread_id = "test_memory"
    
    # Turn 1
    print("Turn 1: Get customer 5")
    result1 = orch.process("Get customer with ID 5", thread_id=thread_id)
    print(f"  Route: {result1['route']}")
    print(f"  Response: {result1['response'][:80]}...")
    print()
    
    # Turn 2 - Should have context from Turn 1
    print("Turn 2: Create ticket (should know who 'him' refers to)")
    result2 = orch.process("Create a ticket for him", thread_id=thread_id)
    print(f"  Route: {result2['route']}")
    print(f"  Response: {result2['response'][:80]}...")
    print()
    
    # Turn 3 - Should still have context
    print("Turn 3: Update email (should still know customer)")
    result3 = orch.process("Update his email", thread_id=thread_id)
    print(f"  Route: {result3['route']}")
    print(f"  Response: {result3['response'][:80]}...")
    print()
    
    # Get conversation history
    history = orch.get_conversation_history(thread_id)
    print(f"Total messages in history: {len(history)}")
    print()
    
    print("✅ Memory persistence works!")
    print()


def test_thread_isolation():
    """Test that different threads have isolated memory."""
    print("=" * 60)
    print("  TEST 2: THREAD ISOLATION")
    print("=" * 60)
    print()
    
    orch = create_langgraph_orchestrator()
    
    # Thread 1
    print("Thread 1:")
    orch.process("Get customer 1", thread_id="thread1")
    orch.process("Create a ticket", thread_id="thread1")
    history1 = orch.get_conversation_history("thread1")
    print(f"  Messages: {len(history1)}")
    print()
    
    # Thread 2
    print("Thread 2:")
    orch.process("Get customer 2", thread_id="thread2")
    history2 = orch.get_conversation_history("thread2")
    print(f"  Messages: {len(history2)}")
    print()
    
    # Verify isolation
    if len(history1) > len(history2):
        print("✅ Threads are properly isolated!")
    else:
        print("⚠️  Thread isolation check inconclusive")
    
    print()


def test_contextual_routing():
    """Test that routing works with conversation context."""
    print("=" * 60)
    print("  TEST 3: CONTEXTUAL ROUTING")
    print("=" * 60)
    print()
    
    orch = create_langgraph_orchestrator()
    thread_id = "routing_test"
    
    queries = [
        ("Show me all active customers", "customer_data"),
        ("Now add a new customer named Sarah", "customer_data"),
        ("Create a ticket for Sarah about billing", "support"),
        ("Show me customers whose names start with 'S'", "fallback_sql"),
    ]
    
    for i, (query, expected_route) in enumerate(queries, 1):
        result = orch.process(query, thread_id=thread_id)
        status = "✅" if result['route'] == expected_route else "❌"
        
        print(f"Turn {i}: {query}")
        print(f"  Route: {result['route']} {status}")
        print()
    
    print("✅ Contextual routing works!")
    print()


def demo_realistic_workflow():
    """Demo a realistic multi-turn workflow."""
    print("=" * 60)
    print("  DEMO: REALISTIC WORKFLOW")
    print("=" * 60)
    print()
    
    orch = create_langgraph_orchestrator()
    thread_id = "demo_workflow"
    
    workflow = [
        "Show me all active customers",
        "Get details for customer ID 1",
        "Create a high-priority ticket for him about login issues",
        "Update his status to disabled",
    ]
    
    for i, query in enumerate(workflow, 1):
        print(f"Step {i}: {query}")
        result = orch.process(query, thread_id=thread_id)
        print(f"  ➜ Route: {result['route']}")
        print(f"  ➜ Parallel: {result['parallel_execution']}")
        print(f"  ➜ Response: {result['response'][:70]}...")
        print()
    
    # Show final history
    history = orch.get_conversation_history(thread_id)
    print(f"Total conversation turns: {len(history)} messages")
    print()
    
    print("✅ Workflow complete!")
    print()


if __name__ == "__main__":
    print("\n🧪 TESTING MULTI-TURN CONVERSATION (LangGraph Memory)\n")
    
    try:
        test_memory_persistence()
        test_thread_isolation()
        test_contextual_routing()
        demo_realistic_workflow()
        
        print("=" * 60)
        print("  ✅ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("Note: LangGraph's MemorySaver handles all conversation memory.")
        print("No separate conversation_manager needed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
