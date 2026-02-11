"""
Performance Tracker - Performans Metrikleri
LLM, STT, TTS sürelerini takip et
"""

import time
from typing import Dict, List, Optional
from collections import defaultdict
from loguru import logger


class PerformanceTracker:
    """Performans metrikleri takip sistemi"""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.operation_start_times: Dict[str, float] = {}
    
    def start_operation(self, operation_name: str):
        """
        İşlem başlat - zamanlayıcıyı aç
        
        Args:
            operation_name: İşlem adı (örn: 'llm_inference', 'stt_transcription')
        """
        
        self.operation_start_times[operation_name] = time.time()
        logger.debug(f"⏱️  {operation_name} başladı")
    
    def end_operation(self, operation_name: str):
        """
        İşlem bitir - süreyi kaydet
        
        Args:
            operation_name: İşlem adı
        """
        
        if operation_name not in self.operation_start_times:
            logger.warning(f"{operation_name} için başlangıç zamanı bulunamadı")
            return
        
        duration = time.time() - self.operation_start_times[operation_name]
        self.metrics[operation_name].append(duration)
        
        del self.operation_start_times[operation_name]
        
        logger.debug(f"✅ {operation_name} tamamlandı ({duration:.2f}s)")
    
    def get_average(self, operation_name: str) -> float:
        """
        İşlem ortalama süresi
        
        Args:
            operation_name: İşlem adı
        
        Returns:
            Ortalama süre (saniye)
        """
        
        if operation_name not in self.metrics or not self.metrics[operation_name]:
            return 0.0
        
        return sum(self.metrics[operation_name]) / len(self.metrics[operation_name])
    
    def get_total_time(self, operation_name: str) -> float:
        """
        İşlem toplam süresi
        
        Args:
            operation_name: İşlem adı
        
        Returns:
            Toplam süre (saniye)
        """
        
        if operation_name not in self.metrics:
            return 0.0
        
        return sum(self.metrics[operation_name])
    
    def get_count(self, operation_name: str) -> int:
        """
        İşlem sayısı
        
        Args:
            operation_name: İşlem adı
        
        Returns:
            Kaç kez yapıldı
        """
        
        if operation_name not in self.metrics:
            return 0
        
        return len(self.metrics[operation_name])
    
    def get_statistics(self, operation_name: str) -> Dict:
        """
        Detaylı istatistikler
        
        Args:
            operation_name: İşlem adı
        
        Returns:
            İstatistik dict'i
        """
        
        if operation_name not in self.metrics or not self.metrics[operation_name]:
            return {
                'count': 0,
                'total_time': 0,
                'average_time': 0,
                'min_time': 0,
                'max_time': 0
            }
        
        times = self.metrics[operation_name]
        
        return {
            'count': len(times),
            'total_time': round(sum(times), 2),
            'average_time': round(sum(times) / len(times), 2),
            'min_time': round(min(times), 2),
            'max_time': round(max(times), 2)
        }
    
    def get_all_statistics(self) -> Dict:
        """
        Tüm işlemler için istatistikler
        
        Returns:
            Tüm istatistikler
        """
        
        all_stats = {}
        
        for operation in self.metrics.keys():
            all_stats[operation] = self.get_statistics(operation)
        
        return all_stats
    
    def print_report(self):
        """Performans raporunu yazdır"""
        
        logger.info("="*60)
        logger.info("PERFORMANCE REPORT")
        logger.info("="*60)
        
        all_stats = self.get_all_statistics()
        
        if not all_stats:
            logger.info("Henüz metrik yok")
            return
        
        for operation, stats in all_stats.items():
            logger.info(f"\n{operation.upper()}:")
            logger.info(f"  Count: {stats['count']}")
            logger.info(f"  Total Time: {stats['total_time']}s")
            logger.info(f"  Average Time: {stats['average_time']}s")
            logger.info(f"  Min Time: {stats['min_time']}s")
            logger.info(f"  Max Time: {stats['max_time']}s")
        
        logger.info("="*60)
    
    def reset(self, operation_name: Optional[str] = None):
        """
        Metrikleri sıfırla
        
        Args:
            operation_name: Belirli bir işlem (None = tümü)
        """
        
        if operation_name:
            if operation_name in self.metrics:
                self.metrics[operation_name] = []
                logger.info(f"{operation_name} metrikleri sıfırlandı")
        else:
            self.metrics = defaultdict(list)
            logger.info("Tüm metrikler sıfırlandı")
    
    def context_timer(self, operation_name: str):
        """
        Context manager olarak kullanım
        
        Usage:
            with tracker.context_timer('my_operation'):
                # ... işlem ...
        """
        
        class TimerContext:
            def __init__(self, tracker, name):
                self.tracker = tracker
                self.name = name
            
            def __enter__(self):
                self.tracker.start_operation(self.name)
                return self
            
            def __exit__(self, *args):
                self.tracker.end_operation(self.name)
        
        return TimerContext(self, operation_name)
