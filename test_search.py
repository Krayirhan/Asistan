import sys
sys.path.insert(0, 'src')
from tools.web_search import WebSearchTool

ws = WebSearchTool({'web_search': {'enabled': True}})

print("=== TEST 1: istanbul kac derece ===")
r = ws.search('istanbul kac derece', max_results=8)
for x in r:
    print(f"  TITLE: {x['title']}")
    print(f"  SNIPPET: {x['snippet'][:300]}")
    print()

print("=== TEST 2: antalya hava durumu sicaklik ===")
r2 = ws.search('antalya hava durumu sicaklik', max_results=8)
for x in r2:
    print(f"  TITLE: {x['title']}")
    print(f"  SNIPPET: {x['snippet'][:300]}")
    print()

print("=== TEST 3: open-meteo API (direct) ===")
import requests
try:
    # Istanbul coords: 41.01, 28.98
    url = "https://api.open-meteo.com/v1/forecast?latitude=41.01&longitude=28.98&current_weather=true&timezone=Europe/Istanbul"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    print(f"  Istanbul: {data}")
except Exception as e:
    print(f"  Hata: {e}")

try:
    # Antalya coords: 36.89, 30.69
    url = "https://api.open-meteo.com/v1/forecast?latitude=36.89&longitude=30.69&current_weather=true&timezone=Europe/Istanbul"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    print(f"  Antalya: {data}")
except Exception as e:
    print(f"  Hata: {e}")
