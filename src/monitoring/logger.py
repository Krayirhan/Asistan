"""
Logger Setup - Structured Logging
"""

import sys
from pathlib import Path
from loguru import logger


def setup_logger(config: dict):
    """
    Loguru logger'ı konfigure et
    
    Args:
        config: Ana config dict'i
    """
    
    log_config = config.get('logging', {})
    level = log_config.get('level', 'INFO')
    save_path = log_config.get('save_path', 'logs/')
    format_type = log_config.get('format', 'json')
    
    # Eski logları temizle
    logger.remove()
    
    # Console logger
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level=level,
        colorize=True
    )
    
    # File logger - Normal text
    Path(save_path).mkdir(parents=True, exist_ok=True)
    
    logger.add(
        f"{save_path}/app_{{time:YYYY-MM-DD}}.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        enqueue=True
    )
    
    # File logger - JSON format (opsiyonel)
    if format_type == 'json':
        logger.add(
            f"{save_path}/app_{{time:YYYY-MM-DD}}.json",
            rotation="1 day",
            retention="7 days",
            level="DEBUG",
            serialize=True,
            enqueue=True
        )
    
    logger.success(f"Logger configured - Level: {level}")


def log_system_info():
    """Sistem bilgilerini logla"""
    
    import platform
    import psutil
    
    logger.info("="*60)
    logger.info("SYSTEM INFORMATION")
    logger.info("="*60)
    
    # OS
    logger.info(f"OS: {platform.system()} {platform.release()}")
    logger.info(f"Python: {platform.python_version()}")
    
    # CPU
    logger.info(f"CPU: {platform.processor()}")
    logger.info(f"CPU Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical")
    
    # RAM
    ram = psutil.virtual_memory()
    logger.info(f"RAM: {ram.total / 1024**3:.1f} GB total, {ram.available / 1024**3:.1f} GB available")
    
    # GPU (eğer varsa)
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        gpu_name = pynvml.nvmlDeviceGetName(handle)
        memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        
        logger.info(f"GPU: {gpu_name}")
        logger.info(f"VRAM: {memory_info.total / 1024**3:.1f} GB")
        
        pynvml.nvmlShutdown()
    except:
        logger.info("GPU: Not available")
    
    logger.info("="*60)
