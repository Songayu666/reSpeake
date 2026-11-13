from __future__ import annotations

import math
import shutil
import subprocess
import wave
from array import array
from collections import deque
from datetime import datetime
from pathlib import Path
from threading import Event
from time import monotonic

from .model import RadarState

SAMPLE_RATE = 16_000
CHANNELS = 6
SAMPLE_WIDTH = 2
CHUNK_FRAMES = 320


def extract_channel(data: bytes, channel: int = 0, channels: int = CHANNELS) -> bytes:
    samples = array("h")
    samples.frombytes(data)
    return array("h", samples[channel::channels]).tobytes()


def rms_level(mono_pcm: bytes) -> tuple[float, float]:
    samples = array("h")
    samples.frombytes(mono_pcm)
    if not samples:
        return 0.0, -96.0
    rms = math.sqrt(sum(value * value for value in samples) / len(samples))
    dbfs = 20.0 * math.log10(max(rms, 1.0) / 32768.0)
    normalized = max(0.0, min(1.0, (dbfs + 60.0) / 54.0))
    return normalized, dbfs


class AudioCapture:
    def __init__(
        self,
        output_dir: Path,
        device: str = "hw:CARD=ArrayUAC10,DEV=0",
        pre_roll_seconds: float = 0.5,
        end_silence_seconds: float = 0.8,
        max_segment_seconds: float = 30.0,
    ) -> None:
        self.output_dir = output_dir
        self.device = device
        self.pre_roll_chunks = max(1, round(pre_roll_seconds * SAMPLE_RATE / CHUNK_FRAMES))
        self.end_silence_chunks = max(1, round(end_silence_seconds * SAMPLE_RATE / CHUNK_FRAMES))
        self.max_segment_chunks = max(1, round(max_segment_seconds * SAMPLE_RATE / CHUNK_FRAMES))

    def run(self, state: RadarState, stop: Event) -> None:
        if not shutil.which("arecord"):
            state.set_audio(False, "arecord not found")
            return
        self.output_dir.mkdir(parents=True, exist_ok=True)
        command = [
            "arecord", "-q", "-D", self.device, "-t", "raw", "-f", "S16_LE",
            "-r", str(SAMPLE_RATE), "-c", str(CHANNELS), "-",
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        state.set_audio(True)
        pre_roll: deque[bytes] = deque(maxlen=self.pre_roll_chunks)
        segment: list[bytes] | None = None
        segment_started = 0.0
        silence_chunks = 0
        bytes_per_chunk = CHUNK_FRAMES * CHANNELS * SAMPLE_WIDTH
        try:
            assert process.stdout is not None
            while not stop.is_set():
                raw = process.stdout.read(bytes_per_chunk)
                if len(raw) != bytes_per_chunk:
                    break
                mono = extract_channel(raw)
                level, dbfs = rms_level(mono)
                state.update_level(level, dbfs)
                voice = state.voice_active()
                if segment is None:
                    pre_roll.append(mono)
                    if voice:
                        segment = list(pre_roll)
                        segment_started = monotonic() - len(segment) * CHUNK_FRAMES / SAMPLE_RATE
                        silence_chunks = 0
                        state.set_recording(True)
                else:
                    segment.append(mono)
                    silence_chunks = 0 if voice else silence_chunks + 1
                    if silence_chunks >= self.end_silence_chunks or len(segment) >= self.max_segment_chunks:
                        self._save_segment(segment, segment_started, state)
                        segment = None
                        pre_roll.clear()
                        silence_chunks = 0
                        state.set_recording(False)
        except Exception as exc:
            state.set_audio(False, f"{type(exc).__name__}: {exc}")
        finally:
            if segment:
                self._save_segment(segment, segment_started, state)
            state.set_recording(False)
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
            if process.returncode not in (None, 0, -15) and not stop.is_set():
                stderr = process.stderr.read().decode(errors="replace").strip() if process.stderr else ""
                state.set_audio(False, stderr or f"arecord exited with {process.returncode}")

    def _save_segment(self, chunks: list[bytes], started: float, state: RadarState) -> None:
        if not chunks:
            return
        filename = datetime.now().astimezone().strftime("voice_%Y%m%d_%H%M%S_%f.wav")
        path = self.output_dir / filename
        with wave.open(str(path), "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(SAMPLE_WIDTH)
            output.setframerate(SAMPLE_RATE)
            output.writeframes(b"".join(chunks))
        duration = len(chunks) * CHUNK_FRAMES / SAMPLE_RATE
        state.add_recording(filename, duration, path.stat().st_size)
