#!/bin/bash
# Script to replace GitHub repo contents with current folder

REPO_URL="https://github.com/DeepaliDagar/Multi-Agent-Ticketing-Support-Assistant.git"

echo "🔄 Setting up Git repository..."

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git initialized"
fi

# Check if remote exists
if git remote | grep -q "origin"; then
    git remote remove origin
fi

# Add remote
git remote add origin $REPO_URL
echo "✅ Remote added: $REPO_URL"

# Fetch existing repo (if any)
echo "📥 Fetching existing repository..."
git fetch origin 2>/dev/null || echo "⚠️  Repository might be empty or inaccessible"

# Checkout or create main branch
git checkout -b main 2>/dev/null || git checkout main

# Remove all existing files from git tracking (keep local files)
git rm -rf --cached . 2>/dev/null || true

# Add all current files
echo "📦 Adding current files..."
git add .

# Commit
echo "💾 Committing changes..."
git commit -m "Replace repository with Google ADK multi-agent system

- Multi-agent customer support system using Google ADK
- FastMCP server with MCP protocol
- Supervisor Agent Architecture
- Interactive chatbot interface
- SQLite database with WAL mode
- 7+ MCP tools for customer and ticket management"

echo ""
echo "🚀 Ready to push!"
echo ""
echo "Next steps:"
echo "1. If you need to force push (replaces everything on GitHub):"
echo "   git push -f origin main"
echo ""
echo "2. If you want to review first:"
echo "   git log"
echo "   git show --stat"
echo ""
echo "⚠️  Force push will DELETE all existing files in the GitHub repository!"
echo "   Make sure you're ready before running: git push -f origin main"
