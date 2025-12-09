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

# This allows absolute imports to work when running directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from a2a.utils import MCP_HTTP_BASE_URL

# Configure logging  ADK handles its own logging via GOOGLE_SDK_PYTHON_LOGGING_SCOPE env var
# Only suppress if explicitly requested via environment variable
if os.getenv('SUPPRESS_ADK_LOGS', 'false').lower() == 'true':
    logging.getLogger('google.adk').setLevel(logging.CRITICAL)
    logging.getLogger('google.genai').setLevel(logging.CRITICAL)
    logging.getLogger('asyncio').setLevel(logging.CRITICAL)

# Suppress app name mismatch warnings - this is expected when using programmatically created agents
# The LlmAgent class comes from google.adk.agents, but we use our own app names
# Apply this suppression early and comprehensively
_adk_runners_logger = logging.getLogger('google.adk.runners')
_adk_runners_logger.setLevel(logging.ERROR)  # Suppress WARNING, keep ERROR
_adk_runners_logger.propagate = False  # Prevent propagation to root logger

# Also suppress warnings at the warning module level
import warnings
warnings.filterwarnings('ignore', message='.*App name mismatch detected.*')

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
# Import agents - wrap in try-except to handle MCP connection issues during import
# Agents are created at module import time, but MCP connections happen lazily
try:
    from .agent.router_agent import router_agent
    from .agent.customer_data_agent import customer_data_agent
    from .agent.support_agent import support_agent
    from .agent.fallback_sql_generator_agent import fallback_sql_generator_agent
except ImportError:
    # Fallback to absolute imports when running as script
    try:
        from a2a.agent.router_agent import router_agent
        from a2a.agent.customer_data_agent import customer_data_agent
        from a2a.agent.support_agent import support_agent
        from a2a.agent.fallback_sql_generator_agent import fallback_sql_generator_agent
    except Exception as e:
        # If agent import fails, we'll handle it in orchestrator initialization
        print(colored(f"⚠️  Warning: Agent import had issues: {e}", "yellow"))
        print(colored(" Agents will be created when needed. Make sure MCP server is running.", "cyan"))
        router_agent = None
        customer_data_agent = None
        support_agent = None
        fallback_sql_generator_agent = None
except Exception as e:
    # Handle any other import errors (like MCP connection issues)
    print(colored(f"⚠️  Warning: Agent creation encountered issues: {e}", "yellow"))
    print(colored(" This is normal if MCP server isn't running yet.", "cyan"))
    print(colored("   Agents will connect to MCP server when first used.", "cyan"))
    # Agents might still be created, continue
    pass


