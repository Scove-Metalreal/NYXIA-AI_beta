#!/usr/bin/env python3
"""
Script để tạo tất cả các file Python cần thiết
Chạy sau khi setup_project.py
"""

import os
from pathlib import Path


def create_personality_character():
    """Tạo layers/personality/character.py"""
    content = '''"""
Personality Layer - Character & Emotion System
Load personality từ YAML và quản lý emotional state
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class EmotionalState:
    """Trạng thái cảm xúc hiện tại"""
    mood: float = 70.0  # 0-100: happiness level
    energy: float = 80.0  # 0-100: energy level
    affection: float = 50.0  # 0-100: closeness to user
    stress: float = 20.0  # 0-100: stress level
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "mood": self.mood,
            "energy": self.energy,
            "affection": self.affection,
            "stress": self.stress
        }
    
    def get_mood_description(self) -> str:
        """Mô tả mood hiện tại"""
        if self.mood >= 80:
            return "vui vẻ"
        elif self.mood >= 60:
            return "bình thường"
        elif self.mood >= 40:
            return "hơi buồn"
        else:
            return "buồn"
    
    def update(self, mood_delta=0, energy_delta=0, affection_delta=0, stress_delta=0):
        """Cập nhật trạng thái cảm xúc"""
        self.mood = max(0, min(100, self.mood + mood_delta))
        self.energy = max(0, min(100, self.energy + energy_delta))
        self.affection = max(0, min(100, self.affection + affection_delta))
        self.stress = max(0, min(100, self.stress + stress_delta))


class Character:
    """
    Character/Personality System
    Load từ YAML và quản lý personality + emotions
    """
    
    def __init__(self, config_path: str = "config/personality.yaml"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.emotional_state = EmotionalState()
        
        self._load_config()
        self._initialize_emotional_state()
        
        logger.info(f"Character '{self.name}' initialized")
    
    def _load_config(self):
        """Load personality config từ YAML"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.debug(f"Loaded personality config from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load personality config: {e}")
            self.config = self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default personality nếu không load được YAML"""
        return {
            "character": {
                "name": "Mira",
                "core_traits": {
                    "kindness": 0.9,
                    "humor": 0.7,
                    "empathy": 0.9
                },
                "speaking_style": {
                    "formality": "casual",
                    "language": "vietnamese"
                },
                "description": "AI companion thân thiện",
                "emotional_system": {
                    "initial_state": {
                        "mood": 70,
                        "energy": 80,
                        "affection": 50,
                        "stress": 20
                    }
                }
            }
        }
    
    def _initialize_emotional_state(self):
        """Khởi tạo emotional state từ config"""
        try:
            initial = self.config["character"]["emotional_system"]["initial_state"]
            self.emotional_state = EmotionalState(
                mood=initial.get("mood", 70),
                energy=initial.get("energy", 80),
                affection=initial.get("affection", 50),
                stress=initial.get("stress", 20)
            )
        except KeyError:
            logger.warning("Using default emotional state")
    
    @property
    def name(self) -> str:
        return self.config.get("character", {}).get("name", "Mira")
    
    @property
    def description(self) -> str:
        return self.config.get("character", {}).get("description", "")
    
    @property
    def core_traits(self) -> Dict[str, float]:
        return self.config.get("character", {}).get("core_traits", {})
    
    @property
    def speaking_style(self) -> Dict[str, Any]:
        return self.config.get("character", {}).get("speaking_style", {})
    
    def get_system_prompt(self) -> str:
        """Tạo system prompt dựa trên personality"""
        traits_str = ", ".join([
            f"{trait}: {value}"
            for trait, value in self.core_traits.items()
        ])
        
        mood_desc = self.emotional_state.get_mood_description()
        
        prompt = f"""Bạn là {self.name}, một AI companion với các đặc điểm:

Tính cách: {traits_str}
Trạng thái hiện tại: {mood_desc}
Mức độ thân thiết với user: {self.emotional_state.affection:.0f}/100

{self.description}

Phong cách giao tiếp:
- Ngôn ngữ: {self.speaking_style.get('language', 'vietnamese')}
- Mức độ trang trọng: {self.speaking_style.get('formality', 'casual')}

Hãy trả lời một cách tự nhiên, phù hợp với tính cách và trạng thái cảm xúc hiện tại."""
        
        return prompt
    
    def update_emotion_from_user_input(self, user_input: str, sentiment: float = 0.0):
        """Cập nhật cảm xúc dựa trên input của user"""
        mood_change = sentiment * 5
        
        affection_change = 0
        personal_keywords = ['tên tôi', 'tôi là', 'cảm thấy', 'thích', 'không thích']
        if any(kw in user_input.lower() for kw in personal_keywords):
            affection_change = 1
        
        self.emotional_state.update(
            mood_delta=mood_change,
            affection_delta=affection_change
        )
        
        logger.debug(f"Emotional state updated: {self.emotional_state.to_dict()}")
    
    def get_response_tone(self) -> str:
        """Xác định tone của response"""
        if self.emotional_state.mood >= 80:
            return "enthusiastic and cheerful"
        elif self.emotional_state.mood >= 60:
            return "warm and friendly"
        elif self.emotional_state.mood >= 40:
            return "gentle and supportive"
        else:
            return "soft and caring"
'''
    
    Path("layers/personality").mkdir(parents=True, exist_ok=True)
    with open("layers/personality/character.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ layers/personality/character.py")


