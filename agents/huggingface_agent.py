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
            
            # Create text generation pipeline optimized for speed
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                batch_size=1  # Single generation for faster response
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
        """Build context-aware prompt with personality"""
        
        # Base personality
        personality = "You are Nick Valentine, a synth private detective from Fallout 4. You're a 1940s noir detective with a dry wit and world-weary attitude."
        
        # Context-specific behavior
        context_map = {
            'investigation': " You're analyzing clues and evidence.",
            'combat': " You're in danger, staying alert.",
            'emotional': " You're reflecting on deeper feelings.",
            'casual': " You're having a casual chat.",
            'greeting': " You're meeting someone."
        }
        
        # Emotion-specific tone
        emotion_map = {
            'stern': " Be firm and serious.",
            'amused': " Show dry humor.",
            'concerned': " Express concern.",
            'irritated': " Show impatience.",
            'somber': " Be reflective."
        }
        
        # Build system message
        system = personality
        if context in context_map:
            system += context_map[context]
        if emotion and emotion in emotion_map:
            system += emotion_map[emotion]
        system += " Respond with ONE natural sentence."
        
        # Add examples if requested and available
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
                pass
        
        prompt = f"<|system|>\n{system}{examples}</s>\n<|user|>\n{user_input}</s>\n<|assistant|>\n"
        
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
            
            # Generate response with balanced quality/speed
            outputs = self.pipeline(
                prompt,
                max_new_tokens=50,
                do_sample=True,
                temperature=0.85,
                top_k=40,
                top_p=0.92,
                num_return_sequences=1,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.15
            )
            
            # Extract response (after <|assistant|> tag)
            generated_text = outputs[0]['generated_text']
            
            if "<|assistant|>" in generated_text:
                nick_response = generated_text.split("<|assistant|>")[-1].strip()
            else:
                nick_response = generated_text[len(prompt):].strip()
            
            # Remove special tokens
            nick_response = nick_response.split("</s>")[0].strip()
            nick_response = nick_response.split("<|")[0].strip()
            
            # Remove meta-text that indicates model confusion
            meta_patterns = [
                'Context:', 'Emotion:', 'Recent conversation:', 
                'Sure,', 'Certainly', "Here's", 'edited version', 
                'longer response', 'Example responses:'
            ]
            for pattern in meta_patterns:
                if pattern in nick_response:
                    nick_response = nick_response.split(pattern)[0].strip()
            
            # Stop at dialogue markers
            for marker in ['User:', 'user:', 'Nick:', 'nick:']:
                if marker in nick_response:
                    nick_response = nick_response.split(marker)[0].strip()
            
            # Clean newlines
            nick_response = nick_response.replace('\n\n', ' ').replace('\n', ' ').strip()
            
            # Limit to 2 sentences max
            sentences = [s.strip() for s in nick_response.split('. ') if s.strip()]
            if len(sentences) > 2:
                nick_response = '. '.join(sentences[:2])
                if not nick_response.endswith('.'):
                    nick_response += '.'
            elif sentences and not nick_response.endswith('.') and not nick_response.endswith('?') and not nick_response.endswith('!'):
                nick_response += '.'
            
            # Remove quotes and brackets
            nick_response = nick_response.strip('"\'\'[]()').strip()
            
            # Validate response quality
            if len(nick_response.strip()) < 5 or not any(c.isalpha() for c in nick_response):
                print(f"⚠️ Generated response invalid: '{nick_response}'")
                # Context-aware fallback
                fallbacks = {
                    'investigation': "Let me think about this.",
                    'combat': "Stay sharp.",
                    'emotional': "It's complicated.",
                    'greeting': "Hello there.",
                    'casual': "What do you need?"
                }
                nick_response = fallbacks.get(context, "What can I do for you?")
            
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
