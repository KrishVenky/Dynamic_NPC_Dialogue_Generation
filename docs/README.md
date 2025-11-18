# Nick Valentine Dialogue Generator 🕵️

Dynamic NPC dialogue generator for Nick Valentine from Fallout 4, powered by Google Gemini AI.

## Features

- 🤖 **AI-Powered Dialogue**: Uses Gemini 1.5 Flash for natural, in-character responses
- 🎭 **Context-Aware**: Different response styles for investigation, combat, casual, etc.
- 😊 **Emotion Control**: Generate responses with specific emotional tones
- 💬 **Conversation History**: Maintains context across multiple exchanges
- 💰 **Cost-Effective**: Uses Gemini Flash free tier for minimal costs
- 🎨 **Interactive UI**: Clean, modern interface for dialogue generation
- 📊 **Analytics**: Track message count and estimated costs
- 💾 **Export**: Save conversations as JSON

## Setup

### Prerequisites

- Node.js (v18 or higher)
- A Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone or navigate to the project directory**

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   GEMINI_MODEL=gemini-1.5-flash
   PORT=3000
   ```

4. **Start the server**
   ```bash
   npm start
   ```
   
   Or for development with auto-reload:
   ```bash
   npm run dev
   ```

5. **Open your browser**
   
   Navigate to `http://localhost:3000`

## Usage

### Web Interface

1. Enter what you want to say to Nick in the text area
2. Select a context (Investigation, Combat, Casual, etc.)
3. Optionally select an emotion/tone
4. Click "Generate Response" or press Enter
5. View Nick's response in the conversation panel

### API Endpoints

#### Generate Dialogue
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

#### Generate Multiple Variations
```bash
POST /api/variations
Content-Type: application/json

{
  "userInput": "Tell me about your past",
  "count": 3,
  "context": "emotional"
}
```

#### Get Conversation History
```bash
GET /api/history
```

#### Reset Conversation
```bash
POST /api/reset
```

#### Export Conversation
```bash
GET /api/export
```

#### Get Cost Estimate
```bash
GET /api/cost-estimate?exchanges=100
```

## Project Structure

```
AFML_Project_NPC_Final/
├── public/                      # Frontend files
│   ├── index.html              # Main UI
│   ├── styles.css              # Styling
│   └── app.js                  # Frontend logic
├── nick_personality.js         # Character profile & prompt engineering
├── dialogue_processor.js       # CSV parser & context retrieval
├── dialogue_generator.js       # Gemini AI integration
├── server.js                   # Express server
├── nick_valentine_dialogue.csv # Original dialogue data
├── package.json                # Dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

## How It Works

### Prompt Engineering

The system uses sophisticated prompt engineering to generate authentic Nick Valentine dialogue:

1. **Character Profile**: Comprehensive personality traits, background, values, and speech patterns
2. **Contextual Examples**: Pulls relevant dialogue from the CSV based on context
3. **Conversation History**: Maintains recent exchanges for continuity
4. **Dynamic Context**: Adjusts tone and style based on situation

### Context Types

- **Investigation**: Detective work, asking questions, examining clues
- **Combat**: Tense situations, danger, protective responses
- **Casual**: Regular conversation, idle chatter
- **Emotional**: Personal moments, vulnerability
- **Moral Choice**: Ethical decisions, expressing values
- **Location**: Comments about places
- **Greeting**: Meeting people, introductions

### Emotion Options

- Neutral, Amused, Stern, Concerned, Irritated, Somber, Puzzled, Angry, Surprised

## Cost Optimization

### Gemini 1.5 Flash FREE Tier

Gemini 1.5 Flash offers a generous **free tier**:
- 15 requests per minute (RPM)
- 1 million tokens per minute (TPM)
- 1,500 requests per day (RPD)

This is more than enough for dialogue generation!

### Cost Estimates (if exceeding free tier)

- **Per 100 exchanges**: ~$0.0045
- **Per 1,000 exchanges**: ~$0.045
- **Per 10,000 exchanges**: ~$0.45

### Tips to Minimize Costs

1. **Disable Examples**: Uncheck "Include Examples" to reduce input tokens by ~50%
2. **Shorter Context**: Keep conversations concise
3. **Use Flash Model**: Stick with `gemini-1.5-flash` (not Pro)
4. **Clear History**: Reset conversation periodically to reduce context size

## Advanced: Vector Database Integration (Optional)

For even better context retrieval, you can implement a vector database:

### Why Vector DB?

- **Semantic Search**: Find similar dialogues by meaning, not just keywords
- **Better Context**: Retrieve the most relevant examples automatically
- **Scalability**: Handle larger dialogue datasets efficiently

### Implementation Options

#### Option 1: ChromaDB (Recommended for Local)

```bash
npm install chromadb
```

```javascript
import { ChromaClient } from 'chromadb';

