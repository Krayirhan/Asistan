"""
Test suite for audio components (STT, TTS).
"""

from pathlib import Path

import numpy as np
import pytest

from src.audio.stt_engine import STTEngine
from src.audio.tts_engine import PIPER_AVAILABLE, TTSEngine
from src.core.model_loader import ModelManager


pytestmark = pytest.mark.integration


def test_stt_engine():
    """STT engine basic behavior."""
    config = {
        "hardware": {"gpu_memory_limit": 7.5, "model_unload_timeout": 30},
        "stt": {
            "model_size": "base",
            "device": "cpu",
            "compute_type": "int8",
            "language": "tr",
            "beam_size": 1,
            "vad_filter": False,
        },
    }

    model_manager = ModelManager(config)
    stt_engine = STTEngine(config, model_manager)

    # 5 seconds of silence
    sample_rate = 16000
    duration = 5
    audio = np.zeros(duration * sample_rate, dtype=np.float32)

    assert bool(stt_engine.is_audio_silent(audio))


def test_tts_engine():
    """TTS should load model when available and stay None when missing."""
    config = {
        "tts": {
            "engine": "piper",
            "model_path": "models/piper/tr_TR-fettah-medium.onnx",
            "device": "cpu",
            "speed": 1.0,
            "sample_rate": 22050,
            "num_threads": 4,
        }
    }

    if not PIPER_AVAILABLE:
        pytest.skip("Piper is not installed")

    tts_engine = TTSEngine(config)
    model_exists = Path(config["tts"]["model_path"]).exists()

    if model_exists:
        assert tts_engine.model is not None, "Model file exists but TTS model did not load"
    else:
        assert tts_engine.model is None, "Model file missing but TTS model appears loaded"
