# Onceliklendirilmis Yapilacaklar

## P0 - Kritik
- [x] `smart_search` intent sirasini duzelt (`src/tools/web_search.py`).
- [x] `smart_search` regresyon testleri ekle (`tests/`): "bugun hava nasil", "bugun dolar kac".
- [x] `analyze_image` icin `try/finally` ile VLM unload garantisi ekle (`src/core/llm_manager.py`).
- [x] `ImageHandler` import/type hint hatasini duzelt; PIL yokken modul cokmesin (`src/tools/image_handler.py`).

## P1 - Yuksek
- [x] TTS model yolunu config'den okut (`src/audio/tts_engine.py`, `config/settings.yaml`).
- [x] Gradio `auth` ayarini `launch()` cagrisina bagla (`src/ui/gradio_ui.py`, `config/settings.yaml`).
- [x] STT `num_workers` degerini config'den yonet (`src/core/model_loader.py`, `config/settings.yaml`).
- [x] Cache icin `max_size_mb` limitini uygula (`src/core/cache_manager.py`).
- [x] Ollama model kontrolunu string arama yerine guvenli parse ile yap (`src/core/model_loader.py`).

## P2 - Iyilestirme
- [x] Testleri `unit` ve `integration` olarak ayir, marker ekle (`tests/`).
- [x] `test_tts_engine` assertion'ini anlamli hale getir (`tests/test_audio.py`).
- [x] `pynvml` -> `nvidia-ml-py` gecis planini uygula (`requirements.txt`, `src/monitoring/*`, `src/core/model_loader.py`).
- [x] Config yolunu calisma dizininden bagimsiz hale getir (`src/main.py`).
- [x] CI ekle: lint + unit test + compile check (`.github/workflows/`).


