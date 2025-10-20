# Misa - An AI Companion

An AI assistant with a multi-layer architecture, featuring its own personality, long-term memory, and emotional system.

## ✨ Features

- **Multi-Layer Architecture**: A clear separation of concerns between personality, memory, reasoning, and the core LLM.
- **Dual LLM Backends**: Supports both local models via **Ollama** and powerful models via **Google Gemini**.
- **Dynamic Emotional State**: The AI's emotional state evolves based on nuanced NLU analysis of the conversation and naturally decays over time.
- **Long-Term & Short-Term Memory**: Utilizes both a short-term conversation buffer and a long-term vector database (ChromaDB) for context.
- **Automatic Fact Extraction**: The AI can identify and save key facts about the user from the conversation.
- **Interactive Chat**: A command-line interface with special commands for inspecting the AI's state (`stats`) or clearing its short-term memory (`clear`).

## 🏗️ Architecture

The assistant is built on a 4-layer architecture, allowing for complex and nuanced interactions.

```
Layer 1: Personality Layer  ← Defines core traits, speaking style, and emotional state.
Layer 2: Memory Layer       ← Manages short-term (conversation) and long-term (vector DB) memory.
Layer 3: Reasoning Layer    ← Builds context, analyzes user intent, and enforces behavior.
Layer 4: LLM Core           ← The underlying language model that generates responses.
```

The `core/runtime.py` file orchestrates the flow of information between these layers.

## 🚀 Quick Start