class A2AOrchestrator:
    """Orchestrator that coordinates multi-agent execution.
    
    Responsibilities:
    - Coordinates agent execution flow
    - Manages sessions and conversation history
    - Passes queries to router agent for routing decisions
    - Executes agents based on router's decisions
    - Does NOT make routing decisions (router agent handles all routing)
    """
    
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
        self.handoff_callback = handoff_callback
        self.conversation_history = []
        
        # Agent mapping
        self.agents = {
            'customer_data': customer_data_agent,
            'support': support_agent,
            'sql': fallback_sql_generator_agent,
        }
        
    
    def _get_session_id(self, app_name: str) -> str:
        """Get the session ID for an agent."""
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

    def _extract_response_from_events(self, events) -> str:
        """Extract text response from event stream."""
        agent_response = None
        accumulated_text = []
        
        try:
            for event in events:
                event_text = None
                
                # Extract text from event
                if event.is_final_response():
                    if hasattr(event, 'content') and event.content:
                        if hasattr(event.content, 'parts') and event.content.parts:
                            for part in event.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    event_text = part.text
                                    break
                        elif hasattr(event.content, 'text') and event.content.text:
                            event_text = event.content.text
                
                if not event_text and hasattr(event, 'text') and event.text:
                    event_text = event.text
                
                if not event_text and hasattr(event, 'content') and hasattr(event.content, 'text'):
                    event_text = event.content.text
                
                if event_text:
                    accumulated_text.append(event_text)
                    if event.is_final_response():
                        agent_response = event_text
        except StopIteration:
            pass
        except (ConnectionError, TimeoutError) as e:
            error_str = str(e).lower()
            if 'failed to get tools' in error_str or 'connection' in error_str or 'timeout' in error_str:
                raise ConnectionError(f"MCP server connection failed")
            raise
        
        return agent_response or (" ".join(accumulated_text) if accumulated_text else None)
    
    def _emergency_fallback(self, query: str) -> dict:
        """Emergency fallback only when router agent completely fails."""
        return {
            'next_agent': 'customer_data',
            'done': False,
            'reason': 'Emergency fallback: Router unavailable'
        }
    
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
        
        # Default fallback when router response cannot be parsed
        return {
            'next_agent': 'customer_data',
            'done': False,
            'reason': 'Could not parse router decision'
        }
    
    async def _supervisor_decide(self, query: str, previous_results: list = None) -> dict:
        """Ask supervisor router to decide next agent or if done."""
        try:
            # Use router_agent.name which should be "router_agent"
            agent_app_name = router_agent.name if hasattr(router_agent, 'name') else "router_agent"
            await self._ensure_session(agent_app_name)
            
            # Create router runner
            router_runner = Runner(
                agent=router_agent,
                app_name=agent_app_name,
                session_service=self.session_service
            )
            
            # Build context for router agent
            context_parts = []
            
            if self.conversation_history:
                recent_history = "\n".join([
                    f"User: {h.get('user', '')}\nAssistant: {h.get('assistant', '')[:200]}..."
                    for h in self.conversation_history[-3:]
                ])
                context_parts.append(f"PREVIOUS CONVERSATION CONTEXT:\n{recent_history}")
            
            if previous_results:
                results_summary = "\n".join([
                    f"Agent: {r['agent']}\nResponse: {r['response'][:300]}..."
                    for r in previous_results
                ])
                context_parts.append(f"PREVIOUS AGENT RESULTS:\n{results_summary}")
            
            # Let router agent use its own instructions - just provide query and context
            router_query = query
            if context_parts:
                router_query = f"{query}\n\n" + "\n\n".join(context_parts)
            
            content = types.Content(
                role="user",
                parts=[types.Part(text=router_query)]
            )
            
            session_id = self._get_session_id(agent_app_name)
            
            # Get router response
            events = router_runner.run(
                user_id=self.user_id,
                session_id=session_id,
                new_message=content
            )
            router_response = self._extract_response_from_events(events)
            if router_response:
                return self._parse_supervisor_decision(router_response)
            else:
                if previous_results and len(previous_results) > 0:
                    return {'next_agent': None, 'done': True, 'reason': 'Query answered by previous agent'}
                return self._emergency_fallback(query)
                
        except (ConnectionError, TimeoutError) as e:
            error_str = str(e).lower()
            if 'connection' in error_str or 'timeout' in error_str or 'failed to get tools' in error_str:
                if previous_results and len(previous_results) > 0:
                    return {'next_agent': None, 'done': True, 'reason': 'Query answered by previous agent'}
                return self._emergency_fallback(query)
            raise
        except Exception as e:
            if previous_results and len(previous_results) > 0:
                return {'next_agent': None, 'done': True, 'reason': 'Query answered by previous agent'}
            return self._emergency_fallback(query)
    
    async def _execute_agent(self, agent_name: str, query: str, conversation_history: list = None) -> str:
        """Execute a query with a specific agent."""
        agent = self.agents[agent_name]
        # Get app name from agent (should be something like "customer_data_agent", "support_agent")
        agent_app_name = agent.name if hasattr(agent, 'name') else f"{agent_name}_agent"
        
        await self._ensure_session(agent_app_name)
        
        # Create runner with agent name as app_name for consistency
        runner = Runner(
            agent=agent,
            app_name=agent_app_name,
            session_service=self.session_service
        )
        
        # Build context-aware query with conversation history
        context_text = ""
        if self.conversation_history:
            recent_context = []
            for h in self.conversation_history[-3:]:  # Last 3 exchanges
                if h.get('user'):
                    recent_context.append(f"Previous user message: {h['user']}")
                if h.get('assistant'):
                    recent_context.append(f"Previous assistant response: {h['assistant'][:300]}...")
            
            if recent_context:
                context_text = f"\n\nCONVERSATION CONTEXT (for reference):\n" + "\n".join(recent_context) + "\n"
        
        # Include agent-specific conversation history if provided
        if conversation_history:
            context_text += f"\nPrevious agent results: {conversation_history}\n"
        
        # Combine query with context
        full_query = query
        if context_text:
            full_query = f"{query}{context_text}\n\nIMPORTANT: Use the conversation context to understand references (e.g., 'his tickets' refers to the customer mentioned earlier)."
        
        content = types.Content(
            role="user",
            parts=[types.Part(text=full_query)]
        )
        
        session_id = self._get_session_id(agent_app_name)
        
        # Execute agent and get response
        try:
            events = runner.run(
                user_id=self.user_id,
                session_id=session_id,
                new_message=content
            )
            agent_response = self._extract_response_from_events(events)
            return agent_response or "No response received from agent."
        except (ConnectionError, TimeoutError) as e:
            error_str = str(e).lower()
            if 'failed to get tools' in error_str or 'connection' in error_str or 'timeout' in error_str:
                raise ConnectionError(f"MCP server connection failed")
            raise
    
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
        
        try:
            results = []
            iteration = 0
            done = False
            
            # Supervisor loop
            while not done and iteration < max_iterations:
                iteration += 1
                
                decision = await self._supervisor_decide(query, previous_results=results if results else None)
                
                if self.handoff_callback and iteration == 1:
                    self.handoff_callback('routing', {
                        'query': query,
                        'decision': decision,
                        'iteration': iteration
                    })
                
                if decision['done'] or decision['next_agent'] is None:
                    if self.handoff_callback:
                        self.handoff_callback('completion', {
                            'query': query,
                            'results': results,
                            'iteration': iteration
                        })
                    done = True
                    break
                
                next_agent = decision['next_agent']
                
                if self.handoff_callback:
                    previous_agent = results[-1]['agent'] if results else None
                    self.handoff_callback('handoff', {
                        'from_agent': previous_agent,
                        'to_agent': next_agent,
                        'iteration': iteration,
                        'reason': decision['reason']
                    })
                
                if results:
                    context_query = f"""Previous agent results:
{chr(10).join(f"- {r['agent']}_agent: {r['response'][:500]}..." for r in results)}

Original user query: {query}

Continue processing based on previous results."""
                else:
                    context_query = query
                
                try:
                    response = await self._execute_agent(next_agent, context_query, 
                                                         [r['response'] for r in results] if results else None)
                except (ConnectionError, TimeoutError) as e:
                    error_str = str(e).lower()
                    if 'failed to get tools' in error_str or 'connection' in error_str or 'timeout' in error_str:
                        response = f"Error: MCP server connection failed. Ensure server is running at {MCP_HTTP_BASE_URL}/mcp"
                        results.append({'agent': next_agent, 'response': response})
                        done = True
                        break
                    raise
                
                results.append({'agent': next_agent, 'response': response})
                
                if self.handoff_callback:
                    self.handoff_callback('agent_complete', {
                        'agent': next_agent,
                        'response_preview': response[:100] + "..." if len(response) > 100 else response,
                        'iteration': iteration
                    })
            
            if iteration >= max_iterations and not done:
                if not silent:
                    print(colored(f"⚠️  Max iterations reached ({max_iterations})", "yellow"))
            
            if len(results) == 1:
                final_response = results[0]['response']
            else:
                final_response = "\n\n".join([
                    f"{r['agent'].replace('_', ' ').title()} Agent:\n{r['response']}"
                    for r in results
                ])
            
            self.conversation_history.append({
                'user': query,
                'assistant': final_response
            })
            
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return final_response
            
        except Exception as e:
            return f"Error: {str(e)}"


