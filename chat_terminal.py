#!/usr/bin/env python3
"""
Terminal Chat Client for A2A-MCP
Uses orchestrator directly 
Just needs MCP server running.
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import requests
from a2a.langgraph_orchestrator import LangGraphOrchestrator
from a2a.a2a_logger import get_a2a_logger

# MCP Server URL (for health check)
MCP_SERVER_URL = "http://localhost:8001"

def check_mcp_server():
    """Check if MCP server is running."""
    try:
        response = requests.get(f"{MCP_SERVER_URL}/health", timeout=2)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def print_response(result: dict, a2a_summary: dict):
    """Pretty print the response."""
    print("\n" + "="*70)
    
    # Main response
    response_text = result.get('response', 'No response received')
    print(f"Agent Response:\n{response_text}")
    
    # Agent info
    route = result.get('route', 'unknown')
    print(f"\n Primary Agent: {route}")
    
    # A2A info
    interactions = a2a_summary.get('interactions', [])
    a2a_count = len(interactions)
    if a2a_count > 0:
        print(f" A2A Interactions: {a2a_count}")
        print("\n   A2A Coordination:")
        for i, interaction in enumerate(interactions[:3], 1):  # Show first 3
            from_agent = interaction.get('from_agent', 'unknown')
            to_agent = interaction.get('to_agent', 'unknown')
            print(f"   {i}. {from_agent} → {to_agent}")
    
    print("="*70 + "\n")

def main():
    """Main chat loop."""
    print("="*70)
    print("  A2A-MCP Terminal Chat")
    print("="*70)
    print("\n💡 Tips:")
    print("   - Type 'quit' or 'exit' to leave")
    print("   - Type 'clear' to clear conversation history")
    print("   - Try: 'List customers', 'Create a ticket', etc.")
    print("\n" + "="*70 + "\n")
    
    # Check MCP server
    if not check_mcp_server():
        print("MCP Server is not running!")
        print(f"   Please start it with: python customer_mcp/server/mcp_server.py")
        print(f"   Make sure it's running on {MCP_SERVER_URL}")
        sys.exit(1)
    
    print(" MCP Server is running!")
    print(" Initializing orchestrator...")
    
    # Initialize orchestrator
    try:
        orchestrator = LangGraphOrchestrator()
        print(" Orchestrator ready!\n")
    except Exception as e:
        print(f" Failed to initialize orchestrator: {e}")
        print("   Make sure:")
        print("   1. MCP server is running")
        print("   2. OpenAI API key is set in .env")
        print("   3. Database exists (Database/support.db)")
        sys.exit(1)
    
    # Get A2A logger
    a2a_logger = get_a2a_logger()
    
    thread_id = "terminal"
    conversation_count = 0
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n Goodbye!\n")
                break
            
            if user_input.lower() == 'clear':
                thread_id = f"terminal_{conversation_count}"
                conversation_count += 1
                print(" Conversation cleared. Starting new thread.\n")
                continue
            
            # Process message
            print(" Processing...")
            try:
                result = orchestrator.process(user_input, thread_id=thread_id)
                a2a_summary = a2a_logger.get_summary()
                print_response(result, a2a_summary)
            except Exception as e:
                print(f"\n Error processing message: {e}\n")
                import traceback
                traceback.print_exc()
        
        except KeyboardInterrupt:
            print("\n\n Goodbye!\n")
            break
        except EOFError:
            print("\n\n Goodbye!\n")
            break
        except Exception as e:
            print(f"\n Unexpected error: {e}\n")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
