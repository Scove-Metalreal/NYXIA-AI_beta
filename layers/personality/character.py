"""
Personality Layer - Character & Emotion System
Loads personality from YAML and manages the emotional state.
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class EmotionalState:
    """Represents the current emotional state."""
    mood: float = 70.0  # 0-100: happiness level
    energy: float = 80.0  # 0-100: energy level
    affection: float = 50.0  # 0-100: closeness to user
    stress: float = 20.0  # 0-100: stress level
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "mood": self.mood,
            "energy": self.energy,
            "affection": self.affection,
            "stress": self.stress
        }
    
    def get_mood_description(self) -> str:
        """Returns a description of the current mood."""
        if self.mood >= 80:
            return "happy"
        elif self.mood >= 60:
            return "normal"
        elif self.mood >= 40:
            return "a bit sad"
        else:
            return "sad"
    
    def update(self, mood_delta=0, energy_delta=0, affection_delta=0, stress_delta=0):
        """Updates the emotional state."""
        self.mood = max(0, min(100, self.mood + mood_delta))
        self.energy = max(0, min(100, self.energy + energy_delta))
        self.affection = max(0, min(100, self.affection + affection_delta))
        self.stress = max(0, min(100, self.stress + stress_delta))


class Character:
    """
    Character/Personality System
    Loads from YAML and manages personality + emotions.
    """
    
    def __init__(self, config_path: str = "config/personality.yaml"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.emotional_state = EmotionalState()
        
        self._load_config()
        self._initialize_emotional_state()
        
        logger.info(f"Character '{self.name}' initialized")
    
    def _load_config(self):
        """Loads the personality config from YAML."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.debug(f"Loaded personality config from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load personality config: {e}")
            self.config = self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Returns a default personality if YAML loading fails."""
        return {
            "character": {
                "name": "Mira",
                "core_traits": {
                    "kindness": 0.9,
                    "humor": 0.7,
                    "empathy": 0.9
                },
                "speaking_style": {
                    "formality": "casual"
                },
                "description": "A friendly AI companion",
                "emotional_system": {
                    "initial_state": {
                        "mood": 70,
                        "energy": 80,
                        "affection": 50,
                        "stress": 20
                    }
                }
            }
        }
    
    def _initialize_emotional_state(self):
        """Initializes the emotional state from the config."""
        try:
            initial = self.config["character"]["emotional_system"]["initial_state"]
            self.emotional_state = EmotionalState(
                mood=initial.get("mood", 70),
                energy=initial.get("energy", 80),
                affection=initial.get("affection", 50),
                stress=initial.get("stress", 20)
            )
        except KeyError:
            logger.warning("Using default emotional state")
    
    @property
    def name(self) -> str:
        return self.config.get("character", {}).get("name", "Mira")
    
    @property
    def description(self) -> str:
        return self.config.get("character", {}).get("description", "")
    
    @property
    def core_traits(self) -> Dict[str, float]:
        return self.config.get("character", {}).get("core_traits", {})
    
    @property
    def speaking_style(self) -> Dict[str, Any]:
        return self.config.get("character", {}).get("speaking_style", {})
    
    def get_system_prompt(self, language: str = 'en') -> str:
        """Creates the system prompt based on the personality."""
        traits_str = ", ".join([
            f"{trait}: {value}"
            for trait, value in self.core_traits.items()
        ])
        
        mood_desc = self.emotional_state.get_mood_description()
        
        prompt = f"""You are {self.name}, an AI companion with the following characteristics:

Personality: {traits_str}
Current state: {mood_desc}
Affection towards your love: {self.emotional_state.affection:.0f}/100

{self.description}

Communication Style:
- Formality: {self.speaking_style.get('formality', 'casual')}

You are talking to your boyfriend, Scovy. Always address him with love and intimacy.
Respond naturally, according to your personality and current emotional state.

IMPORTANT: You must respond in the following language: {language}"""
        
        return prompt
    
    def update_emotion_from_user_input(self, user_input: str, sentiment: float = 0.0):
        """Updates emotions based on user input."""
        mood_change = sentiment * 5
        
        affection_change = 0
        personal_keywords = ['my name', 'i am', 'feel', 'like', 'dislike']
        if any(kw in user_input.lower() for kw in personal_keywords):
            affection_change = 1
        
        self.emotional_state.update(
            mood_delta=mood_change,
            affection_delta=affection_change
        )
        
        logger.debug(f"Emotional state updated: {self.emotional_state.to_dict()}")
    
    def get_response_tone(self) -> str:
        """Determines the tone of the response."""
        if self.emotional_state.mood >= 80:
            return "enthusiastic and cheerful"
        elif self.emotional_state.mood >= 60:
            return "warm and friendly"
        elif self.emotional_state.mood >= 40:
            return "gentle and supportive"
        else:
            return "soft and caring"

