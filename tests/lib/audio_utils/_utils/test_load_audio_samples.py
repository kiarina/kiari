import numpy as np
from kiarina.agi.asr_provider import write_wav

from kiari.lib.audio_utils import load_audio_samples


def test_load_audio_samples(tmp_path) -> None:
    file_path = tmp_path / "audio.wav"
    write_wav(
        file_path,
        np.asarray([0.0, 0.5, -0.5], dtype=np.float32),
        sample_rate=16_000,
    )

    samples, sample_rate = load_audio_samples(file_path)

    assert sample_rate == 16_000
    assert np.allclose(samples, np.asarray([0.0, 0.5, -0.5]), atol=1e-4)
