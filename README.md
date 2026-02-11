# AI Sesli Asistan

RTX 2060 Super (8GB VRAM) için optimize edilmiş, tamamen açık kaynak Türkçe sesli asistan.

[![Python](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![GPU](https://img.shields.io/badge/GPU-RTX%202060%20Super-orange.svg)]()

---

## Özellikler

- Metin ve sesli sohbet (Gradio web arayüzü)
- Gerçek zamanlı internet arama (hava durumu, döviz, kripto, haberler)
- Görsel analiz (resim yükle, soru sor)
- Türkçe ses tanıma ve ses sentezi
- Otomatik VRAM yönetimi

## Teknik Stack

| Bileşen | Model | Detay |
|---------|-------|-------|
| LLM | Qwen2.5-7B | Ollama, ~4GB VRAM |
| VLM | Moondream 2B | Ollama, ~1.7GB VRAM |
| STT | Faster-Whisper | Base, INT8, CPU |
| TTS | Piper TTS | Türkçe (fettah-medium), CPU |
| Web Arama | DuckDuckGo + API | Open-Meteo, ExchangeRate, CoinGecko |
| UI | Gradio | Web arayüzü, 4 sekme |

**VRAM Kullanımı:** ~6GB / 8GB

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

### 3. Python Ortamı

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. Çalıştır

```bash
# Web arayüzü
python src/main.py --mode gui

# Konsol
python src/main.py --mode console
```

Tarayıcınızda `http://127.0.0.1:7861` açılır.

---

## Proje Yapısı

```
asistan/
├── config/
│   └── settings.yaml          # Tüm ayarlar
├── src/
│   ├── core/
│   │   ├── llm_manager.py     # LLM + web arama entegrasyonu
│   │   ├── model_loader.py    # GPU/VRAM yönetimi
│   │   └── cache_manager.py   # Yanıt cache
│   ├── audio/
│   │   ├── stt_engine.py      # Ses tanıma (Whisper)
│   │   └── tts_engine.py      # Ses sentezi (Piper)
│   ├── tools/
│   │   ├── web_search.py      # Arama + API entegrasyonu
│   │   ├── image_handler.py   # Görsel işleme
│   │   └── utils.py
│   ├── ui/
│   │   ├── gradio_ui.py       # Web arayüzü
│   │   └── console_ui.py      # Terminal arayüzü
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

Kullanılan tüm bileşenler ticari kullanıma uygundur:
- Qwen2.5: Apache 2.0
- Moondream: Apache 2.0
- Faster-Whisper: MIT
- Piper TTS: MIT
- Ollama: MIT
