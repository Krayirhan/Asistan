"""
Cache Manager - Response Caching
"""

import json
import hashlib
import time
from typing import Optional, Dict
from pathlib import Path
from loguru import logger


class CacheManager:
    """
    LLM cevaplarını cache'le - aynı soruya hızlı cevap
    """
    
    def __init__(self, config: dict):
        self.config = config['cache']
        self.enabled = self.config.get('enabled', True)
        self.ttl = self.config.get('ttl_seconds', 3600)
        self.max_size_mb = self.config.get('max_size_mb', 500)
        
        # Cache storage
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_file = self.cache_dir / "response_cache.json"
        self.cache_data: Dict = self._load_cache()
        
    def _load_cache(self) -> Dict:
        """Cache'i diskten yükle"""
        if not self.cache_file.exists():
            return {}
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Cache yüklendi: {len(data)} entry")
            return data
        except Exception as e:
            logger.error(f"Cache yükleme hatası: {e}")
            return {}
    
    def _save_cache(self):
        """Cache'i diske kaydet"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Cache kaydetme hatası: {e}")
    
    def _generate_key(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Prompt için unique key oluştur
        
        Args:
            prompt: Kullanıcı sorusu
            context: Ek context (opsiyonel)
        
        Returns:
            Hash key
        """
        content = prompt
        if context:
            content += f"|{context}"
        
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, context: Optional[str] = None) -> Optional[str]:
        """
        Cache'ten cevap al
        
        Args:
            prompt: Kullanıcı sorusu
            context: Ek context
        
        Returns:
            Cached response veya None
        """
        if not self.enabled:
            return None
        
        key = self._generate_key(prompt, context)
        
        if key not in self.cache_data:
            return None
        
        entry = self.cache_data[key]
        
        # TTL kontrolü
        if time.time() - entry['timestamp'] > self.ttl:
            logger.debug(f"Cache expired: {key}")
            del self.cache_data[key]
            return None
        
        logger.info(f"✅ Cache hit: {prompt[:50]}...")
        entry['hits'] += 1
        return entry['response']
    
    def set(self, prompt: str, response: str, context: Optional[str] = None):
        """
        Cevabı cache'e ekle
        
        Args:
            prompt: Kullanıcı sorusu
            response: Model cevabı
            context: Ek context
        """
        if not self.enabled:
            return
        
        key = self._generate_key(prompt, context)
        
        self.cache_data[key] = {
            'prompt': prompt,
            'response': response,
            'timestamp': time.time(),
            'hits': 0
        }
        
        logger.debug(f"Cache'e eklendi: {key}")
        
        # Periyodik kayıt
        if len(self.cache_data) % 10 == 0:
            self._save_cache()
    
    def clear(self):
        """Tüm cache'i temizle"""
        self.cache_data = {}
        self._save_cache()
        logger.info("Cache temizlendi")
    
    def cleanup_expired(self):
        """Süresi dolmuş entryleri temizle"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.cache_data.items():
            if current_time - entry['timestamp'] > self.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache_data[key]
        
        if expired_keys:
            logger.info(f"{len(expired_keys)} expired entry silindi")
            self._save_cache()
    
    def get_statistics(self) -> Dict:
        """
        Cache istatistikleri
        
        Returns:
            İstatistik dict'i
        """
        total_hits = sum(entry['hits'] for entry in self.cache_data.values())
        
        return {
            'total_entries': len(self.cache_data),
            'total_hits': total_hits,
            'cache_file_size_mb': round(self.cache_file.stat().st_size / 1024 / 1024, 2) if self.cache_file.exists() else 0
        }
    
    def __del__(self):
        """Cleanup - cache'i kaydet"""
        self._save_cache()
