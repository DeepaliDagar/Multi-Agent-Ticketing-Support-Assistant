"""
Orchestrator for A2A-MCP System using Google ADK
Routes queries to appropriate agents and coordinates multi-agent execution
"""
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from termcolor import colored
import json
import re
import warnings
import logging
import os
import sys
import asyncio
from pathlib import Path
# Add project root to path when running as script (must be before imports)
# This allows absolute imports to work when running directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from a2a.utils import MCP_HTTP_BASE_URL

# Configure logging - ADK handles its own logging via GOOGLE_SDK_PYTHON_LOGGING_SCOPE env var
# Only suppress if explicitly requested via environment variable
if os.getenv('SUPPRESS_ADK_LOGS', 'false').lower() == 'true':
    logging.getLogger('google.adk').setLevel(logging.CRITICAL)
    logging.getLogger('google.genai').setLevel(logging.CRITICAL)
    logging.getLogger('asyncio').setLevel(logging.CRITICAL)

# Suppress known harmless async cleanup errors from MCP connections
# These happen when connections are cleaned up in background tasks
class AsyncCleanupFilter(logging.Filter):
    """Filter out known harmless async cleanup errors."""
    def filter(self, record):
        message = record.getMessage()
        # Filter out known cleanup-related errors that don't affect functionality
        skip_patterns = [
            'Task exception was never retrieved',
            'Attempted to exit cancel scope',
            'bound to a different event loop',
            'Error during disconnected session cleanup',
            'generator didn\'t stop after athrow()',
            'an error occurred during closing of asynchronous generator'
        ]
        return not any(pattern in message for pattern in skip_patterns)

# Apply filter to asyncio logger
logging.getLogger('asyncio').addFilter(AsyncCleanupFilter())

# Suppress Python warnings for cleaner output (can be controlled via PYTHONWARNINGS env var)
warnings.filterwarnings('ignore')

# Support both relative imports (when used as module) and absolute imports (when run as script)
try:
    from .agent.router_agent import router_agent
    from .agent.customer_data_agent import customer_data_agent
    from .agent.support_agent import support_agent
    from .agent.fallback_sql_generator_agent import fallback_sql_generator_agent
except ImportError:
    # Fallback to absolute imports when running as script
    from a2a.agent.router_agent import router_agent
    from a2a.agent.customer_data_agent import customer_data_agent
    from a2a.agent.support_agent import support_agent
    from a2a.agent.fallback_sql_generator_agent import fallback_sql_generator_agent


