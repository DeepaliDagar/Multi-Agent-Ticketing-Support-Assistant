# Deployment Guide

## Backend Deployment (Render)

### 1. Create/Update Render Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Create new Web Service (or update existing)
3. Connect your GitHub repository

### 2. Configure Render Settings

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn backend_api:app --bind 0.0.0.0:$PORT
```

**Environment Variables:**
```
OPENAI_API_KEY=your_openai_api_key
MCP_HTTP_BASE_URL=http://localhost:8001
PORT=8000
```

### 3. Important Notes

- Backend needs MCP server running (separate service or same instance)
- For production, run MCP server as background process or separate service
- Database file will be created automatically

---

## Frontend Deployment (Vercel)

### 1. Deploy via Vercel CLI

```bash
cd react
npm install
vercel --prod
```

### 2. Or Deploy via Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com)
2. Import your GitHub repository
3. Set root directory to `react/`
4. Build settings are auto-detected from `vercel.json`

### 3. Update API URL

After backend is deployed, update `react/src/services/api.js`:

```javascript
const API_BASE_URL = 'https://your-backend.onrender.com';
```

Then redeploy React app.

---

## Alternative: Run MCP Server on Render

If you want MCP server on same Render instance:

**Start Command:**
```bash
python customer_mcp/server/mcp_server.py & gunicorn backend_api:app --bind 0.0.0.0:$PORT
```

Or create separate Render service for MCP server on port 8001.

---

## Health Checks

**Backend:**
```bash
curl https://your-backend.onrender.com/health
```

**MCP Server (if separate):**
```bash
curl https://your-mcp-server.onrender.com/health
```

