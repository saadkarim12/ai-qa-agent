"""The web page and its API.

    python3 -m tcgen                    # local: http://127.0.0.1:8030, opens a browser

Configuration, all by environment variable, so nothing secret lives in the repo:

    ANTHROPIC_API_KEY       the model provider key (required to generate)
    ANTHROPIC_WORKSPACE_ID  needed only if the key isn't scoped to a workspace
    TCGEN_MODEL             default choice on the page: opus | sonnet | haiku
    TCGEN_PASSWORD          when set, the page asks for this password (HTTP Basic,
                            any username). Set it whenever others can reach the page.
    TCGEN_DAILY_USD         spending cap per day, in USD (default 5)
    PORT                    set by most hosts; when present the server listens on
                            all interfaces instead of 127.0.0.1

Endpoints:
    GET  /api/config            models, defaults, example stories
    POST /api/warm              {model}  - pre-writes the prompt cache (cheap, async)
    POST /api/extract           {filename, content_b64}  - text from an uploaded file
    POST /api/generate/stream   {stories, site_url, model}  - server-sent events
    POST /api/generate          same, one JSON reply at the end

Standard library only, so it runs anywhere Python does.
"""

import base64
import datetime
import hmac
import json
import os
import queue
import socket
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from tcgen.examples import exemplars
from tcgen.extract import SUPPORTED, extract_text
from tcgen.llm import DEFAULT_MODEL, LABELS, MODELS, ModelError, make_client, warm_cache
from tcgen.page import PAGE
from tcgen.pipeline import generate
from tcgen.prompt import build_messages
from tcgen.stories import Story, parse_stories

MAX_BODY = 8 * 1024 * 1024  # uploads arrive base64-encoded
WARM_EVERY = 240            # seconds; the prompt cache lives for 5 minutes
_lock = threading.Lock()
_spend = {"day": None, "usd": 0.0}
_warmed = {}


def _daily_cap() -> float:
    try:
        return float(os.environ.get("TCGEN_DAILY_USD", "5"))
    except ValueError:
        return 5.0


def _spent_today(add: float = 0.0) -> float:
    with _lock:
        today = datetime.date.today().isoformat()
        if _spend["day"] != today:
            _spend["day"], _spend["usd"] = today, 0.0
        _spend["usd"] += add
        return _spend["usd"]


def _example_stories() -> tuple:
    ex = exemplars()
    site = ex[0]["story"]["site_url"] if ex else ""
    text = "\n\n".join(e["story"]["text"] for e in ex)
    return "Site URL: %s\n%s" % (site, text), site


def _choose_model(value) -> str:
    key = (value or DEFAULT_MODEL).strip().lower()
    if key not in LABELS:
        raise ModelError("Choose one of: %s." % ", ".join(v["name"] for v in LABELS.values()))
    return key


def _warm_in_background(model_key: str) -> bool:
    """Warm this model's cache unless it was warmed in the last few minutes."""
    client = make_client()
    if client is None:
        return False
    now = time.time()
    with _lock:
        if now - _warmed.get(model_key, 0) < WARM_EVERY:
            return False
        _warmed[model_key] = now
    ex = exemplars()
    site = ex[0]["story"]["site_url"] if ex else ""
    messages = build_messages(Story("US-0", "warm", "As a user\nI want to warm the cache", site), ex)

    def work():
        try:
            warm_cache(client, model_key, messages)
        except Exception:  # noqa: BLE001 - warming is an optimisation, never an error
            with _lock:
                _warmed.pop(model_key, None)

    threading.Thread(target=work, daemon=True).start()
    return True


