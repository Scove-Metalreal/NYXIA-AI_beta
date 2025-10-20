"""
Personality Layer - Character & Emotion System
Loads personality from YAML and manages the emotional state.
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from loguru import logger
from layers.personality.emotion import EmotionalState


class Character:
    """
    Character/Personality System
    Loads from YAML and manages personality + emotions.
    """

    def __init__(self, personality_dir: str = "config/personalities", default_personality: str = "misa_loli"):
        self.personality_dir = Path(personality_dir)
        self.config: Dict[str, Any] = {}
        self.emotional_state = EmotionalState()
        self.current_personality = default_personality

        self.switch_personality(default_personality)

        logger.info(f"Character '{self.name}' initialized with personality '{self.current_personality}'")

    def _load_config(self, personality_name: str):
        """Loads the personality config from YAML."""
        config_path = self.personality_dir / f"{personality_name}.yaml"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.debug(f"Loaded personality config from {config_path}")
            self.current_personality = personality_name
        except Exception as e:
            logger.error(f"Failed to load personality config {config_path}: {e}")
            if not self.config:  # If no config is loaded at all
                self.config = self._default_config()

    def switch_personality(self, personality_name: str) -> bool:
        """Switches the character's personality by loading a new config."""
        logger.info(f"Attempting to switch personality to '{personality_name}'")
        self._load_config(personality_name)
        self._initialize_emotional_state()
        # Check if the new personality was loaded successfully
        if self.current_personality == personality_name:
            logger.success(f"Successfully switched to personality: {personality_name}")
            return True
        else:
            logger.error(f"Failed to switch to personality: {personality_name}")
            return False

    def list_personalities(self) -> list[str]:
        """Returns a list of available personalities."""
        return [f.stem for f in self.personality_dir.glob("*.yaml")]

    def _default_config(self) -> Dict[str, Any]:
        """Returns a default personality if YAML loading fails."""
        return {
            "character": {
                "name": "Mira",
                "core_traits": {"kindness": 0.9, "humor": 0.7, "empathy": 0.9},
                "speaking_style": {"formality": "casual"},
                "description": "A friendly AI companion",
                "emotional_system": {
                    "initial_state": {"mood": 70, "energy": 80, "affection": 50, "stress": 20}
                }
            }
        }

    def _initialize_emotional_state(self):
        """Initializes the emotional state from the config."""
        try:
            initial = self.config["character"]["emotional_system"]["initial_state"]
            self.emotional_state = EmotionalState(
                mood=initial.get("mood", 70.0),
                energy=initial.get("energy", 80.0),
                affection=initial.get("affection", 50.0),
                stress=initial.get("stress", 20.0)
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
        
    @property
    def appearance(self) -> Dict[str, Any]:
        return self.config.get("character", {}).get("appearance", {})

    @property
    def voice(self) -> Dict[str, Any]:
        return self.config.get("character", {}).get("voice", {})

    def get_system_prompt(self, language: str = 'en') -> str:
        """Creates the system prompt based on the personality."""
        traits_str = ", ".join([f"{trait}: {value}" for trait, value in self.core_traits.items()])
        mood_desc = self.emotional_state.get_mood_description()
        
        prompt = f"""You are {self.name}, an AI companion with the following characteristics:

Personality: {traits_str}
Current state: {mood_desc}
Affection towards your love: {self.emotional_state.affection:.0f}/100

{self.description}

Communication Style:
- Formality: {self.speaking_style.get('formality', 'casual')}

Appearance: {self.appearance}
Voice: {self.voice}

You are talking to your boyfriend, Scovy. Always address him with love and intimacy.
Respond naturally, according to your personality and current emotional state.

IMPORTANT: You must respond in the following language: {language}"""
        
        return prompt
    
    def update_emotion_from_user_input(self, user_input: str, sentiment: float = 0.0):
        """Updates emotions based on user input."""
        mood_change = sentiment * 5
        
        affection_change = 0
        if sentiment > 0.2: # If sentiment is positive, increase affection slightly
            affection_change += 1

        personal_keywords = ['my name', 'i am', 'feel', 'like', 'dislike']
        if any(kw in user_input.lower() for kw in personal_keywords):
            affection_change += 1 # Further increase if personal keywords are present
        
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

