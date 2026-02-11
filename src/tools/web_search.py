"""
Web Search Tool - Tam Optimize Versiyon
========================================
- Open-Meteo API: Hava durumu (81 il + ilceler)
- ExchangeRate API: Doviz kurlari (ucretsiz, guncel)
- CoinGecko API: Kripto paralar (ucretsiz)
- DuckDuckGo: Genel arama + haberler
- Akilli cache sistemi
- Sonuc filtreleme ve kalite kontrolu
"""

import re
import time
from datetime import datetime
from typing import List, Dict, Optional
from loguru import logger

try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    logger.warning("ddgs yuklu degil! pip install ddgs")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests yuklu degil")


# ==============================================================
# SEHIR VERITABANI (81 il + populer ilceler + alias'lar)
# ==============================================================
SEHIR_ALIASES = {
    'istanbul': 'Istanbul', 'ist': 'Istanbul',
    'ankara': 'Ankara', 'ank': 'Ankara',
    'izmir': 'Izmir',
    'antalya': 'Antalya',
    'bursa': 'Bursa',
    'adana': 'Adana',
    'konya': 'Konya',
    'gaziantep': 'Gaziantep', 'antep': 'Gaziantep',
    'diyarbakir': 'Diyarbakir',
    'kayseri': 'Kayseri',
    'eskisehir': 'Eskisehir',
    'trabzon': 'Trabzon',
    'samsun': 'Samsun',
    'mersin': 'Mersin', 'icel': 'Mersin',
    'mugla': 'Mugla',
    'denizli': 'Denizli',
    'malatya': 'Malatya',
    'kahramanmaras': 'Kahramanmaras', 'maras': 'Kahramanmaras',
    'van': 'Van',
    'erzurum': 'Erzurum',
    'sakarya': 'Sakarya', 'adapazari': 'Sakarya',
    'kocaeli': 'Kocaeli', 'izmit': 'Kocaeli',
    'sanliurfa': 'Sanliurfa', 'urfa': 'Sanliurfa',
    'hatay': 'Hatay', 'antakya': 'Hatay',
    'manisa': 'Manisa',
    'balikesir': 'Balikesir',
    'edirne': 'Edirne',
    'tekirdag': 'Tekirdag',
    'ordu': 'Ordu',
    'rize': 'Rize',
    'artvin': 'Artvin',
    'bolu': 'Bolu',
    'duzce': 'Duzce',
    'yalova': 'Yalova',
    'canakkale': 'Canakkale',
    'bodrum': 'Bodrum', 'marmaris': 'Marmaris', 'fethiye': 'Fethiye',
    'alanya': 'Alanya', 'kemer': 'Kemer', 'kas': 'Kas',
    'kusadasi': 'Kusadasi', 'cesme': 'Cesme',
    'didim': 'Didim', 'side': 'Side',
    'afyon': 'Afyon', 'afyonkarahisar': 'Afyon',
    'aksaray': 'Aksaray', 'amasya': 'Amasya',
    'ardahan': 'Ardahan', 'bartin': 'Bartin',
    'batman': 'Batman', 'bayburt': 'Bayburt',
    'bilecik': 'Bilecik', 'bingol': 'Bingol',
    'bitlis': 'Bitlis', 'burdur': 'Burdur',
    'cankiri': 'Cankiri', 'corum': 'Corum',
    'elazig': 'Elazig', 'erzincan': 'Erzincan',
    'giresun': 'Giresun', 'gumushane': 'Gumushane',
    'hakkari': 'Hakkari', 'igdir': 'Igdir',
    'isparta': 'Isparta', 'karabuk': 'Karabuk',
    'karaman': 'Karaman', 'kars': 'Kars',
    'kastamonu': 'Kastamonu', 'kilis': 'Kilis',
    'kirikkale': 'Kirikkale', 'kirklareli': 'Kirklareli',
    'kirsehir': 'Kirsehir', 'kutahya': 'Kutahya',
    'mardin': 'Mardin', 'mus': 'Mus',
    'nevsehir': 'Nevsehir', 'nigde': 'Nigde',
    'osmaniye': 'Osmaniye', 'siirt': 'Siirt',
    'sinop': 'Sinop', 'sirnak': 'Sirnak',
    'sivas': 'Sivas', 'tokat': 'Tokat',
    'tunceli': 'Tunceli', 'usak': 'Usak',
    'yozgat': 'Yozgat', 'zonguldak': 'Zonguldak',
}

