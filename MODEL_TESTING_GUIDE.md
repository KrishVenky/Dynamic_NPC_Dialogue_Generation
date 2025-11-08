# Nick Valentine Chatbot - Model Testing Configuration

## Available Models

You can test different language models by changing the `SELECTED_MODEL` variable in `nick_valentine_chatbot.py` (line 30).

### Models Available:

1. **gpt2** (Default)
   - Model: `gpt2-medium`
   - Speed: Fast
   - Quality: Good
   - GPU: Not required
   - Best for: Quick testing, decent responses

2. **distilgpt2**
   - Model: `distilgpt2`
   - Speed: Very Fast
   - Quality: Moderate
   - GPU: Not required
   - Best for: Fastest responses, lower quality

3. **phi**
   - Model: `microsoft/phi-1_5`
   - Speed: Medium
   - Quality: Very Good
   - GPU: Recommended
   - Best for: High quality with small model size

4. **llama**
   - Model: `meta-llama/Llama-3.2-1B-Instruct`
   - Speed: Medium-Slow
   - Quality: Excellent
   - GPU: Highly recommended
   - HF Token: Required
   - Best for: Best quality responses, instruction following

5. **mistral**
   - Model: `mistralai/Mistral-7B-Instruct-v0.1`
   - Speed: Slow
   - Quality: Excellent
   - GPU: Required (16GB+ VRAM)
   - HF Token: May be required
   - Best for: Highest quality (if you have a powerful GPU)

## How to Switch Models

Open `nick_valentine_chatbot.py` and change line 30:

```python
SELECTED_MODEL = "gpt2"  # Change to "llama", "phi", "mistral", etc.
```

## Dataset Information

**Source**: Nick Valentine dialogue from Fallout 4
- Total entries: 2,569 dialogue lines
- Entries with context: ~913 conversational pairs
- Includes: Scene context, mood/emotion, script notes

**Key Features**:
- DIALOGUE BEFORE: What was said to Nick (query)
- RESPONSE TEXT: Nick's actual response
- SCRIPT NOTES: Emotional tone and context
- SCENE: Game scene identifier

## Running the Chatbot

```bash
python nick_valentine_chatbot.py
```

## Commands During Chat

- `exit` or `quit` - End conversation
- `clear` - Reset conversation history
- `help` - Get tips on what to ask Nick

## Example Questions

- "Can you help me find someone?"
- "What's it like being a synth?"
- "Tell me about Diamond City"
- "Any interesting cases lately?"
- "What do you think about the Institute?"

## Performance Tips

1. **For CPU only**: Use `gpt2` or `distilgpt2`
2. **With GPU (6-8GB VRAM)**: Use `phi` or `llama`
3. **With GPU (16GB+ VRAM)**: Use `mistral` for best quality
4. **For testing**: Start with `gpt2`, then try `llama` if you have GPU

## Troubleshooting

**Out of memory errors**: 
- Switch to a smaller model (`distilgpt2` or `gpt2`)
- Reduce conversation history in code

**Slow responses**:
- Ensure you're using GPU if available
- Use a smaller model
- Reduce `max_new_tokens` in the code

**Poor quality responses**:
- Try `llama` or `phi` models
- Increase `temperature` (line 217) for more creative responses
- Check if your question is relevant to Nick's character