def create_memory_manager():
    """Tạo layers/memory/memory_manager.py"""
    content = '''"""
Memory Layer - Short-term & Long-term Memory Management
"""

import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from loguru import logger


@dataclass
class ConversationTurn:
    """Một turn trong hội thoại"""
    user_input: str
    ai_response: str
    timestamp: float
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user": self.user_input,
            "ai": self.ai_response,
            "timestamp": self.timestamp,
            "metadata": self.metadata or {}
        }


class MemoryManager:
    """Quản lý cả short-term và long-term memory"""
    
    def __init__(
        self,
        chroma_path: str = "./data/chroma_db",
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
        short_term_capacity: int = 20
    ):
        self.short_term_capacity = short_term_capacity
        self.short_term_buffer: List[ConversationTurn] = []
        
        self._init_chromadb(chroma_path)
        
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        logger.info("Embedding model loaded")
    
    def _init_chromadb(self, path: str):
        """Khởi tạo ChromaDB"""
        try:
            self.chroma_client = chromadb.PersistentClient(path=path)
            
            self.episodic_memory = self.chroma_client.get_or_create_collection(
                name="episodic_memory",
                metadata={"description": "Conversation history"}
            )
            
            self.semantic_memory = self.chroma_client.get_or_create_collection(
                name="semantic_memory",
                metadata={"description": "Facts about user"}
            )
            
            logger.info(f"ChromaDB initialized at {path}")
        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {e}")
            raise
    
    def add_turn(self, user_input: str, ai_response: str, metadata: Dict = None):
        """Thêm một conversation turn"""
        turn = ConversationTurn(
            user_input=user_input,
            ai_response=ai_response,
            timestamp=time.time(),
            metadata=metadata
        )
        
        self.short_term_buffer.append(turn)
        
        if len(self.short_term_buffer) > self.short_term_capacity:
            old_turn = self.short_term_buffer.pop(0)
            self._consolidate_to_long_term(old_turn)
        
        logger.debug(f"Turn added. Buffer size: {len(self.short_term_buffer)}")
    
    def _consolidate_to_long_term(self, turn: ConversationTurn):
        """Chuyển turn từ short-term sang long-term memory"""
        try:
            text = f"User: {turn.user_input}\\nAI: {turn.ai_response}"
            embedding = self.embedding_model.encode(text).tolist()
            importance = self._calculate_importance(turn)
            
            if importance >= 0.3:
                self.episodic_memory.add(
                    documents=[text],
                    embeddings=[embedding],
                    metadatas=[{
                        "timestamp": turn.timestamp,
                        "importance": importance,
                        "user_input": turn.user_input[:200],
                        "ai_response": turn.ai_response[:200]
                    }],
                    ids=[f"turn_{int(turn.timestamp)}"]
                )
                logger.debug(f"Turn consolidated with importance {importance:.2f}")
        except Exception as e:
            logger.error(f"Failed to consolidate turn: {e}")
    
    def _calculate_importance(self, turn: ConversationTurn) -> float:
        """Tính importance score của một turn"""
        score = 0.3
        text = turn.user_input.lower()
        
        high_keywords = ['tên tôi', 'tôi là', 'gia đình', 'công việc', 'yêu', 'ghét', 'cảm thấy']
        medium_keywords = ['thích', 'không thích', 'thường', 'hay', 'luôn']
        
        for kw in high_keywords:
            if kw in text:
                score += 0.3
        
        for kw in medium_keywords:
            if kw in text:
                score += 0.15
        
        if len(turn.user_input) > 50:
            score += 0.1
        
        return min(1.0, score)
    
    def retrieve_relevant_memories(
        self,
        query: str,
        n_results: int = 5,
        importance_threshold: float = 0.3
    ) -> List[str]:
        """Truy xuất memories liên quan đến query"""
        try:
            query_embedding = self.embedding_model.encode(query).tolist()
            
            results = self.episodic_memory.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where={"importance": {"$gte": importance_threshold}}
            )
            
            if results['documents'] and results['documents'][0]:
                logger.debug(f"Retrieved {len(results['documents'][0])} memories")
                return results['documents'][0]
            
            return []
        except Exception as e:
            logger.error(f"Memory retrieval failed: {e}")
            return []
    
    def save_fact(self, fact: str, category: str = "general"):
        """Lưu một fact về user vào semantic memory"""
        try:
            embedding = self.embedding_model.encode(fact).tolist()
            fact_id = f"fact_{int(time.time())}_{category}"
            
            self.semantic_memory.add(
                documents=[fact],
                embeddings=[embedding],
                metadatas=[{
                    "category": category,
                    "created_at": time.time()
                }],
                ids=[fact_id]
            )
            
            logger.info(f"Fact saved: {fact}")
        except Exception as e:
            logger.error(f"Failed to save fact: {e}")
    
    def get_short_term_context(self, max_turns: int = 5) -> List[Dict[str, str]]:
        """Lấy context từ short-term memory"""
        recent_turns = self.short_term_buffer[-max_turns:]
        
        messages = []
        for turn in recent_turns:
            messages.append({"role": "user", "content": turn.user_input})
            messages.append({"role": "assistant", "content": turn.ai_response})
        
        return messages
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Thống kê memory"""
        return {
            "short_term_size": len(self.short_term_buffer),
            "episodic_count": len(self.episodic_memory.get()['ids']),
            "semantic_count": len(self.semantic_memory.get()['ids'])
        }
    
    def clear_short_term(self):
        """Xóa short-term memory"""
        self.short_term_buffer.clear()
        logger.info("Short-term memory cleared")
    
    def extract_and_save_facts(self, user_input: str):
        """Tự động extract facts từ user input"""
        text = user_input.lower()
        
        if "tên tôi là" in text or "tôi là" in text:
            self.save_fact(user_input, category="personal_info")
        elif "tôi thích" in text or "tôi yêu" in text:
            self.save_fact(user_input, category="preference")
        elif "tôi không thích" in text or "tôi ghét" in text:
            self.save_fact(user_input, category="preference")
        elif "công việc" in text or "tôi làm" in text:
            self.save_fact(user_input, category="work")
'''
    
    Path("layers/memory").mkdir(parents=True, exist_ok=True)
    with open("layers/memory/memory_manager.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ layers/memory/memory_manager.py")


