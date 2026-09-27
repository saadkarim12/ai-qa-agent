"""Choose the cheapest model that is good enough, by measurement.

    python3 -m tcgen.evaluate                 # haiku, sonnet, opus - 2 runs per fold
    python3 -m tcgen.evaluate --models haiku,sonnet --runs 3

Method: leave-one-out over the user's two example stories. The model is shown
one story and its test cases, asked to write test cases for the other, and the
result is compared with the user's reference test cases for that story. Then
the other way round.

What is measured, per run:
  coverage   - share of the user's reference test cases the model reproduced,
               judged by the keyword rules in REFERENCE (read them - they are
               the definition of "reproduced")
  grounding  - literals the model used that were not in the story or the one
               example it was shown: data, URLs, quoted on-screen text. In this
               set-up these can only have come from the model's memory.
  format     - whether the answer parsed, and how many step/format flags
  cost, time - from the provider's reported token usage

Pass criteria are fixed here, before any model is run:
  * every run parses
  * mean coverage   >= 0.75
  * mean grounding issues per run <= 1.0
The cheapest model that passes is recommended.

Two stories is a very small test set. The result says which model looks
cheapest-adequate on the user's own examples; it is not a general benchmark.
"""

import argparse
import datetime
import json
import os
import statistics
import sys
from typing import Callable, Dict, List

from tcgen.examples import example_text_for_site, exemplars
from tcgen.guard import FORMAT, GROUNDING
from tcgen.llm import MODELS, ModelError, draft, make_client
from tcgen.markdown import render_markdown
from tcgen.pipeline import finalise
from tcgen.prompt import build_messages
from tcgen.stories import Story

PASS_COVERAGE = 0.75
PASS_GROUNDING = 1.0


def _text(case) -> str:
    parts = [case.objective, case.expected_result] + case.steps + case.preconditions
    parts += ["%s %s" % (d.name, d.value) for d in case.test_data]
    return " ".join(parts).lower()


def _about(case) -> str:
    """The objective and expected result: what the test is for."""
    return ("%s %s" % (case.objective, case.expected_result)).lower()


def _any(t: str, words) -> bool:
    return any(w in t for w in words)


# The user's reference test cases, as predicates over a generated case.
# A reference case counts as reproduced if any generated case satisfies it.
REFERENCE: Dict[str, Dict[str, Callable]] = {
    "US-1": {
        "TC-LOGIN-001 valid credentials": lambda c, t: c.category == "positive"
            and _any(t, ["valid credential", "valid username", "standard_user"])
            and not _any(t, ["invalid", "wrong", "incorrect"]),
        "TC-LOGIN-002 invalid password": lambda c, t: _any(t, [
            "invalid password", "wrong password", "incorrect password", "wrong_password"]),
        "TC-LOGIN-003 invalid username": lambda c, t: _any(t, [
            "invalid username", "invalid_user", "unknown user", "non-existent",
            "nonexistent", "unregistered", "incorrect username", "wrong username"]),
        "TC-LOGIN-004 empty credentials": lambda c, t: _any(t, [
            "empty", "blank", "missing", "without entering", "left empty"])
            and _any(t, ["username", "password", "credential"]),
        "TC-LOGIN-005 password masking": lambda c, t: "mask" in t,
        "TC-LOGIN-006 locked-out user": lambda c, t: "locked" in t,
        # Judged on what the test is *about*, not its preconditions: nearly every
        # login test starts "not logged in", which says nothing about access control.
        "TC-LOGIN-007 no access without login": lambda c, t: _any(_about(c), [
            "without logging", "without login", "without being logged", "unauthenticated",
            "without authentication", "directly", "not logged in", "access denied",
            "redirected to the login"])
            and _any(t, ["inventory", "products page", "protected", "url"]),
        "TC-LOGIN-008 SQL injection": lambda c, t: _any(t, ["sql", "injection", "' or '1'='1"]),
    },
    "US-2": {
        "TC-CART-001 add single product": lambda c, t: _any(t, [
            "single product", "one product", "count shows 1", "count becomes 1",
            "count is 1", "a single", "add a product"])
            and not _any(_about(c), ["multiple", "several", "same product", "different products",
                                     "not logged in", "without logging"]),
        "TC-CART-002 add multiple products": lambda c, t: _any(t, [
            "multiple", "several", "two products", "more than one", "two different"]),
        "TC-CART-003 product details in cart": lambda c, t: "cart" in t
            and (("name" in t and "price" in t) or "details" in c.objective.lower()),
        "TC-CART-004 remove product": lambda c, t: "remove" in t,
        "TC-CART-005 persists after navigating": lambda c, t: _any(t, [
            "navigate away", "navigating away", "return", "persist", "remains",
            "still listed", "still in the cart", "after navigating", "retained"]),
    },
}


