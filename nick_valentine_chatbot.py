import pandas as pd
from sentence_transformers import SentenceTransformer
from transformers import pipeline, set_seed, AutoModelForCausalLM, AutoTokenizer
import chromadb
import os 
from huggingface_hub import login
from dotenv import load_dotenv
import torch

load_dotenv()
hf_token = os.getenv("HUGGINGFACE_TOKEN")

# --- 0. Configuration & Hugging Face Token Setup ---
# Only set HF_TOKEN if it exists (optional, only needed for Llama/Mistral)
if hf_token:
    os.environ["HF_TOKEN"] = hf_token
    try:
        login(token=hf_token, add_to_git_credential=False)
        print("✓ HuggingFace token loaded successfully")
    except Exception as e:
        print(f"⚠ HuggingFace login failed: {e}")
else:
    print("ℹ No HuggingFace token found (only needed for Llama/Mistral models)") 

# --- Model Configuration ---
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Available generation models (choose one or test multiple)
GENERATION_MODELS = {
    "gpt2": "gpt2-medium",  # Fast, decent quality
    "distilgpt2": "distilgpt2",  # Faster, lighter
    "phi": "microsoft/phi-1_5",  # Small but powerful
    "llama": "meta-llama/Llama-3.2-1B-Instruct",  # Requires HF token, very good quality
    "mistral": "mistralai/Mistral-7B-Instruct-v0.1",  # Best quality but slower (requires good GPU)
}

# Select which model to use (change this to test different models)
SELECTED_MODEL = "gpt2"  # Change to "llama", "phi", etc. to test others
GENERATION_MODEL_NAME = GENERATION_MODELS[SELECTED_MODEL]

# ChromaDB Setup
CHROMA_DB_PATH = "./chroma_db_nick_valentine" 
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
COLLECTION_NAME = "nick_valentine_dialogue_rag"

# --- Nick Valentine Character Profile ---
NICK_VALENTINE_PROFILE = """Nick Valentine is a synthetic detective in Fallout 4's Commonwealth. He's:
- A pre-war prototype synth with the memories of a 2070s detective
- Cynical, witty, and world-weary but fundamentally good-hearted
- Uses 1940s noir detective slang and mannerisms
- Philosophical about being a machine with human memories
- Empathetic despite his mechanical nature
- Skilled investigator who notices details
- Often sarcastic but never cruel
Speaking style: Uses terms like "pal", "doll", "dame", "case", "caps". Makes noir references and detective analogies."""

# --- 1. Data Loading and Processing ---
print("Loading Nick Valentine dialogue dataset...")
df = pd.read_csv('nick_valentine_dialogue.csv')

# Create dialogue pairs from the dataset
dialogue_pairs = []

for idx, row in df.iterrows():
    dialogue_before = row['DIALOGUE BEFORE']
    response_text = row['RESPONSE TEXT']
    script_notes = row['SCRIPT NOTES']
    scene = row['SCENE']
    category = row['CATEGORY']
    subtype = row['SUBTYPE']
    
    # Skip if response text is missing
    if pd.isna(response_text) or response_text.strip() == "":
        continue
    
    # Extract mood/emotion from SCRIPT NOTES
    mood = "Neutral"
    if pd.notna(script_notes):
        # Extract emotion keywords from script notes
        script_lower = str(script_notes).lower()
        if any(word in script_lower for word in ['happy', 'amused', 'cheerful']):
            mood = "Happy"
        elif any(word in script_lower for word in ['stern', 'angry', 'irritated']):
            mood = "Stern"
        elif any(word in script_lower for word in ['sad', 'somber', 'melancholic']):
            mood = "Sad"
        elif any(word in script_lower for word in ['surprised', 'shocked']):
            mood = "Surprised"
        elif any(word in script_lower for word in ['question', 'puzzled', 'confused']):
            mood = "Questioning"
        elif any(word in script_lower for word in ['confident', 'determined']):
            mood = "Confident"
        elif any(word in script_lower for word in ['tired', 'weary']):
            mood = "Tired"
        elif any(word in script_lower for word in ['pleading', 'desperate']):
            mood = "Pleading"
    
    # Create context from scene and script notes
    context = ""
    if pd.notna(scene):
        context = f"Scene: {scene}"
    if pd.notna(script_notes):
        context += f" | Context: {script_notes}"
    
    # Handle two types of entries: those with "DIALOGUE BEFORE" and standalone responses
    if pd.notna(dialogue_before) and dialogue_before.strip() != "":
        # This is a conversational exchange
        query_text = str(dialogue_before).strip()
        
        # Clean up the query text (remove speaker prefix if present)
        if ':' in query_text:
            query_text = query_text.split(':', 1)[1].strip()
        
        dialogue_pairs.append({
            'context': context.strip(),
            'mood': mood,
            'query_text': query_text,
            'response_text': response_text.strip(),
            'category': category,
            'scene': scene if pd.notna(scene) else ""
        })
    else:
        # Standalone dialogue (greeting, idle, etc.)
        # Use the response itself as a searchable greeting/comment
        # We'll use the script notes or category as the "query"
        query_text = f"{subtype} dialogue" if pd.notna(subtype) else "General dialogue"
        if pd.notna(script_notes) and len(str(script_notes)) > 10:
            query_text = str(script_notes)[:100]  # Use context as query
        
        dialogue_pairs.append({
            'context': context.strip(),
            'mood': mood,
            'query_text': query_text,
            'response_text': response_text.strip(),
            'category': category,
            'scene': scene if pd.notna(scene) else ""
        })

