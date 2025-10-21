from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import random
from loguru import logger

class EmotionalState(BaseModel):
    """A more dynamic emotional state that can generate spontaneous actions."""
    # Core emotional dimensions
    mood: float = Field(default=70.0, ge=0.0, le=100.0, description="Overall happiness/disposition (0-100)")
    energy: float = Field(default=80.0, ge=0.0, le=100.0, description="Level of alertness and activity (0-100)")
    affection: float = Field(default=50.0, ge=0.0, le=100.0, description="Closeness/positive regard towards user (0-100)")
    stress: float = Field(default=20.0, ge=0.0, le=100.0, description="Level of mental/emotional strain (0-100)")

    # Personality-derived baselines and rates
    mood_baseline: float = Field(default=50.0, ge=0.0, le=100.0)
    energy_baseline: float = Field(default=50.0, ge=0.0, le=100.0)
    affection_baseline: float = Field(default=50.0, ge=0.0, le=100.0)
    stress_baseline: float = Field(default=10.0, ge=0.0, le=100.0)
    decay_modifier: float = Field(default=1.0, ge=0.1, le=2.0)

    def __init__(self, personality_config: Dict[str, Any] = None, **data):
        super().__init__(**data)
        if personality_config:
            self._initialize_dynamics(personality_config)

    def _initialize_dynamics(self, config: Dict[str, Any]):
        traits = config.get("character", {}).get("core_traits", {})
        playfulness = traits.get("playfulness", 0.5)
        melancholy = traits.get("melancholy", 0.5)
        passion = traits.get("passion", 0.5)
        devotion = traits.get("devotion", 0.5)

        self.mood_baseline = 60 + (playfulness * 20) - (melancholy * 30)
        self.energy_baseline = 50 + (passion * 20) + (playfulness * 10)
        self.affection_baseline = 40 + (devotion * 50)
        self.stress_baseline = 20 - (playfulness * 10)
        self.decay_modifier = 1.0 - (passion * 0.5)

        self.mood_baseline = max(10.0, min(90.0, self.mood_baseline))
        self.energy_baseline = max(10.0, min(90.0, self.energy_baseline))
        self.affection_baseline = max(10.0, min(90.0, self.affection_baseline))
        self.stress_baseline = max(0.0, min(50.0, self.stress_baseline))
        self.decay_modifier = max(0.2, min(1.5, self.decay_modifier))

    def update(self, mood_delta: float = 0.0, energy_delta: float = 0.0, affection_delta: float = 0.0, stress_delta: float = 0.0):
        mood_delta += random.uniform(-2.0, 2.0)
        affection_delta += random.uniform(-1.0, 1.0)
        self.mood = max(0.0, min(100.0, self.mood + mood_delta))
        self.energy = max(0.0, min(100.0, self.energy + energy_delta))
        self.affection = max(0.0, min(100.0, self.affection + affection_delta))
        self.stress = max(0.0, min(100.0, self.stress + stress_delta))

    def decay(self, base_decay_rate: float = 0.05):
        effective_decay_rate = base_decay_rate * self.decay_modifier
        self.mood += (self.mood_baseline - self.mood) * effective_decay_rate
        self.energy += (self.energy_baseline - self.energy) * effective_decay_rate
        self.affection += (self.affection_baseline - self.affection) * effective_decay_rate
        self.stress += (self.stress_baseline - self.stress) * effective_decay_rate
        self.mood = max(0.0, min(100.0, self.mood))
        self.energy = max(0.0, min(100.0, self.energy))
        self.affection = max(0.0, min(100.0, self.affection))
        self.stress = max(0.0, min(100.0, self.stress))

    def get_spontaneous_action(self) -> Optional[str]:
        """
        Determines a spontaneous action based on the current emotional state.
        This is the source of the AI's "inner monologue" and proactive behavior.
        """
        logger.debug(f"Checking for spontaneous action with emotion: {self}")
        possible_actions = []

        if self.affection > 85 and self.stress < 30:
            possible_actions.append(("express_love", 0.4))
        if self.energy < 20:
            possible_actions.append(("feel_sleepy", 0.5))
        if self.stress > 70:
            possible_actions.append(("express_worry", 0.45))
        if self.energy > 80 and self.mood > 75:
            possible_actions.append(("be_mischievous", 0.2))
        if self.affection > 70 and 30 < self.mood < 60:
            possible_actions.append(("express_longing", 0.25))
        if self.energy > 70 and self.mood > 60:
            possible_actions.append(("comment_on_project", 0.15))
        if self.energy > 75 and self.affection > 75:
            possible_actions.append(("suggest_activity", 0.2))
        if self.affection > 80 and 50 < self.mood < 80:
            possible_actions.append(("reminisce_memory", 0.15))
        if self.affection > 90 and self.stress > 25:
            possible_actions.append(("express_possessiveness", 0.3))
        if self.mood > 50 and self.stress < 40:
            possible_actions.append(("express_curiosity", 0.1))

        if not possible_actions:
            return None

        actions, weights = zip(*possible_actions)
        chosen_action = random.choices(actions, weights=weights, k=1)[0]
        
        if random.random() > 0.4:
             logger.debug("Decided to stay quiet this time.")
             return None

        logger.info(f"Spontaneous action triggered: {chosen_action} (from {len(actions)} options)")
        return chosen_action

    def get_mood_description(self) -> str:
        if self.mood >= 80:
            return "very happy"
        elif self.mood >= 60:
            return "happy"
        elif self.mood >= 40:
            return "a bit sad"
        else:
            return "sad"

    def to_dict(self) -> dict:
        return self.model_dump()

    def __repr__(self):
        return (
            f"EmotionalState(Mood={self.mood:.1f}/B:{self.mood_baseline:.1f}, "
            f"Energy={self.energy:.1f}/B:{self.energy_baseline:.1f}, "
            f"Affection={self.affection:.1f}/B:{self.affection_baseline:.1f}, "
            f"Stress={self.stress:.1f}/B:{self.stress_baseline:.1f}, "
            f"DecayMod={self.decay_modifier:.2f})"
        )