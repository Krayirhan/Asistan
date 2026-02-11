# AI Voice Assistant - Quick Start Guide

## 🎯 En Hızlı Kurulum (Windows)

### 1. Gereksinimler Kontrol
- ✅ Windows 10 veya 11
- ✅ Python 3.10 veya 3.11 ([İndir](https://www.python.org/downloads/))
- ✅ NVIDIA GPU (RTX 2060 Super veya üzeri)
- ✅ CUDA 11.8+ ([İndir](https://developer.nvidia.com/cuda-downloads))

### 2. PowerShell'de Tek Komut
```powershell
# Projeyi klonlayın/indirin
cd d:\asistan

# Kurulum scriptini çalıştırın
.\setup.ps1
```

### 3. Ollama Kur
```powershell
# Windows Package Manager ile
winget install Ollama.Ollama

# Manuel: https://ollama.com/download/windows
```

### 4. Modelleri İndir
```powershell
# LLM
ollama pull qwen2.5:3b-instruct-q4_K_M

# VLM
ollama pull moondream
```

### 5. Çalıştır!
```powershell
# Virtual environment'ı aktive et
venv\Scripts\activate

# Console modu
python src/main.py --mode console

# Sesli mod
python src/main.py --mode voice

# Web arayüzü
python src/main.py --mode gui
```

---

## 🐧 Linux Kurulum

```bash
# Kurulum script
chmod +x setup.sh
./setup.sh

# Ollama kur
curl -fsSL https://ollama.com/install.sh | sh

# Modelleri indir
ollama pull qwen2.5:3b-instruct-q4_K_M
ollama pull moondream

# Çalıştır
source venv/bin/activate
python src/main.py --mode console
```

---

## 🍎 macOS Kurulum

```bash
# Kurulum script
chmod +x setup.sh
./setup.sh

# Ollama kur
brew install ollama

# Modelleri indir
ollama pull qwen2.5:3b-instruct-q4_K_M
ollama pull moondream

# Çalıştır
source venv/bin/activate
python src/main.py --mode console
```

---

## ⚡ İlk Kullanım

### Console Modu
```bash
You: Merhaba
🤖 Assistant: Merhaba! Size nasıl yardımcı olabilirim?

You: /voice
🎤 5 saniye konuşun...
[Konuşun]

You: /image cat.jpg
📸 Görsel analiz ediliyor...

You: /search Python nedir
🔍 Web'de aranıyor...
```

### Sesli Mod
```bash
python src/main.py --mode voice

🎤 "Hey Assistant" deyin...
[Wake word algılandı]
🟢 Dinliyorum...
[Soru sorun]
🤖 [Sesli cevap]
```

### Web Arayüzü
```bash
python src/main.py --mode gui

Running on: http://127.0.0.1:7860
# Tarayıcınızda açılır
```

---

## 🔧 Özelleştirme

### VRAM Limiti Ayarla
```yaml
# config/settings.yaml
hardware:
  gpu_memory_limit: 6.0  # GB (8GB yerine 6GB)
```

### Daha Küçük Model
```yaml
llm:
  model: "qwen2.5:1.5b-instruct-q4_K_M"  # 1.5B daha hafif
```

### Türkçe Wake Word
```yaml
wake_word:
  keyword: "asistan"  # Türkçe wake word
```

---

## ❓ Sık Sorulan Sorular

**S: Kurulum ne kadar sürer?**  
C: İlk kurulum 10-15 dakika, model indirme 5-10 dakika.

**S: İnternet gerekli mi?**  
C: Sadece ilk kurulum ve web araması için. Model çalışması offline.

**S: CPU'da çalışır mı?**  
C: Evet ama çok yavaş. GPU şiddetle önerilir.

**S: Türkçe konuşabilir mi?**  
C: Evet! Hem anlama hem konuşma Türkçe destekli.

---

## 🆘 Yardım

Sorun mu yaşıyorsunuz? 

1. [Troubleshooting](README.md#-troubleshooting) bölümüne bakın
2. [GitHub Issues](../../issues) açın
3. Log dosyalarını kontrol edin: `logs/app_YYYY-MM-DD.log`

---

**Hazır! Artık AI asistanınızla konuşabilirsiniz! 🎉**
