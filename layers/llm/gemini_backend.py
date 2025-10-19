"""
LLM Layer - Gemini Backend
"""

import os
import google.generativeai as genai
from typing import List, Dict, Any
from loguru import logger

class GeminiBackend:
    """Backend for Google Gemini API"""
    
    def __init__(
        self,
        model: str = "gemini-1.5-pro-latest",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        self.model_name = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        
        self._configure_client()
        logger.info(f"Gemini backend initialized with model: {self.model_name}")

    def _configure_client(self):
        """Configures the Google AI client."""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            logger.error(f"Failed to configure Gemini client: {e}")
            raise

    def generate(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False
    ) -> str:
        """Generates a response from the Gemini model."""
        # Gemini uses a different message format, so we need to adapt it.
        # It expects a list of dictionaries with 'role' and 'parts'.
        # The roles are 'user' and 'model'.
        gemini_messages = []
        system_prompt = ""
        for msg in messages:
            if msg['role'] == 'system':
                system_prompt = msg['content']
                continue # System prompt is handled separately in Gemini
            
            # Replace 'assistant' with 'model' for the role
            role = 'model' if msg['role'] == 'assistant' else msg['role']
            gemini_messages.append({'role': role, 'parts': [msg['content']]})

        try:
            # The system prompt is passed separately in the new API
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            if stream:
                # Streaming is handled differently and would require a different implementation
                # For now, we will use the non-streaming version for simplicity.
                logger.warning("Streaming is not yet implemented for the Gemini backend.")

            response = self.model.generate_content(
                contents=gemini_messages,
                generation_config=generation_config,
                # The system instruction can be passed here if needed, though it's often part of the initial messages
            )
            
            return response.text
                
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return "Sorry, I encountered an error while processing with the Gemini API."
