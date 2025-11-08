# 🕵️‍♂️ Nick Valentine Chatbot - Quick Reference

## ⚡ Quick Start

```bash
# 1. Activate virtual environment
.venv\Scripts\activate

# 2. Run the chatbot
python nick_valentine_chatbot.py

# OR use the launcher for model selection
python launch_chatbot.py
```

## 🎮 Chat Commands

| Command | Action |
|---------|--------|
| `help` | Show tips on what to ask Nick |
| `clear` | Reset conversation history |
| `exit` or `quit` | End conversation |

## 💬 Example Questions

**Detective Work:**
- "Can you help me find someone?"
- "I need a detective"
- "Someone's gone missing"

**About Nick:**
- "What's it like being a synth?"
- "Tell me about yourself"
- "How did you become a detective?"

**Commonwealth/Fallout:**
- "Tell me about Diamond City"
- "What do you think about the Institute?"
- "Any interesting cases?"

**Philosophy:**
- "What makes someone human?"
- "Do you have real memories?"
- "What's it like having someone else's memories?"

## 🤖 Model Selection

**Edit line 30 in `nick_valentine_chatbot.py`:**

```python
SELECTED_MODEL = "gpt2"  # Change to: llama, phi, mistral, distilgpt2
```

### Quick Guide:
- 💻 **CPU Only**: `gpt2` or `distilgpt2`
- 🎮 **GPU 6-8GB**: `phi` or `llama`
- 🚀 **GPU 16GB+**: `mistral`

## 📊 Files Overview

| File | Purpose |
|------|---------|
| `nick_valentine_chatbot.py` | Main chatbot (run this) |
| `launch_chatbot.py` | Interactive launcher |
| `test_dataset.py` | Verify data loading |
| `test_models.py` | Compare model outputs |
| `nick_valentine_dialogue.csv` | Dataset (2,569 lines) |

## 🔧 Troubleshooting

### Out of Memory
```python
# In nick_valentine_chatbot.py, reduce:
max_new_tokens=50  # Line 218 (was 80)
```

### Slow Responses
```python
# Switch to faster model:
SELECTED_MODEL = "distilgpt2"  # Line 30
```

### Poor Quality
```python
# Try better model:
SELECTED_MODEL = "llama"  # Line 30 (needs GPU)
```

### ChromaDB Issues
```bash
# Delete and rebuild database
rm -rf chroma_db_nick_valentine/
python nick_valentine_chatbot.py  # Rebuilds automatically
```

## 📝 Dataset Stats

- **Total Dialogues**: 2,569
- **Conversational Pairs**: 913
- **Standalone Lines**: 1,656
- **Categories**: Scene, Miscellaneous, Topic, Detection, Combat
- **Moods**: Happy, Stern, Sad, Surprised, Questioning, Confident, etc.

## 🎯 Pro Tips

1. **Be specific**: "Help me find my son" works better than "hi"
2. **Stay in character**: Ask about detective work, the Commonwealth, synths
3. **Use conversation**: Build on previous responses
4. **Try different models**: Quality varies significantly!
5. **GPU helps**: Llama/Mistral are much better with GPU

## 🔗 Important Links

- **HuggingFace Token**: https://huggingface.co/settings/tokens (for Llama)
- **Model Guide**: `MODEL_TESTING_GUIDE.md`
- **Full Docs**: `README.md`
- **Changes**: `CHANGES_SUMMARY.md`

## ⚙️ Advanced Config

### Adjust Response Creativity

In `nick_valentine_chatbot.py` around line 217:

```python
temperature=0.75,  # Higher = more creative (0.5-1.2)
top_k=50,         # Vocabulary limit (30-100)
top_p=0.92,       # Sampling threshold (0.8-0.95)
```

### Change Retrieval Count

Line 180:
```python
n_results=10,  # Get more similar dialogues (5-20)
```

### Conversation Memory

Line 251:
```python
if len(conversation_history) > 12:  # Increase for more memory (8-20)
```

## 🐛 Common Issues

**Issue**: "Module not found"
**Fix**: `pip install pandas sentence-transformers transformers chromadb`

**Issue**: "CUDA out of memory"
**Fix**: Use `gpt2` or `distilgpt2` instead

**Issue**: Repetitive responses
**Fix**: Try `temperature=0.9` for more variety

**Issue**: Off-character responses
**Fix**: Use `llama` model, it follows character better

## 📈 Performance

| Model | Speed | VRAM | Quality |
|-------|-------|------|---------|
| distilgpt2 | ⚡⚡⚡ | 0GB | ⭐⭐ |
| gpt2 | ⚡⚡ | 0GB | ⭐⭐⭐ |
| phi | ⚡ | 2-4GB | ⭐⭐⭐⭐ |
| llama | ⚡ | 2-4GB | ⭐⭐⭐⭐⭐ |
| mistral | 🐌 | 14GB+ | ⭐⭐⭐⭐⭐ |

---

**Happy detecting! 🔍**
