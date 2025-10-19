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
        gemini_messages = []
        system_prompt = ""
        for msg in messages:
            if msg['role'] == 'system':
                system_prompt = msg['content']
                continue
            
            role = 'model' if msg['role'] == 'assistant' else msg['role']
            gemini_messages.append({'role': role, 'parts': [msg['content']]})

        try:
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            if stream:
                logger.warning("Streaming is not yet implemented for the Gemini backend.")

            response = self.model.generate_content(
                contents=gemini_messages,
                generation_config=generation_config,
                # The system instruction can be passed here if needed
            )
            
            # Check for blocked response before accessing .text
            if not response.candidates or response.candidates[0].finish_reason == 'SAFETY':
                logger.warning(f"Gemini response was blocked. Finish Reason: {response.candidates[0].finish_reason if response.candidates else 'N/A'}. Ratings: {response.candidates[0].safety_ratings if response.candidates else 'N/A'}")
                return "[SAFETY_BLOCKED]"

            return response.text
                
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return "Sorry, I encountered an error while processing with the Gemini API."
