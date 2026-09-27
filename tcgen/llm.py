"""The one place that talks to the model provider.

Every request streams. Generation time is almost entirely the model writing
output (~100-120 tokens/s whatever the model), so the only way to make the page
feel fast is to show each test case the moment it is complete - the first one
typically lands 2-3 seconds in. `CaseStreamParser` pulls finished test cases
out of the partial JSON as it arrives.

Models are chosen by a short key. Prices are USD per million tokens, used to
report what a run cost; check https://www.anthropic.com/pricing before quoting
them. The quality/speed figures in LABELS come from tcgen/eval/EVAL_REPORT.md.
"""

import json
import os
import re
import time
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

from tcgen.models import DraftCase, DraftSet
from tcgen.prompt import SYSTEM

MODELS = {
    # key       model id                $/M in  $/M out  extra request settings
    # effort "low": measured at the same 97% coverage as the default with 40% less
    # time and cost (tcgen/eval_effort/EVAL_REPORT.md), so it is the Opus setting.
    "opus":   {"id": "claude-opus-5",    "in": 5.00, "out": 25.00, "effort": "low"},
    "sonnet": {"id": "claude-sonnet-5",  "in": 2.00, "out": 10.00, "effort": None},
    "haiku":  {"id": "claude-haiku-4-5", "in": 1.00, "out": 5.00,  "effort": None},
}

# What the page shows next to each choice. Numbers are measured, not claimed.
LABELS = {
    "opus":   {"name": "Opus 5", "note": "Best coverage · 97%", "cost": "~6¢ a story",
               "speed": "~20s"},
    "sonnet": {"name": "Sonnet 5", "note": "Middle · 74%", "cost": "~3¢ a story",
               "speed": "~25s"},
    "haiku":  {"name": "Haiku 4.5", "note": "Fastest, misses security cases · 71%",
               "cost": "~1¢ a story", "speed": "~10s"},
}

# Chosen by measurement - see tcgen/eval/EVAL_REPORT.md.
DEFAULT_MODEL = os.environ.get("TCGEN_MODEL", "opus")

# Models for which the API can transparently retry a declined request on
# another model (server-side fallback). The reply then says who served it.
_FALLBACK_MODELS = {"claude-opus-5", "claude-fable-5"}


class ModelError(Exception):
    """A generation failed in a way the user should be told about in plain words."""


@dataclass
class Usage:
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cache_write_tokens: int = 0
    cache_read_tokens: int = 0
    seconds: float = 0.0
    cost_usd: float = 0.0

    def add(self, other: "Usage") -> None:
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        self.cache_write_tokens += other.cache_write_tokens
        self.cache_read_tokens += other.cache_read_tokens
        self.seconds = max(self.seconds, other.seconds)
        self.cost_usd += other.cost_usd


def price(model_key: str, u: Usage) -> float:
    p = MODELS[model_key]
    return (u.input_tokens * p["in"]
            + u.cache_write_tokens * p["in"] * 1.25
            + u.cache_read_tokens * p["in"] * 0.10
            + u.output_tokens * p["out"]) / 1_000_000


def make_client():
    """An Anthropic client, or None when no credentials are configured.

    An organisation-level key that isn't scoped to a workspace must name the
    workspace on every request. ANTHROPIC_WORKSPACE_ID supplies it; the ID is
    not a secret.
    """
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        return None
    import anthropic
    headers = {}
    workspace = os.environ.get("ANTHROPIC_WORKSPACE_ID", "").strip()
    if workspace:
        headers["anthropic-workspace-id"] = workspace
    return anthropic.Anthropic(max_retries=3, timeout=180.0, default_headers=headers or None)


def _output_config(model_key: str) -> dict:
    import anthropic
    cfg = {"format": {"type": "json_schema", "schema": anthropic.transform_schema(DraftSet)}}
    if MODELS[model_key].get("effort"):
        cfg["effort"] = MODELS[model_key]["effort"]
    return cfg


def request_args(model_key: str, messages: List[dict], max_tokens: int = 16000) -> dict:
    """Everything that defines the request. Shared by generation and cache warming,
    because the cache only matches if the prefix is byte-identical."""
    if model_key not in MODELS:
        raise ModelError("Unknown model '%s'. Choose one of: %s"
                         % (model_key, ", ".join(MODELS)))
    model_id = MODELS[model_key]["id"]
    args = {
        "model": model_id,
        "max_tokens": max_tokens,
        "system": SYSTEM,
        "messages": messages,
        "output_config": _output_config(model_key),
    }
    if model_id in _FALLBACK_MODELS:
        args["betas"] = ["server-side-fallback-2026-07-01"]
        args["extra_body"] = {"fallbacks": "default"}
    return args