# Sehir koordinatlari (81 il + populer ilceler)
SEHIR_COORDS = {
    'Istanbul': (41.01, 28.98), 'Ankara': (39.93, 32.86),
    'Izmir': (38.42, 27.14), 'Antalya': (36.89, 30.69),
    'Bursa': (40.19, 29.06), 'Adana': (37.00, 35.33),
    'Konya': (37.87, 32.48), 'Gaziantep': (37.06, 37.38),
    'Diyarbakir': (37.91, 40.24), 'Kayseri': (38.73, 35.49),
    'Eskisehir': (39.78, 30.52), 'Trabzon': (41.00, 39.72),
    'Samsun': (41.29, 36.33), 'Mersin': (36.80, 34.63),
    'Mugla': (37.22, 28.36), 'Denizli': (37.77, 29.09),
    'Malatya': (38.35, 38.31), 'Kahramanmaras': (37.59, 36.94),
    'Van': (38.49, 43.38), 'Erzurum': (39.91, 41.28),
    'Sakarya': (40.69, 30.40), 'Kocaeli': (40.77, 29.92),
    'Sanliurfa': (37.16, 38.79), 'Hatay': (36.40, 36.35),
    'Manisa': (38.61, 27.43), 'Balikesir': (39.65, 27.89),
    'Edirne': (41.68, 26.56), 'Tekirdag': (41.00, 27.52),
    'Ordu': (41.00, 37.88), 'Rize': (41.02, 40.52),
    'Artvin': (41.18, 41.82), 'Bolu': (40.73, 31.61),
    'Duzce': (40.84, 31.16), 'Yalova': (40.66, 29.27),
    'Canakkale': (40.15, 26.41),
    'Bodrum': (37.04, 27.43), 'Marmaris': (36.85, 28.27),
    'Fethiye': (36.65, 29.12), 'Alanya': (36.54, 32.00),
    'Kemer': (36.60, 30.56), 'Kas': (36.20, 29.64),
    'Kusadasi': (37.86, 27.26), 'Cesme': (38.32, 26.30),
    'Didim': (37.37, 27.27), 'Side': (36.77, 31.39),
    'Afyon': (38.75, 30.54), 'Aksaray': (38.37, 34.03),
    'Amasya': (40.65, 35.83), 'Ardahan': (41.11, 42.70),
    'Bartin': (41.64, 32.34), 'Batman': (37.88, 41.13),
    'Bayburt': (40.26, 40.22), 'Bilecik': (40.05, 30.00),
    'Bingol': (38.88, 40.50), 'Bitlis': (38.40, 42.11),
    'Burdur': (37.72, 30.29), 'Cankiri': (40.60, 33.62),
    'Corum': (40.55, 34.95), 'Elazig': (38.67, 39.22),
    'Erzincan': (39.75, 39.49), 'Giresun': (40.91, 38.39),
    'Gumushane': (40.46, 39.48), 'Hakkari': (37.58, 43.74),
    'Igdir': (39.92, 44.05), 'Isparta': (37.76, 30.55),
    'Karabuk': (41.20, 32.63), 'Karaman': (37.18, 33.23),
    'Kars': (40.60, 43.10), 'Kastamonu': (41.39, 33.78),
    'Kilis': (36.72, 37.12), 'Kirikkale': (39.85, 33.51),
    'Kirklareli': (41.73, 27.23), 'Kirsehir': (39.15, 34.17),
    'Kutahya': (39.42, 29.98), 'Mardin': (37.31, 40.73),
    'Mus': (38.95, 41.75), 'Nevsehir': (38.63, 34.71),
    'Nigde': (37.97, 34.68), 'Osmaniye': (37.07, 36.25),
    'Siirt': (37.93, 42.00), 'Sinop': (42.03, 35.15),
    'Sirnak': (37.51, 42.46), 'Sivas': (39.75, 37.01),
    'Tokat': (40.31, 36.55), 'Tunceli': (39.11, 39.55),
    'Usak': (38.67, 29.41), 'Yozgat': (39.82, 34.80),
    'Zonguldak': (41.45, 31.80),
}


