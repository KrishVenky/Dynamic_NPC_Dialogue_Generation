# Model Recommendations for NPC Dialogue Generation

## Current Status
✅ **System is working** - Generation runs without errors  
⚠️ **Response quality is limited** - Base GPT-2 produces inconsistent/incoherent responses

## Why GPT-2 Struggles

**Root Cause**: GPT-2 (all sizes: distilgpt2, gpt2, gpt2-medium, gpt2-large) are **text completion models**, NOT instruction-following models.

- ❌ Not trained to answer questions
- ❌ Not trained to stay in character
- ❌ Not trained to follow system instructions
- ✅ Only trained to continue text naturally

### Example Issues You're Seeing:
```
User: "Why is Shinra hurting the planet?"
Barrett (expected): "They're suckin' the life outta the Planet with those damn Mako Reactors!"
Barrett (actual GPT-2): "I'm sorry to hear that. But this isn't what he's doing..."
```

## Recommended Solutions

### Option 1: Use Instruction-Tuned Models (BEST for Quality)
These models are specifically trained to follow instructions and answer questions:

#### **Flan-T5-Base** (220M params, FREE)
```python
# In dialogue_engine.py, change:
generation_model: str = "google/flan-t5-base"

# Note: Requires minor code changes to use seq2seq pipeline instead of text-generation
```

**Pros:**
- ✅ Trained for Q&A and instruction-following
- ✅ Good quality responses
- ✅ Reasonable size (~1GB download)
- ✅ Works well on CPU

**Cons:**
- ⚠️ Requires code modification (different pipeline type)
- ⚠️ Slightly slower than GPT-2

#### **Flan-T5-Large** (780M params, FREE)
- Better quality than base
- Larger download (~3GB)
- Slower on CPU

### Option 2: Use Smaller Instruction Models

#### **TinyLlama-1.1B-Chat** (1.1B params, FREE)
```bash
export LOCAL_GEN_MODEL="TinyLlama/TinyLlama-1.1B-Chat-v1.0"
```

**Pros:**
- ✅ Instruction-tuned for chat
- ✅ Good balance of size/quality
- ✅ Works with existing code

**Cons:**
- ⚠️ Larger download (~2.2GB)
- ⚠️ Slower generation on CPU

### Option 3: Stick with GPT-2 but Lower Expectations

If you MUST use GPT-2 (no code changes, fast), accept that:
- ❌ Responses will be inconsistent
- ❌ May not answer questions directly
- ❌ May go off-topic
- ✅ But it's fast and works locally

**Improvement tips:**
1. Use very simple, short prompts
2. Include more examples (3-4 instead of 2)
3. Use greedy decoding (do_sample=False) for consistency
4. Post-process heavily to extract useful parts

### Option 4: Hybrid Approach (RECOMMENDED for Demo)

Use **retrieval-based responses** when possible, **generation as fallback**:

```python
# Pseudo-code
def get_response(npc, query):
    # 1. Try to find a similar question in memory
    memories = retrieve_memories(query, n=5)
    
    # 2. If we have a very similar question (score > 0.8), reuse that response
    if memories[0]['score'] > 0.8:
        return memories[0]['document']  # Return existing dialogue
    
    # 3. Otherwise, generate (with low expectations)
    return generate_response(npc, query, memories)
```

**Pros:**
- ✅ High quality when retrieval works
- ✅ Uses your FF7 dialogue corpus directly
- ✅ Fast (no generation needed most of the time)
- ✅ Very in-character (actual game dialogue)

**Cons:**
- ⚠️ Limited to topics covered in your dataset
- ⚠️ Less "dynamic" feeling

## Quick Setup Guide

### To Try TinyLlama (Easy, Just Environment Variable):
```bash
# In terminal, before running test.py:
export LOCAL_GEN_MODEL="TinyLlama/TinyLlama-1.1B-Chat-v1.0"
python test.py
```

### To Try Flan-T5 (Requires Code Change):
1. Install: `pip install torch transformers sentencepiece`
2. Modify `_init_local_generator()` in `dialogue_engine.py`:
```python
def _init_local_generator(self):
    if self._generator is None:
        model_name = os.getenv('LOCAL_GEN_MODEL', self.generation_model_name)
        
        # Check if it's a T5 model
        if 't5' in model_name.lower():
            self._generator = pipeline("text2text-generation", model=model_name, device=-1)
        else:
            self._generator = pipeline("text-generation", model=model_name, device=-1)
    return self._generator
```
3. Update `generate()` method to handle text2text output format

### To Implement Hybrid Retrieval-First Approach:
See `HYBRID_DEMO.py` (I can create this if you want)

## For Your TA Demo

### What to Show:
1. **Retrieval System** (Already working great!)
   - Show how the system finds relevant FF7 dialogue
   - Demonstrate semantic search working

2. **Memory System** (Already working!)
   - Show conversation history being stored
   - Show memory influencing responses

3. **Persona System** (Already working!)
   - Show character-specific prompts
   - Demonstrate persona configs

### What to Emphasize:
- ✅ "The architecture is sound - RAG + memory + personas"
- ✅ "Retrieval finds relevant context correctly"
- ✅ "Generation quality limited by free model constraints"
- ✅ "Could plug in better models (GPT-4, Claude) via API if budget allows"

### What NOT to Demo:
- ❌ Complex open-ended questions (expose GPT-2 weaknesses)
- ❌ Multi-turn conversations (generation quality degrades)

### SAFE Demo Questions:
Use questions that match your dataset closely:
- "Tell me about Mako energy" (should retrieve relevant Barrett/Barret dialogue)
- "What do you think of Shinra?" (good retrieval target)
- "How are you feeling?" (simple, character-appropriate)

## Current System Performance

| Component | Status | Quality |
|-----------|--------|---------|
| RAG Retrieval | ✅ Working | Excellent |
| Memory System | ✅ Working | Excellent |
| Persona Loading | ✅ Working | Good |
| Prompt Assembly | ✅ Working | Good |
| Generation (GPT-2) | ✅ Working | Poor |

## Bottom Line

Your **system architecture is solid**. The limiting factor is the generation model. You have 3 paths:

1. **Easy + Low Quality**: Stick with GPT-2, accept limitations (current state)
2. **Medium Effort + Better**: Try TinyLlama with env variable
3. **More Work + Best Free**: Implement Flan-T5 with code changes

For a class demo, I'd recommend **Option 1 + Hybrid approach** - show off the retrieval system (which works great) and explain that generation is a "future improvement area" with better models.

---

**Need help implementing any of these? Let me know which path you want to take!**
