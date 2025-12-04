# 🤖 Chatbot UI Setup Guide

Complete guide to run the beautiful React chatbot UI for your A2A-MCP system!

---

## ✨ What You Get

A **modern, beautiful chatbot interface** with:

- 💬 **Real-time Chat** - Smooth, responsive messaging
- 🎨 **Beautiful Design** - Gradient backgrounds, animations
- 🤝 **A2A Visualization** - See agents working together
- 📱 **Mobile Responsive** - Works on all devices
- 💡 **Quick Examples** - Pre-built queries
- 🎯 **Agent Indicators** - Know which agent responds
- 📊 **Activity Tracking** - Monitor A2A interactions

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Python Dependencies

```bash
cd /Users/deepalidagar/Desktop/Q4/GENAI/assignment4/A2A-MCP
source genaienv/bin/activate
pip install flask flask-cors
```

### Step 2: Start the Backend API

```bash
# Make sure your API key is set
export OPENAI_API_KEY='your-api-key-here'

# Start the Flask backend
python backend_api.py
```

You should see:
```
======================================================================
  🚀 A2A-MCP Backend API Server
======================================================================
  📍 Server: http://localhost:5000
  🔗 React UI: http://localhost:3000
======================================================================
```

**Keep this terminal open!**

### Step 3: Install React Dependencies

Open a **NEW terminal**:

```bash
cd /Users/deepalidagar/Desktop/Q4/GENAI/assignment4/A2A-MCP/react
npm install
```

### Step 4: Start the React UI

```bash
npm start
```

The app will automatically open in your browser at `http://localhost:3000`! 🎉

---

## 🎨 UI Features

### Header
- 🤖 **Logo** with floating animation
- 🟢 **Online Status** indicator
- 📋 **Menu** button for sidebar

### Chat Window
- 💬 **Messages** with beautiful bubbles
- 👤 **Agent Icons** showing which agent responded
- 🤝 **A2A Badges** showing agent coordination
- 📝 **Markdown Support** for formatted responses
- ⏰ **Timestamps** for each message

### Input Area
- ⌨️ **Multi-line Input** (Shift+Enter for new line)
- 💡 **Quick Examples** to get started
- 🗑️ **Clear Button** to start fresh
- 📤 **Send Button** with loading state

### Sidebar
- 💡 **Example Queries** by category:
  - 👤 Customer Info
  - 🎫 Support & Tickets
  - 🔍 Complex Queries
- 🤝 **A2A Activity Log** (recent interactions)
- ℹ️ **About** section

---

## 🧪 Try These Queries

### Customer Information
```
Get customer 3
List all active customers
Show me details of customers 2 and 4
Add a new customer named John Doe
```

### Support Tickets
```
Show open tickets
Create a ticket for customer 5
Get ticket history for customer 2
Show high priority tickets
```

### Complex (Multi-Agent A2A)
```
Get customer 5 with complete ticket history
Find customers whose name contains Smith
Show customers created in December
Tell me about customer 3 and their open tickets
```

Watch the **A2A badges** appear when agents coordinate! 🤝

---

## 🎯 How It Works

### Architecture

```
┌─────────────────┐
│   React UI      │
│  (Port 3000)    │
└────────┬────────┘
         │ HTTP
         ↓
┌─────────────────┐
│   Flask API     │
│  (Port 8000)    │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────┐
│  LangGraph Orchestrator     │
│  • Router Agent             │
│  • Customer Data Agent      │
│  • Support Agent            │
│  • SQL Generator Agent      │
└─────────────────────────────┘
         │
         ↓
┌─────────────────┐
│   MCP Client    │
│  (Tool Discovery)│
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   MCP Server    │
│  (Tools)        │
└─────────────────┘
         │
         ↓
┌─────────────────┐
│   Database      │
│  (SQLite)       │
└─────────────────┘
```

### Message Flow

1. **User types** in React UI
2. **React sends** HTTP POST to Flask API (`/chat`)
3. **Flask calls** LangGraphOrchestrator
4. **Orchestrator routes** to appropriate agent
5. **Agent uses** MCP Client for tools
6. **Agent may call** other agents (A2A)
7. **Response flows back** to React UI

---

## 🔧 Configuration

### Backend URL

By default, React connects to `http://localhost:5000`.

To change:

1. Create `react/.env`:
```bash
REACT_APP_API_URL=http://your-url:port
```

2. Restart React app

### Backend Port

To change Flask port, edit `backend_api.py`:

```python
app.run(
    host='0.0.0.0',
    port=5001,  # Change this
    debug=True
)
```

