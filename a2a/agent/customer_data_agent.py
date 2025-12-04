"""
Customer Data Agent - Handles customer information retrieval and management
Uses MCP Client for dynamic tool discovery
"""
import os
import sys
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from a2a.utils import CUSTOMER_DATA_MODEL
from a2a.mcp_client import get_mcp_client

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

load_dotenv()

class customer_data_agent:
    """Customer data agent that handles customer information operations."""
    
    def __init__(self, model: str = CUSTOMER_DATA_MODEL):
        """Initialize customer data agent with OpenAI client."""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = model
        self.name = "customer_data_agent"
        
        # Dynamic tool discovery from MCP Client
        self.mcp_client = get_mcp_client()
        self.tools = self.mcp_client.list_tools(for_agent="customer_data")
        
        # Add ask_agent tool for A2A coordination
        self.tools.append({
            "type": "function",
            "function": {
                "name": "ask_agent",
                "description": "Request help from another agent (A2A coordination). Use when you need tickets, support info, or complex SQL queries.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "enum": ["support", "sql"],
                            "description": "Which agent to ask for help"
                        },
                        "query": {
                            "type": "string",
                            "description": "The question/request to send to that agent"
                        }
                    },
                    "required": ["agent_name", "query"]
                }
            }
        })
    
    def _execute_tool(self, tool_name: str, arguments: dict, other_agents: dict = None) -> dict:
        """Execute a tool: either via MCP Client or A2A coordination."""
        if tool_name == "ask_agent":
            # TRUE A2A: Agent requests help from another agent
            from a2a.a2a_logger import log_request, log_response
            
            agent_name = arguments["agent_name"]
            query = arguments["query"]
            
            # Log the A2A request
            log_request(self.name, agent_name, query)
            
            if other_agents and agent_name in other_agents:
                target_agent = other_agents[agent_name]
                result = target_agent.process(query, "", {})
                
                # Log the response
                log_response(agent_name, self.name, f"Completed request: {query[:50]}...")
                
                return {"success": True, "data": result}
            else:
                return {"error": f"Agent {agent_name} not available"}
        else:
            # All other tools: Call via MCP Client
            return self.mcp_client.call_tool(tool_name, **arguments)
    
    def process(self, user_query: str, conversation_history: str = "", other_agents: dict = None) -> str:
        """
        Process user query using OpenAI function calling with TRUE A2A.
        The LLM decides when to ask other agents for help.
        
        Args:
            user_query: The user's customer data request
            conversation_history: Optional conversation history
            other_agents: Dict of other agents for A2A coordination
            
        Returns:
            Agent response as string
        """
        # Build system prompt with agent cards
        system_content = """You are a helpful customer management assistant.

YOUR TOOLS:
- get_customer: Get customer details by ID
- list_customers: List/filter customers
- add_customer: Add new customer
- update_customer: Update customer info
- ask_agent: Request help from other agents (A2A coordination)

AGENT-TO-AGENT (A2A) COORDINATION:
When you need ticket information or complex SQL queries, use ask_agent to request help from other agents.
"""
        
        # Add agent cards if available
        if other_agents and other_agents.get('cards'):
            system_content += f"\n\nAVAILABLE AGENTS:\n{other_agents['cards'][:800]}"
        
        messages = [{"role": "system", "content": system_content}]
        
        if conversation_history:
            messages.append({"role": "system", "content": f"Previous conversation:\n{conversation_history}"})
        
        messages.append({"role": "user", "content": user_query})
        
        try:
            # Multi-turn tool calling loop
            for _ in range(5):  # Max 5 tool calls
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto"
                )
                
                response_message = response.choices[0].message
                
                # No tool calls? We're done!
                if not response_message.tool_calls:
                    return response_message.content or "Request processed."
                
                # Execute all tool calls
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Execute the tool
                    tool_result = self._execute_tool(function_name, function_args, other_agents)
                    
                    # Add to conversation
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result)
                    })
            
            # If we hit max iterations, return what we have
            return "Request processed with multiple steps."
            
        except Exception as e:
            return f"❌ Error processing request: {str(e)}"


def create_customer_data_agent(model: str = CUSTOMER_DATA_MODEL) -> customer_data_agent:
    """Create and return a customer_data_agent instance."""
    return customer_data_agent(model=model)
     