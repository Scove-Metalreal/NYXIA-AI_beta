"""
Reasoning Layer - Context Builder & Decision Engine
"""

import difflib
from typing import List, Dict, Any, Optional
from loguru import logger
from layers.reasoning.nlu import NLUAnalyzer


class ContextBuilder:
    """Builds the context for the LLM."""
    
    def __init__(self):
        pass
    
    def build_llm_context(
        self,
        personality_prompt: str,
        user_input: str,
        short_term_history: List[Dict[str, str]],
        retrieved_memories: List[str],
        emotional_state: Dict[str, float],
        response_tone: str
    ) -> List[Dict[str, str]]:
        """Builds the full context for the LLM."""
        messages = []
        
        system_content = personality_prompt
        system_content += f"\n\nYour current emotional state:"
        system_content += f"\n- Mood: {emotional_state.get('mood', 70):.0f}/100"
        system_content += f"\n- Energy: {emotional_state.get('energy', 80):.0f}/100"
        system_content += f"\n- Affection: {emotional_state.get('affection', 50):.0f}/100"
        
        if retrieved_memories:
            system_content += "\n\nRelevant information from your memory:"
            for i, memory in enumerate(retrieved_memories, 1):
                system_content += f"\n{i}. {memory}"
        
        system_content += f"\n\nPlease respond with a {response_tone} tone."
        
        messages.append({"role": "system", "content": system_content})
        messages.extend(short_term_history)
        messages.append({"role": "user", "content": user_input})
        
        logger.debug(f"Built context with {len(messages)} messages")
        return messages


class DecisionEngine:
    """Makes decisions about the AI's behavior."""
    
    def __init__(self):
        self.nlu_analyzer = NLUAnalyzer()
    
    def analyze_user_emotion(self, user_input: str) -> Dict[str, Any]:
        """Analyzes the user's emotion using the NLUAnalyzer."""
        return self.nlu_analyzer.analyze_text(user_input)


class BehaviorRules:
    """Enforces behavior rules."""
    
    def __init__(self):
        self.recent_responses = []
        self.max_history = 5
    
    def validate_response(self, response: str) -> tuple:
        """Validates the response against a set of rules."""
        if len(response.strip()) < 5:
            return False, "Response too short"
        
        if len(response) > 2000: # Increased max length slightly
            return False, "Response too long"
        
        # Use similarity check instead of exact match for repetition
        for old_response in self.recent_responses:
            similarity = difflib.SequenceMatcher(None, response, old_response).ratio()
            if similarity > 0.9:
                return False, f"Repetitive response (similarity: {similarity:.2f})"
        
        return True, None
    
    def track_response(self, response: str):
        """Tracks the response to prevent repetition."""
        self.recent_responses.append(response)
        if len(self.recent_responses) > self.max_history:
            self.recent_responses.pop(0)
