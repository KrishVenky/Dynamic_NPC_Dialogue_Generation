import json
import pandas as pd
from sentence_transformers import SentenceTransformer
from transformers import pipeline, set_seed
import chromadb
import numpy as np
import os 
from huggingface_hub import login
from dotenv import load_dotenv

load_dotenv()
hf_token = os.getenv("HUGGINGFACE_TOKEN")

# --- 0. Configuration & Hugging Face Token Setup ---
# NOTE: Using os.getenv to securely access your HF_TOKEN environment variable.
os.environ["HF_TOKEN"] = hf_token
try:
    # Attempt to log in using the environment variable token
    login(token=os.getenv("HF_TOKEN"), add_to_git_credential=False)
except Exception:
    # This block executes if the token is not found or login fails (harmless for public models)
    pass 

# Model names
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
GENERATION_MODEL_NAME = "gpt2-medium"

# ChromaDB Client Setup
CHROMA_DB_PATH = "./chroma_db_ff7" 
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# ChromaDB Collection Name
COLLECTION_NAME = "ff7_dialogue_rag"

# --- NEW: CHARACTER PROFILES (The Personality/Mood Baseline for Fallback) ---
CHARACTER_PROFILES = {
    "cloud": "a cold, reserved ex-SOLDIER mercenary focused on his job and money.",
    "tifa": "a kind, caring, and compassionate friend who is fiercely loyal to her past and her cause.",
    "barret": "a loud, passionate, and fiercely anti-Shinra leader with a strong sense of justice.",
    "aerith": "a mysterious, cheerful, and sometimes mischievous flower girl with deep spiritual knowledge.",
    "red xiii": "an intelligent, proud, and wise creature who speaks formally about the Planet and his destiny.",
    "cid": "a gruff, frustrated, and cynical pilot who dreams of going to space and often yells.",
    "yuffie": "a sneaky, energetic, and playful materia hunter who is obsessed with stealing materia.",
    "vincent": "a stoic, melancholic figure with a dark past who speaks formally and with regret.",
    "cait sith": "a playful, fortune-telling feline robot with a surprisingly loyal heart and a Scottish accent."
}

# --- 1. Data Loading and Initial Processing (Dialogue Pairing) ---
# NOTE: This robustly recreates the contextual dialogue DataFrame
with open('data.json', 'r') as f:
    data = json.load(f)

script = data['text']
dialogue_pairs = []
last_dialogue_entry = None
current_location = "Start"
current_action = ""

for entry in script:
    keys = list(entry.keys())
    if not keys:
        continue
    
    key = keys[0]
    value = entry[key]

    if key == 'LOCATION':
        current_location = value
        last_dialogue_entry = None 
        
    elif key == 'ACTION':
        current_action = value 
        last_dialogue_entry = None
    
    elif key == 'CHOICE':
        last_dialogue_entry = None
    
    else: # Dialogue entry
        current_speaker, current_dialogue = key, value
        
        if last_dialogue_entry:
            query_speaker, query_text = list(last_dialogue_entry.items())[0]
            
            dialogue_pairs.append({
                'Location': current_location,
                'Context_Action': current_action,
                'Query_Speaker': query_speaker,
                'Query_Text': query_text,
                'Response_Speaker': current_speaker,
                'Response_Text': current_dialogue
            })
        
        last_dialogue_entry = entry
        current_action = "" 

df_contextual = pd.DataFrame(dialogue_pairs)

# --- 2. Initialize Embedder and Generator Models ---

print(f"Loading Embedding Model: {EMBEDDING_MODEL_NAME}...")
embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
print("Embedding Model Loaded.")

print(f"Loading Generation Model: {GENERATION_MODEL_NAME}...")
generator = pipeline('text-generation', model=GENERATION_MODEL_NAME, max_new_tokens=60, truncation=True)
set_seed(42) 
print("Generation Model Loaded.")

# --- 3. Setup ChromaDB and Add Data (CRITICAL FIX) ---

