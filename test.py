import json
import pandas as pd
import os
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer
from transformers import pipeline, set_seed
from dotenv import load_dotenv
from huggingface_hub import login

# ======================================================
# 0. Environment & Model Setup
# ======================================================

load_dotenv()
hf_token = os.getenv("HUGGINGFACE_TOKEN")

os.environ["HF_TOKEN"] = hf_token or ""
try:
    if hf_token:
        login(token=hf_token, add_to_git_credential=False)
except Exception:
    pass

# Lightweight models that work on CPU / 8GB RAM
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
GENERATION_MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

CHROMA_DB_PATH = "./chroma_db_ff7"
COLLECTION_NAME = "ff7_dialogue_rag"

CHARACTER_PROFILES = {
    "cloud": "a cold, stoic ex-SOLDIER who hides his emotions behind short, blunt replies.",
    "tifa": "a kind, warm-hearted woman who worries for others and tries to keep peace.",
    "barret": "a loud, passionate man with a strong sense of justice and anger toward Shinra.",
    "aerith": "a cheerful, mysterious girl who hides deep wisdom behind her playfulness.",
    "red xiii": "an intelligent, noble creature who speaks formally about destiny and nature.",
    "cid": "a gruff, foul-mouthed pilot who dreams of going to space and gets frustrated easily.",
    "yuffie": "an energetic, mischievous materia hunter who jokes around constantly.",
    "vincent": "a quiet, brooding man haunted by his past, speaking in calm, distant tones.",
    "cait sith": "a playful, talkative cat robot who likes to lighten the mood with humor."
}

# ======================================================
# 1. Preprocessing (merged from preprocessing.py)
# ======================================================

def preprocess_data(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    script = data['text']
    processed_data = []

    CONTEXT_KEYS = ['LOCATION', 'ACTION', 'CHOICE']

    for entry in script:
        if not entry:
            continue

        key = list(entry.keys())[0]
        value = entry[key]

        if key in CONTEXT_KEYS:
            processed_data.append({
                'Type': key,
                'Content': value,
                'Speaker': None,
                'Dialogue': None
            })
        else:
            processed_data.append({
                'Type': 'DIALOGUE',
                'Content': None,
                'Speaker': key,
                'Dialogue': value
            })

    df_processed = pd.DataFrame(processed_data)

    # Build contextual pairs
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
        else:
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

    return pd.DataFrame(dialogue_pairs)

# ======================================================
# 2. ChromaDB Setup
# ======================================================

def initialize_chroma_db(df, embedder, client):
    df_meta = df.rename(columns={
        'Location': 'location',
        'Context_Action': 'context_action',
        'Query_Speaker': 'query_speaker',
        'Query_Text': 'query_text',
        'Response_Speaker': 'response_speaker',
        'Response_Text': 'response_text'
    })

    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    if collection.count() == 0 or collection.count() != len(df):
        print("Building new ChromaDB embeddings...")
        query_embeddings = embedder.encode(df_meta['query_text'].tolist(), show_progress_bar=True)
        metadatas = df_meta.to_dict(orient='records')
        ids = [f"pair_{i}" for i in range(len(df_meta))]

        collection.add(
            embeddings=query_embeddings.tolist(),
            documents=df_meta['query_text'].tolist(),
            metadatas=metadatas,
            ids=ids
        )
        print("ChromaDB initialized with dialogue memory.")
    else:
        print("Using existing ChromaDB collection.")

    return collection

# ======================================================
# 3. Emotion & Persona Aware RAG Response
# ======================================================

def detect_mood(text):
    if "!" in text:
        return "excited or emotional"
    elif "?" in text:
        return "curious or uncertain"
    elif any(word in text.lower() for word in ["why", "how", "what"]):
        return "thoughtful or questioning"
    else:
        return "neutral"

def rag_chatbot_response(user_query, target_npc, conversation_history, chroma_collection, embedder, generator):
    mood = detect_mood(user_query)
    user_query_embedding = embedder.encode([user_query]).tolist()

    retrieved = chroma_collection.query(
        query_embeddings=user_query_embedding,
        n_results=10,
        include=['metadatas', 'documents']
    )

    filtered_results = []
    for i in range(len(retrieved['documents'][0])):
        meta = retrieved['metadatas'][0][i]
        if meta.get('response_speaker', '').lower() == target_npc.lower():
            filtered_results.append(meta)
            if len(filtered_results) >= 4:
                break

    # Construct scene context
    context = ""
    if filtered_results:
        context = " | ".join(
            [f"{r.get('location', '')}: {r.get('context_action', '')}" for r in filtered_results if r.get('location')]
        )

    persona_prompt = (
        f"You are {target_npc}, {CHARACTER_PROFILES.get(target_npc.lower(), 'a person')}.\n"
        f"Scene context: {context or 'unknown setting'}.\n"
        f"Current mood: {mood}.\n"
        f"Stay in character and speak naturally, as if this is a real conversation.\n"
        f"Respond with emotional tone, matching your personality.\n\n"
        f"User: {user_query}\n"
        f"{target_npc}:"
    )

    response = generator(
        persona_prompt,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.9,
        top_p=0.9,
        max_new_tokens=80,
        pad_token_id=generator.tokenizer.eos_token_id
    )[0]['generated_text']

    # Extract clean response
    if f"{target_npc}:" in response:
        response = response.split(f"{target_npc}:")[-1].strip()

    response = response.split("\n")[0].strip()
    if not response.endswith((".", "?", "!")):
        response += "."

    return response

# ======================================================
# 4. Main Chat Loop
# ======================================================

if __name__ == "__main__":
    print("\n=== FF7 Interactive RAG Chatbot (Persona Mode) ===")
    print("Loading models...")

    embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
    generator = pipeline("text-generation", model=GENERATION_MODEL_NAME, max_new_tokens=80, truncation=True)
    set_seed(42)

    print("Models loaded successfully.")

    df = preprocess_data("data.json")
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    chroma_collection = initialize_chroma_db(df, embedder, client)

    print("\nAvailable NPCs: Cloud, Tifa, Barret, Aerith, Red XIII, Cid, Yuffie, Vincent, Cait Sith")
    print("Type 'switch [name]' to change NPC, or 'exit' to quit.\n")

    current_npc = "Cloud"
    conversation_history = []

    while True:
        user_input = input(f"\nYou ({current_npc}): ").strip()
        if user_input.lower() == "exit":
            break

        if user_input.lower().startswith("switch "):
            new_npc = user_input.split(" ", 1)[1].strip().lower()
            if new_npc in CHARACTER_PROFILES:
                current_npc = new_npc.capitalize()
                print(f"--- Now speaking with {current_npc} ---")
                continue
            else:
                print("That NPC isn't available.")
                continue

        conversation_history.append({"speaker": "User", "text": user_input})
        npc_response = rag_chatbot_response(user_input, current_npc, conversation_history, chroma_collection, embedder, generator)
        print(f"{current_npc}: {npc_response}")
        conversation_history.append({"speaker": current_npc, "text": npc_response})

        if len(conversation_history) > 6:
            conversation_history = conversation_history[-6:]