"""
Audio Processor - Ses işleme yardımcıları
Gürültü azaltma, normalizasyon vb.
"""

import numpy as np
from loguru import logger

try:
    import noisereduce as nr
    NOISEREDUCE_AVAILABLE = True
except ImportError:
    NOISEREDUCE_AVAILABLE = False
    logger.warning("noisereduce yüklü değil")


class AudioProcessor:
    """Ses işleme araçları"""
    
    @staticmethod
    def reduce_noise(audio: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
        """
        Gürültü azaltma
        
        Args:
            audio: Ses verisi
            sample_rate: Örnekleme hızı
        
        Returns:
            Temizlenmiş ses
        """
        if not NOISEREDUCE_AVAILABLE:
            logger.warning("noisereduce yüklü değil, gürültü azaltma yapılamıyor")
            return audio
        
        try:
            # Gürültü profili çıkar (ilk 0.5 saniye)
            noise_sample = audio[:int(0.5 * sample_rate)]
            
            # Gürültüyü azalt
            reduced = nr.reduce_noise(
                y=audio,
                sr=sample_rate,
                y_noise=noise_sample,
                stationary=True
            )
            
            return reduced
            
        except Exception as e:
            logger.error(f"Gürültü azaltma hatası: {e}")
            return audio
    
    @staticmethod
    def normalize_audio(audio: np.ndarray, target_level: float = -20.0) -> np.ndarray:
        """
        Ses seviyesini normalize et
        
        Args:
            audio: Ses verisi
            target_level: Hedef seviye (dB)
        
        Returns:
            Normalize edilmiş ses
        """
        # RMS hesapla
        rms = np.sqrt(np.mean(audio**2))
        
        if rms == 0:
            return audio
        
        # dB cinsinden mevcut seviye
        current_db = 20 * np.log10(rms)
        
        # Gain hesapla
        gain_db = target_level - current_db
        gain_linear = 10 ** (gain_db / 20)
        
        # Uygula
        normalized = audio * gain_linear
        
        # Clipping kontrolü
        normalized = np.clip(normalized, -1.0, 1.0)
        
        return normalized
    
    @staticmethod
    def trim_silence(
        audio: np.ndarray,
        threshold: float = 0.01,
        sample_rate: int = 16000
    ) -> np.ndarray:
        """
        Başındaki ve sonundaki sessizliği kes
        
        Args:
            audio: Ses verisi
            threshold: Sessizlik eşiği
            sample_rate: Örnekleme hızı
        
        Returns:
            Kesilmiş ses
        """
        # Ses seviyesi hesapla
        energy = np.abs(audio)
        
        # Eşiğin üzerindeki noktaları bul
        above_threshold = energy > threshold
        
        if not above_threshold.any():
            return audio
        
        # İlk ve son ses noktalarını bul
        start_idx = np.argmax(above_threshold)
        end_idx = len(audio) - np.argmax(above_threshold[::-1])
        
        # Biraz padding ekle (50ms)
        padding = int(0.05 * sample_rate)
        start_idx = max(0, start_idx - padding)
        end_idx = min(len(audio), end_idx + padding)
        
        return audio[start_idx:end_idx]
    
    @staticmethod
    def apply_gain(audio: np.ndarray, gain_db: float) -> np.ndarray:
        """
        Ses seviyesine gain uygula
        
        Args:
            audio: Ses verisi
            gain_db: Gain (dB cinsinden)
        
        Returns:
            Gain uygulanmış ses
        """
        gain_linear = 10 ** (gain_db / 20)
        amplified = audio * gain_linear
        
        # Clipping kontrolü
        return np.clip(amplified, -1.0, 1.0)
    
    @staticmethod
    def get_audio_stats(audio: np.ndarray, sample_rate: int = 16000) -> dict:
        """
        Ses istatistikleri
        
        Args:
            audio: Ses verisi
            sample_rate: Örnekleme hızı
        
        Returns:
            İstatistik dict'i
        """
        rms = np.sqrt(np.mean(audio**2))
        peak = np.max(np.abs(audio))
        duration = len(audio) / sample_rate
        
        return {
            'duration_seconds': round(duration, 2),
            'sample_rate': sample_rate,
            'rms_level': round(rms, 4),
            'peak_level': round(peak, 4),
            'db_level': round(20 * np.log10(rms) if rms > 0 else -np.inf, 2)
        }
