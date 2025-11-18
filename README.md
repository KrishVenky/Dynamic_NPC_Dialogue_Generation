# Nick Valentine Dialogue Generator

**Multi-Agent Dialogue System with Vector DB & Agentic Pipeline**

## 🚀 Quick Start

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Configure API Keys
Edit `.env`:
```env
GEMINI_API_KEY=your_gemini_key_here
HF_TOKEN=your_huggingface_token_here
GEMINI_MODEL=gemini-1.5-flash
PORT=3000
```

### 3. Run Server
```powershell
python app.py
```

### 4. Open Browser
Navigate to `http://localhost:3000`

---

## 📁 Project Structure

```
AFML_Project_NPC_Final/
├── app.py                          # Flask server
├── agents/                         # Agent implementations
│   ├── __init__.py
│   ├── base_agent.py              # Base agent interface
│   ├── agent_manager.py           # Multi-agent coordinator
│   └── gemini_agent.py            # Gemini implementation
├── nick_personality.py            # Character profile
├── dialogue_processor.py          # CSV dialogue parser
├── data/                          # Data files
│   └── nick_valentine_dialogue.csv
├── public/                        # Frontend
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── docs/                          # Documentation
│   ├── PYTHON_QUICKSTART.md
│   ├── REFACTORING_ROADMAP.md
│   └── README.md (old Node.js docs)
├── config/                        # Configuration templates
│   └── .env.example
├── .env                           # Your environment variables
├── .gitignore
└── requirements.txt               # Python dependencies
```

---

## ✨ Features

### Multi-Agent System
- **Seamless Agent Switching**: Switch between models via dropdown
- **Independent Conversations**: Each agent maintains its own history
- **Extensible Architecture**: Easy to add new agents (HF, local models, etc.)

### Current Agents
- ✅ **Gemini Agent** (Active) - Google's Gemini 1.5 Flash
- 🔜 **HuggingFace Agent** - Coming soon
- 🔜 **Local Model Agent** - Coming soon

### Planned Features
- 🔜 ChromaDB Vector Search for context retrieval
- 🔜 RAG (Retrieval Augmented Generation)
- 🔜 Agentic Pipeline for multi-step workflows
- 🔜 Model performance metrics

---

## 🎮 Usage

1. **Select Agent**: Choose from dropdown (Gemini, HF, etc.)
2. **Set Context**: Investigation, Combat, Casual, etc.
3. **Choose Emotion**: Neutral, Amused, Stern, etc.
4. **Chat**: Type and press Enter
5. **Switch Agents**: Select different model → conversation resets

---

## 🔧 API Endpoints

### Dialogue
- `POST /api/generate` - Generate response
- `GET /api/history` - Get conversation history
- `POST /api/reset` - Reset conversation
- `GET /api/export` - Export conversation

### Agent Management
- `GET /api/agents` - List all agents
- `POST /api/agents/switch` - Switch active agent
- `GET /api/agents/active` - Get active agent info

---

## 🛠️ Adding New Agents

1. Create new agent class extending `BaseDialogueAgent`
2. Implement `initialize()` and `generate_response()`
3. Register in `app.py`:
   ```python
   new_agent = YourAgent(config)
   new_agent.initialize()
   agent_manager.register_agent('your_agent', new_agent)
   ```

---

## 📚 Documentation

- **[Python Quickstart](docs/PYTHON_QUICKSTART.md)** - Setup guide
- **[Refactoring Roadmap](docs/REFACTORING_ROADMAP.md)** - Future plans
- **[Old Node.js Docs](docs/README.md)** - Previous implementation

---

## 🎯 Roadmap

See [REFACTORING_ROADMAP.md](docs/REFACTORING_ROADMAP.md) for detailed plans:

- ✅ Flask backend with multi-agent system
- ✅ Agent switching UI
- 🔜 ChromaDB integration
- 🔜 HuggingFace models
- 🔜 Agentic pipeline
- 🔜 Vector search optimization

---

## 💡 Tech Stack

- **Backend**: Flask, Python 3.10+
- **AI**: Google Gemini, HuggingFace Transformers
- **Vector DB**: ChromaDB (planned)
- **Frontend**: Vanilla JavaScript
- **Data**: Pandas, CSV

---

## 🤝 Contributing

Add new agents, improve prompts, optimize vector search!

## 📄 License

MIT
