"""
Agent Card System - Self-describing agent capabilities for A2A coordination
Each agent has a card that describes what it can do and when to use it.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class AgentCard:
    """
    Agent Card - Describes an agent's capabilities, tools, and when to use it.
    Similar to MCP tool schema but for agents.
    """
    name: str
    description: str
    capabilities: List[str]
    tools: List[str]
    best_for: List[str]
    input_format: Dict[str, str]
    output_format: str
    examples: List[Dict[str, str]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert card to dictionary for LLM consumption."""
        return asdict(self)
    
    def to_prompt(self) -> str:
        """Convert card to human-readable prompt format."""
        return f"""
Agent: {self.name}
Description: {self.description}

Capabilities:
{chr(10).join(f"  - {cap}" for cap in self.capabilities)}

Available Tools:
{chr(10).join(f"  - {tool}" for tool in self.tools)}

Best For:
{chr(10).join(f"  - {use_case}" for use_case in self.best_for)}

Input: {', '.join(f"{k}={v}" for k, v in self.input_format.items())}
Output: {self.output_format}

Example Usage:
{chr(10).join(f"  Query: {ex['query']}\n  Use: {ex['reason']}" for ex in self.examples)}
"""


class AgentRegistry:
    """
    Central registry of all available agents and their cards.
    Agents can query this to discover other agents for A2A coordination.
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentCard] = {}
        self._initialize_cards()
    
    def _initialize_cards(self):
        """Initialize agent cards for all available agents."""
        
        # Customer Data Agent Card
        self.agents['customer_data'] = AgentCard(
            name="customer_data_agent",
            description="Manages customer information retrieval and updates",
            capabilities=[
                "Get customer details by ID",
                "List customers with optional status filter",
                "Add new customers to database",
                "Update existing customer information",
                "Activate/deactivate customer accounts"
            ],
            tools=[
                "get_customer",
                "list_customers", 
                "add_customer",
                "update_customer"
            ],
            best_for=[
                "Looking up customer information",
                "Creating new customer records",
                "Updating customer details (name, email, phone, status)",
                "Filtering customers by status (active/inactive)"
            ],
            input_format={
                "query": "str - Natural language customer request",
                "conversation_history": "str - Optional previous context",
                "other_agents": "dict - Other agents for A2A coordination"
            },
            output_format="str - Customer data or operation result",
            examples=[
                {
                    "query": "Get details for customer ID 5",
                    "reason": "Direct customer lookup by ID"
                },
                {
                    "query": "Show me all active customers",
                    "reason": "List customers filtered by status"
                },
                {
                    "query": "Add new customer John Doe with email john@example.com",
                    "reason": "Create new customer record"
                }
            ]
        )
        
        # Support Agent Card
        self.agents['support'] = AgentCard(
            name="support_agent",
            description="Handles support tickets and customer issue tracking",
            capabilities=[
                "Create support tickets for customers",
                "Get customer ticket history",
                "Track customer issues and resolutions",
                "Link tickets to customer records"
            ],
            tools=[
                "create_ticket",
                "get_customer_history"
            ],
            best_for=[
                "Creating support tickets",
                "Tracking customer issues",
                "Getting ticket history for a customer",
                "Handling customer complaints"
            ],
            input_format={
                "query": "str - Natural language support request",
                "conversation_history": "str - Optional previous context",
                "other_agents": "dict - Other agents for A2A coordination"
            },
            output_format="str - Ticket information or customer history",
            examples=[
                {
                    "query": "Create a ticket for customer 3 about billing issue",
                    "reason": "Create support ticket"
                },
                {
                    "query": "Show me ticket history for customer 5",
                    "reason": "Get customer support history"
                },
                {
                    "query": "I have a login problem",
                    "reason": "Customer issue that needs ticket"
                }
            ]
        )
        
        # SQL Generator Agent Card
        self.agents['sql'] = AgentCard(
            name="fallback_sql_generator_agent",
            description="Generates and executes complex SQL queries from natural language",
            capabilities=[
                "Generate SQL from natural language",
                "Execute complex filtering queries",
                "Handle date-based queries",
                "Perform pattern matching (LIKE queries)",
                "Aggregate data across tables"
            ],
            tools=[
                "fallback_sql"
            ],
            best_for=[
                "Complex filtering (name patterns, date ranges)",
                "Custom WHERE clauses beyond simple ID/status",
                "Aggregations and calculations",
                "Queries requiring JOIN operations",
                "Date-based filtering (last 30 days, etc.)"
            ],
            input_format={
                "query": "str - Natural language SQL request",
                "conversation_history": "str - Optional previous context",
                "other_agents": "dict - Other agents for A2A coordination"
            },
            output_format="str - SQL query results or generated SQL",
            examples=[
                {
                    "query": "Find all customers whose name starts with 'A'",
                    "reason": "Pattern matching query"
                },
                {
                    "query": "Get customers created in the last 30 days",
                    "reason": "Date-based filtering"
                },
                {
                    "query": "Show active customers with more than 3 tickets",
                    "reason": "Complex query with aggregation"
                }
            ]
        )
    
    def get_card(self, agent_name: str) -> Optional[AgentCard]:
        """Get agent card by name."""
        return self.agents.get(agent_name)
    
    def get_all_cards(self) -> Dict[str, AgentCard]:
        """Get all agent cards."""
        return self.agents
    
    def get_cards_for_context(self, exclude: Optional[List[str]] = None) -> str:
        """
        Get all agent cards formatted for LLM context.
        Used to help agents decide which other agent to call.
        
        Args:
            exclude: List of agent names to exclude (e.g., current agent)
        """
        exclude = exclude or []
        
        cards_text = "Available Agents for A2A Coordination:\n"
        cards_text += "=" * 60 + "\n\n"
        
        for name, card in self.agents.items():
            if name not in exclude:
                cards_text += card.to_prompt()
                cards_text += "\n" + "=" * 60 + "\n"
        
        return cards_text
    
    def match_agent_for_query(self, query: str) -> str:
        """
        Simple heuristic to suggest which agent might be best for a query.
        This is a helper function - LLMs can also reason about this directly.
        """
        query_lower = query.lower()
        
        # Check for SQL related keywords
        sql_keywords = ['filter', 'starts with', 'ends with', 'contains', 
                       'last', 'days', 'weeks', 'months', 'date', 'between',
                       'aggregat', 'count', 'sum', 'average']
        if any(keyword in query_lower for keyword in sql_keywords):
            return 'sql'
        
        # Check for support keywords
        support_keywords = ['ticket', 'issue', 'problem', 'complaint', 
                           'help', 'support', 'history']
        if any(keyword in query_lower for keyword in support_keywords):
            return 'support'
        
        # Default to customer data for customer-related queries
        customer_keywords = ['customer', 'user', 'account', 'contact',
                            'email', 'phone', 'name', 'add', 'update', 'get', 'list']
        if any(keyword in query_lower for keyword in customer_keywords):
            return 'customer_data'
        
        return 'customer_data'  # Default


# Singleton registry
_agent_registry = None

def get_agent_registry() -> AgentRegistry:
    """Get or create singleton agent registry."""
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry()
    return _agent_registry


# Test
if __name__ == "__main__":
    registry = get_agent_registry()
    
    print("=" * 60)
    print("  Agent Card System Test")
    print("=" * 60)
    print()
    
    # Show all cards
    print(registry.get_cards_for_context())
    
    # Test matching
    test_queries = [
        "Get customer 5",
        "Create a ticket for billing issue",
        "Find customers whose name starts with 'A'"
    ]
    
    print("\nAgent Matching Test:")
    print("-" * 60)
    for query in test_queries:
        suggested = registry.match_agent_for_query(query)
        print(f"Query: {query}")
        print(f"Suggested Agent: {suggested}")
        print()

