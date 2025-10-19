"""
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
            text = f"User: {turn.user_input}\nAI: {turn.ai_response}"
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
