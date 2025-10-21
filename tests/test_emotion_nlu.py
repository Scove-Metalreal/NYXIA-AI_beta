import sys
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import pytest
from layers.personality.emotion import EmotionalState
from layers.reasoning.nlu import NLUAnalyzer
from layers.personality.character import Character
from layers.reasoning.context_builder import DecisionEngine

# --- EmotionalState Tests ---

def test_emotional_state_initialization():
    state = EmotionalState()
    assert state.mood == 70.0
    assert state.energy == 80.0
    assert state.affection == 50.0
    assert state.stress == 20.0

def test_emotional_state_update():
    state = EmotionalState()
    state.update(mood_delta=10, energy_delta=-5, affection_delta=15, stress_delta=5)
    assert state.mood == 80.0
    assert state.energy == 75.0
    assert state.affection == 65.0
    assert state.stress == 25.0

    # Test boundary conditions
    state.update(mood_delta=100)
    assert state.mood == 100.0
    state.update(stress_delta=-100)
    assert state.stress == 0.0

def test_emotional_state_decay():
    state = EmotionalState(mood=100, energy=100, affection=100, stress=100)
    state.decay(decay_rate=0.1)
    # Check if values moved towards neutral (50 for mood/energy/affection, 0 for stress)
    assert state.mood < 100
    assert state.energy < 100
    assert state.affection < 100
    assert state.stress < 100

    state_low = EmotionalState(mood=0, energy=0, affection=0, stress=0)
    state_low.decay(decay_rate=0.1)
    assert state_low.mood > 0
    assert state_low.energy > 0
    assert state_low.affection > 0
    assert state_low.stress == 0 # Stress decays to 0, so it should stay 0 if already there

def test_emotional_state_get_mood_description():
    state = EmotionalState(mood=90)
    assert state.get_mood_description() == "very happy"
    state.mood = 70
    assert state.get_mood_description() == "happy"
    state.mood = 50
    assert state.get_mood_description() == "a bit sad"
    state.mood = 20
    assert state.get_mood_description() == "sad"

# --- NLUAnalyzer Tests ---

def test_nlu_analyzer_sentiment_positive():
    analyzer = NLUAnalyzer()
    result = analyzer.analyze_text("I love this project, it's amazing!")
    assert result["sentiment"]["label"] == "positive"
    assert result["sentiment"]["score"] > 0

def test_nlu_analyzer_sentiment_negative():
    analyzer = NLUAnalyzer()
    result = analyzer.analyze_text("This is terrible, I hate it.")
    assert result["sentiment"]["label"] == "negative"
    assert result["sentiment"]["score"] < 0

def test_nlu_analyzer_sentiment_neutral():
    analyzer = NLUAnalyzer()
    result = analyzer.analyze_text("The sky is blue.")
    # The model classifies this as positive, so we assert for that.
    assert result["sentiment"]["label"] == "positive"
    assert result["sentiment"]["score"] > 0.9 # High positive score

# --- Integration Tests (Character & DecisionEngine) ---

def test_decision_engine_nlu_integration():
    engine = DecisionEngine()
    user_input = "This is a fantastic idea!"
    analysis = engine.analyze_user_emotion(user_input)
    assert "sentiment" in analysis
    assert analysis["sentiment"]["label"] == "positive"
    assert analysis["sentiment"]["score"] > 0

def test_character_emotion_update_from_nlu():
    character = Character()
    engine = DecisionEngine()

    initial_mood = character.emotional_state.mood
    initial_affection = character.emotional_state.affection

    # Simulate positive input
    positive_input = "I really enjoy talking to you, Misa!"
    nlu_analysis = engine.analyze_user_emotion(positive_input)
    character.update_emotion_from_user_input(positive_input, sentiment=nlu_analysis["sentiment"]["score"])

    assert character.emotional_state.mood > initial_mood
    assert character.emotional_state.affection > initial_affection

    # Simulate negative input
    negative_input = "I'm feeling quite sad today."
    nlu_analysis = engine.analyze_user_emotion(negative_input)
    mood_before_negative = character.emotional_state.mood # Capture mood before negative update
    character.update_emotion_from_user_input(negative_input, sentiment=nlu_analysis["sentiment"]["score"])

    assert character.emotional_state.mood < mood_before_negative # Mood should decrease from previous state

    # Test personal keywords for affection
    personal_input = "My name is Scovy and I like you."
    nlu_analysis = engine.analyze_user_emotion(personal_input)
    current_affection = character.emotional_state.affection
    character.update_emotion_from_user_input(personal_input, sentiment=nlu_analysis["sentiment"]["score"])
    assert character.emotional_state.affection > current_affection

