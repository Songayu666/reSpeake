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

    def snapshot(self) -> dict:
        with self._lock:
            return {
                **asdict(self._sample),
                "source": self._source,
                "connected": self._connected,
                "error": self._error,
                "history": [asdict(item) for item in self._history],
            }

