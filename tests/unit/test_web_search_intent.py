import pytest

from src.tools.web_search import WebSearchTool


pytestmark = pytest.mark.unit


def _build_tool():
    tool = WebSearchTool({"web_search": {"enabled": True}})
    tool.get_weather = lambda city: "hava-verisi"
    tool.get_exchange_rates = lambda query: "doviz-verisi"
    tool.get_crypto_prices = lambda query: "kripto-verisi"
    tool.get_gold_price = lambda: "altin-verisi"
    tool.get_sports_results = lambda query: "spor-verisi"
    tool.search_news = lambda query, max_results=5: []
    tool.search = lambda query, max_results=5: [{
        "title": "dummy",
        "url": "https://example.com",
        "snippet": "dummy snippet for deterministic tests",
    }]
    return tool


def test_weather_query_is_not_shadowed_by_time_intent():
    tool = _build_tool()
    result = tool.smart_search("bugun hava nasil")
    assert result.startswith("ANKARA HAVA DURUMU")


def test_currency_query_is_not_shadowed_by_time_intent():
    tool = _build_tool()
    assert tool.smart_search("bugun dolar kac tl") == "doviz-verisi"


def test_explicit_time_query_still_returns_time_info():
    tool = _build_tool()
    result = tool.smart_search("saat kac")
    assert result is not None
    assert "ZAMAN" in result
