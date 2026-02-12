"""
AI Voice Assistant - Main Entry Point
RTX 2060 Super Optimized
"""

import argparse
import yaml
import sys
from pathlib import Path
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

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
    YAML config yükle
    
    Args:
        config_path: Config dosya yolu
    
    Returns:
        Config dict'i
    """
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        logger.error(f"Config dosyası bulunamadı: {config_path}")
        sys.exit(1)
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        logger.success(f"Config yüklendi: {config_path}")
        return config
        
    except Exception as e:
        logger.error(f"Config yükleme hatası: {e}")
        sys.exit(1)


def main():
    """Ana fonksiyon"""
    
    # ASCII Art Banner
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        🎤 AI VOICE ASSISTANT                             ║
    ║        RTX 2060 Super Optimized Edition                  ║
    ║                                                           ║
    ║        Powered by: Qwen2.5, Moondream, Whisper          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Argümanlar
    parser = argparse.ArgumentParser(
        description="AI Voice Assistant - 8GB VRAM Optimized",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--mode",
        choices=["console", "gui"],
        default="console",
        help="Çalışma modu (default: console)"
    )
    
    parser.add_argument(
        "--config",
        default="config/settings.yaml",
        help="Config dosya yolu (default: config/settings.yaml)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug mode (detaylı loglar)"
    )
    
    parser.add_argument(
        "--no-vram-check",
        action="store_true",
        help="VRAM monitoring'i devre dışı bırak"
    )
    
    args = parser.parse_args()
    
    # Config yükle
    config = load_config(args.config)
    
    # Debug mode
    if args.debug:
        config['logging']['level'] = 'DEBUG'
    
    # Logger kur
    setup_logger(config)
    
    logger.info("="*60)
    logger.info("🚀 AI VOICE ASSISTANT BAŞLATILIYOR...")
    logger.info("="*60)
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
    
    # Core bileşenler
    logger.info("\n📦 Core bileşenler yükleniyor...")
    
    try:
        model_manager = ModelManager(config)
        cache_manager = CacheManager(config)
        llm_manager = LLMManager(config, model_manager, cache_manager, perf_tracker)
        
        logger.success("✅ Core bileşenler hazır")
        
    except Exception as e:
        logger.error(f"❌ Core bileşen hatası: {e}")
        sys.exit(1)
    
    # Audio bileşenleri
    logger.info("\n🎵 Audio bileşenleri yükleniyor...")
    
    try:
        stt_engine = STTEngine(config, model_manager)
        tts_engine = TTSEngine(config)
        
        logger.success("✅ Audio bileşenleri hazır")
        logger.info("ℹ️  STT modeli ilk kullanımda yüklenecek (small model, CPU optimized)")
        
    except Exception as e:
        logger.error(f"❌ Audio bileşen hatası: {e}")
        logger.warning("⚠️  Audio özellikleri sınırlı olabilir")
        stt_engine = None
        tts_engine = None
    
    # UI başlat
    logger.info(f"\n🖥️  {args.mode.upper()} UI başlatılıyor...")
    
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
        logger.info("\n\n🛑 Kullanıcı tarafından durduruldu")
        
    except Exception as e:
        logger.error(f"❌ UI hatası: {e}")
        raise
        
    finally:
        # Cleanup
        logger.info("\n🧹 Temizlik yapılıyor...")
        
        # Modelleri boşalt
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
        
        logger.success("\n✅ Temizlik tamamlandı")
        logger.info("👋 Güle güle!\n")


if __name__ == "__main__":
    main()