def initialize_chroma_db(df: pd.DataFrame, embedder: SentenceTransformer, client: chromadb.Client):
    """Initializes or loads the ChromaDB collection with dialogue queries."""
    
    # CRITICAL FIX: Rename columns to explicit lowercase for consistent metadata storage
    df_for_metadata = df.rename(columns={
        'Location': 'location', 
        'Context_Action': 'context_action', 
        'Query_Speaker': 'query_speaker', 
        'Query_Text': 'query_text', 
        'Response_Speaker': 'response_speaker', 
        'Response_Text': 'response_text'
    })

    try:
        collection = client.get_or_create_collection(name=COLLECTION_NAME)
        print(f"ChromaDB collection '{COLLECTION_NAME}' accessed.")
        
        if collection.count() == 0 or collection.count() != len(df):
            print(f"Collection '{COLLECTION_NAME}' is empty or outdated. Re-indexing...")
            
            print("Generating embeddings for dialogue queries...")
            query_embeddings = embedder.encode(df_for_metadata['query_text'].tolist(), show_progress_bar=True)
            
            metadatas = df_for_metadata[[
                'location', 'context_action', 'query_speaker', 'query_text', 
                'response_speaker', 'response_text'
            ]].to_dict(orient='records')
            
            ids = [f"pair_{i}" for i in range(len(df_for_metadata))]
            
            collection.add(
                embeddings=query_embeddings.tolist(), 
                documents=df_for_metadata['query_text'].tolist(), 
                metadatas=metadatas,
                ids=ids
            )
            print(f"Successfully added {collection.count()} entries to ChromaDB.")
        else:
            print(f"ChromaDB collection '{COLLECTION_NAME}' already contains {collection.count()} entries. Skipping re-indexing.")
            
    except Exception as e:
        print(f"Error initializing ChromaDB: {e}")
    
    return client.get_collection(name=COLLECTION_NAME)

# Initialize or load the ChromaDB collection
chroma_collection = initialize_chroma_db(df_contextual, embedder, client)

# --- 4. RAG Chatbot Function (Improved Filtering, Fallback, and Generation) ---

def rag_chatbot_response(user_query: str, target_npc: str, conversation_history: list, chroma_collection, embedder, generator) -> str:
    """Generates a conversational response for a target NPC using RAG."""
    
    # 1. Embed the user query
    user_query_embedding = embedder.encode([user_query]).tolist()
    
    # 2. Retrieve top K similar dialogue entries from ChromaDB
    # Retrieve more results to increase the chance of finding the target NPC
    retrieved_results = chroma_collection.query(
        query_embeddings=user_query_embedding,
        n_results=15, 
        include=['metadatas', 'documents'] 
    )

    # 3. Filter retrieved results for the target NPC
    filtered_results = []
    for i in range(len(retrieved_results['documents'][0])):
        metadata = retrieved_results['metadatas'][0][i]
        
        # Accessing the metadata using the known lowercase key (The Fix)
        if metadata.get('response_speaker', '').lower() == target_npc.lower(): 
            filtered_results.append({
                'query_text': retrieved_results['documents'][0][i],
                'response_text': metadata.get('response_text'),
                'context': metadata.get('location', '') + " | " + metadata.get('context_action', ''),
                'response_speaker': metadata.get('response_speaker')
            })
            if len(filtered_results) >= 4: # Get up to 4 relevant matches now
                break
    
    # --- FALLBACK GENERATION (The key to fixing the repetition) ---
    if not filtered_results:
        # Use the CHARACTER_PROFILES for a non-retrieval-based, but character-consistent, response
        profile = CHARACTER_PROFILES.get(target_npc.lower(), "a normal person")
        
        fallback_prompt = (
            f"Act as {target_npc}, a character who is {profile}. "
            f"You have been asked the question: '{user_query}'. "
            f"Generate a short, concise, and characteristic response. "
            f"{target_npc}:"
        )
        # Generate with a slightly higher temperature for more character flavor
        fallback_output = generator(
            fallback_prompt, 
            num_return_sequences=1, 
            do_sample=True, 
            temperature=0.8,
            top_k=50, top_p=0.95,
            pad_token_id=generator.tokenizer.eos_token_id, 
            max_new_tokens=30 # Keep it short to avoid excessive gibberish
        )[0]['generated_text']

        # Extracting the response
        if f"{target_npc}:" in fallback_output:
            response = fallback_output.split(f"{target_npc}:")[-1].strip()
            
            # Clean up and ensure a sentence end
            sentence_endings = ['.', '?', '!', '\n']
            for ending in sentence_endings:
                if ending in response:
                    response = response.split(ending)[0] + ending
                    break
            # If still no sentence end, use a generic clean-up
            if not any(e in response for e in ['.', '?', '!']):
                response = response.split('\n')[0].strip() + "."
                
            return response.replace(f"{target_npc}:", "").strip()
        
        return "I'm focusing on the mission right now. Come back later."


    # 4. Construct the RAG prompt 
    prompt = ""
    for entry in conversation_history[-2:]: 
        prompt += f"{entry['speaker']}: {entry['text']}\n"
    
    prompt += f"User: {user_query}\n"
    prompt += f"Context for {target_npc}'s response (based on past dialogue):\n"
    for i, res in enumerate(filtered_results):
        prompt += f"  - Similar past interaction (query): '{res['query_text']}'\n"
        prompt += f"  - {target_npc}'s past response: '{res['response_text']}'\n"
    
    prompt += f"\n{target_npc}:" 
    
    # 5. Generate the RAG-based response
    # Using top_k and top_p for better coherence
    generated_output = generator(
        prompt, 
        num_return_sequences=1, 
        do_sample=True, 
        temperature=0.7,
        top_k=50, top_p=0.95,
        pad_token_id=generator.tokenizer.eos_token_id, 
        max_new_tokens=60 
    )[0]['generated_text']

    # 6. Extract only the NPC's actual response
    if f"\n{target_npc}:" in generated_output:
        response_text = generated_output.split(f"\n{target_npc}:")[-1].strip()
        
        # Clean up and ensure a sentence end
        sentence_endings = ['.', '?', '!', '\n']
        for ending in sentence_endings:
            if ending in response_text:
                response_text = response_text.split(ending)[0] + ending
                break
        
        return response_text
    else:
        return "I'm trying to figure out what you mean. Ask me something more specific."