# Create a default orchestrator instance
_orchestrator = None

def get_orchestrator() -> A2AOrchestrator:
    """Get or create the default orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = A2AOrchestrator()
    return _orchestrator

async def process(query: str, thread_id: str = "default", show_usage: bool = False, silent: bool = False, handoff_callback=None) -> str:
    """
    Convenience function to process a query.
    
    Uses Supervisor Agent Architecture where the router supervises agent execution
    and decides if additional agents are needed based on results.
    
    Args:
        query: The user's query
        thread_id: Thread ID for conversation continuity
        show_usage: Whether to show token usage statistics
        silent: Whether to suppress output
        handoff_callback: Optional callback for handoff events
        
    Returns:
        The agent's response
    """
    orchestrator = get_orchestrator()
    if handoff_callback:
        orchestrator.handoff_callback = handoff_callback
    orchestrator.session_id = thread_id
    orchestrator.user_id = f"user_{thread_id}"
    return await orchestrator.process_query(query, show_usage, silent=silent)

# Alias for convenience (alternative name)
ask_agent = process


if __name__ == "__main__":
    import asyncio
    
    print(colored(" A2A-MCP Orchestrator (Google ADK)", "cyan", attrs=["bold"]))
    print(colored(f" Note: Make sure MCP server is running at {MCP_HTTP_BASE_URL}", "yellow"))
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
        print(colored("\n Interrupted by user", "yellow"))
    except Exception as e:
        print(colored(f"\n❌ Error: {e}", "red"))
        print(colored(" Make sure:", "yellow"))
        print(colored("   1. MCP server is running: python customer_mcp/server/mcp_server.py", "yellow"))
        print(colored("   2. API keys are set in .env file", "yellow"))
        sys.exit(1)

