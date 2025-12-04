#!/usr/bin/env python3
"""
Quick start script for TRUE A2A-MCP
Checks dependencies before running main.py
"""
import sys
import subprocess
from pathlib import Path

print("\n" + "=" * 70)
print("  🚀 TRUE A2A-MCP Startup")
print("=" * 70 + "\n")

# Check if we're in a virtual environment
if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    print("⚠️  Warning: Not running in a virtual environment")
    print("   Recommended: source genaienv/bin/activate\n")
    response = input("Continue anyway? (y/n): ")
    if response.lower() != 'y':
        print("\n Run: source genaienv/bin/activate\n")
        sys.exit(0)

# Check for langgraph
try:
    import langgraph
    print()
except ImportError:
    print("❌ LangGraph not found")
    print("\nInstalling dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
        print("Dependencies installed\n")
    except subprocess.CalledProcessError:
        print("\n❌ Failed to install dependencies")
        print("   Try manually: pip install -r requirements.txt\n")
        sys.exit(1)

# Check for OpenAI API key
import os
from dotenv import load_dotenv

try:
    load_dotenv()
except Exception:
    pass

if not os.getenv('OPENAI_API_KEY'):
    print("\n❌ OPENAI_API_KEY not found")
    print("   Please set it in .env file or as environment variable:")
    print("   export OPENAI_API_KEY='your-key-here'\n")
    sys.exit(1)
else:
    print()

# Check database
db_path = Path(__file__).parent / 'Database' / 'support.db'
if not db_path.exists():
    print(f"\n❌ Database not found at {db_path}")
    print("   Run: python Database/database_setup.py\n")
    sys.exit(1)
else:
    print()

print("\n" + "=" * 70)
print("   All checks passed! Starting now...")
print("=" * 70 + "\n")

# Import and run main
from main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Goodbye. Let me know if you need anything else!\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()

