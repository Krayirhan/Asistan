# 🎤 AI Voice Assistant - RTX 2060 Super Optimized

**8GB VRAM için optimize edilmiş, tamamen açık kaynak ve ücretsiz araçlarla çalışan akıllı sesli asistan.**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![VRAM](https://img.shields.io/badge/VRAM-8GB-orange.svg)]()
[![GPU](https://img.shields.io/badge/GPU-RTX%202060%20Super-green.svg)]()

---

## 📋 Özellikler

✨ **İletişim Modları**
- ✅ Metin girişi (konsol veya GUI)
- ✅ Sesli girdi (mikrofon ile konuşma)
- ✅ Wake word aktivasyonu ("Hey Assistant")
- ✅ Metin çıktısı (renkli terminal + Markdown)
- ✅ Sesli çıktı (Kokoro TTS ile doğal Türkçe ses)
- ✅ Hybrid mode (hem yazı hem ses)

🤖 **AI Yetenekleri**
- ✅ Akıllı sohbet (Qwen2.5-3B)
- ✅ Görsel anlama (Moondream - "Bu ne?" soruları)
- ✅ İnternet araması (DuckDuckGo entegrasyonu)
- ✅ Türkçe-İngilizce çift dil
- ✅ Konuşma geçmişi (sliding window)
- ✅ Bağlam anlama

⚡ **Performans Optimizasyonları**
- ✅ GPU Memory Pooling
- ✅ Async Processing
- ✅ Response Caching
- ✅ Auto Model Unload (30s timeout)
- ✅ Mixed Precision (FP16)
- ✅ Lazy Loading

---

## 🛠️ Teknik Stack

| Bileşen | Model | VRAM Kullanımı |
|---------|-------|----------------|
| **LLM** | Qwen2.5-3B (4-bit) | ~2GB |
| **VLM** | Moondream 0.5B | ~1GB |
| **STT** | Faster-Whisper Medium (INT8) | ~1GB |
| **TTS** | Kokoro-82M (CPU) | 0GB |
| **Wake Word** | Porcupine (CPU) | 0GB |

**Maksimum VRAM Kullanımı:** ~3.5GB / 8GB ✅

---

## 🚀 Hızlı Başlangıç

### 1️⃣ Gereksinimler

```yaml
OS: Windows 10+, Linux, macOS
Python: 3.10 veya 3.11
GPU: NVIDIA RTX 2060 Super (8GB VRAM) veya üzeri
CUDA: 11.8 veya 12.1
RAM: 16GB (32GB ideal)
Disk: 15GB boş alan
```

### 2️⃣ Ollama Kurulumu

```bash
# Windows (PowerShell - Admin)
winget install Ollama.Ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama
```

### 3️⃣ Modelleri İndirin

```bash
# LLM - 3B model (hafif ve güçlü)
ollama pull qwen2.5:3b-instruct-q4_K_M

# VLM - Görsel analiz
ollama pull moondream

# Test
ollama run qwen2.5:3b-instruct-q4_K_M "Merhaba"
```

### 4️⃣ Python Ortamı

```bash
# Virtual environment
python -m venv venv

# Aktive et (Windows)
venv\Scripts\activate

# Aktive et (Linux/Mac)
source venv/bin/activate

# Dependencies
pip install -r requirements.txt
```

### 5️⃣ Konfigürasyon

```bash
# .env dosyası oluştur
copy .env.example .env

# (Opsiyonel) Ayarları düzenle
notepad .env
```

### 6️⃣ Çalıştır!

```bash
# Console modu
python src/main.py --mode console

# Sesli mod (Wake word ile)
python src/main.py --mode voice

# Web arayüzü
python src/main.py --mode gui
```

---

## 💬 Kullanım Örnekleri

### Console Modu

```bash
$ python src/main.py --mode console

🎤 AI Assistant Ready!
VRAM: 2.3GB / 8GB

You: Merhaba, nasılsın?
🤖 Assistant: Merhaba! İyiyim, teşekkür ederim. Size nasıl yardımcı olabilirim?

You: Python'da liste nasıl oluşturulur?
🤖 Assistant: Python'da liste oluşturmak için köşeli parantez kullanılır:

```python
my_list = [1, 2, 3, 4, 5]
names = ["Ali", "Ayşe", "Mehmet"]
```

You: /image cat.jpg Bu ne?
📸 Görsel analiz ediliyor...
🤖 Assistant: Bu resimde turuncu renkli, yeşil gözlü bir kedi görüyorum...
```

### Sesli Mod

```bash
$ python src/main.py --mode voice

🎤 Wake Word aktif! "Hey Assistant" deyin...

[Kullanıcı: "Hey Assistant"]
🟢 Dinliyorum... (5 saniye konuşun)

[Kullanıcı konuşuyor: "Bugün hava nasıl?"]
🔍 İnternet arama...
🤖 "Ankara'da bugün 15 derece ve güneşli." [Sesli okuyor]
```

### Web Arayüzü (Gradio)

```bash
$ python src/main.py --mode gui

Running on local URL:  http://127.0.0.1:7860
```

Tarayıcınızda açılır! 🌐

---

## 📁 Proje Yapısı

```
ai-voice-assistant/
├── config/                    # Konfigürasyon dosyaları
│   ├── settings.yaml         # Ana ayarlar
│   ├── prompts.yaml          # System promptlar
│   └── models.yaml           # Model spesifikasyonları
│
├── src/
│   ├── core/                 # Ana bileşenler
│   │   ├── model_loader.py   # Akıllı model yönetimi
│   │   ├── llm_manager.py    # LLM işlemleri
│   │   ├── memory_manager.py # Konuşma geçmişi
│   │   └── cache_manager.py  # Response cache
│   │
│   ├── audio/                # Ses işleme
│   │   ├── stt_engine.py     # Speech-to-Text
│   │   ├── tts_engine.py     # Text-to-Speech
│   │   ├── wake_word.py      # Wake word detector
│   │   └── audio_processor.py
│   │
│   ├── tools/                # Yardımcı araçlar
│   │   ├── web_search.py     # DuckDuckGo arama
│   │   ├── image_handler.py  # Görsel işleme
│   │   └── utils.py
│   │
│   ├── ui/                   # Kullanıcı arayüzleri
│   │   ├── console_ui.py     # Terminal UI
│   │   ├── voice_ui.py       # Sesli UI
│   │   └── gradio_ui.py      # Web UI
│   │
│   ├── monitoring/           # İzleme
│   │   ├── vram_monitor.py   # VRAM takibi
│   │   ├── performance.py    # Performans metrikleri
│   │   └── logger.py
│   │
│   └── main.py               # Ana entry point
│
├── tests/                    # Test dosyaları
│   ├── test_vram.py
│   ├── test_llm.py
│   ├── test_audio.py
│   └── benchmark.py
│
├── requirements.txt
├── README.md
└── LICENSE
```

---

## ⚙️ Konfigürasyon

### Ana Ayarlar (`config/settings.yaml`)

```yaml
# Hardware
hardware:
  gpu_memory_limit: 7.5  # GB
  model_unload_timeout: 30  # saniye
  mixed_precision: true

# LLM
llm:
  model: "qwen2.5:3b-instruct-q4_K_M"
  max_tokens: 1024
  temperature: 0.7
  context_length: 15  # mesaj

# STT
stt:
  model_size: "medium"  # tiny, small, medium
  device: "cuda"
  compute_type: "int8"  # daha az VRAM
  language: "tr"

# TTS
tts:
  model: "kokoro-82m"
  device: "cpu"  # VRAM tasarrufu
  voice: "af_sky"

# Wake Word
wake_word:
  enabled: true
  keyword: "jarvis"  # veya "computer", "hey google"
  sensitivity: 0.5
```

---

## 🎮 Komutlar

### Console Modu Komutları

| Komut | Açıklama |
|-------|----------|
| `/voice` | Sesli mod (mikrofon ile konuş) |
| `/image <path>` | Resim analizi |
| `/search <query>` | Web araması |
| `/clear` | Geçmişi temizle |
| `/exit` | Çıkış |

---

## 📊 Performans Beklentileri

| İşlem | RTX 2060 Super | Açıklama |
|-------|----------------|----------|
| İlk Başlatma | 15-20 sn | Model yükleme |
| Qwen2.5 Cevap | 3-5 sn | 100 kelime |
| Whisper STT | 0.3-0.5 sn | 5 sn konuşma |
| Moondream Görsel | 2-3 sn | Tek resim |
| Kokoro TTS | 2-3 sn | 1 cümle |
| Wake Word | <0.1 sn | Anında |
| **VRAM Kullanımı** | **3-4 GB** | Peak |

---

## 🧪 Testler

```bash
# VRAM optimizasyon testi
python tests/test_vram.py

# LLM testleri
python tests/test_llm.py

# Audio testleri
python tests/test_audio.py

# Performans benchmark
python tests/benchmark.py
```

---

## 🐛 Troubleshooting

### ❌ "CUDA out of memory"

```yaml
# config/settings.yaml
hardware:
  gpu_memory_limit: 6.0  # Daha düşük

llm:
  model: "qwen2.5:1.5b-instruct-q4_K_M"  # Daha küçük model
```

### ❌ "Ollama connection refused"

```bash
# Ollama servisini başlat
ollama serve

# Veya Windows Services'tan "Ollama" başlat
```

### ❌ Ses kalitesi kötü

```yaml
# config/settings.yaml
stt:
  vad_filter: true  # Gürültü filtreleme
  model_size: "large-v2"  # Daha iyi model
```

---

## 📝 Lisans

Apache License 2.0 - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

**Kullanılan Tüm Bileşenler Ticari Kullanıma Uygun:**
- Qwen2.5: Apache 2.0 ✅
- Moondream: Apache 2.0 ✅
- Whisper: MIT ✅
- Kokoro: Apache 2.0 ✅
- Porcupine: Apache 2.0 ✅
- Ollama: MIT ✅

---

## 🙏 Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır!

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

---

## 📧 İletişim

Sorularınız için GitHub Issues kullanabilirsiniz.

---

## 🌟 Teşekkürler

- [Qwen Team](https://github.com/QwenLM/Qwen2.5) - LLM
- [Moondream](https://moondream.ai/) - VLM
- [OpenAI](https://github.com/openai/whisper) - Whisper
- [Ollama](https://ollama.com/) - Model Runtime
- [Picovoice](https://picovoice.ai/) - Wake Word

---

**🎤 Happy Coding!**
