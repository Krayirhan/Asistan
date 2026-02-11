# Kurulum Scripti - Windows PowerShell
Write-Host "================================" -ForegroundColor Cyan
Write-Host "AI VOICE ASSISTANT - KURULUM" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# 1. Python kontrolü
Write-Host "`n[1/6] Python versiyonu kontrol ediliyor..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.(10|11)") {
    Write-Host "✓ Python bulundu: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python 3.10 veya 3.11 gerekli!" -ForegroundColor Red
    exit 1
}

# 2. CUDA kontrolü
Write-Host "`n[2/6] CUDA kontrol ediliyor..." -ForegroundColor Yellow
try {
    $cudaVersion = nvidia-smi 2>&1 | Select-String "CUDA Version"
    Write-Host "✓ CUDA bulundu" -ForegroundColor Green
} catch {
    Write-Host "⚠ CUDA bulunamadı! GPU özellikleri çalışmayabilir" -ForegroundColor Yellow
}

# 3. Virtual environment
Write-Host "`n[3/6] Virtual environment oluşturuluyor..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment zaten mevcut" -ForegroundColor Gray
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment oluşturuldu" -ForegroundColor Green
}

# 4. Activate
Write-Host "`n[4/6] Virtual environment aktive ediliyor..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# 5. Dependencies
Write-Host "`n[5/6] Dependencies yükleniyor (bu biraz zaman alabilir)..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies yüklendi" -ForegroundColor Green
} else {
    Write-Host "✗ Dependency yükleme hatası!" -ForegroundColor Red
    exit 1
}

# 6. .env dosyası
Write-Host "`n[6/6] .env dosyası oluşturuluyor..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env dosyası oluşturuldu" -ForegroundColor Green
} else {
    Write-Host ".env dosyası zaten mevcut" -ForegroundColor Gray
}

# Dizinleri oluştur
Write-Host "`nGerekli dizinler oluşturuluyor..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "cache" | Out-Null
New-Item -ItemType Directory -Force -Path "models" | Out-Null

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "KURULUM TAMAMLANDI!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan

Write-Host "`nSonraki Adımlar:" -ForegroundColor Yellow
Write-Host "1. Ollama'yı kurun: winget install Ollama.Ollama" -ForegroundColor White
Write-Host "2. Modelleri indirin:" -ForegroundColor White
Write-Host "   ollama pull qwen2.5:3b-instruct-q4_K_M" -ForegroundColor Gray
Write-Host "   ollama pull moondream" -ForegroundColor Gray
Write-Host "3. Çalıştırın:" -ForegroundColor White
Write-Host "   python src/main.py --mode console" -ForegroundColor Gray

Write-Host "`nDokümantasyon: README.md" -ForegroundColor Cyan
