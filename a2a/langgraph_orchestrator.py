"""
LangGraph-based Orchestrator with Parallel Execution and Memory
"""
import sys
import os
from typing import TypedDict, Annotated, Sequence, List, Dict, Any
import operator

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langgraph.graph import StateGraph, END #StateGraph is the graph object, END is the end state
from langgraph.checkpoint.memory import MemorySaver

from a2a.agent.router_agent import router_agent
from a2a.agent.customer_data_agent import customer_data_agent
from a2a.agent.support_agent import support_agent
from a2a.agent.fallback_sql_generator_agent import fallback_sql_generator_agent
from a2a.agent_card import get_agent_registry
import httpx


# Define the state schema
class AgentState(TypedDict):
    """State that flows through the graph."""
    query: str
    route: str
    conversation_history: Annotated[List[Dict[str, str]], operator.add]
    customer_data_result: str
    support_result: str
    sql_result: str
    final_response: str


class LangGraphOrchestrator:
    """
    LangGraph-based orchestrator with parallel execution, routing, and memory.
    """
    
    def __init__(self):
        """Initialize the LangGraph orchestrator."""
        # MCP Server HTTP configuration (orchestrator calls MCP server directly)
        self.mcp_server_url = os.getenv('MCP_HTTP_BASE_URL', 'http://localhost:8001')
        self.http_client = httpx.Client(timeout=30.0)
        
        self.router = router_agent()
        
        # Initialize agents - they'll call MCP server via orchestrator's HTTP client
        self.customer_data_agent = customer_data_agent(mcp_server_url=self.mcp_server_url)
        self.support_agent = support_agent(mcp_server_url=self.mcp_server_url)
        self.sql_agent = fallback_sql_generator_agent(mcp_server_url=self.mcp_server_url)
        
        # Get agent registry for A2A coordination
        self.agent_registry = get_agent_registry()
        
        # Create memory saver for conversation history
        self.memory = MemorySaver()
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("route", self._route_query)
        workflow.add_node("customer_data", self._call_customer_data)
        workflow.add_node("support", self._call_support)
        workflow.add_node("sql", self._call_sql)
        workflow.add_node("merge", self._merge_results)
        
        # Set entry point
        workflow.set_entry_point("route")
        
        # Add conditional edges from routing
        workflow.add_conditional_edges(
            "route",
            self._decide_next,
            {
                "customer_data": "customer_data",
                "support": "support",
                "sql": "sql",
            }
        )
        
        # Connect agent nodes to merge
        workflow.add_edge("customer_data", "merge")
        workflow.add_edge("support", "merge")
        workflow.add_edge("sql", "merge")
        
        # End after merge
        workflow.add_edge("merge", END)
        
        # Compile with memory
        return workflow.compile(checkpointer=self.memory)
    
    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """Format conversation history for agents."""
        if not history:
            return ""
        
        formatted = []
        for msg in history[-10:]:  # Last 10 messages
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                formatted.append(f"User: {content}")
            elif role == "agent":
                agent_name = msg.get("agent", "agent")
                formatted.append(f"{agent_name}: {content}")
        
        return "\n".join(formatted)
    
    def _route_query(self, state: AgentState) -> AgentState:
        """Route the query to ONE agent. Agent will use A2A if it needs help from others."""
        query = state["query"]
        
        # Use router to pick PRIMARY agent
        # The agent's LLM will decide if it needs help from others
        route = self.router.route(query)
        
        print(f" Routing to: {route} (agent will coordinate with others if needed)")
        
        return {
            **state,
            "route": route,
        }
    
    def _check_parallel_needs(self, query: str) -> bool:
        """
        Determine if query needs parallel execution.
        
        Examples:
        - "Get customer 5 and create a ticket" -> parallel
        - "Show customers and their tickets" -> parallel
        - "Just list customers" -> single
        """
        parallel_keywords = [
            " and ",
            " then ",
            "both",
            "also",
            "plus",
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in parallel_keywords)
    
    def _decide_next(self, state: AgentState) -> str:
        """Route to primary agent. With A2A coordination, agents coordinate themselves."""
        return state["route"]
    
    def _call_customer_data(self, state: AgentState) -> AgentState:
        """Execute customer data agent with A2A coordination via agent cards."""
        query = state["query"]
        history = self._format_history(state.get("conversation_history", []))
        
        # Pass agent cards (not raw agents)
        # Agent can read cards to decide who to ask for help
        agent_cards_context = self.agent_registry.get_cards_for_context(
            exclude=['customer_data']  # Don't include self
        )
        
        # Pass both cards (for LLM reasoning) and actual agents (for invocation)
        other_agents = {
            "cards": agent_cards_context,
            "support": self.support_agent,
            "sql": self.sql_agent
        }
        
        result = self.customer_data_agent.process(
            query,
            conversation_history=history,
            other_agents=other_agents
        )
        
        return {
            **state,
            "customer_data_result": result,
        }
    
    def _call_support(self, state: AgentState) -> AgentState:
        """Execute support agent with A2A coordination."""
        query = state["query"]
        history = self._format_history(state.get("conversation_history", []))
        
        # Pass agent cards for decision making
        agent_cards_context = self.agent_registry.get_cards_for_context(
            exclude=['support']  # Don't include self
        )
        
        other_agents = {
            "cards": agent_cards_context,
            "customer_data": self.customer_data_agent,
            "sql": self.sql_agent
        }
        
        result = self.support_agent.process(
            query,
            conversation_history=history,
            other_agents=other_agents
        )
        
        return {
            **state,
            "support_result": result,
        }
    
    def _call_sql(self, state: AgentState) -> AgentState:
        """Execute SQL generator agent with A2A coordination."""
        query = state["query"]
        history = self._format_history(state.get("conversation_history", []))
        
        # Pass agent cards for decision making
        agent_cards_context = self.agent_registry.get_cards_for_context(
            exclude=['sql']  # Don't include self
        )
        
        other_agents = {
            "cards": agent_cards_context,
            "customer_data": self.customer_data_agent,
            "support": self.support_agent
        }
        
        result = self.sql_agent.process(
            query,
            conversation_history=history,
            other_agents=other_agents
        )
        
        return {
            **state,
            "sql_result": result,
        }
    
    def _merge_results(self, state: AgentState) -> AgentState:
        """Merge results from all executed agents."""
        route = state["route"]
        
        # Collect non-empty results
        results = []
        
        if state.get("customer_data_result"):
            results.append(("customer_data", state["customer_data_result"]))
        
        if state.get("support_result"):
            results.append(("support", state["support_result"]))
        
        if state.get("sql_result"):
            results.append(("sql", state["sql_result"]))
        
        # Merge based on execution mode
        if len(results) > 1:
            # Parallel execution - combine all results
            final = "Combined Results:\n\n"
            for agent_name, result in results:
                final += f"[{agent_name}]\n{result}\n\n"
        elif len(results) == 1:
            # Single agent execution
            final = results[0][1]
        else:
            final = "No results generated"
        
        # Update conversation history
        new_history = [
            {"role": "user", "content": state["query"]},
            {"role": "agent", "agent": route, "content": final}
        ]
        
        return {
            **state,
            "final_response": final,
            "conversation_history": new_history,
        }
    
    def process(self, query: str, thread_id: str = "default") -> Dict[str, Any]:
        """
        Process a query through the LangGraph workflow.
        
        Args:
            query: User's query
            thread_id: Thread ID for conversation memory
            
        Returns:
            Dict with response and metadata
        """
        # Initial state
        initial_state = {
            "query": query,
            "route": "",
            "conversation_history": [],
            "customer_data_result": "",
            "support_result": "",
            "sql_result": "",
            "final_response": "",
        }
        
        # Configure with thread ID for memory
        config = {"configurable": {"thread_id": thread_id}}
        
        # Run the graph
        final_state = self.graph.invoke(initial_state, config)
        
        return {
            "response": final_state["final_response"],
            "route": final_state["route"],
            "thread_id": thread_id,
        }
    
    def get_conversation_history(self, thread_id: str = "default") -> List[Dict]:
        """Get conversation history for a thread."""
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get state from memory
        state = self.graph.get_state(config)
        
        if state and state.values:
            return state.values.get("conversation_history", [])
        
        return []


