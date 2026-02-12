# -*- coding: utf-8 -*-
"""
Akilli Model Yonetici - VRAM Optimize
8GB VRAM siniri icin tasarlandi
"""

import gc
import time
from typing import Optional, Dict, Iterable, Any, Set
from loguru import logger

try:
    import pynvml  # Provided by nvidia-ml-py
    PYNVML_AVAILABLE = True
except ImportError:
    pynvml = None
    PYNVML_AVAILABLE = False


class ModelManager:
    """
    Lazy loading ve otomatik unload ile VRAM yonetimi
    """

    def __init__(self, config: dict):
        self.config = config
        self.loaded_models: Dict[str, Any] = {}
        self.last_used: Dict[str, float] = {}
        self.max_vram = config['hardware']['gpu_memory_limit']

        # NVIDIA GPU monitoring baslat
        self.gpu_handle = None
        if not PYNVML_AVAILABLE:
            logger.warning("NVML bulunamadi (pip install nvidia-ml-py)")
            return

        try:
            pynvml.nvmlInit()
            self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            logger.info("GPU monitoring aktif")
        except Exception as e:
            logger.warning(f"GPU monitoring baslatilamadi: {e}")
            self.gpu_handle = None

    def get_vram_usage(self) -> float:
        """Mevcut VRAM kullanimi (GB)"""
        if self.gpu_handle is None:
            return 0.0

        try:
            info = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
            return info.used / 1024**3
        except Exception:
            return 0.0

    def load_model(self, model_name: str, force: bool = False):
        """
        Model yukle - gerekirse eskiyi bosalt

        Args:
            model_name: 'llm', 'vlm', 'stt'
            force: Zorla yukle (bellekte baska model olsa bile)
        """

        # Zaten yukluyse
        if model_name in self.loaded_models and not force:
            self.last_used[model_name] = time.time()
            logger.debug(f"{model_name} zaten bellekte")
            return self.loaded_models[model_name]

        # VRAM kontrolu
        current_vram = self.get_vram_usage()
        logger.info(f"Mevcut VRAM: {current_vram:.2f}GB / {self.max_vram}GB")

        # VRAM doluysa eski modelleri bosalt
        if current_vram > self.max_vram * 0.7:  # %70'ten fazlaysa
            self._unload_old_models(keep=model_name)

        # Yeni modeli yukle
        logger.info(f"{model_name} yukleniyor...")

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
        logger.success(f"{model_name} yuklendi! VRAM: {new_vram:.2f}GB (+{new_vram-current_vram:.2f}GB)")

        return model

    def _unload_old_models(self, keep: Optional[str] = None):
        """En eski kullanilan modeli bosalt"""
        if not self.last_used:
            return

        # En eski kullanilanı bul
        candidates = [(k, v) for k, v in self.last_used.items() if k != keep]
        if not candidates:
            return

        oldest = min(candidates, key=lambda x: x[1])
        model_name = oldest[0]
        self.unload_model(model_name)

    def unload_model(self, model_name: str):
        """Modeli bellekten bosalt"""
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            del self.last_used[model_name]

            # Bellegi temizle (Ollama kendi GPU bellegini yonetir, gc yeterli)
            gc.collect()

            logger.info(f"{model_name} bellekten bosaltildi. VRAM: {self.get_vram_usage():.2f}GB")

    def auto_cleanup(self):
        """Timeout'a ugramis modelleri bosalt"""
        timeout = self.config['hardware']['model_unload_timeout']
        current_time = time.time()

        for model_name, last_time in list(self.last_used.items()):
            if current_time - last_time > timeout:
                logger.info(f"{model_name} {timeout}s kullanilmadi, bosaltiliyor")
                self.unload_model(model_name)

    @staticmethod
    def _extract_model_names(models_response: Any) -> Set[str]:
        """Ollama list cevanindan model isimlerini cikar."""
        names: Set[str] = set()

        def add_name(value: Any):
            if isinstance(value, str) and value.strip():
                names.add(value.strip())

        def walk(node: Any):
            if isinstance(node, dict):
                for key in ("name", "model"):
                    if key in node:
                        add_name(node[key])
                for value in node.values():
                    walk(value)
            elif isinstance(node, (list, tuple, set)):
                for item in node:
                    walk(item)
            elif hasattr(node, "name"):
                add_name(getattr(node, "name"))
            elif hasattr(node, "model"):
                add_name(getattr(node, "model"))

        # Yeni Ollama SDK: ListResponse.models listesi
        if hasattr(models_response, 'models'):
            for m in models_response.models:
                if hasattr(m, 'model'):
                    add_name(getattr(m, 'model'))
                if hasattr(m, 'name'):
                    add_name(getattr(m, 'name'))

        walk(models_response)

        if names:
            logger.debug(f"Bulunan Ollama modelleri: {names}")
        else:
            logger.warning(f"Ollama model listesi bos! Raw response type: {type(models_response)}")

        return names

    @staticmethod
    def _resolve_model_name(requested: str, available: Iterable[str]) -> Optional[str]:
        """Istenen modeli mevcut listede eslestir."""
        available_set = {item.strip() for item in available if isinstance(item, str) and item.strip()}
        if requested in available_set:
            return requested

        base = requested.split(":", 1)[0]
        for candidate in available_set:
            if candidate == base or candidate.startswith(base + ":"):
                return candidate
        return None

    def _load_llm(self):
        """Qwen2.5 yukle (Turkce ozel model veya fallback)"""
        try:
            from ollama import Client
            client = Client(host='http://localhost:11434')

            model_name = self.config['llm']['model']
            fallback = self.config['llm'].get('fallback_model', 'qwen2.5:7b')

            # Mevcut modelleri guvenli sekilde parse et.
            available_models = self._extract_model_names(client.list())
            selected = self._resolve_model_name(model_name, available_models)
            fallback_selected = self._resolve_model_name(fallback, available_models)

            if selected:
                logger.success(f"Turkce ozel model bulundu: {selected}")
                self.config['llm']['model'] = selected
            elif fallback_selected:
                logger.warning(f"{model_name} bulunamadi, fallback kullaniliyor: {fallback_selected}")
                self.config['llm']['model'] = fallback_selected
            else:
                logger.warning(
                    f"{model_name} ve {fallback} yuklu degil! "
                    f"'ollama pull {fallback}' calistirin"
                )

            return client
        except Exception as e:
            logger.error(f"LLM yukleme hatasi: {e}")
            raise

    def _load_vlm(self):
        """Moondream yukle"""
        try:
            from ollama import Client
            client = Client(host='http://localhost:11434')
            return client
        except Exception as e:
            logger.error(f"VLM yukleme hatasi: {e}")
            raise

    def _load_stt(self):
        """Faster-Whisper yukle"""
        try:
            from faster_whisper import WhisperModel

            model_size = self.config['stt']['model_size']
            device = self.config['stt']['device']
            compute_type = self.config['stt']['compute_type']
            default_workers = self.config.get('hardware', {}).get('cpu_threads', 4)
            num_workers = int(self.config['stt'].get('num_workers', default_workers))
            num_workers = max(1, num_workers)

            model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
                num_workers=num_workers
            )
            return model
        except Exception as e:
            logger.error(f"STT yukleme hatasi: {e}")
            raise

    def __del__(self):
        """Cleanup"""
        try:
            if self.gpu_handle:
                pynvml.nvmlShutdown()
        except Exception:
            pass
