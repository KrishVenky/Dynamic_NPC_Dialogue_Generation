import os
"""Simple test/demo that exercises the new DialogueEngine.

This script indexes the dialogue pairs (if not already indexed), runs a short query against a
selected NPC, shows retrieved memories and either generates a reply (if a generator backend is
available) or prints the assembled prompt for inspection.
"""

from dialogue_engine import DialogueEngine

def main():
    print("Starting demo...")
    engine = DialogueEngine()
    df = engine.preprocess_data('data.json')

    print("Indexing dataset into Chroma (if needed)...")
    try:
        engine.index_dialogue_pairs(df)
        print("Indexing complete or collection already present.")
    except Exception as e:
        print('Indexing skipped or failed:', e)

    conversation_history = []

    # Demo: ask Barret about Shinra
    user_query = "Why is Shinra hurting the planet?"
    target_npc = 'Barrett'

    print(f"\nQuerying memories for '{target_npc}'...\n")
    memories = engine.retrieve_memories(user_query, target_npc=target_npc, n_results=4)
    for i, m in enumerate(memories):
        print(f"Memory {i+1}: speaker={m['metadata'].get('speaker')} score={m['score']:.3f}\n  doc={m['document'][:200]}")

    prompt = engine.assemble_prompt(target_npc, user_query, conversation_history, memories)

    print('\nAssembled prompt (truncated):')
    print(prompt[:1000])

    # Attempt local free generation by default (small HF model). If it fails, show guidance.
    print('\nAttempting local generation (free HF model)...')
    try:
        reply = engine.generate(prompt)
        print(f"\n{target_npc}: {reply}")
        # store memory of conversation
        engine.write_memory('User', user_query, importance=0.6)
        engine.write_memory(target_npc, reply, importance=0.7)
    except Exception as e:
        print('Local generation failed or not available:', e)
        print('\nIf you want to try a different local model (still free), set:')
        print('  export LOCAL_GEN_MODEL="gpt2-medium"')
        print('\nOr use the Hugging Face Inference API (free tier) to avoid local downloads — you can plug it in later.')
        print('\nLocal generation may download models on first run and can be slow or memory heavy on macOS.')

if __name__ == '__main__':
    main()