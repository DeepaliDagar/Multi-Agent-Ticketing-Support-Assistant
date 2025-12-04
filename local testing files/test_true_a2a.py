"""
Quick test for TRUE A2A coordination
Tests if agents can call each other autonomously
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from a2a.agent.customer_data_agent import customer_data_agent
from a2a.agent.support_agent import support_agent
from a2a.agent.fallback_sql_generator_agent import fallback_sql_generator_agent
from a2a.agent_card import AgentRegistry

print("=" * 70)
print("🤝 TRUE A2A-MCP TEST")
print("=" * 70)

# Initialize agents
customer_agent = customer_data_agent()
support_agent_inst = support_agent()
sql_agent = fallback_sql_generator_agent()

# Initialize agent card registry
registry = AgentRegistry()

# Prepare other_agents for A2A
other_agents_for_support = {
    "customer_data": customer_agent,
    "sql": sql_agent,
    "cards": registry.get_cards_for_context(exclude=['support'])
}

other_agents_for_customer = {
    "support": support_agent_inst,
    "sql": sql_agent,
    "cards": registry.get_cards_for_context(exclude=['customer_data'])
}

print("\n📝 Test 1: Support Agent needs customer info (should call customer_data)")
print("-" * 70)
query1 = "Create a ticket for customer 3 about login issue with high priority"
print(f"Query: {query1}\n")
result1 = support_agent_inst.process(query1, "", other_agents_for_support)
print(f"\nResult:\n{result1}")

print("\n\n📝 Test 2: Customer Agent asked about tickets (should call support)")
print("-" * 70)
query2 = "Get customer 1 and their ticket history"
print(f"Query: {query2}\n")
result2 = customer_agent.process(query2, "", other_agents_for_customer)
print(f"\nResult:\n{result2}")

print("\n\n📝 Test 3: Single agent query (no A2A needed)")
print("-" * 70)
query3 = "List all active customers"
print(f"Query: {query3}\n")
result3 = customer_agent.process(query3, "", other_agents_for_customer)
print(f"\nResult:\n{result3}")

print("\n" + "=" * 70)
print("✅ TRUE A2A TEST COMPLETE!")
print("=" * 70)
print("\nKey indicators of TRUE A2A:")
print("  • Look for '🤝 [agent_name] Requesting help from [other_agent]' messages")
print("  • Agents should autonomously decide when to ask for help")
print("  • No hardcoded coordination logic in the test script")

