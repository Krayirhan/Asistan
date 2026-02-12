# -*- coding: utf-8 -*-
"""
VRAM Monitor - GPU Bellek Takibi
RTX 2060 Super icin optimizasyon amacli
"""

import time
from typing import Dict, Optional
from loguru import logger

try:
    import pynvml  # Provided by nvidia-ml-py
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False
    logger.warning("NVML yuklu degil! pip install nvidia-ml-py")


class VRAMMonitor:
    """GPU bellek monitoru"""

    def __init__(self, config: dict):
        self.config = config.get('monitoring', {})
        self.max_vram_gb = config['hardware']['gpu_memory_limit']
        self.alert_threshold = self.config.get('alert_threshold', 0.9)
        self.check_interval = self.config.get('vram_check_interval', 5)

        self.gpu_handle = None

        if PYNVML_AVAILABLE:
            self._init_nvml()
        else:
            logger.warning("VRAM monitoring devre disi")

    def _init_nvml(self):
        """NVML baslat"""
        try:
            pynvml.nvmlInit()
            self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)

            # GPU bilgisi
            gpu_name = pynvml.nvmlDeviceGetName(self.gpu_handle)
            logger.success(f"GPU algilandi: {gpu_name}")

        except Exception as e:
            logger.error(f"NVML baslatma hatasi: {e}")
            self.gpu_handle = None

    def get_vram_info(self) -> Dict:
        """
        VRAM bilgisi al

        Returns:
            VRAM istatistikleri
        """

        if not self.gpu_handle:
            return {
                'available': False,
                'used_gb': 0,
                'total_gb': 0,
                'usage_percent': 0
            }

        try:
            info = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)

            used_gb = info.used / 1024**3
            total_gb = info.total / 1024**3
            usage_percent = (info.used / info.total) * 100

            return {
                'available': True,
                'used_gb': round(used_gb, 2),
                'free_gb': round((info.total - info.used) / 1024**3, 2),
                'total_gb': round(total_gb, 2),
                'usage_percent': round(usage_percent, 2)
            }

        except Exception as e:
            logger.error(f"VRAM bilgisi alma hatasi: {e}")
            return {'available': False}

    def get_gpu_utilization(self) -> Optional[float]:
        """
        GPU kullanim orani

        Returns:
            Kullanim yuzdesi (0-100)
        """

        if not self.gpu_handle:
            return None

        try:
            util = pynvml.nvmlDeviceGetUtilizationRates(self.gpu_handle)
            return util.gpu

        except Exception as e:
            logger.error(f"GPU utilization hatasi: {e}")
            return None

    def get_temperature(self) -> Optional[float]:
        """
        GPU sicakligi

        Returns:
            Sicaklik (Celsius)
        """

        if not self.gpu_handle:
            return None

        try:
            temp = pynvml.nvmlDeviceGetTemperature(
                self.gpu_handle,
                pynvml.NVML_TEMPERATURE_GPU
            )
            return temp

        except Exception as e:
            logger.error(f"Sicaklik okuma hatasi: {e}")
            return None

    def check_memory_warning(self) -> bool:
        """
        Bellek uyarisi kontrol et

        Returns:
            Uyari var mi?
        """

        info = self.get_vram_info()

        if not info['available']:
            return False

        usage_ratio = info['usage_percent'] / 100

        if usage_ratio > self.alert_threshold:
            logger.warning(
                f"YUKSEK VRAM KULLANIMI! "
                f"{info['used_gb']}GB / {info['total_gb']}GB "
                f"({info['usage_percent']}%)"
            )
            return True

        return False

    def get_full_stats(self) -> Dict:
        """
        Tum GPU istatistikleri

        Returns:
            Tam istatistik dict'i
        """

        vram = self.get_vram_info()
        util = self.get_gpu_utilization()
        temp = self.get_temperature()

        return {
            'vram': vram,
            'utilization_percent': util,
            'temperature_celsius': temp,
            'timestamp': time.time()
        }

    def print_stats(self):
        """Istatistikleri konsola yazdir"""

        stats = self.get_full_stats()

        if not stats['vram']['available']:
            logger.info("GPU monitoring mevcut degil")
            return

        logger.info("=" * 50)
        logger.info("GPU STATISTICS")
        logger.info("=" * 50)
        logger.info(f"VRAM: {stats['vram']['used_gb']} GB / {stats['vram']['total_gb']} GB ({stats['vram']['usage_percent']}%)")
        logger.info(f"Free: {stats['vram']['free_gb']} GB")

        if stats['utilization_percent'] is not None:
            logger.info(f"GPU Utilization: {stats['utilization_percent']}%")

        if stats['temperature_celsius'] is not None:
            logger.info(f"Temperature: {stats['temperature_celsius']}C")

        logger.info("=" * 50)

    def __del__(self):
        """Cleanup"""
        if self.gpu_handle:
            try:
                pynvml.nvmlShutdown()
            except Exception:
                pass