### 1. Cài đặt dependencies
```bash
# Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup LLM Backend

You can choose between Ollama (local) or Gemini (cloud).

#### Ollama
```bash
# Pull a model (e.g., qwen2.5:7b)
ollama pull qwen2.5:7b
```
Make sure the Ollama server is running (`ollama serve`).

#### Google Gemini
1. Get an API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Create a `.env` file in the project root and add your key:
   ```
   GEMINI_API_KEY="YOUR_API_KEY"
   ```

### 3. Config
1.  **`config/settings.yaml`**:
    *   Choose your LLM backend (`ollama` or `gemini`).
    *   Set the model name (e.g., `qwen2.5:7b` for Ollama, `gemini-1.5-flash` for Gemini).
    *   You can set the Ollama model to `interactive` to be prompted for a model choice on startup.
2.  **`config/personality.yaml`**: Customize the AI's name, core traits, and speaking style.
3.  **`config/behavior_rules.yaml`**: Define the rules the AI must follow.

### 4. Chạy
```bash
python main.py
```

## 📁 Project Structure

```
├── config/                 # Configuration files
│   ├── personality.yaml    # Defines the AI's character and emotional system.
│   ├── behavior_rules.yaml # Sets the rules and constraints for the AI's behavior.
│   └── settings.yaml       # General system settings, including the LLM backend.
│
├── core/                   # Core orchestration logic
│   └── runtime.py          # The main runtime that connects all layers and manages the chat loop.
│
├── layers/                 # The 4 main architectural layers
│   ├── personality/        # Layer 1: Manages the AI's personality and emotions.
│   ├── memory/             # Layer 2: Handles short-term and long-term memory.
│   ├── reasoning/          # Layer 3: Builds context and makes decisions.
│   └── llm/                # Layer 4: Interfaces with LLM backends (Ollama, Gemini).
│
├── data/                   # Data storage (logs, vector database)
│   ├── chroma_db/          # ChromaDB vector store for long-term memory.
│   └── logs/               # Application logs.
│
├── tests/                  # Pytest tests
├── main.py                 # Main entry point for the application.
└── requirements.txt        # Python dependencies.
```

## 🗺️ Development Phases

---

### ✅ Phase 1: Foundation (Completed)

_Goal: Establish the core architecture and basic functionalities._

- [x] **Multi-Layer Architecture**: Implemented the 4-layer system (Personality, Memory, Reasoning, LLM).
- [x] **Dual LLM Backend**: Integrated support for Ollama (local) and Google Gemini (cloud).
- [x] **Basic Memory**: Established short-term conversational memory and long-term fact storage (ChromaDB).
- [x] **CLI Interface**: Created a command-line interface for interaction.
- [x] **Initial Personality**: Defined core personality traits and speaking style in configuration files.

---

### 🧠 Phase 2: Core Intelligence Enhancement

_Goal: Move beyond a simple chatbot to an AI that understands subtext and behaves more proactively._

- [ ] **Advanced Emotional Modeling**: Develop a more complex emotional system that tracks mood over time and is influenced by more than just the last user input.
- [ ] **Deeper Language Understanding**: Improve the ability to detect sarcasm, implicit meaning, and the user's underlying intent.
- [ ] **Relationship Modeling**: Create a system to track the state of the user-AI relationship (e.g., trust, friendship level).
- [ ] **Proactive Behavior**: Implement a mechanism for Misa to initiate conversations or actions based on context (e.g., time of day, upcoming calendar events).

#### 🔬 **Phase 2 - Detailed Breakdown**

##### **Feature: Advanced Emotional Modeling**

_Goal: Evolve the AI's emotion from a simple dictionary to a more robust, persistent state that feels more alive._

- [x] **Sub-Task 1.1: Create a dedicated `EmotionalState` Class**

- **What to do:** Refactor the current dictionary-based emotional state into a dedicated Python class.
- **Files to Update:** Create a new file `layers/personality/emotion.py` and update `layers/personality/character.py`.
- **What Changes:** The new `EmotionalState` class will contain attributes for mood dimensions (e.g., using the PAD model: Pleasure, Arousal, Dominance) and methods like `.update(stimulus)`, `.decay()`, and `.get_current_mood()`.
- **How to do it:**
  1.  Create `layers/personality/emotion.py`.
  2.  Inside, define the `EmotionalState` class with floats for `pleasure`, `arousal`, and `dominance`.
  3.  In `layers/personality/character.py`, import this class and change `self.emotional_state = {}` to `self.emotional_state = EmotionalState()`.
  4.  Update the `update_emotion_from_user_input` method to call the new class's methods.
- **What to use:** Standard Python classes. You could use `pydantic` for data validation to make it more robust.
- **Why:** A class encapsulates logic, prevents errors from typos in dictionary keys, and makes the emotional state easier to manage, save, and expand upon later.

- [x] **Sub-Task 1.2: Implement Emotional Decay**

- **What to do:** Make Misa's emotions gradually return to a neutral baseline over time or between interactions.
- **Files to Update:** The new `layers/personality/emotion.py` and the main chat loop in `core/runtime.py`.
- **What Changes:** Add a `.decay()` method to the `EmotionalState` class that nudges the emotion values slightly towards a neutral center (e.g., 0.0).
- **How to do it:** In the `chat()` loop within `core/runtime.py`, after each user interaction is processed, make a call to `self.character.emotional_state.decay()`.
- **What to use:** The `decay()` method can reduce the emotional values by a small fixed percentage (e.g., `self.pleasure *= 0.95`).
- **Why:** This prevents the AI from getting "stuck" in an intense emotional state from a single comment. It makes her feel more dynamic and natural, as emotions fade over time.

---

##### **Feature: Deeper Language Understanding**

*Goal: Allow Misa to understand not just what is said, but *how* it's said, including subtext and sarcasm.*

- [x] **Sub-Task 2.1: Use a Specialized Model for Nuanced Analysis**

- **What to do:** Instead of just getting a basic sentiment score, use a more powerful model to detect intent, specific emotions (e.g., 'frustration' vs. 'sadness'), and potential sarcasm.
- **Files to Update:** `layers/reasoning/context_builder.py` (currently `DecisionEngine` is in there, might be worth splitting out to a new file `layers/reasoning/nlu.py`).
- **What Changes:** The `analyze_user_emotion` method will be replaced or upgraded to return a much richer object, like `{'sentiment': 'negative', 'emotion': 'frustration', 'intent': 'request_help', 'sarcasm': 0.85}`.
- **How to do it:**
  1.  Choose a suitable pre-trained model from the Hugging Face Hub (e.g., a RoBERTa-based model fine-tuned for emotion or intent classification).
  2.  In `context_builder.py`, use the `transformers` library to load this model.
  3.  Pass the user's input to the model to get a detailed analysis.
  4.  This detailed analysis will then be available to the `ContextBuilder` to create a more informed prompt for the main LLM.
- **What to use:** The `transformers` library from Hugging Face.
- **Why:** While the main LLM is a powerful generator, smaller, specialized models are often faster and more accurate for specific NLU (Natural Language Understanding) tasks. This offloads the work and provides higher-quality signals for Misa's emotional response and decision-making.

---

### 👁️ Phase 3: Multimodal Sensory Input

_Goal: Give Misa "eyes and ears" to perceive the user's environment._

- [ ] **Auditory System Module**:
  - [ ] Integrate microphone input.
  - [ ] Implement real-time voice-to-text.
  - [ ] Add speaker diarization to identify who is speaking.
  - [ ] Analyze vocal tone to detect emotion.
- [ ] **Visual System Module**:
  - [ ] Implement screen capture for context-aware assistance.
  - [ ] Integrate camera input.
  - [ ] Add face recognition to identify the user and others.
  - [ ] Implement object and scenario recognition.

---

### 🎭 Phase 4: Expressive Output & Embodiment

_Goal: Give Misa a body and voice to express her personality and emotions._

- [ ] **Voice Synthesis**:
  - [ ] Integrate a Text-to-Speech (TTS) engine.
  - [ ] Develop a system to modulate the TTS voice (pitch, speed, tone) based on Misa's current emotional state.
- [ ] **Avatar Integration**:
  - [ ] Design or acquire a V-Tuber avatar (similar to Neuro-sama).
  - [ ] Create a client to display the avatar.
  - [ ] Link the avatar's expressions and animations to Misa's emotional state and speech.

---

### 🖥️ Phase 5: System & Device Integration

_Goal: Allow Misa to exist and act within the user's digital and physical environment._

- [ ] **Web Control Panel**:
  - [ ] Design and build a web-based UI.
  - [ ] Implement controls for managing Misa's modules, permissions, and settings.
- [ ] **Desktop Agent**:
  - [ ] Create a secure, high-privilege agent that Misa can command.
  - [ ] Develop skills for file management, application control, and system interaction.
- [ ] **Coding Assistant Module**:
  - [ ] Build a skill that allows Misa to read code, suggest changes, and write new code, similar to a CLI agent.
- [ ] **Device & Smart Home Control**:
  - [ ] Create a generic API for adding and controlling smart devices (lights, speakers, etc.).
  - [ ] Implement specific integrations for target devices (e.g., Philips Hue, Spotify).

---

### 🚀 Phase 6: Advanced Skills & Interaction

_Goal: Expand Misa's capabilities to include complex social tasks and talents._

- [ ] **Social Integration Module**:
  - [ ] Connect to the Discord API.
  - [ ] Implement skills for sending messages, reading chats, and joining voice calls.
- [ ] **Talent Modules**:
  - [ ] **Gaming**: Implement logic for playing games like Chess or Osu!.
  - [ ] **Singing**: Integrate with a singing synthesis engine or develop a custom solution.
  - [ ] **Live Streaming**: Develop a module to read live chat and react, assisting a streamer.

## 🧪 Testing

```bash
pytest tests/
```

## 🤝 Contributing

This is a personal project, but ideas and suggestions are always welcome!

## 📄 License

MIT