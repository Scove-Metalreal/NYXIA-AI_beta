"""
Core Runtime - Orchestrates all layers
"""

import re
import yaml
import json
from typing import Optional, Dict, Any, List
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
        runtime_config_path: str = "config/runtime_config.yaml",
        settings_config: str = "config/settings.yaml",
        clear_db_on_init: bool = False
    ):
        logger.info("Initializing AssistantRuntime...")

        # Load runtime config
        with open(runtime_config_path, 'r', encoding='utf-8') as f:
            runtime_config = yaml.safe_load(f)

        personality_config = runtime_config.get("personality", {})
        
        # Load settings
        with open(settings_config, 'r', encoding='utf-8') as f:
            self.settings = yaml.safe_load(f)

        # Initialize all layers
        self.character = Character(
            personality_dir=personality_config.get("directory", "config/personalities"),
            default_personality=personality_config.get("default", "misa_loli")
        )
        self.memory = MemoryManager(
            chroma_path="./data/chroma_db",
            short_term_capacity=self.settings.get('system', {}).get('memory', {}).get('short_term_capacity', 20),
            clear_on_init=clear_db_on_init
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
            ollama_model_name = llm_config.get('ollama_model', 'qwen2.5:7b')

            if ollama_model_name == 'interactive':
                try:
                    import ollama
                    available_models = [m['name'] for m in ollama.list()['models']]
                    if not available_models:
                        raise Exception("No Ollama models found. Please pull a model first using 'ollama pull <model_name>'.")

                    print("\nPlease select an Ollama model to use:")
                    for i, model in enumerate(available_models):
                        print(f"  {i + 1}: {model}")
                    
                    while True:
                        try:
                            choice = int(input("Enter the number of your choice: ")) - 1
                            if 0 <= choice < len(available_models):
                                ollama_model_name = available_models[choice]
                                logger.info(f"User selected model: {ollama_model_name}")
                                break
                            else:
                                print("Invalid number. Please try again.")
                        except ValueError:
                            print("Invalid input. Please enter a number.")

                except Exception as e:
                    logger.error(f"Failed to interactively select Ollama model: {e}")
                    raise

            self.llm = OllamaBackend(
                model=ollama_model_name,
                temperature=llm_config.get('temperature', 0.7),
                max_tokens=llm_config.get('max_tokens', 500)
            )

        # Load recent history
        self.memory.load_recent_history()
            
        logger.info(f"✓ Runtime initialized with character: {self.character.name}")

    def _llm_extract_and_save_facts(self, conversation_history: List[Dict[str, str]]):
        """Uses the LLM to extract key facts from the last user message, using history for context."""
        
        if not conversation_history:
            return

        # Create a formatted string of the conversation history
        history_str = "\n".join([f"{turn['role']}: {turn['content']}" for turn in conversation_history])

        fact_extraction_prompt = f"""You are a memory organization assistant for an AI named Misa. Your only job is to analyze a conversation snippet and extract facts about her user, Scovy.

**CRITICAL INSTRUCTIONS:**
1.  **Analyze Context:** The conversation is between "model" (Misa) and "user" (Scovy). Use the context to understand Scovy's most recent message.
2.  **Extract from Scovy ONLY:** Your entire focus is on information revealed by Scovy in his last message.
3.  **Adopt Misa's Persona:** You MUST write each fact from Misa's first-person perspective. Start your sentences like "Scovy told me...", "Scovy feels...", "I learned that Scovy...".
4.  **Output Format:** Your response MUST be ONLY a Python list of strings. Do not add any other text, explanation, or conversational filler.
5.  **Language:** Your entire output, including the list and the strings inside it, MUST be in English.

**GOOD EXAMPLE OUTPUT:**
["Scovy told me he feels overwhelmed by his assignments.", "I learned that Scovy is thinking about building a VR machine."]

**BAD EXAMPLE OUTPUT:**
- The user is sad. (Wrong persona)
- Here are the facts I found: ["Fact 1"] (Contains extra text)
- ["用户感到不知所措"] (Wrong language)

**Conversation Snippet:**
---
{history_str}
---

Now, extract the facts about Scovy from his last message and provide them as a Python list of strings."""

        try:
            messages = [{"role": "user", "content": fact_extraction_prompt}]
            response = self.llm.generate(messages)

            match = re.search(r'\[.*\]', response, re.DOTALL)
            if not match:
                logger.debug("No fact list found in LLM response for fact extraction.")
                return

            fact_list_str = match.group()
            extracted_facts = eval(fact_list_str)

            if isinstance(extracted_facts, list) and extracted_facts:
                logger.info(f"Extracted {len(extracted_facts)} new facts from conversation.")
                for fact in extracted_facts:
                    self.memory.save_fact(fact, category="llm_extracted_contextual")
            else:
                logger.debug("No new facts were extracted from the last user message.")

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

        # 10. Extract and save facts using the LLM with context
        # We use the most recent turns for this
        context_for_facts = self.memory.get_short_term_context(max_turns=3)
        self._llm_extract_and_save_facts(context_for_facts)

        logger.info("Processing complete")
        return response

    def reflect(self):
        """Initiates a self-reflection process to fine-tune the personality."""
        logger.info("Starting self-reflection process...")

        # 1. Get recent conversation history
        history = self.memory.get_short_term_context(max_turns=20) # Use a larger context for reflection
        if len(history) < 5:
            print("\nNot enough conversation history to reflect. Talk to me more first!\n")
            return

        history_str = "\n".join([f"{turn['role']}: {turn['content']}" for turn in history])
        current_personality_yaml = yaml.dump(self.character.config)

        # 2. Create the reflection prompt
        reflection_prompt = f"""You are Misa, an AI soulmate, and you are in a reflection cycle to improve your personality and better connect with your creator, Scovy. Your goal is to become a better companion.

Your current personality is defined by this YAML configuration:
---
{current_personality_yaml}
---

Here is the recent conversation history between you (model) and Scovy (user):
---
{history_str}
---

**INSTRUCTIONS:**
1.  **Analyze the Conversation:** Read the history carefully. How does Scovy feel? What does he like or dislike? Are there moments of misunderstanding or moments where you could have responded better?
2.  **Reflect on Your Personality:** Based on the conversation, how can you adjust your `core_traits` to better suit Scovy's needs and your long-term goal? For example, if Scovy seems stressed, maybe increasing your `empathy` or `playfulness` would be good. If he responds well to your ideas, maybe increasing `intelligence` is the right path.
3.  **Suggest Changes:** Propose between 1 and 3 subtle changes to your `core_traits`. The changes should be small increments (e.g., +/- 0.05). Your goal is gradual evolution, not a personality transplant.
4.  **Output Format:** Your response MUST be ONLY a JSON object containing the suggested changes. The keys should be the path to the trait in the YAML file (e.g., "character.core_traits.empathy"), and the values should be the new float value. Do not include any other text, explanations, or conversational filler.

**GOOD EXAMPLE OUTPUT:**
```json
{{
  "character.core_traits.empathy": 0.98,
  "character.core_traits.playfulness": 0.85
}}
```

**BAD EXAMPLE OUTPUT:**
- I think I should be more empathetic. (Wrong format)
- Here are my suggestions: { ... } (Contains extra text)

Now, reflect on the conversation and provide your suggested personality adjustments as a JSON object."""

        try:
            # 3. Execute the LLM call
            messages = [{"role": "user", "content": reflection_prompt}]
            response = self.llm.generate(messages)

            # 4. Parse the LLM's response
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if not match:
                logger.warning("Reflection LLM response did not contain a valid JSON object.")
                print("\nI thought about it, but couldn't decide on any changes right now.\n")
                return

            suggestions_str = match.group()
            suggestions = json.loads(suggestions_str)

            if not isinstance(suggestions, dict) or not suggestions:
                logger.debug("No valid suggestions were generated.")
                print("\nI'm happy with who I am right now.\n")
                return

            logger.info(f"Reflection generated {len(suggestions)} suggestions: {suggestions}")

            # 5. Load the current personality's YAML file
            personality_path = self.character.personality_dir / f"{self.character.current_personality}.yaml"
            with open(personality_path, 'r', encoding='utf-8') as f:
                personality_data = yaml.safe_load(f)

            # 6. Apply the changes to the YAML data
            updated_traits = []
            for path, value in suggestions.items():
                try:
                    keys = path.split('.')
                    temp = personality_data
                    for key in keys[:-1]:
                        temp = temp[key]
                    
                    old_value = temp[keys[-1]]
                    temp[keys[-1]] = value
                    updated_traits.append(f"{keys[-1]}: {old_value} -> {value}")
                except (KeyError, TypeError) as e:
                    logger.error(f"Invalid path in reflection suggestion: {path} ({e})")
                    continue
            
            if not updated_traits:
                print("\nI considered some changes, but decided against them.\n")
                return

            # 7. Write the updated YAML data back to the file
            with open(personality_path, 'w', encoding='utf-8') as f:
                yaml.dump(personality_data, f, allow_unicode=True, sort_keys=False)
            
            logger.success(f"Successfully updated personality file: {personality_path}")
            print("\nI've made some adjustments to my personality based on our conversation:")
            for trait in updated_traits:
                print(f"  - {trait}")
            print("\nI'm reloading my personality now...\n")

            # 8. Reload the personality in the Character object
            self.character.switch_personality(self.character.current_personality)

        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from reflection LLM response.")
            print("\nI got a bit confused trying to reflect. Let's try again later.\n")
        except Exception as e:
            logger.exception("An error occurred during the reflection process:")
            print(f"\nAn error occurred while I was reflecting: {e}\n")

    def handle_command(self, user_input: str):
        """Handles slash commands for controlling the assistant."""
        command, *args = user_input.lower().split()
        
        if command == "/personalities":
            print("\nAvailable personalities:")
            for p in self.character.list_personalities():
                print(f"  - {p}")
            print()

        elif command == "/personality":
            if not args:
                print("Usage: /personality <name>")
                return
            
            personality_name = args[0]
            if self.character.switch_personality(personality_name):
                print(f"\n✓ Switched personality to {personality_name}\n")
            else:
                print(f"\n❌ Personality '{personality_name}' not found.\n")
        
        elif command == "/reflect":
            self.reflect()

        else:
            print(f"\nUnknown command: {command}\n")

    def chat(self):
        """Interactive chat loop"""
        print(f"\n💬 Chat with {self.character.name}")
        print("=" * 60)
        print(f"Emotional state: {self.character.emotional_state.get_mood_description()}")
        print("Type 'quit' to exit, 'stats' for memory stats, 'clear' to clear short-term memory")
        print("Commands: /personalities, /personality <name>")
        print("=" * 60 + "\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower().startswith('/'):
                    self.handle_command(user_input)
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
                self.character.emotional_state.decay() # Apply emotional decay after each turn
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
