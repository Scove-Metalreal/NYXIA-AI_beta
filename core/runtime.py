"""
Core Runtime - Orchestrates all layers
"""

import re
import yaml
from typing import Optional, Dict, Any
from loguru import logger
from langdetect import detect
from layers.personality.character import Character
from layers.memory.memory_manager import MemoryManager
from layers.reasoning.context_builder import ContextBuilder, DecisionEngine, BehaviorRules
from layers.llm.ollama_backend import OllamaBackend
from layers.llm.gemini_backend import GeminiBackend


class AssistantRuntime:
    """Main runtime that ties all layers together"""
    
    def __init__(
        self,
        personality_config: str = "config/personality.yaml",
        settings_config: str = "config/settings.yaml"
    ):
        logger.info("Initializing AssistantRuntime...")
        
        # Load settings
        with open(settings_config, 'r', encoding='utf-8') as f:
            self.settings = yaml.safe_load(f)

        # Initialize all layers
        self.character = Character(personality_config)
        self.memory = MemoryManager(
            chroma_path="./data/chroma_db",
            short_term_capacity=self.settings.get('system', {}).get('memory', {}).get('short_term_capacity', 20)
        )
        self.context_builder = ContextBuilder()
        self.decision_engine = DecisionEngine()
        self.behavior_rules = BehaviorRules()
        
        # Dynamically load the LLM backend
        llm_config = self.settings.get('system', {}).get('llm', {})
        logger.debug(f"LLM backend from settings: {llm_config.get('backend')}")
        if llm_config.get('backend') == 'gemini':
            logger.info("Using Gemini backend.")
            self.llm = GeminiBackend(
                model=llm_config.get('gemini_model', 'gemini-pro'),
                temperature=llm_config.get('temperature', 0.7),
                max_tokens=llm_config.get('max_tokens', 1000)
            )
        else:
            logger.info("Using Ollama backend.")
            self.llm = OllamaBackend(
                model=llm_config.get('ollama_model', 'qwen2.5:7b'),
                temperature=llm_config.get('temperature', 0.7),
                max_tokens=llm_config.get('max_tokens', 500)
            )

        # Load recent history
        self.memory.load_recent_history()
            
        logger.info(f"✓ Runtime initialized with character: {self.character.name}")

    def _llm_extract_and_save_facts(self, user_input: str):
        """Uses the LLM to extract key facts from user input and save them."""
        fact_extraction_prompt = f"""Analyze the following statement from a user. Extract any key facts or pieces of information about the user (e.g., their name, preferences, personal details, important events).

If you find one or more facts, list them as a Python list of strings. Each string should be a concise, third-person statement about the user (e.g., "The user's favorite color is blue.", "The user works as a software engineer.").

If no significant facts are found, respond with an empty list: [].

User statement: "{user_input}""" 

        try:
            # Use the 'user' role for a direct instruction
            messages = [{"role": "user", "content": fact_extraction_prompt}]
            response = self.llm.generate(messages)

            # Use regex to find the list within the response
            match = re.search(r'\[.*\]', response, re.DOTALL)
            if not match:
                logger.debug("No fact list found in LLM response.")
                return

            fact_list_str = match.group()
            
            # Safely evaluate the string to a Python list
            extracted_facts = eval(fact_list_str)

            if isinstance(extracted_facts, list) and extracted_facts:
                logger.info(f"Extracted {len(extracted_facts)} facts from user input.")
                for fact in extracted_facts:
                    self.memory.save_fact(fact, category="llm_extracted")
            else:
                logger.debug("No facts were extracted from user input.")

        except Exception as e:
            logger.error(f"Failed to extract facts with LLM: {e}")

    def process_input(self, user_input: str) -> str:
        """Main processing pipeline"""
        logger.info(f"Processing user input: {user_input[:50]}...")

        # 1. Detect language
        try:
            lang = detect(user_input)
            logger.debug(f"Detected language: {lang}")
        except:
            lang = 'en' # Default to English if detection fails
            logger.warning("Language detection failed, defaulting to English.")

        # 2. Analyze user emotion
        user_emotion = self.decision_engine.analyze_user_emotion(user_input)
        logger.debug(f"User emotion: {user_emotion}")

        # 3. Update character's emotional state
        self.character.update_emotion_from_user_input(
                user_input,
                sentiment=user_emotion['sentiment']
            )
            
        # 4. Retrieve relevant memories
        retrieved_memories = self.memory.retrieve_relevant_memories(
            query=user_input,
            n_results=5
        )

        # 5. Get short-term conversation history
        short_term_history = self.memory.get_short_term_context(max_turns=5)

        # 6. Build context for LLM
        personality_prompt = self.character.get_system_prompt(language=lang)
        response_tone = self.character.get_response_tone()

        messages = self.context_builder.build_llm_context(
            personality_prompt=personality_prompt,
            user_input=user_input,
            short_term_history=short_term_history,
            retrieved_memories=retrieved_memories,
            emotional_state=self.character.emotional_state.to_dict(),
            response_tone=response_tone
        )
            
        # 7. Generate response
        max_retries = 3
        for attempt in range(max_retries):
            response = self.llm.generate(messages)

            # 8. Validate response
            is_valid, error = self.behavior_rules.validate_response(response)

            if is_valid:
                self.behavior_rules.track_response(response)
                break
            else:
                logger.warning(f"Invalid response (attempt {attempt + 1}): {error}")
                if attempt == max_retries - 1:
                    response = "Well... I'm thinking about what to say now 🤔"

        # 9. Save to memory
        self.memory.add_turn(
            user_input=user_input,
            ai_response=response,
            metadata={
                'user_emotion': user_emotion,
                'ai_emotion': self.character.emotional_state.to_dict()
            }
        )

        # 10. Extract and save facts using the LLM
        self._llm_extract_and_save_facts(user_input)

        logger.info("Processing complete")
        return response

    def chat(self):
        """Interactive chat loop"""
        print(f"\n💬 Chat with {self.character.name}")
        print("=" * 60)
        print(f"Emotional state: {self.character.emotional_state.get_mood_description()}")
        print("Type 'quit' to exit, 'stats' for memory stats, 'clear' to clear short-term memory")
        print("=" * 60 + "\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == 'quit':
                    print(f"\n👋 {self.character.name}: See you later!")
                    break

                if user_input.lower() == 'stats':
                    stats = self.memory.get_memory_stats()
                    print(f"\n📊 Memory Stats:")
                    print(f"  Short-term: {stats['short_term_size']} turns")
                    print(f"  Episodic: {stats['episodic_count']} memories")
                    print(f"  Semantic: {stats['semantic_count']} facts")
                    print(f"  Emotional state: {self.character.emotional_state.to_dict()}\n")
                    continue

                if user_input.lower() == 'clear':
                    self.memory.clear_short_term()
                    print("✓ Short-term memory cleared\n")
                    continue

                # Process input
                response = self.process_input(user_input)
                print(f"\n{self.character.name}: {response}\n")

            except KeyboardInterrupt:
                print(f"\n\n👋 {self.character.name}: See you later!")
                break
            except Exception as e:
                logger.exception("Error in chat loop:")
                print(f"\n❌ Error: {e}\n")

    def get_stats(self) -> Dict[str, Any]:
        """Get runtime statistics"""
        return {
            "character": {
                "name": self.character.name,
                "emotional_state": self.character.emotional_state.to_dict()
            },
            "memory": self.memory.get_memory_stats()
        }
