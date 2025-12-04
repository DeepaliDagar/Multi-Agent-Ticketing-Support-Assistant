"""
Flask API Backend for React Chatbot UI
Connects the React frontend to the A2A-MCP orchestrator
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from a2a.langgraph_orchestrator import LangGraphOrchestrator
from a2a.a2a_logger import get_a2a_logger

app = Flask(__name__)

# Configure CORS for your Vercel frontend
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",  # Local development
            "https://*.vercel.app",  # All Vercel deployments
            "https://multi-agent-ticketing-support-assistant-axqzj49qd.vercel.app"  # Your current Vercel deployment
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["*"],
        "supports_credentials": True
    }
})

# Store conversation threads
conversation_threads = {}

# Lazy-load orchestrator to handle initialization errors gracefully
orchestrator = None
orchestrator_error = None

def get_orchestrator():
    """Get or initialize the orchestrator with error handling."""
    global orchestrator, orchestrator_error
    if orchestrator is None and orchestrator_error is None:
        try:
            print("🔄 Initializing A2A-MCP orchestrator...")
            orchestrator = LangGraphOrchestrator()
            print("✅ Orchestrator ready!")
        except Exception as e:
            print(f"❌ Failed to initialize orchestrator: {e}")
            import traceback
            traceback.print_exc()
            orchestrator_error = str(e)
    return orchestrator, orchestrator_error

# Initialize orchestrator on startup (but don't crash if it fails)
print("🚀 Starting A2A-MCP Backend API...")
get_orchestrator()  # Try to initialize early, but app will still start if it fails

@app.route('/', methods=['GET'])
def root():
    """Root endpoint - simple test"""
    return jsonify({
        'message': 'A2A-MCP Backend API is running',
        'endpoints': {
            'health': '/health',
            'chat': '/chat (POST)',
            'logs': '/a2a/logs (GET)'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    orch, error = get_orchestrator()
    status = {
        'status': 'ok',
        'service': 'A2A-MCP Backend',
        'version': '1.0.0',
        'orchestrator': 'ready' if orch else 'error',
    }
    if error:
        status['orchestrator_error'] = error
    return jsonify(status)

@app.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat messages from React frontend
    
    Expected JSON:
    {
        "message": "user query",
        "thread_id": "optional thread id"
    }
    
    Returns:
    {
        "response": "agent response",
        "primary_agent": "agent name",
        "a2a_count": 2,
        "a2a_summary": [...]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message']
        thread_id = data.get('thread_id', 'default')
        
        print(f"\n📨 Received message: {user_message}")
        print(f"   Thread ID: {thread_id}")
        
        # Get orchestrator (lazy load)
        orch, error = get_orchestrator()
        if error:
            return jsonify({
                'error': f'Orchestrator initialization failed: {error}',
                'response': 'Backend is not properly initialized. Please check server logs.'
            }), 500
        
        # Process with orchestrator
        result = orch.process(user_message, thread_id=thread_id)
        
        # Get A2A summary
        a2a_logger = get_a2a_logger()
        a2a_summary = a2a_logger.get_summary()
        
        # Format response
        response = {
            'response': result.get('response', 'I apologize, but I encountered an issue.'),
            'primary_agent': result.get('primary_agent', 'unknown'),
            'a2a_count': len(a2a_summary.get('interactions', [])),
            'a2a_summary': a2a_summary
        }
        
        print(f"Response sent from agent: {response['primary_agent']}")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error processing request: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'response': 'Sorry, I encountered an error processing your request.'
        }), 500

@app.route('/a2a/logs', methods=['GET'])
def get_a2a_logs():
    """Get A2A communication logs"""
    try:
        orch, error = get_orchestrator()
        if error:
            return jsonify({'error': f'Orchestrator not initialized: {error}', 'logs': []}), 500
        a2a_logger = get_a2a_logger()
        summary = a2a_logger.get_summary()
        return jsonify(summary)
    except Exception as e:
        print(f"❌ Error fetching A2A logs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/a2a/export', methods=['GET'])
def export_a2a_logs():
    """Export A2A logs to file"""
    try:
        a2a_logger = get_a2a_logger()
        filename = 'a2a_communication_log.json'
        a2a_logger.export_log(filename)
        return jsonify({
            'success': True,
            'filename': filename,
            'message': f'Logs exported to {filename}'
        })
    except Exception as e:
        print(f"❌ Error exporting logs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history"""
    try:
        data = request.get_json()
        thread_id = data.get('thread_id', 'default')
        
        if thread_id in conversation_threads:
            del conversation_threads[thread_id]
        
        return jsonify({
            'success': True,
            'message': 'Conversation cleared'
        })
    except Exception as e:
        print(f"❌ Error clearing conversation: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("Starting A2A-MCP Backend API Server")
    print("="*70)
    print("  📍 Server: http://localhost:8000")
    print("  React UI: http://localhost:3000 (start with 'npm start')")
    print("  Docs: See react/README.md")
    print("="*70 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        threaded=True
    )

