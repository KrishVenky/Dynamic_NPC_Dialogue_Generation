"""
Quick launcher for Nick Valentine chatbot with model selection
"""

import sys
import os

print("="*80)
print("  NICK VALENTINE CHATBOT LAUNCHER")
print("="*80)

print("\n🤖 Available Models:\n")
print("  1. GPT-2 Medium (Default) - Fast, good quality, CPU-friendly")
print("  2. DistilGPT-2 - Very fast, moderate quality, CPU-friendly")
print("  3. Phi-1.5 - Slower, very good quality, GPU recommended")
print("  4. Llama-3.2-1B - Good speed, excellent quality, GPU recommended")
print("  5. Mistral-7B - Slow, best quality, requires powerful GPU\n")

print("⚙️  Current Setup:")
print("  - Embedding: sentence-transformers/all-MiniLM-L6-v2")
print("  - Dataset: 2,569 Nick Valentine dialogue entries")
print("  - Vector DB: ChromaDB\n")

choice = input("Select model (1-5) or press Enter for default [1]: ").strip()

model_map = {
    "1": "gpt2",
    "2": "distilgpt2", 
    "3": "phi",
    "4": "llama",
    "5": "mistral",
    "": "gpt2"
}

selected = model_map.get(choice, "gpt2")

print(f"\n✓ Selected: {selected.upper()}")
print("\nStarting chatbot...\n")
print("="*80)

# Modify the model in the script temporarily
import nick_valentine_chatbot as nvc

# Override the selected model
nvc.SELECTED_MODEL = selected
nvc.GENERATION_MODEL_NAME = nvc.GENERATION_MODELS[selected]

# Run the chatbot
if __name__ == "__main__":
    # Re-execute with the new model
    print(f"\nNote: To permanently change model, edit nick_valentine_chatbot.py line 30")
    print(f"      Set SELECTED_MODEL = \"{selected}\"\n")
    
    exec(open("nick_valentine_chatbot.py").read())
