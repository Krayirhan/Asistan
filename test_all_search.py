"""Test tum web arama kategorilerini"""
import sys
sys.path.insert(0, 'src')
from tools.web_search import WebSearchTool

ws = WebSearchTool({'web_search': {'enabled': True, 'max_results': 5, 'timeout': 10}})

print("=" * 50)
print("1) DOVIZ TESTI")
print("=" * 50)
r = ws.get_exchange_rates('dolar kac tl')
print(r)
print()

print("=" * 50)
print("2) KRIPTO TESTI")
print("=" * 50)
r2 = ws.get_crypto_prices('bitcoin fiyati')
print(r2)
print()

print("=" * 50)
print("3) HAVA DURUMU TESTI")
print("=" * 50)
r3 = ws.get_weather('istanbul')
print(r3)
print()

print("=" * 50)
print("4) SAAT TESTI")
print("=" * 50)
r4 = ws._get_time_info()
print(r4)
print()

print("=" * 50)
print("5) GENEL ARAMA TESTI")
print("=" * 50)
r5 = ws.search('Turkiye cumhurbaskani kimdir', max_results=3)
for x in r5:
    print(f"- {x['title']}: {x['snippet'][:120]}")
print()

print("=" * 50)
print("6) HABER TESTI")
print("=" * 50)
r6 = ws.search_news('turkiye son dakika', max_results=3)
for x in r6:
    src = f"[{x.get('source','')}] " if x.get('source') else ""
    dt = f" ({x.get('date','')})" if x.get('date') else ""
    print(f"- {src}{x['title']}{dt}")
print()

print("=" * 50)
print("7) SMART SEARCH - doviz")
print("=" * 50)
r7 = ws.smart_search('dolar kac tl')
print(r7)
print()

print("=" * 50)
print("8) SMART SEARCH - antalya hava")
print("=" * 50)
r8 = ws.smart_search('antalya hava durumu nasil')
print(r8)
print()

print("=" * 50)
print("TUMU BASARILI!")
print("=" * 50)
