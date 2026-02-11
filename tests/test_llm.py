"""
Test suite for LLM functionality
"""

import pytest
from src.core.model_loader import ModelManager
from src.core.llm_manager import LLMManager


def test_llm_basic_query():
    """Basit LLM sorgusu testi"""
    
    config = {
        'hardware': {
            'gpu_memory_limit': 7.5,
            'model_unload_timeout': 30,
            'auto_memory_management': True
        },
        'llm': {
            'model': 'qwen2.5:3b-instruct-q4_K_M',
            'max_tokens': 100,
            'temperature': 0.7,
            'top_p': 0.9,
            'repeat_penalty': 1.1,
            'context_length': 15,
            'stream': False
        },
        'memory': {
            'max_history': 15,
            'save_to_disk': False
        }
    }
    
    print("\n[TEST] LLM başlatılıyor...")
    model_manager = ModelManager(config)
    llm_manager = LLMManager(config, model_manager)
    
    # Basit soru
    query = "Merhaba, nasılsın?"
    print(f"[TEST] Soru: {query}")
    
    response = llm_manager.generate(query, stream=False)
    
    print(f"[TEST] Cevap: {response[:100]}...")
    
    assert response, "LLM cevap vermedi"
    assert len(response) > 0, "Cevap boş"
    
    print("✅ LLM basic query testi geçti")


def test_conversation_history():
    """Konuşma geçmişi testi"""
    
    config = {
        'hardware': {'gpu_memory_limit': 7.5, 'model_unload_timeout': 30},
        'llm': {
            'model': 'qwen2.5:3b-instruct-q4_K_M',
            'max_tokens': 100,
            'temperature': 0.7
        },
        'memory': {
            'max_history': 5,  # Küçük limit
            'save_to_disk': False
        }
    }
    
    print("\n[TEST] Konuşma geçmişi testi...")
    model_manager = ModelManager(config)
    llm_manager = LLMManager(config, model_manager)
    
    # Birkaç mesaj gönder
    queries = [
        "Benim adım Ali",
        "Sen kimsin?",
        "Benim adım ne?"  # Hatırlamalı
    ]
    
    for query in queries:
        print(f"\n[TEST] Soru: {query}")
        response = llm_manager.generate(query, stream=False)
        print(f"[TEST] Cevap: {response[:80]}...")
    
    # Geçmiş kontrolü
    history = llm_manager.conversation_history
    print(f"\n[TEST] Geçmiş uzunluğu: {len(history)}")
    
    assert len(history) > 0, "Geçmiş kaydedilmedi"
    
    print("✅ Conversation history testi geçti")


if __name__ == "__main__":
    print("="*60)
    print("LLM FUNCTIONALITY TESTS")
    print("="*60)
    
    try:
        test_llm_basic_query()
    except Exception as e:
        print(f"❌ Test 1 başarısız: {e}")
    
    try:
        test_conversation_history()
    except Exception as e:
        print(f"❌ Test 2 başarısız: {e}")
    
    print("\n" + "="*60)
    print("TESTLER TAMAMLANDI")
    print("="*60)