---

## 🐛 Troubleshooting

### "Backend server is not responding"

**Problem:** React can't connect to Flask

**Solutions:**
1. Make sure Flask is running: `python backend_api.py`
2. Check URL matches: `http://localhost:5000`
3. Check Flask terminal for errors
4. Try restarting both servers

### "Port 3000 already in use"

**Problem:** Something else using port 3000

**Solution:**
```bash
PORT=3001 npm start
```

### "Port 5000 already in use"

**Problem:** Something else using port 5000

**Solutions:**
1. Find and kill process: `lsof -ti:5000 | xargs kill -9`
2. Or change port in `backend_api.py`

### Flask Import Errors

**Problem:** Missing dependencies

**Solution:**
```bash
source genaienv/bin/activate
pip install flask flask-cors
```

### React Won't Start

**Problem:** npm issues

**Solution:**
```bash
cd react
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
npm start
```

### Database Errors

**Problem:** Database file not found

**Solution:**
```bash
# Make sure database exists
python customer_mcp/tools/db_utils.py
```

---

## 📱 Mobile Support

The UI is fully responsive! Test on:

- 📱 **iPhone/iPad** (Safari, Chrome)
- 📱 **Android** (Chrome, Firefox)
- 💻 **Desktop** (Chrome, Firefox, Safari, Edge)

---

## 🎨 Customization

### Colors

Edit `react/src/index.css` and `react/src/App.css`:

```css
/* Change gradient colors */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Change to your colors */
background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
```

### Logo

Edit `react/src/components/Header.js`:

```jsx
<span className="logo-icon">🤖</span>  {/* Change emoji */}
<span className="logo-text">A2A-MCP</span>  {/* Change text */}
```

### Agent Icons

Edit `react/src/components/Message.js`:

```javascript
const icons = {
  'customer_data': '👤',  // Change icons
  'support': '🎫',
  'sql': '🔍',
  // Add your icons
};
```

---

## 🚀 Production Deployment

### Build React App

```bash
cd react
npm run build
```

Creates optimized build in `react/build/`

### Serve with Production Server

```bash
# Install serve
npm install -g serve

# Serve build
serve -s build -l 3000
```

### Deploy Options

1. **Netlify** - Free hosting for React apps
2. **Vercel** - Free with automatic deploys
3. **AWS S3 + CloudFront** - Scalable hosting
4. **Your own server** - Nginx + Flask

For backend, deploy Flask to:
- **Heroku** (free tier)
- **AWS EC2** (scalable)
- **DigitalOcean** (simple droplets)
- **Google Cloud Run** (serverless)

---

## 📊 API Endpoints

### POST `/chat`
Send a message:
```json
{
  "message": "Get customer 3",
  "thread_id": "optional-thread-id"
}
```

Response:
```json
{
  "response": "Here are the details...",
  "primary_agent": "customer_data",
  "a2a_count": 2,
  "a2a_summary": {...}
}
```

### GET `/health`
Check backend status

### GET `/a2a/logs`
Get A2A interaction logs

### GET `/a2a/export`
Export logs to file

### POST `/clear`
Clear conversation history

---

## 🎓 Development

### File Structure
```
react/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── components/         # UI components
│   │   ├── Header.js      # Navigation bar
│   │   ├── ChatWindow.js  # Messages area
│   │   ├── Message.js     # Single message
│   │   ├── ChatInput.js   # Input form
│   │   ├── Sidebar.js     # Menu sidebar
│   │   └── TypingIndicator.js  # Loading dots
│   ├── services/
│   │   └── api.js         # Backend API calls
│   ├── App.js             # Main component
│   ├── App.css            # Main styles
│   ├── index.js           # Entry point
│   └── index.css          # Global styles
└── package.json           # Dependencies
```

### Adding New Features

1. **New Component:**
```bash
# Create files
touch src/components/MyComponent.js
touch src/components/MyComponent.css
```

2. **Import and use:**
```javascript
import MyComponent from './components/MyComponent';
```

---

## ✅ Summary

You now have:
- ✅ Beautiful React chatbot UI
- ✅ Flask API backend
- ✅ Full A2A-MCP integration
- ✅ Mobile responsive design
- ✅ Production ready code

**Start chatting and watch your multi-agent system in action!** 🚀

---

## 📚 Resources

- [React Documentation](https://reactjs.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [A2A-MCP Architecture](START_HERE.md)
- [MCP Client Guide](MCP_CLIENT_GUIDE.md)

---

**Enjoy your beautiful chatbot! 🎉**

