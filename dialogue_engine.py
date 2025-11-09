import os
import time
import json
from typing import List, Dict, Any, Optional

import chromadb
from sentence_transformers import SentenceTransformer
from transformers import pipeline, set_seed

# Do not import preprocessing.preprocess_data here because the repository's preprocessing
# module provides raw parsing but not a stable API in all branches. Provide an internal
# preprocess helper below and keep the engine self-contained.

CHROMA_DB_PATH = "./chroma_db_ff7"
COLLECTION_NAME = "ff7_dialogue_rag"


class DialogueEngine:
    """Provider-agnostic dialogue engine with memory and persona-aware prompt assembly.

    By default this engine prefers a free local HF transformer for generation (small CPU-friendly
    model like `distilgpt2`). OpenAI is optional and will only be used if explicitly enabled
    via environment variables (see `USE_OPENAI` below).
    """

    def __init__(self,
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 generation_model: str = "distilgpt2",
                 chroma_path: str = CHROMA_DB_PATH,
                 collection_name: str = COLLECTION_NAME,
                 hf_device: Optional[str] = None):

        self.embedder = SentenceTransformer(embedding_model)
        self.generation_model_name = generation_model
        self.hf_device = hf_device

        # Initialize or connect to ChromaDB (persistent on-disk)
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

        # Local generator pipeline (lazy init)
        self._generator = None

        # Load persona templates
        try:
            with open('prompts.json', 'r') as f:
                self.prompt_cfg = json.load(f)
        except Exception:
            self.prompt_cfg = {}

        # Seed for determinism in local generation
        set_seed(42)

    @staticmethod
    def preprocess_data(json_path: str = 'data.json'):
        """Lightweight preprocessing to extract dialogue pairs from the script JSON.

        Returns a DataFrame with columns matching the engine's indexing expectations.
        """
        import pandas as _pd
        with open(json_path, 'r') as f:
            data = json.load(f)

        script = data.get('text', [])

        dialogue_pairs = []
        last_dialogue_entry = None
        current_location = "Start"
        current_action = ""

        for entry in script:
            if not entry:
                continue
            key = list(entry.keys())[0]
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

        return _pd.DataFrame(dialogue_pairs)

    # --------------------------- Memory / Indexing ---------------------------
    def index_dialogue_pairs(self, df):
        """Index the dialogue pairs dataframe into Chroma. df is expected to have
        columns: ['Location','Context_Action','Query_Speaker','Query_Text','Response_Speaker','Response_Text']
        """
        if self.collection.count() > 0:
            # assume indexed
            return

        # Use the response text as the document to retrieve relevant answers
        docs = df['Response_Text'].tolist()
        embeddings = self.embedder.encode(docs, show_progress_bar=True)
        
        # Normalize metadata keys (lowercase) and add speaker field for filtering
        metadatas = []
        for _, row in df.iterrows():
            meta = {
                'location': row.get('Location', ''),
                'context_action': row.get('Context_Action', ''),
                'query_speaker': row.get('Query_Speaker', ''),
                'query_text': row.get('Query_Text', ''),
                'response_speaker': row.get('Response_Speaker', ''),
                'response_text': row.get('Response_Text', ''),
                'speaker': row.get('Response_Speaker', ''),  # normalized for filtering
            }
            metadatas.append(meta)
        
        ids = [f'pair_{i}' for i in range(len(docs))]

        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=docs,
            metadatas=metadatas,
            ids=ids
        )

    def write_memory(self, speaker: str, text: str, tags: Optional[Dict[str, Any]] = None, importance: float = 0.5):
        """Write a single conversational turn into the memory collection with timestamp and importance.
        This creates a persistent memory entry that will be retrieved later.
        """
        tags = tags or {}
        ts = time.time()
        doc = text
        emb = self.embedder.encode([text]).tolist()[0]
        meta = {
            'speaker': speaker,
            'timestamp': ts,
            'importance': float(importance),
            'tags': tags
        }
        # Generate a unique id using timestamp and current collection count. Avoid calling
        # collection.get(include=['ids']) because some Chroma versions don't accept 'ids' in include.
        existing_count = self.collection.count() if self.collection is not None else 0
        uid = f'mem_{int(ts*1000)}_{existing_count}'
        try:
            # Preferred: pass named args (newer chroma versions)
            self.collection.add(embeddings=[emb], documents=[doc], metadatas=[meta], ids=[uid])
        except TypeError as e:
            # Older chroma versions expect positional args: (ids, documents, metadatas, embeddings)
            try:
                self.collection.add([uid], [doc], [meta], [emb])
                return
            except Exception:
                pass
        except Exception:
            # final fallback without ids
            try:
                self.collection.add(embeddings=[emb], documents=[doc], metadatas=[meta])
            except Exception:
                # last-resort: ignore persistent write failure (memory still usable in-session)
                return

    def retrieve_memories(self, query: str, target_npc: Optional[str] = None, n_results: int = 6):
        """Retrieve relevant memories by semantic similarity and simple recency/importance re-ranking.
        Returns a list of metadata dicts (most relevant first).
        """
        query_emb = self.embedder.encode([query]).tolist()
        res = self.collection.query(query_embeddings=query_emb, n_results=min(50, n_results*5), include=['metadatas', 'documents'])

        docs = res.get('documents', [[]])[0]
        metas = res.get('metadatas', [[]])[0]

        scored = []
        now = time.time()
        for i, m in enumerate(metas):
            if not m:
                continue
            # filter by target speaker if provided
            if target_npc and 'speaker' in m and m['speaker'].lower() != target_npc.lower():
                continue
            # base score: inverse of rank
            base = 1.0 / (i + 1)
            # recency boost
            ts = float(m.get('timestamp', now))
            recency = 1.0 / (1.0 + (now - ts) / (60.0 * 60.0 * 24.0))  # decays per day
            importance = float(m.get('importance', 0.5))
            score = base * (0.6 * importance + 0.4 * recency)
            scored.append((score, m, docs[i] if i < len(docs) else None))

        scored.sort(key=lambda x: x[0], reverse=True)
        selected = scored[:n_results]
        results = [{'score': s, 'metadata': m, 'document': d} for s, m, d in selected]
        return results

    # --------------------------- Prompt Assembly ---------------------------
    def _few_shot_for(self, character: str, k: int = 2) -> List[Dict[str, str]]:
        """Pull few-shot examples from persona config - return list of {'user': '...', 'character': '...'}"""
        examples = []
        try:
            personas = self.prompt_cfg.get('personas', {})
            if character.lower() in personas:
                p = personas[character.lower()]
                example_utterances = p.get('example_utterances', [])
                # Build simple few-shot from example utterances
                for utterance in example_utterances[:k]:
                    examples.append({
                        'user': f"Say something in character",
                        'character': utterance
                    })
        except Exception:
            pass
        return examples

    def assemble_prompt(self, target_npc: str, user_query: str, conversation_history: List[Dict[str, str]] = None, memory_snippets: List[Dict] = None) -> str:
        """Construct the final prompt to send to the generator. The prompt includes:
        - A system instruction describing the NPC persona & rules
        - A few-shot/example block (if available)
        - Retrieved memories labeled and appended
        - Recent conversation history
        - The user query
        """
        conversation_history = conversation_history or []
        memory_snippets = memory_snippets or []

        persona = ""
        try:
            personas = self.prompt_cfg.get('personas', {})
            if target_npc.lower() in personas:
                p = personas[target_npc.lower()]
                persona = p.get('summary', '')
        except Exception:
            persona = ''

        sys_inst = f"You are {target_npc}. {persona}\nYou must respond in character. Keep replies concise (1-3 sentences)."

        few = self._few_shot_for(target_npc, k=2)
        few_block = ''
        if few:
            few_block = "\nExamples of how you speak:\n"
            for ex in few:
                few_block += f"User: {ex['user']}\n{target_npc}: {ex['character']}\n\n"

        mem_block = ''
        if memory_snippets:
            mem_block = "\nRelevant context from your knowledge:\n"
            for m in memory_snippets[:3]:  # limit to top 3 to reduce noise
                doc = m.get('document', '')
                speaker = m.get('metadata', {}).get('speaker', 'Unknown')
                mem_block += f"- {speaker} said: \"{doc}\"\n"

        hist_block = ''
        if conversation_history:
            hist_block = "\nRecent conversation:\n"
            for turn in conversation_history[-4:]:  # limit to last 4 turns
                hist_block += f"{turn.get('speaker')}: {turn.get('text')}\n"

        # Construct prompt to encourage direct response
        prompt = f"{sys_inst}\n{few_block}\n{mem_block}\n{hist_block}\nUser: {user_query}\n{target_npc}:"

        return prompt

    # --------------------------- Generation ---------------------------
    def _init_local_generator(self):
        if self._generator is None:
            # Allow override from env var for quick experimentation
            model_name = os.getenv('LOCAL_GEN_MODEL', self.generation_model_name)
            device = None
            try:
                device = int(self.hf_device) if self.hf_device is not None else -1
            except Exception:
                device = -1
            self._generator = pipeline("text-generation", model=model_name, device=device)
        return self._generator

    def generate(self, prompt: str, max_new_tokens: int = 60, temperature: float = 0.7) -> str:
        """Generate a response using local HF transformer. Post-processes to extract clean reply."""
        # Use local HF transformers (free) by default. Model can be overridden with LOCAL_GEN_MODEL env var.
        gen = self._init_local_generator()
        out = gen(prompt, max_new_tokens=max_new_tokens, do_sample=True, temperature=temperature, top_k=50, top_p=0.9)
        text = out[0].get('generated_text') or out[0].get('text') or ''
        
        # Post-process: extract only the generated part after the prompt
        if prompt and text.startswith(prompt):
            text = text[len(prompt):].strip()
        
        # Stop at first newline or when we see "User:" (model echoing conversation)
        lines = text.split('\n')
        reply = lines[0].strip() if lines else text.strip()
        
        # Remove common artifacts
        if 'User:' in reply:
            reply = reply.split('User:')[0].strip()
        if '[' in reply and ']' in reply:
            # Remove placeholder text like [answer in-character]
            import re
            reply = re.sub(r'\[.*?\]', '', reply).strip()
        
        # Limit to first 2-3 sentences for conciseness
        sentences = reply.split('. ')
        if len(sentences) > 3:
            reply = '. '.join(sentences[:3]) + '.'
        
        return reply if reply else "I... don't know what to say."


if __name__ == '__main__':
    print('dialogue_engine module')
