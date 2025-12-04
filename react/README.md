# A2A-MCP Chatbot UI

Beautiful, modern chatbot interface for the A2A-MCP Multi-Agent System.

## Features

- **Real-time Chat Interface** - Beautiful, responsive design
- **Modern UI/UX** - Gradient backgrounds, smooth animations
- **A2A Visualization** - See agent-to-agent coordination
- **Mobile Responsive** - Works on all devices
- **Quick Examples** - Pre-built queries to get started
- **Agent Indicators** - Know which agent is responding
- **Activity Sidebar** - Track A2A interactions

## Quick Start

### 1. Install Dependencies

```bash
cd react
npm install
```

### 2. Start the Backend Server

First, make sure your Python backend is running:

```bash
# From the A2A-MCP root directory
cd ..
python backend_api.py
```

The backend will start on `http://localhost:5000`

### 3. Start the React App

```bash
npm start
```

The app will open at `http://localhost:3000`

## Configuration

### Backend URL

By default, the app connects to `http://localhost:5000`. To change this:

1. Create a `.env` file in the `react/` directory:

```bash
REACT_APP_API_URL=http://your-backend-url:port
```

2. Restart the React app

## Project Structure

```
react/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── components/         # React components
│   │   ├── Header.js       # Top navigation bar
│   │   ├── ChatWindow.js   # Messages display
│   │   ├── Message.js      # Individual message
│   │   ├── ChatInput.js    # Input area
│   │   ├── Sidebar.js      # Menu & examples
│   │   └── TypingIndicator.js  # Loading animation
│   ├── services/
│   │   └── api.js          # Backend API calls
│   ├── App.js              # Main application
│   ├── App.css             # Main styles
│   ├── index.js            # Entry point
│   └── index.css           # Global styles
├── package.json            # Dependencies
└── README.md              # This file
```

## UI Components

### Header
- Logo and title
- Menu button
- Online status indicator

### Chat Window
- Scrollable message area
- User and bot messages
- Agent indicators
- A2A interaction badges
- Markdown support

### Chat Input
- Text input with multi-line support
- Quick example queries
- Send and clear buttons
- Loading states

### Sidebar
- Example queries by category
- A2A activity log
- System information

## Styling

The UI uses:
- **Gradient backgrounds** - Purple theme
- **Smooth animations** - Fade in, float, pulse
- **Modern components** - Rounded corners, shadows
- **Responsive design** - Works on mobile and desktop

## API Integration

The app communicates with the Python backend via REST API:

### POST /chat
Send a user message:
```json
{
  "message": "Get customer 3",
  "thread_id": "thread_123456"
}
```

Response:
```json
{
  "response": "Here are the details...",
  "primary_agent": "customer_data",
  "a2a_count": 2,
  "a2a_summary": [...]
}
```

### GET /a2a/logs
Get A2A interaction logs

### GET /health
Check backend status

## Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App (irreversible)

### Building for Production

```bash
npm run build
```

Creates optimized production build in `build/` directory.


## Example Queries

Try these queries to see the multi-agent system in action:

**Customer Info:**
- "Get customer 3"
- "List all active customers"
- "Show customers 2 and 4"

**Support & Tickets:**
- "Show open tickets"
- "Create ticket for customer 5"
- "Get ticket history for customer 2"

**Complex Queries (A2A coordination):**
- "Customer 5 with complete ticket history"
- "Find customers named Smith"
- "Show customers with most tickets"

## Troubleshooting

### Backend Not Connecting

**Error:** "Backend server is not responding"

**Solution:**
1. Make sure Python backend is running: `python backend_api.py`
2. Check the URL matches: `http://localhost:5000`
3. Check for CORS issues (backend should allow React origin)

### Port Already in Use

**Error:** "Port 3000 is already in use"

**Solution:**
```bash
# Use a different port
PORT=3001 npm start
```

### Dependencies Installation Failed

**Error:** npm install fails

**Solution:**
```bash
# Clear cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## Learn More

- [React Documentation](https://reactjs.org/)
- [Create React App](https://create-react-app.dev/)
- [A2A-MCP Backend](../README.md)

## License

Part of the multi agent ticket management system project.

---

