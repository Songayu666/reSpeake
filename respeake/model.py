from __future__ import annotations

from dataclasses import asdict, dataclass
from threading import Lock
from time import time


@dataclass(frozen=True)
class SoundSample:
    angle: float
    voice: bool
    level: float
    timestamp: float


class RadarState:
    def __init__(self, history_size: int = 48) -> None:
        self._lock = Lock()
        self._history_size = history_size
        self._sample = SoundSample(0.0, False, 0.0, time())
        self._history: list[SoundSample] = []
        self._source = "starting"
        self._connected = False
        self._error: str | None = None
        self._audio_connected = False
        self._audio_error: str | None = None
        self._dbfs = -96.0
        self._recording = False
        self._recordings: list[dict] = []

    def set_device(self, source: str, connected: bool, error: str | None = None) -> None:
        with self._lock:
            self._source = source
            self._connected = connected
            self._error = error

    def update(self, angle: float, voice: bool, level: float) -> None:
        sample = SoundSample(angle % 360, voice, max(0.0, min(1.0, level)), time())
        with self._lock:
            self._sample = sample
            if voice:
                self._history.append(sample)
                self._history = self._history[-self._history_size :]

    def update_direction(self, angle: float, voice: bool) -> None:
        with self._lock:
            sample = SoundSample(angle % 360, voice, self._sample.level, time())
            self._sample = sample
            if voice:
                self._history.append(sample)
                self._history = self._history[-self._history_size :]

    def update_level(self, level: float, dbfs: float) -> None:
        with self._lock:
            self._sample = SoundSample(
                self._sample.angle,
                self._sample.voice,
                max(0.0, min(1.0, level)),
                time(),
            )
            self._dbfs = dbfs

    def voice_active(self) -> bool:
        with self._lock:
            return self._sample.voice

    def set_audio(self, connected: bool, error: str | None = None) -> None:
        with self._lock:
            self._audio_connected = connected
            self._audio_error = error

    def set_recording(self, recording: bool) -> None:
        with self._lock:
            self._recording = recording

    def add_recording(self, filename: str, duration: float, size_bytes: int) -> None:
        with self._lock:
            self._recordings.insert(
                0,
                {
                    "filename": filename,
                    "timestamp": time(),
                    "duration": round(duration, 2),
                    "size_bytes": size_bytes,
                },
            )
            self._recordings = self._recordings[:50]

    def snapshot(self) -> dict:
        with self._lock:
            return {
                **asdict(self._sample),
                "source": self._source,
                "connected": self._connected,
                "error": self._error,
                "audio_connected": self._audio_connected,
                "audio_error": self._audio_error,
                "dbfs": round(self._dbfs, 1),
                "recording": self._recording,
                "recordings": list(self._recordings),
                "history": [asdict(item) for item in self._history],
            }

