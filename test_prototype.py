#!/usr/bin/env python3
"""
Quick Test Script - Test từng layer riêng lẻ
Chạy trước khi test full system
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def test_imports():
    """Test 1: Imports"""
    print("\n" + "="*60)
    print("TEST 1: Testing Imports")
    print("="*60)
    
    try:
        import yaml
        print("✅ PyYAML")
        
        import chromadb
        print("✅ ChromaDB")
        
        from sentence_transformers import SentenceTransformer
        print("✅ SentenceTransformers")
        
        import ollama
        print("✅ Ollama")
        
        from loguru import logger
        print("✅ Loguru")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_config_files():
    """Test 2: Config files"""
    print("\n" + "="*60)
    print("TEST 2: Testing Config Files")
    print("="*60)
    
    files = [
        "config/personality.yaml",
        "config/behavior_rules.yaml",
        "config/settings.yaml",
        ".env"
    ]
    
    all_exist = True
    for file in files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - NOT FOUND")
            all_exist = False
    
    return all_exist


def test_ollama():
    """Test 3: Ollama connection"""
    print("\n" + "="*60)
    print("TEST 3: Testing Ollama")
    print("="*60)
    
    try:
        import ollama
        
        # List models
        models = ollama.list()
        available = [m['name'] for m in models['models']]
        
        print(f"✅ Ollama connected")
        print(f"   Available models: {', '.join(available)}")
        
        # Check configured model
        configured_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        if configured_model in available:
            print(f"✅ Configured model '{configured_model}' found")
            return True
        else:
            print(f"⚠️  Configured model '{configured_model}' not found")
            print(f"   Run: ollama pull {configured_model}")
            return False
            
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        print("   Make sure Ollama is running: ollama list")
        return False


def test_personality_layer():
    """Test 4: Personality Layer"""
    print("\n" + "="*60)
    print("TEST 4: Testing Personality Layer")
    print("="*60)
    
    try:
        from layers.personality.character import Character
        
        char = Character()
        print(f"✅ Character loaded: {char.name}")
        print(f"   Core traits: {list(char.core_traits.keys())}")
        print(f"   Initial mood: {char.emotional_state.mood}/100")
        
        # Test system prompt
        prompt = char.get_system_prompt()
        print(f"✅ System prompt generated ({len(prompt)} chars)")
        
        return True
    except Exception as e:
        print(f"❌ Personality layer failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_layer():
    """Test 5: Memory Layer"""
    print("\n" + "="*60)
    print("TEST 5: Testing Memory Layer")
    print("="*60)
    
    try:
        from layers.memory.memory_manager import MemoryManager
        
        # Initialize (this will download embedding model if needed)
        print("   Initializing memory manager...")
        mem = MemoryManager()
        print(f"✅ Memory manager initialized")
        
        # Test short-term memory
        mem.add_turn("Hello", "Hi there!", {"test": True})
        print(f"✅ Short-term memory working")
        
        # Test long-term save
        mem.save_fact("User likes testing", category="test")
        print(f"✅ Long-term memory working")
        
        # Test retrieval
        results = mem.retrieve_relevant_memories("testing", n_results=1)
        print(f"✅ Memory retrieval working (found {len(results)} results)")
        
        stats = mem.get_memory_stats()
        print(f"   Memory stats: {stats}")
        
        return True
    except Exception as e:
        print(f"❌ Memory layer failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_reasoning_layer():
    """Test 6: Reasoning Layer"""
    print("\n" + "="*60)
    print("TEST 6: Testing Reasoning Layer")
    print("="*60)
    
    try:
        from layers.reasoning.context_builder import (
            ContextBuilder, DecisionEngine, BehaviorRules
        )
        
        # Test context builder
        builder = ContextBuilder()
        print("✅ Context builder initialized")
        
        # Test decision engine
        engine = DecisionEngine()
        emotion = engine.analyze_user_emotion("Tôi rất vui hôm nay!")
        print(f"✅ Decision engine working")
        print(f"   Detected emotion: {emotion}")
        
        # Test behavior rules
        rules = BehaviorRules()
        is_valid, reason = rules.validate_response("Test response here")
        print(f"✅ Behavior rules working")
        
        return True
    except Exception as e:
        print(f"❌ Reasoning layer failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_layer():
    """Test 7: LLM Layer"""
    print("\n" + "="*60)
    print("TEST 7: Testing LLM Layer")
    print("="*60)
    
    try:
        from layers.llm.ollama_backend import OllamaBackend
        
        llm = OllamaBackend()
        print(f"✅ LLM backend initialized: {llm.model}")
        
        # Test simple generation
        print("   Testing generation (this may take a moment)...")
        messages = [
            {"role": "user", "content": "Say 'Hello' in Vietnamese"}
        ]
        response = llm.generate(messages)
        print(f"✅ Generation working")
        print(f"   Response: {response[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ LLM layer failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_runtime():
    """Test 8: Full Runtime Integration"""
    print("\n" + "="*60)
    print("TEST 8: Testing Full Runtime")
    print("="*60)
    
    try:
        from core.runtime import AssistantRuntime
        
        print("   Initializing runtime...")
        runtime = AssistantRuntime()
        print(f"✅ Runtime initialized")
        
        # Test single interaction
        print("   Testing full interaction...")
        response = runtime.process_input("Xin chào!")
        print(f"✅ Full pipeline working")
        print(f"   Response: {response[:100]}...")
        
        # Check stats
        stats = runtime.get_stats()
        print(f"✅ Stats available: {list(stats.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ Runtime failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 AI ASSISTANT PROTOTYPE - TEST SUITE")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Config Files", test_config_files),
        ("Ollama", test_ollama),
        ("Personality Layer", test_personality_layer),
        ("Memory Layer", test_memory_layer),
        ("Reasoning Layer", test_reasoning_layer),
        ("LLM Layer", test_llm_layer),
        ("Full Runtime", test_full_runtime),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to run main.py")
        print("\nRun: python main.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
