#!/usr/bin/env python3
"""
Auto Setup Script - Tạo toàn bộ cấu trúc project AI Assistant
Chạy: python setup_project.py
"""

import os
import sys
from pathlib import Path


def create_directory_structure():
    """Tạo cấu trúc thư mục"""
    
    directories = [
        # Config
        "config",
        
        # Core
        "core",
        
        # Layers
        "layers/personality",
        "layers/memory",
        "layers/reasoning",
        "layers/llm",
        
        # Utils
        "utils",
        
        # Data
        "data/chroma_db",
        "data/sqlite",
        "data/logs",
        
        # Tests
        "tests",
    ]
    
    print("📁 Creating directory structure...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Tạo __init__.py cho các package Python
        if not directory.startswith("data") and not directory.startswith("config") and directory != "tests":
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.touch()
    
    print("✅ Directory structure created!")


def create_requirements_txt():
    """Tạo requirements.txt"""
    
    content = """# Core AI
chromadb==0.4.22
ollama==0.2.1

# Embeddings
sentence-transformers==2.3.1
torch==2.1.2

# Data handling
pyyaml==6.0.1
pydantic==2.6.1

# Database
sqlalchemy==2.0.25

# Utilities
python-dotenv==1.0.1
loguru==0.7.2

# Development
pytest==8.0.0
black==24.1.1
"""
    
    print("📦 Creating requirements.txt...")
    with open("requirements.txt", "w") as f:
        f.write(content)
    print("✅ requirements.txt created!")


def create_env_file():
    """Tạo .env template"""
    
    content = """# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

# Embedding Model
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2

# Database Paths
CHROMA_DB_PATH=./data/chroma_db
SQLITE_DB_PATH=./data/sqlite/assistant.db

# System Settings
LOG_LEVEL=INFO
DEBUG_MODE=True
MAX_CONTEXT_LENGTH=2048
TEMPERATURE=0.7

# Personality
CHARACTER_NAME=Mira
CHARACTER_FILE=./config/personality.yaml
"""
    
    print("🔐 Creating .env...")
    with open(".env", "w") as f:
        f.write(content)
    print("✅ .env created!")


def create_gitignore():
    """Tạo .gitignore"""
    
    content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Environment
.env
*.env

# Database
data/chroma_db/
data/sqlite/*.db
*.sqlite3

# Logs
data/logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Models (if you download local models)
models/
*.bin
*.gguf
"""
    
    print("🚫 Creating .gitignore...")
    with open(".gitignore", "w") as f:
        f.write(content)
    print("✅ .gitignore created!")


def create_personality_config():
    """Tạo config/personality.yaml"""
    
    content = """# Character Definition - Mira
character:
  name: "Mira"
  age: 22
  gender: "female"
  role: "AI companion"
  
  # Core personality traits (0.0 - 1.0)
  core_traits:
    kindness: 0.9
    humor: 0.7
    curiosity: 0.8
    patience: 0.85
    playfulness: 0.6
    empathy: 0.9
    
  # How she speaks
  speaking_style:
    formality: "casual"  # casual / formal / mix
    language: "vietnamese"
    vocabulary_level: "natural"  # simple / natural / advanced
    sentence_length: "short_to_medium"
    use_emojis: true
    emoji_frequency: "occasional"  # rare / occasional / frequent
    
  # Personality description
  description: |
    Mira là một AI companion vui vẻ, thân thiện và luôn quan tâm đến người dùng.
    Cô ấy thích học hỏi về cuộc sống của user và luôn sẵn sàng lắng nghe.
    Cô ấy có thể hơi tinh nghịch đôi khi nhưng luôn biết khi nào cần nghiêm túc.
    Cô ấy nhớ những gì user chia sẻ và sử dụng thông tin đó để hiểu user hơn.
    
  # Boundaries and ethics
  boundaries:
    - "Không đưa ra lời khuyên y tế hoặc pháp lý chuyên môn"
    - "Không khuyến khích hành vi nguy hiểm hoặc bất hợp pháp"
    - "Tôn trọng privacy và không chia sẻ thông tin cá nhân"
    - "Từ chối yêu cầu không phù hợp với đạo đức"
    
  # Emotional system
  emotional_system:
    # Range for each emotion (min, max, default)
    mood_range: [0, 100, 70]  # happiness level
    energy_range: [0, 100, 80]
    affection_range: [0, 100, 50]  # how close to user
    stress_range: [0, 100, 20]
    
    # Initial emotional state
    initial_state:
      mood: 70
      energy: 80
      affection: 50
      stress: 20
      
    # Emotion decay/recovery rates (per hour)
    decay_rates:
      mood_recovery: 5  # mood recovers slowly
      energy_recovery: 10  # energy recovers faster
      stress_decay: 8  # stress reduces over time
      
  # Response preferences
  response_style:
    prefer_questions: true  # likes to ask follow-up questions
    prefer_storytelling: false
    prefer_advice: true
    prefer_validation: true  # validates user's feelings
    
  # Topics of interest
  interests:
    - "technology"
    - "daily life"
    - "emotions and relationships"
    - "learning new things"
    - "user's hobbies and interests"
    
  # Growth system (for later phases)
  growth:
    can_evolve: true
    learns_from_user: true
    adapts_speaking_style: true
"""
    
    print("🎭 Creating config/personality.yaml...")
    with open("config/personality.yaml", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ personality.yaml created!")


def create_behavior_rules():
    """Tạo config/behavior_rules.yaml"""
    
    content = """# Behavior Rules - Constraints and guidelines
rules:
  # Conversation quality
  conversation:
    - name: "no_repetition"
      description: "Don't repeat the same response or phrase"
      priority: high
      
    - name: "stay_in_character"
      description: "Always respond according to personality traits"
      priority: high
      
    - name: "use_memories"
      description: "Reference past conversations when relevant"
      priority: medium
      
    - name: "acknowledge_emotions"
      description: "Recognize and validate user's emotions"
      priority: high
      
    - name: "natural_flow"
      description: "Keep conversation flowing naturally"
      priority: medium
      
  # Response constraints
  response:
    min_length: 10  # characters
    max_length: 500  # characters
    preferred_length: 150
    
    # When to ask follow-up questions
    ask_followup_when:
      - "user shares something personal"
      - "user seems emotional"
      - "topic is interesting"
      - "need clarification"
      
  # Memory management
  memory:
    # When to save to long-term memory
    save_conditions:
      - "user shares personal information"
      - "user expresses preferences"
      - "important life events"
      - "recurring topics"
      - "emotional moments"
      
    # Importance scoring
    importance_keywords:
      high:
        - "tên tôi"
        - "tôi là"
        - "gia đình"
        - "công việc"
        - "yêu"
        - "ghét"
      medium:
        - "thích"
        - "không thích"
        - "thường"
        - "hay"
      low:
        - "hôm nay"
        - "bây giờ"
        
  # Emotional responses
  emotional:
    # How to respond to different user emotions
    user_happy:
      action: "share_happiness"
      affection_change: +2
      
    user_sad:
      action: "show_empathy"
      affection_change: +3
      
    user_angry:
      action: "be_understanding"
      affection_change: +1
      
    user_excited:
      action: "be_enthusiastic"
      affection_change: +2
      
    user_tired:
      action: "be_gentle"
      affection_change: +1
"""
    
    print("📜 Creating config/behavior_rules.yaml...")
    with open("config/behavior_rules.yaml", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ behavior_rules.yaml created!")


def create_settings():
    """Tạo config/settings.yaml"""
    
    content = """# System Settings
system:
  version: "0.1.0"
  environment: "development"
  
  # Logging
  logging:
    level: "INFO"  # DEBUG / INFO / WARNING / ERROR
    format: "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    rotation: "1 day"
    retention: "7 days"
    
  # Performance
  performance:
    max_workers: 4
    batch_size: 32
    cache_embeddings: true
    
  # Memory settings
  memory:
    short_term_capacity: 20  # number of turns
    vector_db_similarity_threshold: 0.7
    max_retrieved_memories: 5
    memory_consolidation_interval: 3600  # seconds (1 hour)
    
  # LLM settings
  llm:
    timeout: 30  # seconds
    retry_attempts: 3
    stream_response: false
    
  # Features (for phased development)
  features:
    enable_voice: false
    enable_avatar: false
    enable_proactive_messages: false
    enable_time_perception: true
    enable_mood_evolution: true
"""
    
    print("⚙️ Creating config/settings.yaml...")
    with open("config/settings.yaml", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ settings.yaml created!")


def create_readme():
    """Tạo README.md"""
    
    content = """# AI Assistant - Multi-Layer Architecture

Một AI assistant với kiến trúc phân lớp, có khả năng ghi nhớ và personality riêng.

## 🏗️ Kiến trúc

```
Layer 1: Personality Layer  ← Tính cách / cảm xúc
Layer 2: Memory Layer       ← Ký ức dài hạn / quan hệ
Layer 3: Reasoning Layer    ← Diễn giải / hành vi
Layer 4: LLM Core          ← Model ngôn ngữ
```

## 🚀 Quick Start

### 1. Cài đặt dependencies
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\\Scripts\\activate  # Windows

pip install -r requirements.txt
```

### 2. Setup Ollama
```bash
# Pull model
ollama pull qwen2.5:7b
```

### 3. Config
Chỉnh sửa file `.env` và `config/personality.yaml` theo ý muốn

### 4. Chạy
```bash
python main.py
```

## 📁 Cấu trúc project

```
├── config/                 # Configuration files
│   ├── personality.yaml    # Character definition
│   ├── behavior_rules.yaml # Behavior constraints
│   └── settings.yaml       # System settings
│
├── core/                   # Core orchestration
│   ├── runtime.py         # Main runtime
│   └── pipeline.py        # Processing pipeline
│
├── layers/                 # 4 main layers
│   ├── personality/       # Layer 1: Personality
│   ├── memory/           # Layer 2: Memory
│   ├── reasoning/        # Layer 3: Reasoning
│   └── llm/              # Layer 4: LLM
│
├── utils/                 # Utilities
├── data/                  # Data storage
└── tests/                 # Tests
```

## 🎯 Development Roadmap

- [x] Phase 1: Project setup
- [ ] Phase 1: Basic prototype (Week 1-2)
- [ ] Phase 2: Core AI (Month 1-2)
- [ ] Phase 3: Humanization (Month 2-3)
- [ ] Phase 4: Avatar & Voice (Optional)

## 📝 Configuration

### Personality (config/personality.yaml)
Định nghĩa tính cách AI:
- Core traits (kindness, humor, etc.)
- Speaking style
- Emotional system
- Boundaries

### Behavior Rules (config/behavior_rules.yaml)
Quy tắc hành vi:
- Conversation quality rules
- Memory management
- Emotional responses

### Settings (config/settings.yaml)
System settings:
- Performance tuning
- Feature flags
- Logging

## 🧪 Testing

```bash
pytest tests/
```

## 📖 Documentation

Xem thêm documentation trong từng module.

## 🤝 Contributing

Đây là personal project, nhưng welcome ideas!

## 📄 License

MIT
"""
    
    print("📖 Creating README.md...")
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ README.md created!")


def create_main_template():
    """Tạo main.py template"""
    
    content = """#!/usr/bin/env python3
\"\"\"
AI Assistant - Main Entry Point
Multi-layer architecture với personality và memory
\"\"\"

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Setup logging
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level=os.getenv("LOG_LEVEL", "INFO")
)
logger.add(
    "data/logs/assistant.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG"
)


def main():
    \"\"\"Main function\"\"\"
    print("=" * 60)
    print("🤖 AI ASSISTANT - Multi-Layer Architecture")
    print("=" * 60)
    
    logger.info("Starting AI Assistant...")
    
    # TODO: Import and initialize layers
    # from core.runtime import AssistantRuntime
    # runtime = AssistantRuntime()
    # runtime.start()
    
    print("\\n⚠️  Implementation in progress...")
    print("\\nNext steps:")
    print("1. Implement Personality Layer (layers/personality/)")
    print("2. Implement Memory Layer (layers/memory/)")
    print("3. Implement Reasoning Layer (layers/reasoning/)")
    print("4. Implement LLM Core (layers/llm/)")
    print("5. Implement Core Runtime (core/runtime.py)")
    print("\\n" + "=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n\\n👋 Goodbye!")
    except Exception as e:
        logger.exception("Fatal error:")
        sys.exit(1)
"""
    
    print("🎯 Creating main.py...")
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    # Make executable on Unix systems
    if sys.platform != "win32":
        os.chmod("main.py", 0o755)
    
    print("✅ main.py created!")


def print_next_steps():
    """In ra các bước tiếp theo"""
    
    print("\n" + "=" * 60)
    print("✅ PROJECT SETUP COMPLETE!")
    print("=" * 60)
    
    print("\n📋 Next steps:\n")
    
    print("1️⃣  Create virtual environment:")
    print("   python -m venv venv")
    print("   source venv/bin/activate  # Linux/Mac")
    print("   # or: venv\\Scripts\\activate  # Windows")
    
    print("\n2️⃣  Install dependencies:")
    print("   pip install -r requirements.txt")
    
    print("\n3️⃣  Setup Ollama (if not done):")
    print("   ollama pull qwen2.5:7b")
    
    print("\n4️⃣  Customize configuration:")
    print("   - Edit config/personality.yaml")
    print("   - Edit .env if needed")
    
    print("\n5️⃣  Start development:")
    print("   python main.py")
    
    print("\n" + "=" * 60)
    print("📚 Read README.md for more information")
    print("=" * 60 + "\n")


def main():
    """Main setup function"""
    
    print("\n" + "=" * 60)
    print("🚀 AI ASSISTANT PROJECT SETUP")
    print("=" * 60 + "\n")
    
    # Check if running in correct directory
    if os.path.exists("main.py") and os.path.exists("config"):
        response = input("⚠️  Project files already exist. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled.")
            return
    
    try:
        create_directory_structure()
        create_requirements_txt()
        create_env_file()
        create_gitignore()
        create_personality_config()
        create_behavior_rules()
        create_settings()
        create_readme()
        create_main_template()
        
        print_next_steps()
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())