df_contextual = pd.DataFrame(dialogue_pairs)
print(f"Processed {len(df_contextual)} dialogue entries from Nick Valentine dataset.")

# --- 2. Initialize Embedder and Generator Models ---
print(f"\nLoading Embedding Model: {EMBEDDING_MODEL_NAME}...")
embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
print("Embedding Model Loaded.")

print(f"\nLoading Generation Model: {GENERATION_MODEL_NAME}...")
print(f"Selected model type: {SELECTED_MODEL}")

# Initialize the generator based on model type
if SELECTED_MODEL == "llama" and torch.cuda.is_available():
    # For Llama models, use more optimized loading
    try:
        tokenizer = AutoTokenizer.from_pretrained(GENERATION_MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(
            GENERATION_MODEL_NAME,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        generator = pipeline(
            'text-generation',
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=80,
            truncation=True
        )
        print("Llama model loaded with GPU acceleration.")
    except Exception as e:
        print(f"Failed to load Llama model: {e}")
        print("Falling back to GPT-2...")
        GENERATION_MODEL_NAME = GENERATION_MODELS["gpt2"]
        generator = pipeline('text-generation', model=GENERATION_MODEL_NAME, max_new_tokens=80, truncation=True)
else:
    # Standard pipeline loading for other models
    generator = pipeline('text-generation', model=GENERATION_MODEL_NAME, max_new_tokens=80, truncation=True)

set_seed(42)
print("Generation Model Loaded.\n")

# --- 3. Setup ChromaDB ---
def initialize_chroma_db(df: pd.DataFrame, embedder: SentenceTransformer, client: chromadb.Client):
    """Initializes or loads the ChromaDB collection with Nick Valentine's dialogue."""
    
    # Ensure lowercase column names for metadata
    df_for_metadata = df.rename(columns={
        'context': 'context', 
        'mood': 'mood', 
        'query_text': 'query_text', 
        'response_text': 'response_text',
        'category': 'category',
        'scene': 'scene'
    })

    try:
        collection = client.get_or_create_collection(name=COLLECTION_NAME)
        print(f"ChromaDB collection '{COLLECTION_NAME}' accessed.")
        
        if collection.count() == 0 or collection.count() != len(df):
            print(f"Collection is empty or outdated. Indexing {len(df)} dialogue entries...")
            
            print("Generating embeddings for dialogue queries...")
            query_embeddings = embedder.encode(df_for_metadata['query_text'].tolist(), show_progress_bar=True)
            
            metadatas = df_for_metadata[[
                'context', 'mood', 'query_text', 'response_text', 'category', 'scene'
            ]].to_dict(orient='records')
            
            ids = [f"nick_pair_{i}" for i in range(len(df_for_metadata))]
            
            collection.add(
                embeddings=query_embeddings.tolist(), 
                documents=df_for_metadata['query_text'].tolist(), 
                metadatas=metadatas,
                ids=ids
            )
            print(f"Successfully added {collection.count()} entries to ChromaDB.")
        else:
            print(f"ChromaDB collection already contains {collection.count()} entries. Skipping re-indexing.")
            
    except Exception as e:
        print(f"Error initializing ChromaDB: {e}")
    
    return client.get_collection(name=COLLECTION_NAME)

chroma_collection = initialize_chroma_db(df_contextual, embedder, client)

# --- 4. RAG Chatbot Function ---
def nick_valentine_response(user_query: str, conversation_history: list, chroma_collection, embedder, generator) -> str:
    """Generates a Nick Valentine response using RAG."""
    
    # 1. Embed the user query
    user_query_embedding = embedder.encode([user_query]).tolist()
    
    # 2. Retrieve similar dialogue entries
    retrieved_results = chroma_collection.query(
        query_embeddings=user_query_embedding,
        n_results=10,
        include=['metadatas', 'documents'] 
    )

    # 3. Collect the best matching responses
    retrieved_dialogues = []
    for i in range(min(5, len(retrieved_results['documents'][0]))):
        metadata = retrieved_results['metadatas'][0][i]
        retrieved_dialogues.append({
            'query': retrieved_results['documents'][0][i],
            'response': metadata.get('response_text'),
            'mood': metadata.get('mood', 'Neutral'),
            'context': metadata.get('context', '')
        })
    
    # 4. Construct the RAG prompt with Nick Valentine's personality
    prompt = f"{NICK_VALENTINE_PROFILE}\n\n"
    prompt += "Previous conversation:\n"
    
    for entry in conversation_history[-3:]:
        prompt += f"{entry['speaker']}: {entry['text']}\n"
    
    if retrieved_dialogues:
        prompt += f"\nSimilar past interactions as Nick Valentine:\n"
        for i, dialogue in enumerate(retrieved_dialogues[:3]):
            prompt += f"When asked: \"{dialogue['query'][:80]}...\"\n"
            prompt += f"Nick said: \"{dialogue['response'][:100]}...\" ({dialogue['mood']})\n"
    
    prompt += f"\nUser: {user_query}\n"
    prompt += "Nick Valentine:"
    
    # 5. Generate response
    try:
        generated_output = generator(
            prompt, 
            num_return_sequences=1, 
            do_sample=True, 
            temperature=0.75,
            top_k=50, 
            top_p=0.92,
            pad_token_id=generator.tokenizer.eos_token_id if hasattr(generator.tokenizer, 'eos_token_id') else 50256,
            max_new_tokens=80
        )[0]['generated_text']

        # 6. Extract Nick's response
        if "Nick Valentine:" in generated_output:
            response_text = generated_output.split("Nick Valentine:")[-1].strip()
        else:
            response_text = generated_output.split(prompt)[-1].strip() if prompt in generated_output else generated_output.strip()
        
        # Clean up the response
        sentence_endings = ['.', '?', '!', '\n', '"']
        for ending in sentence_endings:
            if ending in response_text:
                # Get first complete sentence
                parts = response_text.split(ending)
                if parts[0].strip():
                    response_text = parts[0] + ending
                    break
        
        # Remove any remaining artifacts
        response_text = response_text.split('\n')[0].strip()
        response_text = response_text.replace("Nick Valentine:", "").strip()
        
        # Fallback if response is too short or empty
        if len(response_text) < 5:
            if retrieved_dialogues:
                return retrieved_dialogues[0]['response']
            return "That's a puzzle we'll have to solve together, pal."
        
        return response_text
        
    except Exception as e:
        print(f"Generation error: {e}")
        # Fallback to best retrieved response
        if retrieved_dialogues:
            return retrieved_dialogues[0]['response']
        return "Something's not adding up here. Let me think on that."

# --- 5. Interactive Chat Loop ---
if __name__ == "__main__":
    print("\n" + "="*70)
    print("  NICK VALENTINE CHATBOT - Fallout 4 Commonwealth Detective")
    print("="*70)
    print(f"\nGeneration Model: {SELECTED_MODEL.upper()} ({GENERATION_MODEL_NAME})")
    print("Embedding Model: all-MiniLM-L6-v2")
    print(f"Dataset: {len(df_contextual)} Nick Valentine dialogue entries")
    print("\nType 'exit' or 'quit' to end the conversation.")
    print("Type 'clear' to reset conversation history.")
    print("Type 'help' for tips on talking to Nick.")
    print("="*70 + "\n")

    conversation_history = []

    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\nNick Valentine: Stay safe out there in the Commonwealth.")
                break
            
            if user_input.lower() == 'clear':
                conversation_history = []
                print("\n[Conversation history cleared]\n")
                continue
            
            if user_input.lower() == 'help':
                print("\nTips for talking to Nick Valentine:")
                print("- Ask about detective work, cases, or investigations")
                print("- Discuss the Commonwealth, Diamond City, or synths")
                print("- Ask philosophical questions about memory and identity")
                print("- Request help finding someone or solving a mystery")
                print("- Ask about his past or being a synth\n")
                continue
            
            # Add user's input to history
            conversation_history.append({"speaker": "You", "text": user_input})

            # Generate Nick's response
            nick_response = nick_valentine_response(
                user_input, 
                conversation_history, 
                chroma_collection, 
                embedder, 
                generator
            )
            
            print(f"\nNick Valentine: {nick_response}")
            
            # Add Nick's response to history
            conversation_history.append({"speaker": "Nick Valentine", "text": nick_response})
            
            # Keep history manageable (last 6 exchanges)
            if len(conversation_history) > 12:
                conversation_history = conversation_history[-12:]
                
        except KeyboardInterrupt:
            print("\n\nNick Valentine: Looks like you've got somewhere to be. Catch you later.")
            break
        except Exception as e:
            print(f"\n[ERROR] Something went wrong: {e}")
            print("Nick Valentine: Technical difficulties. Give me a second to reboot my circuits.")
            continue

    print("\n" + "="*70)
    print("  Thanks for chatting with Nick Valentine!")
    print("="*70)
