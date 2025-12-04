"""
Interactive A2A-MCP System
Run this to interact with the multi-agent system
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from a2a.langgraph_orchestrator import LangGraphOrchestrator
from a2a.a2a_logger import get_a2a_logger, print_a2a_summary, export_a2a_log, reset_a2a_logger


def print_banner():
    """Print welcome banner"""
    print("\n" + "=" * 70)
    print("  Multi Agent Ticketing and Support System")
    print("=" * 70)
    print("\nFeatures:")
    print(" 1. Multi-agent orchestration (Router, Customer Data, Support, SQL)")
    print(" 2. MCP tool discovery (7 tools available)")
    print(" 3. TRUE Agent-to-Agent coordination (Task Allocation, Negotiation, Multi-step)")
    print(" 4. Multi-turn conversation with memory")
    print(" 5. Explicit A2A logging")
    print("\nCommands:")
    print("  • Type your query and press Enter")
    print("  • Type 'history' to see conversation history")
    print("  • Type 'a2a' to see A2A communication summary")
    print("  • Type 'export' to export A2A log to file")
    print("  • Type 'clear' to clear conversation history")
    print("  • Type 'help' for examples")
    print("  • Type 'quit' or 'exit' to exit")
    print("=" * 70 + "\n")


def print_help():
    """Print example queries"""
    print("\n" + "=" * 70)
    print("  📖 Example Queries")
    print("=" * 70)
    print("\n<b><span style='color: blue;'>Single Agent (No A2A):</span></b>")
    print("  • Get customer with ID 5")
    print("  • Show all active customers")
    print("  • Find all customers whose name starts with 'J'")
    print()
    print("<b><span style='color: green;'>TRUE A2A Coordination (Agents collaborate autonomously):</span></b>")
    print("  • Create a ticket for customer 3 about billing issue")
    print("     → Support agent will request customer info from customer_data agent")
    print("  • Get customer 1 and their ticket history")
    print("     → Customer agent will request tickets from support agent")
    print("  • Show me customers 2,3,4 and their open tickets")
    print("     → Watch for messages showing agent coordination!")
    print()
    print("Complex Queries:")
    print("  • Find customers created in the last 30 days with open tickets")
    print("  • Add customer Alice and create a ticket for her")
    print("  • Show active customers with open tickets")
    print()
    print("Multi-Agent (Parallel):")
    print("  • Get customer 5 and create a ticket")
    print("  • List customers and show their tickets")
    print("=" * 70 + "\n")


def main():
    """Main interactive loop"""
    print_banner()
    
    # Reset A2A logger for fresh session
    reset_a2a_logger()
    
    try:
        # Initialize orchestrator
        print("<b><span style='color: <h3>;'>Initializing orchestrator</h3></span></b>")
        orchestrator = LangGraphOrchestrator()
        print("<span style='color: green;'>System ready!</span>\n")
        print("<b>Tip: Type 'a2a' anytime to see agent coordination summary</b>\n")
        
        # Thread ID for conversation persistence
        thread_id = "interactive_session"
        
        # Interactive loop
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                # Handle commands
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n<b>Goodbye. Let me know if you need anything else!</b>\n")
                    break
                
                if user_input.lower() == 'help':
                    print_help()
                    continue
                
                if user_input.lower() == 'clear':
                    thread_id = f"interactive_session_{hash(user_input)}"  # New thread
                    print("<b>Conversation history cleared</b>\n")
                    continue
                
                if user_input.lower() == 'history':
                    # TODO: Implement history viewing
                    print("<b>History viewing not yet implemented</b>\n")
                    continue
                
                if user_input.lower() == 'a2a':
                    print_a2a_summary()
                    continue
                
                if user_input.lower() == 'export':
                    filename = f"a2a_log_{thread_id}.json"
                    export_a2a_log(filename)
                    print(f"<b>A2A log exported to {filename}</b>\n")
                    continue
                
                # Process query
                print("\n<b>Processing...</b>")
                print("-" * 70)
                
                result = orchestrator.process(user_input, thread_id=thread_id)
                
                # Display results
                print(f"\n<b><span style='color: blue;'>Primary Agent:</span> {result.get('route', 'unknown')}</b>")
                print(f"<b>Response:</b>\n")
                print(result.get('response', 'No response'))
                print("\n" + "=" * 70 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n <b>Goodbye. Let me know if you need anything else!</b>\n")
                break
            except Exception as e:
                print(f"\n<b><span style='color: red;'>Error:</span> {e}</b>")
                print("Please try again or type 'help' for examples\n")
    
    
    except Exception as e:
        print(f"\n<b><span style='color: red;'>Failed to initialize system:</span> {e}</b>")
        print("\nTroubleshooting:")
        print("  1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("  2. Check that .env file exists with OPENAI_API_KEY")
        print("  3. Verify database exists: python Database/database_setup.py")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()

