# React Chatbot UI
Chatbot interface for the A2A-MCP Multi-Agent ticket management system.

---

## Quick Start

### 1. Start Backend
```bash
cd {project location}
activate vm
export OPENAI_API_KEY='your-key-here'
python backend_api.py
```
**Runs on:** http://localhost:8000

### 2. Start Frontend
```bash
cd react
npm install  # First time only
npm start
```
**Opens at:** http://localhost:3000

---

## How It Connects

```
User Browser (port 3000)
    ↓ HTTP POST /chat
React UI
    ↓ axios (api.js)
Flask Backend (port 8000)
    ↓ Python
LangGraph Orchestrator
    ↓ A2A coordination
Multi-Agent System
    ↓ MCP Client
MCP Server (Tools)
    ↓
SQLite Database
```

### Connection Details

**Frontend → Backend:**
- React app at `http://localhost:3000`
- Sends POST requests to `http://localhost:8000/chat`
- Uses `axios` library in `react/src/services/api.js`

**Backend → Agents:**
- Flask API receives requests at `/chat` endpoint
- Calls `LangGraphOrchestrator.process(message)`
- Orchestrator routes to appropriate agent
- Agents use MCP Client for dynamic tool discovery
- Tools interact with SQLite database

**Response Flow:**
- Backend returns JSON: `{response, primary_agent, a2a_count}`
- React displays in chat window with agent indicators
- A2A badges show coordination between agents

---

## Features

- Real-time chat interface
- Modern gradient design
- A2A coordination visualization
- Agent indicators
- Mobile responsive
- Quick example queries
- Markdown support

---

## Structure

```
backend_api.py          ← Flask API (port 8000)
react/                  ← React UI (port 3000)
  ├── src/
  │   ├── App.js           ← Main component
  │   ├── services/
  │   │   └── api.js       ← Backend API calls
  │   └── components/      ← UI components
  └── package.json         ← Dependencies
```

---

## Key Files

| File | Purpose |
|------|---------|
| `backend_api.py` | Flask REST API server, connects to orchestrator |
| `react/src/App.js` | Main React component, manages chat state |
| `react/src/services/api.js` | API calls to backend (axios) |
| `react/src/components/` | Chat UI components (Header, Messages, Input) |

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat` | POST | Send message, get response |
| `/health` | GET | Check backend status |
| `/a2a/logs` | GET | Get A2A interaction logs |

---

## Documentation

For detailed guides, see: `local testing files/CHATBOT_UI_GUIDE.md`

---

