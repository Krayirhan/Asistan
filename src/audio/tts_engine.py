# -*- coding: utf-8 -*-
"""
TTS Engine - Piper (High-quality Turkish TTS)
VRAM'dan hic yer kaplamaz, CPU'da calisir
"""

import numpy as np
import sounddevice as sd
from typing import Optional
from loguru import logger
from pathlib import Path

try:
    from piper import PiperVoice
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False
    logger.warning("Piper TTS yuklu degil! pip install piper-tts")


class TTSEngine:
    """High-quality Text-to-Speech using Piper"""

    def __init__(self, config: dict):
        self.config = config['tts']
        self.model_path = Path(self.config.get('model_path', "models/piper/tr_TR-fettah-medium.onnx"))

        if not PIPER_AVAILABLE:
            logger.error("Piper TTS yuklu degil!")
            self.model = None
            return

        # Piper modelini yukle
        logger.info("Piper TTS yukleniyor (CPU)...")
        try:
            if not self.model_path.exists():
                logger.error(f"Piper model bulunamadi: {self.model_path}")
                self.model = None
                return

            self.model = PiperVoice.load(str(self.model_path))
            self.sample_rate = self.model.config.sample_rate

            logger.success(f"Piper hazir! (Sample rate: {self.sample_rate}Hz)")
        except Exception as e:
            logger.error(f"Piper yukleme hatasi: {e}")
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
            text: Okunacak metin (Turkce desteklenir)
            voice: Kullanilmiyor (model sabit)
            speed: Okuma hizi (1.0 = normal)
            save_path: .wav olarak kaydet (opsiyonel)
        """

        if not text or not self.model:
            return

        logger.info(f"Piper TTS: '{text[:50]}...'")

        try:
            # Piper ile ses uret (generator AudioChunk dondurur)
            audio_chunks = []
            for audio_chunk in self.model.synthesize(text):
                # AudioChunk.audio_float_array numpy array'i icerir
                audio_chunks.append(audio_chunk.audio_float_array)

            # Tum chunk'lari birlestir
            if not audio_chunks:
                logger.warning("Hic audio chunk uretilmedi")
                return

            audio_array = np.concatenate(audio_chunks)

            # Oynat
            sd.play(audio_array, self.sample_rate)
            sd.wait()

            logger.success("Ses calindi!")

            # Kaydet (opsiyonel)
            if save_path:
                import soundfile as sf
                sf.write(save_path, audio_array, self.sample_rate)
                logger.info(f"Ses kaydedildi: {save_path}")

        except Exception as e:
            logger.error(f"Piper TTS hatasi: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def test_voice(self):
        """Ses testi yap"""
        test_text = "Merhaba, ben AI asistaninim. Sesi test ediyorum."
        self.speak(test_text)

