"""
HuggingFace Agent for dialogue generation with vector DB integration
"""
import os
from typing import Dict, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from agents.base_agent import BaseDialogueAgent
from dialogue_processor import DialogueProcessor


class HuggingFaceAgent(BaseDialogueAgent):
    """HuggingFace-based dialogue agent using transformer models + vector search"""
    
    def __init__(self, csv_path: str, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        """
        Initialize HuggingFace agent
        
        Args:
            csv_path: Path to dialogue CSV
            model_name: HuggingFace model ID
        """
        super().__init__("HuggingFace", csv_path)
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.conversation_history = []
        self.max_history = 5
        self.vector_store = None
        self.dialogue_processor = DialogueProcessor(csv_path)  # Add this!
    
    def initialize(self) -> bool:
        """Initialize the HuggingFace model"""
        try:
            # Check for HF token
            hf_token = os.environ.get('HF_TOKEN')
            if not hf_token:
                print("⚠️ Warning: HF_TOKEN not found in environment")
            
            print(f"🔄 Loading HuggingFace model: {self.model_name}")
            print(f"   Using device: {self.device}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                token=hf_token,
                padding_side='left'
            )
            
            # Set pad token if not exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                token=hf_token,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            
            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )
            
            print(f"✅ HuggingFace agent initialized: {self.model_name}")
            
            # Try to load vector store
            try:
                from vector_store import get_vector_store
                csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'nick_valentine_dialogue.csv')
                self.vector_store = get_vector_store(csv_path)
                print(f"✅ Vector store loaded for HuggingFace agent")
            except Exception as e:
                print(f"⚠️ Vector store not available: {e}")
                self.vector_store = None
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing HuggingFace agent: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def build_prompt(
        self,
        user_input: str,
        context: str,
        emotion: Optional[str],
        include_examples: bool
    ) -> str:
        """Build TinyLlama chat prompt with vector examples"""
        
        # TinyLlama chat format
        system_msg = "You are Nick Valentine, a 1940s detective from Fallout 4. You're professional, observant, and have a dry wit. Keep responses brief (1-2 sentences)."
        
        # Add vector examples if available
        examples = ""
        if include_examples and self.vector_store:
            try:
                vector_examples = self.vector_store.get_contextual_examples(
                    user_input=user_input,
                    context=context,
                    emotion=emotion,
                    n_results=2
                )
                if vector_examples:
                    examples = f"\n\nExample responses:\n{vector_examples}"
            except Exception as e:
                print(f"⚠️ Vector search failed: {e}")
        
        # TinyLlama format: <|system|>\n{system}\n<|user|>\n{user}\n<|assistant|>\n
        prompt = f"<|system|>\n{system_msg}{examples}</s>\n<|user|>\n{user_input}</s>\n<|assistant|>\n"
        
        return prompt
    
    def generate_response(
        self,
        user_input: str,
        context: str = "casual",
        emotion: Optional[str] = None,
        include_examples: bool = True
    ) -> Dict:
        """Generate response using HuggingFace model"""
        
        if not self.model or not self.pipeline:
            raise Exception("Agent not initialized. Call initialize() first.")
        
        try:
            # Build prompt
            prompt = self.build_prompt(user_input, context, emotion, include_examples)
            
            # Generate response with TinyLlama settings
            outputs = self.pipeline(
                prompt,
                max_new_tokens=30,  # Very short - 1-2 sentences max
                do_sample=True,
                temperature=0.9,
                top_p=0.92,
                top_k=35,
                num_return_sequences=1,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.4,
                no_repeat_ngram_size=3
            )
            
            # Extract response (after <|assistant|> tag)
            generated_text = outputs[0]['generated_text']
            
            # Split by assistant tag
            if "<|assistant|>" in generated_text:
                nick_response = generated_text.split("<|assistant|>")[-1].strip()
            else:
                # Fallback - take everything after prompt
                nick_response = generated_text[len(prompt):].strip()
            
            # Clean up - stop at special tokens, newlines, or excessive length
            nick_response = nick_response.split("</s>")[0].strip()
            nick_response = nick_response.split("<|")[0].strip()
            nick_response = nick_response.split("\n")[0].strip()  # First line only
            
            # Take max 2 sentences
            sentences = nick_response.split('. ')
            if len(sentences) > 2:
                nick_response = '. '.join(sentences[:2]) + '.'
            
            # Remove quotes
            nick_response = nick_response.strip('"\'').strip()
            
            # Fallback if response is empty or too short
            if len(nick_response.strip()) < 5:
                print(f"⚠️ Generated response too short: '{nick_response}'")
                fallback = self.dialogue_processor.get_random_examples(1)
                nick_response = fallback[0].get('RESPONSE TEXT', "What can I do for you?") if fallback else "What can I do for you?"
            
            # Add to history
            self.add_to_history(user_input, nick_response, context, emotion)
            
            return {
                'response': nick_response,
                'context': context,
                'emotion': emotion,
                'agent': self.name,
                'model': self.model_name,
            }
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback to CSV
            fallback = self.dialogue_processor.get_random_examples(1)
            fallback_text = fallback[0].get('RESPONSE TEXT', "Something's not right here...") if fallback else "Something's not right here..."
            
            return {
                'response': fallback_text,
                'error': str(e),
                'fallback': True,
                'agent': self.name,
            }
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
    
    def get_info(self) -> Dict:
        """Get agent information"""
        return {
            'name': self.name,
            'model': self.model_name,
            'device': self.device,
            'ready': self.model is not None,
            'type': 'huggingface'
        }
