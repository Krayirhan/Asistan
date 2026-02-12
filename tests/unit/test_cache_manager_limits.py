import pytest

from src.core.cache_manager import CacheManager


pytestmark = pytest.mark.unit


def test_cache_respects_max_size_limit(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    manager = CacheManager({
        "cache": {
            "enabled": True,
            "ttl_seconds": 3600,
            "max_size_mb": 0.001,  # Very small to force eviction
        }
    })

    for i in range(50):
        manager.set(f"prompt-{i}", "x" * 500)

    assert manager._get_cache_size_mb() <= manager.max_size_mb
