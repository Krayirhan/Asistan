# -*- coding: utf-8 -*-
"""
AI Voice Assistant - Main Entry Point
RTX 2060 Super Optimized
"""

import argparse
import yaml
import sys
from pathlib import Path
from loguru import logger

# Paths
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent

# Add src to path
sys.path.insert(0, str(SRC_DIR))

# Import managers
from core.model_loader import ModelManager
from core.llm_manager import LLMManager
from core.cache_manager import CacheManager

from audio.stt_engine import STTEngine
from audio.tts_engine import TTSEngine

from ui.console_ui import ConsoleUI
from ui.gradio_ui import GradioUI

from monitoring.vram_monitor import VRAMMonitor
from monitoring.performance import PerformanceTracker
from monitoring.logger import setup_logger, log_system_info


def load_config(config_path: str = "config/settings.yaml") -> dict:
    """
    YAML config yukle

    Args:
        config_path: Config dosya yolu

    Returns:
        Config dict'i
    """

    config_file = Path(config_path).expanduser()
    if not config_file.is_absolute():
        repo_relative = PROJECT_ROOT / config_file
        cwd_relative = Path.cwd() / config_file
        if repo_relative.exists():
            config_file = repo_relative
        elif cwd_relative.exists():
            config_file = cwd_relative
        else:
            config_file = repo_relative

    if not config_file.exists():
        logger.error(f"Config dosyasi bulunamadi: {config_file}")
        sys.exit(1)

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        logger.success(f"Config yuklendi: {config_file}")
        return config

    except Exception as e:
        logger.error(f"Config yukleme hatasi: {e}")
        sys.exit(1)


def main():
    """Ana fonksiyon"""

    # ASCII Art Banner
    print("""
    ============================================================
                                                               
            AI VOICE ASSISTANT                                 
            RTX 2060 Super Optimized Edition                   
                                                               
            Powered by: Qwen2.5, Moondream, Whisper           
                                                               
    ============================================================
    """)

    # Argumanlar
    parser = argparse.ArgumentParser(
        description="AI Voice Assistant - 8GB VRAM Optimized",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--mode",
        choices=["console", "gui"],
        default="console",
        help="Calisma modu (default: console)"
    )

    parser.add_argument(
        "--config",
        default="config/settings.yaml",
        help="Config dosya yolu (default: config/settings.yaml)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug mode (detayli loglar)"
    )

    parser.add_argument(
        "--no-vram-check",
        action="store_true",
        help="VRAM monitoring'i devre disi birak"
    )

    args = parser.parse_args()

    # Config yukle
    config = load_config(args.config)

    # Debug mode
    if args.debug:
        config['logging']['level'] = 'DEBUG'

    # Logger kur
    setup_logger(config)

    logger.info("=" * 60)
    logger.info("AI VOICE ASSISTANT BASLATILIYOR...")
    logger.info("=" * 60)
    logger.info(f"Mod: {args.mode}")
    logger.info(f"Config: {args.config}")

    # Sistem bilgilerini logla
    log_system_info()

    # VRAM Monitoring
    vram_monitor = None
    if not args.no_vram_check:
        vram_monitor = VRAMMonitor(config)
        vram_monitor.print_stats()

    # Performance Tracker
    perf_tracker = PerformanceTracker()

    # Core bilesenler
    logger.info("Core bilesenler yukleniyor...")

    try:
        model_manager = ModelManager(config)
        cache_manager = CacheManager(config)
        llm_manager = LLMManager(config, model_manager, cache_manager, perf_tracker)

        logger.success("Core bilesenler hazir")

    except Exception as e:
        logger.error(f"Core bilesen hatasi: {e}")
        sys.exit(1)

    # Audio bilesenleri
    logger.info("Audio bilesenler yukleniyor...")

    try:
        stt_engine = STTEngine(config, model_manager)
        tts_engine = TTSEngine(config)

        logger.success("Audio bilesenler hazir")
        logger.info("STT modeli ilk kullanimda yuklenecek (small model, CPU optimized)")

    except Exception as e:
        logger.error(f"Audio bilesen hatasi: {e}")
        logger.warning("Audio ozellikleri sinirli olabilir")
        stt_engine = None
        tts_engine = None

    # UI baslat
    logger.info(f"{args.mode.upper()} UI baslatiliyor...")

    try:
        if args.mode == "console":
            ui = ConsoleUI(config, llm_manager, stt_engine, tts_engine)
            ui.run()

        elif args.mode == "gui":
            ui = GradioUI(config, llm_manager, stt_engine, tts_engine)
            ui.launch()

        else:
            logger.error(f"Bilinmeyen mod: {args.mode}")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Kullanici tarafindan durduruldu")

    except Exception as e:
        logger.error(f"UI hatasi: {e}")
        raise

    finally:
        # Cleanup
        logger.info("Temizlik yapiliyor...")

        # Modelleri bosalt
        if hasattr(model_manager, 'unload_model'):
            model_manager.unload_model("llm")
            model_manager.unload_model("vlm")
            model_manager.unload_model("stt")

        # Cache kaydet
        if hasattr(cache_manager, '_save_cache'):
            cache_manager._save_cache()

        # Performance raporu
        if perf_tracker:
            perf_tracker.print_report()

        # Final VRAM stats
        if vram_monitor:
            vram_monitor.print_stats()

        logger.success("Temizlik tamamlandi")
        logger.info("Gule gule!")


if __name__ == "__main__":
    main()