# --- 5. Interactive Chat Loop (Example) ---

if __name__ == "__main__":
    print("\n--- FF7 RAG Chatbot Initialized (Fixes Applied) ---")
    print("Available NPCs: Cloud, Tifa, Barret, Aerith, Red XIII, Cid, Yuffie, Vincent, Cait Sith (case-insensitive)")
    print("Type 'exit' to quit. Type 'switch NPC_NAME' to change who you're talking to.")

    current_npc = "Cloud" # Default NPC
    conversation_history = [] 

    while True:
        try:
            user_input = input(f"\nYou ({current_npc}): ")
            if user_input.lower() == 'exit':
                break
            
            if user_input.lower().startswith('switch '):
                new_npc = user_input.split(' ', 1)[1].strip()
                # Simple check if the NPC exists in our Response_Speaker list
                if new_npc.lower() in df_contextual['Response_Speaker'].str.lower().unique():
                    current_npc = new_npc
                    conversation_history = [] 
                    print(f"--- Now chatting with {current_npc}. ---")
                elif new_npc.lower() in CHARACTER_PROFILES:
                    current_npc = new_npc.capitalize()
                    conversation_history = [] 
                    print(f"--- Now chatting with {current_npc}. ---")
                else:
                    print(f"NPC '{new_npc}' not found in the script. Please try a core character like Cloud or Tifa.")
                continue
            
            # Add user's input to history
            conversation_history.append({"speaker": "User", "text": user_input})

            # Generate NPC response
            npc_response = rag_chatbot_response(user_input, current_npc, conversation_history, chroma_collection, embedder, generator)
            print(f"{current_npc}: {npc_response}")
            
            # Add NPC's response to history
            conversation_history.append({"speaker": current_npc, "text": npc_response})
            
            # Keep history to a manageable size (e.g., last 4 turns)
            if len(conversation_history) > 4:
                conversation_history = conversation_history[-4:]
                
        except Exception as e:
            print(f"\n[ERROR] An unexpected error occurred: {e}. Resetting chat history.")
            conversation_history = []
            continue