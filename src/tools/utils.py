"""
Utility Functions - Yardımcı fonksiyonlar
"""

import re
from datetime import datetime, timedelta
from typing import Optional


def format_time(seconds: float) -> str:
    """
    Saniyeyi okunabilir formata çevir
    
    Args:
        seconds: Saniye
    
    Returns:
        Formatlı zaman (örn: "2m 30s")
    """
    
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Metni kısalt
    
    Args:
        text: Metin
        max_length: Maksimum uzunluk
        suffix: Ek (varsayılan "...")
    
    Returns:
        Kısaltılmış metin
    """
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def is_url(text: str) -> bool:
    """
    Metin bir URL mi?
    
    Args:
        text: Kontrol edilecek metin
    
    Returns:
        URL mi?
    """
    
    url_pattern = re.compile(
        r'^https?://'  # http:// veya https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # port (opsiyonel)
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    return bool(url_pattern.match(text))


def clean_text(text: str) -> str:
    """
    Metni temizle (fazla boşluklar, yeni satırlar vb.)
    
    Args:
        text: Ham metin
    
    Returns:
        Temizlenmiş metin
    """
    
    # Fazla boşlukları tek boşluğa çevir
    text = re.sub(r'\s+', ' ', text)
    
    # Başındaki ve sonundaki boşlukları sil
    text = text.strip()
    
    return text


def extract_code_blocks(text: str) -> list:
    """
    Metindeki kod bloklarını çıkar (Markdown formatında)
    
    Args:
        text: Markdown metni
    
    Returns:
        Kod blokları listesi
    """
    
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    return [{'language': lang, 'code': code.strip()} for lang, code in matches]


def format_file_size(size_bytes: int) -> str:
    """
    Byte'ı okunabilir formata çevir
    
    Args:
        size_bytes: Byte cinsinden boyut
    
    Returns:
        Formatlı boyut (örn: "1.5 MB")
    """
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} PB"


def get_timestamp(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Mevcut zaman damgası
    
    Args:
        format: Tarih formatı
    
    Returns:
        Formatlı tarih
    """
    
    return datetime.now().strftime(format)


def parse_duration(duration_str: str) -> Optional[int]:
    """
    Süre stringini saniyeye çevir
    
    Args:
        duration_str: Süre (örn: "5s", "2m", "1h")
    
    Returns:
        Saniye (int) veya None
    """
    
    pattern = r'^(\d+)([smh])$'
    match = re.match(pattern, duration_str.lower())
    
    if not match:
        return None
    
    value, unit = match.groups()
    value = int(value)
    
    if unit == 's':
        return value
    elif unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600
    
    return None


def highlight_keywords(text: str, keywords: list, color: str = "yellow") -> str:
    """
    Metindeki anahtar kelimeleri vurgula (terminal için)
    
    Args:
        text: Metin
        keywords: Vurgulanacak kelimeler
        color: Renk (yellow, green, red, blue)
    
    Returns:
        Vurgulanmış metin
    """
    
    color_codes = {
        'yellow': '\033[93m',
        'green': '\033[92m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'reset': '\033[0m'
    }
    
    code = color_codes.get(color, color_codes['yellow'])
    reset = color_codes['reset']
    
    for keyword in keywords:
        # Case-insensitive vurgulama
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        text = pattern.sub(f"{code}\\g<0>{reset}", text)
    
    return text


def validate_config(config: dict, required_keys: list) -> bool:
    """
    Config dosyasını doğrula
    
    Args:
        config: Konfigürasyon dict'i
        required_keys: Gerekli anahtarlar
    
    Returns:
        Geçerli mi?
    """
    
    for key in required_keys:
        if key not in config:
            return False
    
    return True
