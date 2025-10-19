"""
LLM Layer - Ollama Backend
"""

import ollama
from typing import List, Dict, Any
from loguru import logger
import os


class OllamaBackend:
    """Backend for Ollama"""
    
    def __init__(
        self,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ):
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        self._verify_model()
        logger.info(f"Ollama backend initialized with model: {self.model}")
    
    def _verify_model(self):
        """Verifies that the model is available."""
        try:
            models = ollama.list()
            available = [m['name'] for m in models['models']]
            
            if self.model not in available:
                logger.warning(f"Model {self.model} not found in: {available}")
                raise Exception(f"Model not found. Run: ollama pull {self.model}")
            
            logger.info(f"Model {self.model} verified")
        except Exception as e:
            logger.error(f"Model verification failed: {e}")
            raise
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False
    ) -> str:
        """Generates a response from Ollama."""
        try:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                stream=stream,
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                    "num_gpu": 999,
                }
            )
            
            if stream:
                return self._handle_stream(response)
            else:
                return response['message']['content']
                
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return "Sorry, I encountered an error while processing. Could you please try again?"
    
    def _handle_stream(self, response) -> str:
        """Handles a streaming response."""
        full_response = ""
        try:
            for chunk in response:
                content = chunk['message']['content']
                full_response += content
                print(content, end='', flush=True)
            print()
        except Exception as e:
            logger.error(f"Streaming error: {e}")
        
        return full_response
