"""
Test suite for VRAM management
RTX 2060 Super (8GB) için optimizasyon testleri
"""

import pytest
import time
from src.core.model_loader import ModelManager


def test_vram_limit():
    """VRAM kullanımı limit içinde mi?"""
    
    config = {
        'hardware': {
            'gpu_memory_limit': 7.5,
            'model_unload_timeout': 30,
            'auto_memory_management': True,
            'mixed_precision': True,
            'cpu_threads': 6
        },
        'llm': {
            'model': 'qwen2.5:3b-instruct-q4_K_M',
            'max_tokens': 1024,
            'temperature': 0.7,
            'top_p': 0.9,
            'repeat_penalty': 1.1,
            'context_length': 15,
            'stream': True,
            'num_gpu': 1
        },
        'vlm': {
            'model': 'moondream',
            'enabled': True,
            'lazy_load': True,
            'auto_unload': True
        },
        'stt': {
            'model_size': 'medium',
            'device': 'cuda',
            'compute_type': 'int8'
        }
    }
    
    manager = ModelManager(config)
    
    # LLM yükle
    print("\n[TEST] LLM yükleniyor...")
    manager.load_model("llm")
    vram_llm = manager.get_vram_usage()
    print(f"LLM VRAM: {vram_llm:.2f}GB")
    
    assert vram_llm < 7.5, f"LLM çok fazla VRAM kullanıyor: {vram_llm}GB"
    assert vram_llm > 0, "VRAM ölçümü çalışmıyor"
    
    # VLM ekle
    print("[TEST] VLM yükleniyor...")
    manager.load_model("vlm")
    vram_both = manager.get_vram_usage()
    print(f"LLM+VLM VRAM: {vram_both:.2f}GB")
    
    assert vram_both < 7.5, f"LLM+VLM çok fazla: {vram_both}GB"
    
    print(f"\n✅ VRAM Testi Geçti: Max {vram_both:.2f}GB / 8GB")


def test_auto_cleanup():
    """Otomatik cleanup çalışıyor mu?"""
    
    config = {
        'hardware': {
            'gpu_memory_limit': 7.5,
            'model_unload_timeout': 5,  # Kısa timeout
            'auto_memory_management': True
        },
        'llm': {'model': 'qwen2.5:3b-instruct-q4_K_M'},
        'vlm': {'model': 'moondream'},
        'stt': {'model_size': 'medium', 'device': 'cuda', 'compute_type': 'int8'}
    }
    
    manager = ModelManager(config)
    
    # Model yükle
    print("\n[TEST] Model yükleniyor...")
    manager.load_model("llm")
    vram_before = manager.get_vram_usage()
    
    # Timeout'tan fazla bekle
    print("[TEST] 6 saniye bekleniyor (timeout: 5s)...")
    time.sleep(6)
    
    # Auto cleanup çalıştır
    manager.auto_cleanup()
    vram_after = manager.get_vram_usage()
    
    print(f"VRAM before cleanup: {vram_before:.2f}GB")
    print(f"VRAM after cleanup: {vram_after:.2f}GB")
    
    assert vram_after < vram_before, "Otomatik cleanup çalışmadı"
    
    print("✅ Auto cleanup testi geçti")


if __name__ == "__main__":
    print("="*60)
    print("VRAM OPTIMIZATION TESTS - RTX 2060 Super")
    print("="*60)
    
    # Test 1
    try:
        test_vram_limit()
    except Exception as e:
        print(f"❌ Test 1 başarısız: {e}")
    
    # Test 2
    try:
        test_auto_cleanup()
    except Exception as e:
        print(f"❌ Test 2 başarısız: {e}")
    
    print("\n" + "="*60)
    print("TESTLER TAMAMLANDI")
    print("="*60)