class A2AOrchestrator:
    """Orchestrator that routes queries to appropriate agents and coordinates multi-agent execution"""
    
    def __init__(self, user_id: str = "user_123", session_id: str = "session_456", handoff_callback=None):
        """
        Initialize the orchestrator with session management.
        
        Args:
            user_id: User identifier for session management
            session_id: Session identifier for conversation continuity
            handoff_callback: Optional callback function for handoff events
                            Called as: callback(event_type, data)
                            Event types: 'routing', 'handoff', 'completion'
        """
        self.user_id = user_id
        self.session_id = session_id
        self.session_service = InMemorySessionService()
        self.handoff_callback = handoff_callback  # Callback for handoff events
        
        # Agent mapping
        self.agents = {
            'customer_data': customer_data_agent,
            'support': support_agent,
            'sql': fallback_sql_generator_agent,
        }
        
        print(colored("✅ A2A Orchestrator initialized", "green"))
        print(colored("   Supports single and multi-agent routing", "cyan"))
    
    def _get_session_id(self, app_name: str) -> str:
        """Get the session ID for an app name."""
        clean_name = app_name.replace("_agent", "")
        return f"{self.session_id}_{clean_name}"
    
    async def _ensure_session(self, app_name: str):
        """Ensure a session exists for an agent. Creates it if it doesn't exist."""
        session_id = self._get_session_id(app_name)
        try:
            session = await self.session_service.create_session(
                app_name=app_name,
                user_id=self.user_id,
                session_id=session_id
            )
            return session
        except Exception as e:
            # Session might already exist, try to get it
            try:
                # Try to get existing session
                session = await self.session_service.get_session(
                    app_name=app_name,
                    user_id=self.user_id,
                    session_id=session_id
                )
                return session
            except Exception:
                # If still fails, that's okay - Runner might create it
                pass
            return None
    
    def _parse_supervisor_decision(self, router_response: str) -> dict:
        """Parse the supervisor router's JSON response."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', router_response, re.DOTALL)
            if json_match:
                decision_data = json.loads(json_match.group())
                next_agent = decision_data.get('next_agent')
                done = decision_data.get('done', False)
                reason = decision_data.get('reason', 'No reason provided')
                
                # Validate agent name if provided
                if next_agent and next_agent not in self.agents:
                    print(colored(f"⚠️  Unknown agent: {next_agent}, setting to null", "yellow"))
                    next_agent = None
                    done = True
                
                return {
                    'next_agent': next_agent,
                    'done': done,
                    'reason': reason
                }
        except json.JSONDecodeError as e:
            print(colored(f"⚠️  JSON parse error: {e}", "yellow"))
        
        # Fallback: try to find "done" or agent names in text
        response_lower = router_response.lower()
        
        # Check if done
        if 'done' in response_lower and ('true' in response_lower or 'complete' in response_lower):
            return {
                'next_agent': None,
                'done': True,
                'reason': 'Parsed from text response'
            }
        
        # Find agent name
        for agent_name in self.agents.keys():
            if agent_name in response_lower:
                return {
                    'next_agent': agent_name,
                    'done': False,
                    'reason': 'Parsed from text response'
                }
        
        # Default fallback
        print(colored("⚠️  Could not parse supervisor decision, defaulting to customer_data", "yellow"))
        return {
            'next_agent': 'customer_data',
            'done': False,
            'reason': 'Default fallback'
        }
    
    async def _supervisor_decide(self, query: str, previous_results: list = None) -> dict:
        """Ask supervisor router to decide next agent or if done."""
        try:
            await self._ensure_session("router_agent")
            
            router_runner = Runner(
                agent=router_agent,
                session_service=self.session_service,
                app_name="router_agent"
            )
            
            if previous_results:
                # Supervisor evaluation after agent execution
                results_summary = "\n".join([
                    f"Agent: {r['agent']}\nResponse: {r['response'][:200]}..."
                    for r in previous_results
                ])
                
                supervisor_prompt = f"""EVALUATE: The following agents have executed. Determine if the query is complete or if another agent is needed.

ORIGINAL USER QUERY: "{query}"

PREVIOUS AGENT RESULTS:
{results_summary}

Analyze if the query is FULLY answered:
- If YES → {{"next_agent": null, "done": true, "reason": "Query fully answered"}}
- If NO → {{"next_agent": "agent_name", "done": false, "reason": "Still need..."}}

Available agents: customer_data, support, sql
"""
            else:
                # Initial routing
                supervisor_prompt = f"""INITIAL ROUTING: Determine the FIRST agent to handle this query.

USER QUERY: "{query}"

Respond with JSON:
{{"next_agent": "agent_name", "done": false, "reason": "why this agent"}}

