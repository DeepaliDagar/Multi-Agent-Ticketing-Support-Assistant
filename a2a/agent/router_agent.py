"""
Router Agent - Routes user queries to the appropriate specialized agent
"""
import os
from typing import Literal
from openai import OpenAI
from dotenv import load_dotenv
from a2a.utils import ROUTER_MODEL  
load_dotenv()

class router_agent:
    """
    Simple router that classifies user intent and routes to appropriate agent.
    Each specialized agent has access to MCP tools.
    """
    
    def __init__(self, model: str = ROUTER_MODEL):
        """Initialize router with OpenAI client."""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = model
        self.name = "router_agent"
    
    def route(self, user_query: str) -> Literal["customer_data", "support", "sql"]:
        """
        Classify user query and return which agent to use.
        
        Args:
            user_query: The user's input query
            
        Returns:
            One of: "customer_data", "support", "sql"
        """
        prompt = f"""Classify this user query into ONE category:

USER QUERY: "{user_query}"

CATEGORIES AND THEIR CAPABILITIES:

1. **customer_data** - Simple customer operations:
   - Get customer by ID (specific customer)
   - List customers (all, by status: active/disabled)
   - Add new customer
   - Update customer info
   - CAN coordinate with support agent for tickets (A2A)

2. **support** - Ticket and support operations:
   - Create tickets
   - Get ticket history for a customer
   - Handle customer issues
   - CAN coordinate with customer_data agent for customer info (A2A)

3. **sql** - ONLY for complex queries that REQUIRE:
   - Name pattern matching (starts with, contains, ends with)
   - Date filtering (beyond simple list)
   - Multiple complex conditions
   - Aggregations (count, sum, avg)
   - Custom JOINs

ROUTING RULES:
- If query asks for "customer X and their tickets" → customer_data (it will use A2A to get tickets)
- If query asks for "customer X with ticket history" → customer_data or support (both can handle with A2A)
- If query needs customer by ID + tickets → customer_data or support (NOT sql!)
- ONLY use sql for: name patterns, date ranges, complex filters

EXAMPLES:
"Get customer 5" → customer_data
"Get customer 5 and ticket history" → customer_data (A2A with support)
"Customer 2 details and tickets" → customer_data (A2A with support)
"Show all active customers" → customer_data
"Create ticket for customer 3" → support (A2A with customer_data if needed)
"Find customers whose name starts with 'A'" → sql
"Get customers signed up in January" → sql
"Show customers with ticket count > 5" → sql

Your response (one word):"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,  # Deterministic routing
                max_tokens=20
            )
            
            route = response.choices[0].message.content.strip().lower()
            
            # Validate and return route
            if route in ["customer_data", "support", "sql"]:
                return route
            else:
                return "customer_data"  # Default fallback
        except Exception as e:
            print(f"Router error: {e}")
            return "customer_data"  # Default fallback


def route_query(user_query: str) -> str:
    """
    Simple routing function - returns which agent to use.
    
    Usage:
        agent_name = route_query("Show me all customers")
        # agent_name will be "customer_data"
        # Then call the appropriate agent based on this
    """
    router = router_agent()
    return router.route(user_query)
     