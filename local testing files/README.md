# 📦 Local Testing Files

This folder contains files that are **NOT required** for the production backend or frontend but may be useful for local testing and development.

---

## 📁 Contents

### 🧪 Test Scripts
- `test_a2a_scenarios.py` - Test A2A coordination scenarios
- `test_full_system.py` - End-to-end system test
- `test_mcp_integration.py` - MCP client integration test
- `test_true_a2a.py` - True A2A functionality test
- `test/` - Directory with additional unit tests

### 🎯 Alternative Entry Points
- `main.py` - CLI interface (not needed with React UI)
- `run.py` - Alternative startup script

### 🚀 Startup Scripts
- `start_chatbot.sh` - One-command startup script

### 📚 Documentation
- `A2A_COORDINATION.md` - Agent coordination documentation
- `BEFORE_AFTER.md` - Before/after comparison
- `CHATBOT_UI_COMPLETE.md` - UI completion summary
- `CHATBOT_UI_GUIDE.md` - Complete UI setup guide
- `FIXES_SUMMARY.md` - Summary of fixes made
- `MCP_CLIENT_GUIDE.md` - MCP client documentation
- `MCP_CLIENT_MIGRATION.md` - Migration guide
- `SCENARIOS_GUIDE.md` - A2A scenarios guide
- `START_HERE.md` - Getting started guide
- `SUMMARY.md` - Project summary
- `WHATS_NEW_MCP_CLIENT.md` - MCP client changes
- `UNNECESSARY_FILES.md` - File cleanup analysis

---

## ✅ Production Files (Still in Root)

The following are **REQUIRED** for the backend and frontend:

```
backend_api.py          ← Flask API server
requirements.txt        ← Python dependencies
.env                    ← API keys
README.md              ← Main project documentation
a2a/                   ← Agent system
customer_mcp/          ← Tools & database
react/                 ← React frontend
```

---

## 🎯 When to Use These Files

### For Testing
- Run individual test scripts to verify functionality
- Use `test/` directory for unit testing

### For Alternative Interfaces
- Use `main.py` if you prefer CLI over React UI
- Use `start_chatbot.sh` for one-command startup

### For Documentation
- Reference documentation files for understanding the system
- Share with team members for onboarding

---

## 🗑️ Can Be Deleted

If you don't need local testing or documentation, this entire folder can be safely deleted without affecting your production system.

---

*Created: December 4, 2025*