class VectorDialogueRetriever {
  async initialize() {
    this.client = new ChromaClient();
    this.collection = await this.client.getOrCreateCollection({
      name: "nick_dialogues"
    });
    
    // Embed all dialogues
    await this.embedDialogues();
  }
  
  async embedDialogues() {
    // Add dialogues with embeddings
    for (const dialogue of this.dialogues) {
      await this.collection.add({
        ids: [dialogue.id],
        documents: [dialogue.responseText],
        metadatas: [{
          context: dialogue.context,
          emotion: dialogue.emotion
        }]
      });
    }
  }
  
  async findSimilar(query, n = 5) {
    const results = await this.collection.query({
      queryTexts: [query],
      nResults: n
    });
    return results;
  }
}
```

#### Option 2: Pinecone (Recommended for Production)

```bash
npm install @pinecone-database/pinecone
```

Benefits:
- Fully managed
- Serverless option (pay-per-use)
- High performance
- Free tier available

#### Option 3: Local Embeddings with Transformers.js

```bash
npm install @xenova/transformers
```

```javascript
import { pipeline } from '@xenova/transformers';

const embedder = await pipeline('feature-extraction', 
  'Xenova/all-MiniLM-L6-v2');
```

### Integration Steps

1. Generate embeddings for all dialogue entries
2. Store in vector database
3. When generating response, query for similar dialogues
4. Use retrieved dialogues as examples in prompt
5. Fall back to random selection if no good matches

## Fine-Tuning with Hugging Face (Alternative Approach)

### Why Fine-Tune?

- **Better Character Accuracy**: Model learns Nick's exact patterns
- **Cheaper at Scale**: No prompt engineering needed for each request
- **Faster Responses**: Smaller, specialized model

### Why NOT to Fine-Tune (for this project)

- **Initial Effort**: Requires dataset preparation, training setup
- **Cost**: Training costs money and compute time
- **Maintenance**: Need to retrain when updating dialogue
- **Overkill**: Prompt engineering with Gemini works great for this use case

### If You Want to Fine-Tune Anyway

**Best Model Choice**: `facebook/opt-1.3b` or `gpt2-medium`

**Steps**:

1. **Prepare Dataset** (JSONL format):
   ```json
   {"prompt": "Player: What do you think about synths?", "completion": "Look at me. I'm trash. They threw me in the junk pile ages ago."}
   {"prompt": "Player: Tell me about Diamond City.", "completion": "Night is when the green jewel feels the most honest. Bright lights, but a lot of shadows."}
   ```

2. **Use Hugging Face AutoTrain**:
   ```bash
   pip install autotrain-advanced
   autotrain llm --train \
     --model facebook/opt-1.3b \
     --data-path ./nick_dialogues.jsonl \
     --text-column prompt \
     --target-column completion
   ```

3. **Deploy** with Hugging Face Inference API or locally

4. **Cost**: ~$10-50 for training, then inference costs

### Verdict

**For your use case**: Stick with **Gemini + Prompt Engineering**
- Free tier covers most usage
- No training hassle
- Easy to update and modify
- Quality is excellent with good prompts

## Troubleshooting

### "GEMINI_API_KEY not found"
- Make sure you created a `.env` file (not `.env.example`)
- Verify the API key is correct
- Restart the server after adding the key

### Responses seem out of character
- Try enabling "Include Examples"
- Select more specific context
- Check that your CSV file is in the root directory

### High API costs
- Disable "Include Examples" to reduce tokens by 50%
- Use `gemini-1.5-flash` instead of Pro
- Reset conversation history regularly
- Consider implementing caching for common queries

## Contributing

Feel free to enhance this project! Ideas:
- Add more context types
- Implement vector database for better retrieval
- Add voice synthesis for Nick's responses
- Create conversation visualizations
- Add dialogue branching/choices

## License

MIT

## Credits

- Nick Valentine dialogue from Fallout 4 by Bethesda Game Studios
- Powered by Google Gemini AI
- Built with Express.js and vanilla JavaScript

---

**Have fun chatting with Nick Valentine!** 🕵️‍♂️
