from pydantic import BaseModel, Field

class EmotionalState(BaseModel):
    mood: float = Field(default=70.0, ge=0.0, le=100.0, description="Overall happiness/disposition (0-100)")
    energy: float = Field(default=80.0, ge=0.0, le=100.0, description="Level of alertness and activity (0-100)")
    affection: float = Field(default=50.0, ge=0.0, le=100.0, description="Closeness/positive regard towards user (0-100)")
    stress: float = Field(default=20.0, ge=0.0, le=100.0, description="Level of mental/emotional strain (0-100)")

    def update(self, mood_delta: float = 0.0, energy_delta: float = 0.0, affection_delta: float = 0.0, stress_delta: float = 0.0):
        """Updates the emotional state based on changes, ensuring values stay within bounds."""
        self.mood = max(0.0, min(100.0, self.mood + mood_delta))
        self.energy = max(0.0, min(100.0, self.energy + energy_delta))
        self.affection = max(0.0, min(100.0, self.affection + affection_delta))
        self.stress = max(0.0, min(100.0, self.stress + stress_delta))

    def decay(self, decay_rate: float = 0.05):
        """Gradually returns emotional dimensions towards a neutral baseline."""
        # Decay towards a neutral point (e.g., 50 for mood/affection, 0 for stress, 50 for energy)
        self.mood += (50 - self.mood) * decay_rate
        self.energy += (50 - self.energy) * decay_rate
        self.affection += (50 - self.affection) * decay_rate
        self.stress += (0 - self.stress) * decay_rate # Stress decays to 0

        # Ensure values stay within bounds after decay
        self.mood = max(0.0, min(100.0, self.mood))
        self.energy = max(0.0, min(100.0, self.energy))
        self.affection = max(0.0, min(100.0, self.affection))
        self.stress = max(0.0, min(100.0, self.stress))

    def get_mood_description(self) -> str:
        """Returns a descriptive string of the current mood."""
        if self.mood >= 80:
            return "very happy"
        elif self.mood >= 60:
            return "happy"
        elif self.mood >= 40:
            return "a bit sad"
        else:
            return "sad"

    def to_dict(self) -> dict:
        """Returns the current emotional state as a dictionary."""
        return self.model_dump() # pydantic v2 method

    def __repr__(self):
        return f"EmotionalState(Mood={self.mood:.2f}, Energy={self.energy:.2f}, Affection={self.affection:.2f}, Stress={self.stress:.2f})"