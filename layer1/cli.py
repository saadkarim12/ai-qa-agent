"""Layer 1 demo CLI.

    python3 -m layer1 sample_data/user_stories.md
    python3 -m layer1 sample_data/user_stories.md --json out.json
    python3 -m layer1 stories.docx --no-llm      # fully offline, zero cost
"""

import argparse
import json
import sys
from typing import List

from layer1.contracts import Requirement, RequirementSet, Risk
from layer1.parsers import supported_extensions
from layer1.pipeline import extract_requirements

_RESET, _DIM, _BOLD = "\033[0m", "\033[2m", "\033[1m"
_RISK_COLOUR = {
    Risk.CRITICAL: "\033[91m",
    Risk.HIGH: "\033[93m",
    Risk.MEDIUM: "\033[96m",
    Risk.LOW: "\033[90m",
}


def _c(text: str, colour: str, enabled: bool) -> str:
    return f"{colour}{text}{_RESET}" if enabled else text


def _wrap(text: str, width: int, indent: str) -> List[str]:
    words, lines, line = text.split(), [], ""
    for w in words:
        if line and len(line) + 1 + len(w) > width:
            lines.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    if line:
        lines.append(line)
    return [lines[0]] + [indent + ln for ln in lines[1:]] if lines else [""]


def render(result: RequirementSet, colour: bool) -> str:
    out: List[str] = []
    stats = result.stats
    add = out.append

    add("")
    add(_c(f"Layer 1 - Requirements Intelligence", _BOLD, colour))
    add(_c(f"  {result.document_name}  ({result.document_kind}, extractor: {result.extractor})",
           _DIM, colour))
    add("")

    for i, req in enumerate(result.requirements):
        method = result.extraction_methods[i] if i < len(result.extraction_methods) else "?"
        risk_txt = _c(f"{req.risk.value:<9}", _RISK_COLOUR.get(req.risk, ""), colour)
        header = (
            f"{_c(req.source_ref, _BOLD, colour)}  {risk_txt}"
            f"{_c(f'conf {req.confidence:.2f}  [{req.source.value}/{method}]', _DIM, colour)}"
        )
        add(header)
        add(f"  actor    : {req.actor}")
        add(f"  workflow : {req.workflow}")
        for line in _wrap(req.rule, 88, "             "):
            add(f"  rule     : {line}" if line == _wrap(req.rule, 88, "             ")[0] else line)
        if req.precondition:
            for j, line in enumerate(_wrap(req.precondition, 88, "             ")):
                add(f"  given    : {line}" if j == 0 else line)
        for j, line in enumerate(_wrap(req.expected_outcome, 88, "             ")):
            add(f"  expected : {line}" if j == 0 else line)
        for flag in req.ambiguity_flags:
            add(_c(f"  ambiguity: {flag}", "\033[33m", colour))
        add("")

    add(_c("-" * 78, _DIM, colour))
    add(f"{stats['total']} requirements   "
        f"Critical {stats['by_risk']['Critical']} / High {stats['by_risk']['High']} / "
        f"Medium {stats['by_risk']['Medium']} / Low {stats['by_risk']['Low']}")
    add(f"confirmed {stats['confirmed']}   ambiguous {stats['ambiguous']}   "
        f"avg confidence {stats['avg_confidence']}")
    by_method = ", ".join(f"{k} {v}" for k, v in sorted(stats["by_method"].items())) or "none"
    add(f"extracted by: {by_method}")

    if result.warnings:
        add("")
        add(_c("Warnings", _BOLD, colour))
        for w in result.warnings:
            add(_c(f"  ! {w}", "\033[33m", colour))
    add("")
    return "\n".join(out)


def main(argv: List[str] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="layer1",
        description="Layer 1 - Requirements Intelligence. Ingest a document, emit Requirement[].",
    )
    parser.add_argument("document", help=f"Supported: {', '.join(supported_extensions())}")
    parser.add_argument("--json", dest="json_out", metavar="PATH",
                        help="Write the Requirement[] contract to a JSON file")
    parser.add_argument("--llm", dest="use_llm", action="store_true", default=True,
                        help="Allow LLM enrichment of blocks the rules cannot parse (default)")
    parser.add_argument("--no-llm", dest="use_llm", action="store_false",
                        help="Fully offline: rules only, zero cost, fully reproducible")
    parser.add_argument("--llm-max-blocks", type=int, default=12,
                        help="Cap on blocks sent to the model (default: 12)")
    parser.add_argument("--no-colour", dest="colour", action="store_false", default=True)
    args = parser.parse_args(argv)

    try:
        result = extract_requirements(
            args.document, use_llm=args.use_llm, llm_max_blocks=args.llm_max_blocks
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(render(result, args.colour and sys.stdout.isatty()))

    if args.json_out:
        payload = [r.model_dump(mode="json") for r in result.requirements]
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        print(f"wrote {len(payload)} requirements to {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
