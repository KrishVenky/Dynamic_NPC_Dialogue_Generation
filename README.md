# Nick Valentine Dialogue Generator - Fallout 4 RAG Chatbot

A retrieval-augmented generation (RAG) chatbot that simulates conversations with **Nick Valentine**, the synth detective from Fallout 4, using his actual in-game dialogue dataset.

## 🎭 About Nick Valentine

Nick Valentine is a unique character in Fallout 4:
- Pre-war prototype synth detective
- Has memories of a 1940s-era detective 
- Located in Diamond City, Commonwealth
- Known for his noir detective personality, wit, and philosophical views on being a synthetic human
- Uses classic detective slang: "pal", "doll", "case", "dame"

## 📊 Dataset

**Source**: `nick_valentine_dialogue.csv` - Complete Nick Valentine dialogue from Fallout 4

- **Total entries**: 2,569 dialogue lines
- **Conversational pairs**: 913 entries with context
- **Categories**: Scene dialogues, miscellaneous, topics, detection, combat
- **Features**: Mood/emotion tags, scene context, script notes

### Dataset Structure:
- `DIALOGUE BEFORE`: What was said to Nick (context/query)
- `RESPONSE TEXT`: Nick's actual response
- `SCRIPT NOTES`: Emotional tone and situational context  
- `SCENE`: Game scene identifier
- `CATEGORY/TYPE`: Dialogue classification

## 🚀 Setup

### Prerequisites

```bash
# Activate your virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install required packages
pip install pandas sentence-transformers transformers chromadb numpy python-dotenv huggingface-hub torch
```

### Optional: For Llama Models

Create a `.env` file:
```
HUGGINGFACE_TOKEN=your_hf_token_here
```

Get your token from: https://huggingface.co/settings/tokens

## 🎮 Usage

### Run the Chatbot

```bash
python nick_valentine_chatbot.py
```

### Chat Commands

- `exit` or `quit` - End conversation
- `clear` - Reset conversation history
- `help` - Get tips on what to ask Nick

### Example Conversations

```
You: Can you help me find someone?
Nick Valentine: That's what I do. Give me the details, and we'll see what we can dig up.

You: What's it like being a synth?
Nick Valentine: I'm a synth. Synthetic man. All the parts, minus a few red blood cells.

You: Tell me about Diamond City
Nick Valentine: Good to be back in Diamond City.
```

## 🤖 Available Models

The chatbot supports multiple language models. Change the model by editing line 30 in `nick_valentine_chatbot.py`:

```python
SELECTED_MODEL = "gpt2"  # Change to test different models
```

### Model Options:

| Model | Speed | Quality | GPU Required | Best For |
|-------|-------|---------|--------------|----------|
| **gpt2** (default) | Fast | Good | No | Quick testing, CPU usage |
| **distilgpt2** | Very Fast | Moderate | No | Fastest responses |
| **phi** | Medium | Very Good | Recommended | Balanced quality/speed |
| **llama** | Medium-Slow | Excellent | Highly Recommended | Best quality responses |
| **mistral** | Slow | Excellent | Yes (16GB+ VRAM) | Highest quality |

See `MODEL_TESTING_GUIDE.md` for detailed comparison.

## 🧠 How It Works

### RAG Architecture

1. **Data Processing**: 
   - Loads Nick Valentine's dialogue from CSV
   - Extracts context, mood, and conversational pairs
   - Processes 2,569 dialogue entries into searchable format

2. **Embedding & Storage**:
   - Uses `sentence-transformers/all-MiniLM-L6-v2` for embeddings
   - Stores in ChromaDB vector database for fast retrieval
   - Indexes both conversational pairs and standalone dialogues

3. **Response Generation**:
   - Embeds user query
   - Retrieves top-k similar dialogue exchanges
   - Constructs context-aware prompt with Nick's personality
   - Generates response using selected LLM
   - Cleans and formats output

4. **Character Consistency**:
   - Incorporates Nick's personality profile
   - Uses mood/emotion tags from original dialogue
   - Maintains conversation history
   - Applies detective noir speaking style

## 📁 Project Structure

```
Dynamic_NPC_Dialogue_Generation/
├── nick_valentine_chatbot.py      # Main chatbot script
├── nick_valentine_dialogue.csv    # Dataset (2,569 dialogues)
├── test_dataset.py                # Dataset verification script
├── MODEL_TESTING_GUIDE.md         # Model comparison guide
├── README.md                      # This file
├── .env                           # HuggingFace token (optional)
└── chroma_db_nick_valentine/      # Vector DB (auto-generated)
```

## 🔧 Configuration

### Adjust Generation Quality

Edit these parameters in `nick_valentine_chatbot.py` (around line 217):

```python
temperature=0.75,    # Higher = more creative (0.5-1.0)
top_k=50,           # Limits vocabulary (30-100)
top_p=0.92,         # Nucleus sampling (0.8-0.95)
max_new_tokens=80   # Response length (50-150)
```

### Change Embedding Model

Line 14:
```python
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
```

## 🧪 Testing

Run the dataset verification:
```bash
python test_dataset.py
```

This shows:
- Dataset statistics
- Sample dialogue pairs
- Category breakdown
- Data quality check

## 💡 Tips for Best Results

### Questions Nick Responds Well To:
- Detective work and investigations
- His past and memories
- Being a synth/synthetic
- Diamond City and the Commonwealth
- Finding missing persons
- Philosophical questions about identity

### Model Recommendations:
- **CPU only**: Use `gpt2` or `distilgpt2`
- **GPU 6-8GB**: Use `phi` or `llama`  
- **GPU 16GB+**: Use `mistral` for best quality
- **Quick testing**: Start with `gpt2`

## 🐛 Troubleshooting

### Out of Memory
- Switch to smaller model (`distilgpt2` or `gpt2`)
- Reduce conversation history (line 251)
- Lower `max_new_tokens`

### Slow Responses
- Use smaller model
- Enable GPU if available
- Reduce retrieval count (line 180)

### Poor Quality
- Try `llama` or `phi` models
- Increase `temperature` for creativity
- Check if question fits Nick's character

### ChromaDB Errors
- Delete `chroma_db_nick_valentine/` folder
- Re-run to rebuild database

## 📝 Technical Details

- **Embedding Model**: all-MiniLM-L6-v2 (384 dimensions)
- **Vector Database**: ChromaDB (persistent storage)
- **Generation Models**: GPT-2, DistilGPT-2, Phi-1.5, Llama-3.2, Mistral-7B
- **Context Window**: Last 3 conversation turns
- **Retrieval**: Top-10 similar dialogues, filtered to top-3
- **Temperature**: 0.75 (balanced creativity)

## 🎯 Future Improvements

- [ ] Add more Fallout NPCs (Piper, Hancock, etc.)
- [ ] Implement conversation memory persistence
- [ ] Add quest/mission context awareness
- [ ] Fine-tune small model on Nick's dialogue
- [ ] Web interface with Gradio/Streamlit
- [ ] Multi-turn dialogue coherence improvements

## 📜 License

This project is for educational purposes. Fallout 4 dialogue and characters are property of Bethesda Softworks.

## 🙏 Credits

- **Dataset**: Nick Valentine dialogue from Fallout 4
- **Game**: Bethesda Game Studios
- **Models**: HuggingFace Transformers
- **Embeddings**: sentence-transformers
- **Vector DB**: ChromaDB

---

**Stay safe out there in the Commonwealth, pal.** 🕵️‍♂️