def score(story_id: str, cases) -> dict:
    refs = REFERENCE[story_id]
    matched = {}
    for name, pred in refs.items():
        hit = next((c for c in cases if pred(c, _text(c))), None)
        matched[name] = hit.test_id if hit else None
    used = {tid for tid in matched.values() if tid}
    extra = [c for c in cases if c.test_id not in used]
    return {
        "coverage": sum(1 for v in matched.values() if v) / float(len(refs)),
        "matched": matched,
        "extra": [(c.test_id, c.derivation, c.category, c.objective) for c in extra],
        # Distinct problems: one invented value reused in five cases is one invention.
        "grounding": sorted({i for c in cases for i in c.issues if i.startswith(GROUNDING)}),
        "format": [i for c in cases for i in c.issues if i.startswith(FORMAT)],
    }


def run(models: List[str], runs: int, out_dir: str) -> dict:
    client = make_client()
    if client is None:
        sys.exit("ANTHROPIC_API_KEY is not set. Add it, then run this again.")
    ex = exemplars()
    folds = [(ex[0], ex[1]), (ex[1], ex[0])]  # (target, the one example shown)
    os.makedirs(out_dir, exist_ok=True)

    results: Dict[str, List[dict]] = {m: [] for m in models}
    for model in models:
        for target, shown in folds:
            s = target["story"]
            story = Story(s["id"], s["title"], s["text"], s["site_url"])
            for r in range(1, runs + 1):
                label = "%s %s run %d" % (model, s["id"], r)
                print("  %-22s" % label, end="", flush=True)
                try:
                    drafted, usage = draft(client, model, build_messages(story, [shown]))
                except ModelError as exc:
                    print("FAILED  %s" % exc)
                    results[model].append({"story": s["id"], "run": r, "ok": False,
                                           "error": str(exc)})
                    continue
                cases = finalise(story, drafted, {}, [shown])
                sc = score(s["id"], cases)
                results[model].append({
                    "story": s["id"], "run": r, "ok": True, "cases": len(cases),
                    "derived": sum(1 for c in cases if c.derivation == "derived"),
                    "cost": usage.cost_usd, "seconds": usage.seconds,
                    "tokens_in": usage.input_tokens + usage.cache_read_tokens
                                 + usage.cache_write_tokens,
                    "tokens_out": usage.output_tokens, **sc,
                })
                path = os.path.join(out_dir, "%s-%s-run%d.md" % (model, s["id"], r))
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(render_markdown([story], cases, model=usage.model))
                print("coverage %.2f  grounding %d  cases %d  $%.4f  %.1fs"
                      % (sc["coverage"], len(sc["grounding"]), len(cases),
                         usage.cost_usd, usage.seconds))
    return results


def rescore(out_dir: str) -> dict:
    """Re-check saved runs with the current checker and scoring, no API calls.

    Lets a checker or scoring fix be applied to model output that was already
    paid for, and keeps the report consistent with the code that produced it.
    """
    from tcgen.guard import check_set
    from tcgen.markdown import parse_markdown

    with open(os.path.join(out_dir, "results.json")) as fh:
        old = json.load(fh)["results"]
    ex = exemplars()
    by_id = {e["story"]["id"]: e for e in ex}
    other = {"US-1": by_id["US-2"], "US-2": by_id["US-1"]}
    results: Dict[str, List[dict]] = {}
    for model, runs in old.items():
        results[model] = []
        for r in runs:
            if not r.get("ok"):
                results[model].append(r)
                continue
            target = by_id[r["story"]]
            site = target["story"]["site_url"]
            path = os.path.join(out_dir, "runs", "%s-%s-run%d.md" % (model, r["story"], r["run"]))
            with open(path, encoding="utf-8") as fh:
                cases = parse_markdown(fh.read())
            corpus = (target["story"]["text"] + "\n" + site + "\n"
                      + example_text_for_site(site, [other[r["story"]]]))
            check_set(cases, corpus, site)
            keep = {k: r[k] for k in ("story", "run", "ok", "cases", "derived", "cost",
                                      "seconds", "tokens_in", "tokens_out")}
            results[model].append(dict(keep, **score(r["story"], cases)))
    return results


def summarise(results: dict) -> List[dict]:
    rows = []
    for model, rs in results.items():
        ok = [r for r in rs if r.get("ok")]
        row = {"model": model, "id": MODELS[model]["id"], "runs": len(rs),
               "parsed": len(ok), "all_parsed": len(ok) == len(rs) and bool(rs)}
        if ok:
            row.update({
                "coverage": statistics.mean(r["coverage"] for r in ok),
                "grounding": statistics.mean(len(r["grounding"]) for r in ok),
                "format": statistics.mean(len(r["format"]) for r in ok),
                "cases": statistics.mean(r["cases"] for r in ok),
                "cost": statistics.mean(r["cost"] for r in ok),
                "seconds": statistics.mean(r["seconds"] for r in ok),
            })
            row["passes"] = (row["all_parsed"] and row["coverage"] >= PASS_COVERAGE
                             and row["grounding"] <= PASS_GROUNDING)
        else:
            row["passes"] = False
        rows.append(row)
    return rows


