# Deploying to Vercel

## 🚀 Quick Deploy Steps

### 1. Deploy React Frontend to Vercel

**Option A: Using Vercel CLI (Recommended)**

```bash
# Install Vercel CLI globally
npm install -g vercel

# Navigate to React folder
cd react

# Login to Vercel
vercel login

# Deploy
vercel

# For production deployment
vercel --prod
```

**Option B: Using Vercel Dashboard (Easiest)**

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click "Add New Project"
4. Import your GitHub repository: `Multi-Agent-Ticketing-Support-Assistant`
5. **Important Settings:**
   - **Root Directory**: `react`
   - **Framework Preset**: Create React App
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
   - **Install Command**: `npm install`

6. **Add Environment Variable:**
   - Key: `REACT_APP_API_URL`
   - Value: `YOUR_BACKEND_URL` (see backend deployment below)

7. Click "Deploy"

---

## 🔧 Backend Deployment Options

Your Flask backend needs to be deployed separately. Here are your options:

### Option 1: Render (Free Tier Available)

1. Go to [render.com](https://render.com)
2. Sign in with GitHub
3. Click "New +" → "Web Service"
4. Connect your repository
5. Settings:
   - **Name**: `a2a-mcp-backend`
   - **Root Directory**: `.` (project root)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python backend_api.py`
   - **Environment Variables**:
     ```
     OPENAI_API_KEY=your_openai_key_here
     PORT=8000
     ```
6. Deploy

Your backend URL will be: `https://a2a-mcp-backend.onrender.com`

### Option 2: Railway (Easy, Fast)

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables:
   - `OPENAI_API_KEY`
6. Railway auto-detects Python and deploys

### Option 3: PythonAnywhere (Free for small projects)

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Create free account
3. Upload your code
4. Configure WSGI file
5. Set up environment variables

### Option 4: Keep Backend Local (Development Only)

If you want to test with local backend:

1. Make sure backend is running: `python backend_api.py`
2. Use ngrok to expose it:
   ```bash
   ngrok http 8000
   ```
3. Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)
4. Use this as `REACT_APP_API_URL` in Vercel

---

## 🔄 Update Environment Variable After Backend Deployment

Once your backend is deployed, update Vercel:

1. Go to Vercel Dashboard → Your Project
2. Go to "Settings" → "Environment Variables"
3. Update `REACT_APP_API_URL` to your backend URL:
   ```
   https://your-backend.onrender.com
   ```
4. Redeploy: "Deployments" → Click "..." → "Redeploy"

---

## ⚙️ Backend Configuration for Production

Update your `backend_api.py` to allow Vercel domain:

```python
from flask_cors import CORS

# Update CORS to include your Vercel URL
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "https://your-app.vercel.app",  # Add your Vercel URL
            "https://*.vercel.app"  # Allow all Vercel preview deployments
        ]
    }
})
```

---

## 🧪 Testing Your Deployment

1. **Frontend Only Test:**
   - Visit your Vercel URL: `https://your-app.vercel.app`
   - UI should load correctly

2. **With Backend:**
   - Deploy backend first
   - Update `REACT_APP_API_URL` in Vercel
   - Redeploy
   - Test chat functionality

3. **Check Developer Console:**
   - Open browser DevTools (F12)
   - Check Console for errors
   - Check Network tab for API calls

---

## 🐛 Common Issues & Fixes

### Issue 1: CORS Errors
**Error:** "Access to XMLHttpRequest blocked by CORS policy"

**Fix:**
- Update `backend_api.py` to include your Vercel URL in CORS origins
- Redeploy backend

### Issue 2: 404 on Refresh
**Error:** Page not found when refreshing non-root pages

**Fix:**
- Already handled by `vercel.json` rewrites configuration

### Issue 3: Environment Variable Not Working
**Error:** "Backend server is not responding"

**Fix:**
1. Verify `REACT_APP_API_URL` is set in Vercel
2. Must start with `REACT_APP_` prefix
3. Redeploy after adding/changing variables

### Issue 4: Build Fails
**Error:** Build errors on Vercel

**Fix:**
```bash
# Test build locally first
cd react
npm run build

# If successful locally, check Vercel build logs
# Common fixes:
npm install  # Ensure dependencies are installed
```

---

## 📝 Deployment Checklist

- [ ] React app builds successfully locally (`npm run build`)
- [ ] Backend deployed and accessible
- [ ] `REACT_APP_API_URL` environment variable set in Vercel
- [ ] CORS configured in backend to allow Vercel URL
- [ ] OpenAI API key set in backend environment
- [ ] Test chat functionality after deployment
- [ ] Check browser console for errors

---

## 🎯 Quick Commands Reference

```bash
# Deploy to Vercel
cd react
vercel

# Production deployment
vercel --prod

# Check deployment status
vercel list

# View logs
vercel logs

# Remove deployment
vercel remove
```

---

## 🔗 Useful Links

- **Vercel Dashboard**: https://vercel.com/dashboard
- **Render Dashboard**: https://dashboard.render.com
- **Railway Dashboard**: https://railway.app/dashboard
- **Vercel CLI Docs**: https://vercel.com/docs/cli

---

## 🎉 After Successful Deployment

Your app will be live at:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-backend.onrender.com` (or your chosen platform)

Share the frontend URL to let others try your Multi-Agent Support System! 🚀

