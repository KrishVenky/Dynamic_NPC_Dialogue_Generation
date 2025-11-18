# Python Quickstart Guide

## Quick Start

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Flask server
```bash
python app.py
```

### 3. Open browser
Navigate to `http://localhost:3000`

---

## What This System Does

This is a dynamic NPC dialogue generation system for Nick Valentine from Fallout 4. It uses a local HuggingFace model (Qwen 2.5 3B Instruct) to generate context-aware, in-character dialogue responses.

### Key Features:
- **Conversation Memory**: Remembers last 3 exchanges
- **Context-Aware**: Different responses for Investigation/Combat/Casual/etc.
- **Emotion Control**: Adjusts tone based on selected emotion
- **Vector Search**: Uses ChromaDB to find similar dialogue examples
- **100% Free**: Runs locally, no API costs

---

## Project Structure

```
Dynamic_NPC_Dialogue_Generation/
├── app.py                      # Flask server
├── agents/                     # Agent implementations
│   ├── base_agent.py          # Base agent interface
│   ├── agent_manager.py       # Multi-agent manager
│   └── huggingface_agent.py   # HuggingFace/Qwen implementation
├── dialogue_processor.py      # CSV parser
├── vector_store.py            # ChromaDB integration
├── public/                    # Frontend files
├── data/                      # Dialogue CSV data
└── requirements.txt           # Python dependencies
```

---

## Environment Setup

### Optional Environment Variables

Create a `.env` file if you want to customize:

```env
HF_TOKEN=your_token_here  # Optional - Qwen models don't require auth
HF_MODEL=Qwen/Qwen2.5-3B-Instruct  # Default model
PORT=3000
```

**Note**: Qwen models don't require authentication, so `HF_TOKEN` is optional.

---

## First Run

On first run, the model will download automatically (~6GB). This takes 5-10 minutes depending on your internet connection.

**Requirements:**
- Internet connection (for first download)
- ~8GB RAM minimum
- ~10GB free disk space

---

## Usage

1. **Start the server**: `python app.py`
2. **Open browser**: `http://localhost:3000`
3. **Select context**: Investigation, Combat, Casual, etc.
4. **Select emotion**: Neutral, Amused, Stern, etc.
5. **Type your message** and press Enter
6. **Nick responds** with context-aware dialogue

---

## API Endpoints

### Generate Dialogue
```bash
POST /api/generate
Content-Type: application/json

{
  "userInput": "What do you think about synths?",
  "context": "casual",
  "emotion": "thoughtful",
  "includeExamples": true
}
```

### List Agents
```bash
GET /api/agents
```

### Switch Agent
```bash
POST /api/agents/switch
Content-Type: application/json

{
  "agentId": "huggingface"
}
```

### Get History
```bash
GET /api/history
```

### Reset Conversation
```bash
POST /api/reset
```

---

## Troubleshooting

### "No agents initialized"
- Check terminal output for errors
- Ensure transformers and torch are installed: `pip install transformers torch`
- Check internet connection (model needs to download on first run)

### Slow responses
- Normal on CPU: 5-10 seconds per response
- First request is slower (model loading)
- Consider using GPU if available (automatic if CUDA is installed)

### Model download fails
- Check internet connection
- Ensure sufficient disk space (~10GB)
- Try again - downloads can be interrupted

### Port already in use
- Change PORT in `.env` or command line
- Or kill the process using port 3000

---

## Model Information

**Current Model**: Qwen/Qwen2.5-3B-Instruct

- **Provider**: HuggingFace
- **Size**: ~6GB
- **Type**: Instruction-tuned language model
- **Requirements**: ~8GB RAM
- **Speed**: 5-10 seconds per response (CPU)
- **Cost**: $0 (runs locally)

---

## Next Steps

- See [README.md](../README.md) for full documentation
- See [REFACTORING_ROADMAP.md](REFACTORING_ROADMAP.md) for future plans
- Check `COMPLETE_SETUP_GUIDE.md` for detailed usage instructions

---

Ready to start! Run `python app.py` and open `http://localhost:3000`
