from __future__ import annotations

import argparse
import json
import socket
import threading
import time
from urllib.error import URLError
from urllib.request import urlopen

import uvicorn

from app.main import app


def _available_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _start_backend() -> tuple[uvicorn.Server, threading.Thread, int]:
    port = _available_port()
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    )
    backend = threading.Thread(target=server.run, name="alpha-engine-backend")
    backend.start()
    return server, backend, port


def _wait_for_backend(server: uvicorn.Server, backend: threading.Thread) -> None:
    deadline = time.monotonic() + 15
    while not server.started and backend.is_alive() and time.monotonic() < deadline:
        time.sleep(0.05)
    if not server.started:
        raise RuntimeError("The Alpha Engine backend did not start")


def _stop_backend(server: uvicorn.Server, backend: threading.Thread) -> None:
    server.should_exit = True
    backend.join(timeout=10)
    if backend.is_alive():
        server.force_exit = True
        backend.join(timeout=2)
    if backend.is_alive():
        raise RuntimeError("The Alpha Engine backend did not stop")


def _smoke_test() -> None:
    server, backend, port = _start_backend()

    try:
        _wait_for_backend(server, backend)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                with urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as response:
                    payload = json.loads(response.read())
                if payload != {"status": "ok", "app": "alpha-engine"}:
                    raise RuntimeError(f"Unexpected health response: {payload!r}")
                return
            except (OSError, URLError):
                if not backend.is_alive():
                    raise RuntimeError("The Alpha Engine backend exited before becoming healthy")
                time.sleep(0.05)
        raise RuntimeError("The Alpha Engine backend did not become healthy")
    finally:
        _stop_backend(server, backend)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()
    if args.smoke_test:
        _smoke_test()
        return

    server, backend, port = _start_backend()
    try:
        _wait_for_backend(server, backend)
        import webview

        webview.create_window("Alpha Engine", f"http://127.0.0.1:{port}")
        webview.start()
    finally:
        _stop_backend(server, backend)


if __name__ == "__main__":
    main()