def create_langgraph_orchestrator() -> LangGraphOrchestrator:
    """
    Factory function to create a LangGraph orchestrator.
    
    Returns:
        Configured LangGraphOrchestrator instance
    """
    return LangGraphOrchestrator()


# Demo usage
if __name__ == "__main__":
    print("LangGraph Orchestrator with Parallel Execution")
    print("=" * 60)
    print()
    
    # Create orchestrator
    orch = create_langgraph_orchestrator()
    
    # Test 1: Single agent routing
    print("<b> Test 1: Single Agent Routing</b>")
    print("-" * 60)
    result = orch.process("Show me all active customers", thread_id="demo1")
    print(f"Query: Show me all active customers")
    print(f"Route: {result['route']}")
    print(f"Parallel: {result['parallel_execution']}")
    print(f"Response: {result['response']}")
    print()
    
    # Test 2: Contextual follow-up
    print("<b> Test 2: Contextual Follow-up</b>")
    print("-" * 60)
    result = orch.process("Create a ticket for customer 5", thread_id="demo1")
    print(f"Query: Create a ticket for customer 5")
    print(f"Route: {result['route']}")
    print(f"Response: {result['response']}")
    print()
    
    # Test 3: Parallel execution
    print("<b> Test 3: Parallel Execution Detection</b>")
    print("-" * 60)
    result = orch.process(
        "Get customer details and create a ticket",
        thread_id="demo2"
    )
    print(f"Query: Get customer details and create a ticket")
    print(f"Route: {result['route']}")
    print(f"Parallel: {result['parallel_execution']}")
    print(f"Response: {result['response'][:100]}...")
    print()
    
    # Show conversation history
    print("Conversation History (Thread: demo1)")
    print("-" * 60)
    history = orch.get_conversation_history("demo1")
    for msg in history:
        role = msg.get("role", "")
        content = msg.get("content", "")[:80]
        if role == "user":
            print(f"<b> User: {content}</b>")
        else:
            agent = msg.get("agent", "agent")
            print(f"<b> {agent}: {content}</b>")
    print()
    
    print("<b> LangGraph Orchestrator Ready!</b> <span style='color: green;'>green text</span>")

