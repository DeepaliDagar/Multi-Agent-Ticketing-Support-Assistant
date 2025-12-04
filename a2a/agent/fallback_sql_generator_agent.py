"""
Fallback SQL Generator Agent - Generates SQL queries from natural language
Uses MCP Client for dynamic tool discovery (no hardcoding!)
"""
import os
import sys
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from a2a.utils import SQL_GENERATOR_MODEL
from a2a.mcp_client import get_mcp_client

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

load_dotenv()

# in agent class, we define the agent's behavior and capabilities
class fallback_sql_generator_agent:
    """SQL generator agent that converts natural language to SQL queries."""
    
    # constructor
    def __init__(self, model: str = SQL_GENERATOR_MODEL):
        """Initialize SQL generator agent with OpenAI client."""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = model
        self.name = "fallback_sql_generator_agent"
        
        # Dynamic tool discovery from MCP Client
        self.mcp_client = get_mcp_client()
        
        self.schema = """
Database Schema:
- customers: id, name, email, phone, status, created_at, updated_at
- tickets: id, customer_id, issue, priority, status, created_at, updated_at
"""
    # process method
    def process(self, user_query: str, conversation_history: str = "", other_agents: dict = None) -> str:
        """
        Process user query by generating and executing SQL with TRUE A2A.
        
        Args:
            user_query: The user's SQL request
            conversation_history: Optional conversation history
            other_agents: Dict of other agents for A2A coordination
            
        Returns:
            Agent response as string
        """
        system_content = f"""You are a FALLBACK SQL generator assistant.

{self.schema}

 IMPORTANT: You should ONLY be used for complex queries that cannot be handled by other agents!

Your task:
1. Convert complex natural language queries into SQL
2. Only give me the SQL query, no other text or explanation
3. Only generate SELECT, INSERT, or UPDATE queries (no DELETE, DROP, CREATE TABLE, etc.)
4. Use proper SQL syntax for SQLite
5. Prefer SIMPLE queries - let other agents handle relationships via A2A coordination
6. AVOID JOINS when possible - customer_data and support agents can coordinate

WHEN TO USE SQL:
Name pattern matching (LIKE 'A%')
Date range filtering (created_at > date(...))
Aggregations (COUNT, SUM, AVG)
Complex WHERE conditions and joins

WHEN NOT TO USE SQL (other agents handle these):
Get customer by ID → customer_data agent
Customer + tickets → customer_data + support agents via A2A

Examples of what YOU should handle:
- "Find customers whose name starts with 'A'" → SELECT * FROM customers WHERE name LIKE 'A%'
- "Get customers created in last 30 days" → SELECT * FROM customers WHERE created_at >= date('now','-30 days')
- "Count tickets by priority" → SELECT priority, COUNT(*) FROM tickets GROUP BY priority
"""
        
        # Add agent cards if available
        if other_agents and other_agents.get('cards'):
            system_content += f"\n\nAVAILABLE AGENTS (for context):\n{other_agents['cards'][:500]}"
        
        messages = [{"role": "system", "content": system_content}]
        
        # Add conversation history if available
        if conversation_history:
            messages.append({
                "role": "system",
                "content": f"Previous conversation:\n{conversation_history}"
            })
        
        messages.append({
            "role": "user",
            "content": user_query
        })
        
        try:
            # Generate SQL
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0,  # Deterministic for SQL generation
                max_tokens=500  # Increased from 300 to allow complex queries
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            
            # Execute the generated SQL via MCP Client
            result = self.mcp_client.call_tool("fallback_sql", sql_query=sql_query)
            
            # Format the response
            if result.get("success"):
                # Fix: fallback_sql returns 'results' and 'count', not 'rows' and 'row_count'
                results = result.get("results", [])
                count = result.get("count", 0)
                
                if count == 0:
                    return f"✅ SQL Query Executed:\n```sql\n{sql_query}\n```\n\nNo results found."
                
                # Format results as a table
                response_text = f"✅ SQL Query Executed:\n```sql\n{sql_query}\n```\n\n"
                response_text += f"Found {count} result(s):\n\n"
                
                # Display results
                for i, row in enumerate(results[:10], 1):  # Limit to 10 rows
                    response_text += f"{i}. "
                    response_text += ", ".join([f"{k}: {v}" for k, v in row.items()])
                    response_text += "\n"
                
                if count > 10:
                    response_text += f"\n... and {count - 10} more result(s)"
                
                return response_text
            else:
                return f"❌ SQL Error:\n```sql\n{sql_query}\n```\n\nError: {result.get('error', 'Unknown error')}"
            
        except Exception as e:
            return f"❌ Error processing request: {str(e)}"


def create_fallback_sql_generator_agent(model: str = SQL_GENERATOR_MODEL) -> fallback_sql_generator_agent:
    """Create and return a fallback_sql_generator_agent instance."""
    return fallback_sql_generator_agent(model=model)
