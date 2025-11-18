# Nick Valentine Dialogue Generator - Python/Flask

## Quick Start

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment variables (optional)
Create a `.env` file if needed:
```
HF_TOKEN=your_token_here  # Optional - Qwen models don't require authentication
HF_MODEL=Qwen/Qwen2.5-3B-Instruct  # Default model
PORT=3000
```

### 3. Run the Flask server
```bash
python app.py
```

### 4. Open browser
Navigate to `http://localhost:3000`

---

## What Changed

### Migrated to Python/Flask
- **Backend**: Flask server (`app.py`)
- **Multi-Agent System**: Agent Manager for seamless switching
- **Modular Design**: Base agent class for easy extension

### Agent Architecture
```
AgentManager
  ├── HuggingFace Agent (Active)
  └── Future agents can be added here
```

### New Features
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
│   └── huggingface_agent.py   # HuggingFace implementation
├── nick_personality.py        # Character profile
├── dialogue_processor.py      # CSV parser
├── vector_store.py            # ChromaDB integration
├── public/                    # Frontend
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── requirements.txt           # Python dependencies
└── docs/                      # Documentation
```

---

## API Endpoints

### Dialogue
- `POST /api/generate` - Generate response with active agent
- `GET /api/history` - Get conversation history
- `POST /api/reset` - Reset active agent's conversation
- `GET /api/export` - Export conversation

### Agent Management
- `GET /api/agents` - List all available agents
- `POST /api/agents/switch` - Switch active agent
- `GET /api/agents/active` - Get active agent info

### System
- `GET /api/health` - Health check
- `GET /api/cost-estimate` - Cost estimate (always $0.00 for local models)

---

## Next Steps

### Immediate
1. Test the Flask app
2. Verify agent switching works

### Future (see REFACTORING_ROADMAP.md)
- Add ChromaDB for vector search
- Integrate additional HuggingFace models
- Build agentic pipeline
- Add model performance metrics

---

## Troubleshooting

### Import errors when running
```bash
pip install -r requirements.txt
```

### Port already in use
Change PORT in `.env` file or command line

### No agents initialized
Check terminal output for errors. Common issues:
- Model download failed (check internet connection)
- Insufficient memory (try CPU-only PyTorch)
- Missing dependencies (run `pip install -r requirements.txt`)

---

## Model Information

**Current Model**: Qwen/Qwen2.5-3B-Instruct

- **Size**: ~6GB download
- **Requirements**: ~8GB RAM minimum
- **Speed**: 5-10 seconds per response on CPU
- **Cost**: $0 (runs locally)

---

Ready to run! Execute: `python app.py`
