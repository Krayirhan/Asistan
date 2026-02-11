"""
Benchmark - Performans testleri
RTX 2060 Super için beklenen süreler
"""

import time
from src.core.model_loader import ModelManager
from src.core.llm_manager import LLMManager
from src.monitoring.performance import PerformanceTracker


def benchmark_llm_inference():
    """LLM inference hızı"""
    
    config = {
        'hardware': {'gpu_memory_limit': 7.5, 'model_unload_timeout': 30},
        'llm': {
            'model': 'qwen2.5:3b-instruct-q4_K_M',
            'max_tokens': 100,
            'temperature': 0.7,
            'stream': False
        },
        'memory': {'max_history': 15, 'save_to_disk': False}
    }
    
    print("\n" + "="*60)
    print("LLM INFERENCE BENCHMARK")
    print("="*60)
    
    model_manager = ModelManager(config)
    llm_manager = LLMManager(config, model_manager)
    tracker = PerformanceTracker()
    
    queries = [
        "Merhaba, nasılsın?",
        "Python nedir?",
        "2+2 kaç eder?",
        "Yapay zeka nedir?",
        "Bugün hava nasıl?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/5] Soru: {query}")
        
        tracker.start_operation('llm_inference')
        response = llm_manager.generate(query, stream=False)
        tracker.end_operation('llm_inference')
        
        print(f"Cevap: {response[:60]}...")
    
    # İstatistikler
    stats = tracker.get_statistics('llm_inference')
    
    print("\n" + "="*60)
    print("SONUÇLAR:")
    print("="*60)
    print(f"Toplam Sorgu: {stats['count']}")
    print(f"Toplam Süre: {stats['total_time']}s")
    print(f"Ortalama Süre: {stats['average_time']}s")
    print(f"Min Süre: {stats['min_time']}s")
    print(f"Max Süre: {stats['max_time']}s")
    
    # RTX 2060 Super için beklenen: 3-5s
    print("\n📊 Beklenen Performans (RTX 2060 Super):")
    print("   Ortalama: 3-5 saniye")
    
    if stats['average_time'] < 5:
        print("   ✅ Performans iyi!")
    elif stats['average_time'] < 7:
        print("   ⚠️  Performans kabul edilebilir")
    else:
        print("   ❌ Performans düşük, optimizasyon gerekli")


def benchmark_model_loading():
    """Model yükleme süreleri"""
    
    config = {
        'hardware': {'gpu_memory_limit': 7.5, 'model_unload_timeout': 30},
        'llm': {'model': 'qwen2.5:3b-instruct-q4_K_M'},
        'vlm': {'model': 'moondream'},
        'stt': {'model_size': 'medium', 'device': 'cuda', 'compute_type': 'int8'}
    }
    
    print("\n" + "="*60)
    print("MODEL LOADING BENCHMARK")
    print("="*60)
    
    model_manager = ModelManager(config)
    tracker = PerformanceTracker()
    
    models = ['llm', 'vlm', 'stt']
    
    for model_name in models:
        print(f"\n[TEST] {model_name.upper()} yükleniyor...")
        
        tracker.start_operation(f'{model_name}_load')
        try:
            model_manager.load_model(model_name)
            tracker.end_operation(f'{model_name}_load')
            
            vram = model_manager.get_vram_usage()
            print(f"VRAM: {vram:.2f}GB")
            
        except Exception as e:
            print(f"Hata: {e}")
    
    # İstatistikler
    print("\n" + "="*60)
    print("YÜKLEME SÜRELERİ:")
    print("="*60)
    
    for model_name in models:
        stats = tracker.get_statistics(f'{model_name}_load')
        if stats['count'] > 0:
            print(f"{model_name.upper()}: {stats['average_time']}s")


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        PERFORMANCE BENCHMARK                             ║
    ║        RTX 2060 Super (8GB VRAM)                         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    try:
        benchmark_model_loading()
    except Exception as e:
        print(f"\n❌ Model loading benchmark hatası: {e}")
    
    try:
        benchmark_llm_inference()
    except Exception as e:
        print(f"\n❌ LLM inference benchmark hatası: {e}")
    
    print("\n" + "="*60)
    print("BENCHMARK TAMAMLANDI")
    print("="*60)
