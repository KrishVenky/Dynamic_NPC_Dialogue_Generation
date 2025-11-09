"""
Comprehensive test of the DialogueEngine with multiple characters and questions.
"""

from dialogue_engine import DialogueEngine

def test_character(engine, character, question):
    """Test a single character with a question."""
    print(f"\n{'='*70}")
    print(f"Character: {character}")
    print(f"Question: {question}")
    print(f"{'='*70}")
    
    # Retrieve memories
    memories = engine.retrieve_memories(question, target_npc=character, n_results=3)
    
    # Assemble prompt
    prompt = engine.assemble_prompt(character, question, conversation_history=[], memory_snippets=memories)
    
    # Generate response
    try:
        reply = engine.generate(prompt, max_new_tokens=50, temperature=0.75)
        print(f"\n{character}: {reply}\n")
        
        # Store memory
        engine.write_memory('User', question, importance=0.6)
        engine.write_memory(character, reply, importance=0.7)
        
        return reply
    except Exception as e:
        print(f"Generation error: {e}")
        return None

def main():
    print("Initializing DialogueEngine with TinyLlama...")
    engine = DialogueEngine()
    
    # Load and index data
    print("Loading data...")
    df = engine.preprocess_data('data.json')
    
    print("Indexing (if needed)...")
    try:
        engine.index_dialogue_pairs(df)
        print("✓ Indexing complete")
    except Exception as e:
        print(f"Indexing error: {e}")
    
    # Test cases
    test_cases = [
        ("Barrett", "Why is Shinra hurting the planet?"),
        ("Barrett", "What do you think of Cloud?"),
        ("Aerith", "What is the Lifestream?"),
        ("Aerith", "Can you tell me about the Ancients?"),
        ("Tifa", "How are you feeling?"),
        ("Tifa", "Do you remember our childhood?"),
        ("Cloud", "What's your mission?"),
        ("Cloud", "Do you trust Sephiroth?"),
    ]
    
    print("\n" + "="*70)
    print("TESTING MULTIPLE CHARACTERS")
    print("="*70)
    
    for character, question in test_cases:
        test_character(engine, character, question)
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)

if __name__ == '__main__':
    main()
