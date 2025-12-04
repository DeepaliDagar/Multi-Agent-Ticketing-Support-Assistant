# Quick Start - 2 Minutes!

## ⚡ Fastest Way

```bash
# From A2A-MCP root directory
./start_chatbot.sh
```

**That's it!** Both servers start automatically.

---

## 📖 Manual Start (If you prefer)

### Terminal 1 - Backend
```bash
cd /Users/deepalidagar/Desktop/Q4/GENAI/assignment4/A2A-MCP
source genaienv/bin/activate
export OPENAI_API_KEY='your-key-here'
pip install flask flask-cors
python backend_api.py
```

### Terminal 2 - Frontend
```bash
cd /Users/deepalidagar/Desktop/Q4/GENAI/assignment4/A2A-MCP/react
npm install  # First time only
npm start
```

---

## What Opens

- **Backend:** http://localhost:5000 (Flask API)
- **Frontend:** http://localhost:3000 (React UI - Opens automatically!)

---

## Try These Queries

```
Get customer 3
Show me open tickets
Customer 5 with complete ticket history
```

---