Available agents: customer_data, support, sql
"""
            
            content = types.Content(
                role="user",
                parts=[types.Part(text=supervisor_prompt)]
            )
            
            session_id = self._get_session_id("router_agent")
            
            # Suppress cleanup errors for router too
            import sys
            from io import StringIO
            old_stderr = sys.stderr
            stderr_buffer = StringIO()
            
            try:
                sys.stderr = stderr_buffer
                events = router_runner.run(
                    user_id=self.user_id,
                    session_id=session_id,
                    new_message=content
                )
                
                router_response = None
                for event in events:
                    if event.is_final_response():
                        router_response = event.content.parts[0].text
                        break
            finally:
                sys.stderr = old_stderr
                # Suppress known cleanup errors (same as in _execute_agent)
                error_output = stderr_buffer.getvalue()
                if error_output and not any(
                    err in error_output 
                    for err in [
                        "Task exception was never retrieved",
                        "Attempted to exit cancel scope in a different task",
                        "is bound to a different event loop",
                        "Error during disconnected session cleanup",
                        "generator didn't stop after athrow()"
                    ]
                ):
                    print(error_output, file=old_stderr)
            
            if router_response:
                decision = self._parse_supervisor_decision(router_response)
                return decision
            else:
                raise Exception("No response from supervisor router")
                
        except Exception as e:
            print(colored(f"⚠️  Error in supervisor decision: {e}", "yellow"))
            return {
                'next_agent': 'customer_data' if not previous_results else None,
                'done': bool(previous_results),
                'reason': f'Error: {str(e)}'
            }
    
    async def _execute_agent(self, agent_name: str, query: str, conversation_history: list = None) -> str:
        """Execute a query with a specific agent."""
        agent = self.agents[agent_name]
        app_name = f"{agent_name}_agent"
        
        await self._ensure_session(app_name)
        
        runner = Runner(
            agent=agent,
            session_service=self.session_service,
            app_name=app_name
        )
        
        # Prepare conversation history if provided
        if conversation_history:
            content = types.Content(
                role="user",
                parts=[types.Part(text=f"Previous context: {conversation_history}\n\nUser query: {query}")]
            )
        else:
            content = types.Content(
                role="user",
                parts=[types.Part(text=query)]
            )
        
        session_id = self._get_session_id(app_name)
        
        # Suppress cleanup errors - these happen in background and don't affect functionality
        # The errors are from MCP connection cleanup happening in different event loops
        import sys
        from io import StringIO
        
        # Capture stderr to suppress cleanup errors
        old_stderr = sys.stderr
        stderr_buffer = StringIO()
        
        try:
            sys.stderr = stderr_buffer
            events = runner.run(
                user_id=self.user_id,
                session_id=session_id,
                new_message=content
            )
            
            # Get response
            agent_response = None
            for event in events:
                if event.is_final_response():
                    agent_response = event.content.parts[0].text
                    break
            
            return agent_response or "No response received from agent."
        finally:
            # Restore stderr
            sys.stderr = old_stderr
            
            # Suppress known cleanup errors from background tasks
            # These happen when MCP connections are cleaned up asynchronously
            # They don't affect functionality but create noise
            error_output = stderr_buffer.getvalue()
            # Filter out known harmless cleanup errors
            if error_output and not any(
                err in error_output 
                for err in [
                    "Task exception was never retrieved",
                    "Attempted to exit cancel scope in a different task",
                    "is bound to a different event loop",
                    "Error during disconnected session cleanup",
                    "generator didn't stop after athrow()"
                ]
            ):
                # Only print if it's a real error
                print(error_output, file=old_stderr)
    
    async def process_query(self, query: str, show_usage: bool = False, max_iterations: int = 5, silent: bool = False) -> str:
        """
        Process a user query using Supervisor Agent Architecture.
        
        The supervisor (router) decides the first agent, evaluates results, and
        iteratively decides if more agents are needed until the query is complete.
        
        Args:
            query: The user's query
            show_usage: Whether to show token usage statistics
            max_iterations: Maximum number of agent iterations to prevent infinite loops
            
        Returns:
            The combined agent response
        """
        if not silent:
            print(colored("="*70, "magenta"))
            print(colored(f"👤 USER: {query}", "cyan", attrs=["bold"]))
            print(colored("="*70, "magenta"))
            print()
        
        try:
            results = []
            iteration = 0
            done = False
            
            # Supervisor loop
            while not done and iteration < max_iterations:
                iteration += 1
                
                # Ask supervisor for next decision
                if not silent:
                    if iteration == 1:
                        print(colored("🎯 SUPERVISOR: Initial routing decision...", "cyan"))
                    else:
                        print(colored(f"🎯 SUPERVISOR: Evaluating results (iteration {iteration})...", "cyan"))
                
                decision = await self._supervisor_decide(query, previous_results=results if results else None)
                
                # Callback for routing decision
                if self.handoff_callback and iteration == 1:
                    self.handoff_callback('routing', {
                        'query': query,
                        'decision': decision,
                        'iteration': iteration
                    })
                
                if not silent:
                    print(colored(f"   Decision: {decision['reason']}", "yellow"))
                
                # Check if done
                if decision['done'] or decision['next_agent'] is None:
                    if not silent:
                        print(colored("   ✓ Supervisor: Query complete!", "green"))
                    
                    # Callback for completion
                    if self.handoff_callback:
                        self.handoff_callback('completion', {
                            'query': query,
                            'results': results,
                            'iteration': iteration
                        })
                    
                    done = True
                    break
                
                # Execute next agent
                next_agent = decision['next_agent']
                
                # Callback for handoff
                if self.handoff_callback:
                    previous_agent = results[-1]['agent'] if results else None
                    self.handoff_callback('handoff', {
                        'from_agent': previous_agent,
                        'to_agent': next_agent,
                        'iteration': iteration,
                        'reason': decision['reason']
                    })
                
                if not silent:
                    print(colored(f"   → Next agent: {next_agent}_agent", "yellow"))
                    print()
                
                # Prepare query with previous context
                if results:
                    context_query = f"""Previous agent results:
{chr(10).join(f"- {r['agent']}_agent: {r['response'][:300]}..." for r in results)}