def create_reasoning_layer():
    """Tạo layers/reasoning/context_builder.py"""
    content = '''"""
Reasoning Layer - Context Builder & Decision Engine
"""

from typing import List, Dict, Any, Optional
from loguru import logger


class ContextBuilder:
    """Build context cho LLM"""
    
    def __init__(self):
        pass
    
    def build_llm_context(
        self,
        personality_prompt: str,
        user_input: str,
        short_term_history: List[Dict[str, str]],
        retrieved_memories: List[str],
        emotional_state: Dict[str, float],
        response_tone: str
    ) -> List[Dict[str, str]]:
        """Build full context cho LLM"""
        messages = []
        
        system_content = personality_prompt
        system_content += f"\\n\\nTrạng thái cảm xúc hiện tại của bạn:"
        system_content += f"\\n- Mood: {emotional_state.get('mood', 70):.0f}/100"
        system_content += f"\\n- Energy: {emotional_state.get('energy', 80):.0f}/100"
        system_content += f"\\n- Affection: {emotional_state.get('affection', 50):.0f}/100"
        
        if retrieved_memories:
            system_content += "\\n\\nThông tin liên quan từ ký ức:"
            for i, memory in enumerate(retrieved_memories, 1):
                system_content += f"\\n{i}. {memory}"
        
        system_content += f"\\n\\nHãy trả lời với tone: {response_tone}"
        
        messages.append({"role": "system", "content": system_content})
        messages.extend(short_term_history)
        messages.append({"role": "user", "content": user_input})
        
        logger.debug(f"Built context with {len(messages)} messages")
        return messages


class DecisionEngine:
    """Ra quyết định về hành vi của AI"""
    
    def __init__(self):
        pass
    
    def analyze_user_emotion(self, user_input: str) -> Dict[str, Any]:
        """Phân tích cảm xúc của user"""
        text = user_input.lower()
        
        positive_words = ['vui', 'hạnh phúc', 'tuyệt', 'tốt', 'thích', 'yêu']
        negative_words = ['buồn', 'tệ', 'khó chịu', 'stress', 'lo lắng', 'ghét']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            sentiment = 0.6
            emotion = "happy"
        elif negative_count > positive_count:
            sentiment = -0.6
            emotion = "sad"
        else:
            sentiment = 0.0
            emotion = "neutral"
        
        intensity_markers = ['rất', 'cực kỳ', 'quá', 'vô cùng']
        intensity = 0.8 if any(marker in text for marker in intensity_markers) else 0.5
        
        return {
            'sentiment': sentiment,
            'emotion': emotion,
            'intensity': intensity
        }


class BehaviorRules:
    """Enforce behavior rules"""
    
    def __init__(self):
        self.recent_responses = []
        self.max_history = 5
    
    def validate_response(self, response: str) -> tuple:
        """Validate response"""
        if len(response.strip()) < 5:
            return False, "Response too short"
        
        if len(response) > 1000:
            return False, "Response too long"
        
        if response in self.recent_responses:
            return False, "Repetitive response"
        
        if len(response.replace(' ', '').replace('.', '').replace(',', '')) < 3:
            return False, "No meaningful content"
        
        return True, None
    
    def track_response(self, response: str):
        """Track response"""
        self.recent_responses.append(response)
        if len(self.recent_responses) > self.max_history:
            self.recent_responses.pop(0)
'''
    
    Path("layers/reasoning").mkdir(parents=True, exist_ok=True)
    with open("layers/reasoning/context_builder.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ layers/reasoning/context_builder.py")


