"""
Chatbot Interface for A2A-MCP Orchestrator
Provides a conversational chatbot experience with history and formatting
"""
import sys
from termcolor import colored
from datetime import datetime
from a2a.orchestrator import A2AOrchestrator, process
from a2a.utils import MCP_HTTP_BASE_URL


def print_chat_header():
    """Print chatbot welcome header."""
    print("\n" + "=" * 70)
    print(colored("🤖 Customer Support Chatbot", "cyan", attrs=["bold"]))
    print("=" * 70)
    print(colored("💡 I can help you with:", "yellow"))
    print("   • Customer information and management")
    print("   • Support ticket creation and tracking")
    print("   • Complex data queries")
    print(colored("\n💬 Type 'exit', 'quit', or 'bye' to end the conversation", "green"))
    print(colored("   Type 'clear' to reset conversation history\n", "green"))
    print("-" * 70 + "\n")


def format_chat_message(role: str, content: str, timestamp: bool = True):
    """Format a chat message with proper styling."""
    time_str = datetime.now().strftime("%H:%M:%S") if timestamp else ""
    
    if role == "user":
        print(colored(f"👤 You ({time_str}):", "blue", attrs=["bold"]))
        print(f"   {content}\n")
    elif role == "assistant":
        print(colored(f"🤖 Assistant ({time_str}):", "cyan", attrs=["bold"]))
        # Format response with proper indentation
        lines = content.strip().split('\n')
        for line in lines:
            print(f"   {line}")
        print()


def print_typing_indicator():
    """Show typing indicator."""
    print(colored("   💭 Thinking...", "yellow"))


def handoff_display_callback(event_type: str, data: dict):
    """Display agent handoffs and routing decisions in chatbot."""
    if event_type == 'routing':
        decision = data.get('decision', {})
        next_agent = decision.get('next_agent')
        if next_agent:
            agent_display_name = next_agent.replace('_', ' ').title()
            print(colored(f"   🔀 Routing to: {agent_display_name} Agent", "cyan"))
            print(colored(f"      Reason: {decision.get('reason', 'N/A')}", "yellow"))
    
    elif event_type == 'handoff':
        from_agent = data.get('from_agent')
        to_agent = data.get('to_agent')
        reason = data.get('reason', '')
        
        if from_agent and to_agent:
            from_display = from_agent.replace('_', ' ').title()
            to_display = to_agent.replace('_', ' ').title()
            print(colored(f"   🔄 Handoff: {from_display} → {to_display} Agent", "magenta"))
            if reason:
                print(colored(f"      Reason: {reason}", "yellow"))
        else:
            to_display = to_agent.replace('_', ' ').title()
            print(colored(f"   ➡️  Executing: {to_display} Agent", "cyan"))
    
    elif event_type == 'agent_complete':
        agent = data.get('agent', '')
        agent_display = agent.replace('_', ' ').title()
        print(colored(f"   ✅ {agent_display} Agent completed", "green"))
    
    elif event_type == 'completion':
        results = data.get('results', [])
        if len(results) > 1:
            agent_list = [r['agent'].replace('_', ' ').title() for r in results]
            print(colored(f"   ✨ Completed with {len(results)} agents: {', '.join(agent_list)}", "green"))


def chatbot_session():
    """Run an interactive chatbot session."""
    print_chat_header()
    
    # Initialize orchestrator with handoff callback
    print(colored("🔄 Initializing chatbot...", "yellow"))
    try:
        orchestrator = A2AOrchestrator(handoff_callback=handoff_display_callback)
        print(colored("✅ Ready! Let's chat!\n", "green"))
    except Exception as e:
        print(colored(f"❌ Error initializing: {e}", "red"))
        print(colored(f"💡 Make sure MCP server is running at {MCP_HTTP_BASE_URL}", "yellow"))
        return
    
    conversation_count = 0
    
    while True:
        try:
            # Get user input
            user_input = input(colored("👤 You: ", "blue", attrs=["bold"])).strip()
            
            # Handle special commands
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                print(colored("\n👋 Goodbye! Thanks for chatting!\n", "green"))
                break
            
            if user_input.lower() == 'clear':
                print(colored("\n🔄 Conversation history cleared\n", "yellow"))
                orchestrator = A2AOrchestrator(handoff_callback=handoff_display_callback)
                conversation_count = 0
                continue
            
            if user_input.lower() in ['help', '?']:
                print(colored("\n📚 Help:", "cyan"))
                print("   • Just ask me questions about customers, tickets, or data")
                print("   • Examples:")
                print("     - 'Get customer 1'")
                print("     - 'Show me all active customers'")
                print("     - 'Create a ticket for customer 2'")
                print("   • Type 'clear' to reset conversation")
                print("   • Type 'exit' to quit\n")
                continue
            
            # Process the query
            conversation_count += 1
            print(colored("   💭 Thinking...", "yellow"))
            
            try:
                import asyncio
                # Use silent mode but show handoffs via callback
                # Update orchestrator callback for this query
                orchestrator.handoff_callback = handoff_display_callback
                orchestrator.session_id = "chat_session"
                orchestrator.user_id = f"user_chat_{conversation_count}"
                
                response = asyncio.run(orchestrator.process_query(user_input, show_usage=False, silent=True))
                
                # Format and display response in chat style
                print()  # Space before response
                print(colored("🤖 Assistant:", "cyan", attrs=["bold"]))
                # Clean up response formatting
                response = response.strip()
                lines = response.split('\n')
                for line in lines:
                    # Skip empty lines or markdown headers in combined responses
                    if line.strip() and not line.strip().startswith('**') and not line.strip().endswith('**'):
                        print(f"   {line}")
                    elif line.strip().startswith('**') and line.strip().endswith('**'):
                        # Make section headers more readable
                        header = line.strip().replace('**', '').replace('_', ' ')
                        print(colored(f"\n   {header}:", "yellow", attrs=["bold"]))
                print()  # Space after response
                
            except KeyboardInterrupt:
                print(colored("\n⚠️  Interrupted. Type 'exit' to quit or continue chatting.\n", "yellow"))
                continue
            except Exception as e:
                print(colored(f"\n❌ Error: {str(e)}", "red"))
                print(colored("💡 Please try again or type 'exit' to quit\n", "yellow"))
                continue
                
        except KeyboardInterrupt:
            print(colored("\n\n👋 Goodbye! Thanks for chatting!\n", "green"))
            break
        except EOFError:
            print(colored("\n\n👋 Goodbye! Thanks for chatting!\n", "green"))
            break


if __name__ == "__main__":
    try:
        chatbot_session()
    except KeyboardInterrupt:
        print(colored("\n\n👋 Goodbye!\n", "green"))
        sys.exit(0)

