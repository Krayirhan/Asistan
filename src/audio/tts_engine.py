"""
TTS Engine - Piper (High-quality Turkish TTS)
VRAM'dan hiç yer kaplamaz, CPU'da çalışır
"""

import numpy as np
import sounddevice as sd
from typing import Optional
from loguru import logger
from pathlib import Path
import wave
import io

try:
    from piper import PiperVoice
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False
    logger.warning("Piper TTS yüklü değil! pip install piper-tts")


class TTSEngine:
    """High-quality Text-to-Speech using Piper"""
    
    def __init__(self, config: dict):
        self.config = config['tts']
        
        if not PIPER_AVAILABLE:
            logger.error("Piper TTS yüklü değil!")
            self.model = None
            return
        
        # Piper modelini yükle
        logger.info("Piper TTS yükleniyor (CPU)...")
        try:
            model_path = Path("models/piper/tr_TR-fettah-medium.onnx")
            
            if not model_path.exists():
                logger.error(f"Piper model bulunamadı: {model_path}")
                self.model = None
                return
            
            self.model = PiperVoice.load(str(model_path))
            self.sample_rate = self.model.config.sample_rate
            
            logger.success(f"Piper hazır! (Sample rate: {self.sample_rate}Hz)")
        except Exception as e:
            logger.error(f"Piper yükleme hatası: {e}")
            self.model = None
    
    
    def speak(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        save_path: Optional[str] = None
    ):
        """
        Metni sesli oku
        
        Args:
            text: Okunacak metin (Türkçe desteklenir)
            voice: Kullanılmıyor (model sabit)
            speed: Okuma hızı (1.0 = normal)
            save_path: .wav olarak kaydet (opsiyonel)
        """
        
        if not text or not self.model:
            return
        
        logger.info(f"🔊 Piper TTS: '{text[:50]}...'")
        
        try:
            # Piper ile ses üret (generator AudioChunk döndürür)
            audio_chunks = []
            for audio_chunk in self.model.synthesize(text):
                # AudioChunk.audio_float_array numpy array'i içerir
                audio_chunks.append(audio_chunk.audio_float_array)
            
            # Tüm chunk'ları birleştir
            if not audio_chunks:
                logger.warning("Hiç audio chunk üretilmedi")
                return
                
            audio_array = np.concatenate(audio_chunks)
            
            # Oynat
            sd.play(audio_array, self.sample_rate)
            sd.wait()
            
            logger.success("✅ Ses çalındı!")
            
            # Kaydet (opsiyonel)
            if save_path:
                import soundfile as sf
                sf.write(save_path, audio_array, self.sample_rate)
                logger.info(f"Ses kaydedildi: {save_path}")
                
        except Exception as e:
            logger.error(f"Piper TTS hatası: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def test_voice(self):
        """Ses testi yap"""
        test_text = "Merhaba, ben AI asistanınızım. Sesi test ediyorum."
        self.speak(test_text)
