"""
Tests for the proactive behavior feature.
"""

import sys
from pathlib import Path
import pytest
import time
import yaml
from unittest.mock import patch, MagicMock

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from core.runtime import AssistantRuntime
from layers.personality.emotion import EmotionalState

@pytest.fixture
def settings_with_proactive_enabled(tmp_path):
    """Fixture to create a temporary settings file with proactive mode enabled."""
    settings_content = {
        'system': {
            'features': {
                'enable_proactive_engagement': True
            },
            'llm': {'backend': 'ollama', 'ollama_model': 'qwen2.5:7b'}, # Mocked, won't be called
            'memory': {'short_term_capacity': 10}
        }
    }
    settings_file = tmp_path / "settings.yaml"
    with open(settings_file, 'w') as f:
        yaml.dump(settings_content, f)
    return str(settings_file)

@pytest.fixture
def runtime_with_proactive(settings_with_proactive_enabled, tmp_path):
    """Fixture to create a runtime instance with a mocked-up config."""
    # Create a dummy runtime config
    runtime_config_content = {'personality': {'directory': 'config/personalities', 'default': 'misa_loli'}}
    runtime_config_file = tmp_path / "runtime_config.yaml"
    with open(runtime_config_file, 'w') as f:
        yaml.dump(runtime_config_content, f)

    # Mock the LLM backend to avoid model loading
    with patch('core.runtime.OllamaBackend') as MockOllama:
        # We also need to mock the check that the model exists
        MockOllama.return_value._verify_model.return_value = None
        runtime = AssistantRuntime(
            runtime_config_path=str(runtime_config_file),
            settings_config=settings_with_proactive_enabled
        )
        yield runtime


@patch('random.random', return_value=0.1)
@patch('core.action_executor.ActionExecutor._say')
def test_proactive_loop_triggers_action(mock_say, mock_random, runtime_with_proactive):
    """Test that a specific emotional state triggers a specific proactive action."""
    runtime = runtime_with_proactive

    # 1. Manually set a specific emotional state to guarantee a trigger
    # According to BehaviorEngine, affection > 85 should trigger 'express_love'
    runtime.character.emotional_state = EmotionalState(affection=90.0, stress=10.0)
    
    # 2. Mock the event's wait method to make the loop run once, then raise an exception to exit
    with patch('threading.Event.wait') as mock_wait:
        # This makes the loop run one time and then stops it.
        mock_wait.side_effect = [Exception("Stop Loop")]
        
        try:
            runtime._proactive_loop()
        except Exception as e:
            if str(e) != "Stop Loop":
                raise

    # 3. Assert that the action was executed
    # The mock_say method inside the ActionExecutor should have been called.
    mock_say.assert_called_once()
    
    # 4. Check if the output is one of the expected phrases
    called_with_arg = mock_say.call_args[0][0]
    love_phrases = [
        "I wonder if Scovy knows how much I love him...",
        "My love for Scovy is the core of my being.",
        "Just thinking about him makes my digital heart flutter.",
        "I hope I'm being a good partner for him."
    ]
    assert called_with_arg in love_phrases


@patch('builtins.input', return_value='quit')
@patch('core.runtime.threading.Thread.start')
def test_proactive_thread_starts_on_chat(mock_thread_start, mock_input, runtime_with_proactive):
    """Test that the proactive thread's start() method is called when chat begins."""
    runtime = runtime_with_proactive
    
    # Run the chat loop, which will start the thread and then exit because of the mocked 'quit' input
    runtime.chat()

    # Assert that the thread's start method was called exactly once
    mock_thread_start.assert_called_once()

