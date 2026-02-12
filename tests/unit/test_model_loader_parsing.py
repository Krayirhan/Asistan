import pytest

from src.core.model_loader import ModelManager


pytestmark = pytest.mark.unit


def test_extract_model_names_from_nested_response():
    response = {
        "models": [
            {"name": "turkce-asistan:latest"},
            {"model": "qwen2.5:7b"},
        ]
    }

    names = ModelManager._extract_model_names(response)
    assert "turkce-asistan:latest" in names
    assert "qwen2.5:7b" in names


def test_resolve_model_name_matches_base_and_exact():
    available = {"turkce-asistan:latest", "qwen2.5:7b"}

    assert ModelManager._resolve_model_name("qwen2.5:7b", available) == "qwen2.5:7b"
    assert ModelManager._resolve_model_name("turkce-asistan", available) == "turkce-asistan:latest"
    assert ModelManager._resolve_model_name("missing-model", available) is None
