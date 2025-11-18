# Nick Valentine Dialogue Generator

**Multi-Agent Dialogue System with TinyLlama (100% Free & Local)**

---

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies
```bash
source venv/bin/activate
pip install flask flask-cors python-dotenv pandas transformers torch sentence-transformers chromadb
```

### 2. Run Server
```bash
python app.py
```

### 3. Open Browser
Navigate to `http://localhost:3000`

---

## ✨ NEW Features (Just Fixed!)

### ✅ Conversation Memory
- Remembers last 3 exchanges automatically
- Nick can follow the conversation thread
- Natural multi-turn dialogues

### ✅ Context-Aware Responses  
- **Investigation** → Detective mode
- **Combat** → Alert, ready for danger
- **Casual** → Relaxed conversation
- **Emotional** → Deep, personal topics

### ✅ Emotion Control
- **Neutral** → Standard detective tone
- **Amused** → Dry humor, sarcastic
- **Stern** → Serious, no-nonsense
- **Concerned** → Worried, caring

### ✅ 100% Free & Local
- Uses TinyLlama (no API costs)
- Runs on your machine
- No rate limits
- No safety filters blocking responses

---

## 💬 Example Conversation

```
You: "Hello Nick"
Nick: "Hello. What can I do for you?"

You: "I need help with a murder case"
Nick: "A murder case? Tell me what you know."

You: "The victim was found at the docks"
Nick: "The docks, huh? That's rough territory. Any witnesses?"
```

Notice how Nick **remembers** you're discussing a murder case!

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
- ✅ **HuggingFace Agent** (Primary) - TinyLlama 1.1B Chat (FREE, local)
- ✅ **Vector DB Integration** - ChromaDB for context retrieval

### Planned Features
- ✅ ChromaDB Vector Search for context retrieval
- ✅ RAG (Retrieval Augmented Generation)
- 🔜 Agentic Pipeline for multi-step workflows
- 🔜 Model performance metrics
- 🔜 Fine-tuned character models

---

## 🎮 Usage

1. **Agent is Auto-Selected**: HuggingFace/TinyLlama is the primary agent
2. **Set Context**: Investigation, Combat, Casual, etc.
3. **Choose Emotion**: Neutral, Amused, Stern, etc.
4. **Chat**: Type and press Enter
5. **100% Free**: No API keys required, runs locally on your machine

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
- **AI**: TinyLlama 1.1B Chat (HuggingFace Transformers)
- **Vector DB**: ChromaDB
- **Frontend**: Vanilla JavaScript
- **Data**: Pandas, CSV
- **Cost**: $0 (100% free, runs locally)

---

## 🤝 Contributing

Add new agents, improve prompts, optimize vector search!

## 📄 License

MIT
