from pathlib import Path

import numpy as np
import soundfile as sf  # type: ignore[import-untyped]
from kiarina.agi.audio_types import MonoSamples, SampleRate


def load_audio_samples(file_path: str | Path) -> tuple[MonoSamples, SampleRate]:
    audio, sample_rate = sf.read(file_path, dtype="float32", always_2d=True)
    samples = np.asarray(audio[:, 0] if audio.shape[1] == 1 else audio.mean(axis=1))
    return samples, sample_rate
