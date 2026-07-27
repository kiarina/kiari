import asyncio
import threading

import numpy as np
from pydub import AudioSegment  # type: ignore


async def play_audio(
    file_path: str,
    *,
    buffersize: int = 10_000,
    blocking: bool = True,
    stop_event: threading.Event | None = None,
) -> None:
    await asyncio.to_thread(_play_audio, file_path, buffersize, blocking, stop_event)


def _play_audio(
    file_path: str,
    buffersize: int,
    blocking: bool,
    stop_event: threading.Event | None,
) -> None:
    import sounddevice as sd  # type: ignore

    samples, fps = _load_audio_samples(file_path, buffersize)

    if blocking and stop_event is None:
        sd.play(samples, samplerate=fps, blocking=True)
        return

    sd.play(samples, samplerate=fps, blocking=False)

    if stop_event is None:
        return

    finished_event = threading.Event()
    wait_errors: list[BaseException] = []

    def wait_until_finished() -> None:
        try:
            sd.wait()
        except BaseException as e:
            wait_errors.append(e)
        finally:
            finished_event.set()

    wait_thread = threading.Thread(target=wait_until_finished, daemon=True)
    wait_thread.start()

    while not finished_event.is_set():
        if stop_event.wait(0.05):
            sd.stop()
            break

    wait_thread.join()

    if wait_errors:
        raise wait_errors[0]


def _load_audio_samples(file_path: str, buffersize: int) -> tuple[np.ndarray, int]:
    audio_segment = AudioSegment.from_file(file_path)
    samples = np.array(audio_segment.get_array_of_samples())

    if audio_segment.channels > 1:
        samples = samples.reshape((-1, audio_segment.channels))

    max_value = float(1 << (8 * audio_segment.sample_width - 1))
    samples = samples.astype(np.float32) / max_value

    return samples, audio_segment.frame_rate
