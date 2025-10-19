"""
Core Runtime - Orchestrates all layers
"""

from typing import Optional, Dict, Any
from loguru import logger
from layers.personality.character import Character
from layers.memory.memory_manager import MemoryManager
from layers.reasoning.context_builder import ContextBuilder, DecisionEngine, BehaviorRules
from layers.llm.ollama_backend import OllamaBackend


class AssistantRuntime:
    """Main runtime that ties all layers together"""
    
    def __init__(
        self,
        personality_config: str = "config/personality.yaml",
        settings_config: str = "config/settings.yaml"
    ):
        logger.info("Initializing AssistantRuntime...")
        
        # Initialize all layers
        self.character = Character(personality_config)
        self.memory = MemoryManager(
            chroma_path="./data/chroma_db",
            short_term_capacity=20
        )
        self.context_builder = ContextBuilder()
        self.decision_engine = DecisionEngine()
        self.behavior_rules = BehaviorRules()
        self.llm = OllamaBackend()
            
        logger.info(f"✓ Runtime initialized with character: {self.character.name}")

    def process_input(self, user_input: str) -> str:
        """Main processing pipeline"""
        logger.info(f"Processing user input: {user_input[:50]}...")

        # 1. Analyze user emotion
        user_emotion = self.decision_engine.analyze_user_emotion(user_input)
        logger.debug(f"User emotion: {user_emotion}")

        # 2. Update character's emotional state
        self.character.update_emotion_from_user_input(
                user_input,
                sentiment=user_emotion['sentiment']
            )

        # 3. Extract and save important facts
        self.memory.extract_and_save_facts(user_input)
            
        # 4. Retrieve relevant memories
        retrieved_memories = self.memory.retrieve_relevant_memories(
            query=user_input,
            n_results=5
        )

        # 5. Get short-term conversation history
        short_term_history = self.memory.get_short_term_context(max_turns=5)

        # 6. Build context for LLM
        personality_prompt = self.character.get_system_prompt()
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
                    response = "Ừm... tôi đang nghĩ xem nên nói gì đây 🤔"

        # 9. Save to memory
        self.memory.add_turn(
            user_input=user_input,
            ai_response=response,
            metadata={
                'user_emotion': user_emotion,
                'ai_emotion': self.character.emotional_state.to_dict()
            }
        )

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
                    print(f"\n👋 {self.character.name}: Hẹn gặp lại bạn nhé!")
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
                print(f"\n\n👋 {self.character.name}: Hẹn gặp lại bạn nhé!")
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
