"""Layer 1 - the pipeline.

    document -> parse -> rules -> (optional) LLM on the leftovers -> Requirement[]

This is the whole of Requirements Intelligence for a single document. It is
deliberately a plain function, not a service: Layer 1 is an engine, and the
orchestration around it (Temporal workflow, API, portal) belongs to layers that
do not exist yet. Keeping it callable in-process is what makes it testable and
demoable today.
"""

from typing import List, Optional, Tuple

from layer1.contracts import Requirement, RequirementSet
from layer1.llm import LlmEnricher
from layer1.parsers import parse_document
from layer1.rules import RuleExtractor


def _dedupe(
    pairs: List[Tuple[Requirement, str]]
) -> List[Tuple[Requirement, str]]:
    """Drop exact repeats. Rules win over LLM for the same rule text + ref."""
    seen = {}
    order: List[str] = []
    for req, method in pairs:
        key = (req.source_ref, req.rule.strip().lower())
        if key not in seen:
            seen[key] = (req, method)
            order.append(key)
        elif method == "rules" and seen[key][1] == "llm":
            seen[key] = (req, method)
    return [seen[k] for k in order]


def _flag_duplicates(
    pairs: List[Tuple[Requirement, str]]
) -> List[Tuple[Requirement, str]]:
    """Flag requirements repeated verbatim under different refs.

    A document that states the same criterion twice is a requirements-quality
    problem, and Layer 1's job is to surface it rather than quietly emit both.
    """
    first_seen = {}
    out: List[Tuple[Requirement, str]] = []
    for req, method in pairs:
        key = (req.rule.strip().lower(), req.expected_outcome.strip().lower())
        if key in first_seen:
            flag = f"duplicates {first_seen[key]} - the same criterion is stated more than once"
            req = req.model_copy(
                update={"ambiguity_flags": list(req.ambiguity_flags) + [flag]}
            )
        else:
            first_seen[key] = req.source_ref
        out.append((req, method))
    return out


def extract_requirements(
    path: str,
    use_llm: bool = True,
    llm_max_blocks: int = 12,
    enricher: Optional[LlmEnricher] = None,
) -> RequirementSet:
    """Ingest one document and return validated Requirement[] with provenance.

    `use_llm=False` forces a fully offline, zero-cost, fully reproducible run.
    """
    doc = parse_document(path)
    warnings: List[str] = list(doc.warnings)

    if not doc.blocks:
        warnings.append("document produced no readable blocks")
        return RequirementSet(
            document_name=doc.name, document_kind=doc.kind, extractor="rules", warnings=warnings
        )

    rule_result = RuleExtractor().extract(doc.blocks, doc.source, doc.name)
    warnings.extend(rule_result.warnings)
    pairs: List[Tuple[Requirement, str]] = [(r, "rules") for r in rule_result.requirements]

    used_llm = False
    if use_llm and rule_result.unresolved:
        enricher = enricher or LlmEnricher(max_blocks=llm_max_blocks)
        llm_reqs, llm_warnings = enricher.enrich(rule_result.unresolved, doc.source, doc.name)
        warnings.extend(llm_warnings)
        pairs.extend((r, "llm") for r in llm_reqs)
        used_llm = bool(llm_reqs)
    elif rule_result.unresolved:
        warnings.append(
            f"{len(rule_result.unresolved)} block(s) had no recognisable requirement structure "
            f"and LLM enrichment is off - re-run with --llm to attempt them"
        )

    pairs = _dedupe(pairs)
    pairs = _flag_duplicates(pairs)

    return RequirementSet(
        document_name=doc.name,
        document_kind=doc.kind,
        extractor="rules+llm" if used_llm else "rules",
        requirements=[r for r, _ in pairs],
        extraction_methods=[m for _, m in pairs],
        warnings=warnings,
    )