class WebSearchTool:
    """Tam optimize web aramasi - API'ler + DuckDuckGo + Cache"""

    def __init__(self, config: dict):
        self.config = config.get('web_search', {})
        self.enabled = self.config.get('enabled', True)
        self.max_results = self.config.get('max_results', 5)
        self.timeout = self.config.get('timeout', 10)

        # Cache sistemi (RAM'de)
        self._cache = {}
        self._cache_ttl = self.config.get('cache_ttl', 300)  # 5 dakika

        if not DDGS_AVAILABLE:
            logger.error("DuckDuckGo search yuklu degil!")
            self.enabled = False

    # ==============================================================
    # CACHE SİSTEMİ
    # ==============================================================

    def _get_cache(self, key: str) -> Optional[str]:
        """Cache'den veri al"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                logger.info(f"Cache hit: {key}")
                return data
            else:
                del self._cache[key]
        return None

    def _set_cache(self, key: str, value: str):
        """Cache'e veri yaz"""
        self._cache[key] = (value, time.time())
        if len(self._cache) > 100:
            oldest_key = min(self._cache, key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]

    # ==============================================================
    # HAVA DURUMU - Open-Meteo API
    # ==============================================================

    def get_weather(self, city: str) -> Optional[str]:
        """Sehir icin gercek hava durumu verisi"""
        city_query = self._resolve_city(city)

        cache_key = f"weather_{city_query}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        coords = SEHIR_COORDS.get(city_query)
        if not coords:
            logger.warning(f"Koordinat bulunamadi: {city} -> {city_query}")
            return self._weather_search_fallback(city)

        logger.info(f"Open-Meteo API: {city} -> {city_query} ({coords[0]}, {coords[1]})")

        weather = self._fetch_open_meteo(city_query, coords[0], coords[1])
        if weather:
            self._set_cache(cache_key, weather)
            return weather

        return self._weather_search_fallback(city)

    def _fetch_open_meteo(self, city: str, lat: float, lon: float) -> Optional[str]:
        """Open-Meteo API ile gercek hava durumu"""
        if not REQUESTS_AVAILABLE:
            return None

        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
                f"weather_code,wind_speed_10m,wind_direction_10m,precipitation"
                f"&daily=temperature_2m_max,temperature_2m_min,weather_code,"
                f"precipitation_probability_max"
                f"&timezone=Europe/Istanbul&forecast_days=3"
            )

            response = requests.get(url, timeout=8)

            if response.status_code != 200:
                logger.warning(f"Open-Meteo HTTP {response.status_code}")
                return None

            data = response.json()
            current = data.get('current', {})
            daily = data.get('daily', {})

            temp = current.get('temperature_2m', '?')
            feels = current.get('apparent_temperature', '?')
            humidity = current.get('relative_humidity_2m', '?')
            wind = current.get('wind_speed_10m', '?')
            weather_code = current.get('weather_code', 0)

            weather_desc = self._wmo_to_turkish(weather_code)

            today_max = daily.get('temperature_2m_max', ['?'])[0]
            today_min = daily.get('temperature_2m_min', ['?'])[0]
            rain_prob = daily.get('precipitation_probability_max', [0])[0]

            # Yarin tahmini
            tomorrow_line = ""
            max_list = daily.get('temperature_2m_max', [])
            min_list = daily.get('temperature_2m_min', [])
            codes = daily.get('weather_code', [])
            rain_probs = daily.get('precipitation_probability_max', [])

            if len(max_list) > 1:
                tomorrow_desc = self._wmo_to_turkish(codes[1]) if len(codes) > 1 else ""
                tomorrow_rain = rain_probs[1] if len(rain_probs) > 1 else 0
                tomorrow_line = (
                    f"\nYarin: {min_list[1]}C / {max_list[1]}C, "
                    f"{tomorrow_desc}, yagis ihtimali: %{tomorrow_rain}"
                )

            result = (
                f"Anlik sicaklik: {temp}C\n"
                f"Hissedilen: {feels}C\n"
                f"Durum: {weather_desc}\n"
                f"Nem: %{humidity}\n"
                f"Ruzgar: {wind} km/sa\n"
                f"Bugun en dusuk: {today_min}C, en yuksek: {today_max}C\n"
                f"Yagis ihtimali: %{rain_prob}"
                f"{tomorrow_line}"
            )

            logger.success(f"Open-Meteo: {city} -> {temp}C (hissedilen {feels}C)")
            return result

        except requests.exceptions.Timeout:
            logger.warning("Open-Meteo zaman asimi!")
            return None
        except Exception as e:
            logger.warning(f"Open-Meteo hatasi: {e}")
            return None

    def _wmo_to_turkish(self, code: int) -> str:
        """WMO hava kodu -> Turkce aciklama"""
        wmo_codes = {
            0: 'Acik', 1: 'Cogunlukla acik', 2: 'Parcali bulutlu', 3: 'Kapali',
            45: 'Sisli', 48: 'Kiragili sis',
            51: 'Hafif ciseleme', 53: 'Orta ciseleme', 55: 'Yogun ciseleme',
            61: 'Hafif yagmur', 63: 'Orta yagmur', 65: 'Siddetli yagmur',
            66: 'Dondurucu hafif yagmur', 67: 'Dondurucu siddetli yagmur',
            71: 'Hafif kar', 73: 'Orta kar', 75: 'Yogun kar',
            77: 'Kar taneleri', 80: 'Hafif saganak', 81: 'Orta saganak',
            82: 'Siddetli saganak',
            85: 'Hafif kar saganagi', 86: 'Yogun kar saganagi',
            95: 'Gok gurultulu firtina', 96: 'Dolu ile firtina',
            99: 'Siddetli dolu ile firtina',
        }
        return wmo_codes.get(code, 'Bilinmiyor')

    # ==============================================================
    # DOVIZ KURLARI - ExchangeRate API
    # ==============================================================

    def get_exchange_rates(self, query: str) -> Optional[str]:
        """Doviz kurlarini API'den al"""
        cache_key = "exchange_rates"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        if not REQUESTS_AVAILABLE:
            return self._currency_search_fallback(query)

        try:
            url = "https://open.er-api.com/v6/latest/USD"
            response = requests.get(url, timeout=8)

            if response.status_code != 200:
                return self._currency_search_fallback(query)

            data = response.json()
            rates = data.get('rates', {})

            try_rate = rates.get('TRY', 0)
            eur_usd = rates.get('EUR', 0)
            gbp_usd = rates.get('GBP', 0)

            # EUR/TRY ve GBP/TRY hesapla
            eur_try = try_rate / eur_usd if eur_usd else 0
            gbp_try = try_rate / gbp_usd if gbp_usd else 0

            result = (
                f"Doviz Kurlari (canli):\n"
                f"1 Dolar (USD) = {try_rate:.2f} TL\n"
                f"1 Euro (EUR) = {eur_try:.2f} TL\n"
                f"1 Sterlin (GBP) = {gbp_try:.2f} TL"
            )

            logger.success(f"Doviz: 1 USD = {try_rate:.2f} TL")
            self._set_cache(cache_key, result)
            return result

        except Exception as e:
            logger.warning(f"Exchange rate API hatasi: {e}")
            return self._currency_search_fallback(query)

    def _currency_search_fallback(self, query: str) -> Optional[str]:
        """DuckDuckGo ile doviz fallback"""
        results = self.search(f"{query} kur bugun TL", max_results=5)
        if results:
            text = "Doviz Kurlari (web'den):\n"
            for r in results:
                snippet = r.get('snippet', '')
                if any(w in snippet.lower() for w in ['tl', 'lira', 'kur', 'dolar', 'euro']):
                    text += f"- {r['title']}: {snippet}\n"
            return text if len(text) > 30 else None
        return None

    # ==============================================================
    # KRIPTO PARALAR - CoinGecko API
    # ==============================================================

    def get_crypto_prices(self, query: str) -> Optional[str]:
        """Kripto para fiyatlarini al"""
        query_lower = query.lower()

        crypto_map = {
            'bitcoin': 'bitcoin', 'btc': 'bitcoin',
            'ethereum': 'ethereum', 'eth': 'ethereum',
            'solana': 'solana', 'sol': 'solana',
            'ripple': 'ripple', 'xrp': 'ripple',
            'dogecoin': 'dogecoin', 'doge': 'dogecoin',
            'cardano': 'cardano', 'ada': 'cardano',
            'avalanche': 'avalanche-2', 'avax': 'avalanche-2',
            'bnb': 'binancecoin', 'binance': 'binancecoin',
        }

        found_cryptos = []
        for keyword, coin_id in crypto_map.items():
            if keyword in query_lower and coin_id not in found_cryptos:
                found_cryptos.append(coin_id)

        if not found_cryptos:
            found_cryptos = ['bitcoin']

        cache_key = f"crypto_{'_'.join(sorted(found_cryptos))}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        if not REQUESTS_AVAILABLE:
            return self._crypto_search_fallback(query)

        try:
            ids = ','.join(found_cryptos)
            url = (
                f"https://api.coingecko.com/api/v3/simple/price?"
                f"ids={ids}&vs_currencies=usd,try&include_24hr_change=true"
            )
            response = requests.get(url, timeout=8)

            if response.status_code != 200:
                return self._crypto_search_fallback(query)

            data = response.json()

            name_map = {
                'bitcoin': 'Bitcoin (BTC)', 'ethereum': 'Ethereum (ETH)',
                'solana': 'Solana (SOL)', 'ripple': 'XRP',
                'dogecoin': 'Dogecoin (DOGE)', 'cardano': 'Cardano (ADA)',
                'avalanche-2': 'Avalanche (AVAX)', 'binancecoin': 'BNB',
            }

            lines = ["Kripto Para Fiyatlari (canli):"]
            for coin_id in found_cryptos:
                coin_data = data.get(coin_id, {})
                usd_price = coin_data.get('usd', 0)
                try_price = coin_data.get('try', 0)
                change_24h = coin_data.get('usd_24h_change', 0)

                name = name_map.get(coin_id, coin_id.title())
                if change_24h and change_24h >= 0:
                    change_str = f"+{change_24h:.1f}%"
                elif change_24h:
                    change_str = f"{change_24h:.1f}%"
                else:
                    change_str = "0%"

                if usd_price >= 1:
                    lines.append(
                        f"{name}: ${usd_price:,.2f} / {try_price:,.2f} TL ({change_str} 24sa)"
                    )
                else:
                    lines.append(
                        f"{name}: ${usd_price:.6f} / {try_price:.4f} TL ({change_str} 24sa)"
                    )

            result = "\n".join(lines)
            logger.success(f"Kripto: {len(found_cryptos)} coin fiyati alindi")
            self._set_cache(cache_key, result)
            return result

        except Exception as e:
            logger.warning(f"CoinGecko API hatasi: {e}")
            return self._crypto_search_fallback(query)

    def _crypto_search_fallback(self, query: str) -> Optional[str]:
        """DuckDuckGo ile kripto fallback"""
        results = self.search(f"{query} fiyat bugun USD TL", max_results=5)
        if results:
            text = "Kripto Fiyatlari (web'den):\n"
            for r in results:
                snippet = r.get('snippet', '')
                if any(w in snippet.lower() for w in ['$', 'usd', 'tl', 'fiyat', 'price']):
                    text += f"- {r['title']}: {snippet}\n"
            return text if len(text) > 30 else None
        return None

    # ==============================================================
    # ALTIN FIYATLARI
    # ==============================================================

    def get_gold_price(self) -> Optional[str]:
        """Altin fiyatlarini al"""
        cache_key = "gold_price"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        results = self.search("altin fiyatlari bugun gram ceyrek tam", max_results=5)
        if results:
            text = "Altin Fiyatlari (web'den):\n"
            count = 0
            for r in results:
                snippet = r.get('snippet', '')
                if any(w in snippet.lower() for w in ['tl', 'lira', 'gram', 'ceyrek', 'fiyat']):
                    text += f"- {r['title']}: {snippet}\n"
                    count += 1

            if count > 0:
                self._set_cache(cache_key, text)
                return text

        return None

    # ==============================================================
    # SPOR SONUCLARI
    # ==============================================================

    def get_sports_results(self, query: str) -> Optional[str]:
        """Spor sonuclarini al"""
        cache_key = f"sports_{hash(query) % 10000}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        results = self.search(f"{query} mac skoru sonucu", max_results=5)
        if results:
            text = "Spor Sonuclari:\n"
            for r in results:
                text += f"- {r['title']}: {r['snippet']}\n"
            self._set_cache(cache_key, text)
            return text
        return None

    # ==============================================================
    # SEHIR ALGILAMA
    # ==============================================================

    def _resolve_city(self, city: str) -> str:
        """Sehir adini normalize et"""
        city_lower = city.lower().strip()

        if city_lower in SEHIR_ALIASES:
            return SEHIR_ALIASES[city_lower]

        normalized = self._strip_turkish(city_lower)
        if normalized in SEHIR_ALIASES:
            return SEHIR_ALIASES[normalized]

        return city.strip()

    def _strip_turkish(self, text: str) -> str:
        """Turkce karakterleri ASCII'ye cevir"""
        tr_map = {
            'c\u0327': 'c', 'g\u0306': 'g', '\u0131': 'i', 'o\u0308': 'o',
            's\u0327': 's', 'u\u0308': 'u',
        }
        replacements = [
            ('\u00e7', 'c'), ('\u011f', 'g'), ('\u0131', 'i'),
            ('\u00f6', 'o'), ('\u015f', 's'), ('\u00fc', 'u'),
            ('\u00c7', 'c'), ('\u011e', 'g'), ('\u0130', 'i'),
            ('\u00d6', 'o'), ('\u015e', 's'), ('\u00dc', 'u'),
        ]
        for tr_char, en_char in replacements:
            text = text.replace(tr_char, en_char)
        return text

    def detect_city(self, text: str) -> Optional[str]:
        """Metin icinden sehir adi bul"""
        text_lower = text.lower()
        text_normalized = self._strip_turkish(text_lower)

        sorted_aliases = sorted(SEHIR_ALIASES.keys(), key=len, reverse=True)

        for alias in sorted_aliases:
            alias_lower = alias.lower()
            alias_norm = self._strip_turkish(alias_lower)

            for check_text in [text_lower, text_normalized]:
                for check_alias in [alias_lower, alias_norm]:
                    if (f' {check_alias} ' in f' {check_text} ' or
                        check_text.startswith(check_alias + ' ') or
                        check_text.endswith(' ' + check_alias) or
                        check_text == check_alias):
                        return alias_lower

        return None

    def _weather_search_fallback(self, city: str) -> Optional[str]:
        """Web search ile hava durumu fallback"""
        try:
            results = self.search(f"{city} hava durumu anlik sicaklik", max_results=5)
            if not results:
                return None

            all_text = " ".join([r.get('snippet', '') for r in results])
            normalized_text = self._strip_turkish(all_text)

            temp_matches = re.findall(
                r'(?:sicaklik[i]?\s*[:=]?\s*|hava\s+sicakligi\s*)(\-?\d+(?:[.,]\d+)?)\s*',
                normalized_text, re.IGNORECASE
            )

            if temp_matches:
                return f"Anlik sicaklik: {temp_matches[0]}C (web'den)"

            text = ""
            for r in results[:3]:
                text += f"- {r['title']}: {r['snippet']}\n"
            return text

        except Exception as e:
            logger.error(f"Fallback hatasi: {e}")
            return None

    # ==============================================================
    # GENEL WEB ARAMASI (Kalite filtreli)
    # ==============================================================

    def search(self, query: str, max_results: Optional[int] = None) -> List[Dict]:
        """DuckDuckGo web aramasi - kalite filtreli"""
        if not self.enabled:
            return []

        max_results = max_results or self.max_results
        logger.info(f"Web'de araniyor: '{query}'")

        try:
            ddgs = DDGS()
            results = []

            for result in ddgs.text(query, max_results=max_results + 3):
                title = result.get('title', '').strip()
                snippet = result.get('body', '').strip()
                url = result.get('link', result.get('href', ''))

                # Kalite filtresi
                if len(snippet) < 20:
                    continue

                # Spam filtresi
                spam_words = ['casino', 'slot', 'bahis', 'porn', 'xxx', 'betting']
                if any(spam in snippet.lower() for spam in spam_words):
                    continue

                results.append({
                    'title': title,
                    'url': url,
                    'snippet': snippet[:500],
                })

                if len(results) >= max_results:
                    break

            logger.success(f"{len(results)} sonuc bulundu")
            return results

        except Exception as e:
            logger.error(f"Arama hatasi: {e}")
            return []

    def search_news(self, query: str, max_results: Optional[int] = None) -> List[Dict]:
        """Haber aramasi - Turkce optimize"""
        if not self.enabled:
            return []

        max_results = max_results or self.max_results
        logger.info(f"Haber araniyor: '{query}'")

        try:
            ddgs = DDGS()
            results = []

            # Turkce haber ara (region=tr-tr)
            try:
                for result in ddgs.news(query, region='tr-tr', max_results=max_results):
                    title = result.get('title', '').strip()
                    snippet = result.get('body', '').strip()
                    source = result.get('source', '').strip()
                    date = result.get('date', '')

                    if len(title) < 5:
                        continue

                    date_str = ""
                    if date:
                        try:
                            if isinstance(date, str) and len(date) > 10:
                                dt = datetime.fromisoformat(
                                    date.replace('Z', '+00:00')
                                )
                                date_str = dt.strftime('%d.%m.%Y %H:%M')
                        except Exception:
                            date_str = str(date)[:16]

                    results.append({
                        'title': title,
                        'url': result.get('url', ''),
                        'snippet': snippet[:400],
                        'date': date_str,
                        'source': source
                    })
            except Exception as e:
                logger.warning(f"News API hatasi: {e}")

            # Haber bulunamadiysa text search ile dene
            if not results:
                logger.info("News API bos, text search deneniyor...")
                text_results = self.search(
                    f"{query} haber son dakika site:haberler.com OR site:ntv.com.tr OR site:cnn.com.tr",
                    max_results=max_results
                )
                for r in text_results:
                    results.append({
                        'title': r['title'],
                        'url': r['url'],
                        'snippet': r['snippet'],
                        'date': '',
                        'source': ''
                    })

            logger.success(f"{len(results)} haber bulundu")
            return results

        except Exception as e:
            logger.error(f"Haber arama hatasi: {e}")
            return []

    # ==============================================================
    # AKILLI ARAMA - Ana Giris Noktasi
    # ==============================================================

    def smart_search(self, query: str) -> Optional[str]:
        """
        Sorguyu analiz edip en uygun arama yontemini otomatik sec.
        """
        query_lower = query.lower()
        query_norm = self._strip_turkish(query_lower)

        # ---- SAAT / TARiH ----
        time_keywords = ['saat kac', 'saat', 'kac oldu', 'zaman', 'tarih',
                         'bugun', 'bugunun tarihi', 'gun', 'hangi gun', 'yil']
        if any(kw in query_norm for kw in time_keywords):
            return self._get_time_info()

        # ---- HAVA DURUMU ----
        hava_keywords = ['hava', 'sicaklik', 'derece', 'yagmur', 'kar',
                         'ruzgar', 'nem', 'hava durumu', 'meteoroloji']
        if any(kw in query_norm for kw in hava_keywords):
            city = self.detect_city(query)
            if not city:
                city = 'ankara'
            weather = self.get_weather(city)
            if weather:
                return f"{city.upper()} HAVA DURUMU (CANLI VERI):\n{weather}"

        # ---- DOVIZ ----
        doviz_keywords = ['dolar', 'euro', 'sterlin', 'kur', 'doviz',
                          'pound', 'yen', 'frank']
        if any(kw in query_norm for kw in doviz_keywords):
            result = self.get_exchange_rates(query)
            if result:
                return result

        # ---- KRiPTO ----
        kripto_keywords = ['bitcoin', 'btc', 'ethereum', 'eth', 'kripto',
                           'coin', 'solana', 'dogecoin', 'doge', 'xrp',
                           'bnb', 'cardano', 'avax']
        if any(kw in query_norm for kw in kripto_keywords):
            result = self.get_crypto_prices(query)
            if result:
                return result

        # ---- ALTIN ----
        altin_keywords = ['altin', 'gram altin', 'ceyrek', 'tam altin',
                          'cumhuriyet altini', 'yarim altin', '22 ayar',
                          '14 ayar']
        if any(kw in query_norm for kw in altin_keywords):
            result = self.get_gold_price()
            if result:
                return result

        # ---- SPOR ----
        spor_keywords = ['mac', 'skor', 'lig', 'sampiyonlar', 'galatasaray',
                         'fenerbahce', 'besiktas', 'trabzonspor', 'super lig',
                         'milli takim', 'formula', 'f1', 'nba', 'basketbol']
        if any(kw in query_norm for kw in spor_keywords):
            result = self.get_sports_results(query)
            if result:
                return result

        # ---- HABER ----
        haber_keywords = ['haber', 'son dakika', 'guncel', 'ne oldu',
                          'olay', 'gelisme', 'aciklama', 'duyuru']
        if any(kw in query_norm for kw in haber_keywords):
            results = self.search_news(query, max_results=5)
            if results:
                text = "SON HABERLER:\n"
                for r in results:
                    source = f"[{r['source']}] " if r.get('source') else ""
                    date = f" ({r['date']})" if r.get('date') else ""
                    text += f"- {source}{r['title']}{date}: {r['snippet']}\n"
                return text
            else:
                # Haber bulunamadiysa genel arama yap
                results = self.search(f"{query} haberleri", max_results=5)
                if results:
                    text = "HABERLER (web'den):\n"
                    for r in results:
                        text += f"- {r['title']}: {r['snippet']}\n"
                    return text

        # ---- GENEL BiLGi (genis kapsam) ----
        bilgi_keywords = [
            # Soru kelimeleri
            'kimdir', 'nedir', 'ne demek', 'nasil', 'neden', 'nerede',
            'ne zaman', 'kac', 'kaci', 'kacinci', 'hangi', 'kim', 'ne',
            'nereye', 'nereden',
            # Arama emirleri
            'ara', 'bul', 'internet', 'google', 'wiki', 'arastir',
            'anlat', 'acikla', 'tanitim', 'bilgi', 'ozet',
            # Guncel konular
            'son', 'yeni', 'guncel', 'populer', 'trend',
            # Eglence
            'film', 'dizi', 'sarki', 'muzik', 'oyun',
            # Yemek
            'recete', 'tarif', 'kalori', 'besin',
            # Afet
            'deprem', 'sel', 'yangin', 'afet',
            # Siyaset
            'secim', 'oy', 'siyaset', 'parti',
            # Egitim
            'universite', 'sinav', 'yks', 'kpss', 'ales',
            # Seyahat
            'ucak', 'ucus', 'bilet', 'otel', 'tatil',
            # Saglik
            'hastane', 'ilac', 'doktor', 'hastalik',
            # Alisveris
            'fiyat', 'fiyati', 'kac para', 'ucuz', 'pahali',
            'magaza', 'satis', 'indirim', 'kampanya',
            # Teknoloji
            'telefon', 'bilgisayar', 'laptop', 'tablet',
            'uygulama', 'program', 'yazilim',
        ]
        if any(kw in query_norm for kw in bilgi_keywords):
            results = self.search(query, max_results=5)
            if results:
                text = "INTERNET ARASTIRMA SONUCLARI:\n"
                for r in results:
                    text += f"- {r['title']}: {r['snippet']}\n"
                return text

        # ---- SORU iSARETi VARSA YiNE DE ARA ----
        if '?' in query or query_norm.rstrip().endswith(('mi', 'mu', 'mi?', 'mu?')):
            results = self.search(query, max_results=3)
            if results:
                text = "INTERNET ARASTIRMA SONUCLARI:\n"
                for r in results:
                    text += f"- {r['title']}: {r['snippet']}\n"
                return text

        return None

    def _get_time_info(self) -> str:
        """Guncel saat ve tarih bilgisi"""
        now = datetime.now()

        gun_isimleri = {
            'Monday': 'Pazartesi', 'Tuesday': 'Sali',
            'Wednesday': 'Carsamba', 'Thursday': 'Persembe',
            'Friday': 'Cuma', 'Saturday': 'Cumartesi',
            'Sunday': 'Pazar'
        }
        ay_isimleri = {
            'January': 'Ocak', 'February': 'Subat', 'March': 'Mart',
            'April': 'Nisan', 'May': 'Mayis', 'June': 'Haziran',
            'July': 'Temmuz', 'August': 'Agustos',
            'September': 'Eylul', 'October': 'Ekim',
            'November': 'Kasim', 'December': 'Aralik'
        }

        gun = gun_isimleri.get(now.strftime('%A'), now.strftime('%A'))
        ay = ay_isimleri.get(now.strftime('%B'), now.strftime('%B'))

        return (
            f"GUNCEL ZAMAN BILGISI:\n"
            f"Tarih: {now.day} {ay} {now.year}, {gun}\n"
            f"Saat: {now.strftime('%H:%M')}"
        )
