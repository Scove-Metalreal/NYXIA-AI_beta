#!/usr/bin/env python3
"""
AI Assistant - Main Entry Point
Multi-layer architecture with personality and memory
"""

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
    """Main function"""
    print("=" * 60)
    print("🤖 AI ASSISTANT - Multi-Layer Architecture")
    print("=" * 60)
    
    logger.info("Starting AI Assistant...")
    
    try:
        from core.runtime import AssistantRuntime

        # Initialize runtime
        runtime = AssistantRuntime(runtime_config_path="config/runtime_config.yaml")

        # Start interactive chat
        runtime.chat()
    except Exception as e:
        logger.exception("Failed to start runtime:")
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. Ollama is running: ollama serve")
        print("2. Model is pulled: ollama pull qwen2.5:7b")
        print("3. All dependencies installed: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        logger.exception("Fatal error:")
        sys.exit(1)
