from __future__ import annotations

import argparse
import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Event, Thread
from urllib.parse import urlparse

from .model import RadarState
from .sources import MockDirectionSource, ReSpeakerDirectionSource
from .audio import AudioCapture

WEB_ROOT = Path(__file__).with_name("web")
PROJECT_ROOT = WEB_ROOT.parent.parent


class RadarHandler(BaseHTTPRequestHandler):
    state: RadarState

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/state":
            self._send_json(self.state.snapshot())
            return
        if path == "/api/health":
            snapshot = self.state.snapshot()
            self._send_json(
                {
                    "status": "ok" if snapshot["connected"] else "degraded",
                    "source": snapshot["source"],
                    "error": snapshot["error"],
                }
            )
            return
        if path == "/api/recordings":
            self._send_json({"recordings": self.state.snapshot()["recordings"]})
            return

        relative = "index.html" if path == "/" else path.lstrip("/")
        target = (WEB_ROOT / relative).resolve()
        if WEB_ROOT.resolve() not in target.parents or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        body = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mimetypes.guess_type(target.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: dict) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="ReSpeaker 360-degree sound radar")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--source", choices=("auto", "hardware", "mock"), default="auto")
    parser.add_argument("--no-audio", action="store_true", help="disable ALSA capture and WAV segments")
    parser.add_argument("--recordings-dir", type=Path, default=PROJECT_ROOT / "recordings")
    args = parser.parse_args()

    state = RadarState()
    stop = Event()
    RadarHandler.state = state
    source = choose_source(args.source)
    source_thread = Thread(target=source.run, args=(state, stop), daemon=True)
    source_thread.start()
    if isinstance(source, ReSpeakerDirectionSource) and not args.no_audio:
        audio_thread = Thread(
            target=AudioCapture(args.recordings_dir).run,
            args=(state, stop),
            daemon=True,
        )
        audio_thread.start()

    server = ThreadingHTTPServer((args.host, args.port), RadarHandler)
    print(f"reSpeake is running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        server.server_close()


def choose_source(requested: str):
    if requested == "mock":
        return MockDirectionSource()
    if requested == "hardware":
        return ReSpeakerDirectionSource()
    try:
        from .hardware import ReSpeakerUSB

        device = ReSpeakerUSB.find()
        device.close()
        return ReSpeakerDirectionSource()
    except Exception as exc:
        print(f"ReSpeaker unavailable ({exc}); using mock source")
        return MockDirectionSource()


if __name__ == "__main__":
    main()

