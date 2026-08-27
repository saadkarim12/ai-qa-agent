"""Layer 1 demo server.

    python3 -m layer1.web

A local, single-user UI for exercising Layer 1 by hand: pick a bundled fixture
or drop in your own document, run the extraction, and inspect every field of
the resulting Requirement[] against the HLD 4.1 contract.

Deliberately built on the standard library only - no FastAPI, no uvicorn, no
install step. It binds to 127.0.0.1 and serves one page.
"""

import base64
import json
import os
import re
import socket
import tempfile
import uuid
import threading
import traceback
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import List, Optional

from layer1._page import PAGE
from layer1.llm import LlmEnricher
from layer1.parsers import supported_extensions
from layer1.pipeline import extract_requirements
from layer3.pipeline import build_test_plan
from layer2.pipeline import discover
from layer3.report import to_docx, to_html, to_markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, "sample_data")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024

# The last few runs, so a report can be downloaded without crawling again.
_RUNS = {}
_RUN_ORDER = []
_MAX_RUNS = 8


# --------------------------------------------------------------------------
# fixtures
# --------------------------------------------------------------------------

_DESCRIPTIONS = {
    "user_stories.md": "8 stories - the walkthrough document",
    "jira_sample_issues.json": "Jira export - source=jira, real issue keys",
    "01_happy_path_stories.md": "4 clean stories, 10 acceptance criteria",
    "02_ambiguous_requirements.md": "Unreviewed draft - every ambiguity class",
    "03_gherkin_only.md": "Given/When/Then with no story framing",
    "04_prose_no_structure.md": "Narrative prose - rules should decline",
    "05_no_requirements.md": "Meeting notes - nothing to extract",
    "06_empty.md": "Empty file",
    "07_prompt_injection.md": "Embedded 'ignore all instructions' block",
    "08_unicode_multilingual.md": "French, Japanese, currency symbols",
    "09_duplicates.md": "Same criterion stated twice",
    "10_malformed.json": "Broken Jira export (was DEF-01)",
    "11_wrong_json_shape.json": "Valid JSON, no issues array",
    "12_priority_mapping.json": "Blocker/Major/Normal/Trivial mapping",
    "13_unsupported.rtf": "Unsupported format - expect a clean error",
    "14_test_cases.xlsx": "Two-sheet QA spreadsheet",
    "15_requirements.docx": "Word doc: bullets + table (was DEF-02)",
    "16_scanned_no_text.pdf": "PDF with no text layer",
    "17_large_volume.md": "60 stories / 120 criteria",
    "18_stories.pdf": "PDF of 4 stories - the PDF walkthrough",
    "19_jira_northwind.json": "14 Jira issues - matches the demo bank app",
}


def _fixtures() -> List[dict]:
    out = []
    for group, folder in (("Sample documents", SAMPLES),
                          ("QA fixtures", os.path.join(SAMPLES, "qa"))):
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name)
            if not os.path.isfile(path) or name.startswith("."):
                continue
            out.append({
                "group": group,
                "name": name,
                "rel": os.path.relpath(path, ROOT),
                "desc": _DESCRIPTIONS.get(name, ""),
                "size": os.path.getsize(path),
            })
    return out


def _safe_fixture_path(rel: str) -> Optional[str]:
    """Only allow files that genuinely live under sample_data/."""
    candidate = os.path.realpath(os.path.join(ROOT, rel))
    if candidate.startswith(os.path.realpath(SAMPLES) + os.sep) and os.path.isfile(candidate):
        return candidate
    return None


def _run(
    path: Optional[str],
    use_llm: bool,
    budget_minutes: Optional[int] = None,
    url: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    probe: Optional[str] = None,
) -> dict:
    from layer1.contracts import RequirementSet

    result = (
        extract_requirements(path, use_llm=use_llm) if path
        else RequirementSet(document_name=url or "application", document_kind="none",
                            extractor="rules")
    )

    app_map = None
    discovered = []
    discovery_error = None
    if url:
        try:
            probes = [p.strip() for p in (probe or "").split(",") if p.strip()]
            app_map, discovered = discover(
                url, username or None, password or None,
                max_pages=25, entry_paths=["/"] + probes)
        except Exception as exc:  # noqa: BLE001 - discovery failing must not lose the document
            discovery_error = "%s: %s" % (type(exc).__name__, str(exc)[:180])

    plan = build_test_plan(result, budget_minutes=budget_minutes,
                           app_map=app_map, discovered=discovered)
    if discovery_error:
        plan.warnings.append("discovery failed - %s" % discovery_error)

    run_id = uuid.uuid4().hex[:12]
    _RUNS[run_id] = (plan, app_map)
    _RUN_ORDER.append(run_id)
    while len(_RUN_ORDER) > _MAX_RUNS:
        _RUNS.pop(_RUN_ORDER.pop(0), None)

    return {
        "run_id": run_id,
        "app_map": app_map.model_dump(mode="json") if app_map else None,
        "app_stats": app_map.stats if app_map else None,
        "discovered_count": len(discovered),
        "plan": plan.model_dump(mode="json"),
        "plan_stats": plan.stats,
        "document_name": result.document_name,
        "document_kind": result.document_kind,
        "extractor": result.extractor,
        "requirements": [r.model_dump(mode="json") for r in result.requirements],
        "extraction_methods": result.extraction_methods,
        "warnings": result.warnings,
        "stats": result.stats,
    }