Original user query: {query}

Based on the previous results, continue processing the query."""
                else:
                    context_query = query
                
                if not silent:
                    print(colored(f"🔄 Executing: {next_agent}_agent", "cyan"))
                
                response = await self._execute_agent(next_agent, context_query, 
                                                     [r['response'] for r in results] if results else None)
                
                results.append({
                    'agent': next_agent,
                    'response': response
                })
                
                # Callback for agent completion
                if self.handoff_callback:
                    self.handoff_callback('agent_complete', {
                        'agent': next_agent,
                        'response_preview': response[:100] + "..." if len(response) > 100 else response,
                        'iteration': iteration
                    })
                
                if not silent:
                    print(colored(f"   ✓ {next_agent}_agent completed", "green"))
                    print()
            
            # Safety check for max iterations
            if iteration >= max_iterations and not done:
                if not silent:
                    print(colored(f"⚠️  Reached max iterations ({max_iterations}), stopping", "yellow"))
                    print()
            
            # Combine and return results
            if len(results) == 1:
                final_response = results[0]['response']
                if not silent:
                    print(colored("🤖 FINAL RESPONSE:", "green", attrs=["bold"]))
                    print(final_response)
                    print()
                return final_response
            else:
                combined_response = "\n\n".join([
                    f"**{r['agent'].replace('_', ' ').title()} Agent:**\n{r['response']}"
                    for r in results
                ])
                if not silent:
                    print(colored("🤖 FINAL COMBINED RESPONSE:", "green", attrs=["bold"]))
                    print(combined_response)
                    print()
                return combined_response
            
        except Exception as e:
            error_msg = f"❌ Error processing query: {e}"
            print(colored(error_msg, "red"))
            import traceback
            traceback.print_exc()
            print()
            return error_msg


# Create a default orchestrator instance
_orchestrator = None

def get_orchestrator() -> A2AOrchestrator:
    """Get or create the default orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = A2AOrchestrator()
    return _orchestrator

async def process(query: str, thread_id: str = "default", show_usage: bool = False, silent: bool = False) -> str:
    """
    Convenience function to process a query.
    
    Uses Supervisor Agent Architecture where the router supervises agent execution
    and decides if additional agents are needed based on results.
    
    Args:
        query: The user's query
        thread_id: Thread ID for conversation continuity
        show_usage: Whether to show token usage statistics
        
    Returns:
        The agent's response
    """
    orchestrator = get_orchestrator(handoff_callback=handoff_callback)
    orchestrator.session_id = thread_id
    orchestrator.user_id = f"user_{thread_id}"
    return await orchestrator.process_query(query, show_usage, silent=silent)

# Alias for convenience (alternative name)
ask_agent = process


if __name__ == "__main__":
    import asyncio
    
    print(colored("🚀 A2A-MCP Orchestrator (Google ADK)", "cyan", attrs=["bold"]))
    print(colored(f"💡 Note: Make sure MCP server is running at {MCP_HTTP_BASE_URL}", "yellow"))
    print()
    
    async def main():
        orch = A2AOrchestrator()
        
        # Test queries
        test_queries = [
            "Get customer 1",
            "Show me all active customers",
            "Create a ticket for customer 2 with issue 'Cannot login'",
        ]
        
        for query in test_queries:
            await orch.process_query(query)
            print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(colored("\n🛑 Interrupted by user", "yellow"))
    except Exception as e:
        print(colored(f"\n❌ Error: {e}", "red"))
        print(colored("💡 Make sure:", "yellow"))
        print(colored("   1. MCP server is running: python customer_mcp/server/mcp_server.py", "yellow"))
        print(colored("   2. API keys are set in .env file", "yellow"))
        sys.exit(1)

