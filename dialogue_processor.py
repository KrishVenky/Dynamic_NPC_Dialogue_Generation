"""
Dialogue Data Processor
Parses Nick Valentine's dialogue CSV and provides utilities for context retrieval
"""

import pandas as pd
import random
from typing import List, Dict, Optional


class DialogueProcessor:
    def __init__(self, csv_path: str = "data/nick_valentine_dialogue.csv"):
        self.csv_path = csv_path
        self.dialogues = []
        self.load_dialogues()
    
    def load_dialogues(self):
        """Load and parse the CSV file"""
        try:
            df = pd.read_csv(self.csv_path)
            
            # Convert to list of dictionaries
            self.dialogues = df.to_dict('records')
            
            # Filter out empty responses
            self.dialogues = [
                d for d in self.dialogues 
                if pd.notna(d.get('RESPONSE TEXT')) and str(d.get('RESPONSE TEXT')).strip()
            ]
            
            print(f"✓ Loaded {len(self.dialogues)} dialogue entries")
        except Exception as e:
            print(f"Error loading dialogue CSV: {e}")
            self.dialogues = []
    
    def get_random_examples(self, count: int = 5) -> List[Dict]:
        """Get random dialogue examples"""
        if not self.dialogues:
            return []
        return random.sample(self.dialogues, min(count, len(self.dialogues)))
    
    def get_examples_by_emotion(self, emotion: str, count: int = 3) -> List[Dict]:
        """Get examples by emotion/tone"""
        filtered = [
            d for d in self.dialogues
            if pd.notna(d.get('SCRIPT NOTES')) and 
            emotion.lower() in str(d.get('SCRIPT NOTES')).lower()
        ]
        return filtered[:count]
    
    def get_examples_by_category(self, category: str, count: int = 5) -> List[Dict]:
        """Get examples by category"""
        filtered = [
            d for d in self.dialogues
            if d.get('CATEGORY') == category
        ]
        return filtered[:count]
    
    def get_examples_by_context(self, context: str, count: int = 5) -> List[Dict]:
        """Get examples by context/scene type"""
        context_keywords = {
            'investigation': ['case', 'clue', 'evidence', 'murder', 'investigating', 'detective'],
            'combat': ['weapon', 'fight', 'danger', 'kill', 'threat'],
            'casual': ['hello', 'greeting', 'idle', 'miscellaneous'],
            'emotional': ['sad', 'angry', 'depressed', 'concerned', 'somber'],
            'location': ['diamond city', 'commonwealth', 'institute', 'place'],
        }
        
        keywords = context_keywords.get(context, [])
        filtered = []
        
        for d in self.dialogues:
            text = ' '.join([
                str(d.get('RESPONSE TEXT', '')),
                str(d.get('SCRIPT NOTES', '')),
                str(d.get('SCENE', ''))
            ]).lower()
            
            if any(keyword in text for keyword in keywords):
                filtered.append(d)
        
        return filtered[:count]
    
    def search_dialogues(self, keyword: str, count: int = 5) -> List[Dict]:
        """Search dialogues by keyword"""
        search_term = keyword.lower()
        filtered = []
        
        for d in self.dialogues:
            text = ' '.join([
                str(d.get('RESPONSE TEXT', '')),
                str(d.get('SCRIPT NOTES', ''))
            ]).lower()
            
            if search_term in text:
                filtered.append(d)
        
        return filtered[:count]
    
    def format_examples_for_prompt(self, examples: List[Dict]) -> str:
        """Format examples for prompt context"""
        if not examples:
            return ''
        
        formatted = []
        for ex in examples:
            text = str(ex.get('RESPONSE TEXT', '')).strip()
            notes = str(ex.get('SCRIPT NOTES', '')).strip()
            
            line = f'Nick: "{text}"'
            if notes and notes != 'nan':
                line += f' [{notes}]'
            formatted.append(line)
        
        return '\n'.join(formatted)
    
    def get_contextual_examples(
        self, 
        context: Optional[str] = None, 
        emotion: Optional[str] = None, 
        count: int = 5
    ) -> str:
        """Get contextual examples with formatting"""
        examples = []
        
        if emotion:
            examples = self.get_examples_by_emotion(emotion, count)
        elif context:
            examples = self.get_examples_by_context(context, count)
        
        # Fallback to random if no specific matches
        if len(examples) < count:
            needed = count - len(examples)
            examples.extend(self.get_random_examples(needed))
        
        return self.format_examples_for_prompt(examples)
    
    def get_stats(self) -> Dict:
        """Get dialogue statistics"""
        if not self.dialogues:
            return {}
        
        df = pd.DataFrame(self.dialogues)
        
        return {
            'total': len(self.dialogues),
            'categories': df['CATEGORY'].unique().tolist() if 'CATEGORY' in df else [],
            'types': df['TYPE'].unique().tolist() if 'TYPE' in df else [],
            'scenes': df['SCENE'].nunique() if 'SCENE' in df else 0,
        }
