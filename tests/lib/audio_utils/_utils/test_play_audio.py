import asyncio
import threading

import numpy as np
import pytest
from pydub import AudioSegment  # type: ignore

from kiari.lib.audio_utils import play_audio
from kiari.lib.audio_utils._utils.play_audio import _load_audio_samples


@pytest.mark.skip(reason="Manual test")
async def test_play_audio(audio_file_path) -> None:
    await play_audio(audio_file_path)


@pytest.mark.skip(reason="Manual test")
async def test_non_blocking(audio_file_path) -> None:
    stop_event = threading.Event()

    async def play_and_wait() -> None:
        await play_audio(audio_file_path, blocking=False, stop_event=stop_event)

    play_task = asyncio.create_task(play_and_wait())

    await asyncio.sleep(1.5)
    assert not play_task.done()

    stop_event.set()
    await play_task


def test_load_audio_samples_with_flac(tmp_path) -> None:
    file_path = tmp_path / "audio.flac"
    audio_segment = AudioSegment.silent(duration=1000, frame_rate=24000)
    audio_segment.export(file_path, format="flac")

    samples, fps = _load_audio_samples(str(file_path), 10_000)

    assert fps == 24000
    assert samples.dtype == np.float32
    assert samples.shape == (24000,)
