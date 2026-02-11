#!/bin/bash

# Kurulum Scripti - Linux/macOS

echo "================================"
echo "AI VOICE ASSISTANT - KURULUM"
echo "================================"

# 1. Python kontrolü
echo -e "\n[1/6] Python versiyonu kontrol ediliyor..."
python_version=$(python3 --version 2>&1)
if [[ $python_version =~ Python\ 3\.(10|11) ]]; then
    echo "✓ Python bulundu: $python_version"
else
    echo "✗ Python 3.10 veya 3.11 gerekli!"
    exit 1
fi

# 2. CUDA kontrolü
echo -e "\n[2/6] CUDA kontrol ediliyor..."
if command -v nvidia-smi &> /dev/null; then
    echo "✓ CUDA bulundu"
else
    echo "⚠ CUDA bulunamadı! GPU özellikleri çalışmayabilir"
fi

# 3. Virtual environment
echo -e "\n[3/6] Virtual environment oluşturuluyor..."
if [ -d "venv" ]; then
    echo "Virtual environment zaten mevcut"
else
    python3 -m venv venv
    echo "✓ Virtual environment oluşturuldu"
fi

# 4. Activate
echo -e "\n[4/6] Virtual environment aktive ediliyor..."
source venv/bin/activate

# 5. Dependencies
echo -e "\n[5/6] Dependencies yükleniyor (bu biraz zaman alabilir)..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies yüklendi"
else
    echo "✗ Dependency yükleme hatası!"
    exit 1
fi

# 6. .env dosyası
echo -e "\n[6/6] .env dosyası oluşturuluyor..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env dosyası oluşturuldu"
else
    echo ".env dosyası zaten mevcut"
fi

# Dizinleri oluştur
echo -e "\nGerekli dizinler oluşturuluyor..."
mkdir -p logs cache models

echo -e "\n================================"
echo "KURULUM TAMAMLANDI!"
echo "================================"

echo -e "\nSonraki Adımlar:"
echo "1. Ollama'yı kurun:"
echo "   Linux: curl -fsSL https://ollama.com/install.sh | sh"
echo "   macOS: brew install ollama"
echo ""
echo "2. Modelleri indirin:"
echo "   ollama pull qwen2.5:3b-instruct-q4_K_M"
echo "   ollama pull moondream"
echo ""
echo "3. Çalıştırın:"
echo "   source venv/bin/activate"
echo "   python src/main.py --mode console"
echo ""
echo "Dokümantasyon: README.md"
