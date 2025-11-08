"""
Model Comparison Script - Test different LLMs with Nick Valentine
Runs the same query through different models to compare quality
"""

import pandas as pd
from sentence_transformers import SentenceTransformer
from transformers import pipeline, set_seed
import chromadb
import os

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("  NICK VALENTINE MODEL COMPARISON TEST")
print("="*80)

# Test query
TEST_QUERY = "Can you help me find someone who's missing?"

print(f"\n📝 Test Query: \"{TEST_QUERY}\"\n")

# Load dataset (minimal processing for testing)
print("Loading dataset...")
df = pd.read_csv('nick_valentine_dialogue.csv')
dialogue_pairs = []

for idx, row in df.iterrows():
    if pd.notna(row['RESPONSE TEXT']) and row['RESPONSE TEXT'].strip():
        query = row['DIALOGUE BEFORE'] if pd.notna(row['DIALOGUE BEFORE']) else row['SCRIPT NOTES']
        if pd.notna(query):
            dialogue_pairs.append({
                'query_text': str(query).strip(),
                'response_text': str(row['RESPONSE TEXT']).strip()
            })

df_contextual = pd.DataFrame(dialogue_pairs)
print(f"✓ Loaded {len(df_contextual)} dialogue entries\n")

# Load embedder
print("Loading embedding model...")
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("✓ Embedder ready\n")

# Setup ChromaDB (simple version)
client = chromadb.Client()
collection = client.get_or_create_collection(name="test_comparison")

if collection.count() == 0:
    print("Indexing dialogues...")
    embeddings = embedder.encode(df_contextual['query_text'].tolist()[:500], show_progress_bar=True)
    collection.add(
        embeddings=embeddings.tolist(),
        documents=df_contextual['query_text'].tolist()[:500],
        metadatas=df_contextual[['query_text', 'response_text']].head(500).to_dict(orient='records'),
        ids=[f"test_{i}" for i in range(500)]
    )
    print("✓ Indexed 500 dialogues\n")

# Retrieve context
query_embedding = embedder.encode([TEST_QUERY]).tolist()
results = collection.query(query_embeddings=query_embedding, n_results=3, include=['metadatas'])
retrieved = [r['response_text'] for r in results['metadatas'][0]]

print("🔍 Retrieved similar Nick Valentine responses:")
for i, resp in enumerate(retrieved[:2], 1):
    print(f"   {i}. \"{resp[:100]}...\"")
print()

# Models to test
MODELS_TO_TEST = {
    "GPT-2 Medium": "gpt2-medium",
    "DistilGPT-2": "distilgpt2",
}

# Test each model
print("="*80)
print("  TESTING MODELS")
print("="*80 + "\n")

results_comparison = []

for model_name, model_id in MODELS_TO_TEST.items():
    print(f"🤖 Testing: {model_name}")
    print("-" * 80)
    
    try:
        # Load model
        gen = pipeline('text-generation', model=model_id, max_new_tokens=60, truncation=True)
        set_seed(42)
        
        # Create prompt
        prompt = f"""Nick Valentine is a synth detective from Fallout 4. He's witty, uses 1940s detective slang.

Example Nick responses:
- "{retrieved[0][:80]}..."
- "{retrieved[1][:80]}..."

User: {TEST_QUERY}
Nick Valentine:"""
        
        # Generate
        output = gen(
            prompt,
            num_return_sequences=1,
            do_sample=True,
            temperature=0.75,
            top_k=50,
            top_p=0.92,
            pad_token_id=gen.tokenizer.eos_token_id
        )[0]['generated_text']
        
        # Extract response
        if "Nick Valentine:" in output:
            response = output.split("Nick Valentine:")[-1].strip()
            # Get first sentence
            for ending in ['.', '?', '!']:
                if ending in response:
                    response = response.split(ending)[0] + ending
                    break
            response = response.split('\n')[0].strip()
        else:
            response = "Generation failed"
        
        print(f"Response: {response}")
        print(f"✓ Success\n")
        
        results_comparison.append({
            'model': model_name,
            'response': response,
            'status': 'Success'
        })
        
    except Exception as e:
        print(f"✗ Error: {str(e)[:100]}\n")
        results_comparison.append({
            'model': model_name,
            'response': 'Failed to generate',
            'status': f'Error: {str(e)[:50]}'
        })

# Summary
print("="*80)
print("  RESULTS SUMMARY")
print("="*80 + "\n")

for result in results_comparison:
    print(f"📊 {result['model']}:")
    print(f"   Status: {result['status']}")
    print(f"   Response: \"{result['response']}\"")
    print()

print("="*80)
print("  Tips:")
print("  - For CPU: GPT-2 or DistilGPT-2 work well")
print("  - For GPU: Try 'phi' or 'llama' in main script")
print("  - Edit nick_valentine_chatbot.py line 30 to change model")
print("="*80)
