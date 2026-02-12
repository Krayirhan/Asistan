import pytest

from src.core.llm_manager import LLMManager


pytestmark = pytest.mark.unit


class _FailingVLMClient:
    def chat(self, **kwargs):
        raise RuntimeError("vlm-error")


class _DummyModelManager:
    def __init__(self):
        self.calls = []

    def unload_model(self, name):
        self.calls.append(("unload", name))

    def load_model(self, name):
        self.calls.append(("load", name))
        if name == "vlm":
            return _FailingVLMClient()
        raise AssertionError("LLM load should not be called on VLM failure")


def test_analyze_image_always_unloads_vlm_on_error():
    config = {
        "llm": {"model": "dummy"},
        "vlm": {"model": "dummy-vlm"},
        "memory": {"max_history": 5},
        "web_search": {"enabled": False},
    }
    model_manager = _DummyModelManager()
    manager = LLMManager(config, model_manager)

    result = manager.analyze_image("fake.png", "what is this?")

    assert "Resmi analiz edemedim" in result
    assert ("unload", "vlm") in model_manager.calls
