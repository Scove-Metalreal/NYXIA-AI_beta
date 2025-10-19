"""
Reasoning Layer - Context Builder & Decision Engine
"""

from typing import List, Dict, Any, Optional
from loguru import logger


class ContextBuilder:
    """Build context cho LLM"""
    
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
        """Build full context cho LLM"""
        messages = []
        
        system_content = personality_prompt
        system_content += f"\n\nTrạng thái cảm xúc hiện tại của bạn:"
        system_content += f"\n- Mood: {emotional_state.get('mood', 70):.0f}/100"
        system_content += f"\n- Energy: {emotional_state.get('energy', 80):.0f}/100"
        system_content += f"\n- Affection: {emotional_state.get('affection', 50):.0f}/100"
        
        if retrieved_memories:
            system_content += "\n\nThông tin liên quan từ ký ức:"
            for i, memory in enumerate(retrieved_memories, 1):
                system_content += f"\n{i}. {memory}"
        
        system_content += f"\n\nHãy trả lời với tone: {response_tone}"
        
        messages.append({"role": "system", "content": system_content})
        messages.extend(short_term_history)
        messages.append({"role": "user", "content": user_input})
        
        logger.debug(f"Built context with {len(messages)} messages")
        return messages


class DecisionEngine:
    """Ra quyết định về hành vi của AI"""
    
    def __init__(self):
        pass
    
    def analyze_user_emotion(self, user_input: str) -> Dict[str, Any]:
        """Phân tích cảm xúc của user"""
        text = user_input.lower()
        
        positive_words = ['vui', 'hạnh phúc', 'tuyệt', 'tốt', 'thích', 'yêu']
        negative_words = ['buồn', 'tệ', 'khó chịu', 'stress', 'lo lắng', 'ghét']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            sentiment = 0.6
            emotion = "happy"
        elif negative_count > positive_count:
            sentiment = -0.6
            emotion = "sad"
        else:
            sentiment = 0.0
            emotion = "neutral"
        
        intensity_markers = ['rất', 'cực kỳ', 'quá', 'vô cùng']
        intensity = 0.8 if any(marker in text for marker in intensity_markers) else 0.5
        
        return {
            'sentiment': sentiment,
            'emotion': emotion,
            'intensity': intensity
        }


class BehaviorRules:
    """Enforce behavior rules"""
    
    def __init__(self):
        self.recent_responses = []
        self.max_history = 5
    
    def validate_response(self, response: str) -> tuple:
        """Validate response"""
        if len(response.strip()) < 5:
            return False, "Response too short"
        
        if len(response) > 1000:
            return False, "Response too long"
        
        if response in self.recent_responses:
            return False, "Repetitive response"
        
        if len(response.replace(' ', '').replace('.', '').replace(',', '')) < 3:
            return False, "No meaningful content"
        
        return True, None
    
    def track_response(self, response: str):
        """Track response"""
        self.recent_responses.append(response)
        if len(self.recent_responses) > self.max_history:
            self.recent_responses.pop(0)
