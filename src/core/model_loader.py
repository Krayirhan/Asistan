"""
Akıllı Model Yönetici - VRAM Optimize
8GB VRAM sınırı için tasarlandı
"""

import gc
import time
from typing import Optional, Dict
from loguru import logger
import pynvml

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch bulunamadı, bazı optimizasyonlar devre dışı")


class ModelManager:
    """
    Lazy loading ve otomatik unload ile VRAM yönetimi
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.loaded_models: Dict[str, any] = {}
        self.last_used: Dict[str, float] = {}
        self.max_vram = config['hardware']['gpu_memory_limit']
        
        # NVIDIA GPU monitoring başlat
        try:
            pynvml.nvmlInit()
            self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            logger.info("GPU monitoring aktif")
        except Exception as e:
            logger.warning(f"GPU monitoring başlatılamadı: {e}")
            self.gpu_handle = None
        
    def get_vram_usage(self) -> float:
        """Mevcut VRAM kullanımı (GB)"""
        if self.gpu_handle is None:
            return 0.0
        
        try:
            info = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
            return info.used / 1024**3
        except:
            return 0.0
    
    def load_model(self, model_name: str, force: bool = False):
        """
        Model yükle - gerekirse eskiyi boşalt
        
        Args:
            model_name: 'llm', 'vlm', 'stt'
            force: Zorla yükle (bellekte başka model olsa bile)
        """
        
        # Zaten yüklüyse
        if model_name in self.loaded_models and not force:
            self.last_used[model_name] = time.time()
            logger.debug(f"{model_name} zaten bellekte")
            return self.loaded_models[model_name]
        
        # VRAM kontrolü
        current_vram = self.get_vram_usage()
        logger.info(f"Mevcut VRAM: {current_vram:.2f}GB / {self.max_vram}GB")
        
        # VRAM doluysa eski modelleri boşalt
        if current_vram > self.max_vram * 0.7:  # %70'ten fazlaysa
            self._unload_old_models(keep=model_name)
        
        # Yeni modeli yükle
        logger.info(f"{model_name} yükleniyor...")
        
        if model_name == "llm":
            model = self._load_llm()
        elif model_name == "vlm":
            model = self._load_vlm()
        elif model_name == "stt":
            model = self._load_stt()
        else:
            raise ValueError(f"Bilinmeyen model: {model_name}")
        
        self.loaded_models[model_name] = model
        self.last_used[model_name] = time.time()
        
        new_vram = self.get_vram_usage()
        logger.success(f"{model_name} yüklendi! VRAM: {new_vram:.2f}GB (+{new_vram-current_vram:.2f}GB)")
        
        return model
    
    def _unload_old_models(self, keep: Optional[str] = None):
        """En eski kullanılan modeli boşalt"""
        if not self.last_used:
            return
        
        # En eski kullanılanı bul
        candidates = [(k, v) for k, v in self.last_used.items() if k != keep]
        if not candidates:
            return
            
        oldest = min(candidates, key=lambda x: x[1])
        model_name = oldest[0]
        self.unload_model(model_name)
    
    def unload_model(self, model_name: str):
        """Modeli bellekten boşalt"""
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            del self.last_used[model_name]
            
            # GPU belleğini temizle
            gc.collect()
            if TORCH_AVAILABLE and torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info(f"{model_name} bellekten boşaltıldı. VRAM: {self.get_vram_usage():.2f}GB")
    
    def auto_cleanup(self):
        """Timeout'a uğramış modelleri boşalt"""
        timeout = self.config['hardware']['model_unload_timeout']
        current_time = time.time()
        
        for model_name, last_time in list(self.last_used.items()):
            if current_time - last_time > timeout:
                logger.info(f"{model_name} {timeout}s kullanılmadı, boşaltılıyor")
                self.unload_model(model_name)
    
    def _load_llm(self):
        """Qwen2.5-3B yükle"""
        try:
            from ollama import Client
            client = Client(host='http://localhost:11434')
            
            # Model var mı kontrol et
            models = client.list()
            model_name = self.config['llm']['model']
            
            # Model ismini sadeleştir (tag kısmını al)
            if model_name not in str(models):
                logger.warning(f"{model_name} yüklü değil! 'ollama pull {model_name}' çalıştırın")
            
            return client
        except Exception as e:
            logger.error(f"LLM yükleme hatası: {e}")
            raise
    
    def _load_vlm(self):
        """Moondream yükle"""
        try:
            from ollama import Client
            client = Client(host='http://localhost:11434')
            return client
        except Exception as e:
            logger.error(f"VLM yükleme hatası: {e}")
            raise
    
    def _load_stt(self):
        """Faster-Whisper yükle"""
        try:
            from faster_whisper import WhisperModel
            
            model_size = self.config['stt']['model_size']
            device = self.config['stt']['device']
            compute_type = self.config['stt']['compute_type']
            
            model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
                num_workers=4
            )
            return model
        except Exception as e:
            logger.error(f"STT yükleme hatası: {e}")
            raise
    
    def __del__(self):
        """Cleanup"""
        try:
            if self.gpu_handle:
                pynvml.nvmlShutdown()
        except:
            pass
