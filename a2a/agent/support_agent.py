"""
Support Agent - Handles ticket creation and customer support issues
Uses MCP Client for dynamic tool discovery (no hardcoding!)
"""
import os
import sys
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from a2a.utils import SUPPORT_MODEL
from a2a.mcp_client import get_mcp_client

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

load_dotenv()

class support_agent:
    """Customer support agent with A2A coordination capability."""
    
    def __init__(self, model: str = SUPPORT_MODEL):
        """Initialize support agent with OpenAI client."""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = model
        self.name = "support_agent"
        
        # Dynamic tool discovery from MCP Client
        self.mcp_client = get_mcp_client()
        self.tools = self.mcp_client.list_tools(for_agent="support")
        
        # Add ask_agent tool for A2A coordination
        self.tools.append({
            "type": "function",
            "function": {
                "name": "ask_agent",
                "description": "Request help from another agent (A2A coordination). Use when you need information from another agent's domain. Check agent cards to see who can help.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "enum": ["customer_data", "sql"],
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
        """Execute a tool - either via MCP Client or A2A coordination."""
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
        Process user query using OpenAI function calling with A2A coordination.
        The LLM decides when to ask other agents for help.
        
        Args:
            user_query: The user's support request
            conversation_history: Optional conversation history
            other_agents: Dict of other agents for A2A coordination
            
        Returns:
            Agent response as string
        """
        # Build system prompt with agent cards
        system_content = f"""You are a helpful customer support assistant.

YOUR TOOLS:
- create_ticket: Create support tickets with intelligent priority assignment
- get_customer_history: Get ticket history for a customer
- ask_agent: Request help from other agents (A2A coordination)

PRIORITY ASSIGNMENT GUIDELINES:
When creating tickets, analyze the issue and assign priority based on these criteria:

🔴 HIGH PRIORITY (critical issues affecting customer access or business):
   - Login/authentication issues
   - Account locked or disabled
   - Payment/billing failures
   - Data loss or corruption
   - Service completely unavailable
   - Security concerns

🟡 MEDIUM PRIORITY (important but not blocking):
   - Software bugs affecting functionality
   - Performance/speed issues
   - Billing/invoice questions
   - Feature not working as expected
   - Integration issues

🟢 LOW PRIORITY (nice-to-have or informational):
   - Feature requests
   - General questions/how-to
   - Minor UI issues
   - Documentation requests
   - Cosmetic issues

AGENT-TO-AGENT (A2A) COORDINATION:
When you need information you don't have access to, use ask_agent to request help from other agents.
"""
        
        # Add agent cards if available
        if other_agents and other_agents.get('cards'):
            system_content += f"\n\nAVAILABLE AGENTS:\n{other_agents['cards'][:800]}"
        
        system_content += "\n\nIMPORTANT: If you need customer details (name, email, status), use ask_agent to request from customer_data agent."
        
        messages = [{"role": "system", "content": system_content}]
        
        if conversation_history:
            messages.append({"role": "system", "content": f"Previous conversation:\n{conversation_history}"})
        
        messages.append({"role": "user", "content": user_query})
        
        try:
            # Multi-turn tool calling loop
            for _ in range(5):  # Max 5 tool calls to prevent infinite loops
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto"
                )
                
                response_message = response.choices[0].message
                
                # No tool calls? We're done!
                if not response_message.tool_calls:
                    return response_message.content or "I've processed your request."
                
                # Execute all tool calls
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Execute tool
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
            return f"❌ Error: {str(e)}"


def create_support_agent(model: str = SUPPORT_MODEL) -> support_agent:
    """Create and return a support_agent instance."""
    return support_agent(model=model)