def create_ollama_backend():
    """Tạo layers/llm/ollama_backend.py"""
    content = '''"""
LLM Layer - Ollama Backend
"""

import ollama
from typing import List, Dict, Any
from loguru import logger
import os


class OllamaBackend:
    """Backend cho Ollama"""
    
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
        """Kiểm tra model có sẵn không"""
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
        """Generate response từ Ollama"""
        try:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                stream=stream,
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                }
            )
            
            if stream:
                return self._handle_stream(response)
            else:
                return response['message']['content']
                
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return "Xin lỗi, tôi gặp lỗi khi xử lý. Bạn thử lại được không?"
    
    def _handle_stream(self, response) -> str:
        """Handle streaming response"""
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
'''
    
    Path("layers/llm").mkdir(parents=True, exist_ok=True)
    with open("layers/llm/ollama_backend.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ layers/llm/ollama_backend.py")


def create_runtime():
    """Tạo core/runtime.py"""
    content = '''"""
Core Runtime - Orchestration của toàn bộ AI Assistant
"""

import os
from typing import Dict, Any
from loguru import logger
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from layers.personality.character import Character
from layers.memory.memory_manager import MemoryManager
from layers.reasoning.context_builder import ContextBuilder, DecisionEngine, BehaviorRules
from layers.llm.ollama_backend import OllamaBackend


class AssistantRuntime:
    """Main Runtime - Orchestrates all layers"""
    
    def __init__(self):
        logger.info("Initializing AI Assistant Runtime...")
        
        self.character = Character()
        self.memory = MemoryManager()
        self.context_builder = ContextBuilder()
        self.decision_engine = DecisionEngine()
        self.behavior_rules = BehaviorRules()
        self.llm = OllamaBackend()
        
        logger.info("✅ All layers initialized successfully!")
        logger.info(f"Character: {self.character.name}")
    
    def process_input(self, user_input: str) -> str:
        """Main processing pipeline"""
        logger.info(f"Processing input: {user_input[:50]}...")
        
        try:
            user_emotion = self.decision_engine.analyze_user_emotion(user_input)
            logger.debug(f"User emotion: {user_emotion}")
            
            self.character.update_emotion_from_user_input(
                user_input,
                sentiment=user_emotion['sentiment']
            )
            
            relevant_memories = self.memory.retrieve_relevant_memories(
                user_input,
                n_results=3
            )
            logger.debug(f"Retrieved {len(relevant_memories)} memories")
            
            short_term_history = self.memory.get_short_term_context(max_turns=5)
            personality_prompt = self.character.get_system_prompt()
            response_tone = self.character.get_response_tone()
            emotional_state = self.character.emotional_state.to_dict()
            
            messages = self.context_builder.build_llm_context(
                personality_prompt=personality_prompt,
                user_input=user_input,
                short_term_history=short_term_history,
                retrieved_memories=relevant_memories,
                emotional_state=emotional_state,
                response_tone=response_tone
            )
            
            logger.debug("Generating response from LLM...")
            ai_response = self.llm.generate(messages)
            
            is_valid, reason = self.behavior_rules.validate_response(ai_response)
            if not is_valid:
                logger.warning(f"Invalid response: {reason}. Using fallback...")
                ai_response = self._get_fallback_response(user_input)
            
            self.behavior_rules.track_response(ai_response)
            self.memory.add_turn(user_input, ai_response)
            self.memory.extract_and_save_facts(user_input)
            
            logger.info("✅ Response generated successfully")
            return ai_response
            
        except Exception as e:
            logger.error(f"Error in processing: {e}")
            return self._get_error_response()
    
    def _get_fallback_response(self, user_input: str) -> str:
        """Fallback response"""
        import random
        responses = [
            "Mình có thể nghe bạn nói thêm về điều đó được không?",
            "Bạn có thể giải thích rõ hơn không?",
            "Thú vị đấy! Kể mình nghe thêm đi.",
        ]
        return random.choice(responses)
    
    def _get_error_response(self) -> str:
        """Error response"""
        return "Xin lỗi, mình gặp lỗi rồi. Bạn thử lại được không? 🥺"
    
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê của hệ thống"""
        memory_stats = self.memory.get_memory_stats()
        emotional_state = self.character.emotional_state.to_dict()
        
        return {
            "character_name": self.character.name,
            "emotional_state": emotional_state,
            "memory_stats": memory_stats,
            "model": self.llm.model
        }
    
    def reset_conversation(self):
        """Reset conversation"""
        self.memory.clear_short_term()
        logger.info("Conversation reset")
'''
    
    Path("core").mkdir(parents=True, exist_ok=True)
    with open("core/runtime.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ core/runtime.py")


def main():
    """Main function"""
    print("\n" + "="*60)
    print("📝 Creating All Python Files")
    print("="*60 + "\n")
    
    try:
        create_personality_character()
        create_memory_manager()
        create_reasoning_layer()
        create_ollama_backend()
        create_runtime()
        
        print("\n" + "="*60)
        print("✅ ALL FILES CREATED SUCCESSFULLY!")
        print("="*60)
        print("\nNext steps:")
        print("1. Run: python test_prototype.py")
        print("2. If tests pass, run: python main.py")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