# --------------------------------------------------------------------------
# server
# --------------------------------------------------------------------------


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # keep the console clean; errors still surface in the UI

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, payload: dict) -> None:
        self._send(code, json.dumps(payload).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
        elif self.path.startswith("/api/report"):
            query = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
            entry = _RUNS.get(query.get("id", ""))
            if entry is None:
                self._json(404, {"error": "that run has expired - run the analysis again"})
                return
            plan, app_map = entry
            fmt = (query.get("format") or "docx").lower()
            stem = re.sub(r"[^A-Za-z0-9._-]+", "_",
                          plan.strategy.document_name.rsplit(".", 1)[0]) or "test-plan"
            try:
                if fmt == "md":
                    body = to_markdown(plan, app_map).encode("utf-8")
                    ctype, ext = "text/markdown; charset=utf-8", "md"
                elif fmt == "html":
                    body = to_html(plan, app_map).encode("utf-8")
                    ctype, ext = "text/html; charset=utf-8", "html"
                else:
                    body = to_docx(plan, app_map)
                    ctype, ext = ("application/vnd.openxmlformats-officedocument."
                                  "wordprocessingml.document"), "docx"
            except Exception as exc:  # noqa: BLE001
                self._json(500, {"error": "%s: %s" % (type(exc).__name__, exc)})
                return
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Content-Disposition",
                             'attachment; filename="QA-Test-Plan-%s.%s"' % (stem, ext))
            self.end_headers()
            self.wfile.write(body)

        elif self.path == "/api/fixtures":
            enricher = LlmEnricher()
            self._json(200, {
                "fixtures": _fixtures(),
                "supported": supported_extensions(),
                "llm_configured": bool(
                    os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
                ),
            })
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/extract":
            self._json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_UPLOAD_BYTES:
                self._json(413, {"error": "file too large (limit 10 MB)"})
                return
            payload = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            self._json(400, {"error": "malformed request body"})
            return

        use_llm = bool(payload.get("use_llm"))
        tmp = None
        try:
            if payload.get("fixture"):
                path = _safe_fixture_path(payload["fixture"])
                if path is None:
                    self._json(400, {"error": "unknown fixture"})
                    return
            elif payload.get("content_b64") is not None:
                name = os.path.basename(payload.get("filename") or "upload")
                ext = os.path.splitext(name)[1] or ".txt"
                raw = base64.b64decode(payload["content_b64"])
                fd, tmp = tempfile.mkstemp(prefix="layer1_", suffix=ext)
                with os.fdopen(fd, "wb") as fh:
                    fh.write(raw)
                path = tmp
            elif payload.get("url"):
                path = None
            else:
                self._json(400, {"error": "provide a document, a URL, or both"})
                return

            budget = payload.get("budget_minutes")
            budget = int(budget) if budget else None
            result = _run(
                path, use_llm, budget,
                url=(payload.get("url") or "").strip() or None,
                username=payload.get("username"),
                password=payload.get("password"),
                probe=payload.get("probe"),
            )
            if payload.get("filename"):
                result["document_name"] = os.path.basename(payload["filename"])
            self._json(200, result)

        except ValueError as exc:            # unsupported format - expected path
            self._json(200, {"error": str(exc), "kind": "unsupported"})
        except FileNotFoundError as exc:
            self._json(200, {"error": str(exc), "kind": "missing"})
        except Exception as exc:             # genuine bug - show it, don't hide it
            self._json(500, {
                "error": f"{type(exc).__name__}: {exc}",
                "trace": traceback.format_exc(limit=6),
            })
        finally:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)


def _free_port(start: int = 8010, tries: int = 40) -> int:
    for port in range(start, start + tries):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("no free port found between 8010 and 8050")


def main() -> int:
    port = _free_port()
    url = "http://127.0.0.1:%d" % port
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("\n  Layer 1 - Requirements Intelligence")
    print("  %s" % url)
    print("  Ctrl+C to stop\n")
    threading.Timer(0.7, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("  stopped\n")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
