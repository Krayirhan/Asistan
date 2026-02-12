import pytest

from src.main import load_config


pytestmark = pytest.mark.unit


def test_load_config_works_outside_project_root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = load_config("config/settings.yaml")
    assert "llm" in config
