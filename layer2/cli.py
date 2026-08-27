"""Layer 2 demo CLI.

    python3 -m layer2 http://127.0.0.1:8020
    python3 -m layer2 http://127.0.0.1:8020 --user customer@example.com --password 'Passw0rd!23'
"""

import argparse
import json
import sys
from typing import List

from layer2.pipeline import discover

_R, _D, _B = "\033[0m", "\033[2m", "\033[1m"
_RISK = {"Critical": "\033[91m", "High": "\033[93m", "Medium": "\033[96m", "Low": "\033[90m"}


def _c(t, colour, on):
    return f"{colour}{t}{_R}" if on else t


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="layer2", description="Layer 2 - discover an application through the browser.")
    ap.add_argument("url")
    ap.add_argument("--user")
    ap.add_argument("--password")
    ap.add_argument("--login-path", default="/login")
    ap.add_argument("--max-pages", type=int, default=40)
    ap.add_argument("--max-depth", type=int, default=4)
    ap.add_argument("--probe", action="append", default=None, metavar="PATH",
                    help="Extra entry path to try (repeatable), e.g. --probe /admin")
    ap.add_argument("--deny", action="append", default=None, metavar="FRAGMENT",
                    help="Skip any path containing this fragment (repeatable)")
    ap.add_argument("--allow-destructive", action="store_true",
                    help="Explicitly permit destructive actions (C-04). Off by default.")
    ap.add_argument("--json", dest="json_out", metavar="PATH")
    ap.add_argument("--no-colour", dest="colour", action="store_false", default=True)
    a = ap.parse_args(argv)

    entry = ["/"] + [p for p in (a.probe or []) if p != "/"]
    try:
        amap, reqs = discover(
            a.url, a.user, a.password, a.login_path, a.max_pages, a.max_depth,
            entry_paths=entry, scope_deny=a.deny, allow_destructive=a.allow_destructive)
    except Exception as exc:  # noqa: BLE001
        print("error: %s: %s" % (type(exc).__name__, exc), file=sys.stderr)
        return 2

    on = a.colour and sys.stdout.isatty()
    out: List[str] = []
    add = out.append
    s = amap.stats

    add("")
    add(_c("Layer 2 - Black Box Intelligence", _B, on))
    add(_c("  %s   authenticated: %s" % (amap.base_url, amap.authenticated), _D, on))
    add("")
    add(_c("APPLICATION MAP", _B, on))
    add("  %d pages, %d forms, %d elements, %d journeys  (%d visited, %d skipped)"
        % (s["pages"], s["forms"], s["elements"], s["journeys"],
           amap.pages_visited, amap.pages_skipped))
    add("")
    for p in amap.pages:
        flag = ""
        if p.access_denied:
            flag = _c("  ACCESS DENIED", "\033[91m", on)
        elif p.requires_auth:
            flag = _c("  SIGN-IN REQUIRED", "\033[93m", on)
        add("  %-26s %s  forms %d  links %-3d %s"
            % (p.path, p.status, len(p.forms), len(p.links), flag))
        for f in p.forms:
            req = ", ".join(x.name for x in f.required_fields) or "none"
            add(_c("      form '%s' (%s %s): %d field(s), required: %s"
                   % (f.name, f.method.upper(), f.action or p.path, len(f.fields), req), _D, on))
    add("")

    if amap.journeys:
        add(_c("JOURNEY CANDIDATES", _B, on))
        for j in amap.journeys:
            add("  %-34s %s" % (j.name[:34], " -> ".join(j.paths)))
            add(_c("      %s (confidence %.2f)" % (j.rationale, j.confidence), _D, on))
        add("")

    if amap.blocked_actions:
        add(_c("BLOCKED BY THE SAFETY GOVERNOR", _B, on))
        for b in amap.blocked_actions:
            add(_c("  x %s" % b, "\033[91m", on))
        add(_c("  These were never clicked. Enable with --allow-destructive only on an "
               "environment where that is safe.", _D, on))
        add("")

    add(_c("DISCOVERED REQUIREMENTS  (source=discovered, never confirmed - BR-03)", _B, on))
    for r in reqs:
        add("  %s  %s  conf %.2f"
            % (_c(r.source_ref, _B, on), _c(r.risk.value, _RISK.get(r.risk.value, ""), on),
               r.confidence))
        add("     rule    : %s" % r.rule)
        if r.precondition:
            add("     given   : %s" % r.precondition)
        add("     expected: %s" % r.expected_outcome)
    add("")
    add(_c("-" * 74, _D, on))
    add("%d pages   %d discovered requirements   %d blocked actions"
        % (s["pages"], len(reqs), len(amap.blocked_actions)))
    if amap.warnings:
        add("")
        add(_c("Warnings", _B, on))
        for w in amap.warnings:
            add(_c("  ! %s" % w[:150], "\033[33m", on))
    add("")
    print("\n".join(out))

    if a.json_out:
        with open(a.json_out, "w", encoding="utf-8") as fh:
            json.dump({
                "application_map": amap.model_dump(mode="json"),
                "requirements": [r.model_dump(mode="json") for r in reqs],
            }, fh, indent=2)
        print("wrote %s" % a.json_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
