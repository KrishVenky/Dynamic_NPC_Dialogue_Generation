"""
Gemini Agent
Uses Google's Gemini API for dialogue generation
"""

import google.generativeai as genai
from typing import Dict, Optional
from agents.base_agent import BaseDialogueAgent
from nick_personality import generate_system_prompt, generate_context_prompt
from dialogue_processor import DialogueProcessor


class GeminiAgent(BaseDialogueAgent):
    """Gemini-powered dialogue agent"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash-latest"):
        super().__init__("Gemini Agent", model_name)
        self.api_key = api_key
        self.model = None
        self.dialogue_processor = DialogueProcessor("data/nick_valentine_dialogue.csv")
        
    def initialize(self):
        """Initialize Gemini model"""
        try:
            genai.configure(api_key=self.api_key)
            
            # Force use experimental model - more lenient with safety
            model_to_use = "gemini-2.0-flash-exp"
            print(f"🔧 Forcing experimental model (less strict): {model_to_use}")
            
            self.model = genai.GenerativeModel(
                model_name=model_to_use,
                generation_config={
                    'temperature': 0.9,
                    'top_k': 40,
                    'top_p': 0.95,
                    'max_output_tokens': 150,
                }
            )
            
            print(f"✓ {self.name} initialized successfully")
            print(f"✓ Dialogue stats: {self.dialogue_processor.get_stats()}")
            
        except Exception as e:
            print(f"Error initializing Gemini agent: {e}")
            raise
    
    def build_prompt(
        self, 
        user_input: str, 
        context: str, 
        emotion: Optional[str], 
        include_examples: bool
    ) -> str:
        """Absolute simplest prompt possible"""
        
        # Just the bare minimum - no character, no examples, nothing
        return f"Respond to this greeting: {user_input}"
    
    def generate_response(
        self, 
        user_input: str, 
        context: str = "casual",
        emotion: Optional[str] = None,
        include_examples: bool = True
    ) -> Dict:
        """Generate response using Gemini"""
        if not self.model:
            raise Exception("Agent not initialized. Call initialize() first.")
        
        try:
            prompt = self.build_prompt(user_input, context, emotion, include_examples)
            
            # Generate response - let Gemini use default safety settings
            response = self.model.generate_content(prompt)
            
            # Handle blocked responses gracefully
            if not response.candidates:
                print(f"⚠️ No response candidates returned. Using fallback.")
                raise Exception("No response candidates")
            
            candidate = response.candidates[0]
            
            # Check finish reason - 1 = STOP (success), 2 = SAFETY, 3 = RECITATION, etc.
            if candidate.finish_reason != 1:
                print(f"⚠️ Blocked (reason: {candidate.finish_reason}). Using CSV fallback directly.")
                raise Exception(f"Response blocked: finish_reason={candidate.finish_reason}")
            
            nick_response = response.text.strip()
            
            # Clean up response
            nick_response = (
                nick_response
                .strip('"\'')
                .replace('Nick:', '')
                .replace('Nick Valentine:', '')
                .strip()
            )
            
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
            print(f"   Error type: {type(e).__name__}")
            
            # Print full error details for debugging
            import traceback
            traceback.print_exc()
            
            # Fallback to random dialogue
            fallback = self.dialogue_processor.get_random_examples(1)
            fallback_text = fallback[0].get('RESPONSE TEXT', "Something's not right here...") if fallback else "Something's not right here..."
            
            return {
                'response': fallback_text,
                'error': str(e),
                'fallback': True,
                'agent': self.name,
            }
