from __future__ import annotations

import math
import random
from abc import ABC, abstractmethod
from threading import Event
from time import monotonic, sleep

from .model import RadarState


class DirectionSource(ABC):
    @abstractmethod
    def run(self, state: RadarState, stop: Event) -> None:
        raise NotImplementedError


class MockDirectionSource(DirectionSource):
    """Produces lifelike demo data so the UI is useful without hardware."""

    def run(self, state: RadarState, stop: Event) -> None:
        started = monotonic()
        while not stop.is_set():
            elapsed = monotonic() - started
            angle = (180 + 125 * math.sin(elapsed / 3.2)) % 360
            voice = int(elapsed * 1.4) % 7 not in (0, 6)
            level = (0.45 + 0.35 * math.sin(elapsed * 2.7) + random.uniform(-0.08, 0.08))
            state.update(angle, voice, level if voice else 0.03)
            sleep(0.12)

