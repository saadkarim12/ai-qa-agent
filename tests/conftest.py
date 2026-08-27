"""Shared fixtures.

Layer 2 needs something to crawl. Rather than mock a browser - which would test
the mock, not the crawler - these fixtures start the bundled demo application on
a free port and drive a real Chromium against it.
"""

import http.server
import os
import socket
import sys
import threading

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from demo_app.app import App


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def demo_url():
    port = _free_port()
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), App)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield "http://127.0.0.1:%d" % port
    finally:
        server.shutdown()
        server.server_close()


@pytest.fixture(scope="session")
def crawled(demo_url):
    """One authenticated crawl, shared - launching Chromium per test is slow."""
    from layer2.pipeline import discover

    amap, reqs = discover(
        demo_url, "customer@example.com", "Passw0rd!23",
        max_pages=25, entry_paths=["/", "/admin"],
    )
    return amap, reqs
