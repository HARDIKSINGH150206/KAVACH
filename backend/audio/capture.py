from __future__ import annotations

import asyncio
import math
import time

import numpy as np

SAMPLE_RATE = 16_000
WINDOW_SEC = 2.0
HOP_SEC = 0.5

try:
    import sounddevice as sd
except (ImportError, OSError):  # pragma: no cover
    sd = None


class AudioCaptureError(RuntimeError):
    """Raised when a requested live audio source cannot be opened."""


def synthetic_window(spoof: bool = False) -> np.ndarray:
    """Generate a deterministic demo audio window when no microphone is attached."""
    samples = int(SAMPLE_RATE * WINDOW_SEC)
    t = np.arange(samples, dtype=np.float32) / SAMPLE_RATE
    base = 0.08 * np.sin(2 * math.pi * 180 * t)
    speech_like = base + 0.04 * np.sin(2 * math.pi * 420 * t)
    if spoof:
        speech_like += 0.04 * np.sin(2 * math.pi * 3_200 * t)
        speech_like += 0.025 * np.sign(np.sin(2 * math.pi * 90 * t))
    return speech_like.astype(np.float32)


async def demo_audio_windows():
    """Yield alternating genuine/spoof-like windows for the dashboard demo."""
    tick = 0
    while True:
        spoof = (int(time.time()) // 8) % 2 == 1
        window = synthetic_window(spoof=spoof)
        yield window, spoof, tick
        tick += 1


async def microphone_audio_windows():
    """Yield overlapping microphone windows in the same shape as demo windows."""
    if sd is None:
        raise AudioCaptureError("sounddevice is not installed")

    loop = asyncio.get_running_loop()
    queue: asyncio.Queue[np.ndarray] = asyncio.Queue(maxsize=8)
    hop_size = int(SAMPLE_RATE * HOP_SEC)
    window_size = int(SAMPLE_RATE * WINDOW_SEC)
    buffer = np.zeros(window_size, dtype=np.float32)

    def enqueue_chunk(chunk: np.ndarray) -> None:
        try:
            queue.put_nowait(chunk)
        except asyncio.QueueFull:
            pass

    def callback(indata, _frames, _time_info, status) -> None:
        if status:
            return
        chunk = np.asarray(indata[:, 0], dtype=np.float32).copy()
        loop.call_soon_threadsafe(enqueue_chunk, chunk)

    try:
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=hop_size,
            callback=callback,
        )
        stream.start()
    except Exception as exc:  # pragma: no cover - depends on host audio devices
        raise AudioCaptureError(f"microphone capture unavailable: {exc}") from exc

    tick = 0
    try:
        collected = 0
        while collected < window_size:
            chunk = await queue.get()
            end = min(collected + len(chunk), window_size)
            buffer[collected:end] = chunk[: end - collected]
            collected = end

        while True:
            yield buffer.copy(), False, tick
            chunk = await queue.get()
            buffer[:-hop_size] = buffer[hop_size:]
            buffer[-hop_size:] = chunk[:hop_size]
            tick += 1
    finally:
        stream.stop()
        stream.close()


async def audio_windows(source: str = "demo"):
    """Select a configured audio source, falling back to demo when live capture fails."""
    if source == "mic":
        try:
            async for item in microphone_audio_windows():
                yield item
            return
        except AudioCaptureError:
            pass

    async for item in demo_audio_windows():
        yield item