def recommend(rows: List[dict]) -> dict:
    passing = [r for r in rows if r["passes"]]
    if passing:
        return min(passing, key=lambda r: r["cost"])
    scored = [r for r in rows if "coverage" in r]
    return max(scored, key=lambda r: (r["coverage"], -r["grounding"])) if scored else {}


def write_report(results: dict, rows: List[dict], pick: dict, path: str, runs: int) -> None:
    now = datetime.datetime.now().strftime("%d %b %Y %H:%M")
    L = ["# Model evaluation — test case generator", "",
         "Run %s. Leave-one-out over the two example stories in "
         "`sample_data/fewshot/Sample-US-TC.xlsx`, %d run(s) per story per model." % (now, runs),
         "",
         "**Pass criteria (fixed before running):** every run parses · mean coverage ≥ %.2f "
         "· mean grounding issues ≤ %.1f per run. The cheapest passing model is recommended."
         % (PASS_COVERAGE, PASS_GROUNDING), "",
         "| Model | Coverage | Grounding issues / run | Format flags / run | Test cases / run "
         "| Cost / story | Time / story | Pass |",
         "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if "coverage" not in r:
            L.append("| %s | — | — | — | — | — | — | ✗ (no run parsed) |" % r["id"])
            continue
        L.append("| %s | %.0f%% | %.1f | %.1f | %.1f | $%.4f | %.1fs | %s |" % (
            r["id"], 100 * r["coverage"], r["grounding"], r["format"], r["cases"],
            r["cost"], r["seconds"], "✓" if r["passes"] else "✗"))
    L.append("")
    if pick:
        verdict = ("**Recommended: %s** — the cheapest model that passed."
                   if pick.get("passes") else
                   "**No model passed.** Best result: %s. Don't rely on it without review.")
        L.append(verdict % pick["id"])
        L.append("")
    L += ["## Detail", ""]
    for model, rs in results.items():
        for r in rs:
            L.append("### %s · %s · run %d" % (MODELS[model]["id"], r["story"], r["run"]))
            L.append("")
            if not r.get("ok"):
                L.append("Failed: %s" % r["error"])
                L.append("")
                continue
            L.append("Coverage %.0f%% · %d test cases (%d derived) · $%.4f · %.1fs"
                     % (100 * r["coverage"], r["cases"], r["derived"], r["cost"], r["seconds"]))
            L.append("")
            L.append("| Reference test case | Reproduced by |")
            L.append("|---|---|")
            for name, tid in r["matched"].items():
                L.append("| %s | %s |" % (name, tid or "**missing**"))
            L.append("")
            if r["extra"]:
                L.append("Beyond the reference (check these are sensible, not invented):")
                L.append("")
                for tid, der, cat, obj in r["extra"]:
                    L.append("- %s (%s, %s): %s" % (tid, der, cat, obj))
                L.append("")
            if r["grounding"]:
                L.append("Grounding issues (values not in the story or the example shown):")
                L.append("")
                for i in r["grounding"]:
                    L.append("- %s" % i)
                L.append("")
    L += ["## Limits of this evaluation", "",
          "- Two stories on one site. It shows which model is adequate on your own examples, "
          "not in general.",
          "- Coverage is judged by keyword rules (`REFERENCE` in `tcgen/evaluate.py`). "
          "The per-run tables show exactly which case matched which reference, so a "
          "misjudged match can be checked.",
          "- A test case beyond the reference isn't automatically good or bad; it needs a "
          "person to judge whether it follows from the story.",
          "- Prices are list prices per million tokens as configured in `tcgen/llm.py`."]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="tcgen.evaluate")
    ap.add_argument("--models", default="haiku,sonnet,opus")
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--out", default=os.path.join("tcgen", "eval"))
    ap.add_argument("--rescore", action="store_true",
                    help="Re-check the saved runs with the current checker; no API calls")
    a = ap.parse_args(argv)
    models = [m.strip() for m in a.models.split(",") if m.strip()]
    unknown = [m for m in models if m not in MODELS]
    if unknown:
        sys.exit("Unknown model(s): %s. Choose from %s" % (unknown, list(MODELS)))

    if a.rescore:
        results = rescore(a.out)
        a.runs = max((r["run"] for rs in results.values() for r in rs), default=a.runs)
    else:
        print("Evaluating %s, %d run(s) per story\n" % (", ".join(models), a.runs))
        results = run(models, a.runs, os.path.join(a.out, "runs"))
    rows = summarise(results)
    pick = recommend(rows)
    report = os.path.join(a.out, "EVAL_REPORT.md")
    write_report(results, rows, pick, report, a.runs)
    with open(os.path.join(a.out, "results.json"), "w") as fh:
        json.dump({"results": results, "summary": rows}, fh, indent=1, default=str)
    print("\nReport: %s" % report)
    if pick:
        print("%s: %s" % ("Recommended" if pick.get("passes") else "Best (none passed)",
                          pick["id"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
