"""
STT Engine - Faster-Whisper Optimized
INT8 quantization ile 8GB VRAM'de sorunsuz çalışır
"""

import numpy as np
import sounddevice as sd
import soundfile as sf
from typing import Optional
from loguru import logger

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("Faster-Whisper yüklü değil! pip install faster-whisper")


class STTEngine:
    """Optimized Speech-to-Text"""
    
    def __init__(self, config: dict, model_manager):
        self.config = config['stt']
        self.model_manager = model_manager
        
        # VAD (Voice Activity Detection)
        try:
            import webrtcvad
            self.vad = webrtcvad.Vad(2)  # Aggressiveness: 0-3
            self.vad_available = True
        except ImportError:
            logger.warning("webrtcvad yüklü değil, VAD devre dışı")
            self.vad_available = False
    
    def transcribe(
        self,
        audio_path: Optional[str] = None,
        audio_array: Optional[np.ndarray] = None,
        sample_rate: int = 16000
    ) -> str:
        """
        Ses → Metin
        
        Args:
            audio_path: Ses dosya yolu
            audio_array: NumPy array (mikrofondan)
            sample_rate: Örnekleme hızı
        
        Returns:
            Transkripsiyon metni
        """
        
        if not WHISPER_AVAILABLE:
            logger.error("Faster-Whisper yüklü değil!")
            return ""
        
        # Model yükle
        model = self.model_manager.load_model("stt")
        
        # Ses dosyasını yükle
        if audio_path:
            audio, sr = sf.read(audio_path)
            if sr != 16000:
                # Resample gerekirse
                try:
                    from scipy import signal
                    audio = signal.resample(audio, int(len(audio) * 16000 / sr))
                except ImportError:
                    logger.warning("scipy yüklü değil, resampling yapılamıyor")
        elif audio_array is not None:
            audio = audio_array
        else:
            raise ValueError("audio_path veya audio_array gerekli")
        
        # Mono'ya çevir (gerekirse)
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)
        
        # VAD ile sessizlikleri kes
        if self.config['vad_filter'] and self.vad_available:
            audio = self._apply_vad(audio)
        
        logger.info("Transkripsiyon başlıyor...")
        
        try:
            # Faster-Whisper ile transkribe et
            segments, info = model.transcribe(
                audio,
                language=self.config.get('language', 'tr'),
                beam_size=self.config.get('beam_size', 3),
                vad_filter=self.config.get('vad_filter', False),
                vad_parameters=self.config.get('vad_parameters', {}),
                word_timestamps=False  # Daha hızlı
            )
            
            # Segmentleri birleştir
            text = " ".join([segment.text for segment in segments])
            
            logger.success(f"Transkripsiyon: '{text}'")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Transkripsiyon hatası: {e}")
            return ""
    
    def record_audio(self, duration: int = 5, sample_rate: int = 16000) -> np.ndarray:
        """
        Mikrofondan ses kaydet
        
        Args:
            duration: Kayıt süresi (saniye)
            sample_rate: Örnekleme hızı
        
        Returns:
            Ses verisi (NumPy array)
        """
        logger.info(f"🎤 {duration} saniye ses kaydediliyor...")
        
        try:
            audio = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()
            
            logger.success("Kayıt tamamlandı")
            return audio.flatten()
            
        except Exception as e:
            logger.error(f"Ses kayıt hatası: {e}")
            return np.array([])
    
    def _apply_vad(self, audio: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
        """Voice Activity Detection - sessizlikleri kes"""
        if not self.vad_available:
            return audio
        
        try:
            # Int16'ya çevir (VAD için gerekli)
            audio_int16 = (audio * 32767).astype(np.int16)
            
            frame_duration = 30  # ms (10, 20, 30 olabilir)
            frame_size = int(sample_rate * frame_duration / 1000)
            
            voiced_frames = []
            for i in range(0, len(audio_int16), frame_size):
                frame = audio_int16[i:i+frame_size]
                if len(frame) < frame_size:
                    break
                
                # VAD kontrolü
                is_speech = self.vad.is_speech(frame.tobytes(), sample_rate)
                if is_speech:
                    voiced_frames.append(frame)
            
            # Birleştir
            if voiced_frames:
                result = np.concatenate(voiced_frames)
                return result.astype(np.float32) / 32767.0
            else:
                return audio
                
        except Exception as e:
            logger.warning(f"VAD hatası: {e}")
            return audio
    
    def is_audio_silent(self, audio: np.ndarray, threshold: float = 0.01) -> bool:
        """
        Ses sessiz mi kontrol et
        
        Args:
            audio: Ses verisi
            threshold: Sessizlik eşiği
        
        Returns:
            Sessiz mi?
        """
        rms = np.sqrt(np.mean(audio**2))
        return rms < threshold
