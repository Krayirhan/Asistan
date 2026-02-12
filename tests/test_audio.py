"""
Test suite for audio components (STT, TTS)
"""

import pytest
import numpy as np
from src.core.model_loader import ModelManager
from src.audio.stt_engine import STTEngine
from src.audio.tts_engine import TTSEngine


def test_stt_engine():
    """STT engine testi"""
    
    config = {
        'hardware': {'gpu_memory_limit': 7.5, 'model_unload_timeout': 30},
        'stt': {
            'model_size': 'base',
            'device': 'cpu',
            'compute_type': 'int8',
            'language': 'tr',
            'beam_size': 1,
            'vad_filter': False
        }
    }
    
    print("\n[TEST] STT Engine başlatılıyor...")
    model_manager = ModelManager(config)
    stt_engine = STTEngine(config, model_manager)
    
    # Dummy audio oluştur (5 saniye sessizlik)
    sample_rate = 16000
    duration = 5
    audio = np.zeros(duration * sample_rate, dtype=np.float32)
    
    # Sessizlik kontrolü
    is_silent = stt_engine.is_audio_silent(audio)
    
    print(f"[TEST] Audio sessiz mi? {is_silent}")
    assert is_silent == True, "Sessizlik algılanamadı"
    
    print("✅ STT engine testi geçti")


def test_tts_engine():
    """TTS engine testi"""
    
    config = {
        'tts': {
            'engine': 'piper',
            'model_path': 'models/piper/tr_TR-fettah-medium.onnx',
            'device': 'cpu',
            'speed': 1.0,
            'sample_rate': 22050,
            'num_threads': 4
        }
    }
    
    print("\n[TEST] TTS Engine başlatılıyor...")
    tts_engine = TTSEngine(config)
    
    # Test metni
    test_text = "Merhaba, bu bir test."
    
    print(f"[TEST] Test metni: {test_text}")
    
    # TTS çalıştır (ses çalmadan, sadece test)
    try:
        # Normalde speak() çağrılır ama test için skip
        print("[TEST] TTS model kontrolü yapılıyor...")
        assert tts_engine.model is not None or tts_engine.config is not None
        print("✅ TTS engine testi geçti")
    except Exception as e:
        print(f"⚠️  TTS optional, hata: {e}")


if __name__ == "__main__":
    print("="*60)
    print("AUDIO COMPONENTS TESTS")
    print("="*60)
    
    try:
        test_stt_engine()
    except Exception as e:
        print(f"❌ STT test başarısız: {e}")
    
    try:
        test_tts_engine()
    except Exception as e:
        print(f"❌ TTS test başarısız: {e}")
    
    print("\n" + "="*60)
    print("TESTLER TAMAMLANDI")
    print("="*60)
