"""
Wake Word Detector - Porcupine CPU-Only
"Hey Assistant" gibi tetik kelimeleri algılar
"""

import struct
import numpy as np
import sounddevice as sd
from typing import Optional, Callable
from loguru import logger

try:
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except ImportError:
    PORCUPINE_AVAILABLE = False
    logger.warning("Porcupine yüklü değil! pip install pvporcupine")


class WakeWordDetector:
    """Wake word algılama (CPU-only)"""
    
    def __init__(self, config: dict):
        self.config = config['wake_word']
        self.enabled = self.config.get('enabled', True)
        
        if not self.enabled:
            logger.info("Wake word devre dışı")
            self.porcupine = None
            return
        
        if not PORCUPINE_AVAILABLE:
            logger.error("Porcupine yüklü değil!")
            self.porcupine = None
            return
        
        # Porcupine başlat
        self._init_porcupine()
    
    def _init_porcupine(self):
        """Porcupine'i başlat"""
        try:
            keyword = self.config.get('keyword', 'jarvis')
            sensitivity = self.config.get('sensitivity', 0.5)
            
            # Built-in keywords
            keywords = pvporcupine.KEYWORDS if hasattr(pvporcupine, 'KEYWORDS') else []
            
            if keyword in keywords:
                # Built-in keyword kullan
                self.porcupine = pvporcupine.create(
                    keywords=[keyword],
                    sensitivities=[sensitivity]
                )
                logger.success(f"Wake word '{keyword}' aktif!")
            else:
                # Custom model kullan (eğer varsa)
                custom_model = self.config.get('custom_model_path')
                if custom_model:
                    self.porcupine = pvporcupine.create(
                        keyword_paths=[custom_model],
                        sensitivities=[sensitivity]
                    )
                    logger.success(f"Custom wake word yüklendi!")
                else:
                    logger.warning(f"'{keyword}' bulunamadı, varsayılan 'jarvis' kullanılıyor")
                    self.porcupine = pvporcupine.create(
                        keywords=['jarvis'],
                        sensitivities=[sensitivity]
                    )
                    
        except Exception as e:
            logger.error(f"Porcupine başlatma hatası: {e}")
            self.porcupine = None
    
    def listen(self, callback: Optional[Callable] = None, duration: int = 0):
        """
        Wake word dinle
        
        Args:
            callback: Wake word algılandığında çağrılacak fonksiyon
            duration: Dinleme süresi (0 = sonsuz)
        """
        
        if not self.porcupine:
            logger.error("Porcupine aktif değil!")
            return
        
        logger.info("🎤 Wake word bekleniyor...")
        
        audio_stream = sd.InputStream(
            samplerate=self.porcupine.sample_rate,
            channels=1,
            dtype='int16',
            blocksize=self.porcupine.frame_length
        )
        
        try:
            audio_stream.start()
            start_time = 0
            
            while True:
                # Audio frame oku
                pcm, _ = audio_stream.read(self.porcupine.frame_length)
                pcm = pcm.flatten()
                
                # Wake word algılama
                keyword_index = self.porcupine.process(pcm)
                
                if keyword_index >= 0:
                    logger.success("✅ Wake word algılandı!")
                    
                    if callback:
                        callback()
                    
                    break
                
                # Timeout kontrolü
                if duration > 0:
                    start_time += self.porcupine.frame_length / self.porcupine.sample_rate
                    if start_time >= duration:
                        logger.info("Timeout, wake word algılanamadı")
                        break
                        
        except KeyboardInterrupt:
            logger.info("Wake word dinleme durduruldu")
        finally:
            audio_stream.stop()
            audio_stream.close()
    
    def __del__(self):
        """Cleanup"""
        if self.porcupine:
            self.porcupine.delete()
