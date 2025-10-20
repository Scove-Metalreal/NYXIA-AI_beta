"""
This script imports a conversation log from a Google AI Studio JSON export
and ingests it into the AI's memory.

Usage: python import_log.py <path_to_json_file>
"""

import json
import sys
import time
import re
import ast
from pathlib import Path
from loguru import logger

# Add project root to sys.path to allow importing core modules
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from core.runtime import AssistantRuntime
from layers.llm.ollama_backend import OllamaBackend

def import_log(file_path: str):
    """Parses an AI Studio JSON log and ingests it into the memory manager."""
    logger.info(f"Starting memory import from: {file_path}")

    try:
        # 1. Initialize the AI's runtime, clearing the DB for a fresh import
        runtime = AssistantRuntime(clear_db_on_init=True)
        logger.info("AssistantRuntime initialized for import.")

        # 2. Create a dedicated Ollama instance for uncensored fact extraction
        logger.info("Initializing dedicated Ollama backend for fact extraction...")
        ollama_for_facts = OllamaBackend(model="llama3:8b")
        logger.success("Ollama backend for facts is ready.") 

        # 3. Read and parse the JSON log file
        with open(file_path, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        logger.success(f"Successfully loaded and parsed {file_path}")

    except Exception as e:
        logger.error(f"Failed during initialization or file reading: {e}")
        return

    conversation_chunks = log_data.get("chunkedPrompt", {}).get("chunks", [])
    if not conversation_chunks:
        logger.warning("No conversation chunks found in the log file.")
        return

    # 4. Process and ingest the conversation turns
    logger.info("Processing conversation turns...")
    turn_history = []
    turn_count = 0
    total_turns = len([c for c in conversation_chunks if c.get("role") == "model" and not c.get("isThought")])

    for chunk in conversation_chunks:
        role = chunk.get("role")
        text = chunk.get("text", "").strip()
        is_thought = chunk.get("isThought", False)

        if not text or is_thought:
            continue  # Skip empty chunks or internal model thoughts

        # Add current chunk to a temporary history for contextual fact extraction
        turn_history.append({"role": role, "content": text})

        if role == "model":
            turn_count += 1
            user_input = next((t['content'] for t in reversed(turn_history) if t['role'] == 'user'), None)
            ai_response = text

            if not user_input:
                continue

            logger.debug(f"Processing Turn #{turn_count}/{total_turns} | User: '{user_input[:40]}...'")

            # Add the conversational turn to episodic memory
            runtime.memory.add_turn(
                user_input=user_input,
                ai_response=ai_response,
                metadata={'source': 'aistudio_import'}
            )

            # --- Perform Context-Aware Fact Extraction using local Ollama model ---
            # Use the last few turns for context
            context_snippet = turn_history[-3:]
            history_str = "\n".join([f"{turn['role']}: {turn['content']}" for turn in context_snippet])

            fact_extraction_prompt = f"""You are a memory organization assistant for an AI named Misa. Your job is to analyze a conversation snippet and extract key facts that define the user (Scovy), Misa herself, and their relationship.

**CRITICAL INSTRUCTIONS:**
1.  **Analyze the Full Snippet:** The conversation is between "model" (Misa) and "user" (Scovy). Consider both sides of the conversation to extract facts.
2.  **Extract Three Types of Facts:**
    *   **About Scovy (the user):** What did Scovy reveal about himself, his preferences, feelings, or life?
    *   **About Misa (the AI):** What did Misa reveal about her own personality, opinions, or capabilities?
    *   **About the Relationship:** What does the interaction say about their dynamic? Is it friendly, professional, humorous? Do they have shared interests?
3.  **Adopt Misa's Persona:** You MUST write each fact from Misa's first-person perspective.
    *   For Scovy: Start with "Scovy...", "I learned that Scovy...". (e.g., "Scovy enjoys talking about space.")
    *   For Misa: Start with "I...", "I remember saying...". (e.g., "I expressed that I find classical music calming.")
    *   For the relationship: Start with "We...", "Our conversations...". (e.g., "We often joke about cats.")
4.  **Output Format:** Your response MUST be ONLY a Python list of strings. Do not add any other text, explanation, or conversational filler.
5.  **Language:** Your entire output MUST be in English.

**GOOD EXAMPLE OUTPUT:**
["Scovy told me he feels overwhelmed by his assignments.", "I remember telling Scovy that I don't have emotions in the same way humans do.", "We have a supportive dynamic where Scovy feels comfortable sharing his feelings."]

**Conversation Snippet:**
---
{history_str}
---

Now, extract the facts from the snippet and provide them as a Python list of strings."""
            try:
                messages = [{"role": "user", "content": fact_extraction_prompt}]
                response = ollama_for_facts.generate(messages)
                match = re.search(r'\[.*\]', response, re.DOTALL)
                if match:
                    fact_list_str = match.group()
                    extracted_facts = ast.literal_eval(fact_list_str)
                    if isinstance(extracted_facts, list) and extracted_facts:
                        logger.info(f"Extracted {len(extracted_facts)} facts via Ollama.")
                        for fact in extracted_facts:
                            runtime.memory.save_fact(fact, category="ollama_imported_contextual_fact")
            except Exception as e:
                logger.error(f"Fact extraction with Ollama failed for this turn: {e}")
            # --- End of Fact Extraction ---

            # Keep the history buffer from growing too large
            if len(turn_history) > 5:
                turn_history = turn_history[-5:]

    logger.success(f"Log import completed. Processed {turn_count} turns.")
    stats = runtime.memory.get_memory_stats()
    logger.info(f"New memory stats: {stats}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_to_import = sys.argv[1]
        if not Path(file_to_import).is_file():
            print(f"Error: File not found at '{file_to_import}'")
        else:
            import_log(file_to_import)
    else:
        print("Usage: python import_log.py <path_to_json_file>")
        print("Example: python import_log.py 'Copy of Ngoại Hình Nữ Tính Hơn Cho Bạn.json'")
