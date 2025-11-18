# Nick Valentine Dialogue Generator - Python/Flask

## Quick Start

### 1. Install Python dependencies
```powershell
pip install -r requirements.txt
```

### 2. Your .env is already configured ✓
```
GEMINI_API_KEY=AIzaSyBO9skkGn3DRNdKEKnO8UTYXbUjSxqeAfM
GEMINI_MODEL=gemini-1.5-flash
PORT=3000
```

### 3. Run the Flask server
```powershell
python app.py
```

### 4. Open browser
Navigate to `http://localhost:3000`

---

## What Changed

### ✅ Migrated to Python/Flask
- **Backend**: Flask server (`app.py`)
- **Multi-Agent System**: Agent Manager for seamless switching
- **Modular Design**: Base agent class for easy extension

### ✅ Agent Architecture
```
AgentManager
  ├── Gemini Agent (✓ Active)
  ├── HuggingFace Agent (TODO)
  ├── Local Model Agent (TODO)
  └── Custom Agent (TODO)
```

### ✅ New Features
- **Agent Switching**: Select different models in dropdown
- **Fresh Conversations**: Each agent switch resets dialogue
- **Seamless UX**: Switch agents without reloading page
- **Extensible**: Easy to add new agents

---

## Project Structure (Python)

```
├── app.py                      # Flask server
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Base agent interface
│   ├── agent_manager.py       # Multi-agent manager
│   └── gemini_agent.py        # Gemini implementation
├── nick_personality.py        # Character profile
├── dialogue_processor.py      # CSV parser
├── public/                    # Frontend (updated)
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── requirements.txt           # Python dependencies
└── REFACTORING_ROADMAP.md    # Future plans
```

---

## API Endpoints (Updated)

### Dialogue
- `POST /api/generate` - Generate response with active agent
- `GET /api/history` - Get conversation history
- `POST /api/reset` - Reset active agent's conversation
- `GET /api/export` - Export conversation

### Agent Management (NEW)
- `GET /api/agents` - List all available agents
- `POST /api/agents/switch` - Switch active agent
- `GET /api/agents/active` - Get active agent info

---

## Next Steps

### Immediate
1. Test the Flask app
2. Verify agent switching works

### Future (see REFACTORING_ROADMAP.md)
- Add ChromaDB for vector search
- Integrate HuggingFace models
- Build agentic pipeline
- Add model performance metrics

---

## Troubleshooting

### Import errors when running
```powershell
pip install -r requirements.txt
```

### Port already in use
Change PORT in `.env` file

### No agents initialized
Verify `GEMINI_API_KEY` is set in `.env`

---

**Ready to run! Execute: `python app.py`** 🚀