class CaseStreamParser:
    """Pulls complete test cases out of streaming JSON.

    The model writes {"area_code": "...", "cases": [ {...}, {...}, ... ]}. Each
    time a case object closes, it is valid JSON on its own and can be shown,
    long before the whole answer has arrived.
    """

    _CASES = re.compile(r'"cases"\s*:\s*\[')

    def __init__(self):
        self.buf = ""
        self._pos = 0
        self._in_cases = False
        self._depth = 0
        self._in_str = False
        self._esc = False
        self._start: Optional[int] = None

    def feed(self, text: str) -> List[DraftCase]:
        self.buf += text
        found: List[DraftCase] = []
        if not self._in_cases:
            m = self._CASES.search(self.buf)
            if not m:
                return found
            self._in_cases, self._pos = True, m.end()
        i, buf = self._pos, self.buf
        while i < len(buf):
            ch = buf[i]
            if self._in_str:
                if self._esc:
                    self._esc = False
                elif ch == "\\":
                    self._esc = True
                elif ch == '"':
                    self._in_str = False
            elif ch == '"':
                self._in_str = True
            elif ch == "{":
                if self._depth == 0:
                    self._start = i
                self._depth += 1
            elif ch == "}":
                self._depth -= 1
                if self._depth == 0 and self._start is not None:
                    try:
                        found.append(DraftCase.model_validate(json.loads(buf[self._start:i + 1])))
                    except Exception:  # noqa: BLE001 - the final parse will report it
                        pass
                    self._start = None
            i += 1
        self._pos = i
        return found


def _translate(exc: Exception, model_id: str) -> ModelError:
    import anthropic
    if isinstance(exc, anthropic.AuthenticationError):
        return ModelError("The API key was rejected. Check ANTHROPIC_API_KEY.")
    if isinstance(exc, anthropic.PermissionDeniedError):
        return ModelError("The API key isn't allowed to use %s." % model_id)
    if isinstance(exc, anthropic.NotFoundError):
        return ModelError("Model %s wasn't found for this API key." % model_id)
    if isinstance(exc, anthropic.RateLimitError):
        return ModelError("The model provider is rate-limiting requests. Wait a minute and "
                          "try again.")
    if isinstance(exc, anthropic.BadRequestError):
        if "workspace" in str(exc).lower():
            return ModelError("This API key isn't tied to a workspace. Set "
                              "ANTHROPIC_WORKSPACE_ID, or use a key created inside a workspace.")
        return ModelError("The model provider rejected the request: %s"
                          % getattr(exc, "message", exc))
    if isinstance(exc, anthropic.APIStatusError):
        return ModelError("The model provider returned an error (%s). Try again shortly."
                          % exc.status_code)
    if isinstance(exc, anthropic.APIConnectionError):
        return ModelError("Couldn't reach the model provider. Check the internet connection.")
    return ModelError("Generation failed (%s)." % type(exc).__name__)


def warm_cache(client, model_key: str, messages: List[dict]) -> None:
    """Write the prompt cache for this model before anyone asks for it.

    The system prompt and examples are identical on every request; once cached
    they cost a tenth and let every story in a batch run at once without each
    one paying to write the same cache. The page calls this while the user is
    still typing, so the cost of warming is off the critical path.
    """
    args = request_args(model_key, messages, max_tokens=1)
    client.beta.messages.create(**args)


def draft(client, model_key: str, messages: List[dict],
          on_case: Optional[Callable[[DraftCase], None]] = None) -> Tuple[DraftSet, Usage]:
    """One story in, one DraftSet out. `on_case` is called as each case completes."""
    import anthropic

    args = request_args(model_key, messages)
    model_id = args["model"]
    parser = CaseStreamParser()
    started = time.time()
    try:
        with client.beta.messages.stream(**args) as stream:
            for delta in stream.text_stream:
                for case in parser.feed(delta):
                    if on_case is not None:
                        on_case(case)
            final = stream.get_final_message()
    except ModelError:
        raise
    except anthropic.AnthropicError as exc:
        raise _translate(exc, model_id)

    if final.stop_reason == "refusal":
        raise ModelError("The model declined to write test cases for this story.")
    if final.stop_reason == "max_tokens":
        raise ModelError("The answer was cut off before it finished. Split the story "
                         "into smaller stories and try again.")
    try:
        parsed = DraftSet.model_validate_json(parser.buf)
    except Exception:  # noqa: BLE001
        raise ModelError("The model's answer didn't match the test case format.")

    u = final.usage
    served_by = getattr(final, "model", None)
    usage = Usage(
        model=served_by if isinstance(served_by, str) and served_by else model_id,
        input_tokens=u.input_tokens or 0,
        output_tokens=u.output_tokens or 0,
        cache_write_tokens=getattr(u, "cache_creation_input_tokens", 0) or 0,
        cache_read_tokens=getattr(u, "cache_read_input_tokens", 0) or 0,
        seconds=round(time.time() - started, 1),
    )
    usage.cost_usd = price(model_key, usage)
    return parsed, usage
