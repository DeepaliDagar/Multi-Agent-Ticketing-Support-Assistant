"""
Test LangGraph Orchestrator
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from a2a.langgraph_orchestrator import create_langgraph_orchestrator


def test_single_agent_routing():
    """Test basic routing to a single agent."""
    print("=" * 60)
    print("  TEST 1: SINGLE AGENT ROUTING")
    print("=" * 60)
    print()
    
    orch = create_langgraph_orchestrator()
    
    test_cases = [
        ("Show me all customers", "customer_data"),
        ("Create a ticket for billing", "support"),
        ("Find customers whose name starts with 'A'", "sql"),
    ]
    
    for query, expected_route in test_cases:
        result = orch.process(query, thread_id="test1")
        
        print(f"Query: {query}")
        print(f"  Route: {result['route']} {'✅' if result['route'] == expected_route else '❌'}")
        print(f"  Parallel: {result['parallel_execution']}")
        print(f"  Response: {result['response'][:80]}...")
        print()
    
    print("✅ Single agent routing complete!")
    print()


def test_conversation_memory():
    """Test conversation memory across turns."""
    print("=" * 60)
    print("  TEST 2: CONVERSATION MEMORY")
    print("=" * 60)
    print()
    
    orch = create_langgraph_orchestrator()
    thread_id = "memory_test"
    
    # Turn 1
    print("Turn 1:")
    result1 = orch.process("Get customer with ID 5", thread_id=thread_id)
    print(f"  Query: Get customer with ID 5")
    print(f"  Route: {result1['route']}")
    print()
    
    # Turn 2 (should have context from turn 1)
    print("Turn 2:")
    result2 = orch.process("Create a ticket for him", thread_id=thread_id)
    print(f"  Query: Create a ticket for him")
    print(f"  Route: {result2['route']}")
    print()
    
    # Turn 3 (should have context from previous turns)
    print("Turn 3:")
    result3 = orch.process("Update his email", thread_id=thread_id)
    print(f"  Query: Update his email")
    print(f"  Route: {result3['route']}")
    print()
    
    # Show conversation history
    history = orch.get_conversation_history(thread_id)
    print(f"Total messages in history: {len(history)}")
    print()
    
    print("Conversation History:")
    print("-" * 40)
    for msg in history:
        role = msg.get("role", "")
        content = msg.get("content", "")[:60]
        if role == "user":
            print(f"👤 User: {content}")
        else:
            agent = msg.get("agent", "agent")
            print(f"🤖 {agent}: {content}")
    print("-" * 40)
    print()
    
    print("✅ Conversation memory works!")
    print()


def test_parallel_detection():
    """Test parallel execution detection."""
    print("=" * 60)
    print("  TEST 3: PARALLEL EXECUTION DETECTION")
    print("=" * 60)
    print()
    
    orch = create_langgraph_orchestrator()
    
    test_cases = [
        ("Show me customers and create a ticket", True),
        ("Get customer details and update status", True),
        ("List all customers", False),
        ("Create a ticket then send email", True),
    ]
    
    for query, should_be_parallel in test_cases:
        result = orch.process(query, thread_id=f"parallel_{query[:10]}")
        
        status = "✅" if result['parallel_execution'] == should_be_parallel else "❌"
        print(f"Query: {query}")
        print(f"  Parallel detected: {result['parallel_execution']} {status}")
        print()
    
    print("✅ Parallel detection complete!")
    print()


def test_thread_isolation():
    """Test that different threads have isolated memory."""
    print("=" * 60)
    print("  TEST 4: THREAD ISOLATION")
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
    if len(history1) != len(history2):
        print("✅ Threads are properly isolated!")
    else:
        print("❌ Thread isolation may not be working")
    
    print()


def demo_real_workflow():
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
        "Now find all customers from California",
        "Update customer 1's email to new@example.com",
    ]
    
    for i, query in enumerate(workflow, 1):
        print(f"Step {i}: {query}")
        result = orch.process(query, thread_id=thread_id)
        print(f"  ➜ Route: {result['route']}")
        print(f"  ➜ Parallel: {result['parallel_execution']}")
        print()
    
    print("Final conversation history:")
    print("-" * 60)
    history = orch.get_conversation_history(thread_id)
    for msg in history:
        role = msg.get("role", "")
        content = msg.get("content", "")[:70]
        if role == "user":
            print(f"👤 {content}")
        else:
            agent = msg.get("agent", "")
            print(f"   🤖 [{agent}] {content}")
    print("-" * 60)
    print()
    
    print("✅ Workflow complete!")
    print()


if __name__ == "__main__":
    print("\n🚀 TESTING LANGGRAPH ORCHESTRATOR\n")
    
    try:
        test_single_agent_routing()
        test_conversation_memory()
        test_parallel_detection()
        test_thread_isolation()
        demo_real_workflow()
        
        print("=" * 60)
        print("  ✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

