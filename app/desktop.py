from __future__ import annotations

import socket
import threading
import time

import uvicorn
import webview

from app.main import app


def _available_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def main() -> None:
    port = _available_port()
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    )
    backend = threading.Thread(target=server.run, name="alpha-engine-backend")
    backend.start()

    try:
        deadline = time.monotonic() + 15
        while not server.started and backend.is_alive() and time.monotonic() < deadline:
            time.sleep(0.05)
        if not server.started:
            raise RuntimeError("The Alpha Engine backend did not start")

        webview.create_window("Alpha Engine", f"http://127.0.0.1:{port}")
        webview.start()
    finally:
        server.should_exit = True
        backend.join(timeout=10)
        if backend.is_alive():
            server.force_exit = True
            backend.join(timeout=2)
        if backend.is_alive():
            raise RuntimeError("The Alpha Engine backend did not stop after the window closed")


if __name__ == "__main__":
    main()
