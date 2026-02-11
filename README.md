# AI Sesli Asistan

RTX 2060 Super (8GB VRAM) icin optimize edilmis, tamamen acik kaynak Turkce sesli asistan.

[![Python](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![GPU](https://img.shields.io/badge/GPU-RTX%202060%20Super-orange.svg)]()

---

## Ozellikler

- Metin ve sesli sohbet (Gradio web arayuzu)
- Gercek zamanli internet arama (hava durumu, doviz, kripto, haberler)
- Gorsel analiz (resim yukle, soru sor)
- Turkce ses tanima ve ses sentezi
- Otomatik VRAM yonetimi

## Teknik Stack

| Bilesen | Model | Detay |
|---------|-------|-------|
| LLM | Qwen2.5-7B | Ollama, ~4GB VRAM |
| VLM | Moondream 2B | Ollama, ~1.7GB VRAM |
| STT | Faster-Whisper | Base, INT8, CPU |
| TTS | Piper TTS | Turkce (fettah-medium), CPU |
| Web Arama | DuckDuckGo + API | Open-Meteo, ExchangeRate, CoinGecko |
| UI | Gradio | Web arayuzu, 4 sekme |

**VRAM Kullanimi:** ~6GB / 8GB

---

## Kurulum

### 1. Gereksinimler

- Windows 10+
- Python 3.10
- NVIDIA GPU (8GB VRAM)
- Ollama

### 2. Ollama Kur

```bash
# Windows
winget install Ollama.Ollama

# Modelleri indir
ollama pull qwen2.5:7b
ollama pull moondream
```

### 3. Python Ortami

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. Calistir

```bash
# Web arayuzu
python src/main.py --mode gui

# Konsol
python src/main.py --mode console
```

Tarayicinizda `http://127.0.0.1:7861` acilir.

---

## Proje Yapisi

```
asistan/
├── config/
│   └── settings.yaml          # Tum ayarlar
├── src/
│   ├── core/
│   │   ├── llm_manager.py     # LLM + web arama entegrasyonu
│   │   ├── model_loader.py    # GPU/VRAM yonetimi
│   │   └── cache_manager.py   # Yanit cache
│   ├── audio/
│   │   ├── stt_engine.py      # Ses tanima (Whisper)
│   │   └── tts_engine.py      # Ses sentezi (Piper)
│   ├── tools/
│   │   ├── web_search.py      # Arama + API entegrasyonu
│   │   ├── image_handler.py   # Gorsel isleme
│   │   └── utils.py
│   ├── ui/
│   │   ├── gradio_ui.py       # Web arayuzu
│   │   └── console_ui.py      # Terminal arayuzu
│   ├── monitoring/
│   │   ├── vram_monitor.py    # VRAM takibi
│   │   ├── performance.py     # Performans metrikleri
│   │   └── logger.py
│   └── main.py
├── tests/
├── requirements.txt
├── LICENSE
└── README.md
```

## Lisans

Apache License 2.0

Kullanilan tum bilesenler ticari kullanima uygundur:
- Qwen2.5: Apache 2.0
- Moondream: Apache 2.0
- Faster-Whisper: MIT
- Piper TTS: MIT
- Ollama: MIT
