from __future__ import annotations

import struct
from dataclasses import dataclass

import usb.core
import usb.util

SEEED_VID = 0x2886
RESPEAKER_USB_4MIC_PID = 0x0018


class DeviceNotFound(RuntimeError):
    pass


@dataclass(frozen=True)
class ReSpeakerReading:
    angle: int
    voice: bool


class ReSpeakerUSB:
    """Minimal Python 3 driver for the XVF3000 vendor control endpoint."""

    timeout_ms = 8_000

    def __init__(self, device: usb.core.Device) -> None:
        self.device = device

    @classmethod
    def find(cls) -> "ReSpeakerUSB":
        device = usb.core.find(idVendor=SEEED_VID, idProduct=RESPEAKER_USB_4MIC_PID)
        if device is None:
            raise DeviceNotFound(
                f"ReSpeaker not found (expected {SEEED_VID:04x}:{RESPEAKER_USB_4MIC_PID:04x})"
            )
        return cls(device)

    def _read_int(self, parameter_id: int, offset: int) -> int:
        # XMOS protocol: bit 7 reads, bit 6 selects integer, low bits are offset.
        command = 0x80 | 0x40 | offset
        response = self.device.ctrl_transfer(
            usb.util.CTRL_IN | usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE,
            0,
            command,
            parameter_id,
            8,
            self.timeout_ms,
        )
        value, _exponent = struct.unpack("<ii", bytes(response))
        return value

    def read(self) -> ReSpeakerReading:
        # XVF3000 parameter map: DOAANGLE=(21,0), VOICEACTIVITY=(19,32).
        angle = self._read_int(21, 0)
        voice = bool(self._read_int(19, 32))
        return ReSpeakerReading(angle=angle % 360, voice=voice)

    def led_trace(self) -> None:
        """Let firmware display VAD and DOA on the twelve-pixel ring."""
        self._led_command(0)

    def led_off(self) -> None:
        self._led_command(1, [0, 0, 0, 0])

    def _led_command(self, command: int, data: list[int] | None = None) -> None:
        self.device.ctrl_transfer(
            usb.util.CTRL_OUT | usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE,
            0,
            command,
            0x1C,
            data or [0],
            self.timeout_ms,
        )

    def close(self) -> None:
        usb.util.dispose_resources(self.device)

