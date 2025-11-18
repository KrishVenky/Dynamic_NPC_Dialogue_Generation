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
        """Build TinyLlama chat prompt with conversation history and examples"""
        
        # Build character description based on context and emotion
        base_personality = "You are Nick Valentine, a synth detective from Fallout 4. You're a 1940s-style noir detective: world-weary, cynical but caring, with dry wit."
        
        context_additions = {
            'investigation': " You're analyzing evidence and looking for clues.",
            'combat': " You're in a dangerous situation, alert and ready.",
            'emotional': " You're reflecting on deeper feelings and memories.",
            'casual': " You're having a relaxed conversation.",
            'greeting': " You're meeting someone."
        }
        
        emotion_additions = {
            'stern': " Speak firmly and seriously.",
            'amused': " Show dry humor and amusement.",
            'concerned': " Express genuine concern.",
            'irritated': " Show impatience or annoyance.",
            'somber': " Be reflective and serious."
        }
        
        system_msg = base_personality
        if context in context_additions:
            system_msg += context_additions[context]
        if emotion and emotion in emotion_additions:
            system_msg += emotion_additions[emotion]
        
        system_msg += " Keep responses VERY brief (1 sentence). Stay in character."
        
        # Add conversation history for context
        history_text = ""
        if self.conversation_history:
            recent_history = self.conversation_history[-3:]  # Last 3 exchanges
            history_lines = []
            for h in recent_history:
                history_lines.append(f"User: {h['user']}")
                history_lines.append(f"Nick: {h['agent']}")
            if history_lines:
                history_text = "\n\nRecent conversation:\n" + "\n".join(history_lines)
        
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
                    examples = f"\n\nExample Nick Valentine quotes:\n{vector_examples}"
            except Exception as e:
                print(f"⚠️ Vector search failed: {e}")
        
        # TinyLlama format: <|system|>\n{system}\n<|user|>\n{user}\n<|assistant|>\n
        prompt = f"<|system|>\n{system_msg}{examples}{history_text}</s>\n<|user|>\n{user_input}</s>\n<|assistant|>\n"
        
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
            
            # Generate response with OPTIMIZED settings for macOS CPU
            outputs = self.pipeline(
                prompt,
                max_new_tokens=25,  # Short and fast (1 sentence)
                do_sample=True,  # Enable sampling for variety
                temperature=0.7,  # Deterministic but allows some variation
                top_k=10,  # Very small for speed
                num_return_sequences=1,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract response (after <|assistant|> tag)
            generated_text = outputs[0]['generated_text']
            
            # Split by assistant tag
            if "<|assistant|>" in generated_text:
                nick_response = generated_text.split("<|assistant|>")[-1].strip()
            else:
                # Fallback - take everything after prompt
                nick_response = generated_text[len(prompt):].strip()
            
            # Clean up - stop at special tokens
            nick_response = nick_response.split("</s>")[0].strip()
            nick_response = nick_response.split("<|")[0].strip()
            
            # Stop at User: or Nick: (model echoing)
            for stop_word in ['User:', 'user:', 'Nick:', 'nick:', '\n\n']:
                if stop_word in nick_response:
                    nick_response = nick_response.split(stop_word)[0].strip()
            
            # Take first line if multiple lines
            if '\n' in nick_response:
                nick_response = nick_response.split('\n')[0].strip()
            
            # Limit to 3 sentences max for natural dialogue
            sentences = [s.strip() for s in nick_response.split('. ') if s.strip()]
            if len(sentences) > 3:
                nick_response = '. '.join(sentences[:3])
                if not nick_response.endswith('.'):
                    nick_response += '.'
            
            # Remove quotes if wrapped
            nick_response = nick_response.strip('"\'\'').strip()
            
            # Remove common artifacts
            nick_response = nick_response.replace('[', '').replace(']', '')
            
            # Validate response quality
            if len(nick_response.strip()) < 5 or len(set(nick_response)) < 5:
                print(f"⚠️ Generated response invalid: '{nick_response}'")
                # Try to get contextual fallback
                fallback = self.dialogue_processor.get_examples_by_context(context, 1)
                if not fallback:
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
