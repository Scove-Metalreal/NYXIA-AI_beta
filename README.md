# NYXIA AI - Multi-Layer Architecture

An AI assistant with a multi-layer architecture, featuring its own personality, long-term memory, and emotional system.

## ✨ Features

- **Multi-Layer Architecture**: A clear separation of concerns between personality, memory, reasoning, and the core LLM.
- **Dual LLM Backends**: Supports both local models via **Ollama** and powerful models via **Google Gemini**.
- **Dynamic Emotional State**: The AI's emotional state evolves based on the conversation.
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

## 🎯 Development Roadmap

- [x] Phase 1: Project setup & Basic prototype
- [x] Phase 2: Core AI functionality (memory, emotion, multi-layer pipeline)
- [ ] Phase 3: Humanization (proactive actions, relationship building)
- [ ] Phase 4: Tool usage & external API integration
- [ ] Phase 5: Avatar & Voice (Optional)

## 🧪 Testing

```bash
pytest tests/
```

## 🤝 Contributing

This is a personal project, but ideas and suggestions are always welcome!

## 📄 License

MIT