class Handler(BaseHTTPRequestHandler):
    server_version = "tcgen"

    def log_message(self, fmt, *args):
        pass

    # -- plumbing ---------------------------------------------------------
    def _headers(self, code, ctype, length=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        if length is not None:
            self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()

    def _send(self, code, body, ctype):
        self._headers(code, ctype, len(body))
        self.wfile.write(body)

    def _json(self, code, payload):
        self._send(code, json.dumps(payload).encode(), "application/json; charset=utf-8")

    def _body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            raise ModelError("That's too large for one request. Split it into smaller batches.")
        try:
            return json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            raise ModelError("The request wasn't valid JSON.")

    def _authorised(self) -> bool:
        password = os.environ.get("TCGEN_PASSWORD")
        if not password:
            if "PORT" not in os.environ:
                return True  # running on your own computer
            # Hosted with no password would let anyone with the link spend the
            # API credit. Refuse rather than warn.
            body = (b"TCGEN_PASSWORD is not set. Add it in the host's environment "
                    b"settings and redeploy.")
            self.send_response(503)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return False
        header = self.headers.get("Authorization", "")
        if header.startswith("Basic "):
            try:
                _, _, given = base64.b64decode(header[6:]).decode().partition(":")
            except Exception:
                given = ""
            if hmac.compare_digest(given, password):
                return True
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Test Case Writer"')
        self.send_header("Content-Length", "0")
        self.end_headers()
        return False

    def _cap_error(self):
        cap = _daily_cap()
        if _spent_today() >= cap:
            return ("Today's spending limit ($%.2f) has been reached. It resets at midnight, "
                    "or an administrator can raise TCGEN_DAILY_USD." % cap)
        return None

    # -- routes -----------------------------------------------------------
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/healthz":
            return self._json(200, {"ok": True})
        if not self._authorised():
            return
        if path in ("/", "/index.html"):
            return self._send(200, PAGE.encode(), "text/html; charset=utf-8")
        if path == "/api/config":
            text, site = _example_stories()
            return self._json(200, {
                "models": [dict(key=k, id=MODELS[k]["id"], **LABELS[k]) for k in LABELS],
                "default_model": DEFAULT_MODEL if DEFAULT_MODEL in LABELS else "opus",
                "model": MODELS[DEFAULT_MODEL]["id"],
                "configured": make_client() is not None,
                "example_stories": text,
                "example_site": site,
                "upload_types": list(SUPPORTED),
                "preview": os.environ.get("TCGEN_PREVIEW") == "1",
            })
        return self._json(404, {"error": "Not found"})

    def do_POST(self):
        if not self._authorised():
            return
        path = self.path.split("?", 1)[0]
        try:
            body = self._body()
        except ModelError as exc:
            return self._json(400, {"error": str(exc)})

        if path == "/api/warm":
            try:
                started = _warm_in_background(_choose_model(body.get("model")))
            except ModelError as exc:
                return self._json(400, {"error": str(exc)})
            return self._json(202, {"warming": started})

        if path == "/api/extract":
            return self._extract(body)

        if path in ("/api/generate", "/api/generate/stream"):
            cap = self._cap_error()
            if cap:
                return self._json(429, {"error": cap})
            try:
                model_key = _choose_model(body.get("model"))
            except ModelError as exc:
                return self._json(400, {"error": str(exc)})
            args = (body.get("stories", ""), body.get("site_url") or None, make_client(),
                    model_key)
            if path.endswith("/stream"):
                return self._stream(args)
            try:
                result = generate(*args)
            except ModelError as exc:
                return self._json(400, {"error": str(exc)})
            except Exception as exc:  # noqa: BLE001 - never leak a stack trace to the page
                return self._json(500, {"error": "Something went wrong writing the test cases "
                                                 "(%s). Try again." % type(exc).__name__})
            _spent_today(result.usage.cost_usd)
            return self._json(200, _result_json(result))

        return self._json(404, {"error": "Not found"})

    def _extract(self, body):
        name = os.path.basename(body.get("filename") or "upload")
        try:
            data = base64.b64decode(body.get("content_b64") or "")
            text, notes = extract_text(name, data)
        except (ValueError, TypeError) as exc:
            return self._json(400, {"error": str(exc)})
        stories = parse_stories(text)
        return self._json(200, {"filename": name, "text": text, "notes": notes,
                                "stories_found": len(stories)})

    def _stream(self, args):
        """Server-sent events: each test case goes out the moment it is written."""
        events: "queue.Queue" = queue.Queue()
        done = object()

        def work():
            try:
                result = generate(*args, on_event=events.put)
                _spent_today(result.usage.cost_usd)
                events.put(dict(type="done", **_result_json(result)))
            except ModelError as exc:
                events.put({"type": "error", "error": str(exc)})
            except Exception as exc:  # noqa: BLE001
                events.put({"type": "error", "error": "Something went wrong writing the test "
                                                      "cases (%s). Try again." % type(exc).__name__})
            finally:
                events.put(done)

        self._headers(200, "text/event-stream; charset=utf-8")
        threading.Thread(target=work, daemon=True).start()
        connected = True
        while True:
            try:
                item = events.get(timeout=15)
            except queue.Empty:
                item = {"type": "ping"}  # keeps proxies from closing a quiet connection
            if item is done:
                break
            if not connected:
                continue  # let generation finish so its cost is counted
            try:
                self.wfile.write(("data: %s\n\n" % json.dumps(item)).encode())
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                connected = False


def _result_json(result) -> dict:
    u = result.usage
    return {
        "stories": [dict(s.__dict__) for s in result.stories],
        "cases": [c.model_dump() for c in result.cases],
        "markdown": result.markdown,
        "errors": result.errors,
        "notes": result.notes,
        "usage": {"model": u.model, "input_tokens": u.input_tokens,
                  "output_tokens": u.output_tokens, "cache_read_tokens": u.cache_read_tokens,
                  "cost_usd": round(u.cost_usd, 6), "seconds": u.seconds},
    }


def _free_port(start: int) -> int:
    for port in range(start, start + 30):
        with socket.socket() as s:
            # Same reuse rule as the server itself, so a port that was just
            # released by a restart isn't mistaken for one that is in use.
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free port found near %d" % start)


def main() -> int:
    hosted = "PORT" in os.environ
    host = "0.0.0.0" if hosted else "127.0.0.1"
    port = int(os.environ["PORT"]) if hosted else _free_port(8030)
    if hosted and not os.environ.get("TCGEN_PASSWORD"):
        print("TCGEN_PASSWORD is not set: the page will refuse every request until it is.")
    server = ThreadingHTTPServer((host, port), Handler)
    url = "http://%s:%d" % ("127.0.0.1" if not hosted else host, port)
    print("\n  Test Case Writer  %s" % url)
    print("  default model %s · key %s · daily cap $%.2f\n"
          % (MODELS[DEFAULT_MODEL]["id"], "set" if make_client() else "MISSING", _daily_cap()))
    if not hosted:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0
